from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from itertools import groupby

from core.permissions import (
    editable_queryset, user_can_edit, viewable_queryset, can_edit_family_or_global,
)
from curricula.models import Curriculum, CurriculumPlacement
from worklog.models import WorkLogEntry

from . import ai, grading, mastery, spend
from .forms import AssessmentRequestForm, FinalizeForm
from .models import MasteryAssessment, Material, QuestionSet, ResponseSheet


def _entry_objectives(entry):
    """Lesson objectives for a work-log entry, when it came from a portal sheet.

    Gives the grader concept context on the parent-initiated path (the portal
    auto-grader already passes objectives). Returns "" when there's no linked lesson.
    """
    sheet = entry.response_sheets.select_related("question_set__lesson").first()
    if sheet and sheet.question_set.lesson_id:
        return sheet.question_set.lesson.objectives or ""
    return ""


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
            if not ai.is_configured():
                messages.error(
                    request,
                    "AI grading isn't set up yet. Add an ANTHROPIC_API_KEY to enable it.",
                )
                return redirect("worklog:worklog_detail", pk=entry.pk)
            # Refuse here rather than letting the background grade fail: this is the
            # only point in the flow where someone is looking at a page and can be
            # told why. Past this line the parent gets a pending spinner (HH-145).
            if spend.budget_exceeded():
                messages.error(request, spend.refusal_message())
                return redirect("worklog:worklog_detail", pk=entry.pk)
            # Already graded (e.g. the portal auto-grader beat us here)? Go to it.
            existing = MasteryAssessment.objects.filter(work_entry=entry).first()
            if existing:
                return redirect("tutor:assess_detail", pk=existing.pk)
            # Judge at the curriculum's academic grade when the work links one;
            # otherwise fall back to the child's school Level.
            if entry.curriculum and entry.curriculum.grade_level:
                grade_context = entry.curriculum.get_grade_level_display()
            else:
                grade_context = entry.child.get_grade_level_display()
            # Grade OFF the request path — grading can take longer than Heroku's
            # hard 30s cap under load, which used to H12 ("Application error").
            # The pending page polls and lands the parent on the draft when ready.
            grading.start_manual_grade(
                entry.pk,
                rubric=form.cleaned_data["rubric"],
                answers=form.cleaned_data["answers"],
                grade_level=grade_context,
                subject=entry.subject,
                objectives=_entry_objectives(entry),
                graded_by_id=request.user.pk,
            )
            return redirect("tutor:assess_pending", entry_pk=entry.pk)
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
def assess_pending(request, entry_pk):
    """Waiting page shown while a parent-initiated grade runs in the background.

    Grading was moved off the request path so it can't hit Heroku's 30s cap; this
    page polls ``assess_status`` and forwards to the draft as soon as it's saved.
    """
    if not user_can_edit(request.user):
        raise Http404
    entry = get_object_or_404(
        editable_queryset(WorkLogEntry.objects.all(), request.user), pk=entry_pk,
    )
    assessment = MasteryAssessment.objects.filter(work_entry=entry).first()
    if assessment:
        return redirect("tutor:assess_detail", pk=assessment.pk)
    return render(request, "tutor/assess_pending.html", {
        "entry": entry,
        "configured": ai.is_configured(),
    })


@login_required
def assess_status(request, entry_pk):
    """Poll target for the pending page: has the background grade saved yet?"""
    if not user_can_edit(request.user):
        raise Http404
    entry = get_object_or_404(
        editable_queryset(WorkLogEntry.objects.all(), request.user), pk=entry_pk,
    )
    assessment = MasteryAssessment.objects.filter(work_entry=entry).first()
    if assessment:
        return JsonResponse({
            "ready": True,
            "url": reverse("tutor:assess_detail", kwargs={"pk": assessment.pk}),
        })
    # `grading: false` is what the template turns into a legible message instead of
    # a spinner. The ceiling can be crossed between the create-time check and the
    # background thread, and that grade dies inside a broad except — without this,
    # the parent watches "Still working…" for 150s and is then told to try again.
    return JsonResponse({
        "ready": False,
        "grading": ai.is_configured() and not spend.budget_exceeded(),
    })


@login_required
def assessment_list(request):
    """Grading history: every assessment for the family's children.

    Drafts awaiting review float to the top; finalized results read as a
    chronological history. Optional per-child filter feeds from Progress.
    """
    entries = viewable_queryset(WorkLogEntry.objects.all(), request.user)
    qs = (
        MasteryAssessment.objects.filter(work_entry__in=entries)
        .select_related("work_entry", "work_entry__child", "work_entry__curriculum")
        .order_by("-created_at")
    )

    child_id = request.GET.get("child_id", "").strip()
    if child_id.isdigit():
        qs = qs.filter(work_entry__child_id=child_id)

    assessments = list(qs)
    drafts = [a for a in assessments if a.status == MasteryAssessment.DRAFT]
    finalized = [a for a in assessments if a.status == MasteryAssessment.FINALIZED]

    from students.models import Student

    children = Student.objects.filter(
        work_log_entries__in=entries,
    ).distinct().order_by("first_name")

    return render(request, "tutor/assessment_list.html", {
        "drafts": drafts,
        "finalized": finalized,
        "children": children,
        "selected_child": child_id,
        "meets_bar_count": sum(1 for a in finalized if a.meets_bar),
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
    can_edit = can_edit_family_or_global(
        request.user, getattr(assessment.work_entry, "family", None),
    )
    finalize_form = FinalizeForm(
        initial={"final_level": assessment.effective_level or mastery.PROFICIENT},
    ) if can_edit and assessment.status == MasteryAssessment.DRAFT else None

    return render(request, "tutor/assess_detail.html", {
        "assessment": assessment,
        "can_edit": can_edit,
        "finalize_form": finalize_form,
        "levels": mastery.CHOICES,
        "work": _assessed_work(assessment),
        "child": getattr(assessment.work_entry, "child", None),
    })


def _assessed_work(assessment):
    """The child's ACTUAL work, question by question — not a transcript of it.

    `assessment.answers` is a plain-text snapshot taken at grading time. It is
    the right thing to send a model and the wrong thing to show a parent: a
    drawing arrives as "[a drawing — 4 pen stroke(s)]" and a marked-up sentence
    as a sentence about marks. The parent is being asked to judge the work, so
    they should be looking at the work.

    Returns None when the assessment has no sheet behind it — a rubric typed
    straight into the manual grading form has no questions to show, and the
    stored snapshot is then all there is.
    """
    entry = assessment.work_entry
    # Scoped to the entry's own child as well as the entry. Nothing today can
    # attach two sheets to one entry, but `.first()` orders by -updated_at, so
    # if anything ever could, this page would render one child's answers under
    # another child's name.
    sheet = (entry.response_sheets
             .filter(child_id=entry.child_id)
             .select_related("question_set")
             .prefetch_related("question_set__questions")
             .first()) if entry else None
    if sheet is None:
        return None
    rows = []
    for question in sheet.question_set.questions.all():
        shown = sheet.answer_display(question)
        rows.append({
            "question": question,
            "answer": shown,
            "answered": shown not in ("", "(no answer)", "(nothing drawn yet)",
                                      "(nothing written yet)"),
            "replay": sheet.answer_replay(question),
        })
    return {"sheet": sheet, "rows": rows}


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
def lexicon_guide(request, curriculum_pk):
    """Parent guide for Operation Lexicon — the booklet's own front matter.

    The printed guide opens with how to run the unit; the app swallowed that,
    leaving the parent to infer the method from the child's pages. It also says
    plainly which of the guide's materials this version still needs (the ten
    books) and which it has taken over (the poster, the coloured pencils).
    """
    from students.models import Student
    from tutor import lexicon

    curriculum = get_object_or_404(
        viewable_queryset(Curriculum.objects.all(), request.user), pk=curriculum_pk,
    )
    if curriculum.name != lexicon.CURRICULUM_NAME:
        raise Http404

    children = []
    for placement in CurriculumPlacement.objects.filter(
        curriculum=curriculum,
        child__in=viewable_queryset(Student.objects.all(), request.user),
    ).select_related("child"):
        done = set(
            ResponseSheet.objects.filter(
                child=placement.child,
                question_set__lesson__chapter__curriculum=curriculum,
                status=ResponseSheet.SUBMITTED,
            ).values_list("question_set__lesson__number", flat=True)
        )
        children.append({
            "child": placement.child,
            "weeks_done": len(done),
            "words": len(done) * 10,
            "next_week": next(
                (w for w in lexicon.WEEKS if w["number"] not in done), None),
        })

    return render(request, "tutor/lexicon_guide.html", {
        "curriculum": curriculum,
        "epigraph": lexicon.EPIGRAPH,
        "why": lexicon.WHY_IT_EXISTS,
        "how_to_proceed": lexicon.HOW_TO_PROCEED,
        "materials": lexicon.MATERIALS,
        "weeks": lexicon.WEEKS,
        "children": children,
    })


@login_required
def dickinson_guide(request, curriculum_pk):
    """Parent guide for Operation Lexicon: Emily Dickinson.

    Same reason as the guide above: the booklet opens by explaining how a week
    runs, and the app was swallowing that and leaving the parent to infer the
    method from Kaylin's pages. This one also has to say which portions she
    writes by hand and why, because that is the guide's actual pedagogy rather
    than a preference of ours.
    """
    from students.models import Student
    from tutor import dickinson
    from tutor.management.commands.seed_lexicon_kaylin import WRITTEN_BY_HAND

    curriculum = get_object_or_404(
        viewable_queryset(Curriculum.objects.all(), request.user), pk=curriculum_pk,
    )
    if curriculum.name != dickinson.CURRICULUM_NAME:
        raise Http404

    children = []
    for placement in CurriculumPlacement.objects.filter(
        curriculum=curriculum,
        child__in=viewable_queryset(Student.objects.all(), request.user),
    ).select_related("child"):
        # A week counts as done when all three of its days are turned in — one
        # day in is progress, not a finished week.
        by_week = {}
        for number, set_pk in ResponseSheet.objects.filter(
            child=placement.child,
            question_set__lesson__chapter__curriculum=curriculum,
            status=ResponseSheet.SUBMITTED,
        ).values_list("question_set__lesson__number", "question_set_id"):
            by_week.setdefault(number, set()).add(set_pk)
        done = {n for n, sets in by_week.items() if len(sets) >= 3}
        children.append({
            "child": placement.child,
            "weeks_done": len(done),
            "days_done": sum(len(s) for s in by_week.values()),
            "words": len(done) * 4,
            "next_week": next(
                (w for w in dickinson.WEEKS if w["number"] not in done), None),
        })

    return render(request, "tutor/dickinson_guide.html", {
        "curriculum": curriculum,
        "epigraph": dickinson.EPIGRAPH,
        "why": dickinson.WHY_IT_EXISTS,
        "how_a_day_runs": dickinson.HOW_A_DAY_RUNS,
        "starters": dickinson.STORY_STARTERS,
        "weeks": dickinson.WEEKS,
        "by_hand": WRITTEN_BY_HAND,
        "children": children,
    })

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
    _cur = getattr(getattr(getattr(material, "lesson", None), "chapter", None), "curriculum", None)
    return render(request, "tutor/material_detail.html", {
        "material": material,
        "can_edit": can_edit_family_or_global(request.user, getattr(_cur, "family", None)),
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


@login_required
def onetrue_guide(request, curriculum_pk):
    """Parent guide for One True Sentence: Tools of Style.

    The book's "For the Teacher" page plus its Sentence Construction Basics —
    the reference the weekly lessons quietly assume you already know, and which
    a parent otherwise has to reconstruct from Violet's answers.
    """
    from students.models import Student
    from tutor import onetrue
    from tutor.management.commands.seed_onetrue_violet import WRITTEN_BY_HAND

    curriculum = get_object_or_404(
        viewable_queryset(Curriculum.objects.all(), request.user), pk=curriculum_pk,
    )
    if curriculum.name != onetrue.CURRICULUM_NAME:
        raise Http404

    children = []
    for placement in CurriculumPlacement.objects.filter(
        curriculum=curriculum,
        child__in=viewable_queryset(Student.objects.all(), request.user),
    ).select_related("child"):
        # A week is the lesson AND the practice — one of the two is half a week.
        by_week = {}
        for number, set_pk in ResponseSheet.objects.filter(
            child=placement.child,
            question_set__lesson__chapter__curriculum=curriculum,
            status=ResponseSheet.SUBMITTED,
        ).values_list("question_set__lesson__number", "question_set_id"):
            by_week.setdefault(number, set()).add(set_pk)
        done = {n for n, sets in by_week.items() if len(sets) >= 2}
        children.append({
            "child": placement.child,
            "weeks_done": len(done),
            "sets_done": sum(len(s) for s in by_week.values()),
            "next_week": next(
                (w for w in onetrue.WEEKS if w["number"] not in done), None),
        })

    return render(request, "tutor/onetrue_guide.html", {
        "curriculum": curriculum,
        "epigraph": onetrue.EPIGRAPH,
        "for_the_teacher": onetrue.FOR_THE_TEACHER,
        "how_it_teaches": onetrue.HOW_IT_TEACHES,
        "basics": onetrue.BASICS,
        "weeks": onetrue.WEEKS,
        "by_hand": WRITTEN_BY_HAND,
        "children": children,
    })


@login_required
def poetry_guide(request, curriculum_pk):
    """Parent guide for Poetry: Small Forms.

    The one page that shows all twelve forms at a glance — pattern, totals,
    progress — and says how the method runs and where the original pages live.
    """
    from students.models import Student
    from tutor import poetry

    curriculum = get_object_or_404(
        viewable_queryset(Curriculum.objects.all(), request.user), pk=curriculum_pk,
    )
    if curriculum.name != poetry.CURRICULUM_NAME:
        raise Http404

    children = []
    for placement in CurriculumPlacement.objects.filter(
        curriculum=curriculum,
        child__in=viewable_queryset(Student.objects.all(), request.user),
    ).select_related("child"):
        done = set(
            ResponseSheet.objects.filter(
                child=placement.child,
                question_set__lesson__chapter__curriculum=curriculum,
                status=ResponseSheet.SUBMITTED,
            ).values_list("question_set__lesson__number", flat=True)
        )
        children.append({
            "child": placement.child,
            "sections_done": len(done),
            "next_section": next(
                (s for s in poetry.SECTIONS if s["number"] not in done), None),
        })

    sections = [dict(s, total=poetry.total_syllables(s)) for s in poetry.SECTIONS]
    return render(request, "tutor/poetry_guide.html", {
        "curriculum": curriculum,
        "epigraph": poetry.EPIGRAPH,
        "how_it_runs": poetry.HOW_IT_RUNS,
        "poetic_slash": poetry.POETIC_SLASH,
        "sections": sections,
        "children": children,
    })
