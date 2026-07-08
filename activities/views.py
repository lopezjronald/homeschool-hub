"""Parent-side management of external activities (School of Rock, CodaKid, …)."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.permissions import editable_queryset, scoped_queryset, user_can_edit
from core.utils import get_active_family, get_selected_family
from students.models import Student
from worklog.models import WorkLogEntry

from .forms import ExternalActivityForm
from .models import ExternalActivity


@login_required
@require_POST
def activity_checkin(request, pk):
    """Handle a check-in nudge: log it (→ WorkLogEntry), snooze, or mute."""
    activity = get_object_or_404(
        editable_queryset(ExternalActivity.objects.all(), request.user), pk=pk,
    )
    action = request.POST.get("action")
    today = timezone.localdate()

    if action == "log":
        # Idempotent for the day: a double-click must not duplicate entries.
        if activity.last_logged_at == today:
            messages.info(request, f"{activity.display_label} is already logged today.")
            return redirect("home")
        # One WorkLogEntry per child: the tagged child, or every child in this
        # family. A null-family activity falls back to the owner's own
        # null-family children so the fan-out can never reach another family.
        if activity.student:
            children = [activity.student]
        elif activity.family_id:
            children = list(Student.objects.filter(family=activity.family))
        else:
            children = list(Student.objects.filter(parent=activity.parent, family__isnull=True))
        for child in children:
            WorkLogEntry.objects.create(
                parent=request.user, family=activity.family, child=child,
                subject=activity.title[:100],  # WorkLogEntry.subject caps at 100
                description=f"{activity.display_label} — logged from the activity check-in.",
                date=today,
            )
        activity.last_logged_at = today
        activity.snoozed_until = None
        activity.save(update_fields=["last_logged_at", "snoozed_until", "updated_at"])
        messages.success(request, f"Logged {activity.display_label}. 🎉")
    elif action == "snooze":
        activity.snoozed_until = today + timedelta(days=1)
        activity.save(update_fields=["snoozed_until", "updated_at"])
        messages.info(request, f"Snoozed {activity.display_label} until tomorrow.")
    elif action == "mute":
        activity.is_muted = True
        activity.save(update_fields=["is_muted", "updated_at"])
        messages.info(request, f"Muted reminders for {activity.display_label}.")

    # The check-in card only ever lives on the home hub, so home is the only
    # redirect target — no caller-supplied `next` (which would be an open redirect).
    return redirect("home")


@login_required
def activity_list(request):
    """All of the selected family's activities, grouped by child vs family-wide."""
    family = get_selected_family(request)
    activities = scoped_queryset(ExternalActivity.objects.all(), request.user, family).select_related("student")
    return render(request, "activities/activity_list.html", {
        "activities": activities,
        "can_edit": user_can_edit(request.user),
    })


@login_required
def activity_create(request):
    if not user_can_edit(request.user):
        raise Http404
    family = get_selected_family(request)
    if request.method == "POST":
        form = ExternalActivityForm(request.POST, user=request.user, family=family)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.parent = request.user
            activity.family = get_active_family(request.user)
            activity.save()
            messages.success(request, "Activity added.")
            return redirect("activities:activity_list")
    else:
        form = ExternalActivityForm(user=request.user, family=family)
    return render(request, "activities/activity_form.html", {"form": form, "action": "Add"})


@login_required
def activity_update(request, pk):
    if not user_can_edit(request.user):
        raise Http404
    activity = get_object_or_404(
        editable_queryset(ExternalActivity.objects.all(), request.user), pk=pk,
    )
    family = get_selected_family(request)
    if request.method == "POST":
        form = ExternalActivityForm(request.POST, instance=activity, user=request.user, family=family)
        if form.is_valid():
            form.save()
            messages.success(request, "Activity updated.")
            return redirect("activities:activity_list")
    else:
        form = ExternalActivityForm(instance=activity, user=request.user, family=family)
    return render(request, "activities/activity_form.html", {"form": form, "activity": activity, "action": "Edit"})


@login_required
def activity_delete(request, pk):
    if not user_can_edit(request.user):
        raise Http404
    activity = get_object_or_404(
        editable_queryset(ExternalActivity.objects.all(), request.user), pk=pk,
    )
    if request.method == "POST":
        activity.delete()
        messages.success(request, "Activity removed.")
        return redirect("activities:activity_list")
    return render(request, "activities/activity_confirm_delete.html", {"activity": activity})
