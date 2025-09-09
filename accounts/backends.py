from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameModelBackend:
    """Authenticate with either email or username.

    Email comparison is case-insensitive; username comparison is exact.
    """

    def authenticate(self, request, username: str | None = None, password: str | None = None, **kwargs):
        """Authenticate a user by email or username and password.

        Args:
            request: HttpRequest object.
            username: The username or email provided by the user.
            password: The raw password.
            **kwargs: Additional keyword arguments.

        Returns:
            CustomUser | None: Authenticated user or None.
        """
        if not username or not password:
            return None
        try:
            user = User.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
        except User.DoesNotExist:
            return None
        return user if user.check_password(password) and self.user_can_authenticate(user) else None

    def user_can_authenticate(self, user) -> bool:
        """Return True if the user is active (mirrors Django defaults)."""
        is_active = getattr(user, "is_active", None)
        return bool(is_active or is_active is None)
