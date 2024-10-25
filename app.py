import seaborn as sns
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import requests
import polars as pl
from datetime import date

# Load data
df = pl.read_csv("tjstuff_plus_pitch_data_2024.csv").fill_nan(None)
df = df.drop_nulls(subset=['pitch_grade','tj_stuff_plus'])
df = df.sort(['pitcher_name','tj_stuff_plus'], ascending=[False,True])

# df = df.with_columns([
#     pl.col('tj_stuff_plus').cast(pl.Int64).alias('tj_stuff_plus'),
#     pl.col('pitches').cast(pl.Int64).alias('pitches'),
#     pl.col('pitcher_id').cast(pl.Int64).alias('pitcher_id'),
#     pl.col('pitch_grade').cast(pl.Int64).alias('pitch_grade')
# ])
column_config_dict = {
    'pitcher_id': 'Pitcher ID',
    'pitcher_name': 'Pitcher Name',
    'pitch_type': 'Pitch Type',
    'pitches': 'Pitches',
    'tj_stuff_plus': st.column_config.NumberColumn("tjStuff+", format="%.0f%"),
    'pitch_grade': st.column_config.NumberColumn("Pitch Grade", format="%.0f%")
}




st.dataframe(df[['pitcher_id', 'pitcher_name', 'pitch_type', 'pitches', 'tj_stuff_plus', 'pitch_grade']],
                hide_index=True,
                column_config=column_config_dict,
                width=1500)
