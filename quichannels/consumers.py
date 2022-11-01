from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from quiz.settings import SECRET_KEY

from .utils import (
    code_is_valid, change_game_state, NextQuestionSender, GroupMessageSender, UpdateLeaderBoardEvent
)

from team.models import Team

from game.models import Game

import json


class TeamConsumer(NextQuestionSender, UpdateLeaderBoardEvent, WebsocketConsumer):

    def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.team = (
            Team.objects.filter(code=self.code).select_related('game').prefetch_related('game__question_set').first()
        )
        self.team_name = f'{self.code}_team'
        code_is_valid(self.team)

        async_to_sync(self.channel_layer.group_add)(
            self.team_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.team_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['type'] == 'next_question':
            self.send_to_next_question(self.team)

    def next_question(self, event):
        self.send(text_data=json.dumps({
            'event': 'next_question',
            'event_data': event['event_data'],
        }))

    def change_state(self, event):
        self.send(text_data=json.dumps({
            'event': 'change_state',
            'event_data': event['game_state'],
        }))


class GameConsumer(GroupMessageSender, UpdateLeaderBoardEvent, WebsocketConsumer):

    def connect(self):
        self.secret_key = self.scope['url_route']['kwargs']['secret_key']
        game_pk = self.scope['url_route']['kwargs']['game_pk']
        self.game_name = f"{game_pk}_game"
        self.game = Game.objects.filter(pk=game_pk).prefetch_related('team_set')

        if not self.secret_key == SECRET_KEY:
            return

        async_to_sync(self.channel_layer.group_add)(
            self.game_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.game_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        state = text_data_json['game_state']
        change_game_state(self.game.first(), state)

        self.send_to_all(self.game.first(), {'type': 'change_state', 'game_state': state})


class TimerConsumer(NextQuestionSender, WebsocketConsumer):

    def connect(self):
        secret_key = self.scope['url_route']['kwargs']['secret_key']
        print('connect...')
        if not secret_key == SECRET_KEY:
            return
        self.accept()

    def receive(self, text_data):
        print(f'{text_data=}')
        team = Team.objects.get(code=text_data)
        print(f'{team=}')
        try:
            self.send_to_next_question(team)
        except Exception as e:
            print(e)
        print('question was send')

        self.close()
