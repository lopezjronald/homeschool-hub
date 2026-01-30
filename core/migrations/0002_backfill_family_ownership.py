"""Backfill Family and FamilyMembership for existing parent-owned data.

Idempotent: safe to run multiple times. Skips rows where family is already set.
"""

from django.db import migrations

from core.utils import backfill_families


def reverse_backfill(apps, schema_editor):
    """Reverse: clear family FKs (does NOT delete Family/Membership rows)."""
    Student = apps.get_model("students", "Student")
    Curriculum = apps.get_model("curricula", "Curriculum")
    Assignment = apps.get_model("assignments", "Assignment")

    Student.objects.filter(family__isnull=False).update(family=None)
    Curriculum.objects.filter(family__isnull=False).update(family=None)
    Assignment.objects.filter(family__isnull=False).update(family=None)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("students", "0002_student_family"),
        ("curricula", "0002_curriculum_family"),
        ("assignments", "0004_assignment_family"),
        ("accounts", "0002_alter_customuser_managers_alter_customuser_email"),
    ]

    operations = [
        migrations.RunPython(backfill_families, reverse_backfill),
    ]
