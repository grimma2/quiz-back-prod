from rest_framework import serializers

from .models import Game, Question

from team.serializers import TeamSerializer


class GamesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ('name', 'game_state', 'pk')


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('text', 'order', 'correct_answers', 'pk')


class GameDetailSerializer(serializers.ModelSerializer):
    team_set = TeamSerializer(many=True)
    question_set = QuestionSerializer(many=True)

    class Meta:
        model = Game
        fields = (
            'name', 'users_in_team_lim', 'question_time',
            'game_state', 'question_set', 'team_set', 'pk'
        )
