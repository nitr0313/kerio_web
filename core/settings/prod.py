import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

DEBUG = False

DJANGO_APPS = []
DEV_APPS = []
INSTALLED_APPS += PROJECT_APPS

sentry_sdk.init(
    dsn=env.str("SENTRY_URL", "http://localhost:3333/"),
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True
)
