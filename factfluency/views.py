"""Fact Dash, in the child's portal (HH-203).

Token-authed like every other portal surface — children here have no login, so
the student comes from the signed link, never from request.user.

THE SERVER DECIDES WHAT IS CORRECT. The client is sent each answer so it can
give instant green-tick feedback with no round trip, but it does not get to
report the verdict: every attempt is re-marked here against the fact itself. It
costs nothing and it means her records mean something.
"""

import json
import uuid

from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from portal.tokens import student_from_token

from . import scheduling
from .models import (
    FLUENCY_THRESHOLD_MS, Attempt, Fact, GameSession, Level, Operation,
    PersonalRecord, RecordType,
)


def _student(token):
    student = student_from_token(token)
    if student is None:
        raise Http404
    return student


def _levels_with_state(student):
    levels = list(Level.objects.prefetch_related("facts").all())
    rows = scheduling.unlocked_levels(student, levels)
    records = {}
    for record in PersonalRecord.objects.filter(student=student):
        records.setdefault(record.level_id, {})[record.record_type] = record
    for row in rows:
        mastered, total = scheduling.level_progress(student, row["level"])
        row["mastered"] = mastered
        row["total"] = total
        row["pct"] = int(round(100 * mastered / total)) if total else 0
        row["records"] = records.get(row["level"].pk, {})
    return rows


def factdash_home(request, token):
    """The level map — what she can play, how far through, and her records."""
    student = _student(token)
    rows = _levels_with_state(student)
    return render(request, "factfluency/home.html", {
        "token": token,
        "student": student,
        "rows": rows,
        "playable": [r for r in rows if r["unlocked"]],
    })


def factdash_play(request, token, slug):
    """The game screen for one level."""
    student = _student(token)
    level = get_object_or_404(Level, slug=slug)
    rows = {r["level"].pk: r for r in _levels_with_state(student)}
    row = rows.get(level.pk)
    if row is None or not row["unlocked"]:
        raise Http404  # not reachable yet; the map does not link it either
    return render(request, "factfluency/play.html", {
        "token": token,
        "student": student,
        "level": level,
        "row": row,
    })


@require_POST
def api_start(request, token, slug):
    """Begin a round: creates the session AND returns its questions.

    One call rather than the two the brief suggested — a separate "create
    session" step buys nothing and leaves an orphan row behind every time the
    second call fails.
    """
    student = _student(token)
    level = get_object_or_404(Level, slug=slug)
    if not any(r["level"].pk == level.pk and r["unlocked"]
               for r in _levels_with_state(student)):
        raise Http404

    questions = scheduling.build_round(student, level)
    session = GameSession.objects.create(student=student, level=level)
    return JsonResponse({
        "session_id": session.pk,
        "questions": questions,
        "threshold_ms": FLUENCY_THRESHOLD_MS,
    })


@require_POST
def api_attempts(request, token, session_id):
    """Record a batch of answers and move the scheduler on.

    Idempotent per attempt on client_uuid, so a retry after a flaky moment
    cannot count the same question twice and inflate a record.
    """
    student = _student(token)
    session = get_object_or_404(GameSession, pk=session_id, student=student)

    try:
        payload = json.loads(request.body or "{}")
    except ValueError:
        return JsonResponse({"error": "bad json"}, status=400)
    rows = payload.get("attempts")
    if not isinstance(rows, list):
        return JsonResponse({"error": "attempts must be a list"}, status=400)

    newly_mastered = []
    accepted = 0
    for row in rows[:100]:                      # a round is 20; 100 is generous
        if not isinstance(row, dict):
            continue
        client_uuid = str(row.get("client_uuid") or "")[:64]
        if not client_uuid or Attempt.objects.filter(client_uuid=client_uuid).exists():
            continue                            # missing or already counted
        fact = Fact.objects.filter(pk=row.get("fact_id")).first()
        operation = row.get("operation")
        if fact is None or operation not in Operation.values:
            continue
        if operation not in fact.operations():
            continue                            # e.g. a division form of a zero fact

        try:
            response_ms = max(0, min(int(row.get("response_ms") or 0), 600000))
        except (TypeError, ValueError):
            continue
        given = row.get("answer_given")
        try:
            given = None if given is None else int(given)
        except (TypeError, ValueError):
            given = None

        # The verdict is ours, not the client's.
        is_correct = given is not None and given == fact.answer(operation)
        fluent = scheduling.is_fluent(is_correct, response_ms)

        with transaction.atomic():
            Attempt.objects.create(
                session=session, fact=fact, operation=operation,
                answer_given=given, is_correct=is_correct,
                response_ms=response_ms, was_fluent=fluent,
                client_uuid=client_uuid,
            )
            state = scheduling.ensure_states(student, [(fact, operation)])[
                (fact.pk, operation)]
            if scheduling.apply_attempt(state, is_correct=is_correct,
                                        response_ms=response_ms,
                                        session_id=session.pk):
                newly_mastered.append(fact.prompt(operation))
        accepted += 1

    return JsonResponse({"accepted": accepted, "newly_mastered": newly_mastered})


@require_POST
def api_finish(request, token, session_id):
    """Close the round, total it up, and work out what she just beat."""
    student = _student(token)
    session = get_object_or_404(GameSession, pk=session_id, student=student)

    attempts = list(session.attempts.all())
    streak = best = 0
    for attempt in attempts:
        if attempt.was_fluent:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0

    session.ended_at = timezone.now()
    session.duration_ms = sum(a.response_ms for a in attempts)
    session.num_attempted = len(attempts)
    session.num_correct = sum(1 for a in attempts if a.is_correct)
    session.num_fluent = sum(1 for a in attempts if a.was_fluent)
    session.longest_streak = best
    session.save()

    beaten = []
    if session.num_attempted:
        beaten += _maybe_record(session, RecordType.LONGEST_STREAK, best)
        beaten += _maybe_record(session, RecordType.BEST_ACCURACY,
                                round(100 * session.accuracy, 1))
        # A "best time" only means something on a clean round — otherwise the
        # fastest run is the one where she got everything wrong quickly.
        if session.num_correct == session.num_attempted:
            beaten += _maybe_record(session, RecordType.BEST_TIME, session.duration_ms)

    mastered, total = scheduling.level_progress(student, session.level)
    return JsonResponse({
        "records_beaten": beaten,
        "level_beaten": scheduling.is_level_beaten(student, session.level),
        "mastered": mastered,
        "total": total,
        "pct": int(round(100 * mastered / total)) if total else 0,
        "num_correct": session.num_correct,
        "num_attempted": session.num_attempted,
        "num_fluent": session.num_fluent,
        "longest_streak": best,
    })


def _maybe_record(session, record_type, value):
    """Store a new personal best, and say so. Returns [] when it stands."""
    lower_is_better = record_type == RecordType.BEST_TIME
    existing = PersonalRecord.objects.filter(
        student=session.student, level=session.level, record_type=record_type).first()
    if existing is not None:
        if lower_is_better and value >= existing.value:
            return []
        if not lower_is_better and value <= existing.value:
            return []
        existing.value = value
        existing.session = session
        existing.save()
    else:
        PersonalRecord.objects.create(
            student=session.student, level=session.level,
            record_type=record_type, value=value, session=session)
    return [{"type": record_type, "label": RecordType(record_type).label, "value": value}]


def api_progress(request, token):
    """Everything the map needs, as JSON. Handy for a later dashboard."""
    student = _student(token)
    return JsonResponse({
        "levels": [
            {
                "slug": r["level"].slug,
                "name": r["level"].name,
                "unlocked": r["unlocked"],
                "beaten": r["beaten"],
                "mastered": r["mastered"],
                "total": r["total"],
            }
            for r in _levels_with_state(student)
        ],
    })
