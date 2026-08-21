from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("families/settings/", views.family_settings, name="family_settings"),
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
    path(
        "families/members/<int:membership_id>/remove/",
        views.remove_member,
        name="remove_member",
    ),
    path("handoff/", views.handoff_new, name="handoff_new"),
    path("handoff/preview/", views.handoff_preview, name="handoff_preview"),
    path("handoff/people/", views.handoff_recipients, name="handoff_recipients"),
    path("handoff/people/<int:pk>/remove/", views.handoff_recipient_remove,
         name="handoff_recipient_remove"),
    path("handoff/<int:pk>/send/", views.handoff_send, name="handoff_send"),
]
