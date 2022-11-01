import datetime

from celery.contrib.abortable import AbortableAsyncResult
from django.db import models, IntegrityError

from quiz.settings import SYMBOLS_IN_TEAM_CODE
from quiz.celery import app as celery_app
from quichannels.tasks import set_timer

import random


class CodeGenerator:
    ALPHABET_SYMBOLS = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    DIGIT_SYMBOLS = '1234567890_.'

    @classmethod
    def generate_code(cls) -> str:
        all_symbols = cls.ALPHABET_SYMBOLS + cls.DIGIT_SYMBOLS
        return ''.join([random.choice(all_symbols) for _ in range(SYMBOLS_IN_TEAM_CODE)])


class Timer(models.Model):
    start_time = models.DateTimeField('Время отсчёта таймера вопроса', auto_now=True)
    task_id = models.CharField(
        'id таска отвечающего за таймер',
        max_length=99
    )

    def restart(self) -> None:
        old_task = AbortableAsyncResult(self.task_id, app=celery_app)
        old_task.abort()
        new_task = set_timer.apply_async(args=old_task.args)

        self.start_time = datetime.datetime.now()
        self.task_id = new_task.id
        self.save()


class Team(models.Model):
    name = models.CharField('Название команды', max_length=255)
    game = models.ForeignKey('game.Game', on_delete=models.CASCADE)
    code = models.CharField(
        'Код вступления в команду',
        default=CodeGenerator.generate_code(),
        max_length=SYMBOLS_IN_TEAM_CODE,
        unique=True
    )
    active_question = models.PositiveSmallIntegerField('Номер активного вопроса', default=0)
    timer = models.OneToOneField(Timer, on_delete=models.SET_NULL, related_name='team', blank=True, null=True)

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