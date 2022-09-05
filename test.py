import json
import netflix
import imdb
import tomatoes


read_folder = 'data'
write_folder = 'data'
countries = ['us']

# finding all titles by market & genre and saving to json
"""
for c in countries:
    title_ids = netflix.query_genres(country=c)
    with open(f'{write_folder}/titles_{c}.json', 'w') as f:
        json.dump(title_ids, f, indent=4)
"""


# reading all titles by market
all_title_ids = []
for c in countries:
    f = open(f'{read_folder}/titles_{c}.json')
    all_title_ids.extend(json.load(f))
all_title_ids = list(set(all_title_ids))
print(f'total titles: {len(all_title_ids)}')


# read stored title data to find new titles without data
f = open(f'{read_folder}/title_data.json')
all_title_data = json.load(f)
stored_title_ids = [t['title_id'] for t in all_title_data]
missing_title_ids = [t for t in all_title_ids if t not in stored_title_ids]
print(f'missing titles: {len(missing_title_ids)}')


# querying netflix data for missing titles
queried_title_data = netflix.query_titles(missing_title_ids)
all_title_data.extend(queried_title_data)
with open(f'{write_folder}/title_data.json', 'w') as f:
    json.dump(all_title_data, f, indent=4)


def write_missing_data(read_folder: str, write_folder: str, file_path: str, query_function, all_title_ids: list):
    f = open(read_folder + file_path)
    all_data = json.load(f)
    stored_titles = [t['title_id'] for t in all_data]
    missing_titles = [{'name': t['name'], 'title_id': t['title_id']} for t in all_title_ids
                      if t['title_id'] not in stored_titles
                      ]

    print(f'titles_to_query: {len(missing_titles)}')

    queried_data = query_function(missing_titles)
    all_data.extend(queried_data)
    with open(write_folder + file_path, 'w') as f:
        json.dump(all_data, f, indent=4)


write_missing_data(read_folder, write_folder, '/tomato_data.json', tomatoes.query_tomatoes, all_title_ids)
write_missing_data(read_folder, write_folder, '/imdb_data.json', imdb.query_imdb, all_title_ids)
