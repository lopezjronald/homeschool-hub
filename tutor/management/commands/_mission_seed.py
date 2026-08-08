"""Shared machinery for the self-directed "mission" courses (Social Studies, Science).

A mission course = a blueprint (Units → Missions) + one APPROVED Material per
mission built from LessonBlock rows. NO QuestionSet and NO AI — a mission is
completed by a LessonProgress "done" mark (parent's weekly review, or a kid
"finished" action), which advances the lesson and lights the streak/hours report
with zero API cost. Callers: seed_sci_violet, seed_sci_kaylin (and the same shape
as seed_ss_violet / seed_ss_kaylin).
"""
from django.core.management.base import CommandError
from django.utils import timezone

from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint
from students.models import Student
from tutor.models import LessonBlock, Material

from ._saxon_seed import validate_blocks


def resolve_child(name):
    child = Student.objects.filter(first_name__iexact=name).order_by("pk").first()
    if child is None:
        raise CommandError(f"No student named {name!r} found.")
    return child


def setup_course(child, blueprint):
    """Ensure the Curriculum exists, apply the blueprint (Units → Missions), and
    place the child on it. Idempotent. Returns the Curriculum."""
    curriculum, _ = Curriculum.objects.get_or_create(
        parent=child.parent,
        name=blueprint["name"],
        defaults={
            "family": child.family,
            "subject": blueprint["subject"],
            "grade_level": blueprint["grade_level"],
        },
    )
    apply_blueprint(curriculum, blueprint)
    CurriculumPlacement.objects.get_or_create(
        child=child, curriculum=curriculum, defaults={"is_active": True})
    return curriculum


def upsert_mission(curriculum, child, number, *, title, intro, parent_content, blocks):
    """Upsert one APPROVED Material (validated LessonBlocks) for the mission lesson
    identified by its global ``number``. Idempotent — rewrites blocks in order and
    trims any that a shortened mission dropped."""
    validate_blocks(blocks)
    lesson = Lesson.objects.filter(
        chapter__curriculum=curriculum, number=number).first()
    if lesson is None:
        raise CommandError(f"Mission {number} lesson not found — blueprint not applied?")
    material, created = Material.objects.get_or_create(
        lesson=lesson, skill_type=Material.SKILL_LESSON,
        defaults={
            "title": title, "student_intro": intro, "student_content": intro,
            "parent_content": parent_content, "child": child,
            "family": curriculum.family,
            "status": Material.APPROVED, "approved_at": timezone.now(),
        },
    )
    if not created:
        material.title = title
        material.parent_content = parent_content
        material.child = material.child or child
        if material.status != Material.APPROVED:
            material.status = Material.APPROVED
            material.approved_at = timezone.now()
        material.save()
    for order, (kind, data) in enumerate(blocks, start=1):
        LessonBlock.objects.update_or_create(
            material=material, order=order, defaults={"kind": kind, "data": data})
    LessonBlock.objects.filter(material=material, order__gt=len(blocks)).delete()
    return material
