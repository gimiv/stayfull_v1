"""
Production settings for Stayfull PMS.
"""

from .base import *
import os

# Ensure DEBUG is False in production
DEBUG = False

# CSRF trusted origins (required for Railway and other cloud platforms)
CSRF_TRUSTED_ORIGINS = [
    'https://web-production-2765.up.railway.app',
    'https://*.railway.app',
]

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
