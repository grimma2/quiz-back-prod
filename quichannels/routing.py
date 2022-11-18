from django.urls import re_path

from .consumers import TeamConsumer, GameConsumer, TimerConsumer, GameChangeState


websocket_urlpatterns = [
    re_path('team-socket/(?P<code>.+)/$', TeamConsumer.as_asgi()),
    re_path('game-socket/(?P<game_pk>\d+)/(?P<secret_key>.+)/$', GameConsumer.as_asgi()),
    re_path('timer/(?P<secret_key>.+)/$', TimerConsumer.as_asgi()),
    re_path('game-change-state/(?P<secret_key>.+)/$', GameChangeState.as_asgi())
]
