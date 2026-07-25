"""Leitner box scheduler for KIDS_EARLY (D-31, LGA-59).

Five boxes with widening intervals. A correct review promotes the card one box (so it
comes back less often); a MISS resets it to box 1 — non-punitive: back to daily, never
a penalty, a lockout, or a negative box. The child never self-grades; a parent taps
got-it/missed, and unambiguous recognition cards (tap the matching picture) can
auto-grade to shrink the parent-as-grader dependency (see services.auto_grade_recognition).

Pure logic only (no ORM, no Django) so it's trivially testable and extractable — the
service layer maps this onto a ReviewItem row.
"""
from datetime import timedelta

MAX_BOX = 5
# Days a card waits in each box before it's due again. Deliberately gentle at the low
# boxes (a young learner sees new/missed words often), widening as the word sticks.
INTERVALS_DAYS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 15}


class LeitnerScheduler:
    name = "leitner"

    def initial_state(self):
        return {"box": 1}

    def review(self, state, correct, *, now):
        """Advance a card from a review grade. Returns (new_state, next_due).

        correct -> promote one box (capped at MAX_BOX); miss -> reset to box 1.
        The next due date is ``now`` + the destination box's interval."""
        # Clamp a corrupt/out-of-range stored box into [1, MAX_BOX] before advancing, so
        # bad JSON (e.g. {"box": -3} or {"box": 99}) can never KeyError the interval lookup.
        box = max(1, min(int((state or {}).get("box", 1)), MAX_BOX))
        box = min(box + 1, MAX_BOX) if correct else 1
        due = now + timedelta(days=INTERVALS_DAYS[box])
        return {"box": box}, due
