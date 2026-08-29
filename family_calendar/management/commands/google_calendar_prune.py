"""Remove the app's own copies from a calendar it no longer pushes to.

WHY THIS EXISTS. ``push_event`` sends every event to each id in
GOOGLE_CALENDAR_IDS. Take one out of that list and the pushing stops, but the
copies already on it are orphaned: nothing revisits a calendar that is no longer
configured, so they sit there forever and every event shows twice to anyone
subscribed to both. That is what happened with two calendars configured at once
— 84 soccer practices, each of them on both calendars.

    heroku run python manage.py google_calendar_prune \\
        --calendar family...@group.calendar.google.com          # dry run
    heroku run python manage.py google_calendar_prune \\
        --calendar family...@group.calendar.google.com --yes    # actually delete

It deletes ONLY events the app created, found through the GoogleCalendarLink
rows that record what was pushed where. An event with no link row is somebody's
own, and this never touches it.

It REFUSES a calendar that is still configured. Pruning one of those would be
undone by the next push and leave the link rows lying about a calendar that has
since been repopulated — so remove the id from GOOGLE_CALENDAR_IDS first, which
is the step that actually stops the duplication.
"""

from django.core.management.base import BaseCommand, CommandError

from family_calendar import google_api, sync
from family_calendar.models import GoogleCalendarLink


class Command(BaseCommand):
    help = ("Delete the app's own copies from a calendar it no longer syncs to "
            "(dry run unless --yes).")

    def add_arguments(self, parser):
        parser.add_argument("--calendar", required=True,
                            help="The calendar to clear the app's events off.")
        parser.add_argument("--yes", action="store_true",
                            help="Actually delete. Without this, nothing changes.")

    def handle(self, *args, **options):
        calendar_id = options["calendar"].strip()
        if not google_api.is_configured():
            raise CommandError("Google Calendar is not configured.")

        configured = google_api.calendar_ids()
        # Case-folded deliberately: calendar ids are email addresses, and
        # matching exactly here while the ORM also matches exactly would mean
        # two accidents standing in for one check.
        if calendar_id.casefold() in {c.casefold() for c in configured}:
            raise CommandError(
                "%s is still in GOOGLE_CALENDAR_IDS, so the next push would put "
                "everything back. Remove it from that config var first:\n"
                "    heroku config:set GOOGLE_CALENDAR_IDS=%s"
                % (calendar_id,
                   ",".join(c for c in configured if c != calendar_id)))

        links = list(GoogleCalendarLink.objects.filter(calendar_id=calendar_id)
                     .select_related("event").order_by("pk"))
        if not links:
            self.stdout.write("Nothing to do: the app has no record of pushing "
                              "anything to %s." % calendar_id)
            return

        pushed = [l for l in links if l.google_event_id]
        self.stdout.write("%d event(s) the app pushed to %s:"
                          % (len(pushed), calendar_id))
        for link in pushed[:20]:
            self.stdout.write("    %s" % (getattr(link.event, "title", "?")))
        if len(pushed) > 20:
            self.stdout.write("    ... and %d more" % (len(pushed) - 20))
        stale = len(links) - len(pushed)
        if stale:
            self.stdout.write("  (plus %d link row(s) with no Google copy)" % stale)

        if not options["yes"]:
            self.stdout.write(self.style.WARNING(
                "\nDry run — nothing deleted. Re-run with --yes to delete these "
                "%d event(s) from %s." % (len(pushed), calendar_id)))
            return

        # remove_event already knows how to delete a copy and forget its row,
        # and treats an already-deleted event as success rather than failure.
        results = sync.remove_event(links=links)
        deleted = sum(1 for _cal, status in results if status == "deleted")
        failed = sum(1 for _cal, status in results if status == "failed")
        self.stdout.write(self.style.SUCCESS(
            "Deleted %d event(s) from %s." % (deleted, calendar_id)))
        if failed:
            self.stdout.write(self.style.ERROR(
                "%d failed — their link rows were kept, so running this again "
                "will retry them." % failed))
        left = GoogleCalendarLink.objects.filter(calendar_id=calendar_id).count()
        self.stdout.write("Link rows remaining for that calendar: %d" % left)
