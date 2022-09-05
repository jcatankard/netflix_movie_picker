from bs4 import BeautifulSoup
import requests


class ImdbScraper:
    base_url = 'https://www.imdb.com'
    page_url = None

    def __init__(self, title_id: str, title: str, show_type: str):
        self.title_id = title_id
        self.title = title
        self.show_type = show_type
        self.search_url = self.build_search_url()
        self.data = {'name': self.title, 'title_id': self.title_id}

    def build_search_url(self):
        search_term = self.title.replace(' ', '%20')
        if self.show_type == 'tvshow':
            return f'{self.base_url}/find?q={search_term}&s=tt&ttype=tv&ref_=fn_tv'
        elif self.show_type == 'movie':
            return f'{self.base_url}/find?q={search_term}&s=tt&ttype=ft&ref_=fn_ft'

    def query(self):
        text = requests.get(self.search_url).text
        html = BeautifulSoup(text, 'html.parser')
        result = html.find(class_='findResult odd')
        if result is not None:
            self.page_url = self.base_url + result.find('a').get('href')
            self.data['url'] = self.page_url
            self.query_page()

    def query_page(self):
        text = requests.get(self.page_url).text
        html = BeautifulSoup(text, 'html.parser')

        imdb_score = html.find(class_='sc-7ab21ed2-1 jGRxWM')
        imdb_score = None if imdb_score is None else imdb_score.get_text()
        self.data['imdb_score'] = imdb_score

        sections = html.find_all('section')
        box_office = list(filter(lambda x: x.get('data-testid') == 'BoxOffice', sections))
        if len(box_office) > 0:
            box_office = box_office[0]
            parts = box_office.find_all(class_='ipc-metadata-list__item sc-6d4f3f8c-2 fJEELB')
            for p in parts:
                text = p.find(class_='ipc-metadata-list-item__label')
                text = None if text is None else text.get_text()
                if text is not None:
                    value = p.find(class_='ipc-metadata-list-item__list-content-item')
                    self.data[text] = None if value is None else value.get_text().replace(' (estimated)', '')
