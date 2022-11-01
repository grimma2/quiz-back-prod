from datetime import datetime, date

from django.db.models import QuerySet

from rest_framework.views import APIView
from rest_framework.response import Response

from team.models import Team

from .serializers import GamesSerializer, GameDetailSerializer
from .models import Game, Question
from .utils import (
    update_foreign_key, update_non_foreign_key, parse_non_foreign_key, get_leader_board
)


class Games(APIView):

    @staticmethod
    def post(request):
        queryset = Game.objects.filter(pk__in=request.data['games'])
        serializer = GamesSerializer(queryset, many=True)

        return Response(serializer.data)


class GameDetail(APIView):

    @staticmethod
    def post(request):
        serializer = GameDetailSerializer(Game.objects.get(pk=request.data['pk']))
        return Response(serializer.data)


class SetGameState(APIView):

    @staticmethod
    def post(request):
        game = Game.objects.get(pk=request.data['pk'])
        game.game_state = request.data['game_state']
        game.save()

        return Response(status=200)


class DeleteGameDetail(APIView):

    @staticmethod
    def post(request):
        if Game.objects.filter(pk=request.data['pk']).delete()[0] == 0:
            return Response(status=404)

        return Response(status=200)


class CreateGame(APIView):

    @staticmethod
    def post(request):
        game = Game.objects.create(**parse_non_foreign_key(request.data))

        update_foreign_key(Question, QuerySet(game), request.data['question_set'], game.question_set)
        update_foreign_key(Team, QuerySet(game), request.data['team_set'], game.team_set)

        return Response(data={'pk': game.pk}, status=200)


class UpdateGame(APIView):

    @staticmethod
    def post(request):
        game = Game.objects.filter(pk=request.data['pk'])
        update_non_foreign_key(request.data, game)

        update_foreign_key(Question, game, request.data['question_set'], game.first().question_set)
        update_foreign_key(Team, game, request.data['team_set'], game.first().team_set)

        return Response(data={'pk': game.first().pk}, status=200)


class LeaderBoard(APIView):

    @staticmethod
    def post(request):
        team = Team.objects.filter(code=request.data['code']).select_related('game')
        return Response(data=get_leader_board(team.first().game))


class QuestionTime(APIView):

    @staticmethod
    def post(request):
        game = (
            Team.objects.filter(code=request.data['code']).prefetch_related('game').first().game
        )
        time = datetime.combine(date.min, game.question_time) - datetime.min
        return Response(data={'time': int(time.total_seconds())})
