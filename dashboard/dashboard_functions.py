import pandas as pd
import streamlit as st
import os


@st.cache
def load_data() -> pd.DataFrame:
    pdf = (pd.read_json('../data/title_data.json')
           .rename(columns={'name': 'title'})
           # .sort_values(by='tomato_score', ascending=False)
           .set_index('title', append=False)
           )
    pdf['title'] = pdf.index
    pdf['year'] = pdf['year'].fillna(0).map(int)
    pdf['main_genre'] = pdf['main_genre'].fillna('')
    pdf['cast'] = pdf['cast'].apply(lambda x: [] if x is None else x)
    return pdf


def read_available_markets() -> list:
    dir_list = os.listdir('../data/markets')
    return [d.replace('.json', '').replace('titles_', '') for d in dir_list]
