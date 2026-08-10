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
