from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

DJANGO_APPS = []
DEV_APPS = []
INSTALLED_APPS += \
    [
        'debug_toolbar'
    ] + PROJECT_APPS

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

TEMPLATES[0].update({"BACKEND": "django.template.backends.django.DjangoTemplates"})

AUTH_PASSWORD_VALIDATORS = []

sentry_sdk.init(
    dsn=env.str("SENTRY_URL", "http://localhost:3333/"),
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True
)
