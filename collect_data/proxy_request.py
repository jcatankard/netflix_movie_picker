import requests
import random
import pandas as pd
from bs4 import BeautifulSoup


class ProxyRequest:

    ip_address = None
    protocol = None
    proxy = None

    def __init__(self, country: str):

        self.country = country.upper()
        self.available_proxies = self.query_proxies()

    def query_proxies(self):
        text = requests.get('https://free-proxy-list.net/').text
        df = pd.read_html(text)[0]
        df = df[(df['Code'] == self.country)].reset_index(drop=True)
        return df

    def choose_proxy(self):
        row = random.randint(0, len(self.available_proxies) - 1)
        self.ip_address = self.available_proxies['IP Address'][row]
        https = self.available_proxies['Https'][row]
        self.port = str(self.available_proxies['Port'][row])
        self.protocol = 'https' if https == 'yes' else 'http'
        self.proxy = self.protocol + '://' + self.ip_address + ':' + self.port

    def query_request_text_from_url(self, request_url: str):
        self.choose_proxy()
        try:
            response = requests.get(request_url, proxies={self.protocol: self.proxy}, verify=False)
            response = response.text
            return BeautifulSoup(response, 'html.parser')
        except Exception as e:
            return self.query_request_text_from_url(request_url)
