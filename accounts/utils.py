import json
import os
import logging

import requests
from django.conf import settings
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from accounts.models import KerioGroup, IPAddress

logger = logging.getLogger('main_logger')
User = get_user_model()

#
# class KerioModuleAPI:
#
#     def __init__(self):
#         self.cookie = None
#         self.session = None
#         self.host = settings.KERIO_MODULE_HOST
#         self.port = settings.KERIO_MODULE_PORT
#         self.token = os.environ.get("KERIO_MODULE_TOKEN")
#         self.create_session()
#         self.get_token()
#
#     def send_kerio_request(self, method, params) -> dict:
#         url = self.get_base_path() + "kerio_request"
#         data = dict(
#             method=method,
#             params=params
#         )
#         response = self.session.post(url, json.dumps(data))
#         if response.status_code == 401:
#             # "Не авторизован!"
#             self.token = None
#             self.get_token()
#             response = self.session.post(url, json.dumps(data))
#         return self.handle_request(response)
#
#     def request(self, url, data) -> dict:
#         response = self.session.post(url, data)
#         if response.status_code == 200:
#             return self.handle_request(response)
#         logger.error("{}".format(json.dumps(response.text)))
#         return {}
#
#     @staticmethod
#     def add_error(message, method=''):
#         m = 'No specific method: '
#         if method != '':
#             m = "While running {}".format(method)
#         print("{} {}".format(m, message))
#
#     def handle_request(self, r):
#         result = json.loads(r.text)
#         # TODO add logging and bad result with information about errors
#         if 'error' in result:
#             self.add_error(result['error'])
#             return []
#         if 'errors' in result and result['errors']:
#             self.add_error(result['errors'][0]['message'])
#             return []
#         if 'detail' in result:
#             self.add_error(result['detail'])
#             return []
#         return result
#
#     def get_token(self):
#         if self.token is not None:
#             return
#         username = settings.KERIO_MODULE_USERNAME
#         password = settings.KERIO_MODULE_PASSWORD
#
#         answer = self.request(
#             url=f"http://{self.host}:{self.port}/token",
#             data={"username": username, "password": password}
#         )
#         if answer:
#             self.token = answer['access_token']
#             self.session.headers.update({"Authorization": 'Bearer ' + self.token})
#             os.environ.setdefault("KERIO_MODULE_TOKEN", self.token)
#
#     def create_session(self):
#         if self.session is None:
#             self.session = requests.Session()
#
#     def get_trusted_ips(self, type_='Host', start=0, limit=500) -> list:
#         method = "IpAddressGroups.get"
#         params = {"query": {"start": start, "limit": limit,
#                             "orderBy": [{"columnName": "description", "direction": "Asc"}]}}
#         answer = self.send_kerio_request(method, params)
#
#         if not answer:
#             return []
#         ips = answer["list"]
#         result = [user for user in ips if user['type'] == type_]
#         return result
#
#     def set_disable_all_trusted_api(self):
#         all_ids = [
#             (user['description'], self.set_enable_or_disable_trusted_ids(user['id'], False))
#             for user in self.get_trusted_ips()]
#         return all_ids
#
#     def set_trusted_ip(self, user: IPAddress):
#         method = "IpAddressGroups"
#
#         params = {
#             "groupIds": [
#                 user.router_id
#             ],
#             "details": {
#                 "groupId": user.router_group.kerio_id,
#                 "groupName": user.router_group.kerio_name,
#                 "host": user.ipaddress,
#                 "type": "Host",
#                 "enabled": user.is_active
#             }
#         }
#         answer = self.send_kerio_request(method + '.set', params)
#         if answer is not None:
#             # self.save_call([{'method': method + '.apply'}])
#             return True
#         return False
#
#     def add_trusted_ip(self, ip, name):
#         group = KerioGroup.objects.first()
#         method = "IpAddressGroups"
#         params = {
#             "groups": [
#                 {
#                     "groupId": group.kerio_id,
#                     "groupName": group.kerio_name,
#                     "host": ip,
#                     "type": "Host",
#                     "description": name,
#                     "enabled": True
#                 }
#             ]
#         }
#         result = self.send_kerio_request(method + '.create', params)
#         if result is not None:
#             self.send_kerio_request([{'method': method + '.apply'}])
#             new_user = [user for user in self.get_trusted_ips() if user['description'] == name]
#             # TODO Нужно возвращать ифну о новом id
#             return new_user[0] if new_user else False
#         return False
#
#     def set_enable_or_disable_trusted_ids(self, ids, enabled=True):
#         method = "IpAddressGroups"
#         params = {"details": {"enabled": enabled}, "groupIds": ids}
#         result = self.send_kerio_request(method + '.set', params)
#         if result is not None:
#             self.save_call([{'method': method + '.apply'}])
#             return True
#         return False
#
#     def save_call(self, methods: list):
#         method = "Batch.run"
#         params = {"commandList": methods}
#         answer = self.send_kerio_request(method, params)
#         return answer
#
#     def get_id_by_ipaddress(self, ip):
#         all_ips = self.get_trusted_ips()
#         for user in all_ips:
#             if ip == user['ip']:
#                 return user['id']
#
#     def logout(self):
#         print("logout")
#         self.send_kerio_request("Session.logout", {})
#
#     def get_base_path(self):
#         return f"http://{self.host}:{self.port}/"


from abc import ABC, abstractmethod


class RemoteModuleCommand(ABC):
    endpoint: str = None
    result: dict = None
    _required_fields = []

    def __init__(self, data=None):
        self.data = data
        if data is not None:
            self.__test_data()
        self._create_params()

    def _create_params(self):
        ...

    def __test_data(self):
        for field in self._required_fields:
            try:
                _ = getattr(self.data, field)
            except AttributeError:
                print(f"Не все данные получены!\n Необходимые поля: {', '.join(self._required_fields)}")


class ChangeUserIp(RemoteModuleCommand):
    endpoint = "change_user_ip"
    _required_fields = ['router_id', 'router_group', 'ipaddress', 'is_active']

    def _create_params(self):
        self.result = dict(
            user_router_id=self.data.router_id,
            details=dict(
                group_id=self.data.router_group.kerio_id,
                group_name=self.data.router_group.kerio_name,
                host=self.data.ipaddress,
                enabled=self.data.is_active
            )
        )


class GetAllTrustedIP(RemoteModuleCommand):
    endpoint = "get_all_users_ips"
    _required_fields = []

    def __init__(self, data=None, start=0, limit=500):
        self.start = start
        self.limit = limit
        super().__init__(data=data)

    def _create_params(self):
        self.result = dict(start=self.start, limit=self.limit)


class GetAPIToken(RemoteModuleCommand):
    endpoint = "token"
    _required_fields = ["username", "password"]

    def _create_params(self):
        self.result = dict(
            username=self.data["username"],
            password=self.data["password"])


class RemoteModuleAPI:
    api_endpoints = {
        'get_all_users_ips',
        'change_user_ip',
        'del_user',
        'create_user'
    }

    def __init__(self):
        self.cookie = None
        self.session = None
        self.host = settings.KERIO_MODULE_HOST
        self.port = settings.KERIO_MODULE_PORT
        self.token = None
        self.create_session()
        self.get_token()

    def send_kerio_request(self, method, params) -> dict:
        url = self.get_base_path() + "kerio_request"
        data = dict(
            method=method,
            params=params
        )
        response = self.session.post(url, json.dumps(data))
        if response.status_code == 401:
            # "Не авторизован!"
            self.token = None
            self.get_token()
            response = self.session.post(url, json.dumps(data))
        return self.handle_request(response)

    @staticmethod
    def add_error(message, method=''):
        m = 'No specific method: '
        if method != '':
            m = "While running {}".format(method)
        print("{} {}".format(m, message))

    def handle_request(self, r):
        result = json.loads(r.text)
        # TODO add logging and bad result with information about errors
        if 'error' in result:
            self.add_error(result['error'])
            return []
        if 'errors' in result and result['errors']:
            self.add_error(result['errors'][0]['message'])
            return []
        if 'detail' in result:
            self.add_error(result['detail'])
            return []
        return result

    def create_session(self):
        if self.session is None:
            self.session = requests.Session()

    def remote_module_request(self, endpoint, data) -> dict:
        url = self.get_base_path() + endpoint
        response = self.session.post(url, json.dumps(data))
        if response.status_code == 401:
            self.token = None
            self.get_token()
            response = self.session.post(url, data)
        return self.handle_request(response)

    def request(self, endpoint, data) -> dict:
        url = self.get_base_path() + endpoint
        response = self.session.post(url, data)
        if response.status_code == 401:
            self.token = None
            self.get_token()
            response = self.session.post(url, data)
        return self.handle_request(response)

    def get_token(self):
        if self.token is not None:
            return
        username = settings.KERIO_MODULE_USERNAME
        password = settings.KERIO_MODULE_PASSWORD
        command_class = GetAPIToken(data={"username": username, "password": password})
        answer = self.request(endpoint=command_class.endpoint,
                                            data=command_class.result)
        if answer:
            self.token = answer['access_token']
            self.session.headers.update({"Authorization": 'Bearer ' + self.token})

    def get_all_users_ips(self):
        command_class = GetAllTrustedIP()
        answer = self.remote_module_request(endpoint=command_class.endpoint,
                                            data=command_class.result)
        if answer is not None:
            return answer
        return False

    def change_user_ip(self, user: IPAddress):
        command_class = ChangeUserIp(data=user)
        answer = self.remote_module_request(endpoint=command_class.endpoint,
                                            data=command_class.result)
        if answer is not None:
            return True
        return False

    def add_trusted_ip(self, ip, name):
        group = KerioGroup.objects.first()
        method = "IpAddressGroups"
        params = {
            "groups": [
                {
                    "groupId": group.kerio_id,
                    "groupName": group.kerio_name,
                    "host": ip,
                    "type": "Host",
                    "description": name,
                    "enabled": True
                }
            ]
        }
        result = self.send_kerio_request(method + '.create', params)
        if result is not None:
            self.send_kerio_request([{'method': method + '.apply'}])
            new_user = [user for user in self.get_trusted_ips() if user['description'] == name]
            # TODO Нужно возвращать ифну о новом id
            return new_user[0] if new_user else False
        return False

    def get_id_by_ipaddress(self, ip):
        all_ips = self.get_trusted_ips()
        for user in all_ips:
            if ip == user['ip']:
                return user['id']

    def get_base_path(self):
        return f"http://{self.host}:{self.port}/"


def send_email_about_new_ip(user_id, new_ip):
    print(f"send_mail to {user_id=} about {new_ip=}")
    user = User.objects.get(id=user_id)
    if not user.email:
        return
    email = user.email
    name = user.first_name or user.username
    try:
        cc = send_mail(
            subject='Уведомление от сайта об изменении IP!',
            message=f'Добрый день, {name}!\nВаш ip [{new_ip}] был добавлен в список доверенных',
            from_email='sovmk@ya.ru',
            recipient_list=[email],
        )
    except Exception as e:
        return str(e)
    return cc


if __name__ == "__main__":
    @dataclass
    class Settings:
        KERIO_MODULE_USERNAME: str
        KERIO_MODULE_PASSWORD: str
        KERIO_MODULE_HOST: str
        KERIO_MODULE_PORT: str


    settings = Settings(KERIO_MODULE_USERNAME='Admin', KERIO_MODULE_PASSWORD='0147', KERIO_MODULE_HOST='127.0.0.1',
                        KERIO_MODULE_PORT='8000')
    kerio = RemoteModuleAPI()
    print(kerio.get_all_users_ips())
