from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import EmailOrUsernameAuthenticationForm
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("verify/<uidb64>/<token>/", views.verify, name="verify"),
    path("post-login/", views.post_login, name="post_login"),
    path("welcome/", views.welcome, name="welcome"),
    path("hints/dismiss/", views.dismiss_hint, name="dismiss_hint"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=EmailOrUsernameAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    # Settings hub + per-section handlers
    path("settings/", views.settings_view, name="settings"),
    path("settings/account/", views.account_update, name="account_update"),
    path("settings/contact/", views.contact_update, name="contact_update"),
    path("settings/notifications/", views.notifications_update, name="notifications_update"),
    path("settings/preferences/", views.preferences_update, name="preferences_update"),
    path("settings/email/", views.change_email, name="change_email"),
    path(
        "settings/email/confirm/<uidb64>/<token>/",
        views.change_email_confirm,
        name="change_email_confirm",
    ),
    # Change password while signed in (Django built-ins, like the reset flow).
    path(
        "settings/password/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url=reverse_lazy("accounts:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "settings/password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # Password reset flow (Django built-ins)
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/emails/password_reset_email.txt",
            subject_template_name="accounts/emails/password_reset_subject.txt",
            # --- FIX: Tell the view where to redirect on success ---
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            # --- FIX: Also add success_url here for consistency ---
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]