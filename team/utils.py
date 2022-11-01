import logging
from datetime import datetime, date, timedelta, tzinfo
from dataclasses import dataclass

from django.db.models import QuerySet

from game.models import Game
from game.utils import get_leader_board
from game.serializers import QuestionSerializer

from .models import Team, CodeGenerator


ZERO = timedelta(0)


class UTC(tzinfo):

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()


def update_team_codes(game: Game) -> QuerySet:
    for team in game.team_set.all():
        team.code = CodeGenerator.generate_code()
        team.save()

    return game.team_set


@dataclass(kw_only=True)
class TeamDataParser:
    team: Team
    game: Game

    def get_data(self) -> dict:
        if self.game.game_state == 'ON':
            data = self.get_game_on_data()
            data['game_state'] = 'ON'
            return data
        else:
            data = self.get_game_off_data()
            data['game_state'] = 'OFF'
            return data

    def get_game_off_data(self) -> dict:
        return {'leader_board': get_leader_board(self.game)}

    def get_game_on_data(self) -> dict:
        questions = self.game.question_set.order_by('order')
        active_question = get_team_question(self.team.active_question, questions)

        if active_question:
            logging.getLogger('DL').info('get active question with timer')
            return {
                'active_question': QuestionSerializer(active_question).data,
                'timer': self._get_timer_value()
            }
        else:
            return {'leader_board': get_leader_board(self.game)}

    def _get_timer_value(self):
        ques_time = datetime.combine(date.min, self.game.question_time) - datetime.min
        time_passed = datetime.now(utc) - self.team.timer.start_time
        timer_value = ques_time - time_passed

        return int(timer_value.total_seconds())


def get_team_question(active_question_number: int, questions: QuerySet):
    try:
        question = questions[active_question_number]
    except IndexError:
        pass
    else:
        return question