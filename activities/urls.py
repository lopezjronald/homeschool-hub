from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="activity_list"),
    path("add/", views.activity_create, name="activity_create"),
    path("<int:pk>/edit/", views.activity_update, name="activity_update"),
    path("<int:pk>/delete/", views.activity_delete, name="activity_delete"),
    path("<int:pk>/checkin/", views.activity_checkin, name="activity_checkin"),
]
