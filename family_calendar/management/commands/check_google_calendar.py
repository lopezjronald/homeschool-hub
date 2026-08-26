"""Does the Google Calendar handshake actually work? (HH-168)

Run this after sharing the calendars with the service account. It answers the
one question the setup cannot answer by eye: Google's own view of what this app
is allowed to do. The sharing UI will happily show a robot as "pending" forever
even when the permission is live, so looking at the screen proves nothing.

    heroku run python manage.py check_google_calendar -a steadfast-scholars

It creates no events and changes nobody's calendar. It may add a
calendar to the SERVICE ACCOUNT's own list, which is how a robot picks up a
share nobody can accept on its behalf.
"""

from django.core.management.base import BaseCommand

from family_calendar import google_api


class Command(BaseCommand):
    help = "Report what the service account may do with each configured calendar."

    def handle(self, *args, **options):
        sa = None
        try:
            sa = google_api.service_account()
        except google_api.GoogleCalendarError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        if sa is None:
            self.stdout.write(self.style.WARNING(
                "GOOGLE_CALENDAR_SA_KEY_JSON is not set — the sync is switched off."))
            return

        ids = google_api.calendar_ids()
        self.stdout.write("Signing as %s" % sa["client_email"])
        if not ids:
            self.stdout.write(self.style.WARNING(
                "GOOGLE_CALENDAR_IDS is empty — there is nowhere to write to."))
            return

        try:
            google_api.access_token()
        except google_api.GoogleCalendarError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            self.stderr.write(
                "The key itself was rejected, so no calendar can work yet. "
                "Check that the Calendar API is enabled on the project.")
            return
        self.stdout.write(self.style.SUCCESS("Key accepted, token minted."))
        self.stdout.write("")

        ok = True
        for calendar_id in ids:
            try:
                role = google_api.access_role(calendar_id)
            except google_api.GoogleCalendarError as exc:
                ok = False
                self.stdout.write(self.style.ERROR("  FAIL  %s" % calendar_id))
                if exc.status == 404:
                    self.stdout.write(
                        "        Google has never heard of this calendar for this "
                        "account. Either the id is wrong, or it was never shared "
                        "with the address above.")
                elif exc.status == 403:
                    # Calendar v3 answers 404 — not 403 — when access is denied,
                    # so it cannot leak whether a calendar exists. A 403 here is
                    # a quota or rate limit, and telling the operator to reshare
                    # a correctly-shared calendar would send them the wrong way.
                    self.stdout.write(
                        "        Google refused with a quota or rate limit, not a "
                        "permission problem. Wait a minute and run this again.")
                else:
                    self.stdout.write("        %s" % exc)
                continue

            if role in google_api.WRITABLE_ROLES:
                self.stdout.write(self.style.SUCCESS(
                    "  OK    %s  (%s)" % (calendar_id, role)))
            elif role == google_api.ROLE_PARTIAL:
                ok = False
                self.stdout.write(self.style.WARNING(
                    "  NEAR  %s  (%s)" % (calendar_id, role)))
                self.stdout.write(
                    "        That is the row ABOVE the one we need. Reshare with "
                    "'Make changes and see event details'.")
            else:
                ok = False
                self.stdout.write(self.style.ERROR(
                    "  READ  %s  (%s)" % (calendar_id, role or "no access")))
                self.stdout.write(
                    "        Read-only. Reshare with 'Make changes and see event "
                    "details'.")

        self.stdout.write("")
        if ok:
            self.stdout.write(self.style.SUCCESS(
                "Every calendar is writable — the handshake is done."))
        else:
            self.stdout.write(self.style.WARNING(
                "Not ready yet. Fix the calendars flagged above and run this again."))
