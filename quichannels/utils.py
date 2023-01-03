import json
from dataclasses import dataclass
from datetime import datetime, date

from asgiref.sync import async_to_sync
from django.db.models import F

from .tasks import set_timer

from team.models import Team, Timer
from team.utils import get_team_question

from game.models import Game, FinishTeam, LeaderBoard
from game.serializers import QuestionSerializer
from game.utils import LeaderBoardFetcher


def set_remain_answers(question, teams):
    print(f'{question.correct_answers=}')
    for team in teams:
        team.remain_answers = question.correct_answers
        team.save()
        print(f'before refresh {team.remain_answers=}')
        team.refresh_from_db()
        print(f'after refresh {team.remain_answers=}')


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
    for team in game.team_set.all():
        if team.active_question != finished_team_question:
            break
    else:
        return True


def change_game_state(game: Game, state, revoke_timers=True) -> None:

    if state == 'OFF':
        fetcher = LeaderBoardFetcher(game=game)
        fetcher.board.finish()
        game_off_team_basics(game, revoke_timers)
    else:
        if (blitz_question := game.question_set.first()).question_type == 'blitz':
            set_remain_answers(blitz_question, game.team_set.all())
        else:
            print(blitz_question.question_type)
        dependency = GameTimersDependency(game=game)
        LeaderBoard.objects.create(game=game)
        dependency.set_timers()

    game.game_state = state
    game.save()


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
        ques_time = datetime.combine(date.min, self.game.question_time) - datetime.min
        for team in self.game.team_set.all():
            task = set_timer.apply_async(args=[ques_time.total_seconds(), team.code])
            team.timer = Timer.objects.create(task_id=task.id)
            team.save()

    def revoke_timers(self):
        for team in self.game.team_set.all():
            print(f'{team.timer}')
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
        questions = team.game.question_set.all()
        # clear remain_answers field for previous question if it is blitz type
        self._clear_current_question(get_team_question(team.active_question, questions), team)
        team.active_question = F('active_question') + 1
        team.bonus_points = F('bonus_points') + bonus_points
        team.save()
        team.refresh_from_db()

        question = get_team_question(team.active_question, questions)

        if question:
            if question.question_type == 'blitz':
                team.remain_answers = question.correct_answers
                team.save()

            # set new timer if new question has begun
            team.timer.restart(
                code=team.code,
                question_time=team.game.question_time
            )
            return QuestionSerializer(question).data
        else:
            # delete timer if question not run anymore
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
            print('before send')
            async_to_sync(self.channel_layer.group_send)(
                f'{team.game.pk}_game',
                {
                    'type': 'game_socket_change_state',
                    'event_data': 'OFF'
                }
            )

            self.send_to_all(team.game, {'type': 'change_state', 'event_data': Game.GameState.OFF})
        else:
            parsed_data = fetcher.parse()
            self.send_to_all(
                team.game,
                {'type': 'update_leader_board', 'event_data': parsed_data},
                exclude_code=team.code
            )
            return parsed_data

    @staticmethod
    def _clear_current_question(question, team: Team):
        if question.question_type == 'blitz':
            print('_clear_current_question...')
            team.remain_answers = None


class UpdateLeaderBoardEvent:

    def update_leader_board(self, event):
        self.send(text_data=json.dumps({
            'event': 'update_leader_board',
            'event_data': event['event_data'],
        }))


def code_is_valid(team_code: str, received_code: str):
    if team_code != received_code.strip():
        raise Exception('received code is not valid')
