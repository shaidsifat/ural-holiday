from pathlib import Path
from .utils import get_secret

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = True
# ALLOWED_HOSTS = ["uralholidays.co.uk", "www.uralholidays.co.uk", "uralholidays.com", "www.uralholidays.com"]
ALLOWED_HOSTS = ['*']
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
        'PORT': '3306',
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
EMAIL_HOST_USER = 'apikey'  # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = get_secret('SENDGRID_API_KEY')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
DEFAULT_FROM_EMAIL = 'Uralholidays Team <admin@uralholidays.com>'
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATIC_ROOT = BASE_DIR / "static/assets"
# MEDIA_ROOT = BASE_DIR / "static/media"

# STATIC_URL = 'https://static.uralholidays.com/assets/'
# MEDIA_URL = 'https://static.uralholidays.com/media/'
