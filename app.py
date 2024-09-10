import seaborn as sns
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import PitchPlotFunctions as ppf
import requests
import polars as pl
from datetime import date

# Initialize the plotter object from PitchPlotFunctions
ploter = ppf.PitchPlotFunctions()

# # URL of the file to download (raw content)
# file_url = "https://raw.githubusercontent.com/tnestico/mlb_scraper/main/api_scraper.py"
# local_file_path = "api_scraper.py"

# # Download the file from GitHub
# response = requests.get(file_url)
# if response.status_code == 200:
#     with open(local_file_path, 'wb') as file:
#         file.write(response.content)
# else:
#     print(f"Failed to download file: {response.status_code}")

# Import the downloaded scraper module
import api_scraper

# Initialize the scraper object
scraper = api_scraper.MLB_Scrape()


sport_id_dict = {'MLB':1,
                 'AAA':11}


selected_league = st.selectbox('#### Select League', list(sport_id_dict.keys()))
selected_sport_id = sport_id_dict[selected_league]

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
st.write("#### Select Pitcher")
selected_pitcher = st.selectbox('', list(pitcher_name_id_dict.keys()))
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
max_date = date(2024, 10, 1)

# Create columns for input widgets
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
                                            sport_id=selected_sport_id)

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
                             batter_hand=batter_hand,
                             )
        print(df)
        if len(df) == 0:
            st.write('Please select different parameters.')
            
            
        else:
        # Generate the final plot
            ploter.final_plot(
             df=df,
             pitcher_id=pitcher_id,
             plot_picker=plot_picker,
             sport_id = selected_sport_id)
          
          # Use a container to control the width of the AgGrid display
        with st.container():


                        # Group the data by pitch type
            grouped_df = (
                df.group_by(['pitcher_id','pitch_description'])
                .agg([
                    pl.col('is_pitch').drop_nans().count().alias('pitches'),
                    pl.col('start_speed').drop_nans().mean().round(1).alias('start_speed'),
                    pl.col('ivb').drop_nans().mean().round(1).alias('ivb'),
                    pl.col('hb').drop_nans().mean().round(1).alias('hb'),
                    pl.col('spin_rate').drop_nans().mean().round(0).alias('spin_rate'),
                ])
                .with_columns(
                    (pl.col('pitches') / pl.col('pitches').sum().over('pitcher_id') * 100).round(3).alias('proportion')
                )).sort('proportion', descending=True)


            st.write("#### Pitching Data")
            column_config_dict = {
                'pitcher_id': 'Pitcher ID',
                'pitch_description': 'Pitch Type',
                'pitches': 'Pitches',
                'start_speed': 'Velocity (mph)',
                'ivb': 'iVB (in)',
                'hb': 'HB (in)',
                'spin_rate': 'Spin Rate (rpm)',
                'proportion': st.column_config.NumberColumn("Pitch%",  format="%.1f%%")
            }
                
            #st.column_config.NumberColumn("Dollar values”, format=”$ %d")}



            st.dataframe(grouped_df,
                         hide_index=True,
                         column_config=column_config_dict
        
                         )

            # Configure the AgGrid options
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



