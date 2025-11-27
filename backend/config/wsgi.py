"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from config.logger import setup_logging
from config.settings.schemas import config_registry as config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", config.django_settings_module)

setup_logging()

application = get_wsgi_application()
