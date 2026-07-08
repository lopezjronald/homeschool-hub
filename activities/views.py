"""Parent-side management of external activities (School of Rock, CodaKid, …)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import editable_queryset, scoped_queryset, user_can_edit
from core.utils import get_active_family, get_selected_family

from .forms import ExternalActivityForm
from .models import ExternalActivity


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
