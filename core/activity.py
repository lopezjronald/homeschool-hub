"""Cross-app activity aggregation — the one place that answers "what did this child
do, when, and in which subject?" (roadmap foundation F2).

The signal is fragmented: the Work Log has dated entries (+ optional minutes), the
curricula app has lesson-complete marks, and the lingua module has its own reading
and listening sessions. Every engagement feature (the whole-school streak, the
hours/attendance report, family analytics, the trophy case) needs them UNIONED.

The union happens through PROVIDERS resolved from the ``ACTIVITY_SIGNAL_PROVIDERS``
setting — dotted paths imported best-effort, mirroring ``lingua.services
.get_worklog_sink``. Each provider exposes one method::

    subject_activity(child, start, end) -> {canonical_subject: {"days": set[date],
                                                                 "minutes": int}}

``start``/``end`` are inclusive local dates, or ``None`` for an open bound. This
module imports NO app models and does NOT know lingua exists — the only code that
reaches into lingua is the lingua provider adapter, exactly as the WorkLogSink
adapter does today. Remove lingua and its dotted path drops out; the aggregator
still runs (proven by test). That keeps lingua extractable in both directions.

Days DE-DUP because they collect into a set; the lingua book mirror already writes a
"Spanish reading" Work Log row, so a reading day is seen by both the worklog and the
lingua provider — union counts it once. Minutes do NOT double-count only because the
mirrored row carries no minutes; the real Spanish minutes come solely from the lingua
provider. Both invariants are asserted by test, never assumed.
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string


def _providers():
    """Instantiate the activity providers named in ``ACTIVITY_SIGNAL_PROVIDERS``.

    Best-effort, per provider: a missing or broken one is skipped, never fatal — an
    activity report is an enhancement over the raw records, and one dud adapter must
    not blank the whole page (same contract as ``get_worklog_sink``)."""
    providers = []
    for dotted in getattr(settings, "ACTIVITY_SIGNAL_PROVIDERS", ()):
        try:
            providers.append(import_string(dotted)())
        except Exception:  # noqa: BLE001 — a bad provider is skipped, not fatal
            continue
    return providers


def aggregate_activity(child, start=None, end=None):
    """Union every provider's signal for ``child`` within ``[start, end]``.

    Returns a dict::

        {
          "by_subject": {slug: {"days": set[date], "minutes": int}},
          "days": set[date],          # distinct days across ALL subjects
          "days_count": int,
          "total_minutes": int,
        }

    Read-only: never provisions or writes anything (the lingua provider looks its
    learner up, it does not create one)."""
    merged = {}
    for provider in _providers():
        try:
            contrib = provider.subject_activity(child, start, end) or {}
        except Exception:  # noqa: BLE001 — one provider failing must not blank the rest
            continue
        for slug, data in contrib.items():
            bucket = merged.setdefault(slug, {"days": set(), "minutes": 0})
            bucket["days"].update(data.get("days") or ())
            bucket["minutes"] += data.get("minutes") or 0

    all_days = set()
    total_minutes = 0
    for data in merged.values():
        all_days |= data["days"]
        total_minutes += data["minutes"]
    return {
        "by_subject": merged,
        "days": all_days,
        "days_count": len(all_days),
        "total_minutes": total_minutes,
    }


def _streak_from_days(days, *, on):
    """Consecutive days ending at ``on`` on which the child did something.

    Lifted verbatim from ``lingua.services.camino_streak`` so the whole-school streak
    behaves exactly like the Spanish one the family already knows: today's absence
    does not break it — yesterday still counts when today hasn't started — so opening
    the app in the morning never shows the streak already lost."""
    days = {d for d in days if d <= on}
    if not days:
        return 0
    cursor = on if on in days else on - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def current_streak(child, *, on=None):
    """The child's forgiving whole-school streak as of ``on`` (default: today)."""
    on = on or timezone.localdate()
    agg = aggregate_activity(child, None, on)
    return _streak_from_days(agg["days"], on=on)
