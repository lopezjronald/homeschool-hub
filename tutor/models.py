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


class Material(models.Model):
    """A two-layer learning material for a lesson (authored manually, not by AI).

    ``student_content`` is what the child sees (e.g. a comic script);
    ``parent_content`` is a teaching guide for the parent. A material is only
    visible to a student once it is approved.
    """

    SKILL_MANGA = "manga"
    SKILL_COMIC = "comic"
    SKILL_FLASHCARDS = "flashcards"
    SKILL_DRILL = "drill"
    SKILL_CHOICES = [
        (SKILL_MANGA, "Manga"),
        (SKILL_COMIC, "Comic"),
        (SKILL_FLASHCARDS, "Flashcards"),
        (SKILL_DRILL, "Drill"),
    ]

    DRAFT = "draft"
    APPROVED = "approved"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (APPROVED, "Approved"),
    ]

    lesson = models.ForeignKey(
        "curricula.Lesson",
        on_delete=models.CASCADE,
        related_name="materials",
    )
    child = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materials",
    )
    family = models.ForeignKey(
        "core.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materials",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_materials",
    )
    title = models.CharField(max_length=200)
    skill_type = models.CharField(max_length=20, choices=SKILL_CHOICES, default=SKILL_MANGA)
    student_content = models.TextField(help_text="What the child sees (e.g. a comic script).")
    parent_content = models.TextField(blank=True, help_text="Teaching guide for the parent.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_approved(self):
        return self.status == self.APPROVED

    @property
    def visible_to_student(self):
        """A material only reaches the student once approved."""
        return self.is_approved
