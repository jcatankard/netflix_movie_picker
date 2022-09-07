import pandas as pd
import numpy as np
import streamlit as st
import os
import json
from datetime import date
from datetime import timedelta


@st.cache
def load_data(folder: str) -> pd.DataFrame:
    pdf, rt, im, yt = read_jsons_to_pandas(folder)
    pdf = join_dataframes(pdf, [rt, im, yt])
    pdf = cast_col(pdf, ['year', 'tomato_score', 'tomato_reviews', 'audience_score'], int)
    pdf = cast_col(pdf, ['Budget', 'Gross worldwide'], str)
    pdf = pdf.set_index('name', append=False)
    return pdf.sort_values(by='tomato_score', ascending=False)


def read_jsons_to_pandas(folder: str):
    df = (pd.read_json(folder + 'title_data.json')
          .assign(main_genre=lambda x: x['main_genre'].fillna(''),
                  cast=lambda x: x['cast'].apply(lambda z: [] if z is None else z),
                  title=lambda x: x['name']
                  )
          )
    rt = pd.read_json(folder + 'tomato_data.json').drop(columns=['name', 'url'])
    im = (pd.read_json(folder + 'imdb_data.json')
          .drop(columns=['title', 'name', 'url'])
          .assign(Budget=lambda x: x['Budget'].map(str))
          )
    yt = pd.read_json(folder + 'youtube_data.json').drop(columns=['name', 'url'])
    return df, rt, im, yt


def join_dataframes(left_df: pd.DataFrame, right_dfs: list) -> pd.DataFrame:
    for df in right_dfs:
        left_df = left_df.merge(df, how='left', on='title_id')
    return left_df


def cast_col(df: pd.DataFrame, int_cols: list, col_type) -> pd.DataFrame:
    for c in int_cols:
        df[c] = df[c].fillna(0).map(col_type)
    return df


def read_available_markets(folder: str) -> list:
    dir_list = os.listdir(folder + 'markets')
    return [d.replace('.json', '').replace('titles_', '') for d in dir_list]


def filter_data_by_market(folder: str, market: str, df: pd.DataFrame) -> pd.DataFrame:
    f = open(f'{folder}markets/titles_{market}.json')
    title_ids = json.load(f)
    df = df[df['title_id'].map(str).isin(title_ids)]
    return df


def show_title(title: str, url: str, img: str):
    md = f'<a href={url} target="_blank"><h1>{title}</h1></a>'
    st.markdown(md, unsafe_allow_html=True)
    st.image(img)


def show_tomato_rating(score: int):
    if score >= 60:
        rating_img_url = 'https://upload.wikimedia.org/wikipedia/commons/5/5b/Rotten_Tomatoes.svg'
    else:
        rating_img_url = 'https://upload.wikimedia.org/wikipedia/commons/5/52/Rotten_Tomatoes_rotten.svg'

    md = f'<h1><img style="width:50px" src="{rating_img_url}" alt="rotten"> {score}</h1>'
    st.markdown(md, unsafe_allow_html=True)


def show_trailer(video_id: str):
    md = f'<iframe width="640" height="360" src="https://www.youtube.com/embed/{video_id}" \
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; \
    gyroscope; picture-in-picture" allowfullscreen></iframe>'
    st.markdown(md, unsafe_allow_html=True)


def show_imdb_data(row):
    for i in ['imdb_score', 'Gross worldwide', 'Budget']:
        if isinstance(row[i], str):
            if row[i] not in ['', 'nan', None, np.nan, '0']:
                st.markdown(f'<b>{i}:</b> {row[i]}', unsafe_allow_html=True)
        elif not np.isnan(row[i]):
            st.markdown(f'<b>{i}:</b> {str(row[i])}', unsafe_allow_html=True)


def filter_on_list(df: pd.DataFrame, col: str, text: str) -> pd.DataFrame:
    options = df[~df[col].isnull()][col]
    all_options = [item for element in options for item in element]
    all_options = list(set(all_options))
    choice = st.multiselect(text, sorted(all_options))
    if len(choice) > 0:
        df = df[df[col].apply(lambda x: np.intersect1d(x, choice).size > 0)]
    return df


def filter_on_year(df: pd.DataFrame) -> pd.DataFrame:
    year_options = np.array([y for y in df['year'] if (y not in [0, None]) & (y <= date.today().year)])
    min_year = date(year_options.min(), 1, 1)
    max_year = date(year_options.max() + 1, 1, 1) - timedelta(days=1)
    if min_year != max_year:
        choice = st.slider('release year', min_value=min_year, value=[min_year, max_year])
        if (choice[0] != min_year) | (choice[1] != max_year):
            df = df[(df['year'] >= choice[0].year) & (df['year'] <= choice[1].year)]
            st.write(f'filtered between {choice[0].year} and {choice[1].year}')
    return df


def filter_on_critics(df: pd.DataFrame, watch_type: str):
    max_critics = int(df['tomato_reviews'].max())
    min_critics = int(df['tomato_reviews'].min())
    if (watch_type == 'movie') & (max_critics != min_critics):
        max_critics = int(df['tomato_reviews'].max())
        min_critics = st.slider('minimum no. of critics', max_value=max_critics)
        df = df[df['tomato_reviews'] >= min_critics]
    return df
