from django.db import models

from .utils import CodeGenerator


class Team(models.Model):
    name = models.CharField('Название команды', max_length=255)
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE)
    code = models.CharField('Код вступления в команду', default=CodeGenerator.generate_code(), max_length=5)
    active_question = models.PositiveSmallIntegerField(
        'Номер активного вопроса',
        default=0
    )
