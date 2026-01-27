from datetime import date

from django.conf import settings
from django.db import models

from curricula.models import Curriculum
from students.models import Student


class Assignment(models.Model):
    """An assignment linking a child to a curriculum entry."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (NOT_STARTED, "Not Started"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
    ]

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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
        default=NOT_STARTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "title"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Return True if due_date is in the past and status is not COMPLETED."""
        return self.due_date < date.today() and self.status != self.COMPLETED
