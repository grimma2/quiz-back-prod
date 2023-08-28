from typing import Any
from copy import copy
import random

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
        active_question = get_team_question(self.team)

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


def get_team_question(team: Team):
    try:
        questions = team.game.question_set.all()
        team_question_ordering = list(map(int, team.question_ordering.split(',')))
        question = questions[team_question_ordering[team.active_question]]
    except IndexError:
        return
    else:
        return question


@dataclass(kw_only=True)
class QuestionOrderDependency:
    game: Any

    def set_order_for_teams(self):
        sorted_orders: list[list[int]]

        # пытаемся получить правильный порядок в бесконечном цикле
        # в будущем планируется изменить
        while True:
            try:
                # получаем сгенерированые значения с помощью этой футнкции
                # и колличества команд и вопросов в игре
                sorted_orders = self.sorting(
                    number_of_questions=self.game.question_set.count(),
                    number_of_teams=self.game.team_set.count()
                )
            except IndexError:
                pass
            else:
                break

        for i, question_order in enumerate(sorted_orders):
            question_order = list(map(str, question_order))
            current_team = self.game.team_set.all()[i]

            print(','.join(question_order))

            current_team.question_ordering = ','.join(question_order)
            current_team.save()

    def sorting(self, number_of_questions, number_of_teams):
        question_array = list(range(number_of_questions))
        team_question_order = []

        for team_index in range(number_of_teams):
            team_order = []
            question_array_copy = copy(question_array)

            for i in range(len(question_array)):
                choose_number = random.choice(
                    self.filter_for_unique(question_array_copy, team_question_order, i)
                )
                
                question_array_copy.remove(choose_number)
                team_order.append(choose_number)

            team_question_order.append(team_order)

        return team_question_order

    def filter_for_unique(self, array, team_question_order, index):
        if team_question_order == []:
            return array

        decline_numbers = list(zip(*team_question_order))[index]

        return list(set(array) - set(decline_numbers))
