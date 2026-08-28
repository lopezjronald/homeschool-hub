"""Re-seed the Fact Dash levels (HH-203).

The data migration does this on deploy; this command exists for when the fact
lists CHANGE, since a migration that has already run will not run again.
Idempotent — it updates in place and never touches a child's progress.
"""

from django.core.management.base import BaseCommand

from factfluency.seed import seed


class Command(BaseCommand):
    help = "Create or update the Fact Dash facts and levels."

    def handle(self, *args, **options):
        facts, levels = seed()
        self.stdout.write(self.style.SUCCESS(
            "%d facts across %d levels." % (facts, levels)))
