from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.permissions import editable_queryset, user_can_edit, viewable_queryset
from worklog.models import WorkLogEntry

from . import ai, mastery
from .forms import AssessmentRequestForm, FinalizeForm
from .models import MasteryAssessment


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
            try:
                result = ai.grade_work(
                    rubric=form.cleaned_data["rubric"],
                    answers=form.cleaned_data["answers"],
                    grade_level=entry.child.get_grade_level_display(),
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
        form = AssessmentRequestForm(initial={"answers": entry.description})

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
