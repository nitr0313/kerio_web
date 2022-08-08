from dataclasses import dataclass
from celery import shared_task
from celery.result import AsyncResult
import secrets
from system_statuses.utils import TestModuleApi

from celery.utils.log import get_task_logger

logger = get_task_logger('celery.worker')


@dataclass
class Task:
    task_id: int


@shared_task
def start_tests():
    # task = Task(task_id=secrets.token_hex(16))
    test_module = TestModuleApi()
    task_id = start_tests.request.id  # TODO ЗДЕСЬ ПОЧЕМУТО НЕ ID а <property object at 0x000001C9B2E8B470>!!!!
    logger.info(f"{task_id=} {start_tests.request=}")
    task_results = test_module.start_tests(task_id)
    logger.info(f"{task_results=}")
