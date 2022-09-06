# Netflix Movie Picker app

I always wanted a more efficient way to choose which film to watch rather than endlessly scrolling through Netflix.
I often use Rotten Tomatoes as a quick (albeit not entirely reliable) indicator to determine if a film is worth watching.

So here is the "Netflix Movie Picker" app.

## front end
The front end is a Streamlit dashboard that allows you to easily select a movie or tv series based on your chosen filters.

## backend
The backend systematically scrapes data from:
 - Netflix (title, genres, cast, synopsis, image, runtime, age rating, movie or tv series)
 - Rotten Tomatoes (tomato meter, number of critics, audience score, number of audience ratings)
 - IMDB (IMDB rating, film budget, box office)
 - YouTube (video identifier for embedding the trailer into the dashboard)

The scraping stores a single json file with all the Netflix title data and then individual json files for the title ids available by market.
This means we don't duplicate the data for each title and will make scraping data for multiple markets more efficient.

Data for Rotten Tomatoes, YouTube and IMDB are stored in their own files with the title id as a lookup reference.
This means it is easier it is easier to replenish the data for one without having to update all.

When the data is refreshed, it will check which titles are available vs the data we have currently stores to save having to scrape all data again.

## tbd
Currently, the app only features titles from Netflix ES. I plan to implement the use of proxies to scrape titles from other markets.

Possibly try building the scraping functionality in Go instead of Python.

Currently, the backend can be triggered manually or automatically as a job. I could add a button in the dashboard to trigger an update.


## folder structure
 - collect_data
   - classes for scraping each particular website (Netflix, YouTube, Rotten Tomatoes, IMDB)
   - main.py (file to be triggered to update data)
   - collect_functions.py (functions that are abstracted from the main.py)
   - proxy_request.py (a handler to manage requests using a proxy. not currently implemented.)
 - dashboard
   - main.py (launches dashboard with "python -m streamlit run main.py)
   - dashboard_functions.py (functions that are abstracted from the main.py)
 - data
   - markets (contains json files by market with the title ids available in each)
   - json data files for each of Netflix, YouTube, Rotten Tomatoes, IMDB
   - test (where data is written during test executions)
 - README.md
 - requirements.txt