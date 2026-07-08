from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from itertools import groupby

from core.permissions import editable_queryset, user_can_edit, viewable_queryset
from curricula.models import Curriculum
from worklog.models import WorkLogEntry

from . import ai, mastery
from .forms import AssessmentRequestForm, FinalizeForm
from .models import MasteryAssessment, Material, QuestionSet


@login_required
def assess_create(request, entry_pk):
    """Grade a work log entry against a rubric (editors only)."""
    if not user_can_edit(request.user):
        raise Http404
    entry = get_object_or_404(
        editable_queryset(WorkLogEntry.objects.all(), request.user), pk=entry_pk,
    )

    if request.method == "POST":
        form = AssessmentRequestForm(request.POST)
        if form.is_valid():
            # Judge at the curriculum's academic grade when the work links one;
            # otherwise fall back to the child's school Level.
            if entry.curriculum and entry.curriculum.grade_level:
                grade_context = entry.curriculum.get_grade_level_display()
            else:
                grade_context = entry.child.get_grade_level_display()
            try:
                result = ai.grade_work(
                    rubric=form.cleaned_data["rubric"],
                    answers=form.cleaned_data["answers"],
                    grade_level=grade_context,
                    subject=entry.subject,
                )
            except ai.GraderNotConfigured:
                messages.error(
                    request,
                    "AI grading isn't set up yet. Add an ANTHROPIC_API_KEY to enable it.",
                )
                return redirect("worklog:worklog_detail", pk=entry.pk)
            except ai.GraderError as exc:
                messages.error(request, f"The AI grader couldn't complete: {exc}")
                return render(request, "tutor/assess_form.html", {"form": form, "entry": entry})

            assessment = MasteryAssessment.objects.create(
                work_entry=entry,
                graded_by=request.user,
                rubric=form.cleaned_data["rubric"],
                answers=form.cleaned_data["answers"],
                ai_level=result["level"],
                ai_summary=result["summary"],
                ai_criteria=result["criteria"],
                ai_encouragement=result["encouragement"],
            )
            messages.success(request, "Draft assessment ready — review and finalize.")
            return redirect("tutor:assess_detail", pk=assessment.pk)
    else:
        initial = {"answers": entry.description}
        # If this entry came from a portal response sheet, prefill the question
        # set's own rubric (e.g. Blackbird's) and the formatted Q&A.
        sheet = entry.response_sheets.select_related("question_set").first()
        if sheet:
            rubric = sheet.question_set.rubric or ""
            if sheet.question_set.answer_key:
                rubric = (rubric + "\n\n---\n### Reference answers (for grading only)\n"
                          + sheet.question_set.answer_key).strip()
            if rubric:
                initial["rubric"] = rubric
            initial["answers"] = sheet.as_worklog_text()
        form = AssessmentRequestForm(initial=initial)

    return render(request, "tutor/assess_form.html", {
        "form": form,
        "entry": entry,
        "configured": ai.is_configured(),
    })


@login_required
def assess_detail(request, pk):
    """View an assessment; editors can finalize (with an optional override)."""
    assessment = get_object_or_404(
        MasteryAssessment.objects.filter(
            work_entry__in=viewable_queryset(WorkLogEntry.objects.all(), request.user),
        ).select_related("work_entry", "work_entry__child"),
        pk=pk,
    )
    can_edit = user_can_edit(request.user)
    finalize_form = FinalizeForm(
        initial={"final_level": assessment.effective_level or mastery.PROFICIENT},
    ) if can_edit and assessment.status == MasteryAssessment.DRAFT else None

    return render(request, "tutor/assess_detail.html", {
        "assessment": assessment,
        "can_edit": can_edit,
        "finalize_form": finalize_form,
        "levels": mastery.CHOICES,
    })


@login_required
@require_POST
def assess_finalize(request, pk):
    """Finalize an assessment with the parent's decision (editors only)."""
    assessment = get_object_or_404(
        MasteryAssessment.objects.filter(
            work_entry__in=editable_queryset(WorkLogEntry.objects.all(), request.user),
        ),
        pk=pk,
    )
    form = FinalizeForm(request.POST)
    if form.is_valid():
        chosen = form.cleaned_data["final_level"]
        if chosen != assessment.ai_level:
            assessment.parent_override_level = chosen
        assessment.final_level = chosen
        assessment.status = MasteryAssessment.FINALIZED
        assessment.finalized_at = timezone.now()
        assessment.save()
        messages.success(request, "Assessment finalized.")
    else:
        messages.error(request, "Please choose a valid mastery level.")
    return redirect("tutor:assess_detail", pk=assessment.pk)


def _materials_for(user, editable=False):
    """Materials whose curriculum the user can view (or edit)."""
    scope = editable_queryset if editable else viewable_queryset
    curricula = scope(Curriculum.objects.all(), user)
    return Material.objects.filter(lesson__chapter__curriculum__in=curricula)


@login_required
def discussion_guide(request, curriculum_pk):
    """Teacher-facing discussion guide: the oral, Socratic sets for a curriculum.

    These sets are never shown to the student — they're for the parent/teacher to
    lead a discussion. Grouped by section, with each question's facilitation hint.
    """
    curriculum = get_object_or_404(
        viewable_queryset(Curriculum.objects.all(), request.user), pk=curriculum_pk,
    )
    sets = (
        QuestionSet.objects.filter(
            lesson__chapter__curriculum=curriculum, mode=QuestionSet.MODE_DISCUSSION,
        )
        .prefetch_related("questions")
        .select_related("lesson", "lesson__chapter")
        .order_by("lesson__chapter__number", "lesson__order", "id")
    )
    groups = [
        {"heading": chapter_title, "sets": list(items)}
        for (_num, chapter_title), items in groupby(
            sets, key=lambda s: (s.lesson.chapter.number, s.lesson.chapter.title),
        )
    ]
    return render(request, "tutor/discussion_guide.html", {
        "curriculum": curriculum,
        "groups": groups,
    })


@login_required
def material_detail(request, pk):
    """Show a lesson material (both layers) to the parent."""
    material = get_object_or_404(
        _materials_for(request.user).select_related("lesson", "lesson__chapter", "child"),
        pk=pk,
    )
    return render(request, "tutor/material_detail.html", {
        "material": material,
        "can_edit": user_can_edit(request.user),
    })


@login_required
@require_POST
def material_approve(request, pk):
    """Approve a draft material so it becomes visible to the student (editors)."""
    material = get_object_or_404(_materials_for(request.user, editable=True), pk=pk)
    if material.status == Material.DRAFT:
        material.status = Material.APPROVED
        material.approved_at = timezone.now()
        material.save(update_fields=["status", "approved_at", "updated_at"])
        messages.success(request, f'"{material.title}" is approved and ready for the student.')
    return redirect("tutor:material_detail", pk=material.pk)
