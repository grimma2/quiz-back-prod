# Generated by Django 3.2 on 2022-11-19 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now=True, verbose_name='Время отсчёта таймера вопроса')),
                ('task_id', models.CharField(max_length=99, verbose_name='id таска отвечающего за таймер')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название команды')),
                ('code', models.CharField(default='PJY6V', max_length=5, unique=True, verbose_name='Код вступления в команду')),
                ('active_question', models.PositiveSmallIntegerField(default=0, verbose_name='Номер активного вопроса')),
                ('bonus_points', models.PositiveIntegerField(default=0, verbose_name='Баллы команды')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.game')),
                ('timer', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team', to='team.timer')),
            ],
        ),
    ]
