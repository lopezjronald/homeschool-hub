"""The lingua activity provider for core.activity.aggregate_activity (F2).

This is the ONLY module that imports lingua for activity aggregation — the same
adapter seam as lingua_worklog.py / lingua_ai.py. core.activity depends only on the
ACTIVITY_SIGNAL_PROVIDERS dotted paths, so removing lingua drops this one path and
the aggregator still runs (proven by CrossAppActivityTests.test_runs_without_lingua).

All Spanish input files under the single canonical subject "spanish", which is also
what curricula.subjects.canonical() folds the lingua book mirror's "Spanish reading"
Work Log rows into — so a reading day seen by both providers unions to one day, and
the real minutes come only from here (the mirrored row carries none).

Read-only and side-effect-free: it LOOKS the learner up (never provisions one), so
aggregating a child who has never touched Spanish creates no Learner row.
"""
from lingua import services as lingua_services
from lingua.models import Learner

SUBJECT = "spanish"


class LinguaSignals:
    def subject_activity(self, child, start, end):
        learner = Learner.objects.filter(host_student_id=child.pk).first()
        if learner is None:
            return {}
        days = {
            d for d in lingua_services.camino_active_days(learner)
            if (start is None or d >= start) and (end is None or d <= end)
        }
        minutes = lingua_services.input_minutes(learner, start=start, end=end)
        if not days and not minutes:
            return {}
        return {SUBJECT: {"days": days, "minutes": minutes}}
