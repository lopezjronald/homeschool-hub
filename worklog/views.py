from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import (
    editable_queryset,
    scoped_queryset,
    user_can_edit,
    viewable_queryset,
)
from core.utils import get_active_family, get_selected_family

from .forms import WorkLogEntryForm
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
