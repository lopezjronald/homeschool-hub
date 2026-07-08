import uuid

from django.conf import settings
from django.db import models


def _new_portal_key():
    return uuid.uuid4().hex


class Student(models.Model):
    """A child profile managed by a parent user."""

    # A child's school Level is their year of school — distinct from a
    # curriculum's academic grade. A child at Level 3 might work a Grade 3
    # math and a Grade 5 reading curriculum. (Field name kept as grade_level
    # for storage/back-compat; it represents the child's Level.)
    LEVEL_CHOICES = [
        ("PREK", "Pre-K"),
        ("K", "Kindergarten"),
        ("G01", "Level 1"),
        ("G02", "Level 2"),
        ("G03", "Level 3"),
        ("G04", "Level 4"),
        ("G05", "Level 5"),
        ("G06", "Level 6"),
        ("G07", "Level 7"),
        ("G08", "Level 8"),
        ("G09", "Level 9"),
        ("G10", "Level 10"),
        ("G11", "Level 11"),
        ("G12", "Level 12"),
    ]

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children",
    )
    family = models.ForeignKey(
        "core.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    grade_level = models.CharField(
        max_length=4,
        choices=LEVEL_CHOICES,
        verbose_name="level",
        help_text="The child's year of school (their Level).",
    )
    portal_key = models.CharField(
        max_length=32,
        default=_new_portal_key,
        editable=False,
        help_text="Rotate to revoke this child's existing portal link.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def get_full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
