from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from team.models import Team


class Game(models.Model):

    class GameState(models.TextChoices):
        ON = 'ON', _('Game is on')
        OFF = 'OFF', _('Game is off')

    name = models.CharField('Имя', max_length=255)
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
    order = models.PositiveSmallIntegerField(default=1)
    correct_answers = models.JSONField('Правильные ответы на вопрос', default=list)

    class Meta:
        ordering = ['order']


class LeaderBoard(models.Model):
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, related_name='leader_boards')
    start_time = models.DateTimeField('Дата начала игры', default=timezone.now)
    end_date = models.DateTimeField('Дата окончания игры', blank=True, null=True)
    already_end = models.BooleanField('Игра окончена', default=False)

    def finish(self):
        self.end_date = timezone.now()
        self.already_end = True

        for team in self.game.team_set.all():
            FinishTeam.objects.get_or_create(
                team=team, leader_board=self, bonus_points=team.bonus_points
            )

        self.save()
        self.refresh_from_db()


class FinishTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    leader_board = models.ForeignKey(LeaderBoard, on_delete=models.CASCADE)
    finish_date = models.DateTimeField(
        'Дата и время финиша команды', default=timezone.now
    )
    bonus_points = models.PositiveIntegerField('Бонусные баллы', default=0)
