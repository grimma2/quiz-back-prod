from typing import Any

from dataclasses import dataclass
from datetime import datetime, date

from autologging import logged

from django.db.models import QuerySet
from django.utils import timezone

from game.utils import LeaderBoardFetcher
from game.serializers import QuestionSerializer, HintSerializer
from game.models import Question

from .models import Team, CodeGenerator


def update_team_codes(game) -> QuerySet:
    for team in game.team_set.all():
        team.code = CodeGenerator.generate_code()
        team.save()

    return game.team_set


@logged
@dataclass(kw_only=True)
class QuestionTimeUtils:
    question: Question
    team: Team

    def get_timer_value(self) -> int:
        time_passed = (datetime.min + (timezone.now() - self.team.timer.start_time)).time()

        self.__log.debug(f'hints: {self.question.hints.filter(appear_after__gt=time_passed)}')
        if (hints := self.question.hints.filter(appear_after__gt=time_passed)):
            hint_time = hints.first().appear_after

            timer_value = (
                (datetime.combine(date.min, hint_time) - datetime.min) -
                (datetime.combine(date.min, time_passed) - datetime.min)
            )

            return int(timer_value.total_seconds())

        return 0

    def get_active_hints(self):
        # get hints what already should appear
        time_passed_timedelta = timezone.now() - self.team.timer.start_time
        time_passed = (datetime.min + time_passed_timedelta).time()
        return self.question.hints.filter(appear_after__lte=time_passed)


@dataclass(kw_only=True)
class TeamDataParser:
    team: Team
    game: Any

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
        fetcher = LeaderBoardFetcher(game=self.game)
        return {'leader_board': fetcher.parse()}

    def get_game_on_data(self) -> dict:
        questions = self.game.question_set.all()
        active_question = get_team_question(self.team.active_question, questions)

        dependency = QuestionTimeUtils(team=self.team, question=active_question)

        if active_question:
            return {
                'active_question': QuestionSerializer(active_question).data,
                'timer': dependency.get_timer_value(),
                'remain_answers': self.team.remain_answers if active_question.question_type == 'blitz' else None,
                'hints': HintSerializer(dependency.get_active_hints(), many=True).data
            }
        else:
            fetcher = LeaderBoardFetcher(game=self.game)
            return {'leader_board': fetcher.parse()}


def get_team_question(active_question_number: int, questions: QuerySet):
    try:
        question = questions[active_question_number]
    except IndexError:
        return
    else:
        return question
