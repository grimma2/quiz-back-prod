from django.urls import path

from . import views


urlpatterns = [
    path('list/', views.Games.as_view()),
    path('detail/', views.GameDetail.as_view()),
    path('delete-detail/', views.DeleteGameDetail.as_view()),
    path('create/', views.CreateGame.as_view()),
    path('update/', views.UpdateGame.as_view()),

    path('get/leader-board/', views.LeaderBoard.as_view()),
    path('get/question-time/', views.QuestionTime.as_view()),
    path('get/games-cookie/', views.GetGamesCookie.as_view()),

    path('set/games-cookie/', views.SetGamesCookie.as_view()),
    # path('set/detail-state/', views.SetGameState.as_view()),
]
