from dataclasses import dataclass
from datetime import datetime, date

from django.db.models import QuerySet
from django.utils import timezone

from game.models import Game
from game.utils import LeaderBoardFetcher
from game.serializers import QuestionSerializer

from .models import Team, CodeGenerator


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
        fetcher = LeaderBoardFetcher(game=self.game)
        return {'leader_board': fetcher.parse()}

    def get_game_on_data(self) -> dict:
        questions = self.game.question_set.all()
        active_question = get_team_question(self.team.active_question, questions)

        if active_question:
            return {
                'active_question': QuestionSerializer(active_question).data,
                'timer': self._get_timer_value(),
                'remain_answers': self.team.remain_answers if active_question.question_type == 'blitz' else None
            }
        else:
            fetcher = LeaderBoardFetcher(game=self.game)
            return {'leader_board': fetcher.parse()}

    def _get_timer_value(self):
        ques_time = datetime.combine(date.min, self.game.question_time) - datetime.min
        time_passed = timezone.now() - self.team.timer.start_time
        timer_value = ques_time - time_passed

        return int(timer_value.total_seconds())


def get_team_question(active_question_number: int, questions: QuerySet):
    try:
        question = questions[active_question_number]
    except IndexError:
        return
    else:
        return question
