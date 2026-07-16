from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from core.permissions import user_can_edit

from .forms import (
    AccountNameForm,
    ChangeEmailForm,
    ContactForm,
    NotificationsForm,
    PreferencesForm,
    RegisterForm,
)
from .models import UserProfile
from .services import UserService

User = get_user_model()


@csrf_protect
def register(request):
    """Register a new user and send a verification email."""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            verify_url = UserService.build_verify_link(request, user)
            UserService.send_verification_email(user=user, verify_url=verify_url)
            messages.success(
                request,
                "If that email is valid, we sent a verification link. Please check your inbox.",
            )
            return redirect("accounts:login")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@csrf_protect
def verify(request, uidb64: str, token: str):
    """Activate a user if token is valid; otherwise show a safe error."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        messages.success(request, "Email verified. You may now log in.")
        return redirect("accounts:login")

    messages.error(request, "The verification link is invalid or has expired.")
    return redirect("accounts:login")


@login_required
def post_login(request):
    """Route a user after login: first-timers to the welcome page, read-only
    reviewers to Progress, everyone else to the hub. LOGIN_REDIRECT_URL points
    here (Django still honors a safe ``?next=`` before reaching this view)."""
    profile = UserProfile.get_for(request.user)
    if not profile.has_seen_welcome:
        return redirect("accounts:welcome")
    # Honour an explicit landing preference (inbox only for editors, who have one).
    if profile.landing == "home":
        return redirect("home")
    if profile.landing == "dashboard":
        return redirect("dashboard:dashboard")
    if profile.landing == "inbox" and user_can_edit(request.user):
        return redirect("inbox:inbox")
    if not user_can_edit(request.user):
        return redirect("dashboard:dashboard")
    return redirect("home")


@login_required
@csrf_protect
def welcome(request):
    """One-question welcome survey, shown once (drives the setup emphasis)."""
    profile = UserProfile.get_for(request.user)

    if request.method == "POST":
        goal = "" if "skip" in request.POST else request.POST.get("goal", "")
        valid = {c[0] for c in UserProfile.GOAL_CHOICES}
        profile.onboarding_goal = goal if goal in valid else ""
        profile.has_seen_welcome = True
        profile.save(update_fields=["onboarding_goal", "has_seen_welcome"])
        if profile.onboarding_goal == UserProfile.GOAL_REVIEW:
            return redirect("dashboard:dashboard")
        return redirect("home")

    if profile.has_seen_welcome:
        return redirect("home")
    return render(request, "accounts/welcome.html", {
        "goal_choices": UserProfile.GOAL_CHOICES,
    })


@login_required
@require_POST
def dismiss_hint(request):
    """Persist that the user closed a just-in-time hint, then return them back."""
    key = request.POST.get("key", "").strip()[:50]
    if key:
        profile = UserProfile.get_for(request.user)
        if key not in profile.dismissed_hints:
            profile.dismissed_hints = list(profile.dismissed_hints) + [key]
            profile.save(update_fields=["dismissed_hints"])

    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(
        nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return redirect(nxt)
    return redirect("home")


@csrf_protect
def logout_view(request):
    """Logout via POST only to ensure CSRF coverage."""
    if request.method != "POST":
        return HttpResponseForbidden("Logout must be a POST request.")
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def settings_view(request):
    """The account settings hub: name, contact, notifications, email, password."""
    profile = UserProfile.get_for(request.user)
    return render(request, "accounts/settings.html", {
        "name_form": AccountNameForm(instance=request.user),
        "contact_form": ContactForm(instance=profile),
        "notif_form": NotificationsForm(instance=profile),
        "pref_form": PreferencesForm(instance=profile),
        "email_form": ChangeEmailForm(user=request.user),
        "pending_email": request.user.pending_email,
    })


@login_required
@require_POST
def account_update(request):
    """Save the display name."""
    form = AccountNameForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Your name was updated.")
    else:
        messages.error(request, "Please fix the errors and try again.")
    return redirect("accounts:settings")


@login_required
@require_POST
def contact_update(request):
    """Save contact info."""
    form = ContactForm(request.POST, instance=UserProfile.get_for(request.user))
    if form.is_valid():
        form.save()
        messages.success(request, "Contact info saved.")
    else:
        messages.error(request, "Please fix the errors and try again.")
    return redirect("accounts:settings")


@login_required
@require_POST
def notifications_update(request):
    """Save notification preferences."""
    form = NotificationsForm(request.POST, instance=UserProfile.get_for(request.user))
    if form.is_valid():
        form.save()
        messages.success(request, "Notification preferences saved.")
    return redirect("accounts:settings")


@login_required
@require_POST
def preferences_update(request):
    """Save display preferences (timezone, default landing page)."""
    form = PreferencesForm(request.POST, instance=UserProfile.get_for(request.user))
    if form.is_valid():
        form.save()
        messages.success(request, "Preferences saved.")
    else:
        messages.error(request, "Please fix the errors and try again.")
    return redirect("accounts:settings")


@login_required
@require_POST
def change_email(request):
    """Start an email change: stash the new address and email it a confirm link.

    The current email is left untouched until the link is clicked (verify-then-
    commit), so a mistyped address can never lock the account. Requires the
    current password.
    """
    form = ChangeEmailForm(request.POST, user=request.user)
    if form.is_valid():
        request.user.pending_email = form.cleaned_data["new_email"]
        request.user.save(update_fields=["pending_email"])
        confirm_url = UserService.build_change_email_link(request, request.user)
        UserService.send_change_email(
            user=request.user,
            pending_email=request.user.pending_email,
            confirm_url=confirm_url,
        )
        messages.success(request, "Almost there — click the link we sent to your new address to confirm.")
    else:
        for field_errors in form.errors.values():
            messages.error(request, field_errors[0])
    return redirect("accounts:settings")


@login_required
def change_email_confirm(request, uidb64: str, token: str):
    """Commit a pending email change once the new-address link is clicked."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    # Must be the signed-in user, with a matching token and a pending change.
    if (
        user is None
        or user.pk != request.user.pk
        or not user.pending_email
        or not default_token_generator.check_token(user, token)
    ):
        messages.error(request, "That confirmation link is invalid or has expired.")
        return redirect("accounts:settings")

    new_email = user.pending_email
    # The target may have been registered since the request — re-check.
    if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
        user.pending_email = None
        user.save(update_fields=["pending_email"])
        messages.error(request, "That email was just taken by another account.")
        return redirect("accounts:settings")

    try:
        user.email = new_email
        user.pending_email = None
        user.save(update_fields=["email", "pending_email"])
        messages.success(request, "Your email address was updated.")
    except IntegrityError:
        messages.error(request, "That email is already in use.")
    return redirect("accounts:settings")
