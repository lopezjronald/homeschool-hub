"""The family calendar: real-world events with light weekly recurrence.

One model, ``CalendarEvent`` — sports practices, co-op days, appointments,
charter-school meetings (LRM), breaks, and anything else with a date. A mission's
"due date" is deliberately NOT stored here: due dates are projected live from
curriculum placements (curricula/pacing.py) so they can never go stale.

Dates and times are stored as separate DateField + TimeField (never DateTimeField)
so an all-day event can't drift across the UTC boundary.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models


class CalendarEvent(models.Model):
    TYPE_ACTIVITY = "activity"
    TYPE_COOP = "coop"
    TYPE_APPOINTMENT = "appointment"
    TYPE_CHARTER = "charter"
    TYPE_BREAK = "break"
    TYPE_OTHER = "other"
    TYPE_CHOICES = [
        (TYPE_ACTIVITY, "Activity / sports"),
        (TYPE_COOP, "Co-op / class"),
        (TYPE_APPOINTMENT, "Appointment"),
        (TYPE_CHARTER, "Charter school (LRM, meetings)"),
        (TYPE_BREAK, "Break / no school"),
        (TYPE_OTHER, "Other"),
    ]
    TYPE_EMOJI = {
        TYPE_ACTIVITY: "🥋",
        TYPE_COOP: "🧑‍🏫",
        TYPE_APPOINTMENT: "🩺",
        TYPE_CHARTER: "🏫",
        TYPE_BREAK: "🌴",
        TYPE_OTHER: "📌",
    }

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="calendar_events",
    )
    family = models.ForeignKey(
        "core.Family", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="calendar_events",
    )
    child = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="calendar_events", help_text="Leave blank for a whole-family event.",
    )
    activity = models.ForeignKey(
        "activities.ExternalActivity", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="calendar_events",
        help_text="Optional: the program this event belongs to (borrows its icon).",
    )

    title = models.CharField(max_length=200, help_text="e.g. 'Jiu-jitsu', 'LRM with Mrs. Lee'")
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_OTHER)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    date = models.DateField(
        help_text="The date — or the first occurrence, for a repeating event.",
    )
    start_time = models.TimeField(null=True, blank=True, help_text="Blank = all-day.")
    end_time = models.TimeField(null=True, blank=True)

    # Light weekly recurrence — no rrule machinery. A repeating event occurs on
    # each listed weekday (or the anchor date's weekday when the list is empty)
    # from `date` through `repeat_until` (inclusive; blank = open-ended), minus
    # any individually-cancelled dates in `skip_dates`.
    repeats_weekly = models.BooleanField(default=False)
    repeat_weekdays = models.JSONField(
        default=list, blank=True,
        help_text="Weekday numbers 0=Mon … 6=Sun. Empty = the start date's weekday.",
    )
    repeat_until = models.DateField(null=True, blank=True)
    skip_dates = models.JSONField(
        default=list, blank=True,
        help_text="ISO dates of cancelled occurrences.",
    )

    # Reminders are Google's job, not ours (HH-168). The app stores WHEN to nudge;
    # the actual notification is delivered by Google Calendar, which already knows
    # how to reach a phone. Building our own notifier would mean re-solving push,
    # email and quiet hours for one household.
    #
    # A CharField rather than an integer because "no reminder at all" and "whatever
    # that calendar normally does" are both real answers, and neither is a number.
    REMIND_DEFAULT = ""
    REMIND_NONE = "none"
    REMINDER_CHOICES = [
        (REMIND_DEFAULT, "The calendar's usual reminder"),
        (REMIND_NONE, "No reminder"),
        ("0", "At the start time"),
        ("10", "10 minutes before"),
        ("30", "30 minutes before"),
        ("60", "1 hour before"),
        ("120", "2 hours before"),
        ("1440", "1 day before"),
        ("2880", "2 days before"),
        ("10080", "1 week before"),
    ]
    reminder = models.CharField(
        max_length=8, blank=True, default=REMIND_DEFAULT, choices=REMINDER_CHOICES,
        help_text="When Google should nudge you. Blank leaves it to the calendar's "
                  "own setting.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "start_time", "id"]

    def __str__(self):
        return f"{self.title} ({self.date})"

    @property
    def is_all_day(self):
        return self.start_time is None

    @property
    def emoji(self):
        if self.activity_id and self.activity and self.activity.emoji:
            return self.activity.emoji
        return self.TYPE_EMOJI.get(self.event_type, "📌")

    def reminder_overrides(self):
        """The Google ``reminders`` payload for this event, or None to defer.

        None means "send useDefault: true" — the event behaves like any other on
        that calendar. An empty list means the parent explicitly asked for silence,
        which Google expresses as useDefault: false with no overrides.
        """
        if self.reminder == self.REMIND_DEFAULT:
            return None
        if self.reminder == self.REMIND_NONE:
            return []
        try:
            minutes = int(self.reminder)
        except (TypeError, ValueError):
            return None            # a junk value defers rather than crashing a sync
        # Google rejects anything outside 0..40320 (four weeks).
        if not 0 <= minutes <= 40320:
            return None
        return [{"method": "popup", "minutes": minutes}]

    def weekday_set(self):
        """The weekdays a repeating event lands on (defensive against bad JSON)."""
        days = {d for d in (self.repeat_weekdays or []) if isinstance(d, int) and 0 <= d <= 6}
        return days or {self.date.weekday()}

    def occurrences(self, window_start, window_end):
        """Concrete occurrence dates inside [window_start, window_end] (inclusive).

        Pure and bounded: callers clamp the window (feeds.parse_window), so the
        day-walk can't run away on an open-ended series.
        """
        if window_end < window_start:
            return []
        if not self.repeats_weekly:
            return [self.date] if window_start <= self.date <= window_end else []
        skips = {s for s in (self.skip_dates or []) if isinstance(s, str)}
        days = self.weekday_set()
        start = max(self.date, window_start)
        end = window_end if self.repeat_until is None else min(self.repeat_until, window_end)
        out = []
        d = start
        while d <= end:
            if d.weekday() in days and d.isoformat() not in skips:
                out.append(d)
            d += timedelta(days=1)
        return out
