"""
Development settings for Stayfull PMS.
"""

from .base import *

# Override DEBUG to True in development
DEBUG = True

# Additional apps for development
INSTALLED_APPS = ['corsheaders'] + INSTALLED_APPS + ['debug_toolbar']

# Middleware for CORS and Debug Toolbar
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
] + MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# CORS settings (development only - allow frontend access)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js dev server
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

# Django Debug Toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# Database connection debugging (optional)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # Change to DEBUG to see SQL queries
        },
    },
}
