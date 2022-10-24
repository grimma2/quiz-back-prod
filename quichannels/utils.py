import json

from asgiref.sync import async_to_sync
from django.db.models import F
from django.forms import model_to_dict

from team.models import Team
from team.utils import get_team_question, get_leader_board

from game.models import Game


def code_is_valid(team: Team) -> None:
    if not team:
        raise Exception('Team with this code not found')


def clear_team_active_question(game: Game):
    for team in game.team_set.all():
        team.active_question = 0
        team.save()


def change_game_state(game: Game, state) -> None:
    game.game_state = state
    game.save()

    if state == 'OFF':
        clear_team_active_question(game)


class GroupMessageSender:

    def send_to_all(self, game: Game, send: dict) -> None:
        print('send_to_all...')
        for team in game.team_set.all():
            print(team.code)
            try:
                async_to_sync(self.channel_layer.group_send)(
                    f'{team.code}_team', send
                )
            except Exception as e:
                print(e)


class TeamConsumerMixin(GroupMessageSender):

    def send_to_next_question(self):
        print(self.team_name)
        async_to_sync(self.channel_layer.group_send)(
            self.team_name,
            {
                'type': 'next_question',
                'event_data': self.get_next_question(),
            }
        )

    def get_next_question(self):
        self.team.active_question = F('active_question') + 1
        self.team.save()
        self.team.refresh_from_db()
        questions = self.team.game.question_set.order_by('order')

        question = get_team_question(self.team.active_question, questions)

        if question:
            return model_to_dict(question)
        else:
            leader_board = get_leader_board(self.team.game)
            self.send_to_all(
                self.team.game, {'type': 'update_leader_board', 'leader_board': leader_board}
            )
            return leader_board


class UpdateLeaderBoardEvent:

    def update_leader_board(self, event):
        self.send(text_data=json.dumps({
            'event': 'update_leader_board',
            'event_data': event['leader_board'],
        }))