from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.db.models import ProtectedError, Q
from django.db.models.functions import Greatest
from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from core.permissions import (
    viewable_queryset, editable_queryset, scoped_queryset, user_can_edit,
    can_edit_family_or_global,
)
from core.utils import get_active_family, get_selected_family, resolve_family_for_write
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
    show_deactivated = request.GET.get("show_deactivated") == "1"

    subject = request.GET.get("subject", "").strip()
    grade = request.GET.get("grade", "").strip()
    q = request.GET.get("q", "").strip()

    # "Show deactivated" now means "show everything that is switched off", which
    # covers both the waiting shelf and the archive — the template groups them.
    curricula = base if show_deactivated else base.filter(is_active=True)
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
    facet_base = base if show_deactivated else base.filter(is_active=True)
    subjects = sorted({s for s in facet_base.values_list("subject", flat=True) if s})
    present_grades = set(facet_base.exclude(grade_level="").values_list("grade_level", flat=True))
    grade_choices = [(v, label) for v, label in Curriculum.GRADE_CHOICES if v in present_grades]
    deactivated_count = base.filter(is_active=False).count()
    # Split the switched-off ones so the shelf reads at a glance: what is still
    # coming vs what is behind us.
    in_use = [c for c in curricula if c.state == Curriculum.STATE_IN_USE]
    ready = [c for c in curricula if c.state == Curriculum.STATE_READY]
    archived = [c for c in curricula if c.state == Curriculum.STATE_ARCHIVED]

    return render(request, "curricula/curriculum_list.html", {
        "curricula": curricula,
        "in_use": in_use,
        "ready_to_start": ready,
        "archived": archived,
        "ready_count": base.filter(is_active=False, archived_at__isnull=True).count(),
        "archived_count": base.filter(is_active=False, archived_at__isnull=False).count(),
        # Gate the Add/edit controls on the SELECTED family (global content falls back
        # to the global edit right), not on "can edit somewhere" — closes the leak
        # where a viewer of the selected family saw edit controls.
        "can_edit": can_edit_family_or_global(request.user, family),
        "subjects": subjects,
        "grade_choices": grade_choices,
        "active_subject": subject,
        "active_grade": grade,
        "q": q,
        "has_filters": bool(subject or grade or q or show_deactivated),
        "total_count": facet_base.count(),
        "show_deactivated": show_deactivated,
        "deactivated_count": deactivated_count,
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
            curriculum.family = resolve_family_for_write(request)
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
    # Gate edit controls on THIS curriculum's family (global content → global right).
    can_edit = can_edit_family_or_global(request.user, curriculum.family)

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
        try:
            curriculum.delete()
        except ProtectedError as err:
            # Assignment.curriculum is on_delete=PROTECT, so a curriculum with linked
            # assignments can't be deleted — name what's blocking instead of 500-ing.
            kinds = sorted({
                str(obj._meta.verbose_name_plural).lower()
                for obj in err.protected_objects
            })
            what = ", ".join(kinds) if kinds else "related records"
            messages.error(
                request,
                f'"{name}" can\'t be deleted yet because it still has {what}. '
                f"Remove those first, then try again.",
            )
            return redirect("curricula:curriculum_detail", pk=curriculum.pk)
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


@login_required
@require_POST
def curriculum_toggle_active(request, pk):
    """Turn a curriculum on or off for the girls (HH-149).

    Switching ON always clears any archive stamp: a course you have deliberately
    picked back up is in use, not finished.
    """
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    curriculum.is_active = not curriculum.is_active
    # Curriculum.save() drops archived_at on the way on, so the off branch can
    # never be reached with a stale stamp still attached.
    curriculum.save(update_fields=["is_active", "updated_at"])
    if curriculum.is_active:
        messages.success(request, f'"{curriculum.name}" is in use again — the girls can see it.')
    else:
        messages.success(
            request,
            f'"{curriculum.name}" is turned off and waiting. Nothing is lost — switch it '
            f'back on whenever she\'s ready.',
        )
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)


@login_required
@require_POST
def curriculum_toggle_archived(request, pk):
    """Retire a finished course, or bring it back to the waiting shelf.

    Archiving is deliberately NOT the same as turning off. Both hide the course,
    but only one of them means "we're done with this" — without the distinction a
    shelf of switched-off courses can't tell you what is still coming.
    """
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    if curriculum.archived_at:
        curriculum.archived_at = None
        curriculum.save(update_fields=["archived_at", "updated_at"])
        messages.success(
            request,
            f'"{curriculum.name}" moved back to Ready to start. Turn it on when she is.',
        )
    else:
        curriculum.archived_at = timezone.now()
        curriculum.is_active = False
        curriculum.save(update_fields=["archived_at", "is_active", "updated_at"])
        messages.success(request, f'"{curriculum.name}" archived — finished and filed away.')
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)


@login_required
@require_POST
def curriculum_toggle_placement_active(request, pk, child_pk):
    """Turn a subject on/off for one child without deleting the placement (HH-149)."""
    curriculum = get_object_or_404(editable_queryset(Curriculum.objects.all(), request.user), pk=pk)
    child = get_object_or_404(_curriculum_students(request.user, curriculum), pk=child_pk)
    # The button reads "Show on portal" when there is no placement yet, so CREATING
    # one has to mean shown. Toggling unconditionally made the first click create it
    # active and immediately flip it off — the parent pressed "Show" and was told it
    # was hidden, and had to press twice.
    placement, created = CurriculumPlacement.objects.get_or_create(
        child=child, curriculum=curriculum, defaults={"is_active": True},
    )
    if not created:
        placement.is_active = not placement.is_active
        placement.save(update_fields=["is_active", "updated_at"])
    if placement.is_active:
        messages.success(request, f"{child.first_name} can see {curriculum.name} again.")
    else:
        messages.success(
            request,
            f"{curriculum.name} hidden from {child.first_name}'s portal.",
        )
    return redirect("curricula:curriculum_detail", pk=curriculum.pk)
