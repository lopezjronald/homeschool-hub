from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomerUserManager


class CustomUser(AbstractUser):
    """Project user model based on Django's ``AbstractUser``.

    Attributes:
        email: Unique, indexed email address for email-based auth.
        role: Simple role tag (``parent`` | ``student`` | ``admin``).
    """

    ROLE_CHOICES = [
        ("parent", "Parent"),
        ("student", "Student"),
        ("admin", "Admin"),
    ]

    email = models.EmailField("email address", unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="parent")

    objects = CustomerUserManager()

    def __str__(self) -> str:
        """Return string representation as ``username (role)``."""
        return f"{self.username} ({self.role})"
