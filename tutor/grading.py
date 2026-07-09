"""Submit-time grading agent for the student portal.

When a child turns in a response sheet, the portal asks this module for quick
feedback: it grades the sheet against the question set's rubric (plus the
teacher answer key, when one exists) and stores a DRAFT MasteryAssessment —
``graded_by=None`` marks it as agent-drafted. The child sees only the warm,
child-facing pieces (encouragement + highlights, never a level); the parent
reviews the same draft on the hub and finalizes, so what the parent confirms
aligns with what the child was told.

The agent never finalizes: that stays a parent decision (mastery-not-grades).
"""

from django.db import transaction

from . import ai
from .models import MasteryAssessment


def _grade_context(sheet):
    """Judge at the curriculum's academic grade; fall back to the child's Level."""
    curriculum = sheet.question_set.lesson.chapter.curriculum
    if curriculum.grade_level:
        return curriculum.get_grade_level_display()
    return sheet.child.get_grade_level_display()


def _rubric_for(question_set):
    rubric = question_set.rubric or "Complete, thoughtful, age-appropriate work."
    if question_set.answer_key:
        rubric = (
            rubric
            + "\n\n---\n### Reference answers (for grading only — never shown to the child)\n"
            + question_set.answer_key
        )
    return rubric


def auto_grade_sheet(sheet, client=None):
    """Grade a submitted sheet once, idempotently. Returns (assessment, created).

    Returns (None, False) when the sheet has no work entry yet (not submitted)
    or the grader isn't configured. Raises ai.GraderError on API failure so the
    caller can degrade gracefully.
    """
    if not sheet.is_submitted or sheet.work_entry_id is None:
        return None, False
    if not ai.is_configured():
        return None, False

    # Serialize concurrent generate calls (double-tap / retry) on the sheet row:
    # the first request creates the assessment, the second returns it.
    with transaction.atomic():
        locked = type(sheet).objects.select_for_update().get(pk=sheet.pk)
        existing = MasteryAssessment.objects.filter(work_entry=locked.work_entry_id).first()
        if existing:
            return existing, False

    question_set = sheet.question_set
    entry = sheet.work_entry
    result = ai.grade_work(
        rubric=_rubric_for(question_set),
        answers=sheet.as_worklog_text(),
        grade_level=_grade_context(sheet),
        subject=entry.subject,
        objectives=question_set.lesson.objectives or "",
        client=client,
    )

    with transaction.atomic():
        locked = type(sheet).objects.select_for_update().get(pk=sheet.pk)
        existing = MasteryAssessment.objects.filter(work_entry=locked.work_entry_id).first()
        if existing:
            return existing, False  # a concurrent request won the race
        assessment = MasteryAssessment.objects.create(
            work_entry=entry,
            lesson=question_set.lesson,
            graded_by=None,  # agent-drafted; the parent reviews and finalizes
            rubric=_rubric_for(question_set),
            answers=sheet.as_worklog_text(),
            ai_level=result["level"],
            ai_summary=result["summary"],
            ai_criteria=result["criteria"],
            ai_encouragement=result["encouragement"],
            ai_kid_highlights=result.get("kid_highlights", []),
        )
    return assessment, True
