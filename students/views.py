from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Student
from .forms import StudentForm


def get_student_for_user(user, pk):
    """Get a student owned by the given user, or 404."""
    return get_object_or_404(Student, pk=pk, parent=user)


@login_required
def student_list(request):
    """Display list of children for the logged-in parent."""
    students = Student.objects.filter(parent=request.user)
    return render(request, "students/student_list.html", {"students": students})


@login_required
def student_create(request):
    """Create a new child profile."""
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.parent = request.user
            student.save()
            messages.success(request, f"{student.first_name} has been added.")
            return redirect("students:student_list")
    else:
        form = StudentForm()

    return render(request, "students/student_form.html", {"form": form, "action": "Add"})


@login_required
def student_detail(request, pk):
    """View details of a single child."""
    student = get_student_for_user(request.user, pk)
    return render(request, "students/student_detail.html", {"student": student})


@login_required
def student_update(request, pk):
    """Edit an existing child profile."""
    student = get_student_for_user(request.user, pk)

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
    """Delete a child profile with confirmation."""
    student = get_student_for_user(request.user, pk)

    if request.method == "POST":
        name = student.first_name
        student.delete()
        messages.success(request, f"{name}'s profile has been deleted.")
        return redirect("students:student_list")

    return render(request, "students/student_confirm_delete.html", {"student": student})
