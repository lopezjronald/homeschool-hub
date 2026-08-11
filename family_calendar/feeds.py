"""Shared calendar-feed builders.

Both feeds (parent + kid portal), the hub tile, and the portal agenda strip call
these so every surface agrees on colors, titles, and windows. Everything here is
plain data-in/data-out; scoping (WHICH events, WHICH children) is the caller's
job — the parent feed scopes via core.permissions, the portal feed via the token.
"""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import CalendarEvent

# Per-child event colors — all AA (>= 4.5:1) with white text. Children map to the
# palette by index over the family's students (Student.Meta orders by first_name),
# stable for a small family and cycling beyond it. Whole-family events are navy.
# The raw brand amber (#EBA83A) deliberately fails AA on white, so amber duties
# fall to its 700-weight.
CHILD_PALETTE = ["#0A5C63", "#2F6FB3", "#1E7A50", "#8A5B12"]
FAMILY_COLOR = "#152A45"
BREAK_COLOR = "#F5E3C0"  # background wash, not a chip — text never sits on it


def child_color_map(children):
    """{student_id: color} for an ordered iterable of students."""
    return {
        s.pk: CHILD_PALETTE[i % len(CHILD_PALETTE)] for i, s in enumerate(children)
    }


def safe_parse_date(raw):
    """`parse_date` that can never raise: slices a datetime down to its date and
    returns None for anything malformed OR out-of-range (parse_date itself
    raises ValueError on well-formed nonsense like 2026-99-99)."""
    try:
        return parse_date((raw or "")[:10].strip())
    except ValueError:
        return None


def parse_window(request, *, max_days=400, default_back=30, default_fwd=60):
    """The [start, end] date window a feed request asks for, hardened + clamped.

    FullCalendar sends ISO datetimes (`?start=2026-08-01T00:00:00-07:00`), so the
    date is sliced off the front before parsing; garbage never 500s, it just
    falls back to a sensible default window around today.
    """
    today = timezone.localdate()
    start = safe_parse_date(request.GET.get("start")) or (today - timedelta(days=default_back))
    end = safe_parse_date(request.GET.get("end")) or (today + timedelta(days=default_fwd))
    if end < start:
        start, end = end, start
    if (end - start).days > max_days:
        end = start + timedelta(days=max_days)
    return start, end


def event_json(event, occ_date, *, color, url=""):
    """One FullCalendar event object for one concrete occurrence."""
    if event.is_all_day:
        start = occ_date.isoformat()
        end = None
    else:
        start = f"{occ_date.isoformat()}T{event.start_time.strftime('%H:%M:%S')}"
        end = (
            f"{occ_date.isoformat()}T{event.end_time.strftime('%H:%M:%S')}"
            if event.end_time else None
        )
    data = {
        "id": f"ev-{event.pk}-{occ_date.isoformat()}",
        "title": f"{event.emoji} {event.title}",
        "start": start,
        "allDay": event.is_all_day,
        "color": color,
        "extendedProps": {
            "layer": "events",
            "event_type": event.event_type,
            "child_id": event.child_id,
            "location": event.location,
        },
    }
    if end:
        data["end"] = end
    if url:
        data["url"] = url
    if event.event_type == CalendarEvent.TYPE_BREAK:
        # Breaks paint the day, they don't compete for chip space.
        data["display"] = "background"
        data["color"] = BREAK_COLOR
    return data


def event_layer(events, window, colors, *, url_for=None):
    """FullCalendar objects for every occurrence of `events` inside `window`.

    `colors` is a {student_id: color} map; `url_for(event)` supplies the
    click-through (parent: edit page; portal: none).
    """
    start, end = window
    out = []
    for event in events:
        color = colors.get(event.child_id, FAMILY_COLOR)
        url = url_for(event) if url_for else ""
        for occ in event.occurrences(start, end):
            out.append(event_json(event, occ, color=color, url=url))
    return out


def mission_layer(placements, window, colors, *, today=None, breaks=frozenset(),
                  url_for=None, label_for=None):
    """Projected "due" events for paced placements (weekly_pace set).

    Never stored: each call re-projects from ``resolved_lesson_ids()``, so
    completing a lesson moves every remaining due date on the next fetch.
    Missions render OUTLINED (white fill, child-colored border/text — the CSS
    keys on layer=missions) so a projection never reads as a hard appointment.
    """
    from curricula.models import Lesson
    from curricula.pacing import project_due_dates

    today = today or timezone.localdate()
    start, end = window
    out = []
    for placement in placements:
        if not placement.weekly_pace or not placement.is_active:
            continue
        ordered, resolved = placement.resolved_lesson_ids()
        projected = [
            (lid, due) for lid, due in project_due_dates(
                ordered, resolved, placement.weekly_pace, today, skip_dates=breaks)
            if start <= due <= end
        ]
        if not projected:
            continue
        lessons = Lesson.objects.in_bulk([lid for lid, _ in projected])
        color = colors.get(placement.child_id, FAMILY_COLOR)
        for lid, due in projected:
            lesson = lessons.get(lid)
            if lesson is None:
                continue
            label = label_for(placement, lesson) if label_for else (lesson.title or lesson.code)
            out.append({
                "id": f"mission-{placement.pk}-{lid}",
                "title": f"🎯 {label}",
                "start": due.isoformat(),
                "allDay": True,
                "color": color,
                "textColor": color,
                "url": url_for(placement, lesson) if url_for else "",
                "extendedProps": {
                    "layer": "missions",
                    "child_id": placement.child_id,
                    "curriculum_id": placement.curriculum_id,
                },
            })
    return out


HISTORY_BG = "#E4F0E9"
HISTORY_TEXT = "#1E5238"
HISTORY_MAX_LOOKBACK_DAYS = 183


def history_layer(children, window, *, today=None, muted=False):
    """One quiet ✓ event per child per past day they did work — the calendar
    doubles as an attendance/record view. Reads core.activity.aggregate_activity
    (the same union the streak and hours report use) and never looks forward or
    further back than ~6 months, whatever window the client asks for.
    """
    from core.activity import aggregate_activity

    today = today or timezone.localdate()
    start, end = window
    end = min(end, today - timedelta(days=1))                 # history is the past
    start = max(start, today - timedelta(days=HISTORY_MAX_LOOKBACK_DAYS))
    if end < start:
        return []
    out = []
    for child in children:
        agg = aggregate_activity(child, start=start, end=end)
        by_day = {}
        for slug, info in agg.get("by_subject", {}).items():
            for day in info.get("days", ()):
                by_day.setdefault(day, set()).add(slug.replace("-", " "))
        # Days with activity but no subject breakdown still deserve their ✓.
        for day in agg.get("days", ()):
            by_day.setdefault(day, set())
        for day, subjects in sorted(by_day.items()):
            if not (start <= day <= end):
                continue
            labels = ", ".join(sorted(subjects)[:3])
            out.append({
                "id": f"hist-{child.pk}-{day.isoformat()}",
                "title": f"✓ {child.first_name}" + (f" · {labels}" if labels else ""),
                "start": day.isoformat(),
                "allDay": True,
                "color": HISTORY_BG,
                "textColor": HISTORY_TEXT,
                "extendedProps": {"layer": "history", "child_id": child.pk},
            })
    return out


def birthday_layer(children, window):
    """🎂 all-day events for every birthday that falls inside the window."""
    from datetime import date

    start, end = window
    out = []
    for child in children:
        dob = child.date_of_birth
        if not dob:
            continue
        for year in range(start.year, end.year + 1):
            try:
                bday = date(year, dob.month, dob.day)
            except ValueError:                                # Feb 29 on a common year
                bday = date(year, 2, 28)
            if start <= bday <= end and year >= dob.year:
                out.append({
                    "id": f"bday-{child.pk}-{year}",
                    "title": f"🎂 {child.first_name} turns {year - dob.year}",
                    "start": bday.isoformat(),
                    "allDay": True,
                    "color": "#8A5B12",                        # amber-700, AA on white
                    "extendedProps": {"layer": "birthdays", "child_id": child.pk},
                })
    return out


def break_dates(events, window, child=None):
    """All break/no-school dates in `window` that apply to `child`.

    A break tagged to a different child doesn't pause this child's pacing;
    whole-family breaks (child=None) pause everyone.
    """
    start, end = window
    out = set()
    for event in events:
        if event.event_type != CalendarEvent.TYPE_BREAK:
            continue
        if event.child_id and child is not None and event.child_id != child.pk:
            continue
        out.update(event.occurrences(start, end))
    return out


def upcoming_occurrences(events, *, limit=3, days=14, today=None):
    """The next few (date, event) pairs across `events` — for the hub tile.

    Skips break washes (they're context, not appointments).
    """
    today = today or timezone.localdate()
    window = (today, today + timedelta(days=days))
    pairs = []
    for event in events:
        if event.event_type == CalendarEvent.TYPE_BREAK:
            continue
        for occ in event.occurrences(*window):
            pairs.append((occ, event))
    pairs.sort(key=lambda p: (p[0], p[1].start_time or timezone.datetime.min.time()))
    return pairs[:limit]
