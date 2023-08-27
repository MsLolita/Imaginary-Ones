import pyuseragents

from core.utils import Session


class Discord(Session):
    def __init__(self, auth_token: str, proxy: str):
        self.headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': auth_token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/oauth2/authorize',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': pyuseragents.random(),
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'Asia/Riyadh',
        }

        self.proxy = proxy

        super().__init__()

    def connect(self, connection_link: str):
        json_data = {
            'permissions': '0',
            'authorize': True,
        }

        response = self.session.post(connection_link, json=json_data)

        return response.json()["location"]
