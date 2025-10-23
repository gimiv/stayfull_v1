"""
Development settings for Stayfull PMS.
"""

from .base import *

# Override DEBUG to True in development
DEBUG = True

# Additional apps for development
INSTALLED_APPS += [
    # Add development-specific apps here if needed
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
