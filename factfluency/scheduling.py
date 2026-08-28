"""The Leitner scheduler and round builder (HH-203).

Pure-ish functions over the models, kept out of the views so the rules that
matter — what counts as fluent, what promotes, what a round is made of — can be
tested without a browser.

THE RULE THAT MAKES THIS WORK, and the easiest one to get wrong:

    right-but-slow is not fluent, and does not promote.

A child who answers 7x8 correctly after five seconds has DERIVED it, not
recalled it. Promoting her would push the fact out to a longer interval on the
strength of an answer she reconstructed, and it would quietly disappear from
practice while still being slow. So a slow-correct answer holds its box and
comes back soon.
"""

import random

from django.utils import timezone
from datetime import timedelta

from .models import (
    BOX_INTERVALS, FLUENCY_THRESHOLD_MS, MASTERY_STREAK, MAX_BOX,
    NEW_FACTS_PER_ROUND,
    Fact, Operation, StudentFactState,
)

# How long a round is. Short enough to fit the 5-10 minutes of daily practice
# the research favours, long enough to be a real run at a record.
ROUND_LENGTH = 20

# Roughly this share of a round is drawn from levels she has already beaten, so
# old facts stay warm instead of decaying the moment a level is finished.
REVIEW_SHARE = 0.2


def is_fluent(is_correct, response_ms, threshold=FLUENCY_THRESHOLD_MS):
    """Fast AND right. Either alone is not fluency."""
    return bool(is_correct) and response_ms is not None and response_ms <= threshold


def _interval(box):
    return timedelta(days=BOX_INTERVALS.get(box, BOX_INTERVALS[MAX_BOX]))


def apply_attempt(state, *, is_correct, response_ms, threshold=FLUENCY_THRESHOLD_MS,
                  now=None, session_id=None):
    """Move one fact's state on by one attempt. Returns True if it just mastered.

    Three outcomes, and the middle one is the point of the whole system:

      correct + fluent  -> promote a box, due later, streak grows
      correct + slow    -> HOLD the box, due again soon, streak resets
      incorrect         -> back to box 1, due immediately
    """
    now = now or timezone.now()
    was_mastered = state.is_mastered
    fluent = is_fluent(is_correct, response_ms, threshold)

    state.total_attempts += 1
    if is_correct:
        state.total_correct += 1
    state.last_response_ms = response_ms

    if not is_correct:
        state.leitner_box = 1
        state.consecutive_fluent = 0
        state.is_mastered = False          # a fact she just missed is not mastered
        state.due_at = now
    elif fluent:
        # ONCE PER SESSION. A round drills its small new set several times over,
        # which is the point — but three fluent hits half a minute apart is not
        # recall, it is short-term memory. Counting only the first keeps mastery
        # meaning three separate sittings.
        first_this_session = (session_id is None
                              or state.last_counted_session != session_id)
        if first_this_session:
            state.leitner_box = min(state.leitner_box + 1, MAX_BOX)
            state.consecutive_fluent += 1
            state.last_counted_session = session_id
            state.due_at = now + _interval(state.leitner_box)
            # Mastery is the STREAK, not the box — see MASTERY_STREAK. Gating on
            # box 5 would make every level take a fortnight regardless of skill.
            if state.consecutive_fluent >= MASTERY_STREAK:
                state.is_mastered = True
    else:
        # Right but slow: hold the box, come back to it today. Deliberately does
        # NOT clear is_mastered — a single sluggish answer on a long-known fact
        # is a bad day, not a regression.
        state.consecutive_fluent = 0
        state.due_at = now + timedelta(minutes=10)

    state.save()
    return state.is_mastered and not was_mastered


def _division_is_earned(fact, operation, states):
    """May this form be INTRODUCED yet?

    Multiplication always. A division only once its own multiplication has been
    answered fluently at least once — because division is derived from it. A
    child who does not yet know 5x7=35 cannot recall 35/7, she can only count
    up, which by our own rule is not fluent, so the fact would churn in box 1
    while she gets nothing from it.

    "Fluently at least once" is leitner_box >= 2: the box only ever advances on
    a fluent answer, so being out of box 1 IS the record of having recalled it.
    The gate is on INTRODUCTION only — once a division is in play it schedules
    like anything else, and a later fumble on the multiplication does not take
    it away again.
    """
    if operation == Operation.MULT:
        return True
    mult = states.get((fact.pk, Operation.MULT))
    if mult is None:
        return False
    return mult.is_mastered or mult.leitner_box >= 2


def _forms_for_level(level):
    """Every (fact, operation) pair in a level, in a stable order."""
    out = []
    for fact in level.facts.all():
        for operation in fact.operations():
            out.append((fact, operation))
    return out


def ensure_states(student, forms):
    """Fetch or create the state rows for these forms, keyed by (fact_id, op)."""
    existing = {
        (s.fact_id, s.operation): s
        for s in StudentFactState.objects.filter(
            student=student, fact__in={f for f, _ in forms})
    }
    out = {}
    for fact, operation in forms:
        key = (fact.pk, operation)
        state = existing.get(key)
        if state is None:
            state = StudentFactState.objects.create(
                student=student, fact=fact, operation=operation)
        out[key] = state
    return out


def level_progress(student, level):
    """How far through a level she is, as (mastered_forms, total_forms)."""
    forms = _forms_for_level(level)
    total = len(forms)
    if not total:
        return 0, 0
    mastered = StudentFactState.objects.filter(
        student=student, is_mastered=True,
        fact__in={f for f, _ in forms},
    ).values_list("fact_id", "operation")
    wanted = {(f.pk, o) for f, o in forms}
    hits = sum(1 for row in mastered if row in wanted)
    return hits, total


def is_level_beaten(student, level):
    """Has she cleared this level's facts?

    A challenge level is never "beaten": its facts are all met elsewhere, so
    the bar would read full before she started. Nothing unlocks after it, and
    it is scored on records instead.
    """
    if level.is_challenge:
        return False
    mastered, total = level_progress(student, level)
    if not total:
        return False
    return (mastered / total) >= level.mastery_threshold


def unlocked_levels(student, levels):
    """Which levels she may play.

    The first is always open; each later one opens when the one before it is
    beaten. Beaten levels stay playable — a record is only worth having if you
    can go back and break it.
    """
    out = []
    previous_beaten = True
    for level in levels:
        out.append({"level": level, "unlocked": previous_beaten,
                    "beaten": is_level_beaten(student, level)})
        previous_beaten = out[-1]["beaten"]
    return out


def build_round(student, level, *, length=ROUND_LENGTH, now=None, rng=None):
    """The questions for one round, in the order they will be asked.

    Priority: everything DUE in this level, then a capped handful of facts she
    has never seen, then review from levels she has already beaten, then — only
    if the round is still short — anything else from this level.
    """
    now = now or timezone.now()
    rng = rng or random

    forms = _forms_for_level(level)
    states = ensure_states(student, forms)

    fresh, due, known = [], [], []
    for fact, operation in forms:
        state = states[(fact.pk, operation)]
        if state.total_attempts == 0:
            if _division_is_earned(fact, operation, states):
                fresh.append((fact, operation))
        elif state.due_at <= now:
            due.append((fact, operation, state.due_at))
        else:
            known.append((fact, operation))

    due.sort(key=lambda row: row[2])           # longest overdue first
    chosen = [(f, o) for f, o, _ in due]

    # New facts are capped hard. This is the acquisition-rate finding: a small
    # set among mostly-known material beats a big set every time.
    rng.shuffle(fresh)
    chosen += fresh[:NEW_FACTS_PER_ROUND]

    # Keep earlier levels warm.
    review_target = int(length * REVIEW_SHARE)
    if review_target and len(chosen) < length:
        chosen += _review_forms(student, level, review_target, rng)

    if len(chosen) < length:
        rng.shuffle(known)
        chosen += known[:length - len(chosen)]

    chosen = chosen[:length]
    rng.shuffle(chosen)
    chosen = _pad(chosen, length, rng)
    return [
        {
            "fact_id": fact.pk,
            "operation": operation,
            "prompt": fact.prompt(operation),
            "answer": fact.answer(operation),
        }
        for fact, operation in chosen
    ]


# A round shorter than this is over before it starts — four questions is twenty
# seconds, and the very first round of a new level is exactly that, because only
# four new facts are allowed in. Repeating them is not padding for its own sake:
# drilling a small set is what incremental rehearsal IS.
MIN_ROUND = 12


def _pad(chosen, length, rng):
    """Repeat the chosen forms until the round is worth playing.

    Never puts the same question back to back — answering 6x8 twice in a row is
    reading, not recall.
    """
    if not chosen or len(chosen) >= MIN_ROUND:
        return chosen
    out = list(chosen)
    i = 0
    while len(out) < min(length, MIN_ROUND):
        candidate = chosen[i % len(chosen)]
        i += 1
        if len(chosen) > 1 and candidate == out[-1]:
            continue
        out.append(candidate)
    return out


def _review_forms(student, level, count, rng):
    """A few forms from earlier levels, preferring ones going stale."""
    from .models import Level

    earlier = list(Level.objects.filter(order__lt=level.order).prefetch_related("facts"))
    pool = []
    for previous in earlier:
        pool += _forms_for_level(previous)
    if not pool:
        return []
    states = {
        (s.fact_id, s.operation): s
        for s in StudentFactState.objects.filter(
            student=student, fact__in={f for f, _ in pool})
    }
    # Only things she has actually met — a "review" of a fact she has never
    # seen is just a new fact wearing a disguise, and it dodges the cap above.
    seen = [(f, o) for f, o in pool
            if (f.pk, o) in states and states[(f.pk, o)].total_attempts > 0]
    if not seen:
        return []
    seen.sort(key=lambda row: states[(row[0].pk, row[1])].due_at)
    head = seen[:max(count * 3, count)]
    rng.shuffle(head)
    return head[:count]


def portal_summary(student):
    """A cheap snapshot for the portal tile: where she is and how far in.

    Deliberately NOT unlocked_levels() — that runs a query per level, and this
    sits on the page she opens most. Two queries: every level with its facts,
    and every mastered state she has.
    """
    from .models import Level

    levels = list(Level.objects.prefetch_related("facts").all())
    if not levels:
        return None

    mastered = set(
        StudentFactState.objects.filter(student=student, is_mastered=True)
        .values_list("fact_id", "operation")
    )

    total_forms = 0
    total_done = 0
    current = None
    previous_beaten = True
    for level in levels:
        forms = _forms_for_level(level)
        done = sum(1 for f, o in forms if (f.pk, o) in mastered)
        if not level.is_challenge:
            total_forms += len(forms)
            total_done += done
        beaten = (not level.is_challenge and forms
                  and (done / len(forms)) >= level.mastery_threshold)
        if current is None and previous_beaten and not beaten:
            current = {"level": level, "done": done, "of": len(forms)}
        previous_beaten = beaten

    return {
        "current": current or {"level": levels[-1], "done": 0, "of": 0},
        "mastered": total_done,
        "total": total_forms,
    }
