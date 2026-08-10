"""Auto-pacing: project a placement's remaining lessons onto future weekdays.

Due dates are never stored — they're computed from what's actually unresolved at
request time, so finishing a lesson this morning moves every projection on the
next feed fetch. Everything here is pure (inject ``today``), which keeps the
tests deterministic without clock-freezing.
"""

from datetime import timedelta


def project_due_dates(ordered_ids, resolved, weekly_pace, today, *,
                      horizon_days=56, skip_dates=frozenset()):
    """[(lesson_id, due_date), …] — remaining unresolved lessons distributed onto
    weekdays (Mon–Fri) at ``weekly_pace`` per ISO week, skipping ``skip_dates``
    (break/no-school days). Projection starts AT ``today`` (today's mission is
    due today) and stops at the horizon, so an enormous course can't flood a feed.
    """
    if not weekly_pace:
        return []
    remaining = [lid for lid in ordered_ids if lid not in resolved]
    if not remaining:
        return []
    out = []
    per_week = {}
    d = today
    end = today + timedelta(days=horizon_days)
    while d <= end and remaining:
        if d.weekday() < 5 and d not in skip_dates:
            week = d.isocalendar()[:2]
            if per_week.get(week, 0) < weekly_pace:
                out.append((remaining.pop(0), d))
                per_week[week] = per_week.get(week, 0) + 1
        d += timedelta(days=1)
    return out


def next_due(placement, today, *, skip_dates=frozenset(), precomputed=None):
    """(lesson_id, due_date) for the placement's next projected lesson, or None.

    ``precomputed`` is the (ordered_ids, resolved) pair from
    ``placement.resolved_lesson_ids()`` when the caller already has it.
    """
    if not placement.weekly_pace:
        return None
    ordered, resolved = precomputed or placement.resolved_lesson_ids()
    projected = project_due_dates(
        ordered, resolved, placement.weekly_pace, today, skip_dates=skip_dates)
    return projected[0] if projected else None
