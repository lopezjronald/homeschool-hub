from django.conf import settings
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


class UserProfile(models.Model):
    """Per-user onboarding state (not authorization — roles stay on FamilyMembership).

    Holds only "have we welcomed / oriented this person" flags: the one-time
    welcome survey, whether they've dismissed the hub setup checklist, and which
    just-in-time hints they've already closed.
    """

    GOAL_CHARTER = "charter"
    GOAL_SIMPLE = "simple"
    GOAL_REVIEW = "review"
    GOAL_CHOICES = [
        (GOAL_CHARTER, "Homeschooling under a charter or state program — records & reports matter"),
        (GOAL_SIMPLE, "Just tracking our days, simply"),
        (GOAL_REVIEW, "I was invited to help or review a family"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile",
    )
    onboarding_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, blank=True)
    has_seen_welcome = models.BooleanField(default=False)
    setup_dismissed = models.BooleanField(default=False)
    dismissed_hints = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile<{self.user}>"

    @classmethod
    def get_for(cls, user):
        """Return (creating if needed) the profile for a signed-in user."""
        profile, _ = cls.objects.get_or_create(user=user)
        return profile
