import time
import requests
import random
import pandas as pd


class ProxyRequest:
    """
    proxy request is to change the location our query is made from
    it randomly chooses a proxy each time it is called
    best to initiate once for target market then call query_request_text_from_url for each individual query
    """

    ip_address = None
    protocol = None
    proxy = None
    port = None

    def __init__(self, country: str):

        self.country = country.upper()
        self.available_proxies = self.query_proxies()

    def query_proxies(self) -> pd.DataFrame:
        """
        :return: dataframe of proxies available for particular market
        """
        text = requests.get('https://free-proxy-list.net/').text
        df = pd.read_html(text)[0]
        return df[(df['Code'] == self.country)]

    def remove_proxy(self):
        """
        :return: removes proxy if it failed so we don't lose time trying it again
        """
        self.available_proxies = self.available_proxies[self.available_proxies['IP Address'] != self.ip_address]

    def choose_proxy(self):
        """
        :return: chooses a random proxy from available proxies
        """
        row = random.randint(0, len(self.available_proxies) - 1)
        self.available_proxies = self.available_proxies.reset_index(drop=True)
        self.ip_address = self.available_proxies['IP Address'][row]
        https = self.available_proxies['Https'][row]
        self.port = str(self.available_proxies['Port'][row])
        self.protocol = 'https' if https == 'yes' else 'http'
        self.proxy = self.ip_address + ':' + self.port

    def query_request_text_from_url(self, request_url: str, is_proxy=False) -> str:
        """
        :param request_url: target url
        :param is_proxy: use proxy or not
        :return: text from target url
        """
        try:
            if is_proxy:
                self.choose_proxy()
                print(self.proxy)
                proxies = {'https': self.proxy, 'http': self.proxy}
            else:
                time.sleep(random.random())  # avoiding pinging the server directly over and over
                proxies = None
            response = requests.get(request_url, proxies=proxies)
            return response.text
        except Exception as e:
            self.remove_proxy()
            return self.query_request_text_from_url(request_url)
