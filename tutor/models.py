from django.conf import settings
from django.db import models

from . import mastery


class MasteryAssessment(models.Model):
    """An AI-assisted, parent-finalized mastery assessment of a work log entry.

    The AI proposes a level + feedback; the parent may override before
    finalizing. The AI never finalizes on its own.
    """

    DRAFT = "draft"
    FINALIZED = "finalized"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (FINALIZED, "Finalized"),
    ]

    work_entry = models.ForeignKey(
        "worklog.WorkLogEntry",
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    lesson = models.ForeignKey(
        "curricula.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessments",
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mastery_assessments",
    )

    rubric = models.TextField(help_text="The criteria the work is judged against.")
    answers = models.TextField(help_text="The child's work / answers that were assessed.")

    ai_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)
    ai_summary = models.TextField(blank=True)
    ai_criteria = models.JSONField(default=list, blank=True)
    ai_encouragement = models.TextField(blank=True)

    parent_override_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)
    final_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Assessment of {self.work_entry} ({self.get_status_display()})"

    @property
    def effective_level(self):
        """The level that counts: the finalized level, else the AI's proposal."""
        return self.final_level or self.ai_level

    @property
    def meets_bar(self):
        """True if the effective level is Proficient or above."""
        return mastery.meets_bar(self.effective_level)

    @property
    def badge_class(self):
        """Badge class for the effective (final-or-AI) level."""
        return mastery.BADGE.get(self.effective_level, "bg-secondary")

    @property
    def ai_badge_class(self):
        """Badge class for the AI-proposed level."""
        return mastery.BADGE.get(self.ai_level, "bg-secondary")
