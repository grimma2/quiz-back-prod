import json
import logging
from datetime import datetime, date
from dataclasses import dataclass

from celery.contrib.abortable import AbortableAsyncResult
from asgiref.sync import async_to_sync
from django.db.models import F

from .tasks import set_timer

from quiz.celery import app as celery_app

from team.models import Team, Timer
from team.utils import get_team_question, get_leader_board

from game.models import Game
from game.serializers import QuestionSerializer


def code_is_valid(team: Team) -> None:
    if not team:
        raise Exception('Team with this code not found')


def clear_team_active_question(game: Game):
    for team in game.team_set.all():
        team.active_question = 0
        team.save()


def change_game_state(game: Game, state) -> None:
    print('change_game_state')
    logging.getLogger('DL').info('change_game_state')
    game.game_state = state
    game.save()
    dependency = GameTimersDependency(game=game)

    if state == 'OFF':
        clear_team_active_question(game)
        dependency.revoke_timers()
    else:
        dependency.set_timers()


class GroupMessageSender:

    def send_to_all(self, game: Game, send: dict) -> None:
        for team in game.team_set.all():
            async_to_sync(self.channel_layer.group_send)(
                f'{team.code}_team', send
            )


@dataclass(kw_only=True)
class GameTimersDependency:
    game: Game

    def set_timers(self):
        print('set_timers')
        logging.getLogger('DL').info('set_timers...')
        ques_time = datetime.combine(date.min, self.game.question_time) - datetime.min
        print(f'{ques_time=}')
        for team in self.game.team_set.all():
            print(f'{team.code=}')
            task = set_timer.apply_async(args=[ques_time.total_seconds(), team.code])
            print(f'{task.state=}')
            team.timer = Timer.objects.create(task_id=task.id)
            team.save()

    def revoke_timers(self):
        print('revoke_timers')
        for team in self.game.team_set.all():
            print(f'{team.timer=}')
            if not team.timer:
                return

            print('before revoke')
            AbortableAsyncResult(team.timer.task_id, app=celery_app).abort()
            team.timer.delete()
            print('after revoke')


class NextQuestionSender(GroupMessageSender):

    def send_to_next_question(self, team: Team):
        async_to_sync(self.channel_layer.group_send)(
            f'{team.code}_team',
            {
                'type': 'next_question',
                'event_data': self.get_next_question(team),
            }
        )

    def get_next_question(self, team: Team):
        team.active_question = F('active_question') + 1
        team.save()
        team.refresh_from_db()
        questions = team.game.question_set.order_by('order')

        question = get_team_question(team.active_question, questions)

        if question:
            # set new timer if new question has begun
            team.timer.restart()
            return QuestionSerializer(question).data
        else:
            # delete timer if question not run anymore
            print('delete timer')
            team.timer.delete()

            leader_board = get_leader_board(team.game)
            self.send_to_all(
                team.game, {'type': 'update_leader_board', 'leader_board': leader_board}
            )
            return leader_board


class UpdateLeaderBoardEvent:

    def update_leader_board(self, event):
        self.send(text_data=json.dumps({
            'event': 'update_leader_board',
            'event_data': event['leader_board'],
        }))
