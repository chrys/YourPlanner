"""
Production settings for YourPlanner project.
"""
import os
from dotenv import load_dotenv
from .base import *

# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Use environment variable for secret key
SECRET_KEY = os.getenv('SECRET_KEY', SECRET_KEY)

# Allow specific hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'www.fasolaki.com').split(',')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

FORCE_SCRIPT_NAME = '/yourplanner'
USE_X_FORWARDED_HOST = True
CSRF_COOKIE_PATH = '/yourplanner'
SESSION_COOKIE_PATH = '/yourplanner'

# Static/Media files
STATIC_URL = '/yourplanner/static/'
STATIC_ROOT = BASE_DIR.parent / 'static'
MEDIA_URL = '/yourplanner/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Database
if os.getenv('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'yourplanner'),
            'USER': os.getenv('DB_USER', 'planner'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'PlannerPlanner2025!'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'options': '-c search_path=public'
            }
        }
    }

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Cache settings
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

# Logging
LOGGING['handlers']['file']['filename'] = os.path.join(BASE_DIR, 'logs', 'yourplanner.log')
LOGGING['handlers']['file']['level'] = 'ERROR'
LOGGING['loggers']['django']['level'] = 'ERROR'

