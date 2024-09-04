import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import PitchPlotFunctions as ppf
ploter = ppf.PitchPlotFunctions()

pos_dict = {1 :'P',
            2 :'C',
            3 :'1B',
            4 :'2B',
            5 :'3B',
            6 :'SS',
            7 :'LF',
            8 :'CF',
            9 :'RF',
            10 :'DH'}

# Set Streamlit page configuration
#st.set_page_config(layout="wide")

# # Inject custom CSS to set the width of the container to 1250px
# st.markdown(
#     """
#     <style>
#     .main-container {
#         max-width: 1250px;
#         margin: 0 auto;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )



# df_all = pl.read_csv("C:/Users/thoma/Google Drive/Python/Baseball/season_stats/2024/2024_regular_data.csv")
from datasets import load_dataset
dataset = load_dataset('nesticot/mlb_data', data_files=['mlb_pitch_data_2024.csv' ])
dataset_train = dataset['train']
df_all = dataset_train.to_polars()#.set_index(list(dataset_train.features.keys())[0]).reset_index(drop=True)


# Assuming df_2023 is already defined and loaded
df_all = df_all.drop('Unnamed: 0')
# Concatenate 'pitcher_name' and 'pitcher_id' with a space
df_all = df_all.with_columns(
    (pl.concat_str(["pitcher_name", "pitcher_id"], separator=" - ").alias("pitcher_name_id"))
)

# Select specific columns and convert to dictionary
pitcher_name_id_dict = dict(df_all.select(['pitcher_name_id', 'pitcher_id']).iter_rows())


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



df = ploter.df_to_polars(df_original=df_all,
                                 pitcher_id=pitcher_id,
                                 start_date=str(start_date),
                                 end_date=str(end_date),
                                 batter_hand=batter_hand)

# fig = plt.figure(figsize=(16, 16), dpi=400)

if st.button('Generate Plot'):
    try:
            ploter.final_plot(
                              df=df,
                              pitcher_id=pitcher_id,
                              plot_picker=plot_picker)
    except IndexError:
            st.write('Please select different parameters.')
                
            
            # st.pyplot(final)


