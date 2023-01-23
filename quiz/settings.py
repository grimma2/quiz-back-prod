from pathlib import Path
import logging
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECONDS_FOR_SINGLE_POINT = 1

SYMBOLS_IN_TEAM_CODE = 5

logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='w',
                    format='%(asctime)s - logger:%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DL')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler(filename='log.log'))


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ['rediss://red-cf4lr59gp3js6fk10ok0:s6t1AcvLM7q9KL1w46MiVnyLIiN2rLI6@singapore-redis.render.com:6379'],
        },
    },
}

SECRET_KEY = 'fz@z7-a=yvq!rvy+0#f(laxf@@z6-jgjh2wk$!+ydea2jk@)xz'

DEBUG = False

ALLOWED_HOSTS = [
    'earnest-cassata-8f1bf8.netlify.app',
    'quiz-game1.ru',
    '127.0.0.1',
    '62.113.104.181'
]

SESSION_COOKIE_SAMESITE = None
CRSF_COOKIE_SAMESITE = None

# django-cors-headers
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'https://earnest-cassata-8f1bf8.netlify.app',
    'https://quiz-game1.ru',
    'http://127.0.0.1:8000',
    'https://62.113.104.181'
]

# end django-cors-headers


INSTALLED_APPS = [
    'channels',
    'rest_framework',
    'corsheaders',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'game.apps.GameConfig',
    'team.apps.TeamConfig',
    'quichannels.apps.QuichannelsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quiz.urls'

TEMPLATES_ROOT = '/templates/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / TEMPLATES_ROOT],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'quiz.wsgi.application'
ASGI_APPLICATION = 'quiz.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'quiz',
        'USER': 'quizuser',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/collectedstatic/'
STATIC_ROOT = BASE_DIR / STATIC_URL
STATICFILES_DIRS = [BASE_DIR / '/static/']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CELERY_BROKER_URL = 'rediss://red-cf4lr59gp3js6fk10ok0:s6t1AcvLM7q9KL1w46MiVnyLIiN2rLI6@singapore-redis.render.com:6379'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
