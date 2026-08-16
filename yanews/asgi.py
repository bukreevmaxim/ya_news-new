"""ASGI configuration for YaNews."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yanews.settings')

application = get_asgi_application()
