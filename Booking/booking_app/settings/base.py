from .utils import get_secret
from pathlib import Path
from django.urls import reverse_lazy
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

SECRET_KEY = get_secret('SECRET_KEY')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'corsheaders',
    'allauth.account',
    'allauth.socialaccount',
    'geoip2',
    'air',
    'django_simple_coupons'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'booking_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'booking_app/templates/' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'booking_app.context_processors.site_global_temp_var',
            ],
        },
    },
]

WSGI_APPLICATION = 'booking_app.wsgi.application'


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


# STATIC_URL = '/static/'
# # STATIC_ROOT = BASE_DIR / 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = int(get_secret('SITE_ID'))

LOGIN_REDIRECT_URL = '/'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

# STATICFILES_DIRS = [
#     BASE_DIR / "static/client",
# ]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/uralholidays_cache'
    }
}

TIME_INPUT_FORMATS = [
    '%H:%M:%S',     # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M',        # '14:30'
    '%H:%M %P'
]

STATICFILES_DIRS = [
    BASE_DIR / "static"
]


"""************************************** AMADEUS SETTINGS **************************************"""
AMADEUS_API_KEY = get_secret('AMADEUS_API_KEY')
AMADEUS_API_SECRET = get_secret('AMADEUS_API_SECRET')
AMADEUS_HOSTNAME = get_secret('AMADEUS_HOSTNAME')
"""************************************** END AMADEUS SETTINGS **************************************"""


"""************************************** GEOIP SETTINGS **************************************"""
GEOIP_PATH = os.path.join(BASE_DIR, 'geoip')
GEOIP_COUNTRY = "GeoIP2-Country.mmdb"
"""************************************** END GEOIP SETTINGS **************************************"""

"""************************************** STRIPE SETTINGS **************************************"""
STRIPE_PUBLISHABLE_KEY = get_secret('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = get_secret('STRIPE_SECRET_KEY')
"""************************************** END STRIPE SETTINGS **************************************"""

"""************************************** SENDGRID SETTINGS **************************************"""
SENDGRID_API_KEY = get_secret('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_ECHO_TO_STDOUT = True
"""************************************** END SENDGRID SETTINGS **************************************"""



AUTH_USER_MODEL = 'air.User'
ACCOUNT_ADAPTER = 'booking_app.adapter.MyAccountAdapter'
# ACCOUNT_SIGNUP_REDIRECT_URL = "/phone-verification/"
ACCOUNT_SIGNUP_REDIRECT_URL = reverse_lazy("account_login")
ACCOUNT_LOGOUT_ON_GET = True
