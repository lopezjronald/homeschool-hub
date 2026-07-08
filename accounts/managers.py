from django.contrib.auth.models import UserManager


class CustomerUserManager(UserManager):
    """Custom manager for ``CustomUser`` with email normalization.

    Inherits from Django's :class:`UserManager` and overrides ``_create_user``
    to normalize emails.
    """

    def _create_user(self, username: str, email: str | None, password: str | None, **extra_fields):
        """Create and save a user with the given username, email, and password.

        Args:
            username: Username value (kept for AbstractUser compatibility).
            email: Email address; will be normalized and lowercased.
            password: Raw password.
            **extra_fields: Additional model fields (e.g., role, is_staff).

        Returns:
            CustomUser: The created user.
        """
        email = (self.normalize_email(email) or "").strip().lower()
        return super()._create_user(username, email, password, **extra_fields)
