from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class UserService:
    """Service layer for user operations (verification links/emails)."""

    @staticmethod
    def build_verify_link(request, user: User) -> str:
        """Construct a signed verification URL for the given user.

        Args:
            request: The current HttpRequest.
            user: The user to build a verification link for.

        Returns:
            str: Absolute URL the user can click to verify their email.
        """
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return request.build_absolute_uri(
            reverse("accounts:verify", kwargs={"uidb64": uid, "token": token})
        )

    @staticmethod
    def send_verification_email(*, user: User, verify_url: str) -> None:
        """Send the verification email using the configured email backend.

        Args:
            user: The recipient user.
            verify_url: The absolute verification URL to include in the email.
        """
        ctx = {"user": user, "verify_url": verify_url}
        subject = render_to_string("accounts/emails/verify_subject.txt", ctx).strip()
        body = render_to_string("accounts/emails/verify_email.txt", ctx)
        send_mail(subject, body, getattr(settings, "DEFAULT_FROM_EMAIL", None), [user.email])
