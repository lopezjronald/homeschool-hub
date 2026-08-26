"""Push the family calendar into Google, and repair anything that drifted.

Three jobs in one command:

  * the BACKFILL — everything from today forward, once, when the feature is
    first switched on;
  * the RETRY — a push that failed because Google was briefly unreachable. The
    save that triggered it deliberately swallowed the error so the parent never
    saw it, which means something else has to notice;
  * the RECONCILE — an event edited while the dyno was restarting, whose
    background push died mid-flight.

    heroku run python manage.py sync_google_calendar -a steadfast-scholars

Safe to run repeatedly: an event whose content has not changed since its last
push is skipped without touching Google.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from family_calendar import google_api, sync


class Command(BaseCommand):
    help = "Push calendar events to Google, retrying anything that failed."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all", action="store_true",
            help="Include past events. By default only today forward is pushed, "
                 "because nobody needs a reminder for last March.")
        parser.add_argument(
            "--force", action="store_true",
            help="Re-push even events whose content is unchanged.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="List what would be pushed, and touch nothing.")

    def handle(self, *args, **options):
        if not google_api.is_configured():
            self.stdout.write(self.style.WARNING(
                "Google Calendar is not configured — nothing to do."))
            return

        since = None if options["all"] else timezone.localdate()
        events = list(sync.pending_events(since=since))
        self.stdout.write("%d event%s in scope."
                          % (len(events), "" if len(events) == 1 else "s"))

        if options["dry_run"]:
            for event in events:
                self.stdout.write("  would push: %s (%s)" % (event.title, event.date))
            self.stdout.write(self.style.WARNING("Dry run — nothing was sent."))
            return

        tally = {}
        failures = []
        for event in events:
            for calendar_id, status in sync.push_event(event, force=options["force"]):
                tally[status] = tally.get(status, 0) + 1
                if status == "failed":
                    failures.append((event, calendar_id))

        for status in ("created", "updated", "unchanged", "failed"):
            if tally.get(status):
                line = "  %-9s %d" % (status, tally[status])
                self.stdout.write(
                    self.style.ERROR(line) if status == "failed"
                    else self.style.SUCCESS(line) if status in ("created", "updated")
                    else line)

        if failures:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("Still failing:"))
            for event, calendar_id in failures[:20]:
                link = event.google_links.filter(calendar_id=calendar_id).first()
                self.stdout.write("  %s (%s) -> %s" % (
                    event.title, event.date, (link.last_error if link else "")[:160]))
            if len(failures) > 20:
                self.stdout.write("  ... and %d more" % (len(failures) - 20))
        elif events:
            self.stdout.write(self.style.SUCCESS("Google is up to date."))
