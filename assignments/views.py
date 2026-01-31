from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from core.models import FamilyMembership
from core.permissions import viewable_queryset, editable_queryset, scoped_queryset, user_can_edit
from core.utils import get_active_family, get_selected_family
from curricula.models import Curriculum
from students.models import Student

from .forms import AssignmentForm, AssignmentStatusForm, ResourceLinkForm
from .models import Assignment, AssignmentResourceLink


def _user_editable_assignments(user):
    """Return assignments the user can edit.

    Parents/admins: all assignments in their editable families + legacy.
    Teachers: only their own teacher-created assignments in viewable families.
    """
    if user_can_edit(user):
        return editable_queryset(Assignment.objects.all(), user)
    return viewable_queryset(
        Assignment.objects.filter(
            source=Assignment.SOURCE_TEACHER, created_by=user,
        ),
        user,
    )


@login_required
def assignment_list(request):
    family = get_selected_family(request)
    assignments = scoped_queryset(
        Assignment.objects.all(), request.user, family,
    ).select_related("child", "curriculum")
    is_parent_or_admin = user_can_edit(request.user)
    can_create = is_parent_or_admin or family is not None
    return render(
        request,
        "assignments/assignment_list.html",
        {
            "assignments": assignments,
            "can_create": can_create,
            "is_parent_or_admin": is_parent_or_admin,
        },
    )


@login_required
def assignment_create(request):
    family = get_selected_family(request)
    is_parent_or_admin = user_can_edit(request.user)

    # Allow parents/admins OR teachers with a selected family
    if not is_parent_or_admin and family is None:
        raise Http404

    # Check if user has accessible children and curricula
    if is_parent_or_admin:
        has_children = editable_queryset(Student.objects.all(), request.user).exists()
        has_curricula = editable_queryset(Curriculum.objects.all(), request.user).exists()
    else:
        has_children = scoped_queryset(Student.objects.all(), request.user, family).exists()
        has_curricula = scoped_queryset(Curriculum.objects.all(), request.user, family).exists()

    if not has_children or not has_curricula:
        return render(
            request,
            "assignments/assignment_form.html",
            {
                "action": "Create",
                "has_children": has_children,
                "has_curricula": has_curricula,
                "empty_state": True,
                "is_parent_or_admin": is_parent_or_admin,
            },
        )

    if request.method == "POST":
        form = AssignmentForm(request.POST, user=request.user, family=family)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user

            if is_parent_or_admin:
                assignment.parent = request.user
                assignment.family = get_active_family(request.user)
                assignment.source = Assignment.SOURCE_PARENT
            else:
                # Teacher: set parent to family's first parent member
                family_parent_id = (
                    FamilyMembership.objects
                    .filter(family=family, role="parent")
                    .values_list("user_id", flat=True)
                    .first()
                )
                if family_parent_id is None:
                    raise Http404
                assignment.parent_id = family_parent_id
                assignment.family = family
                assignment.source = Assignment.SOURCE_TEACHER

            assignment.save()
            messages.success(request, f"Assignment '{assignment.title}' created.")
            return redirect("assignments:assignment_list")
    else:
        form = AssignmentForm(user=request.user, family=family)

    return render(
        request,
        "assignments/assignment_form.html",
        {"form": form, "action": "Create"},
    )


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(
        viewable_queryset(
            Assignment.objects.all(), request.user,
        ).select_related("created_by"),
        pk=pk,
    )
    is_parent_or_admin = user_can_edit(request.user)
    is_own_teacher_assignment = (
        assignment.source == Assignment.SOURCE_TEACHER
        and assignment.created_by == request.user
    )
    can_edit = is_parent_or_admin or is_own_teacher_assignment
    can_delete = is_parent_or_admin
    resource_form = ResourceLinkForm() if can_edit else None
    assessment_links = assignment.resource_links.filter(
        link_type=AssignmentResourceLink.TYPE_ASSESSMENT,
    )
    resource_links = assignment.resource_links.filter(
        link_type=AssignmentResourceLink.TYPE_RESOURCE,
    )
    return render(
        request,
        "assignments/assignment_detail.html",
        {
            "assignment": assignment,
            "resource_form": resource_form,
            "can_edit": can_edit,
            "can_delete": can_delete,
            "assessment_links": assessment_links,
            "resource_links": resource_links,
        },
    )


@login_required
def assignment_update(request, pk):
    assignment = get_object_or_404(_user_editable_assignments(request.user), pk=pk)
    family = get_selected_family(request)

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment, user=request.user, family=family)
        if form.is_valid():
            form.save()
            messages.success(request, f"Assignment '{assignment.title}' updated.")
            return redirect("assignments:assignment_list")
    else:
        form = AssignmentForm(instance=assignment, user=request.user, family=family)

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

    assessment_links = assignment.resource_links.filter(
        link_type=AssignmentResourceLink.TYPE_ASSESSMENT,
    )
    resource_links = assignment.resource_links.filter(
        link_type=AssignmentResourceLink.TYPE_RESOURCE,
    )
    return render(
        request,
        "assignments/assignment_student_update.html",
        {
            "assignment": assignment,
            "form": form,
            "assessment_links": assessment_links,
            "resource_links": resource_links,
        },
    )


@login_required
def resource_link_add(request, pk):
    """Add a resource link to an assignment (editors only)."""
    assignment = get_object_or_404(_user_editable_assignments(request.user), pk=pk)

    if request.method == "POST":
        form = ResourceLinkForm(request.POST)
        if form.is_valid():
            AssignmentResourceLink.objects.create(
                assignment=assignment,
                url=form.cleaned_data["url"],
                label=form.cleaned_data["label"],
                link_type=form.cleaned_data["link_type"],
                window_start=form.cleaned_data.get("window_start"),
                window_end=form.cleaned_data.get("window_end"),
            )
            messages.success(request, "Link added.")
    return redirect("assignments:assignment_detail", pk=pk)


@login_required
def resource_link_delete(request, link_pk):
    """Delete a resource link (editors only)."""
    link = get_object_or_404(
        AssignmentResourceLink.objects.filter(
            assignment__in=_user_editable_assignments(request.user)
        ),
        pk=link_pk,
    )
    assignment_pk = link.assignment.pk

    if request.method == "POST":
        link.delete()
        messages.success(request, "Resource link removed.")
    return redirect("assignments:assignment_detail", pk=assignment_pk)
