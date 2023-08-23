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

    class Meta:
        model = Question
        fields = ('text', 'order', 'correct_answers', 'question_type', 'time', 'pk')


class QuestionSerializerWithHints(serializers.ModelSerializer):
    hints = HintSerializer(many=True)

    class Meta:
        model = Question
        fields = ('text', 'order', 'correct_answers', 'question_type', 'hints', 'time', 'pk')


class GameDetailSerializer(serializers.ModelSerializer):
    team_set = TeamSerializer(many=True)
    question_set = QuestionSerializerWithHints(many=True)

    class Meta:
        model = Game
        fields = (
            'name', 'game_state', 'question_set', 'team_set', 'pk'
        )
