from django.urls import path

from . import views

app_name = "lingua"

urlpatterns = [
    path("approvals/", views.batch_approval, name="approvals"),
    path("progress/", views.progress, name="progress"),
    path("read/<int:story_id>/", views.read_story, name="read"),
]
