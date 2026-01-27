from django.conf import settings
from django.db import models


class Curriculum(models.Model):
    """A curriculum/subject that a parent teaches."""

    # Grade choices matching students.Student.GRADE_CHOICES
    GRADE_CHOICES = [
        ("PREK", "Pre-K"),
        ("K", "Kindergarten"),
        ("G01", "1st Grade"),
        ("G02", "2nd Grade"),
        ("G03", "3rd Grade"),
        ("G04", "4th Grade"),
        ("G05", "5th Grade"),
        ("G06", "6th Grade"),
        ("G07", "7th Grade"),
        ("G08", "8th Grade"),
        ("G09", "9th Grade"),
        ("G10", "10th Grade"),
        ("G11", "11th Grade"),
        ("G12", "12th Grade"),
    ]

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="curricula",
    )
    name = models.CharField(
        max_length=200,
        help_text="e.g., 'Singapore Math 5A' or 'American History'",
    )
    subject = models.CharField(
        max_length=100,
        help_text="e.g., 'Math', 'Science', 'Reading'",
    )
    grade_level = models.CharField(
        max_length=4,
        choices=GRADE_CHOICES,
        blank=True,
        help_text="Optional grade level for this curriculum",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["subject", "name"]
        verbose_name_plural = "curricula"

    def __str__(self):
        return self.name

    def get_related_assignments_count(self):
        """Return count of related assignments, or 0 if Assignment model doesn't exist yet."""
        # Placeholder for HH-26: when Assignment model exists with FK to Curriculum,
        # this will return the count. For now, safely return 0.
        if hasattr(self, "assignments"):
            return self.assignments.count()
        return 0
