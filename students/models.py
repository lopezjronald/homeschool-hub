from django.conf import settings
from django.db import models


class Student(models.Model):
    """A child profile managed by a parent user."""

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
        related_name="children",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    grade_level = models.CharField(max_length=4, choices=GRADE_CHOICES)
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
