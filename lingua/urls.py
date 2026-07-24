from django.urls import path

from . import views

app_name = "lingua"

urlpatterns = [
    path("approvals/", views.batch_approval, name="approvals"),
]
