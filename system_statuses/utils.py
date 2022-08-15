import abc
import json
import redis

from abc import ABC, abstractclassmethod
from dataclasses import dataclass

import requests as requests
from celery.result import AsyncResult
from celery.utils.serialization import jsonify

from accounts.utils import RemoteModuleAPI
from django.conf import settings

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)


@dataclass
class ResponseS:
    url: str
    status_code: int
    text: str


@dataclass
class Status:
    title: str
    address: str
    status: bool = None
    result: str = None

    def __str__(self):
        return f"{self.title} -> Status: {self.status}"

    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BaseCheckKerioModule(ABC):
    next_task: str = None
    title: str = None
    test_path: str = None

    def run_test(self, base_path, session):
        raise NotImplementedError

    @staticmethod
    def raw_request(session, url, data, method='get'):
        try:
            if method == 'get':
                response = session.get(url)
            else:
                response = session.post(url, data)
        except Exception as e:
            return ResponseS(url=url, status_code=429, text=str(e)).__dict__
        return response

    @staticmethod
    def get_result(task_id):
        result = AsyncResult(task_id)
        return jsonify({'task_id': result.task_id, 'task_status': result.status})


class CheckKerioModuleAvailable(BaseCheckKerioModule):
    dependency = None
    title = "kerio_module_available"
    test_path = "ping"

    def run_test(self, base_path, session):
        url = f"{base_path}{self.test_path}"
        result = self.raw_request(session=session, url=url, data={})
        return result


class CheckKerioModuleAuth(BaseCheckKerioModule):
    dependency = CheckKerioModuleAvailable
    title = "kerio_module_auth"
    test_path = "token"

    def run_test(self, base_path, session):
        url = f"{base_path}{self.test_path}"
        username = settings.KERIO_MODULE_USERNAME
        password = settings.KERIO_MODULE_PASSWORD
        data = {"username": username, "password": password}
        result = self.raw_request(session=session, url=url, data=data, method="post")
        return result


class CheckKerioControlStatus(BaseCheckKerioModule):
    dependency = CheckKerioModuleAuth
    title = "kerio_control_status"
    test_path = "status"

    def run_test(self, base_path, session):
        url = f"{base_path}{self.test_path}"
        result = self.raw_request(session=session, url=url, data={})
        return result


class CheckersKeeper:
    tests = []

    def __init__(self, objects: list):
        self._add(objects)

    def _add(self, objects):
        for obj in objects:
            dep = obj.dependency
            if dep is None:
                self.tests.insert(0, obj)
            elif dep in self.tests:
                index = self.tests.index(dep)
                self.tests.insert(index + 1, obj)
            else:
                self.tests.append(obj)

    def __iter__(self):
        for test in self.tests:
            yield test


class TestModuleApi:
    session = None

    def __init__(self):
        self.host = settings.KERIO_MODULE_HOST
        self.port = settings.KERIO_MODULE_PORT
        self.create_session()
        self._result = list()
        self.tests = CheckersKeeper([CheckKerioModuleAvailable,
                                     CheckKerioModuleAuth,
                                     CheckKerioControlStatus])

    def create_session(self):
        if self.session is None:
            self.session = requests.Session()

    def get_base_path(self):
        return f"http://{self.host}:{self.port}/"

    def get_tests(self):
        result: dict = {}
        for test in self.tests:
            result[test.title] = Status(
                title=test.title,
                address=f"{self.get_base_path()}{test.test_path}"
            )
        return result

    def start_tests(self, task_id=None):
        result: dict = {}
        for CheckClass in self.tests:
            obj = CheckClass()
            response = obj.run_test(base_path=self.get_base_path(), session=self.session)
            data = dict(
                title=obj.title,
                status=True if response.status_code == 200 else False,
                result=f"{response.text[:20]}..." if 'access_token' in response.text else response.text
            )
            # redis_instance.set(f"{AsyncResult.task_id}_check_{obj.title}", json.dumps(data))
            redis_instance.set(f"{task_id}_check_{obj.title}", json.dumps(data))

            result[obj.title] = self.create_status(
                test_name=obj.title,
                response=response)
        return result

    def create_status(self, test_name, response: requests.Response | ResponseS):
        return Status(
            title=test_name,
            address=response.url,
            status=True if response.status_code == 200 else False,
            result=f"{response.text[:20]}..." if 'access_token' in response.text else response.text)

    def get_result(self, task_id):
        result = AsyncResult(task_id)
        return jsonify({'task_id': result.task_id, 'task_status': result.status})
