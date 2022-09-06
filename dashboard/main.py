from dashboard_functions import load_data, filter_data_by_market, read_available_markets, show_imdb_data
from dashboard_functions import show_tomato_rating, filter_on_list, show_trailer, show_title, filter_on_year
from dashboard_functions import filter_on_critics
import streamlit as st


# https://docs.streamlit.io/library/cheatsheet

folder = '../data/'

st.set_page_config(page_icon='👾', page_title='movie selector')
st.title('movie finder')
st.write('this app uses data from netflix, rotten tomatoes and imdb to help you choose which movie to watch')

# read data
pdf = load_data(folder)
df = pdf.copy(deep=True)

# choose markets
markets = read_available_markets()
market = st.selectbox('choose a market', markets)
df = filter_data_by_market(folder, market, df)

# filter selection
with st.expander('expand to view filters', expanded=True):
    # filter by movie or tv
    watch_type = st.selectbox('movie or tv', df['type'].unique())
    df = df[df['type'] == watch_type]

    df = filter_on_list(df, col='all_genres', text='choose a genre')
    df = filter_on_list(df, col='cast', text='choose some actors')
    df = filter_on_year(df)
    df = filter_on_critics(df, watch_type)

st.write(f'{len(df)} titles available')

# display data
with st.expander('expand to view films', expanded=True):
    cols = ['year', 'runtime', 'main_genre', 'imdb_score']
    cols = cols + ['tomato_score', 'audience_score'] if watch_type == 'movie' else cols
    st.dataframe(df[cols].rename(columns={c: c.replace('_', ' ') for c in cols}))

# choose film
title = st.selectbox('Choose a film', sorted(df.index))
title_row = df.loc[title]
with st.container():
    try:
        with st.spinner(text='In progress'):

            show_title(title, title_row['url'], title_row['img'])
            if watch_type == 'movie':
                show_tomato_rating(title_row['tomato_score'])
                st.markdown('<b>number of critics:</b> ' + str(title_row['tomato_reviews']), unsafe_allow_html=True)
            st.markdown('<b>genre:</b> ' + ', '.join(title_row['all_genres']), unsafe_allow_html=True)
            st.markdown('<b>cast:</b> ' + ', '.join(title_row['cast']), unsafe_allow_html=True)
            st.markdown('<b>runtime:</b> ' + title_row['runtime'], unsafe_allow_html=True)
            st.markdown('<b>year:</b> ' + str(title_row['year']), unsafe_allow_html=True)
            st.markdown('<b>age rating:</b> ' + title_row['maturity'], unsafe_allow_html=True)
            show_imdb_data(title_row)
            st.write(title_row['synopsis'])
            show_trailer(title_row['video_id'])

            st.success('Done')
    except AttributeError:
        st.error('oops! please choose another film.')
