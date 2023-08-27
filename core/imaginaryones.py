from random import choice

import requests
import pyuseragents

from core.utils import str_to_file, logger, Session
from string import ascii_lowercase, digits

from core.utils.socials import Discord
from inputs.config import (
    MOBILE_PROXY,
    MOBILE_PROXY_CHANGE_IP_LINK
)


class ImaginaryOnes(Session):
    uuid = "MF1f7cbbc42a"
    api_token = "bce6be8e01cd681565f472b097c3479387243e24"

    def __init__(self, email: str, address: str, discord_token: str, proxy: str = None, ref_code: str = None):
        self.email = email
        self.address = address.lower()
        self.discord_token = discord_token
        self.proxy = ImaginaryOnes.get_proxy(proxy)
        self.main_ref_code = ref_code

        self.headers = {
            'authority': 'app.referralhero.com',
            'accept': '*/*',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://carnival-prelaunch.imaginaryones.com',
            'referer': 'https://carnival-prelaunch.imaginaryones.com/',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': pyuseragents.random(),
        }

        super().__init__()

        self.fingerprint = ImaginaryOnes.generate_fingerprint(32)
        self.user_id = None
        self.ref_code = None
        self.extra_field = None

    @staticmethod
    def get_proxy(proxy: str):
        if MOBILE_PROXY:
            ImaginaryOnes.change_ip()
            proxy = MOBILE_PROXY

        if proxy is not None:
            return f"http://{proxy}"

    @staticmethod
    def change_ip():
        requests.get(MOBILE_PROXY_CHANGE_IP_LINK)

    def register(self):
        resp_json = self.create_account()
        data = resp_json["data"]

        self.user_id = data["id"]
        self.ref_code = data["code"]

        self.retrieve_account()

        # logger.info(f"{self.email} | Registered!")

    def create_account(self):
        return self.subscriber_send()

    def retrieve_account(self):
        return self.subscriber_send(one_click_signup=True)

    def subscriber_send(self, one_click_signup: bool = False):
        url = f'https://app.referralhero.com/widget/{ImaginaryOnes.uuid}/post'

        json_data = {
            'test_mode': False,
            'check_status': False,
            'one_click_signup': True,
            'email': self.email,
            'crypto_wallet_address': self.address,
            'uuid': ImaginaryOnes.uuid,
            'host': 'https://carnival-prelaunch.imaginaryones.com/',
            'source': '',
            'campaign': '',
            'fingerprint': self.fingerprint,
            'require_leaderboard': False,
            'subscribe_page_url': 'https://carnival-prelaunch.imaginaryones.com/?mwr=',
            'landing_page_url': 'https://carnival-prelaunch.imaginaryones.com/?mwr=',
        }

        if one_click_signup:
            json_data["terms_conditions"] = True
        else:
            json_data["referrer"] = self.main_ref_code
            json_data["phone_number"] = ""
            json_data["status"] = 'registered'

        response = self.session.post(url, json=json_data)

        return response.json()

    def connect_ds(self):
        headers = {
            'authority': 'world-api-svr.imaginaryones.com',
            'accept': '*/*',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://carnival-prelaunch.imaginaryones.com',
            'referer': 'https://carnival-prelaunch.imaginaryones.com/',
            'user-agent': pyuseragents.random(),
        }

        ds_link = self.get_ds_auth_link(headers)

        discord = Discord(self.discord_token, self.proxy)
        connection_link = discord.connect(ds_link)
        connection_code = connection_link.split("&access_token=")[1].split("&expires_in")[0]

        data = self.send_connection_code(headers, connection_code)
        self.extra_field = data["data"]["user"]["id"]

        self.update_user_ds_id()
        self.promote()

    def get_ds_auth_link(self, headers: dict):
        url = 'https://world-api-svr.imaginaryones.com/production/auth/discord'

        params = {
            'mode': 'carnival-prelaunch',
            'data': self.email,
        }

        response = self.session.get(url, params=params, headers=headers)

        return response.json()["redirectTo"]

    def send_connection_code(self, headers: dict, connection_code: str):
        url = 'https://world-api-svr.imaginaryones.com/production/auth/discord/join'

        json_data = {
            'access_token': connection_code,
        }

        response = self.session.put(url, headers=headers, json=json_data)

        return response.json()

    def update_user_ds_id(self):
        url = f'https://app.referralhero.com/api/v2/lists/{ImaginaryOnes.uuid}/subscribers/{self.user_id}'

        params = {
            'api_token': ImaginaryOnes.api_token,
            'extra_field': self.extra_field,
            'crypto_wallet_address': self.address,
        }

        response = self.session.post(url, params=params)

        return response.json()

    def promote(self):
        url = f'https://app.referralhero.com/api/v2/lists/{ImaginaryOnes.uuid}/subscribers/{self.user_id}/promote'

        params = {
            'api_token': ImaginaryOnes.api_token,
        }

        response = self.session.post(url, params=params)

        return response.json()

    def claim_chest(self):
        url = f'https://app.referralhero.com/api/v2/lists/{ImaginaryOnes.uuid}/subscribers/{self.user_id}/unlock_promoted_reward'

        params = {
            'api_token': ImaginaryOnes.api_token,
            'reward_id': '13280',
        }

        resp = self.session.post(url, params=params)

        return resp.json()["response"] == "reward_unlocked"

    def logs(self):
        file_msg = f"{self.email}|{self.address}|{self.ref_code}|{self.proxy}"
        str_to_file(f"./logs/success.txt", file_msg)
        logger.success(f"{self.email} | Register")

    def logs_fail(self, msg: str = ""):
        file_msg = f"{self.email}|{self.address}|{self.ref_code}|{self.proxy}"
        str_to_file(f"./logs/failed.txt", file_msg)
        logger.error(f"{self.email}")

    @staticmethod
    def generate_fingerprint(k=10):
        return ''.join([choice(ascii_lowercase + digits) for _ in range(k)])
