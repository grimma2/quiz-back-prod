from django.urls import path

from . import views


urlpatterns = [
    path('generate-codes/', views.GenerateTeamCodes.as_view()),
    path('get/active-question/', views.ActiveQuestion.as_view()),
    path('get/data/', views.DataByCode.as_view())
]
