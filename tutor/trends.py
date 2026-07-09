"""Mastery-over-time: turn a child's finalized assessments into a per-subject
series of points for a small inline-SVG sparkline (no charting library)."""

from collections import defaultdict

from . import mastery

# Hex colors per level for SVG fills (the Bootstrap badge classes don't help SVG).
LEVEL_COLOR = {
    mastery.NO_EVIDENCE: "#6c757d",
    mastery.BEGINNING: "#dc3545",
    mastery.DEVELOPING: "#f0ad4e",
    mastery.PROFICIENT: "#0dcaf0",
    mastery.MASTERED: "#198754",
}
_LABELS = dict(mastery.CHOICES)


def mastery_series(assessments, width=260, height=64, pad=12):
    """Group finalized assessments by subject and lay out sparkline points.

    ``assessments`` is any iterable of MasteryAssessment; only those with an
    effective level are plotted, oldest→newest. Returns a list of dicts:
    {subject, points:[{x,y,level,label,color,date}], polyline, latest, count}.
    y maps mastery rank (no_evidence…mastered) to bottom…top.
    """
    by_subject = defaultdict(list)
    for a in assessments:
        if a.effective_level:
            by_subject[a.work_entry.subject or "—"].append(a)

    top_rank = len(mastery.LEVELS) - 1  # 4
    series = []
    for subject, items in by_subject.items():
        items.sort(key=lambda a: (a.finalized_at or a.created_at))
        n = len(items)
        points = []
        for i, a in enumerate(items):
            level = a.effective_level
            r = mastery.rank(level)
            x = pad if n == 1 else pad + (width - 2 * pad) * i / (n - 1)
            y = height - pad - (height - 2 * pad) * (r / top_rank if top_rank else 0)
            points.append({
                "x": round(x, 1),
                "y": round(y, 1),
                "level": level,
                "label": _LABELS.get(level, level),
                "color": LEVEL_COLOR.get(level, "#6c757d"),
                "date": a.finalized_at or a.created_at,
            })
        series.append({
            "subject": subject,
            "points": points,
            "polyline": " ".join(f"{p['x']},{p['y']}" for p in points),
            "latest": points[-1] if points else None,
            "count": n,
            "width": width,
            "height": height,
        })
    series.sort(key=lambda s: s["subject"])
    return series
