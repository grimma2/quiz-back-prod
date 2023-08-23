from dataclasses import dataclass, field
from operator import itemgetter
from typing import Any
from datetime import time as datetime_time, timedelta

from autologging import logged

from django.db.models import Model, QuerySet

from quiz.settings import SECONDS_FOR_SINGLE_POINT
from .models import Game, LeaderBoard, Question, Hint


def timedelta_to_str(time: timedelta):
    seconds = int(time.total_seconds())
    print(f'{seconds}')
    # 3600 seconds = 1 hour
    hours = seconds // 3600
    minutes = seconds // 60 - hours * 60
    converted_seconds = seconds - (hours * 3600 + minutes * 60)
    print(f'{minutes}:{converted_seconds}', f'{hours}')

    return f'{hours}:{minutes}:{converted_seconds}' if hours else f'{minutes}:{converted_seconds}'


def parse_time_field(time: str):
    minutes, seconds = map(int, time.split(':')[1:])
    return datetime_time(minute=minutes, second=seconds)


def parse_non_foreign_key(fields: dict) -> dict:
    return (
        {key: value for key, value in fields.items() if not isinstance(value, list)}
    )


def update_foreign_key(model, game, field_: list[dict], game_manager):
    converted_pks = []
    unconverted_pks = []
    for instance in field_:
        try:
            int(instance['pk'])
        except ValueError:
            # 'unconverted_pks' be only created new model instances
            unconverted_pks.append(instance)
        else:
            converted_pks.append(instance)

    updater = ForeignKeyUpdater(model=model, game=game, game_manager=game_manager)
    # WARNING! Is necessarily call 'update_instances' before 'create_instances'
    # because 'update_instances' entirely override model field
    updater.update_instances(converted_pks)
    updater.create_instances(unconverted_pks)


def update_non_foreign_key(fields: dict, instance: QuerySet):
    # delete pk field
    fields.pop('pk')
    instance.update(**parse_non_foreign_key(fields))


@logged
@dataclass(kw_only=True)
class ForeignKeyUpdater:
    model: Model
    game: Game
    game_manager: Any

    def create_instances(self, instances: list[dict]) -> None:
        print(instances)
        for instance in instances:
            instance.pop('pk')

            if self.model == Hint:
                hint = self.model.objects.create(**instance)
                self.game.hints.add(hint)
            elif self.model == Question:
                hints = instance.pop('hints')
                new_obj = self.model.objects.create(**instance, game=self.game)
                instance['pk'] = new_obj.pk
                instance['hints'] = hints
            else:
                self.model.objects.create(**instance, game=self.game)

    def update_instances(self, instances: list[dict]) -> None:
        updated_pks = [instance['pk'] for instance in instances]

        for remain in self.game_manager.all():
            if not (remain.pk in updated_pks):
                # delete instances what was removed
                self.game_manager.filter(pk=remain.pk).delete()
                continue
            print('delete remain in loop')
            update_fields = [instance for instance in instances if int(instance['pk']) == remain.pk][0]

            if self.model.__class__.__name__ == 'Team':
                delete_fields = ['code']
            elif self.model == Question:
                delete_fields = ['hints']
            else: 
                delete_fields = []

            update_fields = self.parse_fields(fields=update_fields)

            deleter = TemporaryDelete(work_object=update_fields, delete_fields=delete_fields)
            deleter.delete()
            obj, _ = self.model.objects.update_or_create(pk=remain.pk, defaults=deleter.work_object)
            self.add_hint(hint=obj)
            deleter.recover()
            instances.remove(deleter.work_object)
            
    def parse_fields(self, fields: dict):        
        if 'time' in fields.keys():
            fields['time'] = parse_time_field(fields['time'])
        elif 'appear_after' in fields.keys():
            fields['appear_after'] = parse_time_field(fields['appear_after'])

        return fields
    
    def add_hint(self, hint):
        if type(self.game) == Question:
            self.game.hints.add(hint)



class LeaderBoardFetcher:
    board: LeaderBoard
    game: Game
    use_bonus_points: bool = False

    def __init__(self, game: Game):
        self.game = game
        if game.game_state == Game.GameState.ON:
            self.board = self.get_game_on()
        elif game.game_state == Game.GameState.OFF:
            self.use_bonus_points = True
            self.board = self.get_game_off()

    def get_game_on(self) -> LeaderBoard:
        board = LeaderBoard.objects.filter(already_end=False, game=self.game).prefetch_related('finishteam_set')
        if board.exists():
            if len(board) > 1:
                raise Exception('Found more then 1 LeaderBoard for game_on state')
            return board.first()
        else:
            raise Exception('Not found leader_board for game_on state')

    def get_game_off(self) -> LeaderBoard:
        board = LeaderBoard.objects.filter(game=self.game).prefetch_related(
            'finishteam_set'
        ).order_by('end_date').last()
        return board

    def parse(self):
        if not self.board:
            return

        self.board.refresh_from_db()
        finish_teams = self.board.finishteam_set.all()
        teams = []

        for finish_team in finish_teams:
            if not finish_team.team:
                continue

            if self.use_bonus_points:
                finish_team_date = (
                    finish_team.finish_date - timedelta(seconds=finish_team.bonus_points * SECONDS_FOR_SINGLE_POINT)
                )
            else:
                finish_team_date = finish_team.finish_date

            play_time = finish_team_date - finish_team.leader_board.start_time

            print(f'play_time seconds: {play_time.total_seconds()}')

            teams.append(
                {
                    'name': finish_team.team.name,
                    'play_time': timedelta_to_str(play_time),
                    'bonus_seconds': finish_team.bonus_points
                }
            )

        return {'leader_board': sorted(teams, key=itemgetter('play_time'))}


@dataclass(kw_only=True)
class TemporaryDelete:
    work_object: dict
    delete_fields: dict
    deleted: dict = field(default_factory=dict)

    def delete(self):
        for field_ in self.delete_fields:
            self.deleted[field_] = self.work_object.pop(field_)

    def recover(self):
        self.work_object.update(self.deleted)
