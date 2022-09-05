from dashboard_functions import load_data
from dashboard_functions import read_available_markets
import pandas as pd
import numpy as np
import json
from datetime import date
from datetime import timedelta
import streamlit as st


# https://docs.streamlit.io/library/cheatsheet

st.set_page_config(page_icon='👾', page_title='movie selector')
st.title('movie finder')
st.write('this app uses data from netflix, rotten tomatoes and imdb to help you choose which movie to watch')

# read data
pdf = load_data()
df = pdf.copy(deep=True)

# choose markets
markets = read_available_markets()
market = st.selectbox('choose a market', markets)
f = open(f'../data/markets/titles_{market}.json')
title_ids = json.load(f)
st.write(market, len(title_ids))
df = df[df['title_id'].map(str).isin(title_ids)]

# filter selection
with st.expander('expand to view filters', expanded=True):
    # filter by movie or tv
    watch_type = df['type'].unique()
    watch_type = st.selectbox('movie or tv', watch_type)
    df = df[df['type'] == watch_type]

    # filter by genre
    genres = [item for element in df['all_genres'] for item in element]
    genres = np.unique(genres)
    chosen_genre = st.multiselect('choose a genre', genres)
    if len(chosen_genre) > 0:
        df = df[df['all_genres'].apply(lambda x: np.intersect1d(x, chosen_genre).size > 0)]

    # filter by cast
    actors = df[~df['cast'].isnull()]['cast']
    actors = [item for element in actors for item in element]
    actors = np.unique(actors)
    actors = st.multiselect('choose a actor', actors)
    if len(actors) > 0:
        df = df[df['cast'].apply(lambda x: np.intersect1d(x, actors).size > 0)]

    # filter by year
    year_choices = np.array([y for y in df['year'] if y not in [0, None]])
    min_year = date(year_choices.min(), 1, 1)
    max_year = date(date.today().year + 1, 1, 1) - timedelta(days=1)
    year = st.slider('release year', min_value=min_year, value=[min_year, max_year])
    if (year[0] == min_year) & (year[1] == max_year):
        pass
    else:
        df = df[(df['year'] >= year[0].year) & (df['year'] <= year[1].year)]

    # filter by runtime
    maturity = sorted(df['maturity'].unique())
    maturity = st.multiselect('maturity rating', maturity)
    if len(maturity) > 0:
        df = df[df['maturity'].isin(maturity)]

st.write(f'{len(df)} titles available')

# display data
with st.expander('expand to view films', expanded=True):
    # cols = ['title', 'genre', 'tomato_score', 'imdb_score', 'budget', 'gross', 'image']
    # st.markdown(df[cols].to_html(escape=False, index=False, justify='center'), unsafe_allow_html=True)
    cols = ['year', 'runtime', 'main_genre', 'all_genres', 'cast'] # , 'tomato_score', 'imdb_score', 'budget', 'gross']
    st.dataframe(df[cols])

# choose film
title = st.selectbox('Choose a film', sorted(df.index))
title_row = df.loc[title]

with st.container():
    try:
        with st.spinner(text='In progress'):

            # display image
            url = title_row['url']
            md = f'<a href={url} target="_blank"><h1>{title}</h1></a>'
            st.markdown(md, unsafe_allow_html=True)
            st.image(title_row['img'])

            # display tomato score
            # tomato_score = title_row['tomato_score']
            # tomato_link = title_row['tomato_link']
            # if tomato_score >= 60:
            #     rating_img_url = 'https://upload.wikimedia.org/wikipedia/commons/5/5b/Rotten_Tomatoes.svg'
            # else:
            #     rating_img_url = 'https://upload.wikimedia.org/wikipedia/commons/5/52/Rotten_Tomatoes_rotten.svg'
            # md = f"""
            # <a href="{tomato_link}">
            # <h1><img style="width:50px" src="{rating_img_url}" alt="rotten"> {tomato_score}</h1>
            # </a>
            # """
            # st.markdown(md, unsafe_allow_html=True)

            # display imdb link
            # imdb_link = title_row['imdb_link']
            # st.markdown(f'<h1><a href="{imdb_link}">IMDB page</a></h1>', unsafe_allow_html=True)

            # movie data
            st.write('genre: ' + ', '.join(title_row['all_genres']))
            st.write('cast: ' + ', '.join(title_row['cast']))
            st.write(title_row['synopsis'])
            st.success('Done')
    except AttributeError:
        st.error('oops! please choose another film.')

# add trailer
md = '<iframe width="640" height="360" src="https://www.youtube.com/embed/v1AsEbg2y-M" \
frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; \
gyroscope; picture-in-picture" allowfullscreen></iframe>'
st.markdown(md, unsafe_allow_html=True)