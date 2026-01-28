from django.urls import path

from . import views

app_name = "assignments"

urlpatterns = [
    path("", views.assignment_list, name="assignment_list"),
    path("create/", views.assignment_create, name="assignment_create"),
    path("<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("<int:pk>/update/", views.assignment_update, name="assignment_update"),
    path("<int:pk>/delete/", views.assignment_delete, name="assignment_delete"),
    path("<int:pk>/resources/add/", views.resource_link_add, name="resource_link_add"),
    path("resources/<int:link_pk>/delete/", views.resource_link_delete, name="resource_link_delete"),
    path("s/<str:token>/", views.assignment_student_update, name="assignment_student_update"),
]
