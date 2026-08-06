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

KNOWN_WIDGETS = {"grid", "ratiobar", "scislide", "chart", "binary", "triangle"}

# A window big enough to hold the grid lines but not so big the shape is a smudge.
DEFAULT_VIEW = {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6}


# What each widget actually needs to build itself. Without this a typo in a
# config key passes validation and the child gets a blank section — the very
# failure the validator exists to prevent.
WIDGET_KEYS = {
    "grid": ("view",),
    "ratiobar": ("parts",),
    "scislide": ("mantissa", "exponent"),
    "chart": ("data", "kinds"),
    "binary": ("bits",),
    "triangle": ("angle",),
}


def _unplottable(i, config):
    """Points a child is asked to plot that fall outside the grid she is given.

    Caught here because the failure is silent and cruel: she reads "plot (2, 8)",
    finds no row 8 on the paper, and concludes she has misunderstood the lesson.
    The grid clamps to its edges, so the dot would land on 6 and every later
    answer check would then disagree with her for a reason she cannot see.

    Checks BOTH keys: `table` is the list she is asked to plot herself, `points`
    is a list drawn for her. Either one off the grid is the same problem.

    Never raises. audit_content calls this over live rows, and one malformed row
    must not abort the standing sweep.
    """
    if not isinstance(config, dict):
        return [f"block {i}: config is not a mapping"]
    raw_view = config.get("view") or {}
    if not isinstance(raw_view, dict):
        return [f"block {i}: 'view' is not a mapping"]
    view = dict(DEFAULT_VIEW, **raw_view)
    if not all(isinstance(view.get(k), (int, float)) and not isinstance(view.get(k), bool)
               for k in ("xmin", "xmax", "ymin", "ymax")):
        return [f"block {i}: 'view' does not describe a grid"]
    out = []
    for key in ("table", "points"):
        rows = config.get(key)
        if not rows:
            continue
        if not isinstance(rows, (list, tuple)):
            out.append(f"block {i}: {key!r} is not a list of points")
            continue
        for row in rows:
            if (not isinstance(row, (list, tuple)) or len(row) != 2
                    or not all(isinstance(n, (int, float)) and not isinstance(n, bool)
                               for n in row)):
                out.append(f"block {i}: {key!r} has a bad point {row!r}")
                continue
            x, y = row
            if not (view["xmin"] <= x <= view["xmax"]
                    and view["ymin"] <= y <= view["ymax"]):
                out.append(
                    f"block {i}: {key} asks for ({x}, {y}) but the grid only shows "
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
            config = data.get("config") or {}
            if not isinstance(config, dict):
                # Reported, not raised as AttributeError: this function's whole
                # job is to name what is wrong with the content.
                problems.append(f"block {i}: config is not a mapping")
                continue
            for key in WIDGET_KEYS.get(data.get("widget"), ()):
                if config.get(key) is None:
                    problems.append(f"block {i}: {data.get('widget')} needs "
                                    f"config[{key!r}] and it is missing")
            problems += _unplottable(i, config)
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

        # Read what is there BEFORE writing over it. Comparing after the write
        # compares the new data to itself and never reports a change, which
        # quietly defeated the re-approval guard below.
        was = {b.order: (b.kind, b.data)
               for b in LessonBlock.objects.filter(material=material)}
        # `updates` counts too. title and student_intro are rendered at the top of
        # the child's page and parent_content IS the teaching guide — a rewrite of
        # any of them is new words she would otherwise read under an approval he
        # gave to the old ones.
        changed = bool(updates) or len(was) > len(self.BLOCKS)
        for order, (kind, data) in enumerate(self.BLOCKS, start=1):
            if was.get(order) != (kind, data):
                changed = True
            LessonBlock.objects.update_or_create(
                material=material, order=order,
                defaults={"kind": kind, "data": data},
            )
        # A revised lesson may be shorter than the one it replaces.
        LessonBlock.objects.filter(material=material).filter(
            order__gt=len(self.BLOCKS)).delete()

        # Revised content on an APPROVED lesson goes back to DRAFT. A parent
        # approved the words that were there; replacing them — including fixing a
        # mathematical error — is a new thing for him to look at, and the rest of
        # the app enforces that everywhere else.
        if changed and material.status == Material.APPROVED and not created:
            material.status = Material.DRAFT
            material.save(update_fields=["status"])
            self.stdout.write(self.style.WARNING(
                "Content changed — set back to Draft for re-approval."
            ))

        verb = "Created" if created else ("Updated" if updates or changed else "Refreshed")
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
