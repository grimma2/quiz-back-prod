from django.contrib import admin

from .models import Team


class TeamAdmin(admin.ModelAdmin):
    list_display = ('game', 'name', 'code', 'active_question', 'pk')
    list_display_links = ('name', 'pk')


admin.site.register(Team, TeamAdmin)
