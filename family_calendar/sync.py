"""Pushing the family calendar into Google (HH-168).

One direction only: the app owns the data, Google owns the notifications. Two-way
sync would need change-watching, conflict resolution and a public webhook, and
nobody asked to edit school events from a phone — they asked to stop missing them.

Only stored CalendarEvent rows travel. The calendar's other four layers
(missions, birthdays, Spanish, history) are projections rebuilt on every fetch —
a mission due date moves whenever a lesson is completed — so pushing them would
mean rewriting hundreds of Google events every time a child ticks a box, and
burying the one real appointment underneath them.
"""

import hashlib
import json
import logging
from datetime import datetime, time as dt_time, timedelta, timezone as dt_timezone

from django.conf import settings
from django.utils import timezone

from . import google_api
from .models import CalendarEvent, GoogleCalendarLink

logger = logging.getLogger(__name__)

# RRULE weekday tokens, indexed by Python's weekday(): 0=Mon. CalendarEvent
# stores exactly that, so this is a straight lookup rather than a conversion.
RRULE_DAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

# How far ahead to look for a repeating event's first real occurrence. A weekly
# series lands within seven days; a year is a generous bound that still cannot
# run away on an open-ended series.
_FIRST_OCCURRENCE_HORIZON = 370

# An event with a start but no end. Google requires an end, and a zero-length
# event renders as a hairline nobody can tap.
DEFAULT_DURATION = timedelta(hours=1)


def _tz_name():
    return getattr(settings, "TIME_ZONE", "America/Los_Angeles")


def first_occurrence(event):
    """The date Google should treat as the series start.

    NOT simply ``event.date``. RFC 5545 makes DTSTART an instance of the series
    whether or not it matches BYDAY, and Google honours that — so an event
    anchored on a Monday but repeating Tue/Thu would grow a phantom Monday in
    Google that the app itself does not show. Handing Google the first date the
    app agrees is real keeps the two in step.
    """
    if not event.repeats_weekly:
        return event.date
    window_end = event.date + timedelta(days=_FIRST_OCCURRENCE_HORIZON)
    if event.repeat_until:
        window_end = min(window_end, event.repeat_until)
    occurrences = event.occurrences(event.date, window_end)
    return occurrences[0] if occurrences else None


def recurrence_lines(event, start_date):
    """The RRULE (and any EXDATE) for a repeating event, or [] for a one-off."""
    if not event.repeats_weekly or start_date is None:
        return []

    days = sorted(event.weekday_set())
    rule = "RRULE:FREQ=WEEKLY;BYDAY=" + ",".join(RRULE_DAYS[d] for d in days)

    if event.repeat_until:
        # UNTIL is inclusive at both ends, but for a TIMED series it must be a
        # UTC instant — so take the last local moment of repeat_until and convert.
        # Using midnight would drop the final occurrence.
        if event.is_all_day:
            rule += ";UNTIL=%s" % event.repeat_until.strftime("%Y%m%d")
        else:
            last = _localise(datetime.combine(event.repeat_until, dt_time(23, 59, 59)))
            rule += ";UNTIL=%s" % last.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [rule]
    exdates = _exdates(event, start_date)
    if exdates:
        if event.is_all_day:
            lines.append("EXDATE;VALUE=DATE:" + ",".join(
                d.strftime("%Y%m%d") for d in exdates))
        else:
            # The EXDATE value type must match DTSTART's, so a timed series needs
            # the time of day attached and the series timezone named.
            stamp = event.start_time.strftime("%H%M%S")
            lines.append("EXDATE;TZID=%s:" % _tz_name() + ",".join(
                "%sT%s" % (d.strftime("%Y%m%d"), stamp) for d in exdates))
    return lines


def _exdates(event, start_date):
    """Cancelled dates that Google would otherwise generate.

    Filtered against the pattern: a skip_date for a day the series never lands
    on is not an exception, and sending one makes Google reject the whole event.
    """
    from datetime import date as date_cls

    days = event.weekday_set()
    out = []
    for raw in (event.skip_dates or []):
        if not isinstance(raw, str):
            continue
        try:
            parsed = date_cls.fromisoformat(raw)
        except ValueError:
            continue
        if parsed < start_date:
            continue
        if event.repeat_until and parsed > event.repeat_until:
            continue
        if parsed.weekday() in days:
            out.append(parsed)
    return sorted(out)


def _localise(naive):
    """Attach the family's timezone to a naive datetime."""
    try:
        from zoneinfo import ZoneInfo

        return naive.replace(tzinfo=ZoneInfo(_tz_name()))
    except Exception:                      # pragma: no cover - bad TZ database
        return timezone.make_aware(naive)


def event_body(event):
    """The Google event for ``event``, or None if it has no real occurrence."""
    start_date = first_occurrence(event)
    if start_date is None:
        return None

    title = event.title
    if event.child_id and event.child:
        # Both households read this calendar; whose event it is matters more
        # than it does inside the app, where a colour already says so.
        title = "%s · %s" % (title, event.child.first_name)

    body = {
        "summary": title,
        "description": event.notes or "",
        "location": event.location or "",
    }

    if event.is_all_day:
        # Google treats an all-day end as EXCLUSIVE, so a single day ends on the
        # following date. Sending the same date for both makes the event vanish.
        body["start"] = {"date": start_date.isoformat()}
        body["end"] = {"date": (start_date + timedelta(days=1)).isoformat()}
    else:
        start = _localise(datetime.combine(start_date, event.start_time))
        if event.end_time:
            end = _localise(datetime.combine(start_date, event.end_time))
        else:
            end = start + DEFAULT_DURATION
        tz = _tz_name()
        # Both the offset AND the named zone: the offset fixes the instant, and
        # the name is what keeps a recurring 4pm at 4pm across a DST boundary
        # rather than sliding to 3pm. One of the two calendars is set to UTC,
        # which makes this the difference between right and an hour out.
        body["start"] = {"dateTime": start.isoformat(), "timeZone": tz}
        body["end"] = {"dateTime": end.isoformat(), "timeZone": tz}

    recurrence = recurrence_lines(event, start_date)
    if recurrence:
        body["recurrence"] = recurrence

    overrides = event.reminder_overrides()
    if overrides is None:
        # The parent did not choose, so behave like any other event on that
        # calendar rather than imposing a scheme of ours.
        body["reminders"] = {"useDefault": True}
    else:
        body["reminders"] = {"useDefault": False, "overrides": overrides}

    return body


def content_hash(body):
    """A stable fingerprint, so an unchanged event costs nothing to re-save."""
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def push_event(event, *, force=False):
    """Send one event to every configured calendar.

    Returns a list of (calendar_id, status) where status is "created",
    "updated", "unchanged" or "failed". NEVER raises: a calendar that Google
    cannot be reached for is recorded on the link and retried later, because a
    parent saving a dentist appointment must not see an error from Google.
    """
    if not google_api.is_configured():
        return []

    body = event_body(event)
    if body is None:
        # A repeating event whose window contains no occurrence has nothing to
        # show. Remove anything already pushed rather than leaving a stale copy.
        remove_event(event)
        return []

    digest = content_hash(body)
    results = []
    for calendar_id in google_api.calendar_ids():
        link, _ = GoogleCalendarLink.objects.get_or_create(
            event=event, calendar_id=calendar_id)
        if (not force and link.google_event_id and link.content_hash == digest
                and not link.last_error):
            results.append((calendar_id, "unchanged"))
            continue
        try:
            if link.google_event_id:
                google_api.request(
                    "PUT",
                    "/calendars/%s/events/%s" % (_q(calendar_id),
                                                 _q(link.google_event_id)),
                    json_body=body)
                status = "updated"
            else:
                created = google_api.request(
                    "POST", "/calendars/%s/events" % _q(calendar_id),
                    json_body=body)
                link.google_event_id = (created or {}).get("id", "")
                status = "created"
        except google_api.GoogleCalendarError as exc:
            if link.google_event_id and getattr(exc, "status", None) in (404, 410):
                # Someone deleted it in Google. Forget the id so the next run
                # creates a fresh one instead of updating a corpse forever.
                link.google_event_id = ""
            link.last_error = str(exc)[:500]
            link.save()
            logger.warning("calendar push failed for event %s -> %s: %s",
                           event.pk, calendar_id, exc)
            results.append((calendar_id, "failed"))
            continue

        link.content_hash = digest
        link.last_error = ""
        link.synced_at = timezone.now()
        link.save()
        results.append((calendar_id, status))
    return results


def remove_event(event=None, *, links=None):
    """Delete the Google copies for an event. Never raises.

    Accepts pre-read links so a post_delete receiver can hand over rows it
    captured before the cascade removed them.
    """
    if not google_api.is_configured():
        return []
    if links is None:
        links = list(GoogleCalendarLink.objects.filter(event=event))

    results = []
    for link in links:
        if not link.google_event_id:
            _forget(link)
            continue
        try:
            google_api.request(
                "DELETE", "/calendars/%s/events/%s" % (_q(link.calendar_id),
                                                       _q(link.google_event_id)))
        except google_api.GoogleCalendarError as exc:
            # Already gone is the outcome we wanted, not a failure.
            if getattr(exc, "status", None) not in (404, 410):
                logger.warning("calendar delete failed for %s: %s",
                               link.google_event_id, exc)
                results.append((link.calendar_id, "failed"))
                continue
        _forget(link)
        results.append((link.calendar_id, "deleted"))
    return results


def _forget(link):
    if link.pk:
        link.delete()


def _q(value):
    import requests

    return requests.utils.quote(str(value), safe="")


def pending_events(*, since=None):
    """Events that still owe Google something: never pushed, changed since the
    last push, or failed last time. ``since`` bounds the backfill to the future."""
    from django.db.models import Q

    events = CalendarEvent.objects.all()
    if since is not None:
        # A repeating series that is still running counts as future even though
        # its anchor date is in the past.
        events = events.filter(
            Q(date__gte=since)
            | Q(repeats_weekly=True, repeat_until__isnull=True)
            | Q(repeats_weekly=True, repeat_until__gte=since))
    return events.select_related("child").order_by("date", "id")
