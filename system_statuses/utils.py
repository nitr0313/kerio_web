import json
import random
from dataclasses import dataclass

import requests as requests

from accounts.utils import KerioModuleAPI
from django.conf import settings


@dataclass
class Status:
    title: str
    address: str
    status: bool = None
    result: str = None


@dataclass
class ResponseS:
    url: str
    status_code: int
    text: str


class TestModuleApi(KerioModuleAPI):

    def __init__(self):
        super().__init__()
        self._result = list()

    def _status_api(self):
        url = self.get_base_path()
        result = self.raw_request(url=url, data={})
        self._result.append(self.create_status('Api status', result))

    def _status_login(self):
        username = settings.KERIO_MODULE_USERNAME
        password = settings.KERIO_MODULE_PASSWORD
        url = f"http://{self.host}:{self.port}/token"
        data = {"username": username, "password": password}
        result = self.raw_request(url=url, data=data, method='post')
        if 'access_token' in result.text:
            self.session.headers.update({"Authorization": 'Bearer ' + json.loads(result.text)['access_token']})
        self._result.append(self.create_status('Try API Login', result))

    def _status_kerio(self):
        result = self.set_trusted_ip('koran')
        self._result.append(self.create_status('Test kerio', result[0]))
        self._result.append(self.create_status('Test kerio', result[1]))

    def get_statuses(self):
        for method_name in self.all_test():
            getattr(self, method_name)()
        return self._result

    def all_test(self):
        return [method for method in self.__dir__() if method.startswith('_status_')]

    def raw_request(self, url, data, method='get') -> requests.Response | ResponseS:
        print(f'test:\n\t{url=}\n\t{data=}\n\t{method=}')
        try:
            if method == 'get':
                response = self.session.get(url)
            else:
                response = self.session.post(url, data)
        except Exception as e:
            return ResponseS(url=url, status_code=429, text=str(e))
        return response

    def create_status(self, test_name, response: requests.Response | ResponseS):
        return Status(
            title=test_name,
            address=response.url,
            status=True if response.status_code == 200 else False,
            result=f"{response.text[:20]}..." if 'access_token' in response.text else response.text
        )

    def set_trusted_ip(self, user=None) -> tuple:
        method = "IpAddressGroups"
        params = {
            "groupIds": [
                76
            ],
            "details": {
                "groupId": "0JTQvtCy0LXRgNC10L3QvdGL0LUgSVAgZm9yIFJEUA==",
                "groupName": "Доверенные IP for RDP",
                "host": '.'.join([str(random.randint(1, 254)) for _ in range(4)]),
                "type": "Host",
                "enabled": False
            }
        }
        result1 = self.send_kerio_request(method + '.set', params)
        result2 = self.save_call([{'method': method + '.apply'}])
        return result1, result2

    def send_kerio_request(self, method, params) -> requests.Response:
        url = self.get_base_path() + "kerio_request"
        data = dict(
            method=method,
            params=params
        )
        return self.session.post(url, json.dumps(data))

