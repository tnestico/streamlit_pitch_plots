import seaborn as sns
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import PitchPlotFunctions as ppf
import requests
import polars as pl
from datetime import date
import api_scraper



# Display the app title and description
st.markdown("""
## MLB & AAA Pitch Plots App

##### By: Thomas Nestico ([@TJStats](https://x.com/TJStats))
##### Code: [GitHub Repo](https://github.com/tnestico/streamlit_pitch_plots)
##### Data: [MLB](https://baseballsavant.mlb.com/)

#### About
This Streamlit app retrieves MLB and AAA Pitching Data for a selected pitcher from the MLB Stats API and is accessed using my [MLB Stats API Scraper](https://github.com/tnestico/mlb_scraper).

The app outputs the pitcher's data into both a plot and table to illustrate and summarize the data. 
It can also display data for games currently in progress.

*More information about the data and plots is shown at the bottom of this page.*

"""
)

# Initialize the plotter object from PitchPlotFunctions
ploter = ppf.PitchPlotFunctions()
# Initialize the scraper object
scraper = api_scraper.MLB_Scrape()

# Dictionary mapping league names to sport IDs
sport_id_dict = {'MLB': 1, 'AAA': 11}

# Create two columns for league and pitcher selection
st.write("#### Plot")
col_1, col_2 = st.columns(2)
with col_1:
    # Select league
    selected_league = st.selectbox('##### Select League', list(sport_id_dict.keys()))
    selected_sport_id = sport_id_dict[selected_league]

with col_2:
    # Get player data and filter for pitchers
    df_player = scraper.get_players(sport_id=selected_sport_id)
    df_player = df_player.filter(pl.col('position').str.contains('P'))
    df_player = df_player.with_columns(
        (pl.concat_str(["name", "player_id"], separator=" - ").alias("pitcher_name_id"))
    )
    
    # Select specific columns and convert to dictionary
    pitcher_name_id_dict = dict(df_player.select(['pitcher_name_id', 'player_id']).iter_rows())
    
    # Initialize session state for previous selection
    if 'prev_pitcher_id' not in st.session_state:
        st.session_state.prev_pitcher_id = None
    
    # Display a selectbox for pitcher selection
    selected_pitcher = st.selectbox("##### Select Pitcher", list(pitcher_name_id_dict.keys()))
    pitcher_id = pitcher_name_id_dict[selected_pitcher]

# Clear cache if selection changes
if pitcher_id != st.session_state.prev_pitcher_id:
    st.cache_data.clear()
    st.session_state.prev_pitcher_id = pitcher_id
    st.session_state.cache_cleared = False
    st.write('Cache cleared!')

# Initialize session state for cache status
if 'cache_cleared' not in st.session_state:
    st.session_state.cache_cleared = False

# Dictionary for batter hand selection
batter_hand_picker = {
    'All': ['L', 'R'],
    'LHH': ['L'],
    'RHH': ['R']
}

# Define date range for the season
min_date = date(2024, 3, 20)
max_date = date(2024, 11, 30)

# Create columns for input widgets
st.write("##### Filters")
col1, col2, col3 = st.columns(3)
with col1:
    # Selectbox for batter handedness
    batter_hand_select = st.selectbox('Batter Handedness:', list(batter_hand_picker.keys()))
    batter_hand = batter_hand_picker[batter_hand_select]
with col2:
    # Date input for start date
    start_date = st.date_input('Start Date:', 
                  value=min_date, 
                  min_value=min_date, 
                  max_value=max_date, 
                  format="YYYY-MM-DD")
with col3:
    # Date input for end date
    end_date = st.date_input('End Date:', 
                  value="default_value_today", 
                  min_value=min_date, 
                  max_value=max_date, 
                  format="YYYY-MM-DD")

# Dictionary for plot type selection
plot_picker_dict = {
    'Short Form Movement': 'short_form_movement',
    'Long Form Movement': 'long_form_movement',
    'Release Points': 'release_point'
}

# Selectbox for plot type
plot_picker_select = st.selectbox('Select Plot Type:', list(plot_picker_dict.keys()))
plot_picker = plot_picker_dict[plot_picker_select]

# Extract season from start date
season = str(start_date)[0:4]

# Get list of games for the selected player and date range
player_games = scraper.get_player_games_list(player_id=pitcher_id, season=season,
                                             start_date=str(start_date), end_date=str(end_date),
                                             sport_id=selected_sport_id,
                                             game_type = ['R','P'])

# Function to fetch data and cache it
@st.cache_data
def fetch_data():
    data = scraper.get_data(game_list_input=player_games)
    df = scraper.get_data_df(data_list=data)
    return df

# Fetch data and manage cache status
if not st.session_state.cache_cleared:
    df_original = fetch_data()
    st.session_state.cache_cleared = True
else:
    df_original = fetch_data()

# Button to generate plot
if st.button('Generate Plot'):
    try:
        # Convert dataframe to polars and filter based on inputs
        df = ploter.df_to_polars(df_original=df_original,
                                 pitcher_id=pitcher_id,
                                 start_date=str(start_date),
                                 end_date=str(end_date),
                                 batter_hand=batter_hand)
        print(df)
        if len(df) == 0:
            st.write('Please select different parameters.')
        else:
            # Generate the final plot
            ploter.final_plot(
                df=df,
                pitcher_id=pitcher_id,
                plot_picker=plot_picker,
                sport_id=selected_sport_id)
            
            # Use a container to control the width of the AgGrid display
            with st.container():
                # Group the data by pitch type
                grouped_df = (
                    df.group_by(['pitcher_id', 'pitch_description'])
                    .agg([
                        pl.col('is_pitch').drop_nans().count().alias('pitches'),
                        pl.col('start_speed').drop_nans().mean().round(1).alias('start_speed'),
                        pl.col('vb').drop_nans().mean().round(1).alias('vb'),
                        pl.col('ivb').drop_nans().mean().round(1).alias('ivb'),
                        pl.col('hb').drop_nans().mean().round(1).alias('hb'),
                        pl.col('spin_rate').drop_nans().mean().round(0).alias('spin_rate'),
                        pl.col('x0').drop_nans().mean().round(1).alias('x0'),
                        pl.col('z0').drop_nans().mean().round(1).alias('z0'),
                    ])
                    .with_columns(
                        (pl.col('pitches') / pl.col('pitches').sum().over('pitcher_id') * 100).round(3).alias('proportion')
                    )).sort('proportion', descending=True).select(["pitch_description", "pitches", "proportion", "start_speed", "vb", "ivb", "hb",
                                                                   "spin_rate", "x0", "z0"])

                st.write("#### Pitching Data")
                column_config_dict = {
                    'pitcher_id': 'Pitcher ID',
                    'pitch_description': 'Pitch Type',
                    'pitches': 'Pitches',
                    'start_speed': 'Velocity',
                    'vb': 'VB',
                    'ivb': 'iVB',
                    'hb': 'HB',
                    'spin_rate': 'Spin Rate',
                    'proportion': st.column_config.NumberColumn("Pitch%", format="%.1f%%"),
                    'x0': 'hRel',
                    'z0': 'vRel',
                }

                st.markdown(f"""##### {selected_pitcher.split('-')[0]} {selected_league} Pitch Data""")
                st.dataframe(grouped_df,
                             hide_index=True,
                             column_config=column_config_dict,
                             width=1500)

                # Configure the AgGrid options
                # gb = GridOptionsBuilder.from_dataframe(grouped_df)
                # # Set display names for columns
                # for col, display_name in zip(grouped_df.columns, grouped_df.columns):
                #     gb.configure_column(col, headerName=display_name)

                # grid_options = gb.build()

                # # Display the dataframe using AgGrid
                # grid_response = AgGrid(
                #     grouped_df,
                #     gridOptions=grid_options,
                #     height=300,
                #     allow_unsafe_jscode=True,
                # )

    except IndexError:
        st.write('Please select different parameters.')

# Display column and plot descriptions
st.markdown("""
#### Column Descriptions

- **`Pitch Type`**: Describes the type of pitch thrown (e.g., 4-Seam Fastball, Curveball, Slider).
- **`Pitches`**: The total number of pitches thrown by the pitcher.
- **`Pitch%`**: Proportion of pitch thrown.
- **`Velocity`**: The initial velocity of the pitch as it leaves the pitcher's hand, measured in miles per hour (mph).
- **`VB`**: Vertical Break (VB), representing the amount movement of a pitch due to spin and gravity, measured in inches (in).
- **`iVB`**: Induced Vertical Break (iVB), representing the amount movement of a pitch strictly due to the spin imparted on the ball, measured in inches (in).
- **`HB`**: Horizontal Break (HB), indicating the amount of horizontal movement of a pitch, measured in inches (in).
- **`Spin Rate`**: The rate of spin of the pitch as it is released, measured in revolutions per minute (rpm).
- **`hRel`**: The horizontal release point of the pitch, measured in feet from the center of the pitcher's mound (ft).
- **`vRel`**: The vertical release point of the pitch, measured in feet above the ground (ft).

#### Plot Descriptions

- **`Short Form Movement`**: Illustrates the movement of the pitch due to spin, where (0,0) indicates a pitch with perfect gyro-spin (e.g. Like a Football).
- **`Long Form Movement`**: Illustrates the movement of the pitch due to spin and gravity.
- **`Release Points`**: Illustrates a pitchers release points from the catcher's perspective.

#### Acknowledgements

Big thanks to [Michael Rosen](https://twitter.com/bymichaelrosen) and [Jeremy Maschino](https://twitter.com/pitchprofiler) for inspiration for this project

Check Out Michael's [Pitch Plotting App](https://pitchplotgenerator.streamlit.app/)

Check Out Jeremy's Website [Pitch Profiler](http://www.mlbpitchprofiler.com/)
"""
)
