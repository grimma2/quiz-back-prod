from autologging import traced

import json
from dataclasses import dataclass
from datetime import datetime, date

from asgiref.sync import async_to_sync
from django.db.models import F

from .tasks import set_timer

from team.models import Team, Timer
from team.utils import get_team_question, QuestionOrderDependency

from game.models import Game, FinishTeam, LeaderBoard, Question
from game.serializers import QuestionSerializer
from game.utils import LeaderBoardFetcher


def set_remain_answers(question, teams):
    for team in teams:
        team.remain_answers = question.correct_answers
        team.save()
        team.refresh_from_db()


def game_off_team_basics(game: Game, revoke_timers=True) -> None:
    for team in game.team_set.all():
        team.active_question = 0
        team.bonus_points = 0
        team.question_ordering = ''

        if revoke_timers:
            if team.timer:
                team.save()
                team.timer.delete()
                return

        team.save()


def all_teams_finished(finished_team_question: int, game: Game) -> bool:
    for team in game.team_set.all():
        if team.active_question != finished_team_question:
            break
    else:
        return True


@traced
def change_game_state(game: Game, state, revoke_timers=True) -> None:

    if state == 'OFF':
        fetcher = LeaderBoardFetcher(game=game)
        fetcher.board.finish()
        game_off_team_basics(game, revoke_timers)
    else:
        if (blitz_question := game.question_set.first()).question_type == 'blitz':
            set_remain_answers(blitz_question, game.team_set.all())

        timers_dependency = GameTimersDependency(game=game)
        question_dependency = QuestionOrderDependency(game=game)

        LeaderBoard.objects.create(game=game)

        timers_dependency.set_timers()
        question_dependency.set_order_for_teams()

    game.game_state = state
    game.save()


class GroupMessageSender:

    def send_to_all(self, game: Game, send: dict, *, exclude_code=None) -> None:
        teams = (
            game.team_set.all().exclude(code=exclude_code) if exclude_code else game.team_set.all()
        )
        for team in teams:
            async_to_sync(self.channel_layer.group_send)(
                f'{team.code}_team', send
            )

# timer utils below
def question_hints_for_timer(question: Question) -> dict[int, int]:
    '''
    question: question model
    return: dict with keys as hint's pks what contain question's field `question.hints`
            with m2m relation
    '''
    result = {}
    for hint in question.hints.all():
        hint_key = (datetime.combine(date.min, hint.appear_after) - datetime.min).total_seconds()
        result[int(hint_key)] = int(hint.pk)
        
    return result


@dataclass(kw_only=True)
class GameTimersDependency:
    game: Game

    def set_timers(self):
        # !FIXME получить первый вопрос, чтобы установить таймер,
        # вместо того, чтобы брать время из инстанса игры
        # was fixed теперь получаем первый вопрос игры и берём у него время
        first_question = self.game.question_set.first()
        for team in self.game.team_set.all():
            # run task with needed args
            
            task = set_timer.apply_async(
                args=[
                    team.code, 
                    question_hints_for_timer(first_question)
                ]
            )
            
            # create new timer for watching when task was runned and save this changes in Team model
            team.timer = Timer.objects.create(task_id=task.id)
            team.save()

# end timer utils

class NextQuestionSender(GroupMessageSender):

    def send_to_next_question(self, team: Team, bonus_points: int):
        event_data = self.get_next_question(team, bonus_points)

        if not event_data:
            # not send next_question if we don't need event_data and this is None
            return

        async_to_sync(self.channel_layer.group_send)(
            f'{team.code}_team',
            {
                'type': 'next_question',
                'event_data': event_data,
            }
        )

    def get_next_question(self, team: Team, bonus_points):
        # clear remain_answers field for previous question if it is blitz type
        self._clear_current_question(
            get_team_question(team), team
        )

        team.active_question = F('active_question') + 1
        team.bonus_points = F('bonus_points') + bonus_points
        team.save()
        team.refresh_from_db()

        question = get_team_question(team)

        if question:
            if question.question_type == 'blitz':
                team.remain_answers = question.correct_answers
                team.save()

            # set new timer if new question has begun
            '''
            was changed from `question_time=team.game.question_time` to
            `question_time=question.time
            '''
            team.timer.restart(
                code=team.code,
                hints=question_hints_for_timer(question)
            )
            return QuestionSerializer(question).data
        else:
            # delete timer if question not run anymore
            team.timer.delete()

            fetcher = LeaderBoardFetcher(game=team.game)
            return self.send_to_leader_board(fetcher, team)

    def send_to_leader_board(self, fetcher: LeaderBoardFetcher, team: Team):
        FinishTeam.objects.create(
            team=team, leader_board=fetcher.board, bonus_points=team.bonus_points
        )

        if all_teams_finished(team.active_question, team.game):
            # turn off game if all teams are finished
            change_game_state(team.game, state='OFF', revoke_timers=False)
            async_to_sync(self.channel_layer.group_send)(
                f'{team.game.pk}_game',
                {
                    'type': 'game_socket_change_state',
                    'event_data': 'OFF'
                }
            )

            self.send_to_all(team.game, {'type': 'change_state', 'event_data': Game.GameState.OFF})
        else:
            parsed_data = fetcher.parse()
            self.send_to_all(
                team.game,
                {'type': 'update_leader_board', 'event_data': parsed_data},
                exclude_code=team.code
            )
            return parsed_data

    @staticmethod
    def _clear_current_question(question, team: Team):
        if question.question_type == 'blitz':
            team.remain_answers = None


class UpdateLeaderBoardEvent:

    def update_leader_board(self, event):
        self.send(text_data=json.dumps({
            'event': 'update_leader_board',
            'event_data': event['event_data'],
        }))


def code_is_valid(team_code: str, received_code: str):
    if team_code != received_code.strip():
        raise Exception('received code is not valid')
