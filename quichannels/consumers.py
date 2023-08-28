from autologging import logged, traced

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.db.models import F

from game.serializers import HintSerializer

from .utils import (
    change_game_state, NextQuestionSender,
    GroupMessageSender, UpdateLeaderBoardEvent, code_is_valid
)

from team.models import Team

from game.models import Game, Hint

import json



@logged
@traced
class TeamConsumer(NextQuestionSender, UpdateLeaderBoardEvent, WebsocketConsumer):

    def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        print(self.code)
        self.team = (
            Team.objects.filter(code=self.code).select_related('game').prefetch_related('game__question_set').first()
        )
        self.team_name = f'{self.code}_team'
        code_is_valid(self.team.code, self.code)

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
        self.team.refresh_from_db()
        if text_data_json['type'] == 'next_question':
            try:
                self.send_to_next_question(self.team, text_data_json['bonus_points'])
            except Exception as e:
                print(e)
        elif text_data_json['type'] == 'decrement_remain_answers':
            try:
                # self.team.refresh_from_db()
                print('decrement_remain_answers')
                print(self.team.remain_answers)
                for i, answer in enumerate(self.team.remain_answers):
                    if answer['text'] == text_data_json['answer_text']:
                        del self.team.remain_answers[i]
                    else:
                        print(f"{answer['text']} !== {text_data_json['answer_text']}")

                if self.team.remain_answers:
                    print(f'{self.team.remain_answers=}')
                    if text_data_json['bonus_points']:
                        self.team.bonus_points = F('bonus_points') + text_data_json['bonus_points']
                    self.team.save()

                    async_to_sync(self.channel_layer.group_send)(
                        self.team_name,
                        {
                            'type': 'send_remain_answers',
                            'event_data': self.team.remain_answers
                        }
                    )

                    print('after send_remain_answers to all')
                else:
                    print(f'{self.team.remain_answers} after')
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

    def game_socket_change_state(self, event):
        self.send(text_data=json.dumps({
            'event': 'change_state',
            'event_data': event['event_data'],
        }))

    def send_remain_answers(self, event):
        self.send(text_data=json.dumps({
            'event': 'decrement_remain_answers',
            'event_data': event['event_data'],
        }))

    def add_hint(self, event):
        self.send(text_data=json.dumps({
            'event': 'add_hint',
            'event_data': event['event_data'],
        }))


@logged
@traced
class GameConsumer(UpdateLeaderBoardEvent, GroupMessageSender, WebsocketConsumer):

    def connect(self):
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


class HintConsumer(WebsocketConsumer):

    def connect(self):
        print('hint connect...')
        self.accept()

    def receive(self, text_data):
        try:
            hint_pk, code = text_data.split(', ')
            hint = Hint.objects.get(pk=hint_pk)

            async_to_sync(self.channel_layer.group_send)(
                f'{code}_team',
                {
                    'type': 'add_hint',
                    'event_data': HintSerializer(hint).data
                }
            )
        except Exception as e:
            print(e)

        self.close()
