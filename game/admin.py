from django.contrib import admin

from .models import Game, Question


class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'users_in_team_lim', 'question_time', 'game_state', 'pk')
    list_display_links = ('name', 'pk')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('game', 'text', 'order', 'correct_answers', 'pk')
    list_display_links = ('text', 'pk')


admin.site.register(Game, GameAdmin)
admin.site.register(Question, QuestionAdmin)
