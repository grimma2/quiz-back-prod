# Generated by Django 3.2 on 2022-11-05 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_finishteam_leaderboard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finishteam',
            name='finish_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата и время финиша команды'),
        ),
        migrations.AlterField(
            model_name='leaderboard',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата начала игры'),
        ),
    ]
