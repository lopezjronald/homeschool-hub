from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Curriculum
from .forms import CurriculumForm


def get_curriculum_for_user(user, pk):
    """Get a curriculum owned by the given user, or 404."""
    return get_object_or_404(Curriculum, pk=pk, parent=user)


@login_required
def curriculum_list(request):
    """Display list of curricula for the logged-in parent."""
    curricula = Curriculum.objects.filter(parent=request.user)
    return render(request, "curricula/curriculum_list.html", {"curricula": curricula})


@login_required
def curriculum_create(request):
    """Create a new curriculum."""
    if request.method == "POST":
        form = CurriculumForm(request.POST)
        if form.is_valid():
            curriculum = form.save(commit=False)
            curriculum.parent = request.user
            curriculum.save()
            messages.success(request, f'Curriculum "{curriculum.name}" has been created.')
            return redirect("curricula:curriculum_list")
    else:
        form = CurriculumForm()

    return render(
        request, "curricula/curriculum_form.html", {"form": form, "action": "Create"}
    )


@login_required
def curriculum_detail(request, pk):
    """View details of a single curriculum."""
    curriculum = get_curriculum_for_user(request.user, pk)
    return render(request, "curricula/curriculum_detail.html", {"curriculum": curriculum})


@login_required
def curriculum_update(request, pk):
    """Edit an existing curriculum."""
    curriculum = get_curriculum_for_user(request.user, pk)

    if request.method == "POST":
        form = CurriculumForm(request.POST, instance=curriculum)
        if form.is_valid():
            form.save()
            messages.success(request, f'Curriculum "{curriculum.name}" has been updated.')
            return redirect("curricula:curriculum_list")
    else:
        form = CurriculumForm(instance=curriculum)

    return render(
        request,
        "curricula/curriculum_form.html",
        {"form": form, "curriculum": curriculum, "action": "Edit"},
    )


@login_required
def curriculum_delete(request, pk):
    """Delete a curriculum with confirmation."""
    curriculum = get_curriculum_for_user(request.user, pk)
    assignment_count = curriculum.get_related_assignments_count()

    if request.method == "POST":
        name = curriculum.name
        curriculum.delete()
        messages.success(request, f'Curriculum "{name}" has been deleted.')
        return redirect("curricula:curriculum_list")

    return render(
        request,
        "curricula/curriculum_confirm_delete.html",
        {"curriculum": curriculum, "assignment_count": assignment_count},
    )
