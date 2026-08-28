"""Replay every recorded attempt through the CURRENT scheduling rules.

    python manage.py rebuild_fact_states --child Violet --dry-run
    python manage.py rebuild_fact_states --child Violet

Why this exists. `StudentFactState` is derived data: box, streak, mastery and
due date are a fold over the attempts. When the rules that do the folding change,
the stored state is a fossil of the old rules — and a child keeps being punished
by a bug after it is fixed.

Violet was stuck at 13 of 29 because a slow REPEAT inside a round wiped the
streak the first ask had just earned, and because one thoughtful answer zeroed a
streak of two outright. Both are fixed, but her rows still carry the damage. She
earned that progress; this gives it back rather than making her redo it.

Every attempt is replayed in the order it happened, with `now` set to when it
actually happened, so the due dates come out where they belong instead of all
landing today. Idempotent: run it twice and you get the same answer.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from students.models import Student

from factfluency import scheduling
from factfluency.models import Attempt, StudentFactState


class Command(BaseCommand):
    help = "Recompute StudentFactState from the attempt history."

    def add_arguments(self, parser):
        parser.add_argument("--child", help="First name; omit for every child.")
        parser.add_argument("--dry-run", action="store_true",
                            help="Report what would change and write nothing.")

    def handle(self, *args, **options):
        students = Student.objects.all()
        if options["child"]:
            students = students.filter(first_name__iexact=options["child"])
            if not students.exists():
                raise CommandError("No child named %r." % options["child"])

        for student in students:
            attempts = list(
                Attempt.objects
                .filter(session__student=student)
                .select_related("fact", "session")
                .order_by("pk")
            )
            if not attempts:
                continue
            self._rebuild(student, attempts, dry_run=options["dry_run"])

    def _rebuild(self, student, attempts, *, dry_run):
        before = {
            (s.fact_id, s.operation): (s.leitner_box, s.consecutive_fluent,
                                       s.is_mastered)
            for s in StudentFactState.objects.filter(student=student)
        }

        with transaction.atomic():
            # Reset in place rather than deleting: a delete would cascade and
            # take the attempts we are replaying with it.
            StudentFactState.objects.filter(student=student).update(
                leitner_box=1, consecutive_fluent=0, is_mastered=False,
                total_attempts=0, total_correct=0, last_counted_session=None,
                last_response_ms=None,
            )
            states = {}
            for attempt in attempts:
                key = (attempt.fact_id, attempt.operation)
                if key not in states:
                    states[key] = scheduling.ensure_states(
                        student, [(attempt.fact, attempt.operation)])[key]
                scheduling.apply_attempt(
                    states[key],
                    is_correct=attempt.is_correct,
                    response_ms=attempt.response_ms,
                    # As it happened, so the spacing lands where it belongs
                    # rather than stacking every fact onto today.
                    now=attempt.created_at,
                    session_id=attempt.session_id,
                )

            after = {
                (s.fact_id, s.operation): (s.leitner_box, s.consecutive_fluent,
                                           s.is_mastered)
                for s in StudentFactState.objects.filter(student=student)
            }
            gained = sorted(
                k for k, v in after.items()
                if v[2] and not before.get(k, (0, 0, False))[2])
            lost = sorted(
                k for k, v in after.items()
                if not v[2] and before.get(k, (0, 0, False))[2])

            self.stdout.write(
                "%s: %d attempts replayed · mastered %d → %d (+%d, -%d)"
                % (student.first_name, len(attempts),
                   sum(1 for v in before.values() if v[2]),
                   sum(1 for v in after.values() if v[2]),
                   len(gained), len(lost)))
            for key in lost:
                self.stdout.write(self.style.WARNING(
                    "  lost mastery: %s" % (key,)))

            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("  dry run — nothing written"))
