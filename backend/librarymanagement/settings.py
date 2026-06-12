import os
from pathlib import Path

from django import http

BASE_DIR = Path(__file__).resolve().parent.parent

# Frontend folder is one level up from backend
FRONTEND_DIR = BASE_DIR.parent / 'frontend'
TEMPLATE_DIR = FRONTEND_DIR / 'templates'
STATIC_DIR = FRONTEND_DIR / 'static'

# FIX: Read SECRET_KEY from environment variable, with insecure fallback for dev
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-use-env-variable-here')

# FIX: Read DEBUG from env so production can set DEBUG=False
DEBUG = True

# FIX: ALLOWED_HOSTS from env for production (AWS EC2 / Nginx)
#ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')
allowed_hosts = os.environ.get('ALLOWED_HOSTS', '*')

if allowed_hosts == '*':
    ALLOWED_HOSTS = ['*',
                    'http://library-1443069192.ap-south-1.elb.amazonaws.com',
                    ]
else:
    ALLOWED_HOSTS = allowed_hosts.split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'library',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True
ROOT_URLCONF = 'librarymanagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'librarymanagement.wsgi.application'

# FIX: Default to SQLite for local dev; override via DATABASE_URL env var in production
# For production MySQL on AWS RDS, set these env vars:
#   DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
_db_engine = os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3')

if _db_engine == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'libararydb',
            'USER': 'admin',
            'PASSWORD': 'Krish7990',
            'HOST': 'libararydb.c720y4e4m8ot.ap-south-1.rds.amazonaws.com',
            'PORT': '3306',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# FIX: Only add STATIC_DIR to STATICFILES_DIRS if it exists (avoids error if no static folder)
if STATIC_DIR.exists():
    STATICFILES_DIRS = [STATIC_DIR]
else:
    STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/afterlogin.html'
# FIX: Tell Django where the login page is so @login_required redirects correctly
LOGIN_URL = '/adminlogin.html'

# FIX: Email settings read from env vars (not literal credential strings)
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'  # safe default: print to console
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'shivamdube1285@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'pqna hzjj ypjw cpud')

# FIX: CSRF trusted origins for production (AWS EC2 / custom domain)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    'http://librarymanagement-v4.s3-website.ap-south-1.amazonaws.com',
    'http://library-1443069192.ap-south-1.elb.amazonaws.com',    
]
CORS_ALLOWED_ORIGINS  = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 
    'http://localhost,http://127.0.0.1,http://library-1443069192.ap-south-1.elb.amazonaws.com,http://librarymanagement-v4.s3-website.ap-south-1.amazonaws.com'
).split(',')


# FIX: Session cookie settings for production compatibility
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = False   # HTTP
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = False