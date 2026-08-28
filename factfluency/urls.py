"""Fact Dash lives inside the child's portal, so every route carries her token."""

from django.urls import path

from . import views

app_name = "factfluency"

urlpatterns = [
    path("<str:token>/factdash/", views.factdash_home, name="home"),
    path("<str:token>/factdash/<slug:slug>/", views.factdash_play, name="play"),
    path("<str:token>/factdash/<slug:slug>/start/", views.api_start, name="api_start"),
    path("<str:token>/factdash/session/<int:session_id>/attempts/",
         views.api_attempts, name="api_attempts"),
    path("<str:token>/factdash/session/<int:session_id>/finish/",
         views.api_finish, name="api_finish"),
    path("<str:token>/factdash-progress/", views.api_progress, name="api_progress"),
]
