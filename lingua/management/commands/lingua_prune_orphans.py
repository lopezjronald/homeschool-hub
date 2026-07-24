"""Delete lingua Learners whose host Student no longer exists (orphans).

The backstop for the inline purge in the host's student-delete path (D-03): with
no FK from lingua to the host, deleting a Student can't cascade into lingua, so
the host calls ``lingua.services.delete_learner_for_student`` inline — and this
command sweeps up anything that inline call missed (a crash, a deletion done
outside the view, a bulk delete). Idempotent; safe to run on Heroku Scheduler.
"""
from django.core.management.base import BaseCommand

from lingua.integrations import directory
from lingua.models import Learner


class Command(BaseCommand):
    help = "Delete lingua Learners whose host Student no longer exists (orphans)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be deleted without deleting anything.",
        )

    def handle(self, *args, **options):
        learners = list(Learner.objects.values_list("pk", "host_student_id"))
        if not learners:
            self.stdout.write("No learners.")
            return
        existing = directory.existing_student_ids(hsid for _, hsid in learners)
        orphan_pks = [pk for pk, hsid in learners if hsid not in existing]
        if not orphan_pks:
            self.stdout.write("No orphaned learners.")
            return
        if options["dry_run"]:
            self.stdout.write(
                f"[dry-run] would delete {len(orphan_pks)} orphaned learner(s)."
            )
            return
        deleted, _ = Learner.objects.filter(pk__in=orphan_pks).delete()
        self.stdout.write(
            f"Deleted {deleted} row(s) for {len(orphan_pks)} orphaned learner(s)."
        )
