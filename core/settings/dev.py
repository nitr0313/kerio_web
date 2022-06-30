from .base import *

DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]

ALLOWED_HOSTS = ['127.0.0.1']

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
