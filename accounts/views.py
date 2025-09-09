from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect

from .forms import RegisterForm
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


@csrf_protect
def logout_view(request):
    """Logout via POST only to ensure CSRF coverage."""
    if request.method != "POST":
        return HttpResponseForbidden("Logout must be a POST request.")
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")
