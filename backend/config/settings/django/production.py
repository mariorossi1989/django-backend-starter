"""Production environment Django settings.

Extends base settings with production-specific configurations including
enhanced security settings, logging, and static file handling.
"""

from config.settings.django.base import *  # noqa: F403

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files configuration for production
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
