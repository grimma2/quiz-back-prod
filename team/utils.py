from django.db.models import QuerySet
from django.forms import model_to_dict

from game.models import Game
from game.utils import get_leader_board

from .models import Team, CodeGenerator

from dataclasses import dataclass


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
            return {'active_question': model_to_dict(active_question)}
        else:
            return {'leader_board': get_leader_board(self.game)}


def get_team_question(active_question_number: int, questions: QuerySet):
    print(active_question_number)
    try:
        question = questions[active_question_number]
    except IndexError:
        print('indexerror')
        pass
    else:
        return question
