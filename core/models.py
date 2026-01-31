import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    """A charter school, state program, co-op, or other oversight body."""

    ORG_TYPE_CHOICES = [
        ("charter", "Charter School"),
        ("state_program", "State Program"),
        ("co_op", "Co-op"),
        ("private", "Private"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=200)
    org_type = models.CharField(max_length=20, choices=ORG_TYPE_CHOICES)
    requires_teacher_oversight = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_org_type_display()})"


class Family(models.Model):
    """A household unit that groups parents, teachers, and students."""

    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="families",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "families"

    def __str__(self):
        return self.name


class FamilyMembership(models.Model):
    """Links a user to a family with a specific role."""

    ROLE_CHOICES = [
        ("parent", "Parent"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_memberships",
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "family"],
                name="unique_user_family",
            ),
        ]
        ordering = ["family", "role"]

    def __str__(self):
        return f"{self.user} - {self.family} ({self.get_role_display()})"


class Invitation(models.Model):
    """An email invitation to join a Family with a given role."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (EXPIRED, "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    role = models.CharField(max_length=20, default="teacher")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "family"],
                condition=models.Q(status="pending"),
                name="unique_pending_invite_per_email_family",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite {self.email} → {self.family} ({self.status})"

    @property
    def is_expired(self):
        max_age = getattr(settings, "INVITE_MAX_AGE_DAYS", 7)
        return timezone.now() > self.created_at + timedelta(days=max_age)
