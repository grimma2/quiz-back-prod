from django.db.models import QuerySet

from quiz.settings import SYMBOLS_IN_TEAM_CODE

from game.models import Game

import random


class CodeGenerator:
    ALPHABET_SYMBOLS = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    DIGIT_SYMBOLS = '1234567890'
    SPECIAL_SYMBOLS = '!@#)(*'

    @classmethod
    def generate_code(cls) -> str:
        all_symbols = cls.ALPHABET_SYMBOLS + cls.DIGIT_SYMBOLS + cls.SPECIAL_SYMBOLS
        return ''.join([random.choice(all_symbols) for _ in range(SYMBOLS_IN_TEAM_CODE)])


def update_team_codes(game: Game) -> QuerySet:
    for team in game.team_set.all():
        team.code = CodeGenerator.generate_code()
        team.save()

    return game.team_set
