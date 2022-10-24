from django.db import models, IntegrityError

from quiz.settings import SYMBOLS_IN_TEAM_CODE

import random


class CodeGenerator:
    ALPHABET_SYMBOLS = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    DIGIT_SYMBOLS = '1234567890_.'

    @classmethod
    def generate_code(cls) -> str:
        all_symbols = cls.ALPHABET_SYMBOLS + cls.DIGIT_SYMBOLS
        return ''.join([random.choice(all_symbols) for _ in range(SYMBOLS_IN_TEAM_CODE)])


class Team(models.Model):
    name = models.CharField('Название команды', max_length=255)
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE)
    code = models.CharField(
        'Код вступления в команду',
        default=CodeGenerator.generate_code(),
        max_length=SYMBOLS_IN_TEAM_CODE,
        unique=True
    )
    active_question = models.PositiveSmallIntegerField(
        'Номер активного вопроса',
        default=0
    )

    def save(self, *args, **kwargs):
        while True:
            try:
                super().save(*args, **kwargs)
            except IntegrityError as e:
                if not (('UNIQUE' in str(e)) and ('team_team.code' in str(e))):
                    break
                continue
            else:
                break
