from django.conf import settings
from django.db import models


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
