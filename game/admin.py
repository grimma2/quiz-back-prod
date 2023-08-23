from django.contrib import admin

from .models import Game, Question, LeaderBoard, FinishTeam, Hint


class HintAdmin(admin.ModelAdmin):
    list_display = ('text', 'appear_after', 'pk')
    list_display_links = ('text', 'pk')


class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_state', 'pk')
    list_display_links = ('name', 'pk')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('game', 'text', 'order', 'time', 'correct_answers', 'question_type', 'pk')
    list_display_links = ('text', 'pk')


class LeaderBoardAdmin(admin.ModelAdmin):
    list_display = ('game', 'start_time', 'end_date', 'already_end', 'pk')
    list_display_links = ('start_time', 'end_date', 'pk')


class FinishTeamAdmin(admin.ModelAdmin):
    list_display = ('leader_board', 'team', 'finish_date', 'bonus_points', 'pk')
    list_display_links = ('finish_date', 'pk')


admin.site.register(Game, GameAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(LeaderBoard, LeaderBoardAdmin)
admin.site.register(FinishTeam, FinishTeamAdmin)
admin.site.register(Hint, HintAdmin)
