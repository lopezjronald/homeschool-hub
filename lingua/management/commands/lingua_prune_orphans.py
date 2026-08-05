"""Delete lingua Learners whose host Student no longer exists (orphans).

The backstop for the inline purge in the host's student-delete path (D-03): with
no FK from lingua to the host, deleting a Student can't cascade into lingua, so
the host calls ``lingua.services.delete_learner_for_student`` inline — and this
command sweeps up anything that inline call missed (a crash, a deletion done
outside the view, a bulk delete). Idempotent; safe to run on Heroku Scheduler.
"""
from django.core.management.base import BaseCommand

from lingua import services
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
        # STUDENT-BACKED learners only. An adult learner (LGA-103) has
        # host_student_id NULL, and `None not in existing_student_ids` is always
        # true — so without this filter every scheduled run would classify the
        # parent's own learner as an orphan and delete it, cascading his entire
        # history. This command runs unattended on Heroku Scheduler, so that would
        # have happened quietly, overnight, once.
        learners = list(
            Learner.objects.filter(host_student_id__isnull=False)
            .values_list("pk", "host_student_id")
        )
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
        orphan_hsids = [hsid for _, hsid in learners if hsid not in existing]
        deleted, _ = Learner.objects.filter(pk__in=orphan_pks).delete()
        # Sweep the other model that carries a bare host_student_id (D-03): a packet
        # for a deleted child is private homework nothing will ever clean up. Shared
        # (NULL host_student_id) packets are excluded inside purge_tutor_packets.
        packets, stranded = services.purge_tutor_packets(orphan_hsids)
        self.stdout.write(
            f"Deleted {deleted} row(s) for {len(orphan_pks)} orphaned learner(s)"
            f"{f' and {packets} orphaned tutor packet row(s)' if packets else ''}."
        )
        if stranded:
            # Say it loudly: the rows are gone, so nothing points at these objects
            # any more and no later run can find them. A recurring count means the
            # storage credentials cannot delete, not that one key was missing.
            self.stderr.write(self.style.ERROR(
                f"{stranded} uploaded file(s) could NOT be removed from storage and "
                f"are now unreferenced. Check the storage credentials' delete "
                f"permission, then remove them by hand."
            ))
