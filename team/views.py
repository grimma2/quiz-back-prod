from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import update_team_codes, TeamDataParser
from .serializers import TeamSerializer
from .models import Team

from game.models import Game
from game.serializers import QuestionSerializer


class GenerateTeamCodes(APIView):

    @staticmethod
    def post(request):
        game = Game.objects.filter(pk=request.data['pk']).prefetch_related('team_set')
        serializer = TeamSerializer(update_team_codes(game.first()), many=True)

        return Response(serializer.data)


class ActiveQuestion(APIView):

    @staticmethod
    def post(request):
        team = (
            Team.objects.filter(code=request.data['code']).select_related('game').prefetch_related('game__question_set')
        )

        print(team.first().game.question_set.all())
        question = team.first().game.question_set.all()[team.first().active_question]
        serializer = QuestionSerializer(question)

        return Response(serializer.data)


class DataByCode(APIView):

    @staticmethod
    def post(request):
        team = (
            Team.objects.filter(code=request.data['code']).select_related('game').prefetch_related('game__question_set')
        )
        parser = TeamDataParser(team=team.first(), game=team.first().game)

        return Response(parser.get_data())

