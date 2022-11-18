from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from quiz.settings import SECRET_KEY

from .utils import (
    code_is_valid, change_game_state, NextQuestionSender,
    GroupMessageSender, UpdateLeaderBoardEvent, SecretKeyValidation
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
        self.team.refresh_from_db(fields=['timer'])
        if text_data_json['type'] == 'next_question':
            try:
                self.send_to_next_question(self.team, text_data_json['bonus_points'])
            except Exception as e:
                print(e)

    def next_question(self, event):
        self.send(text_data=json.dumps({
            'event': 'next_question',
            'event_data': event['event_data'],
        }))

    def change_state(self, event):
        self.send(text_data=json.dumps({
            'event': 'change_state',
            'event_data': event['event_data'],
        }))


class GameConsumer(SecretKeyValidation, UpdateLeaderBoardEvent, GroupMessageSender, WebsocketConsumer):

    def connect(self):
        self.validate_connect()
        game_pk = self.scope['url_route']['kwargs']['game_pk']
        self.game_name = f"{game_pk}_game"
        self.game = Game.objects.filter(pk=game_pk).prefetch_related('team_set')

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

        if text_data_json['type'] == 'change_state':
            change_game_state(self.game.first(), text_data_json['event_data'])
            self.send_to_all(
                self.game.first(),
                {'type': 'change_state', 'event_data': text_data_json['event_data']}
            )

    def game_socket_change_state(self, event):
        self.send(text_data=json.dumps({
            'event': 'change_state',
            'event_data': event['event_data'],
        }))


class TimerConsumer(SecretKeyValidation, UpdateLeaderBoardEvent, NextQuestionSender, WebsocketConsumer):

    def connect(self):
        self.validate_connect()
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


class GameChangeState(SecretKeyValidation, WebsocketConsumer):

    def connect(self):
        print('dsfsghfjkl;hglfkdhss')
        self.validate_connect()
        self.accept()

    def receive(self, text_data):
        print('receive GameChangeState')
        text_data_json = json.loads(text_data)
        print(text_data_json)
        try:
            async_to_sync(self.channel_layer.group_send)(
                f"{text_data_json['pk']}_game",
                {
                    'type': 'game_socket_change_state',
                    'event_data': text_data_json['event_data']
                }
            )
        except Exception as e:
            print(e)
        self.close()

    def game_socket_change_state(self, event):
        self.send(text_data=json.dumps({
            'event': 'change_state',
            'event_data': event['event_data'],
        }))
