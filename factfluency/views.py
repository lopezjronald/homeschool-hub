"""Fact Dash, in the child's portal (HH-203).

Token-authed like every other portal surface — children here have no login, so
the student comes from the signed link, never from request.user.

THE SERVER DECIDES WHAT IS CORRECT. The client is sent each answer so it can
give instant green-tick feedback with no round trip, but it does not get to
report the verdict: every attempt is re-marked here against the fact itself. It
costs nothing and it means her records mean something.
"""

import json

from django.db import IntegrityError, transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from portal.tokens import student_from_token

from . import scheduling
from .models import (
    FLUENCY_THRESHOLD_MS, Attempt, Fact, GameSession, Level, Operation,
    PersonalRecord, RecordType, threshold_for,
)


def _student(token):
    student = student_from_token(token)
    if student is None:
        raise Http404
    return student


#: How each personal best is worded on the map, in the order they appear.
#: "12901ms" means nothing to a nine-year-old, and a bare "20" never said
#: twenty of what. Ordered here because PersonalRecord has no default ordering,
#: so the chips used to come out in whatever order the rows happened to arrive.
RECORD_CHIPS = [
    (RecordType.BEST_TIME, lambda v: "⏱ %.1fs a question" % (v / 1000.0)),
    (RecordType.BEST_ACCURACY, lambda v: "🎯 %d%% best" % round(v)),
    (RecordType.LONGEST_STREAK, lambda v: "🔥 %d in a row" % round(v)),
]


def _record_chips(by_type):
    return [{"text": word(by_type[kind].value)}
            for kind, word in RECORD_CHIPS if kind in by_type]


def _levels_with_state(student):
    levels = list(Level.objects.prefetch_related("facts").all())
    rows = scheduling.unlocked_levels(student, levels)
    records = {}
    for record in PersonalRecord.objects.filter(student=student):
        records.setdefault(record.level_id, {})[record.record_type] = record
    for row in rows:
        mastered, learning, total = scheduling.level_breakdown(student, row["level"])
        row["mastered"] = mastered
        row["learning"] = learning
        row["total"] = total
        row["pct"] = int(round(100 * mastered / total)) if total else 0
        # The second band of the bar. Right-but-slow is real progress and was
        # worth nothing on screen.
        row["learning_pct"] = int(round(100 * learning / total)) if total else 0
        row["records"] = _record_chips(records.get(row["level"].pk, {}))
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


def _int_field(value, *, low, high):
    """A JSON integer within bounds, or None. Strict: floats, bools, strings
    and Infinity are all refused rather than coerced — int(float("inf")) is an
    OverflowError, int(1.5) silently answers a different question, and
    int(True) is a boolean pretending to be a count."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < low or value > high:
        return None
    return value


def _allowed_forms(level):
    """Every (fact_id, operation) this session may legitimately report.

    The session's own level plus every level below it — build_round mixes in
    review from beaten earlier levels. Without this check the endpoint took ANY
    fact from ANY level: the audit mastered all 162 forms and unlocked the
    whole map with six POSTs from a ones-and-twos session.
    """
    allowed = set()
    for lv in (Level.objects.filter(order__lte=level.order)
               .prefetch_related("facts")):
        for fact in lv.facts.all():
            for operation in fact.operations():
                allowed.add((fact.pk, operation))
    return allowed


@require_POST
def api_attempts(request, token, session_id):
    """Record a batch of answers and move the scheduler on.

    Idempotent per attempt on client_uuid, so a retry after a flaky moment
    cannot count the same question twice and inflate a record. A malformed row
    is SKIPPED, never guessed at: recording a garbled answer_given as "wrong"
    would demote a fact she never actually missed.
    """
    student = _student(token)
    session = get_object_or_404(GameSession, pk=session_id, student=student)

    try:
        payload = json.loads(request.body or "{}")
    except ValueError:
        return JsonResponse({"error": "bad json"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "body must be an object"}, status=400)
    rows = payload.get("attempts")
    if not isinstance(rows, list):
        return JsonResponse({"error": "attempts must be a list"}, status=400)

    allowed = _allowed_forms(session.level)
    newly_mastered = []
    accepted = 0
    # The client queue caps at 200 and a round adds at most ~20, so 400 covers
    # every legitimate batch — this bound is a backstop, not a working limit.
    for row in rows[:400]:
        if not isinstance(row, dict):
            continue
        client_uuid = str(row.get("client_uuid") or "")[:64]
        if not client_uuid or Attempt.objects.filter(
                session=session, client_uuid=client_uuid).exists():
            continue                            # missing or already counted
        fact_id = _int_field(row.get("fact_id"), low=1, high=10**9)
        operation = row.get("operation")
        if fact_id is None or (fact_id, operation) not in allowed:
            continue                            # not a form this round could ask
        fact = Fact.objects.get(pk=fact_id)

        # No time reported means no fluency judgement is possible — skip, do
        # not score it as an instant (and therefore fluent) answer.
        response_ms = _int_field(row.get("response_ms"), low=0, high=600000)
        if response_ms is None:
            continue
        # The keypad allows three digits; anything else is not her.
        given = _int_field(row.get("answer_given"), low=0, high=999)
        if given is None:
            continue

        # The verdict is ours, not the client's.
        is_correct = given == fact.answer(operation)
        # Per-digit bar: the clock runs to her last keystroke, so a
        # two-digit answer is charged an extra tap the 3s benchmark
        # never included.
        bar = threshold_for(fact.answer(operation))
        fluent = scheduling.is_fluent(is_correct, response_ms, bar)

        try:
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
                                            threshold=bar,
                                            session_id=session.pk):
                    newly_mastered.append(fact.prompt(operation))
        except IntegrityError:
            continue    # a concurrent retry of the same batch won the race
        accepted += 1

    return JsonResponse({"accepted": accepted, "newly_mastered": newly_mastered})


@require_POST
def api_finish(request, token, session_id):
    """Close the round, total it up, and work out what she just beat.

    Finishes ONCE. A second call returns the stored summary unchanged — a
    closed round used to be re-totalled forever, so answers posted after the
    end kept inflating a "finished" session's numbers.
    """
    student = _student(token)
    session = get_object_or_404(GameSession, pk=session_id, student=student)
    if session.ended_at is not None:
        return _finish_response(session, [], session.longest_streak)

    attempts = list(session.attempts.all())
    streak = best = 0
    for attempt in attempts:
        if attempt.was_fluent:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0

    session.ended_at = timezone.now()
    # Clamped to the columns' real capacity — Postgres raises where SQLite
    # shrugs, and a smallint overflow here would be a user-reachable 500.
    session.duration_ms = min(sum(a.response_ms for a in attempts), 2**31 - 1)
    session.num_attempted = min(len(attempts), 32767)
    session.num_correct = min(sum(1 for a in attempts if a.is_correct), 32767)
    session.num_fluent = min(sum(1 for a in attempts if a.was_fluent), 32767)
    session.longest_streak = min(best, 32767)
    session.save()

    beaten = []
    if session.num_attempted:
        beaten += _maybe_record(session, RecordType.LONGEST_STREAK, best)
        beaten += _maybe_record(session, RecordType.BEST_ACCURACY,
                                round(100 * session.accuracy, 1))
        # A "best time" only means something on a clean round — otherwise the
        # fastest run is the one where she got everything wrong quickly. It is
        # stored PER QUESTION: rounds grow from 12 to 20 questions as facts
        # accumulate, so a raw total set on day one could never be beaten again
        # no matter how much faster she got. And only on a full-length round —
        # a one-question round must not set an unbeatable record.
        if (session.num_correct == session.num_attempted
                and session.num_attempted >= scheduling.MIN_ROUND):
            beaten += _maybe_record(
                session, RecordType.BEST_TIME,
                round(session.duration_ms / session.num_attempted))

    return _finish_response(session, beaten, best)


def _finish_response(session, beaten, best):
    mastered, learning, total = scheduling.level_breakdown(
        session.student, session.level)
    return JsonResponse({
        "records_beaten": beaten,
        "level_beaten": scheduling.is_level_beaten(session.student, session.level),
        "mastered": mastered,
        "learning": learning,
        "total": total,
        "pct": int(round(100 * mastered / total)) if total else 0,
        "learning_pct": int(round(100 * learning / total)) if total else 0,
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
