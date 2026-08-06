"""Work Log activity provider for core.activity.aggregate_activity (F2).

The Work Log is the richest host signal: dated per-child entries, each with a
free-text subject and (since F3) optional minutes.
"""
from curricula.subjects import canonical

from .models import WorkLogEntry


class WorkLogSignals:
    def subject_activity(self, child, start, end):
        qs = WorkLogEntry.objects.filter(child=child)
        if start is not None:
            qs = qs.filter(date__gte=start)
        if end is not None:
            qs = qs.filter(date__lte=end)
        out = {}
        for subject, day, minutes in qs.values_list("subject", "date", "minutes"):
            bucket = out.setdefault(canonical(subject), {"days": set(), "minutes": 0})
            bucket["days"].add(day)
            bucket["minutes"] += minutes or 0
        return out
