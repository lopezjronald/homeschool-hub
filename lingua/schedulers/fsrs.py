"""FSRS scheduler for KIDS_OLDER — two-button (D-32/D-30, LGA-60).

Wraps py-fsrs (``fsrs`` 6.x — pure-Python, zero-dependency). The learner sees just TWO
buttons — got-it / missed — which map to ``Rating.Good`` / ``Rating.Again``; the full
4-rating FSRS scale is hidden. Fuzzing is DISABLED so intervals are deterministic
(stable and testable). The FSRS ``Card`` is stored verbatim as the ReviewItem's
``scheduler_state`` JSON via ``Card.to_dict()``/``from_dict()`` — which is why fsrs is
PINNED to 6.x: a major bump could change that blob's shape and orphan stored cards.

Pure wrapper (no ORM, no Django) so the service layer maps it onto a ReviewItem row
exactly like the Leitner scheduler.
"""
from fsrs import Card, Rating, Scheduler

# One shared, deterministic scheduler. enable_fuzzing=False removes the interval jitter
# so the same review always yields the same due (required for stable tests + reasoning).
_SCHEDULER = Scheduler(enable_fuzzing=False)


class FSRSScheduler:
    name = "fsrs"

    def initial_state(self):
        """A fresh FSRS card as a JSON-serializable dict (the scheduler_state blob)."""
        return Card().to_dict()

    def review(self, state, correct, *, now):
        """Advance a card from a two-button grade. Returns (new_state, next_due).

        correct -> Rating.Good (longer interval); miss -> Rating.Again (relearn soon).
        ``now`` must be timezone-aware (the service passes ``timezone.now()``)."""
        card = Card.from_dict(state) if state else Card()
        rating = Rating.Good if correct else Rating.Again
        new_card, _log = _SCHEDULER.review_card(card, rating, review_datetime=now)
        return new_card.to_dict(), new_card.due
