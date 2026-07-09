from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.db.models import Q
from django.db.models.functions import Greatest
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from core.permissions import viewable_queryset, editable_queryset, scoped_queryset, user_can_edit
from core.utils import get_active_family, get_selected_family
from students.models import Student

from .blueprints import BLUEPRINTS
from .forms import ApplyBlueprintForm, CurriculumDocumentForm, CurriculumForm, CurriculumResourceForm
from .models import Curriculum, CurriculumPlacement, Lesson
from .services import apply_blueprint, get_blueprint
from .subjects import emoji_for


def _fuzzy_search(qs, q):
    """Misspelling-tolerant search over name/subject.

    On Postgres, pg_trgm similarity lets "Dimensios Math" still find
    "Dimensions Math 3A"; exact substring matches always qualify too, and
    results order by similarity. On SQLite (dev/tests) it degrades to the
    plain icontains filter. Row counts are tiny, so no GIN index needed yet.
    """
    contains = Q(name__icontains=q) | Q(subject__icontains=q)
    if connection.vendor != "postgresql":
        return qs.filter(contains)
    from django.contrib.postgres.search import TrigramSimilarity

    return (
        qs.annotate(sim=Greatest(TrigramSimilarity("name", q), TrigramSimilarity("subject", q)))
        .filter(contains | Q(sim__gt=0.25))
        .order_by("-sim", "subject", "name")
    )


@login_required
def curriculum_list(request):
    """Filterable, searchable, tiled list of curricula the user can view."""
    family = get_selected_family(request)
    base = scoped_queryset(Curriculum.objects.all(), request.user, family)

    subject = request.GET.get("subject", "").strip()
    grade = request.GET.get("grade", "").strip()
    q = request.GET.get("q", "").strip()

    curricula = base
    if subject:
        curricula = curricula.filter(subject__iexact=subject)
    if grade:
        curricula = curricula.filter(grade_level=grade)
    if q:
        curricula = _fuzzy_search(curricula, q)

    curricula = list(curricula)
    for c in curricula:
        c.emoji = emoji_for(c.subject)

    # Facets derived from the full scoped set (so options don't vanish mid-filter).
    subjects = sorted({s for s in base.values_list("subject", flat=True) if s})
    present_grades = set(base.exclude(grade_level="").values_list("grade_level", flat=True))
    grade_choices = [(v, label) for v, label in Curriculum.GRADE_CHOICES if v in present_grades]

    return render(request, "curricula/curriculum_list.html", {
        "curricula": curricula,
        "can_edit": user_can_edit(request.user),
        "subjects": subjects,
        "grade_choices": grade_choices,
        "active_subject": subject,
        "active_grade": grade,
        "q": q,
        "has_filters": bool(subject or grade or q),
        "total_count": base.count(),
    })


@login_required
def curriculum_create(request):
    """Create a new curriculum (editors only)."""
    if not user_can_edit(request.user):
        raise Http404

    if request.method == "POST":
        form = CurriculumForm(request.POST)
        if form.is_valid():
            curriculum = form.save(commit=False)
            curriculum.parent = request.user
            curriculum.family = get_active_family(request.user)
            curriculum.save()
            messages.success(request, f'Curriculum "{curriculum.name}" has been created.')
            return redirect("curricula:curriculum_detail", pk=curriculum.pk)
    else:
        form = CurriculumForm()

    return render(
        request, "curricula/curriculum_form.html", {"form": form, "action": "Create"}
    )


def _curriculum_students(user, curriculum):
    """Children the user may view that belong to this curriculum's context."""
    students = viewable_queryset(Student.objects.all(), user)
    if curriculum.family_id:
        return students.filter(family_id=curriculum.family_id)
    return students.filter(family__isnull=True)


@login_required
def curriculum_detail(request, pk):
    """Curriculum detail: structure (chapters/lessons), documents, and progress."""
    curriculum = get_object_or_404(viewable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    can_edit = user_can_edit(request.user)

    chapters = curriculum.chapters.prefetch_related("lessons", "lessons__materials")
    documents = curriculum.documents.all()
    resources = curriculum.resources.all()
    ordered_lessons = list(
        Lesson.objects.filter(chapter__curriculum=curriculum)
        .select_related("chapter")
        .order_by("chapter__number", "order")
    )

    students = _curriculum_students(request.user, curriculum)
    placements = {
        p.child_id: p
        for p in CurriculumPlacement.objects.filter(
            curriculum=curriculum, child__in=students,
        ).select_related("current_lesson")
    }
    child_rows = []
    for child in students:
        placement = placements.get(child.id)
        child_rows.append({
            "child": child,
            "placement": placement,
            "progress": placement.progress() if placement else None,
            "next": placement.next_lesson() if placement else None,
        })

    return render(request, "curricula/curriculum_detail.html", {
        "curriculum": curriculum,
        "can_edit": can_edit,
        "chapters": chapters,
        "documents": documents,
        "resources": resources,
        "ordered_lessons": ordered_lessons,
        "child_rows": child_rows,
        "apply_form": ApplyBlueprintForm() if can_edit else None,
        "doc_form": CurriculumDocumentForm() if can_edit else None,
        "resource_form": CurriculumResourceForm() if can_edit else None,
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
            return redirect("curricula:curriculum_detail", pk=curriculum.pk)
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


@login_required
@require_POST
def curriculum_apply_blueprint(request, pk):
    """Populate a curriculum's chapters/lessons from a built-in blueprint (editors)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    form = ApplyBlueprintForm(request.POST)
    if form.is_valid():
        blueprint = get_blueprint(form.cleaned_data["blueprint"])
        if blueprint:
            chapters, lessons = apply_blueprint(curriculum, blueprint)
            messages.success(
                request,
                f"Loaded {blueprint['name']}: {chapters} chapters and {lessons} lessons.",
            )
    else:
        messages.error(request, "Please choose a valid curriculum blueprint.")
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)


@login_required
@require_POST
def curriculum_document_add(request, pk):
    """Attach a source document to a curriculum (editors)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    form = CurriculumDocumentForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.curriculum = curriculum
        doc.uploaded_by = request.user
        doc.save()
        messages.success(request, f'Added document "{doc.title}".')
    else:
        messages.error(request, "Could not add the document. Please check the file and try again.")
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)


@login_required
@require_POST
def curriculum_document_delete(request, pk, doc_pk):
    """Delete a curriculum document (editors)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    doc = get_object_or_404(curriculum.documents, pk=doc_pk)
    title = doc.title
    if doc.file:
        doc.file.delete(save=False)
    doc.delete()
    messages.success(request, f'Removed document "{title}".')
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)


@login_required
@require_POST
def curriculum_resource_add(request, pk):
    """Add an external resource link to a curriculum (editors)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    form = CurriculumResourceForm(request.POST)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.curriculum = curriculum
        resource.save()
        messages.success(request, f'Added resource "{resource.label}".')
    else:
        messages.error(request, "Could not add the resource. Please check the link and try again.")
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)


@login_required
@require_POST
def curriculum_resource_delete(request, pk, resource_pk):
    """Delete a curriculum resource link (editors)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    resource = get_object_or_404(curriculum.resources, pk=resource_pk)
    label = resource.label
    resource.delete()
    messages.success(request, f'Removed resource "{label}".')
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)


@login_required
@require_POST
def curriculum_set_placement(request, pk, child_pk):
    """Set a child's current lesson in this curriculum (editors)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    child = get_object_or_404(_curriculum_students(request.user, curriculum), pk=child_pk)

    lesson_id = request.POST.get("current_lesson")
    lesson = None
    if lesson_id:
        lesson = get_object_or_404(
            Lesson.objects.filter(chapter__curriculum=curriculum), pk=lesson_id,
        )

    CurriculumPlacement.objects.update_or_create(
        child=child, curriculum=curriculum,
        defaults={"current_lesson": lesson},
    )
    messages.success(request, f"Updated {child.get_full_name()}'s progress.")
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)
