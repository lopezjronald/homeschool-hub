"""Curriculum services: applying built-in blueprints to a Curriculum."""

from .blueprints import BLUEPRINTS
from .models import Chapter, Lesson


def get_blueprint(slug):
    """Return the blueprint dict for a slug, or None."""
    return BLUEPRINTS.get(slug)


def apply_blueprint(curriculum, blueprint):
    """Populate a curriculum's chapters/lessons from a blueprint (idempotent).

    Re-running updates titles/objectives in place (keyed on chapter number and
    lesson order), so it is safe to run repeatedly. Returns (chapters, lessons)
    counts touched.
    """
    chapters = 0
    lessons = 0
    for ch in blueprint["chapters"]:
        chapter, _ = Chapter.objects.update_or_create(
            curriculum=curriculum,
            number=ch["number"],
            defaults={"title": ch["title"]},
        )
        chapters += 1
        for lsn in ch["lessons"]:
            Lesson.objects.update_or_create(
                chapter=chapter,
                order=lsn["order"],
                defaults={
                    "number": lsn["number"],
                    "title": lsn["title"],
                    "lesson_type": lsn["type"],
                    "objectives": lsn["objectives"],
                },
            )
            lessons += 1
    return chapters, lessons
