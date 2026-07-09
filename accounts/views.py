from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from core.permissions import user_can_edit

from .forms import RegisterForm
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
