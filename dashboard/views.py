from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.dateparse import parse_date

from core.permissions import scoped_queryset
from core.utils import get_selected_family
from curricula.models import CurriculumPlacement
from curricula.subjects import emoji_for
from students.models import Student
from tutor import mastery
from tutor.models import MasteryAssessment
from worklog.models import WorkLogEntry


@login_required
def dashboard_view(request):
    """Progress: the real signals for each child.

    Re-pointed off the legacy Assignment model onto what actually flows through
    the app — per-subject curriculum placement progress, recent Work Log
    activity, and finalized mastery levels.
    """
    family = get_selected_family(request)

    # Validate GET params so a malformed URL can't 500 the page.
    child_id = request.GET.get("child_id", "").strip()
    if not child_id.isdigit():
        child_id = ""
    start = parse_date(request.GET.get("start_date", "").strip()) or None
    end = parse_date(request.GET.get("end_date", "").strip()) or None
    start_date = start.isoformat() if start else ""   # echoed back to the form
    end_date = end.isoformat() if end else ""
    has_filters = any([child_id, start_date, end_date])

    all_children = scoped_queryset(
        Student.objects.all(), request.user, family,
    ).order_by("first_name")
    children = all_children.filter(id=child_id) if child_id else all_children

    worklog = scoped_queryset(WorkLogEntry.objects.all(), request.user, family)
    if start:
        worklog = worklog.filter(date__gte=start)
    if end:
        worklog = worklog.filter(date__lte=end)

    child_cards = []
    for child in children:
        placements = (
            CurriculumPlacement.objects.filter(child=child)
            .select_related("curriculum", "current_lesson", "current_lesson__chapter")
        )
        subjects = [
            {
                "curriculum": p.curriculum,
                "emoji": emoji_for(p.curriculum.subject),
                "progress": p.progress(),
                "current_lesson": p.current_lesson,
            }
            for p in placements
        ]

        entries = (
            worklog.filter(child=child)
            .select_related("curriculum")
            .order_by("-date", "-created_at")
        )

        # Only finalized levels count — a parent-reviewed judgment, never a
        # raw AI draft (whose effective_level would otherwise inflate mastery).
        assessments = MasteryAssessment.objects.filter(
            work_entry__child=child, status=MasteryAssessment.FINALIZED,
        )
        if start:
            assessments = assessments.filter(work_entry__date__gte=start)
        if end:
            assessments = assessments.filter(work_entry__date__lte=end)
        assessments = assessments.select_related("work_entry", "lesson").order_by("-created_at")
        levels = [a.effective_level for a in assessments if a.effective_level]

        child_cards.append({
            "child": child,
            "subjects": subjects,
            "worklog_count": entries.count(),
            "last_entry": entries.first(),
            "recent_entries": list(entries[:5]),
            "assessed_count": len(levels),
            "meets_bar_count": sum(1 for lvl in levels if mastery.meets_bar(lvl)),
            # Only the levels actually present, most-advanced first, with badges.
            "mastery_counts": [
                {"level": lvl, "label": label, "count": levels.count(lvl),
                 "badge": mastery.BADGE.get(lvl, "bg-secondary")}
                for lvl, label in reversed(mastery.CHOICES) if levels.count(lvl)
            ],
            "recent_assessments": list(assessments[:4]),
        })

    summary = {
        "children": len(child_cards),
        "subjects": sum(len(c["subjects"]) for c in child_cards),
        "worklog_count": sum(c["worklog_count"] for c in child_cards),
        "assessed": sum(c["assessed_count"] for c in child_cards),
        "meets_bar": sum(c["meets_bar_count"] for c in child_cards),
    }

    return render(request, "dashboard/dashboard.html", {
        "child_cards": child_cards,
        "summary": summary,
        "children": all_children,
        "selected_child": child_id,
        "start_date": start_date,
        "end_date": end_date,
        "has_filters": has_filters,
        "today": date.today(),
    })
