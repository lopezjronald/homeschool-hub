from collections import defaultdict
from datetime import timedelta
from itertools import groupby
from operator import attrgetter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

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
    """A print-ready charter report: the work-log record PLUS finalized mastery
    and a mastery-over-time trend, for a date range and (optionally) one child.

    View access is enough (teachers/grandparents too) — this is the artifact a
    charter Educational Specialist reads. Print to PDF from the browser.
    """
    from tutor.models import MasteryAssessment
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
        .order_by("child__first_name", "child__last_name", "child_id", "date", "created_at")
    )
    if selected_child:
        entries = entries.filter(child=selected_child)
    entries = list(entries)

    # Finalized mastery in the range, keyed by child (assessments scope through
    # the same work-log entries, so they inherit the family scoping).
    assessments = list(
        MasteryAssessment.objects.filter(
            work_entry__in=scoped_queryset(WorkLogEntry.objects.all(), request.user, family),
            status=MasteryAssessment.FINALIZED,
            work_entry__date__range=(start, end),
        ).select_related("work_entry", "work_entry__child").order_by("work_entry__date")
    )
    if selected_child:
        assessments = [a for a in assessments if a.work_entry.child_id == selected_child.id]

    entries_by_child = defaultdict(list)
    for e in entries:
        entries_by_child[e.child_id].append(e)
    assess_by_child = defaultdict(list)
    for a in assessments:
        assess_by_child[a.work_entry.child_id].append(a)

    child_ids = list(dict.fromkeys([e.child_id for e in entries] + [a.work_entry.child_id for a in assessments]))
    children = {}
    for e in entries:
        children.setdefault(e.child_id, e.child)
    for a in assessments:
        children.setdefault(a.work_entry.child_id, a.work_entry.child)

    groups = []
    for cid in child_ids:
        child_entries = entries_by_child.get(cid, [])
        child_assess = assess_by_child.get(cid, [])
        groups.append({
            "child": children[cid],
            "entries": child_entries,
            "count": len(child_entries),
            "day_count": len({e.date for e in child_entries}),
            "subjects": sorted({e.subject for e in child_entries}),
            "assessments": child_assess,
            "trends": [s for s in mastery_series(child_assess) if s["count"] >= 2],
        })

    return render(request, "worklog/charter_report.html", {
        "form": form,
        "groups": groups,
        "start": start,
        "end": end,
        "selected_child": selected_child,
        "total_entries": len(entries),
        "total_days": len({e.date for e in entries}),
        "family": family,
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
