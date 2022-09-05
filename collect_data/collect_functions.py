import time
import random
import json
import os
import netflix


def query_titles_by_market(countries: list, write_folder: str):
    """
    finding all titles by market & genre and saving to json
    :param countries: which countries do we want to query
    :param write_folder: where to save the data
    """
    for c in countries:
        title_ids = netflix.query_genres(country=c)
        with open(f'{write_folder}/markets/titles_{c}.json', 'w') as f:
            json.dump(title_ids, f, indent=4)
        print(f'{c} genres queried')


def read_all_titles_by_market(read_folder: str) -> list:
    """
    :param read_folder: where to read data from
    :return: all unique title ids for all markets
    """
    path = f'{read_folder}/markets'
    dir_list = os.listdir(path)
    all_title_ids = []
    for d in dir_list:
        all_title_ids.extend(read_data(path, '/' + d))
    all_title_ids = list(set(all_title_ids))
    print(f'total titles: {len(all_title_ids)}')
    return all_title_ids


def find_missing_titles_from_netflix_data(all_title_ids: list, read_folder) -> list:
    """
    read stored title data to find new titles without data
    :param all_title_ids: all title ids found on netflix
    :param read_folder: where to read the data from
    :return: title ids missing from stored data
    """
    f = open(f'{read_folder}/title_data.json')
    all_title_data = json.load(f)
    stored_title_ids = [t['title_id'] for t in all_title_data]
    missing_title_ids = [t for t in all_title_ids if t not in stored_title_ids]
    print(f'missing titles: {len(missing_title_ids)}')
    return missing_title_ids


def read_data(read_folder: str, file_path: str) -> list:
    """
    :param read_folder: folder where data is
    :param file_path: file path where data is
    :return: json loaded data
    """
    f = open(read_folder + file_path)
    return json.load(f)


def query_missing_netflix_data(missing_title_ids: list, read_folder: str, write_folder: str):
    """
    querying netflix data for missing titles
    :param missing_title_ids: title ids missing from stored data
    :param read_folder: where to read data from
    :param write_folder: where to save the new data
    """
    queried_title_data = netflix.query_titles(missing_title_ids)
    all_title_data = read_data(read_folder, '/title_data.json')
    all_title_data.extend(queried_title_data)
    with open(f'{write_folder}/title_data.json', 'w') as f:
        json.dump(all_title_data, f, indent=4)


def query_missing_data(read_folder: str, write_folder: str, file_path: str, object_type):
    """
    queries all data that is missing for particular type of scraping class
    :param read_folder: where to read data from
    :param write_folder: where to save data
    :param file_path: file name of stored data
    :param object_type: type of scraping class
    """

    all_data = read_data(read_folder, file_path)
    all_title_data = read_data(read_folder, '/title_data.json')

    stored_titles = [t['title_id'] for t in all_data]
    missing_titles = [{'name': t['name'], 'title_id': t['title_id'], 'type': t['type']}
                      for t in all_title_data
                      if t['title_id'] not in stored_titles
                      ]

    print(f'titles to query: {len(missing_titles)}')

    queried_data = query(missing_titles, object_type)
    all_data.extend(queried_data)
    with open(write_folder + file_path, 'w') as f:
        json.dump(all_data, f, indent=4)


def query(title_data: list, object_type) -> list:
    """
    :param title_data: list of title ids and title names to be scraped
    :param object_type: scraper type
    :return: data queried
    """
    queried_data = []
    for t in title_data:
        try:
            o = object_type(t['title_id'], t['name'], t['type'])
            o.query()
            queried_data.append(o.data)
            print(f'done: {t["name"]}')
        except Exception as e:
            print(f'error with {t["name"]}')
            print(object_type)
            print(e)
        time.sleep(random.random())
    return queried_data
