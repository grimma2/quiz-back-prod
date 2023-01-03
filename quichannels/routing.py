from django.urls import re_path

from .consumers import TeamConsumer, GameConsumer, TimerConsumer


websocket_urlpatterns = [
    re_path('team-socket/(?P<code>.+)/$', TeamConsumer.as_asgi()),
    re_path('game-socket/(?P<game_pk>\d+)/$', GameConsumer.as_asgi()),
    re_path('timer/', TimerConsumer.as_asgi()),
]
