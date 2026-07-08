"""Apply a built-in curriculum blueprint to a Curriculum.

Examples:
    # Apply to an existing curriculum by id
    python manage.py apply_blueprint dimensions_math_3a --curriculum 5

    # Create (get-or-create) a curriculum for a user, then apply
    python manage.py apply_blueprint dimensions_math_3a --for-user lopezjronald
"""

from django.core.management.base import BaseCommand, CommandError

from core.utils import get_active_family
from curricula.blueprints import BLUEPRINTS
from curricula.models import Curriculum
from curricula.services import apply_blueprint, get_blueprint


class Command(BaseCommand):
    help = "Apply a built-in curriculum blueprint (chapters/lessons) to a Curriculum."

    def add_arguments(self, parser):
        parser.add_argument("slug", help=f"Blueprint slug. Available: {', '.join(BLUEPRINTS)}")
        parser.add_argument("--curriculum", type=int, help="Existing Curriculum id to populate.")
        parser.add_argument(
            "--for-user",
            help="Username to own a get-or-created curriculum named after the blueprint.",
        )

    def handle(self, *args, **options):
        blueprint = get_blueprint(options["slug"])
        if blueprint is None:
            raise CommandError(
                f"Unknown blueprint '{options['slug']}'. Available: {', '.join(BLUEPRINTS)}"
            )

        curriculum = self._resolve_curriculum(blueprint, options)
        chapters, lessons = apply_blueprint(curriculum, blueprint)
        self.stdout.write(
            self.style.SUCCESS(
                f"Applied '{blueprint['name']}' to curriculum #{curriculum.pk} "
                f"({curriculum.name}): {chapters} chapters, {lessons} lessons."
            )
        )

    def _resolve_curriculum(self, blueprint, options):
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
            curriculum, created = Curriculum.objects.get_or_create(
                parent=user,
                name=blueprint["name"],
                defaults={
                    "subject": blueprint["subject"],
                    "grade_level": blueprint["grade_level"],
                    "family": get_active_family(user),
                },
            )
            verb = "Created" if created else "Using existing"
            self.stdout.write(f"{verb} curriculum #{curriculum.pk} for {user.username}.")
            return curriculum

        raise CommandError("Provide either --curriculum <id> or --for-user <username>.")
