import seaborn as sns
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import PitchPlotFunctions as ppf
import requests
import polars as pl

ploter = ppf.PitchPlotFunctions()

# URL of the file to download (raw content)
file_url = "https://raw.githubusercontent.com/tnestico/mlb_scraper/main/api_scraper.py"
local_file_path = "api_scraper.py"

# Download the file from GitHub
response = requests.get(file_url)
if response.status_code == 200:
    with open(local_file_path, 'wb') as file:
        file.write(response.content)
else:
    print(f"Failed to download file: {response.status_code}")

import api_scraper

scraper = api_scraper.MLB_Scrape()

df_player = scraper.get_players(sport_id=1)
# Assuming df_player is already defined and loaded
df_player = df_player.filter(pl.col('position').str.contains('P'))
df_player = df_player.with_columns(
    (pl.concat_str(["name", "player_id"], separator=" - ").alias("pitcher_name_id"))
)

# Select specific columns and convert to dictionary
pitcher_name_id_dict = dict(df_player.select(['pitcher_name_id', 'player_id']).iter_rows())


st.write("#### Select Pitcher")
selected_pitcher= st.selectbox('',list(pitcher_name_id_dict.keys()))
pitcher_id = pitcher_name_id_dict[selected_pitcher]

batter_hand_picker = {
        'All': ['L', 'R'],
        'LHH': ['L'],
        'RHH': ['R']
    }


from datetime import date
min_date = date(2024, 3, 20)
max_date = date(2024, 10, 1)

col1, col2, col3 = st.columns(3)
with col1:

    
    batter_hand_select = st.selectbox('Handedness:',list(batter_hand_picker.keys()))
    batter_hand = batter_hand_picker[batter_hand_select]
with col2:
    start_date = st.date_input('Start Date:', 
                  value= min_date, 
                  min_value=min_date, 
                  max_value=max_date, 
                  format="YYYY-MM-DD")
with col3:
    end_date = st.date_input('End Date:', 
                  value= "default_value_today", 
                  min_value=min_date, 
                  max_value=max_date, 
                  format="YYYY-MM-DD")


plot_picker_dict = {
    'Short Form Movement': 'short_form_movement',
    'Long Form Movement': 'long_form_movement',
    'Release Points' : 'release_point'
                    
}

plot_picker_select = st.selectbox('',list(plot_picker_dict.keys()))
plot_picker = plot_picker_dict[plot_picker_select]

season = start_date[0:4]


player_games = scraper.get_player_games_list(player_id=pitcher_id, season=season,
                                             start_date=str(start_date), end_date=str(end_date))


data = scraper.get_data(game_list_input=player_games)
df = scraper.get_data_df(data_list=data)


df = ploter.df_to_polars(df_original=df,
                                 pitcher_id=pitcher_id,
                                 start_date=str(start_date),
                                 end_date=str(end_date),
                                 batter_hand=batter_hand)


if st.button('Generate Plot'):
    try:
            ploter.final_plot(
                              df=df,
                              pitcher_id=pitcher_id,
                              plot_picker=plot_picker)
    except IndexError:
            st.write('Please select different parameters.')
                

