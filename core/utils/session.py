import requests


class Session:
    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(self.headers)
        self.session.proxies.update({'https': self.proxy, 'http': self.proxy})
