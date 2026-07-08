"""The student portal — a kid's own view of just their work.

Every view resolves a signed token to ONE student and scopes every queryset to
that student. No login, no navigation into the parent app, nothing that isn't
theirs. Parents generate the link from the child's profile page.
"""

import json
from itertools import groupby

from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from curricula.models import CurriculumPlacement
from tutor.models import Material, QuestionSet, ResponseSheet
from worklog.models import WorkLogEntry

from .tokens import student_from_token


def _resolve_student(token):
    student = student_from_token(token)
    if student is None:
        raise Http404
    return student


def _placed_curriculum_ids(student):
    return list(student.placements.values_list("curriculum_id", flat=True))


def _visible_materials(student):
    """Approved materials for this child (theirs, or unpinned ones in their curricula)."""
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        Material.objects.filter(status=Material.APPROVED)
        .filter(
            Q(child=student)
            | Q(child__isnull=True, lesson__chapter__curriculum_id__in=curriculum_ids)
        )
        .select_related("lesson", "lesson__chapter")
        .order_by("lesson__chapter__number", "lesson__order")
    )


def _visible_question_sets(student):
    """Queryset of approved question sets this child may open."""
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        QuestionSet.objects.filter(status=QuestionSet.APPROVED)
        .filter(
            Q(child=student)
            | Q(child__isnull=True, lesson__chapter__curriculum_id__in=curriculum_ids)
        )
        .select_related("lesson", "lesson__chapter", "lesson__chapter__curriculum")
    )


def _annotated_question_sets(student):
    """Ordered list of visible sets with this child's response attached."""
    sets = list(
        _visible_question_sets(student).order_by(
            "lesson__chapter__curriculum__name", "lesson__chapter__number", "lesson__order", "id",
        )
    )
    responses = {
        r.question_set_id: r
        for r in ResponseSheet.objects.filter(child=student, question_set__in=sets)
    }
    for qs in sets:
        qs.my_response = responses.get(qs.pk)
    return sets


def portal_home(request, token):
    """The kid's dashboard: their curricula, their adventures, their writing."""
    student = _resolve_student(token)

    placements = (
        CurriculumPlacement.objects.filter(child=student)
        .select_related("curriculum", "current_lesson", "current_lesson__chapter")
    )
    progress = [
        {
            "curriculum": p.curriculum,
            "current_lesson": p.current_lesson,
            "progress": p.progress(),
        }
        for p in placements
    ]

    # Group the writing work by curriculum section so a 5-week course reads as
    # five tidy groups instead of a wall of cards.
    sets = _annotated_question_sets(student)
    set_groups = [
        {"heading": f"{cur_name} — {ch_title}", "sets": list(items)}
        for (cur_name, ch_title), items in groupby(
            sets, key=lambda s: (s.lesson.chapter.curriculum.name, s.lesson.chapter.title),
        )
    ]

    return render(request, "portal/portal_home.html", {
        "student": student,
        "token": token,
        "progress": progress,
        "materials": _visible_materials(student),
        "set_groups": set_groups,
    })


def portal_material(request, token, pk):
    """Kid view of an approved material — student layers only, never the teaching guide."""
    student = _resolve_student(token)
    material = get_object_or_404(_visible_materials(student), pk=pk)
    return render(request, "portal/portal_material.html", {
        "student": student,
        "token": token,
        "material": material,
    })


def _sheet_for(student, question_set):
    sheet, _ = ResponseSheet.objects.get_or_create(question_set=question_set, child=student)
    return sheet


def portal_questions(request, token, set_pk):
    """The response form: no autocorrect, autosaves as the child types."""
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = _sheet_for(student, question_set)
    questions = list(question_set.questions.all())
    for q in questions:
        q.my_answer = sheet.answer_for(q)

    if request.method == "POST" and not sheet.is_submitted:
        # Final submit (autosave arrives via the JSON endpoint).
        _merge_answers(sheet, request.POST)
        sheet.status = ResponseSheet.SUBMITTED
        sheet.submitted_at = timezone.now()
        sheet.work_entry = WorkLogEntry.objects.create(
            parent=student.parent,
            family=student.family,
            child=student,
            curriculum=question_set.lesson.chapter.curriculum,
            subject=question_set.lesson.chapter.curriculum.subject or "Literature",
            description=(
                f"{question_set.title} — submitted from {student.first_name}'s portal.\n\n"
                + sheet.as_worklog_text()
            ),
            date=timezone.localdate(),
        )
        sheet.save()
        return redirect("portal:portal_questions", token=token, set_pk=set_pk)

    return render(request, "portal/portal_questions.html", {
        "student": student,
        "token": token,
        "question_set": question_set,
        "questions": questions,
        "sheet": sheet,
    })


def _merge_answers(sheet, data):
    """Merge posted answer_<id> fields into the sheet's answers JSON."""
    answers = dict(sheet.answers or {})
    question_ids = set(
        str(pk) for pk in sheet.question_set.questions.values_list("pk", flat=True)
    )
    for key, value in data.items():
        if key.startswith("answer_"):
            qid = key.removeprefix("answer_")
            if qid in question_ids:
                answers[qid] = value
    sheet.answers = answers


@csrf_exempt
@require_POST
def portal_autosave(request, token, set_pk):
    """Autosave endpoint — merges the draft answers, returns a saved timestamp.

    CSRF-exempt by design: portal auth is the unguessable signed token in the
    URL (not an ambient cookie), so cross-site forgery has nothing to ride on,
    and exemption lets ``navigator.sendBeacon`` deliver the last-chance save.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = _sheet_for(student, question_set)
    if sheet.is_submitted:
        return JsonResponse({"ok": False, "error": "already submitted"}, status=409)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        posted = payload.get("answers", {})
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "bad payload"}, status=400)

    question_ids = set(str(pk) for pk in question_set.questions.values_list("pk", flat=True))
    answers = dict(sheet.answers or {})
    for qid, text in posted.items():
        if str(qid) in question_ids and isinstance(text, str):
            answers[str(qid)] = text
    sheet.answers = answers
    sheet.save(update_fields=["answers", "updated_at"])

    return JsonResponse({
        "ok": True,
        "saved_at": timezone.localtime(sheet.updated_at).strftime("%I:%M %p").lstrip("0"),
        "answered": sheet.answered_count,
    })
