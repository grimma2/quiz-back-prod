from django.urls import path

from . import views


urlpatterns = [
    path('generate-codes/', views.GenerateTeamCodes.as_view())
]
