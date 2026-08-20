"""What to practise today, and what happens when she answers.

The weekly shape is Learn → Sort → Quiz → Dictation, but the day of the week is
a suggestion, not a gate: whatever she has not done yet this week is what comes
next. A child who misses Tuesday should not be locked out of the sort.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import (
    SpellingCard, SpellingPlacement, SpellingSession, SpellingWeek, SpellingWord,
)

# The order the four activities are meant to happen in.
WEEK_FLOW = [
    SpellingSession.LEARN,
    SpellingSession.SORT,
    SpellingSession.QUIZ,
    SpellingSession.DICTATION,
]

QUIZ_CAP = 15          # never more than this in one sitting
REVIEW_CAP = 5         # of which at most this many come from earlier weeks
REPEAT_THRESHOLD = 0.4  # still-in-box-1 share that repeats the week


def week_start(today=None):
    """Monday of the current week — the boundary the flow resets on."""
    today = today or timezone.localdate()
    return today - timedelta(days=today.weekday())


def placement_for(child):
    placement, _ = SpellingPlacement.objects.get_or_create(child=child)
    return placement


def ensure_cards(child, week):
    """Every word in the week becomes a card the first time she meets it."""
    existing = set(
        SpellingCard.objects.filter(child=child, word__week=week)
        .values_list("word_id", flat=True)
    )
    missing = [w for w in week.words.all() if w.pk not in existing]
    if missing:
        SpellingCard.objects.bulk_create(
            [SpellingCard(child=child, word=w) for w in missing],
            ignore_conflicts=True,
        )
    return SpellingCard.objects.filter(child=child, word__week=week)


def due_cards(child, week, *, today=None, cap=QUIZ_CAP, review_cap=REVIEW_CAP):
    """This week's due words, topped up with the oldest overdue from before.

    Continuous review is the point: words do not disappear after a test, they
    keep surfacing until they stick. Capped so a session stays under ten minutes.
    """
    today = today or timezone.localdate()
    this_week = list(
        SpellingCard.objects.filter(child=child, word__week=week, due__lte=today)
        .select_related("word", "word__week")
    )
    room = max(0, cap - len(this_week))
    review = list(
        SpellingCard.objects.filter(child=child, due__lte=today)
        .exclude(word__week=week)
        .exclude(box__gte=SpellingCard.MAX_BOX)
        .select_related("word", "word__week")
        .order_by("due", "id")[: min(review_cap, room)]
    )
    return this_week[:cap] + review


def next_activity(child, *, today=None):
    """(kind, week) for the one thing she should do now, or (None, week) if done.

    Friday onward there is no new activity — only a review quiz, and only if
    something is actually due. "All done this week" is a legitimate answer.
    """
    today = today or timezone.localdate()
    placement = placement_for(child)
    week = SpellingWeek.objects.filter(number=placement.current_week).first()
    if week is None:
        return None, None

    done = set(
        SpellingSession.objects
        .filter(child=child, week=week, on_date__gte=week_start(today))
        .values_list("kind", flat=True)
    )
    for kind in WEEK_FLOW:
        if kind not in done:
            return kind, week

    # Everything done: offer a review quiz only when there is enough to review.
    if len(due_cards(child, week, today=today)) >= REVIEW_CAP:
        return SpellingSession.QUIZ, week
    return None, week


def should_repeat_week(child, week):
    """True when too much of the week is still in box 1.

    This is the signal the spec asks for: if she has not moved most of the
    week's words off "see it again tomorrow", moving on just buries the gap.
    """
    cards = list(SpellingCard.objects.filter(child=child, word__week=week))
    if not cards:
        return False
    stuck = sum(1 for c in cards if c.box <= 1)
    return stuck / len(cards) > REPEAT_THRESHOLD


@transaction.atomic
def advance_if_ready(child, *, today=None):
    """Move to the next week, or repeat this one. Returns the week she is on."""
    today = today or timezone.localdate()
    placement = placement_for(child)
    week = SpellingWeek.objects.filter(number=placement.current_week).first()
    if week is None:
        return None
    done = set(
        SpellingSession.objects
        .filter(child=child, week=week, on_date__gte=week_start(today))
        .values_list("kind", flat=True)
    )
    if not set(WEEK_FLOW).issubset(done):
        return week
    if should_repeat_week(child, week):
        placement.repeat_flagged_on = today
        placement.save(update_fields=["repeat_flagged_on"])
        return week
    nxt = SpellingWeek.objects.filter(number__gt=week.number).order_by("number").first()
    if nxt:
        placement.current_week = nxt.number
        placement.repeat_flagged_on = None
        placement.save(update_fields=["current_week", "repeat_flagged_on"])
        return nxt
    return week


def streak(child, *, today=None):
    """Consecutive days with at least one session, counting back from today."""
    today = today or timezone.localdate()
    days = set(
        SpellingSession.objects.filter(child=child).values_list("on_date", flat=True)
    )
    if not days:
        return 0
    # Today not being done yet shouldn't zero a real streak mid-morning.
    start = today if today in days else today - timedelta(days=1)
    count, day = 0, start
    while day in days:
        count += 1
        day -= timedelta(days=1)
    return count
