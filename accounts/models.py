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
    pending_email = models.EmailField(
        "pending email address",
        blank=True,
        null=True,
        default=None,
        help_text="A new email awaiting verification; committed to `email` once the "
        "owner clicks the confirmation link. Not unique — validated at commit time.",
    )

    objects = CustomerUserManager()

    def __str__(self) -> str:
        """Return the username."""
        return self.username


class UserProfile(models.Model):
    """Per-user profile (not authorization — roles stay on FamilyMembership).

    Holds onboarding state (the one-time welcome survey, setup-checklist dismissal,
    closed hints), optional contact info, and notification preferences plus the
    action-inbox "last seen" marker.
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

    # Contact info (optional) — kept per-user for charter/ES communication.
    phone = models.CharField(max_length=32, blank=True)
    address_line1 = models.CharField("street address", max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=64, blank=True)
    postal_code = models.CharField(max_length=16, blank=True)

    # Notifications + action inbox.
    notify_on_submission = models.BooleanField(
        default=True,
        help_text="Email me when a child submits work that needs my finalization.",
    )
    inbox_seen_at = models.DateTimeField(null=True, blank=True)

    # Preferences.
    TIMEZONE_CHOICES = [
        ("", "Site default"),
        ("America/New_York", "Eastern (New York)"),
        ("America/Chicago", "Central (Chicago)"),
        ("America/Denver", "Mountain (Denver)"),
        ("America/Phoenix", "Arizona (Phoenix)"),
        ("America/Los_Angeles", "Pacific (Los Angeles)"),
        ("America/Anchorage", "Alaska (Anchorage)"),
        ("Pacific/Honolulu", "Hawaii (Honolulu)"),
    ]
    timezone = models.CharField(
        max_length=64, blank=True, choices=TIMEZONE_CHOICES,
        help_text="Show dates and times in this timezone.",
    )
    LANDING_CHOICES = [
        ("", "Smart default (based on your role)"),
        ("home", "Hub"),
        ("dashboard", "Progress"),
        ("inbox", "Action inbox"),
    ]
    landing = models.CharField(
        max_length=20, blank=True, choices=LANDING_CHOICES,
        help_text="Where to go right after you log in.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile<{self.user}>"

    @classmethod
    def get_for(cls, user):
        """Return (creating if needed) the profile for a signed-in user."""
        profile, _ = cls.objects.get_or_create(user=user)
        return profile
