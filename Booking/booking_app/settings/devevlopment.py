from pathlib import Path
from .utils import get_secret

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
'''

DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.mysql',
         'NAME': get_secret('DB_NAME'),
        'USER': get_secret('DB_USER'),
        'PASSWORD': get_secret('DB_PASSWORD'),
         'HOST': get_secret('DB_HOST'),
         'PORT': get_secret('DB_PORT'),
    },
 }
'''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


LANGUAGE_CODE = 'en-us'

EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey' # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = get_secret('SENDGRID_API_KEY')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
DEFAULT_FROM_EMAIL = 'Uralholidays Team <admin@uralholidays.com>'

STATIC_ROOT = BASE_DIR / "static/assets"
MEDIA_ROOT = BASE_DIR / "static/media"

STATIC_URL = '/static/'
MEDIA_URL = 'https://static.rhizo.us/media/'
