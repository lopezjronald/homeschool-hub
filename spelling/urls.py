from django.urls import path

from . import views

app_name = "spelling"

urlpatterns = [
    # Kid surfaces — reached with her signed portal token, no login.
    path("p/<str:token>/", views.home, name="home"),
    path("p/<str:token>/learn/", views.learn, name="learn"),
    path("p/<str:token>/sort/", views.sort_words, name="sort"),
    path("p/<str:token>/quiz/", views.quiz, name="quiz"),
    path("p/<str:token>/dictation/", views.dictation, name="dictation"),
    path("p/<str:token>/answer/", views.answer, name="answer"),
    path("p/<str:token>/finish/", views.finish, name="finish"),
    # Parent surface — normal login + family scoping.
    path("<int:pk>/", views.parent_dashboard, name="parent_dashboard"),
]
