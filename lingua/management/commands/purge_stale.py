"""Purge lingua data past its retention window (D-56).

Retention limits are a written policy (lingua/RETENTION.md) enforced in code. For
now the only time-bounded store is the audit trail; as content/review models land
(M1/M2) their retention rules are added here. Idempotent; Heroku-Scheduler-safe.
"""
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from lingua.models import AuditEvent

DEFAULT_AUDIT_RETENTION_DAYS = 548  # ~18 months


class Command(BaseCommand):
    help = "Purge lingua data past its retention window (audit events)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would be purged without deleting.",
        )

    def handle(self, *args, **options):
        cfg = getattr(settings, "LINGUA", {})
        days = cfg.get("AUDIT_RETENTION_DAYS", DEFAULT_AUDIT_RETENTION_DAYS)
        cutoff = timezone.now() - timedelta(days=days)
        stale = AuditEvent.objects.filter(ts__lt=cutoff)
        count = stale.count()
        if not count:
            self.stdout.write(f"No audit events older than {days} days.")
            return
        if options["dry_run"]:
            self.stdout.write(f"[dry-run] would purge {count} audit event(s) older than {days}d.")
            return
        deleted, _ = stale.delete()
        self.stdout.write(f"Purged {deleted} audit event(s) older than {days}d.")
