"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from config.settings.schemas import config_registry as config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", config.django_settings_module)

application = get_asgi_application()
