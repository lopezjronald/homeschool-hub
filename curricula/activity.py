"""Curricula activity provider for core.activity.aggregate_activity (F2).

A parent marking a lesson complete is a day of work even when no separate Work Log
entry was written, so LessonProgress contributes DAYS (never minutes — a checkbox
carries no time). SKIPPED lessons are excluded: a skip is the parent passing the
lesson over, not the child doing it.
"""
from django.utils import timezone

from curricula.subjects import canonical

from .models import LessonProgress


class LessonProgressSignals:
    def subject_activity(self, child, start, end):
        qs = (
            LessonProgress.objects.filter(child=child)
            .exclude(status=LessonProgress.SKIPPED)
        )
        if start is not None:
            qs = qs.filter(created_at__date__gte=start)
        if end is not None:
            qs = qs.filter(created_at__date__lte=end)
        out = {}
        rows = qs.values_list("lesson__chapter__curriculum__subject", "created_at")
        for subject, created_at in rows:
            day = timezone.localdate(created_at)
            out.setdefault(canonical(subject), {"days": set(), "minutes": 0})["days"].add(day)
        return out
