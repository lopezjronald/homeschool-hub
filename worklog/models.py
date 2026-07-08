import os

from django.conf import settings
from django.db import models
from django.utils import timezone


class WorkLogEntry(models.Model):
    """A record of work a child completed on a given day.

    The Work Log is the product spine: a simple, no-AI record a parent hands to
    the charter Educational Specialist, and the source the AI grader/recommender
    read from later. Family-scoped through the same permissions layer as the
    rest of the app.
    """

    IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic")

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_log_entries",
    )
    family = models.ForeignKey(
        "core.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_log_entries",
    )
    child = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="work_log_entries",
    )
    curriculum = models.ForeignKey(
        "curricula.Curriculum",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_log_entries",
        help_text="Optional: link this work to a curriculum.",
    )
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_log_entries",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_work_log_entries",
    )
    date = models.DateField(
        default=timezone.localdate,
        help_text="The day this work was done.",
    )
    subject = models.CharField(
        max_length=100,
        help_text="e.g., 'Math', 'Reading', 'Nature walk'.",
    )
    description = models.TextField(
        blank=True,
        help_text="What did they do? What did you observe?",
    )
    attachment = models.FileField(
        upload_to="work_log/%Y/%m/",
        blank=True,
        help_text="Optional photo or file of the work.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "work log entry"
        verbose_name_plural = "work log entries"

    def __str__(self):
        return f"{self.child} — {self.subject} ({self.date})"

    @property
    def is_image(self):
        """True if the attachment looks like a displayable image."""
        if not self.attachment:
            return False
        ext = os.path.splitext(self.attachment.name)[1].lower()
        return ext in self.IMAGE_EXTENSIONS

    @property
    def attachment_filename(self):
        """Bare filename of the attachment, for display/download links."""
        if not self.attachment:
            return ""
        return os.path.basename(self.attachment.name)
