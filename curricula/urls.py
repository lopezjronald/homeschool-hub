from django.urls import path

from . import views

app_name = "curricula"

urlpatterns = [
    path("", views.curriculum_list, name="curriculum_list"),
    path("add/", views.curriculum_create, name="curriculum_create"),
    path("<int:pk>/", views.curriculum_detail, name="curriculum_detail"),
    path("<int:pk>/edit/", views.curriculum_update, name="curriculum_update"),
    path("<int:pk>/delete/", views.curriculum_delete, name="curriculum_delete"),
]
