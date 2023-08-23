from django.urls import re_path

from .consumers import TeamConsumer, GameConsumer, TimerConsumer, HintConsumer


websocket_urlpatterns = [
    re_path('api/team-socket/(?P<code>.+)/$', TeamConsumer.as_asgi()),
    re_path('api/game-socket/(?P<game_pk>\d+)/$', GameConsumer.as_asgi()),
    re_path('api/timer/', TimerConsumer.as_asgi()),
    re_path('api/next-hint/', HintConsumer.as_asgi())
]
