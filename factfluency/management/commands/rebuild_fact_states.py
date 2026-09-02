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
from factfluency.policy import policy_for, threshold_for
from factfluency.models import Attempt, GameSession, StudentFactState


class Command(BaseCommand):
    help = "Recompute StudentFactState from the attempt history."

    def add_arguments(self, parser):
        parser.add_argument("--child", help="First name; omit for every child.")
        parser.add_argument("--report", action="store_true",
                            help="After the replay, print where she stands on "
                                 "every level and name each un-mastered form.")
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
            self._rebuild(student, attempts, dry_run=options["dry_run"],
                          report=options["report"])

    def _rebuild(self, student, attempts, *, dry_run, report=False):
        # History is judged by the band she is in NOW. Change her grade and
        # re-run this, and every attempt is re-judged by the new clock — that is
        # intended: mastered by the standard of the year she is in.
        policy = policy_for(student)
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
            skipped = 0
            reflagged = []
            for attempt in attempts:
                # Migration 0008 outlawed the division forms of the zero and one
                # facts but left their attempts behind (the facts survived, so
                # nothing cascaded). Replaying those re-creates the very rows
                # that migration deleted. They are invisible to every reader,
                # but they inflate this command's own "+N mastered" headline —
                # the number used to decide whether to run it for real.
                if attempt.operation not in attempt.fact.operations():
                    skipped += 1
                    continue
                key = (attempt.fact_id, attempt.operation)
                if key not in states:
                    states[key] = scheduling.ensure_states(
                        student, [(attempt.fact, attempt.operation)])[key]
                bar = threshold_for(attempt.fact.answer(attempt.operation), policy)
                scheduling.apply_attempt(
                    states[key],
                    is_correct=attempt.is_correct,
                    response_ms=attempt.response_ms,
                    threshold=bar,
                    # As it happened, so the spacing lands where it belongs
                    # rather than stacking every fact onto today.
                    now=attempt.created_at,
                    session_id=attempt.session_id,
                )
                # The stored flag was judged by the bar of the day it was
                # answered. It feeds the done-screen counts and the records, so
                # it has to agree with the state it sits beside.
                fluent = scheduling.is_fluent(attempt.is_correct,
                                              attempt.response_ms, bar)
                if attempt.was_fluent != fluent:
                    attempt.was_fluent = fluent
                    reflagged.append(attempt)
            if reflagged:
                Attempt.objects.bulk_update(reflagged, ["was_fluent"],
                                            batch_size=500)
            self._retally_sessions(attempts)

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
                "%s: %d attempts replayed%s · mastered %d → %d (+%d, -%d)"
                % (student.first_name, len(attempts) - skipped,
                   " (%d on retired forms skipped)" % skipped if skipped else "",
                   sum(1 for v in before.values() if v[2]),
                   sum(1 for v in after.values() if v[2]),
                   len(gained), len(lost)))
            for key in lost:
                self.stdout.write(self.style.WARNING(
                    "  lost mastery: %s" % (key,)))

            if reflagged:
                self.stdout.write("  %d attempt(s) re-judged under her band"
                                  % len(reflagged))
            if report:
                self._report(student)

            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("  dry run — nothing written"))

    def _retally_sessions(self, attempts):
        """Finished sessions' fluent count and streak, from the replayed flags."""
        from collections import defaultdict

        by_session = defaultdict(list)
        for attempt in attempts:
            by_session[attempt.session_id].append(attempt)
        changed = []
        for session_id, rows in by_session.items():
            session = rows[0].session
            if session.ended_at is None:
                continue
            streak = best = 0
            for attempt in rows:
                if attempt.was_fluent:
                    streak += 1
                    best = max(best, streak)
                else:
                    streak = 0
            fluent = sum(1 for a in rows if a.was_fluent)
            if (session.num_fluent, session.longest_streak) != (fluent, best):
                session.num_fluent = fluent
                session.longest_streak = best
                changed.append(session)
        if changed:
            GameSession.objects.bulk_update(
                changed, ["num_fluent", "longest_streak"], batch_size=200)

    def _report(self, student):
        """Where she stands, level by level — the answer to 'why is she still
        on this one'."""
        from ...models import Level

        for level in Level.objects.prefetch_related("facts"):
            if level.is_challenge:
                continue
            mastered, learning, total = scheduling.level_breakdown(student, level)
            never = total - mastered - learning
            beaten = scheduling.is_level_beaten(student, level)
            self.stdout.write(
                "  L%d %-10s mastered %2d  learning %2d  never-right %2d  /%2d"
                "  need %2d  %s" % (level.order, level.slug, mastered, learning,
                                    never, total, scheduling.forms_needed(total),
                                    "BEATEN" if beaten else ""))
            if beaten:
                continue
            forms = scheduling._forms_for_level(level)
            rows = {(s.fact_id, s.operation): s
                    for s in StudentFactState.objects.filter(
                        student=student, fact__in={f for f, _ in forms})}
            for fact, operation in forms:
                state = rows.get((fact.pk, operation))
                if state is None or state.total_attempts == 0:
                    self.stdout.write("      %-8s never asked" % fact.prompt(operation))
                elif not state.is_mastered:
                    self.stdout.write(
                        "      %-8s box %d  streak %d  %d/%d right"
                        % (fact.prompt(operation), state.leitner_box,
                           state.consecutive_fluent, state.total_correct,
                           state.total_attempts))
            # Only the CURRENT level gets the form-by-form list.
            break

