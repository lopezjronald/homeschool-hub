from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import viewable_queryset, editable_queryset, user_can_edit
from core.utils import get_active_family
from curricula.models import Curriculum
from students.models import Student

from .forms import AssignmentForm, AssignmentStatusForm, ResourceLinkForm
from .models import Assignment, AssignmentResourceLink


@login_required
def assignment_list(request):
    assignments = viewable_queryset(
        Assignment.objects.all(), request.user,
    ).select_related("child", "curriculum")
    can_edit = user_can_edit(request.user)
    return render(
        request,
        "assignments/assignment_list.html",
        {"assignments": assignments, "can_edit": can_edit},
    )


@login_required
def assignment_create(request):
    if not user_can_edit(request.user):
        raise Http404

    # Check if user has children and curricula they can edit
    has_children = editable_queryset(Student.objects.all(), request.user).exists()
    has_curricula = editable_queryset(Curriculum.objects.all(), request.user).exists()

    if not has_children or not has_curricula:
        return render(
            request,
            "assignments/assignment_form.html",
            {
                "action": "Create",
                "has_children": has_children,
                "has_curricula": has_curricula,
                "empty_state": True,
            },
        )

    if request.method == "POST":
        form = AssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.parent = request.user
            assignment.family = get_active_family(request.user)
            assignment.save()
            messages.success(request, f"Assignment '{assignment.title}' created.")
            return redirect("assignments:assignment_list")
    else:
        form = AssignmentForm(user=request.user)

    return render(
        request,
        "assignments/assignment_form.html",
        {"form": form, "action": "Create"},
    )


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(
        viewable_queryset(Assignment.objects.all(), request.user), pk=pk,
    )
    can_edit = user_can_edit(request.user)
    resource_form = ResourceLinkForm() if can_edit else None
    return render(
        request,
        "assignments/assignment_detail.html",
        {"assignment": assignment, "resource_form": resource_form, "can_edit": can_edit},
    )


@login_required
def assignment_update(request, pk):
    assignment = get_object_or_404(
        editable_queryset(Assignment.objects.all(), request.user), pk=pk,
    )

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Assignment '{assignment.title}' updated.")
            return redirect("assignments:assignment_list")
    else:
        form = AssignmentForm(instance=assignment, user=request.user)

    return render(
        request,
        "assignments/assignment_form.html",
        {"form": form, "action": "Edit", "assignment": assignment},
    )


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(
        editable_queryset(Assignment.objects.all(), request.user), pk=pk,
    )

    if request.method == "POST":
        title = assignment.title
        assignment.delete()
        messages.success(request, f"Assignment '{title}' deleted.")
        return redirect("assignments:assignment_list")

    return render(
        request,
        "assignments/assignment_confirm_delete.html",
        {"assignment": assignment},
    )


def assignment_student_update(request, token):
    """
    Allow students to update assignment status via signed magic link.
    No login required. Token expires after 7 days.
    """
    assignment = Assignment.get_from_student_token(token)

    if assignment is None:
        return render(
            request,
            "assignments/assignment_student_update.html",
            {"error": "This link is invalid or has expired."},
        )

    if request.method == "POST":
        form = AssignmentStatusForm(request.POST)
        if form.is_valid():
            assignment.status = form.cleaned_data["status"]
            assignment.save()
            return render(
                request,
                "assignments/assignment_student_update.html",
                {"assignment": assignment, "success": True},
            )
    else:
        form = AssignmentStatusForm(initial={"status": assignment.status})

    return render(
        request,
        "assignments/assignment_student_update.html",
        {"assignment": assignment, "form": form},
    )


@login_required
def resource_link_add(request, pk):
    """Add a resource link to an assignment (editors only)."""
    assignment = get_object_or_404(
        editable_queryset(Assignment.objects.all(), request.user), pk=pk,
    )

    if request.method == "POST":
        form = ResourceLinkForm(request.POST)
        if form.is_valid():
            AssignmentResourceLink.objects.create(
                assignment=assignment,
                url=form.cleaned_data["url"],
                label=form.cleaned_data.get("label", ""),
            )
            messages.success(request, "Resource link added.")
    return redirect("assignments:assignment_detail", pk=pk)


@login_required
def resource_link_delete(request, link_pk):
    """Delete a resource link (editors only)."""
    link = get_object_or_404(
        AssignmentResourceLink.objects.filter(
            assignment__in=editable_queryset(Assignment.objects.all(), request.user)
        ),
        pk=link_pk,
    )
    assignment_pk = link.assignment.pk

    if request.method == "POST":
        link.delete()
        messages.success(request, "Resource link removed.")
    return redirect("assignments:assignment_detail", pk=assignment_pk)
