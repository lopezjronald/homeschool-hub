"""Shared base for the ``seed_violet_*`` manga-lesson commands.

Each manga lesson is the same command wearing a different script: resolve the
curriculum, find the lesson, upsert one ``Material``. The first few lessons were
written out longhand, which was fine at one or two and is not at seven — so the
machinery lives here and a lesson file carries only its content.

A subclass sets CHAPTER / LESSON_NUMBER / TITLE and the three content blocks.
"""

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from students.models import Student
from tutor.models import Material

CURRICULUM_NAME = "Dimensions Math 3A"


class MangaSeedCommand(BaseCommand):
    """Upsert one manga Material onto a Dimensions Math 3A lesson (idempotent)."""

    CHAPTER = 3
    LESSON_NUMBER = None
    TITLE = ""
    STUDENT_INTRO = ""
    STUDENT_CONTENT = ""
    PARENT_CONTENT = ""

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Curriculum id to attach the manga to.")
        parser.add_argument("--for-user", help=f"Username whose '{CURRICULUM_NAME}' curriculum to use.")
        parser.add_argument("--child-name", default="Violet", help="Child first name to link (optional).")

    def handle(self, *args, **options):
        curriculum = resolve_curriculum(options)
        lesson = (
            Lesson.objects.filter(
                chapter__curriculum=curriculum,
                chapter__number=self.CHAPTER,
                number=self.LESSON_NUMBER,
            )
            .select_related("chapter")
            .first()
        )
        if lesson is None:
            raise CommandError(
                f"Chapter {self.CHAPTER}, Lesson {self.LESSON_NUMBER} not found. Apply the "
                f"{CURRICULUM_NAME} blueprint first (manage.py apply_blueprint "
                f"dimensions_math_3a --curriculum <id>)."
            )

        child = self._resolve_child(curriculum, options.get("child_name"))

        material, created = Material.objects.get_or_create(
            lesson=lesson,
            title=self.TITLE,
            skill_type=Material.SKILL_MANGA,
            defaults={
                "student_intro": self.STUDENT_INTRO,
                "student_content": self.STUDENT_CONTENT,
                "parent_content": self.PARENT_CONTENT,
                "child": child,
                "family": curriculum.family,
                "status": Material.DRAFT,
                # The art reserves an open balloon zone up top, so speech floats
                # over it rather than being boxed underneath.
                "manga_text_layout": Material.LAYOUT_FLOAT,
            },
        )

        updates = []
        if not created:
            for field, value in (
                ("student_intro", self.STUDENT_INTRO),
                ("student_content", self.STUDENT_CONTENT),
                ("parent_content", self.PARENT_CONTENT),
                ("manga_text_layout", Material.LAYOUT_FLOAT),
            ):
                if getattr(material, field) != value:
                    setattr(material, field, value)
                    updates.append(field)
            if child and material.child_id is None:
                material.child = child
                updates.append("child")
            if updates:
                material.save(update_fields=updates)

        verb = "Created" if created else ("Updated" if updates else "Already present")
        self.stdout.write(self.style.SUCCESS(
            f"{verb}: Material #{material.pk} '{material.title}' on {lesson.code} "
            f"(status: {material.get_status_display()})."
        ))

    def _resolve_child(self, curriculum, name):
        if name:
            by_name = Student.objects.filter(first_name__iexact=name)
            if curriculum.family_id:
                child = by_name.filter(family_id=curriculum.family_id).first()
                if child:
                    return child
            child = by_name.filter(parent=curriculum.parent).first()
            if child:
                return child
        placement = curriculum.placements.select_related("child").first()
        return placement.child if placement else None


def resolve_curriculum(options):
    """--curriculum <id> or --for-user <username>; shared by the seed and art commands."""
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
        curriculum = Curriculum.objects.filter(parent=user, name=CURRICULUM_NAME).first()
        if curriculum is None:
            raise CommandError(f"No '{CURRICULUM_NAME}' curriculum found for {user.username}.")
        return curriculum
    raise CommandError("Provide either --curriculum <id> or --for-user <username>.")
