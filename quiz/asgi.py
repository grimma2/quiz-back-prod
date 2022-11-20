import os

import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# place setup before fetch app code what ain't done for this
django.setup()

import quichannels.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            quichannels.routing.websocket_urlpatterns
        )
    )
})
