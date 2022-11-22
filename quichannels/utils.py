import json
import logging
from datetime import datetime, date
from dataclasses import dataclass

from asgiref.sync import async_to_sync
from django.db.models import F

from .tasks import set_timer, send_state_to_consumer

from team.models import Team, Timer
from team.utils import get_team_question

from game.models import Game, FinishTeam, LeaderBoard
from game.serializers import QuestionSerializer
from game.utils import LeaderBoardFetcher


def code_is_valid(team: Team) -> None:
    if not team:
        raise Exception('Team with this code not found')


def game_off_team_basics(game: Game, revoke_timers=True) -> None:
    for team in game.team_set.all():
        team.active_question = 0
        team.bonus_points = 0

        if revoke_timers:
            if team.timer:
                team.save()
                team.timer.delete()
                return

        team.save()


def all_teams_finished(finished_team_question: int, game: Game) -> bool:
    print(game.team_set.all())
    for team in game.team_set.all():
        print(f'check code {team.active_question=}')
        if team.active_question != finished_team_question:
            break
    else:
        return True


def change_game_state(game: Game, state, revoke_timers=True) -> None:
    print('change_game_state')
    game.game_state = state
    game.save()
    dependency = GameTimersDependency(game=game)

    if state == 'OFF':
        LeaderBoardFetcher(game=game).board.finish()
        game_off_team_basics(game, revoke_timers)
    else:
        LeaderBoard.objects.create(game=game)
        dependency.set_timers()


class GroupMessageSender:

    def send_to_all(self, game: Game, send: dict, *, exclude_code=None) -> None:
        teams = (
            game.team_set.all().exclude(code=exclude_code) if exclude_code else game.team_set.all()
        )
        for team in teams:
            async_to_sync(self.channel_layer.group_send)(
                f'{team.code}_team', send
            )


@dataclass(kw_only=True)
class GameTimersDependency:
    game: Game

    def set_timers(self):
        print('set_timers')
        logging.getLogger('DL').info('set_timers...')
        ques_time = datetime.combine(date.min, self.game.question_time) - datetime.min
        for team in self.game.team_set.all():
            print(f'{team.code=}')
            task = set_timer.apply_async(args=[ques_time.total_seconds(), team.code])
            print(f'{task.state=}')
            team.timer = Timer.objects.create(task_id=task.id)
            team.save()

    def revoke_timers(self):
        print('revoke_timers')
        for team in self.game.team_set.all():
            print(f'{team.timer=}')
            if not team.timer:
                return

            team.timer.delete()


class NextQuestionSender(GroupMessageSender):

    def send_to_next_question(self, team: Team, bonus_points: int):
        event_data = self.get_next_question(team, bonus_points)

        if not event_data:
            # not send next_question if we don't need event_data and this is None
            return

        async_to_sync(self.channel_layer.group_send)(
            f'{team.code}_team',
            {
                'type': 'next_question',
                'event_data': event_data,
            }
        )

    def get_next_question(self, team: Team, bonus_points):
        team.active_question = F('active_question') + 1
        team.bonus_points = F('bonus_points') + bonus_points
        team.save()
        team.refresh_from_db()
        questions = team.game.question_set.all()

        question = get_team_question(team.active_question, questions)

        if question:
            # set new timer if new question has begun
            team.timer.restart(
                code=team.code,
                question_time=team.game.question_time
            )
            return QuestionSerializer(question).data
        else:
            # delete timer if question not run anymore
            print('delete timer')
            team.timer.delete()

            fetcher = LeaderBoardFetcher(game=team.game)
            return self.send_to_leader_board(fetcher, team)

    def send_to_leader_board(self, fetcher: LeaderBoardFetcher, team: Team):
        FinishTeam.objects.create(
            team=team, leader_board=fetcher.board, bonus_points=team.bonus_points
        )

        if all_teams_finished(team.active_question, team.game):
            print('all_teams_finished')
            # turn off game if all teams are finished
            change_game_state(team.game, state='OFF', revoke_timers=False)
            send_state_to_consumer.apply_async(args=['OFF', team.game.pk])
            self.send_to_all(team.game, {'type': 'change_state', 'event_data': Game.GameState.OFF})
        else:
            parsed_data = fetcher.parse()
            self.send_to_all(
                team.game,
                {'type': 'update_leader_board', 'event_data': parsed_data},
                exclude_code=team.code
            )
            return parsed_data


class UpdateLeaderBoardEvent:

    def update_leader_board(self, event):
        print(event)
        self.send(text_data=json.dumps({
            'event': 'update_leader_board',
            'event_data': event['event_data'],
        }))
