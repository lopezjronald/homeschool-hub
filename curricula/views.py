from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from core.permissions import viewable_queryset, editable_queryset, user_can_edit
from core.utils import get_active_family

from .models import Curriculum
from .forms import CurriculumForm


@login_required
def curriculum_list(request):
    """Display list of curricula the user can view."""
    curricula = viewable_queryset(Curriculum.objects.all(), request.user)
    can_edit = user_can_edit(request.user)
    return render(request, "curricula/curriculum_list.html", {
        "curricula": curricula,
        "can_edit": can_edit,
    })


@login_required
def curriculum_create(request):
    """Create a new curriculum (editors only)."""
    if not user_can_edit(request.user):
        from django.http import Http404
        raise Http404

    if request.method == "POST":
        form = CurriculumForm(request.POST)
        if form.is_valid():
            curriculum = form.save(commit=False)
            curriculum.parent = request.user
            curriculum.family = get_active_family(request.user)
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
    curriculum = get_object_or_404(viewable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    can_edit = user_can_edit(request.user)
    return render(request, "curricula/curriculum_detail.html", {
        "curriculum": curriculum,
        "can_edit": can_edit,
    })


@login_required
def curriculum_update(request, pk):
    """Edit an existing curriculum (editors only)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)

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
    """Delete a curriculum with confirmation (editors only)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
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
