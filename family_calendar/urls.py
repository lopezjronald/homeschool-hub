from django.urls import path

from . import views

app_name = "family_calendar"

urlpatterns = [
    path("", views.calendar_page, name="calendar"),
    path("feed/", views.events_feed, name="feed"),
    path("add/", views.event_create, name="event_create"),
    path("<int:pk>/edit/", views.event_update, name="event_update"),
    path("<int:pk>/duplicate/", views.event_duplicate, name="event_duplicate"),
    path("<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("<int:pk>/skip/", views.occurrence_skip, name="occurrence_skip"),
    path("pace/<int:placement_pk>/", views.set_pace, name="set_pace"),
]
