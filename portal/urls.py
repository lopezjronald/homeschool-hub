from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("<str:token>/", views.portal_home, name="portal_home"),
    path("<str:token>/subject/<int:curriculum_id>/", views.portal_subject, name="portal_subject"),
    path("<str:token>/materials/<int:pk>/", views.portal_material, name="portal_material"),
    path("<str:token>/questions/<int:set_pk>/", views.portal_questions, name="portal_questions"),
    path("<str:token>/questions/<int:set_pk>/autosave/", views.portal_autosave, name="portal_autosave"),
    path("<str:token>/questions/<int:set_pk>/feedback/", views.portal_feedback, name="portal_feedback"),
    path(
        "<str:token>/questions/<int:set_pk>/feedback/generate/",
        views.portal_feedback_generate,
        name="portal_feedback_generate",
    ),
]
