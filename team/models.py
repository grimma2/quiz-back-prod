from django.db import models


class Team(models.Model):
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE)
    code = models.CharField('Код вступления в команду', default=generate_team_code, max_length=5)
    active_question = models.PositiveSmallIntegerField(
        'Номер активного вопроса',
        default=0
    )
