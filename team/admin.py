from django.contrib import admin

from .models import Team, Timer


class TeamAdmin(admin.ModelAdmin):
    list_display = ('game', 'name', 'code', 'active_question', 'pk')
    list_display_links = ('name', 'pk')


class TimerAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'task_id', 'pk')
    list_display_links = ('pk',)


admin.site.register(Timer, TimerAdmin)
admin.site.register(Team, TeamAdmin)
