"""Seed the Lopez family's real external activities (idempotent).

School of Rock (guitar + drums) for each girl, and CodaKid (coding) family-wide.
URLs are the providers' login/home pages; edit anytime in the Activities page.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.utils import get_active_family
from students.models import Student

from activities.models import ExternalActivity

SCHOOL_OF_ROCK = "https://my.schoolofrock.com/"
CODAKID = "https://app.codakid.com/login"


class Command(BaseCommand):
    help = "Seed School of Rock (guitar/drums per child) + CodaKid activities. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        family = get_active_family(user)
        children = list(Student.objects.filter(parent=user))
        created = 0

        def ensure(title, provider, url, emoji, cadence, student=None):
            nonlocal created
            _, made = ExternalActivity.objects.get_or_create(
                parent=user, family=family, student=student, title=title, provider=provider,
                defaults={"url": url, "emoji": emoji, "cadence": cadence},
            )
            created += 1 if made else 0

        # School of Rock — guitar + drums for each child, weekly.
        for child in children:
            ensure("Guitar", "School of Rock", SCHOOL_OF_ROCK, "🎸",
                   ExternalActivity.CADENCE_WEEKLY, student=child)
            ensure("Drums", "School of Rock", SCHOOL_OF_ROCK, "🥁",
                   ExternalActivity.CADENCE_WEEKLY, student=child)
        # CodaKid — coding, family-wide, weekly.
        ensure("Coding", "CodaKid", CODAKID, "💻", ExternalActivity.CADENCE_WEEKLY)

        self.stdout.write(self.style.SUCCESS(
            f"Activities seeded ({created} new): School of Rock guitar+drums for "
            f"{len(children)} child(ren) + CodaKid coding."
        ))
