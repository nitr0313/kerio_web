from pathlib import Path

import environ

VERSION = '0.2 beta'

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx'
]

PROJECT_APPS = [
    'accounts.apps.AccountsConfig',
    'system_statuses.apps.SystemStatusesConfig',
    'action_logger.apps.ActionLoggerConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.current_version'
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
SECRET_KEY = env.str('SECRET_KEY')

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

DATABASES = {'default': env.db('DATABASE_URL')}
PUBLIC_ROOT = Path(env.str('PUBLIC_ROOT', BASE_DIR / 'public'))
MEDIA_ROOT = PUBLIC_ROOT / 'media'
MEDIA_URL = env.str('MEDIA_URL', default='/media/')

STATIC_ROOT = PUBLIC_ROOT / 'static'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_URL = env.str('STATIC_URL', default='static/')

REDIS_HOST = env.str('REDIS_HOST', default='localhost')
REDIS_PORT = env.int('REDIS_PORT', default=6379)
REDIS_DB = env.int('REDIS_DB', default=0)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


KERIO_MODULE_USERNAME = env.str('KERIO_MODULE_USERNAME')
KERIO_MODULE_PASSWORD = env.str('KERIO_MODULE_PASSWORD')
KERIO_MODULE_HOST = env.str('KERIO_MODULE_HOST')
KERIO_MODULE_PORT = env.str('KERIO_MODULE_PORT')
KERIO_MODULE_COUNT_TRY = env.str('KERIO_MODULE_COUNT_TRY', 3)

EMAIL_CONFIG = env.email(
    'EMAIL_URL',
    default='consolemail://'
)

vars().update(EMAIL_CONFIG)
FROM_EMAIL = env.str("FROM_EMAIL", "example@example.com")
EMAIL_HOST = env.str("EMAIL_HOST", 'smtp.example.com')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'main_logger': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
