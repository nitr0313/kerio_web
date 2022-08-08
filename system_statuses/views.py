import json

import redis
from celery.result import AsyncResult

from django.shortcuts import render

from django.conf import settings
from django.contrib.auth.views import login_required

from system_statuses.utils import TestModuleApi
from .tasks import start_tests

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)


@login_required
def status(request):
    task_id = request.session.get('status_task_id')
    test_module = TestModuleApi()
    model_statuses = test_module.get_tests()
    if not task_id:
        task = start_tests.delay()
        # task = start_tests()
        task_id = task.task_id
        request.session['status_task_id'] = task_id
    else:
        for task_redis_id in redis_instance.keys(f"{task_id}_check*"):
            task_result = redis_instance.get(task_redis_id)
            data = json.loads(task_result)
            model_statuses[data['title']].update(data)
        else:
            del request.session['status_task_id']
    status_task = AsyncResult(task_id)
    # if status_task.status == "SUCCESS":
    #     del request.session['status_task_id']
    #     redis_instance.flushdb()

    return render(request,
                  template_name="system_statuses/status.html",
                  context={'statuses': model_statuses.values(),
                           'status_tasks': status_task.status}
                  )
