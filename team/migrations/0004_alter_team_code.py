# Generated by Django 3.2 on 2022-12-12 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0003_auto_20221212_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='code',
            field=models.CharField(default='R10UL', max_length=5, unique=True, verbose_name='Код вступления в команду'),
        ),
    ]