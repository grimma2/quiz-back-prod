from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import GamesSerializer, GameDetailSerializer

from .models import Game


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
