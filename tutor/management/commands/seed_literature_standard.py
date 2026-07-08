"""Tie a literature curriculum to the Socratic method + literary-tools toolbox.

Run this whenever a literature book is added, so it's instantly set up for
literary analysis at the student's grade level. Works two ways:

    # Apply to an existing literature curriculum (level from its grade or a placed child)
    python manage.py seed_literature_standard --curriculum 42

    # Create a literature scaffold for a child and apply the standard
    python manage.py seed_literature_standard --for-user ronald --child-name Violet \
        --name "Blackbird Literature (Grade 3)" --level G03
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Curriculum, CurriculumPlacement
from students.models import Student
from tutor import literature


class Command(BaseCommand):
    help = "Apply the Socratic + literary-tools standard to a literature curriculum (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Existing literature Curriculum id.")
        parser.add_argument("--for-user", help="Username (with --name to create a scaffold).")
        parser.add_argument("--child-name", help="Child to place in a newly-created curriculum.")
        parser.add_argument("--name", help="Curriculum name when creating a scaffold.")
        parser.add_argument("--level", help="Grade level code (e.g. G03). Defaults to the "
                                            "curriculum's grade or the placed child's Level.")

    @transaction.atomic
    def handle(self, *args, **options):
        curriculum, level, family = self._resolve(options)
        if not level:
            raise CommandError(
                "Could not determine a grade level — pass --level (e.g. G03), set the "
                "curriculum's grade_level, or place a child in it."
            )
        sets, questions = literature.apply_literature_standard(curriculum, level, family=family)
        band = literature.socratic.band_for_level(level)
        self.stdout.write(self.style.SUCCESS(
            f"Applied the literature standard to '{curriculum.name}' at level {level} "
            f"(band {band}): {sets} teacher-led sets, {questions} questions "
            f"(Story-Grammar Seminar + Literary Toolbox)."
        ))

    def _resolve(self, options):
        if options.get("curriculum"):
            try:
                curriculum = Curriculum.objects.get(pk=options["curriculum"])
            except Curriculum.DoesNotExist:
                raise CommandError(f"Curriculum #{options['curriculum']} does not exist.")
            level = options.get("level") or curriculum.grade_level or self._level_from_placement(curriculum)
            return curriculum, level, curriculum.family

        if options.get("for_user") and options.get("name"):
            from django.contrib.auth import get_user_model

            user = get_user_model().objects.filter(username=options["for_user"]).first()
            if user is None:
                raise CommandError(f"User '{options['for_user']}' does not exist.")
            level = options.get("level") or "G03"
            family = get_active_family(user)
            curriculum, _ = Curriculum.objects.get_or_create(
                parent=user, name=options["name"],
                defaults={"subject": "Literature", "grade_level": level, "family": family},
            )
            if options.get("child_name"):
                child = Student.objects.filter(
                    parent=user, first_name__iexact=options["child_name"],
                ).first()
                if child is None:
                    raise CommandError(f"No child named '{options['child_name']}' found.")
                anchor = literature.ensure_anchor_lesson(curriculum)
                CurriculumPlacement.objects.get_or_create(
                    child=child, curriculum=curriculum, defaults={"current_lesson": anchor},
                )
            return curriculum, level, family

        raise CommandError("Provide --curriculum <id>, or --for-user + --name (+ --level).")

    def _level_from_placement(self, curriculum):
        placement = curriculum.placements.select_related("child").first()
        return placement.child.grade_level if placement else ""
