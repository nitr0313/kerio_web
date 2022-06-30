from .base import *

DEBUG = True
DJANGO_APPS = []
DEV_APPS = []
INSTALLED_APPS += PROJECT_APPS
AUTH_PASSWORD_VALIDATORS = []
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3'
    }
}
