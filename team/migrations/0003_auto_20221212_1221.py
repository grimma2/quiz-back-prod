# Generated by Django 3.2 on 2022-12-12 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_alter_team_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='remain_answers',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='code',
            field=models.CharField(default='IZ_CB', max_length=5, unique=True, verbose_name='Код вступления в команду'),
        ),
    ]
