"""Print a child's tokenless portal link (for handing to a kid or bookmarking).

Examples:
    python manage.py portal_link --for-user ronald
    python manage.py portal_link --for-user ronald --child-name Kaylin \
        --base-url https://steadfast-scholars-13d0d5cf8a5a.herokuapp.com
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from portal.tokens import make_portal_token
from students.models import Student


class Command(BaseCommand):
    help = "Print the signed portal link(s) for a user's children."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True, help="Parent username.")
        parser.add_argument("--child-name", help="Only this child (default: all their children).")
        parser.add_argument(
            "--base-url", default="",
            help="Absolute base URL (e.g. https://…herokuapp.com). Omit for a relative path.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        children = Student.objects.filter(parent=user)
        if options.get("child_name"):
            children = children.filter(first_name__iexact=options["child_name"])
        if not children.exists():
            raise CommandError("No matching children found.")

        base = options["base_url"].rstrip("/")
        for child in children:
            path = reverse("portal:portal_home", kwargs={"token": make_portal_token(child)})
            self.stdout.write(f"{child.get_full_name()} ({child.get_grade_level_display()}):")
            self.stdout.write(self.style.SUCCESS(f"  {base}{path}"))
