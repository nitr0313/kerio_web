from django.shortcuts import render

# Create your views here.
from accounts.utils import KerioModuleAPI
from dataclasses import dataclass
from django.conf import settings
from django.contrib.auth.views import login_required

from system_statuses.utils import TestModuleApi


@login_required
def status(request):
    test_module = TestModuleApi()
    model_statuses = test_module.get_statuses()
    # TODO сделать быстрый возврат таблицы с тестами, а результаты подтягивать по ходу выполнения в фоне Tasks
    return render(request,
                  template_name="system_statuses/status.html",
                  context={'statuses': model_statuses}
                  )
