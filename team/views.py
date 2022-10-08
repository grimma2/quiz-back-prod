from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import update_team_codes
from .serializers import TeamSerializer

from game.models import Game


class GenerateTeamCodes(APIView):

    @staticmethod
    def post(request):
        game = Game.objects.filter(pk=request.data['pk']).prefetch_related('team_set')
        serializer = TeamSerializer(update_team_codes(game.first()), many=True)

        return Response(serializer.data)
