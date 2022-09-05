from bs4 import BeautifulSoup
import requests


class TomatoScraper:
    search_base_url = 'https://www.rottentomatoes.com/search?search={}'
    page_url = None

    def __init__(self, title_id: str, title: str, show_type: str):
        self.title_id = title_id
        self.title = title
        self.show_type = 'movie' if show_type == 'movie' else 'tv'
        self.search_url = self.build_search_url()
        self.data = {'name': self.title, 'title_id': self.title_id}

    def build_search_url(self):
        search_term = self.title.replace(' ', '%20')
        return self.search_base_url.format(search_term)

    def query(self):
        text = requests.get(self.search_url).text
        html = BeautifulSoup(text, 'html.parser')
        result_sections = html.find_all('search-page-result')
        results = list(filter(lambda x: x.get('type') == self.show_type, result_sections))
        if len(results) > 0:
            results = results[0]
            result = results.find('search-page-media-row')  # first result
            self.page_url = result.find('a').get('href')
            self.data['url'] = self.page_url
            self.query_page()

    def query_page(self):
        text = requests.get(self.page_url).text
        html = BeautifulSoup(text, 'html.parser')
        score_board = html.find('score-board')
        if score_board is not None:
            audience_state = score_board.get('audiencestate')
            audience_score = score_board.get('audiencescore')
            audience_score = None if audience_score == '' else int(audience_score)

            tomato_meter_state = score_board.get('tomatometerstate')
            tomato_score = score_board.get('tomatometerscore')
            tomato_score = None if tomato_score == '' else int(tomato_score)

            critic_count = html.find(class_='scoreboard__link scoreboard__link--tomatometer')
            critic_count = None if critic_count is None else critic_count.get_text().replace(' Reviews', '')
            critic_count = None if critic_count is None else int(critic_count)

            audience_count = html.find(class_='scoreboard__link scoreboard__link--audience')
            audience_count = None if audience_count is None else audience_count.get_text()

            self.data['tomato_score'] = tomato_score
            self.data['tomato_reviews'] = critic_count
            self.data['tomato_meter_state'] = tomato_meter_state
            self.data['audience_score'] = audience_score
            self.data['audience_reviews'] = audience_count
            self.data['audience_state'] = audience_state
