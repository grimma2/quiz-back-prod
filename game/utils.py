from dataclasses import dataclass
from typing import Any
from datetime import time as datetime_time

from django.db.models import Model, QuerySet


def parse_time_field(time: str):
    hours, minutes, seconds = map(int, time.split(':'))
    return datetime_time(minute=minutes, second=seconds)


def parse_non_foreign_key(fields: dict) -> dict:
    # parse time field to datetime.time instance
    fields['question_time'] = parse_time_field(fields['question_time'])

    return (
        {key: value for key, value in fields.items() if not isinstance(value, list)}
    )


def update_foreign_key(model, game, field: list[dict], game_manager):
    converted_pks = []
    unconverted_pks = []
    for instance in field:
        try:
            int(instance['pk'])
        except ValueError:
            # 'unconverted_pks' be only created new model instances
            unconverted_pks.append(instance)
        else:
            converted_pks.append(instance)

    updater = ForeignKeyUpdater(model, game, game_manager)
    # WARNING! Is necessarily call 'update_instances' before 'create_instances'
    # because 'update_instances' entirely override model field
    updater.update_instances(converted_pks)
    updater.create_instances(unconverted_pks)


def update_non_foreign_key(fields: dict, instance: QuerySet):
    # delete pk field
    fields.pop('pk')
    instance.update(**parse_non_foreign_key(fields))


@dataclass
class ForeignKeyUpdater:
    model: Model
    game: QuerySet
    game_manager: Any

    def create_instances(self, instances: list[dict]) -> None:
        for instance in instances:
            instance.pop('pk')
            self.model.objects.create(**instance, game=self.game.first())

    def update_instances(self, instances: list[dict]) -> None:
        updated_pks = [instance['pk'] for instance in instances]
        for remain in self.game_manager.all():
            if not remain.pk in updated_pks:
                QuerySet(remain).delete()
                continue

            update_fields = [instance for instance in instances if int(instance['pk']) == remain.pk][0]
            update_fields.pop('pk')
            QuerySet(remain).update(**update_fields)
