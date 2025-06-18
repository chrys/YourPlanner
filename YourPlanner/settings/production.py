import os
from .base import *
import dj_database_url

# General Production Settings
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['www.fasolaki.com']

# Subpath Configuration
# This tells Django that the entire application is served under /yourplanner/
#FORCE_SCRIPT_NAME = '/yourplanner'
USE_X_FORWARDED_HOST = True

# Security Settings for HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static & Media Files
# URLs must include the subpath prefix.
STATIC_URL = '/yourplanner/static/'
MEDIA_URL = '/yourplanner/media/'

# STATIC_ROOT is where `collectstatic` will place all static files.
# Your web server (Nginx) should be configured to serve files from this directory.
STATIC_ROOT = BASE_DIR.parent / 'staticfiles_production'

# MEDIA_ROOT is for user-uploaded files.
MEDIA_ROOT = BASE_DIR.parent / 'media_production'



# Cookie Paths
# Scope cookies to the application's subpath.
CSRF_COOKIE_PATH = '/'
SESSION_COOKIE_PATH = '/'

# Database Configuration
# Uses DATABASE_URL environment variable for security.
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'), conn_max_age=600)
}

# Caching (using Redis is recommended for production)
if os.getenv('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Logging (adjust as needed)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}