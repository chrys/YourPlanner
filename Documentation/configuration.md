# Django Project Configuration Guide

This document outlines the configuration settings for the YourPlanner Django project, covering both development/testing and production environments.

## Settings Files

The project uses two main settings files:

*   `YourPlanner/settings/base.py`: Contains common settings applicable to all environments. It's also used by default for development and testing.
*   `YourPlanner/settings/production.py`: Contains settings specific to the production environment. It imports settings from `base.py` and overrides/extends them.

To use the production settings, the `DJANGO_SETTINGS_MODULE` environment variable must be set to `YourPlanner.settings.production`.

## Environment Variables

For security and flexibility, sensitive data and environment-specific settings should be managed using environment variables.



**Examples:**

*   **`SECRET_KEY`**:
    ```python
    # In settings.py (base.py or production.py)
    import os
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-default-secret-key-for-dev')
    ```
*   **Database Credentials (for `production.py`)**:
    ```python
    # In settings.py (production.py)
    import os
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'options': '-c search_path=public'
            }
        }
    }
    ```

## Security Best Practices

The following security settings are configured or recommended:

*   **`CSRF_COOKIE_SECURE = True`** (Production): Ensures the CSRF cookie is only sent over HTTPS.
*   **`SESSION_COOKIE_SECURE = True`** (Production): Ensures the session cookie is only sent over HTTPS.
*   **`SECURE_SSL_REDIRECT = True`** (Production): Redirects all HTTP requests to HTTPS.
*   **`X_FRAME_OPTIONS = 'DENY'`** (Default via Middleware): Protects against clickjacking attacks by preventing the site from being embedded in iframes. This is enabled by default by `django.middleware.clickjacking.XFrameOptionsMiddleware`.
*   **`SECURE_BROWSER_XSS_FILTER = True`** (Production): Enables the browser's XSS filtering protections.
*   **`SECURE_CONTENT_TYPE_NOSNIFF = True`** (Production): Prevents the browser from interpreting files as a different MIME type than what is declared by the server.

## Logging Configuration

### Testing/Development (`base.py`)

The `base.py` settings include a logging configuration that outputs logs to both the console and a file named `debug.log` located in the project's base directory.

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'), # BASE_DIR is project root
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        # Example for app-specific logging:
        # 'orders': {
        #     'handlers': ['console', 'file'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # },
    },
}
```

### Production (`production.py` Recommendation)

For production environments, it is highly recommended to integrate with `systemd`'s journald logging system for robust log management. Django's console output can be captured by `systemd` when the application is run as a service (e.g., via Gunicorn managed by `systemd`).

Alternatively, to explicitly send logs to syslog (which `systemd` journal can read), you can configure a `SysLogHandler`:

```python
# In production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'syslog': {
            'level': 'INFO', # Adjust level as needed
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'address': '/dev/log', # Or ('localhost', 514) for network syslog
        },
        'console': { # Keep console output for systemd to capture if not using syslog directly
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'syslog'], # Or just ['console'] if systemd captures stdout/stderr
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'syslog'], # Or just ['console']
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'syslog'], # Or just ['console']
            'level': 'ERROR', # Log only errors for requests
            'propagate': False,
        },
        # Add other loggers as needed
    },
}
```
Ensure your application server (like Gunicorn) is configured to output logs to stdout/stderr if you rely on `systemd` to capture them directly.

## Database Configuration

### Testing/Development (`base.py`)

For development and testing, the project is configured to use SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # BASE_DIR is project root
    }
}
```
This creates a `db.sqlite3` file in the project's root directory.

### Production (`production.py`)

For production, the project uses PostgreSQL. The configuration in `production.py` is:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'options': '-c search_path=public'
        }
    }
}
```
**Note:** As mentioned under "Environment Variables," these credentials should be sourced from environment variables in a live production environment.

## Static and Media Files

Configuration for static (CSS, JS, images) and media (user-uploaded files) files:

*   **`STATIC_URL = 'static/'`** (in `base.py`):
    URL prefix for static files during development.
    In `production.py`, this is overridden to `'/yourplanner/static/'`.

*   **`STATIC_ROOT = BASE_DIR.parent / 'static'`** (in `production.py`):
    The absolute filesystem path to the directory where `collectstatic` will gather all static files for deployment. This directory is typically served by a web server like Nginx in production. `BASE_DIR.parent` points to the directory containing the `YourPlanner` project directory.

*   **`MEDIA_URL = '/yourplanner/media/'`** (in `production.py`):
    URL prefix for user-uploaded media files.

*   **`MEDIA_ROOT = BASE_DIR / 'media'`** (in `production.py`):
    The absolute filesystem path to the directory that will hold user-uploaded files. `BASE_DIR` is the project root (YourPlanner).

During development, Django's development server automatically serves static files. In production, `python manage.py collectstatic` must be run to gather static files into `STATIC_ROOT`.

## `ALLOWED_HOSTS`

This setting lists the host/domain names that this Django site can serve.

*   **Testing/Development (`base.py`):**
    `ALLOWED_HOSTS = []`
    When `DEBUG = True` (the default in `base.py`), and `ALLOWED_HOSTS` is empty, Django allows requests to `['localhost', '127.0.0.1', '[::1]']`. This is suitable for local development.

*   **Production (`production.py`):**
    `ALLOWED_HOSTS = ['www.fasolaki.com']`
    In production (`DEBUG = False`), this **must** be set to the correct domain(s) the site will be accessed from.

## Rate Limiting (Recommendation)

To protect against brute-force attacks on login forms and other sensitive API endpoints, implementing rate limiting is crucial. A common package for this is `django-ratelimit`.

**Installation (conceptual):**
```bash
pip install django-ratelimit
```

**Configuration (conceptual example in `settings.py`):**
```python
# In settings.py (e.g., base.py or production.py)
INSTALLED_APPS += [
    'ratelimit',
]

# Optional: Define default rate limit settings
RATELIMIT_GLOBAL = '100/h' # Default for all views if not specified otherwise
RATELIMIT_LOGIN_ATTEMPTS = '5/m' # Example: 5 login attempts per minute

MIDDLEWARE += [
    'ratelimit.middleware.RatelimitMiddleware',
]
```

**Usage (conceptual example in `views.py` or `urls.py`):**

You can apply rate limits using decorators in your views or directly in your URL configurations.

*   **In `views.py`:**
    ```python
    from ratelimit.decorators import ratelimit

    @ratelimit(key='ip', rate='5/m', block=True) # Per IP, 5 per minute
    def login_view(request):
        # ... your login logic
        pass

    @ratelimit(key='user_or_ip', rate='10/h', block=True) # Per authenticated user or IP, 10 per hour
    def sensitive_api_view(request):
        # ... your API logic
        pass
    ```

*   **In `urls.py` (less common for view-specific rates but possible for groups):**
    Consult `django-ratelimit` documentation for advanced URL-based configuration.

It's important to identify all sensitive endpoints (authentication, password reset, form submissions prone to abuse) and apply appropriate rate limits.
