from bs4 import BeautifulSoup
import requests


class YouTubeScraper:
    base_url = 'https://www.youtube.com'
    search_base_url = base_url + '/results?search_query={}'
    page_url = None

    def __init__(self, title_id: str, title: str, show_type: str = None):
        self.title_id = title_id
        self.title = title
        self.show_type = show_type
        self.search_url = self.build_search_url()
        self.data = {'name': self.title, 'title_id': self.title_id}

    def build_search_url(self):
        search_term = self.title.replace(' ', '+').replace('#', '%23') + '+trailer'
        return self.search_base_url.format(search_term)

    def query(self):
        text = requests.get(self.search_url).text
        html = BeautifulSoup(text, 'html.parser')
        result = str(html).split('"videoId":')

        if len(result) > 0:
            video_id = result[1].split(',')[0].replace('"', '')
            self.page_url = self.base_url + '/watch?v=' + video_id
            self.data['video_id'] = video_id
            self.data['url'] = self.page_url
