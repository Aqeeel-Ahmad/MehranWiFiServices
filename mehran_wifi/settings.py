"""
Django settings for mehran_wifi project.
Mehran WiFi Service - Modern Fiber ISP Platform
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', os.environ.get('SECRET_KEY', 'django-insecure-(o5m+%2l722!tt^p^sn!m@_-3cw%h(0=n!buw1%zkk)0h+5u=q'))

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*', '.vercel.app', '.now.sh', 'localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
    'http://127.0.0.1',
    'http://localhost',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Django Allauth
    'allauth',
    'allauth.account',

    # Local Apps
    'apps.core.apps.CoreConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.packages.apps.PackagesConfig',
    'apps.payments.apps.PaymentsConfig',
    'apps.complaints.apps.ComplaintsConfig',
    'apps.notifications.apps.NotificationsConfig',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mehran_wifi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'mehran_wifi.wsgi.application'

# Database Configuration (Supports persistent PostgreSQL via DATABASE_URL / POSTGRES_URL, or SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
        }
    except Exception:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
elif 'VERCEL' in os.environ:
    tmp_db = Path('/tmp/db.sqlite3')
    orig_db = BASE_DIR / 'db.sqlite3'
    if not tmp_db.exists() and orig_db.exists():
        try:
            shutil.copy2(orig_db, tmp_db)
        except Exception:
            pass
    DB_PATH = tmp_db if tmp_db.exists() else orig_db
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DB_PATH,
        }
    }
else:
    DB_PATH = BASE_DIR / 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DB_PATH,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Enable WhiteNoise finders so all static assets are served reliably in serverless environments
WHITENOISE_USE_FINDERS = True

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
if 'VERCEL' in os.environ:
    MEDIA_ROOT = Path('/tmp/media')
    try:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
else:
    MEDIA_ROOT = BASE_DIR / 'media'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Django Allauth Configuration
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_ON_SIGNUP = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_REDIRECT_URL = 'dashboard'
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'
ACCOUNT_FORMS = {
    'signup': 'apps.accounts.forms.CustomAllauthSignupForm',
    'login': 'apps.accounts.forms.CustomAllauthLoginForm',
}

# Session & Cookie Persistence Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 14 days
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Email Settings (Console backend for testing, outputs cleanly in console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'support@mehranwifi.com'
SERVER_EMAIL = 'admin@mehranwifi.com'

# Mehran WiFi Service Constants
EASYPAISA_NUMBER = '03454524086'
EASYPAISA_ACCOUNT_NAME = 'Mehran WiFi Service'
ISP_NAME = 'MEHRAN WIFI SERVICE'
ISP_TAGLINE = 'Fast, Reliable & Unlimited Fiber Internet'
ISP_PHONE = '03454524086'
ISP_EMAIL = 'support@mehranwifi.com'
ISP_ADDRESS = 'Main Optical Fiber Hub, Mehran City, Pakistan'
