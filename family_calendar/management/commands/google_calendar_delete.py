"""Delete named events from a Google calendar, using the app's service account.

For cleaning up events the app did NOT create — a hand-made series that has been
superseded by a synced one, or a stray left behind by a failed push. The sync
itself never touches anything it does not own, and this is the deliberate,
explicit exception.

Dry by default. It names what it would delete and changes nothing until --yes:

    heroku run python manage.py google_calendar_delete \\
        --calendar mom.dad.homeschool@gmail.com --event ABC123

It REFUSES to delete an event the app manages. Deleting one of those would only
desync the two: the next push would find the id gone and create it again, so the
event would come back and the link row would be stale in the meantime. If you
want an app-managed event gone, delete the CalendarEvent and let the sync remove
its copies.
"""

from django.core.management.base import BaseCommand, CommandError

from family_calendar import google_api
from family_calendar.models import GoogleCalendarLink


class Command(BaseCommand):
    help = "Delete specific events from a Google calendar (dry run unless --yes)."

    def add_arguments(self, parser):
        parser.add_argument("--calendar", required=True,
                            help="Calendar id the events live on.")
        parser.add_argument("--event", action="append", required=True,
                            dest="events", metavar="EVENT_ID",
                            help="Event id to delete. Repeat for several.")
        parser.add_argument("--yes", action="store_true",
                            help="Actually delete. Without this, nothing changes.")

    def handle(self, *args, **options):
        if not google_api.is_configured():
            raise CommandError("Google Calendar is not configured.")

        calendar_id = options["calendar"]
        if calendar_id not in google_api.calendar_ids():
            # Not a hard rule of Google's — a guard against a typo'd calendar id
            # silently doing nothing, or worse, hitting the wrong calendar.
            self.stdout.write(self.style.WARNING(
                "%s is not one of the configured calendars (%s). Continuing, but "
                "check the id." % (calendar_id, ", ".join(google_api.calendar_ids()))))

        quoted_cal = self._q(calendar_id)
        doomed = []
        for event_id in options["events"]:
            owned = GoogleCalendarLink.objects.filter(
                calendar_id=calendar_id, google_event_id=event_id).first()
            if owned:
                self.stdout.write(self.style.ERROR(
                    "  REFUSED  %s — the app manages this one (event #%s)."
                    % (event_id, owned.event_id)))
                self.stdout.write(
                    "           Delete the event in the app instead; the sync "
                    "will remove its copies.")
                continue
            try:
                event = google_api.request(
                    "GET", "/calendars/%s/events/%s" % (quoted_cal, self._q(event_id)))
            except google_api.GoogleCalendarError as exc:
                if exc.status in (404, 410):
                    self.stdout.write("  GONE     %s — already not there." % event_id)
                else:
                    self.stdout.write(self.style.ERROR(
                        "  ERROR    %s — %s" % (event_id, exc)))
                continue
            summary = (event or {}).get("summary", "(untitled)")
            recurrence = (event or {}).get("recurrence") or []
            self.stdout.write("  %s  %s%s" % (
                "DELETE  " if options["yes"] else "would delete",
                summary, "  [recurring series]" if recurrence else ""))
            doomed.append((event_id, summary))

        if not doomed:
            self.stdout.write("Nothing to do.")
            return

        if not options["yes"]:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(
                "Dry run — nothing was deleted. Add --yes to do it."))
            return

        for event_id, summary in doomed:
            try:
                google_api.request(
                    "DELETE",
                    "/calendars/%s/events/%s" % (quoted_cal, self._q(event_id)))
            except google_api.GoogleCalendarError as exc:
                if exc.status not in (404, 410):
                    self.stdout.write(self.style.ERROR(
                        "  FAILED   %s — %s" % (summary, exc)))
                    continue
            self.stdout.write(self.style.SUCCESS("  deleted  %s" % summary))

    @staticmethod
    def _q(value):
        import requests

        return requests.utils.quote(str(value), safe="")
