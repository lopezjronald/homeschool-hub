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

import logging
import threading

from django.conf import settings
from django.db import connections, transaction

from . import ai
from .models import MasteryAssessment

logger = logging.getLogger(__name__)


def _background_timeout():
    """API timeout for grades that run off the request path (no 30s router cap).

    A slow model under load used to exceed the tight in-request timeout and the
    grade was silently dropped ("it didn't grade"). Off-request we can wait.
    """
    return getattr(settings, "GRADE_BACKGROUND_TIMEOUT", 110)


def start_background_grade(sheet_pk):
    """Grade sheet ``sheet_pk`` off the request path so it can't hit the 30s wall.

    Grading a submission used to run inside the child's web request, racing
    Heroku's hard 30s router cap; heavier lessons blew past it and the assessment
    was never saved. Instead we hand the grade to a daemon thread and let the
    feedback page poll for the result. Grading is idempotent (``auto_grade_sheet``
    serialises on the sheet row), so a duplicate kickoff is harmless.

    Tests set ``GRADE_IN_BACKGROUND = False`` to run the grade inline (no thread),
    which keeps the DB transaction and any mocked client on the calling thread.
    """
    if getattr(settings, "GRADE_IN_BACKGROUND", True):
        threading.Thread(target=_threaded_grade, args=(sheet_pk,), daemon=True).start()
    else:
        _grade_now(sheet_pk)


def _threaded_grade(sheet_pk):
    """Run a grade in its own thread, then release that thread's DB connection."""
    try:
        _grade_now(sheet_pk)
    finally:
        # This thread opened its own (thread-local) connection; close it so we
        # don't leak a Postgres connection per grade on the dyno.
        connections.close_all()


def _grade_now(sheet_pk):
    """Load the sheet fresh and grade it, swallowing failures (a background grade
    must never take down the worker). A failed grade leaves no assessment, so the
    feedback poll simply times out and the parent can still grade from the report."""
    from .models import ResponseSheet

    try:
        sheet = (
            ResponseSheet.objects.select_related(
                "question_set__lesson__chapter__curriculum", "child", "work_entry",
            ).get(pk=sheet_pk)
        )
        auto_grade_sheet(sheet, timeout=_background_timeout())
    except Exception:  # noqa: BLE001 — never let a background grade crash the worker
        logger.exception("Background grade failed for response sheet %s", sheet_pk)


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


def auto_grade_sheet(sheet, client=None, timeout=None):
    """Grade a submitted sheet once, idempotently. Returns (assessment, created).

    Returns (None, False) when the sheet has no work entry yet (not submitted)
    or the grader isn't configured. Raises ai.GraderError on API failure so the
    caller can degrade gracefully. ``timeout`` overrides the API timeout (the
    background caller passes a generous one); ignored when ``client`` is injected.
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
        timeout=timeout if timeout is not None else ai.IN_REQUEST_TIMEOUT,
    )

    with transaction.atomic():
        # Lock the WORK ENTRY row — the key both this portal auto-grader and the
        # parent's manual grader (start_manual_grade) share — so the two paths
        # can't each create an assessment for the same entry (there's no DB
        # uniqueness on work_entry, and they'd otherwise lock different rows).
        type(entry).objects.select_for_update().get(pk=entry.pk)
        existing = MasteryAssessment.objects.filter(work_entry=entry).first()
        if existing:
            return existing, False  # a concurrent grade won the race
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
            ai_parent_pointers=result.get("parent_pointers", []),
        )

    # A fresh draft means a parent needs to finalize — ping them (best-effort;
    # the notifier is fail-soft too, but never let it break grading).
    try:
        from core.notifications import notify_parents_of_submission

        notify_parents_of_submission(assessment)
    except Exception:  # noqa: BLE001
        logger.exception("submission notification failed for sheet %s", sheet.pk)
    return assessment, True


def start_manual_grade(entry_pk, *, rubric, answers, grade_level, subject,
                       objectives, graded_by_id):
    """Grade a PARENT-initiated assessment off the request path.

    The manual "AI Grade" button used to grade inside the request and could blow
    past Heroku's hard 30s cap under load (an H12 "Application error"). Now it
    hands the grade to a daemon thread; the page polls and lands the parent on
    the draft once it's ready. Idempotent on the work entry (one per entry).
    """
    args = (entry_pk, rubric, answers, grade_level, subject, objectives, graded_by_id)
    if getattr(settings, "GRADE_IN_BACKGROUND", True):
        threading.Thread(target=_threaded_manual_grade, args=args, daemon=True).start()
    else:
        _manual_grade_now(*args)


def _threaded_manual_grade(*args):
    try:
        _manual_grade_now(*args)
    finally:
        connections.close_all()


def _manual_grade_now(entry_pk, rubric, answers, grade_level, subject, objectives,
                      graded_by_id):
    """Grade one parent-initiated entry and save the DRAFT assessment. Swallows
    failures (a background grade must never crash the worker); a failed grade
    leaves no assessment, so the pending page keeps waiting and the parent can
    retry."""
    from worklog.models import WorkLogEntry

    try:
        if MasteryAssessment.objects.filter(work_entry_id=entry_pk).exists():
            return  # already graded (idempotent)
        entry = WorkLogEntry.objects.get(pk=entry_pk)
        result = ai.grade_work(
            rubric=rubric,
            answers=answers,
            grade_level=grade_level,
            subject=subject,
            objectives=objectives,
            timeout=_background_timeout(),
        )
        with transaction.atomic():
            # Re-check under a row lock so a double-submit can't create two.
            locked = WorkLogEntry.objects.select_for_update().get(pk=entry_pk)
            if MasteryAssessment.objects.filter(work_entry=locked).exists():
                return
            MasteryAssessment.objects.create(
                work_entry=locked,
                graded_by_id=graded_by_id,
                rubric=rubric,
                answers=answers,
                ai_level=result["level"],
                ai_summary=result["summary"],
                ai_criteria=result["criteria"],
                ai_encouragement=result["encouragement"],
                ai_kid_highlights=result.get("kid_highlights", []),
                ai_parent_pointers=result.get("parent_pointers", []),
            )
    except Exception:  # noqa: BLE001 — never let a background grade crash the worker
        logger.exception("Manual grade failed for work entry %s", entry_pk)
