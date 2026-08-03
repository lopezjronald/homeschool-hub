"""Shared base for seeding a Saxon Pre-Algebra lesson.

One lesson is: a Material carrying the taught explainer as LessonBlock rows, plus
a parent teaching guide in ``parent_content``. Idempotent — re-running updates in
place rather than duplicating, so a lesson can be revised and re-seeded freely.

Block payloads are VALIDATED here, against the kinds the template actually
renders. An unknown kind would otherwise fall through every branch of
``_lesson_blocks.html`` and render as nothing at all — a blank space on a child's
screen with no error anywhere. That failure mode has happened once in this
codebase already, so it fails loudly at seed time instead.
"""

import json

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.models import LessonBlock, Material

CURRICULUM_NAME = "Saxon Pre-Algebra (DIVE)"

# kind -> keys that must be present. Checked at seed time so a typo cannot ship a
# blank section to a child.
REQUIRED_KEYS = {
    LessonBlock.KIND_MASTHEAD: ("title",),
    LessonBlock.KIND_PURPOSE: ("title", "paragraphs"),
    LessonBlock.KIND_IDEA: ("n", "of", "title", "paragraphs"),
    LessonBlock.KIND_SAY: ("text",),
    LessonBlock.KIND_STEPS: ("title", "steps"),
    LessonBlock.KIND_WORKED: ("number", "question", "steps"),
    LessonBlock.KIND_STEPPER: ("title", "steps"),
    LessonBlock.KIND_TRANSLATION: ("title", "rows"),
    LessonBlock.KIND_ERRORS: ("items",),
    LessonBlock.KIND_TABLE: ("rows",),
    LessonBlock.KIND_MATH: ("display",),
    LessonBlock.KIND_REVEAL: ("prompt", "answer"),
    LessonBlock.KIND_TOOL: ("widget", "config"),
    LessonBlock.KIND_RECAP: ("items",),
}

KNOWN_WIDGETS = {"grid", "ratiobar", "scislide"}

# A window big enough to hold the grid lines but not so big the shape is a smudge.
DEFAULT_VIEW = {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6}


def _unplottable(i, config):
    """Points a child is asked to plot that fall outside the grid she is given.

    Caught here because the failure is silent and cruel: she reads "plot (2, 8)",
    finds no row 8 on the paper, and concludes she has misunderstood the lesson.
    The grid clamps to its edges, so the dot would land on 6 and every later
    answer check would then disagree with her for a reason she cannot see.
    """
    table = config.get("table")
    if not table:
        return []
    view = dict(DEFAULT_VIEW, **(config.get("view") or {}))
    out = []
    for x, y in table:
        if not (view["xmin"] <= x <= view["xmax"] and view["ymin"] <= y <= view["ymax"]):
            out.append(
                f"block {i}: the table asks for ({x}, {y}) but the grid only shows "
                f"x {view['xmin']}..{view['xmax']}, y {view['ymin']}..{view['ymax']}"
            )
    return out


def validate_blocks(blocks):
    """Raise CommandError on anything the template could not render."""
    problems = []
    for i, (kind, data) in enumerate(blocks, start=1):
        if kind not in REQUIRED_KEYS:
            problems.append(f"block {i}: unknown kind {kind!r}")
            continue
        for key in REQUIRED_KEYS[kind]:
            if key not in data or data[key] in (None, "", [], {}):
                problems.append(f"block {i} ({kind}): missing {key!r}")
        if kind == LessonBlock.KIND_TOOL and data.get("widget") not in KNOWN_WIDGETS:
            problems.append(f"block {i}: no such widget {data.get('widget')!r}")
        if kind == LessonBlock.KIND_TOOL:
            # The config crosses into JS through json_script, so it has to be
            # JSON-serialisable here rather than failing at render time.
            try:
                json.dumps(data.get("config"))
            except (TypeError, ValueError) as exc:
                problems.append(f"block {i}: config is not JSON ({exc})")
            problems += _unplottable(i, data.get("config") or {})
    if problems:
        raise CommandError("Lesson blocks are not renderable:\n  " + "\n  ".join(problems))


class SaxonSeedCommand(BaseCommand):
    """Upsert one Saxon lesson's Material and its blocks."""

    LESSON_NUMBER = None        # the printed Saxon number
    TITLE = ""
    STUDENT_INTRO = ""
    PARENT_CONTENT = ""
    BLOCKS = []                 # [(kind, data), ...]

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int,
                            help="Curriculum id to attach the lesson to.")
        parser.add_argument("--for-user",
                            help=f"Username whose '{CURRICULUM_NAME}' curriculum to use.")
        parser.add_argument("--child-name", default="Kaylin",
                            help="Child first name to link the material to.")

    def handle(self, *args, **options):
        validate_blocks(self.BLOCKS)
        curriculum = resolve_curriculum(options)
        lesson = Lesson.objects.filter(
            chapter__curriculum=curriculum, number=self.LESSON_NUMBER,
        ).select_related("chapter").first()
        if lesson is None:
            raise CommandError(
                f"Lesson {self.LESSON_NUMBER} not found in curriculum #{curriculum.pk}. "
                f"Apply the blueprint first: manage.py apply_blueprint "
                f"saxon_prealgebra_dive --curriculum {curriculum.pk}"
            )

        child = resolve_child(curriculum, options.get("child_name"))
        material, created = Material.objects.get_or_create(
            lesson=lesson,
            skill_type=Material.SKILL_LESSON,
            defaults={
                "title": self.TITLE,
                "student_intro": self.STUDENT_INTRO,
                # Blocks are the body; student_content is the plain-text fallback
                # that renders only when a material has no blocks.
                "student_content": self.STUDENT_INTRO,
                "parent_content": self.PARENT_CONTENT,
                "child": child,
                "family": curriculum.family,
                "status": Material.DRAFT,
            },
        )

        updates = []
        if not created:
            for field, value in (
                ("title", self.TITLE),
                ("student_intro", self.STUDENT_INTRO),
                ("parent_content", self.PARENT_CONTENT),
            ):
                if getattr(material, field) != value:
                    setattr(material, field, value)
                    updates.append(field)
            if child and material.child_id is None:
                material.child = child
                updates.append("child")
            if updates:
                material.save(update_fields=updates)

        for order, (kind, data) in enumerate(self.BLOCKS, start=1):
            LessonBlock.objects.update_or_create(
                material=material, order=order,
                defaults={"kind": kind, "data": data},
            )
        # A revised lesson may be shorter than the one it replaces.
        LessonBlock.objects.filter(material=material).filter(
            order__gt=len(self.BLOCKS)).delete()

        verb = "Created" if created else ("Updated" if updates else "Refreshed")
        self.stdout.write(self.style.SUCCESS(
            f"{verb}: {lesson.code} '{material.title}' — {len(self.BLOCKS)} blocks "
            f"({material.get_status_display()})."
        ))


def resolve_curriculum(options):
    """--curriculum <id>, or the named curriculum belonging to --for-user."""
    if options.get("curriculum"):
        try:
            return Curriculum.objects.get(pk=options["curriculum"])
        except Curriculum.DoesNotExist:
            raise CommandError(f"Curriculum #{options['curriculum']} does not exist.")
    if options.get("for_user"):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")
        curriculum = Curriculum.objects.filter(parent=user).filter(
            name__icontains="Saxon").first()
        if curriculum is None:
            raise CommandError(f"No Saxon curriculum found for {user.username}.")
        return curriculum
    raise CommandError("Provide either --curriculum <id> or --for-user <username>.")


def resolve_child(curriculum, name):
    if name:
        by_name = Student.objects.filter(first_name__iexact=name)
        if curriculum.family_id:
            child = by_name.filter(family_id=curriculum.family_id).first()
            if child:
                return child
        child = by_name.filter(parent=curriculum.parent).first()
        if child:
            return child
    placement = CurriculumPlacement.objects.filter(
        curriculum=curriculum).select_related("child").first()
    return placement.child if placement else None
