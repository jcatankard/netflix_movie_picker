from collect_functions import query_titles_by_market, read_all_titles_by_market, query_missing_data
from collect_functions import find_missing_titles_from_netflix_data, query_missing_netflix_data
import tomatoes
import imdb
import youtube

read_folder = '../data'
write_folder = '../data'  # change for testing
countries = ['es']

query_titles_by_market(countries, write_folder)
all_title_ids = read_all_titles_by_market(read_folder)
missing_title_ids = find_missing_titles_from_netflix_data(all_title_ids, read_folder)
query_missing_netflix_data(missing_title_ids, read_folder, write_folder)
query_missing_data(read_folder, write_folder, '/tomato_data.json', tomatoes.TomatoScraper)
query_missing_data(read_folder, write_folder, '/imdb_data.json', imdb.ImdbScraper)
query_missing_data(read_folder, write_folder, '/youtube_data.json', youtube.YouTubeScraper)
