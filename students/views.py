from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from core.permissions import viewable_queryset, editable_queryset, user_can_edit
from core.utils import get_active_family

from .models import Student
from .forms import StudentForm


@login_required
def student_list(request):
    """Display list of children the user can view (via family membership)."""
    students = viewable_queryset(Student.objects.all(), request.user)
    can_edit = user_can_edit(request.user)
    return render(request, "students/student_list.html", {
        "students": students,
        "can_edit": can_edit,
    })


@login_required
def student_create(request):
    """Create a new child profile (editors only)."""
    if not user_can_edit(request.user):
        from django.http import Http404
        raise Http404

    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.parent = request.user
            student.family = get_active_family(request.user)
            student.save()
            messages.success(request, f"{student.first_name} has been added.")
            return redirect("students:student_list")
    else:
        form = StudentForm()

    return render(request, "students/student_form.html", {"form": form, "action": "Add"})


@login_required
def student_detail(request, pk):
    """View details of a single child."""
    student = get_object_or_404(viewable_queryset(Student.objects.all(), request.user), pk=pk)
    can_edit = user_can_edit(request.user)
    return render(request, "students/student_detail.html", {
        "student": student,
        "can_edit": can_edit,
    })


@login_required
def student_update(request, pk):
    """Edit an existing child profile (editors only)."""
    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"{student.first_name}'s profile has been updated.")
            return redirect("students:student_list")
    else:
        form = StudentForm(instance=student)

    return render(
        request, "students/student_form.html", {"form": form, "student": student, "action": "Edit"}
    )


@login_required
def student_delete(request, pk):
    """Delete a child profile with confirmation (editors only)."""
    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)

    if request.method == "POST":
        name = student.first_name
        student.delete()
        messages.success(request, f"{name}'s profile has been deleted.")
        return redirect("students:student_list")

    return render(request, "students/student_confirm_delete.html", {"student": student})
