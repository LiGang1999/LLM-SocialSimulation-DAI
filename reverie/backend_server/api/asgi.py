"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django_wsgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {"http": django_wsgi_app, "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns))}
)
