import proxy_request
from bs4 import BeautifulSoup


class Page:
    base_url = 'https://www.netflix.com/'
    html = None
    queried_urls = []
    titles = []
    genres = []

    def __init__(self, page_type: str, page_id: str, country: str = None, lang: str = 'en'):
        self.page_id = str(page_id)
        self.country = country
        self.lang = lang
        self.page_type = page_type
        self.url = self.build_url()

    def build_url(self):
        if self.country is None:
            return self.base_url + self.page_type + self.page_id
        else:
            return self.base_url + self.country + '-' + self.lang + '/' + self.page_type + self.page_id

    def query(self, r: proxy_request.ProxyRequest):
        text = r.query_request_text_from_url(self.url)
        self.html = BeautifulSoup(text, 'html.parser')
        a_tags = self.html.find_all('a')
        self.queried_urls = [a.get('href') for a in a_tags]
        self.genres = self.find_pages('/browse/genre/')
        self.titles = self.find_pages('/title/')

    def find_pages(self, search: str):
        urls = [u for u in self.queried_urls if search in u]
        return [u.split(search)[1] for u in urls]


class Genre(Page):
    page_type = 'browse/genre/'

    def __init__(self, page_id: str, country: str, lang: str = 'en'):
        super().__init__(self.page_type, page_id, country, lang)

    def genre_name(self):
        result = self.html.find(class_='nm-collections-metadata-title')
        return None if result is None else result.get_text()

    @property
    def data(self):
        return {'genre_id': self.page_id, 'url': self.url, 'name': self.genre_name()}


class Title(Page):
    page_type = 'title/'
    data = {}

    def __init__(self, page_id: str, country: str = None, lang: str = 'en'):
        super().__init__(self.page_type, page_id, country, lang)

    @property
    def data(self):
        title = self.html.find(class_='title-title').get_text()

        synopsis = self.html.find(class_='title-info-synopsis')
        synopsis = None if synopsis is None else synopsis.get_text()

        cast = self.html.find(class_='title-data-info-item-list')
        cast = [] if cast is None else cast.get_text().split(',')
        cast = [c.strip() for c in cast]

        main_genre = self.html.find(class_='title-info-metadata-item item-genre')
        main_genre = None if main_genre is None else main_genre.get_text()

        year = self.html.find(class_='title-info-metadata-item item-year')
        year = None if year is None else year.get_text()

        maturity = self.html.find(class_='title-info-metadata-item item-maturity')
        maturity = None if maturity is None else maturity.get_text()

        runtime = self.html.find(class_='title-info-metadata-item item-runtime')
        runtime = None if runtime is None else runtime.get_text()

        img = self.html.find('picture')
        img = None if img is None else img.find('source').get('srcset')

        all_genres = self.html.find_all(class_='more-details-item item-genres')
        all_genres = [] if all_genres is None else [i.get_text().replace(', ', '') for i in all_genres]
        all_genres = list(set(all_genres))

        episodes = self.html.find(class_='episode')
        title_type = 'movie' if episodes is None else 'tvshow'

        return {'title_id': self.page_id,
                'name': title,
                'type': title_type,
                'main_genre': main_genre,
                'all_genres': all_genres,
                'url': self.url,
                'img': img,
                'year': year,
                'maturity': maturity,
                'runtime': runtime,
                'synopsis': synopsis,
                'cast': cast
                }


def query_genres(country: str, start_id: str = '34399') -> list:
    # initiate proxy handler
    r = proxy_request.ProxyRequest(country=country)
    unqueried = [start_id]
    queried = []
    titles = []

    while len(unqueried) > 0:

        new_id = unqueried[0]
        unqueried.remove(new_id)
        queried.append(new_id)

        new_page = Genre(new_id, country=country)
        new_page.query(r)

        [unqueried.append(g) for g in new_page.genres if (g not in unqueried) & (g not in queried)]
        [queried.append(g) for g in new_page.genres if g not in queried]

        [titles.append(t) for t in new_page.titles if t not in titles]
        print(country, 'genre:', new_page.data['name'], new_page.url)

    return titles


def query_titles(titles: list) -> list:
    # initiate proxy handler
    r = proxy_request.ProxyRequest(country='us')
    queried_data = []
    for t in titles:
        new_page = Title(t)
        new_page.query(r)
        queried_data.append(new_page.data)
        print(f'netflix done: {new_page.data["name"]}')
    return queried_data

# titles = query_genres('us')
# print(len(titles), 'us')
# 4520
titles = query_genres('gb')
print(len(titles), 'gb')
