# One-time backfill: the four live mission courses get a default pace of
# 3 missions/week so the family calendar projects due dates the day it ships.
# Only touches placements whose pace is still NULL — a parent-set value (or a
# deliberate "off") is never overwritten, and reversing is a no-op.

from django.db import migrations

MISSION_COURSE_PREFIXES = [
    "Social Studies 3",
    "World History 7",
    "Science 3",
    "Science 7",
]


def set_default_pace(apps, schema_editor):
    CurriculumPlacement = apps.get_model("curricula", "CurriculumPlacement")
    for prefix in MISSION_COURSE_PREFIXES:
        CurriculumPlacement.objects.filter(
            curriculum__name__startswith=prefix, weekly_pace__isnull=True,
        ).update(weekly_pace=3)


class Migration(migrations.Migration):

    dependencies = [
        ("curricula", "0010_curriculumplacement_weekly_pace"),
    ]

    operations = [
        migrations.RunPython(set_default_pace, migrations.RunPython.noop),
    ]
