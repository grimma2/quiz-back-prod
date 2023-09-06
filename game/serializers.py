from rest_framework import serializers

from .models import Game, Question, Hint

from team.serializers import TeamSerializer


class GamesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ('name', 'game_state', 'pk')


class HintSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Hint
        fields = ('text', 'appear_after', 'pk')


class QuestionSerializer(serializers.ModelSerializer):
    hints = HintSerializer(many=True)
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Question
        fields = ('text', 'order', 'correct_answers', 'question_type', 'image', 'hints', 'pk')


class GameDetailSerializer(serializers.ModelSerializer):
    team_set = TeamSerializer(many=True)
    question_set = QuestionSerializer(many=True)

    class Meta:
        model = Game
        fields = (
            'name', 'game_state', 'question_set', 'team_set', 'pk'
        )
