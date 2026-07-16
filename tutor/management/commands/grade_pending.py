"""Grade any submitted response sheet that still has no assessment.

A reliable backstop for the fire-and-forget background grader: if that daemon
thread died mid-grade (a deploy or dyno restart, a worker recycle), the
submission would sit ungraded and the parent would have to grade it by hand.
Run this on a schedule (Heroku Scheduler, e.g. every 10 minutes) so nothing
stays stuck. Idempotent — safe to run as often as you like.

    python manage.py grade_pending
    python manage.py grade_pending --limit 20
"""

from django.core.management.base import BaseCommand

from tutor import ai, grading


class Command(BaseCommand):
    help = "Grade every submitted response sheet that has no assessment yet (idempotent backstop)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Max sheets to grade this run (default: all pending).",
        )

    def handle(self, *args, **options):
        if not ai.is_configured():
            self.stdout.write("AI grader not configured (no ANTHROPIC_API_KEY) — nothing to do.")
            return
        graded, failed = grading.grade_pending_sheets(limit=options.get("limit"))
        style = self.style.SUCCESS if not failed else self.style.WARNING
        self.stdout.write(style(f"grade_pending: graded {graded}, failed {failed}."))
