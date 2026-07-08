from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomerUserManager


class CustomUser(AbstractUser):
    """Project user model based on Django's ``AbstractUser``.

    Roles are not stored here — a user's role is defined per family via
    ``core.FamilyMembership.role`` (the sole source of truth for authorization).

    Attributes:
        email: Unique, indexed email address for email-based auth.
    """

    email = models.EmailField("email address", unique=True, db_index=True)

    objects = CustomerUserManager()

    def __str__(self) -> str:
        """Return the username."""
        return self.username
