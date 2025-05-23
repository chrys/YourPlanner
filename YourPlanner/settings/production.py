from .base import *

DEBUG = False
ALLOWED_HOSTS = ['www.fasolaki.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yourplanner',
        'USER': 'planner',
        'PASSWORD': 'PlannerPlanner2025!',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}
