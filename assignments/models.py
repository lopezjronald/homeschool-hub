from datetime import date

from django.conf import settings
from django.core import signing
from django.db import models
from django.urls import reverse

from curricula.models import Curriculum
from students.models import Student


class Assignment(models.Model):
    """An assignment linking a child to a curriculum entry."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETE = "complete"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (IN_PROGRESS, "In Progress"),
        (SUBMITTED, "Submitted"),
        (COMPLETE, "Complete"),
    ]

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    family = models.ForeignKey(
        "core.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )
    child = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "title"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Return True if due_date is in the past and status is not complete."""
        return self.due_date < date.today() and self.status != self.COMPLETE

    def get_student_status_token(self):
        """Generate a signed token for student status updates (7 day expiry)."""
        return signing.dumps({"assignment_id": self.pk}, salt="student-status-update")

    def get_student_status_url(self):
        """Return the relative URL for student status updates."""
        token = self.get_student_status_token()
        return reverse("assignments:assignment_student_update", args=[token])

    @classmethod
    def get_from_student_token(cls, token, max_age=7 * 24 * 60 * 60):
        """
        Retrieve an assignment from a signed student token.
        Returns None if token is invalid or expired.
        max_age: 7 days in seconds (default)
        """
        try:
            data = signing.loads(token, salt="student-status-update", max_age=max_age)
            return cls.objects.get(pk=data["assignment_id"])
        except (signing.BadSignature, signing.SignatureExpired, cls.DoesNotExist):
            return None


class AssignmentResourceLink(models.Model):
    """An external resource link attached to an assignment."""

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="resource_links",
    )
    url = models.URLField()
    label = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.label or self.url

    @property
    def display_label(self):
        """Return label if set, otherwise the URL."""
        return self.label if self.label else self.url
