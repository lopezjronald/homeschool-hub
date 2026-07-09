from django.urls import path

from . import views

app_name = "curricula"

urlpatterns = [
    path("", views.curriculum_list, name="curriculum_list"),
    path("add/", views.curriculum_create, name="curriculum_create"),
    path("<int:pk>/", views.curriculum_detail, name="curriculum_detail"),
    path("<int:pk>/edit/", views.curriculum_update, name="curriculum_update"),
    path("<int:pk>/delete/", views.curriculum_delete, name="curriculum_delete"),
    path("<int:pk>/apply-blueprint/", views.curriculum_apply_blueprint, name="curriculum_apply_blueprint"),
    path("<int:pk>/documents/add/", views.curriculum_document_add, name="curriculum_document_add"),
    path(
        "<int:pk>/documents/<int:doc_pk>/delete/",
        views.curriculum_document_delete,
        name="curriculum_document_delete",
    ),
    path("<int:pk>/resources/add/", views.curriculum_resource_add, name="curriculum_resource_add"),
    path(
        "<int:pk>/resources/<int:resource_pk>/delete/",
        views.curriculum_resource_delete,
        name="curriculum_resource_delete",
    ),
    path(
        "<int:pk>/children/<int:child_pk>/placement/",
        views.curriculum_set_placement,
        name="curriculum_set_placement",
    ),
]
