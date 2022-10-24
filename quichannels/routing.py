from django.urls import re_path

from .consumers import TeamConsumer, GameConsumer


websocket_urlpatterns = [
    re_path('team-socket/(?P<code>.+)/$', TeamConsumer.as_asgi()),
    re_path('game-socket/(?P<game_pk>\d+)/(?P<secret_key>.+)/$', GameConsumer.as_asgi()),
]
