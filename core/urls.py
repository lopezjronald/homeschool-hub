from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("invites/new/", views.invite_teacher, name="invite_teacher"),
    path(
        "invites/<uuid:invite_id>/resend/",
        views.resend_invite,
        name="resend_invite",
    ),
    path(
        "invites/accept/<uuid:invite_id>/",
        views.accept_invite,
        name="accept_invite",
    ),
]
