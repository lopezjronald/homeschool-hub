import csv
import os
from collections import OrderedDict, defaultdict
from datetime import timedelta
from itertools import groupby
from operator import attrgetter
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.permissions import (
    editable_queryset,
    scoped_queryset,
    user_can_edit,
    viewable_queryset,
)
from core.utils import get_active_family, get_selected_family

from .forms import WorkLogEntryForm, WorkLogReportForm
from .models import WorkLogEntry


@login_required
def worklog_list(request):
    """List work log entries the user can view, scoped to the selected family."""
    family = get_selected_family(request)
    entries = scoped_queryset(
        WorkLogEntry.objects.all(), request.user, family,
    ).select_related("child", "curriculum")
    return render(request, "worklog/worklog_list.html", {
        "entries": entries,
        "can_edit": user_can_edit(request.user),
    })


@login_required
def worklog_report(request):
    """Date-range completion report of logged work, grouped by child.

    Available to anyone with view access to the family (teachers and
    grandparents included) — the record a charter Educational Specialist or
    reviewing teacher can read and print. Defaults to the last 30 days.
    """
    family = get_selected_family(request)

    today = timezone.localdate()
    start = today - timedelta(days=29)
    end = today
    selected_child = None

    if request.GET:
        form = WorkLogReportForm(request.GET, user=request.user, family=family)
        if form.is_valid():
            start = form.cleaned_data.get("start") or start
            end = form.cleaned_data.get("end") or end
            selected_child = form.cleaned_data.get("child")
    else:
        form = WorkLogReportForm(
            user=request.user, family=family, initial={"start": start, "end": end},
        )

    entries = (
        scoped_queryset(WorkLogEntry.objects.all(), request.user, family)
        .filter(date__range=(start, end))
        .select_related("child", "curriculum")
        .order_by("child__first_name", "child__last_name", "child_id", "-date", "-created_at")
    )
    if selected_child:
        entries = entries.filter(child=selected_child)

    entries = list(entries)
    groups = []
    for _child_id, items in groupby(entries, key=attrgetter("child_id")):
        items = list(items)
        groups.append({
            "child": items[0].child,
            "entries": items,
            "count": len(items),
            "day_count": len({e.date for e in items}),
            "subjects": sorted({e.subject for e in items}),
        })

    return render(request, "worklog/worklog_report.html", {
        "form": form,
        "groups": groups,
        "start": start,
        "end": end,
        "selected_child": selected_child,
        "total_entries": len(entries),
        "total_days": len({e.date for e in entries}),
        "family": family,
    })


@login_required
def charter_report(request):
    """A polished, print-ready report of a child's submitted SAMPLE WORK in a
    date range — each piece shown with the AI's SUGGESTED mastery level and the
    parent's STAMPED level (which the parent can apply inline).

    View access is enough to read it (teachers/grandparents too); stamping a
    grade requires edit rights. Print to PDF from the browser, or download the
    grade summary as CSV (``?format=csv``).
    """
    from tutor import mastery
    from tutor.models import MasteryAssessment, ResponseSheet
    from tutor.trends import mastery_series

    family = get_selected_family(request)
    today = timezone.localdate()
    start = today - timedelta(days=29)
    end = today
    selected_child = None

    if request.GET:
        form = WorkLogReportForm(request.GET, user=request.user, family=family)
        if form.is_valid():
            start = form.cleaned_data.get("start") or start
            end = form.cleaned_data.get("end") or end
            selected_child = form.cleaned_data.get("child")
    else:
        form = WorkLogReportForm(
            user=request.user, family=family, initial={"start": start, "end": end},
        )

    entries = (
        scoped_queryset(WorkLogEntry.objects.all(), request.user, family)
        .filter(date__range=(start, end))
        .select_related("child", "curriculum")
        .prefetch_related(
            Prefetch(
                "response_sheets",
                queryset=ResponseSheet.objects.select_related("question_set")
                .prefetch_related("question_set__questions"),
            ),
            Prefetch("assessments", queryset=MasteryAssessment.objects.select_related("lesson")),
        )
        .order_by("child__first_name", "child__last_name", "child_id", "date", "created_at")
    )
    if selected_child:
        entries = entries.filter(child=selected_child)
    entries = list(entries)

    items = [_report_item(e, mastery) for e in entries]

    if request.GET.get("format") == "csv":
        return _report_csv(items, start, end)

    # Group items by child, preserving the queryset order.
    by_child = OrderedDict()
    for it in items:
        by_child.setdefault(it["entry"].child_id, {"child": it["entry"].child, "items": []})
        by_child[it["entry"].child_id]["items"].append(it)

    groups = []
    for _cid, g in by_child.items():
        g_items = g["items"]
        finalized = [it["assessment"] for it in g_items if it["stamped"]]
        graded = sum(1 for it in g_items if it["stamped"])
        groups.append({
            "child": g["child"],
            "items": g_items,
            "count": len(g_items),
            "day_count": len({it["entry"].date for it in g_items}),
            "subjects": sorted({it["entry"].subject for it in g_items}),
            "graded_count": graded,
            "ungraded_count": len(g_items) - graded,
            "dist": _distribution(g_items, mastery),
            "trends": [s for s in mastery_series(finalized) if s["count"] >= 2],
        })

    return render(request, "worklog/charter_report.html", {
        "form": form,
        "groups": groups,
        "start": start,
        "end": end,
        "selected_child": selected_child,
        "total_entries": len(entries),
        "total_days": len({e.date for e in entries}),
        "total_ungraded": sum(g["ungraded_count"] for g in groups),
        "levels": mastery.CHOICES,
        "family": family,
        "today": today,
        "can_edit": user_can_edit(request.user),
        "csv_qs": _preserved_get_qs(request, extra={"format": "csv"}),
    })


def _report_item(entry, mastery):
    """View-model for one work-log entry: its sample work + AI/parent grade."""
    from tutor.models import MasteryAssessment

    sheets = list(entry.response_sheets.all())
    sheet = sheets[0] if sheets else None
    assessments = list(entry.assessments.all())
    a = assessments[0] if assessments else None

    qa_rows = []
    if sheet:
        for q in sheet.question_set.questions.all():
            display = sheet.answer_display(q)
            qa_rows.append({
                "question": q,
                "answer": display,
                "answered": display not in ("", "(no answer)"),
            })

    ext = os.path.splitext(entry.attachment.name)[1].lower() if entry.attachment else ""
    show_image = bool(entry.attachment) and entry.is_image and ext != ".heic"
    kind = "portal" if sheet else ("image" if show_image else ("file" if entry.attachment else "note"))
    stamped = bool(a and a.final_level and a.status == MasteryAssessment.FINALIZED)

    return {
        "entry": entry,
        "title": sheet.question_set.title if sheet else (
            entry.curriculum.name if entry.curriculum else entry.subject),
        "kind": kind,
        "show_image": show_image,
        "sheet": sheet,
        "qa_rows": qa_rows,
        "assessment": a,
        "has_ai": bool(a and a.ai_level),
        "stamped": stamped,
        "finalize_default": a.effective_level if (a and a.effective_level) else mastery.PROFICIENT,
        "can_ai_grade_link": bool(sheet and not a),
    }


def _distribution(items, mastery):
    """Counts of STAMPED final levels, for the overview strip (official record)."""
    counts = OrderedDict((lvl, 0) for lvl, _ in mastery.CHOICES)
    for it in items:
        a = it["assessment"]
        if it["stamped"] and a and a.final_level in counts:
            counts[a.final_level] += 1
    labels = dict(mastery.CHOICES)
    return [
        {"level": lvl, "label": labels[lvl], "n": n, "badge": mastery.BADGE.get(lvl, "bg-secondary")}
        for lvl, n in counts.items() if n
    ]


def _report_csv(items, start, end):
    """A grade-summary spreadsheet for the same items (stdlib csv, no deps)."""
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = (
        'attachment; filename="charter-report-%s_to_%s.csv"' % (start.isoformat(), end.isoformat())
    )
    writer = csv.writer(resp)
    writer.writerow(["Date", "Child", "Subject", "Lesson", "AI level", "Final level", "Status"])
    for it in items:
        e = it["entry"]
        a = it["assessment"]
        writer.writerow([
            e.date.isoformat(),
            e.child.get_full_name() or e.child.first_name,
            e.subject,
            it["sheet"].question_set.title if it["sheet"] else (e.curriculum.name if e.curriculum else ""),
            a.get_ai_level_display() if (a and a.ai_level) else "",
            a.get_final_level_display() if (a and a.final_level) else "",
            "Finalized" if it["stamped"] else ("Draft" if a else "Not graded"),
        ])
    return resp


def _preserved_get_qs(request, extra=None):
    """Re-encode the report's child/start/end GET filters (+ any extra)."""
    params = {k: request.GET[k] for k in ("child", "start", "end") if request.GET.get(k)}
    if extra:
        params.update(extra)
    return urlencode(params)


@login_required
@require_POST
def report_stamp(request, entry_pk):
    """Stamp (finalize) the parent's mastery grade for one work entry, straight
    from the report. Reuses tutor.forms.FinalizeForm. Creates the assessment if
    none exists yet (photo/manual work, or a submission whose AI grading never
    ran). Edit rights required (others get a 404). Returns to the report with
    the same child/date filters preserved.
    """
    from tutor.forms import FinalizeForm
    from tutor.models import MasteryAssessment

    entry = get_object_or_404(
        editable_queryset(WorkLogEntry.objects.all(), request.user), pk=entry_pk,
    )
    form = FinalizeForm(request.POST)
    if form.is_valid():
        chosen = form.cleaned_data["final_level"]
        assessments = list(entry.assessments.all())
        a = assessments[0] if assessments else None
        now = timezone.now()
        if a:
            if a.ai_level and chosen != a.ai_level:
                a.parent_override_level = chosen
            a.final_level = chosen
            a.status = MasteryAssessment.FINALIZED
            a.finalized_at = now
            a.save()
        else:
            sheets = list(entry.response_sheets.all())
            sheet = sheets[0] if sheets else None
            MasteryAssessment.objects.create(
                work_entry=entry,
                graded_by=request.user,
                rubric=(sheet.question_set.rubric if sheet else "Parent stamp"),
                answers=(sheet.as_worklog_text() if sheet else (entry.description or "(work on file)")),
                ai_level="",
                final_level=chosen,
                status=MasteryAssessment.FINALIZED,
                finalized_at=now,
            )
        messages.success(request, "Grade saved.")
    else:
        messages.error(request, "Please choose a mastery level.")

    params = {k: request.POST[k] for k in ("child", "start", "end") if request.POST.get(k)}
    url = reverse("worklog:charter_report")
    if params:
        url += "?" + urlencode(params)
    return redirect(url)


def sample_report(request):
    """A static, demo-data charter report — the payoff, shown before any setup.

    Linked from the Work Log / Progress empty states (and How-it-works) so a new
    or prospective parent can see exactly what the record they're building looks
    like. No real data, no login required.
    """
    today = timezone.localdate()

    def d(days_ago):
        return today - timedelta(days=days_ago)

    groups = [{
        "name": "Sample Scholar",
        "level": "3rd grade",
        "count": 6,
        "day_count": 5,
        "subjects": ["Literature", "Math", "Writing"],
        "assessments": [
            {"date": d(2), "subject": "Literature", "level": "Proficient", "badge": "bg-success"},
            {"date": d(9), "subject": "Math", "level": "Developing", "badge": "bg-warning text-dark"},
            {"date": d(16), "subject": "Writing", "level": "Mastered", "badge": "bg-primary"},
        ],
        "entries": [
            {"date": d(2), "subject": "Literature", "description": "Read Ch. 4 of “A Mouse Called Wolf” and answered the comprehension set — strong on character motivation."},
            {"date": d(4), "subject": "Math", "description": "Saxon Lesson 42: multi-digit addition with regrouping. Needed a nudge on carrying the tens."},
            {"date": d(9), "subject": "Writing", "description": "Drafted a paragraph about our weekend hike; revised for a stronger topic sentence with the writing coach."},
            {"date": d(11), "subject": "Math", "description": "Beast Academy online — measurement puzzles. Finished the chapter check."},
            {"date": d(16), "subject": "Literature", "description": "Vocabulary matching for Ch. 5 — matched all ten words on the second try."},
        ],
    }]

    return render(request, "worklog/sample_report.html", {
        "groups": groups,
        "start": d(29),
        "end": today,
        "total_entries": 6,
        "total_days": 5,
        "today": today,
    })


@login_required
def worklog_create(request):
    """Log a new piece of work (editors only)."""
    if not user_can_edit(request.user):
        raise Http404

    family = get_selected_family(request)
    if request.method == "POST":
        form = WorkLogEntryForm(
            request.POST, request.FILES, user=request.user, family=family,
        )
        if form.is_valid():
            entry = form.save(commit=False)
            entry.parent = request.user
            entry.created_by = request.user
            entry.family = get_active_family(request.user)
            entry.save()
            messages.success(request, "Work log entry saved.")
            return redirect("worklog:worklog_detail", pk=entry.pk)
    else:
        form = WorkLogEntryForm(user=request.user, family=family)

    return render(request, "worklog/worklog_form.html", {"form": form, "action": "Log"})


@login_required
def worklog_detail(request, pk):
    """View a single work log entry."""
    entry = get_object_or_404(
        viewable_queryset(WorkLogEntry.objects.all(), request.user).select_related(
            "child", "curriculum", "created_by",
        ),
        pk=pk,
    )
    return render(request, "worklog/worklog_detail.html", {
        "entry": entry,
        "can_edit": user_can_edit(request.user),
    })


@login_required
def worklog_update(request, pk):
    """Edit a work log entry (editors only)."""
    entry = get_object_or_404(
        editable_queryset(WorkLogEntry.objects.all(), request.user), pk=pk,
    )
    family = get_selected_family(request)
    if request.method == "POST":
        form = WorkLogEntryForm(
            request.POST, request.FILES, instance=entry, user=request.user, family=family,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Work log entry updated.")
            return redirect("worklog:worklog_detail", pk=entry.pk)
    else:
        form = WorkLogEntryForm(instance=entry, user=request.user, family=family)

    return render(
        request,
        "worklog/worklog_form.html",
        {"form": form, "entry": entry, "action": "Edit"},
    )


@login_required
def worklog_delete(request, pk):
    """Delete a work log entry with confirmation (editors only)."""
    entry = get_object_or_404(
        editable_queryset(WorkLogEntry.objects.all(), request.user), pk=pk,
    )
    if request.method == "POST":
        entry.delete()
        messages.success(request, "Work log entry deleted.")
        return redirect("worklog:worklog_list")

    return render(request, "worklog/worklog_confirm_delete.html", {"entry": entry})
