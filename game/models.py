from django.db import models
from django.utils.translation import gettext_lazy as _


class Game(models.Model):

    class GameState(models.TextChoices):
        ON = 'ON', _('Game is on')
        OFF = 'OFF', _('Game is off')

    users_in_team_lim = models.PositiveSmallIntegerField(
        'Предел человек в команде',
        default=0
    )
    question_time = models.TimeField('Время на один вопрос')
    game_state = models.CharField(
        max_length=3,
        choices=GameState.choices,
        default=GameState.OFF
    )


class Question(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    text = models.TextField('Текст вопроса')
    order = models.PositiveSmallIntegerField()
    correct_answers = models.JSONField('Правильные ответы на вопрос', default={})
