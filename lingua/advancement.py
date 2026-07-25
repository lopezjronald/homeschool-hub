"""The level engine: a transparent, small-N-safe counting rule (D-64, LGA-67).

A RECOMMENDATION only — never auto-applied; a parent confirms (D-64). The pure
``evaluate`` below is DB-free so the thresholds are trivially testable; the service
layer gathers a learner's signals and calls it.

Asymmetric by design (a dead-band that prevents oscillation): promotion needs a strong
majority over a window (≥4 of the last 5 comprehension checks at proficient+), while
demotion is gentler and slower (3 consecutive at the very bottom). Between the two, the
learner holds.
"""
from . import comprehension

PROMOTE, DEMOTE, HOLD = "promote", "demote", "hold"

PROMOTE_WINDOW = 5   # look at the last 5 checks
PROMOTE_HITS = 4     # ≥4 of them at proficient+
# Belt-and-suspenders lower bound on graded checks. Note the 4/5 rule already implies
# ≥4 graded, so this only bites if PROMOTE_HITS is ever lowered below it.
FLOOR_N = 3
MIN_WEEKS = 2        # ...spread over ≥2 weeks (not a single-day burst)
DEMOTE_STREAK = 3    # demote only after 3 consecutive at 'beginning'
NUDGE_DEBOUNCE_SESSIONS = 5  # D-67: reading sessions between "testing above" nudges


def evaluate(recent, *, n_graded, weeks_active, level_rank, top_rank):
    """Decide PROMOTE / DEMOTE / HOLD from a learner's state (all args are plain data).

    ``recent`` = graded comprehension results, NEWEST FIRST. ``n_graded`` = total graded
    checks. ``weeks_active`` = weeks since the first graded check. ``level_rank`` =
    profiles.level_rank(content_ceiling); ``top_rank`` = the highest ladder rank.
    """
    # Demote first (gentler, and safety takes priority): last 3 all 'beginning', and
    # there's room below. Requiring a clean 3-streak keeps a dead-band vs promotion.
    last3 = recent[:DEMOTE_STREAK]
    if (len(last3) == DEMOTE_STREAK
            and all(r == comprehension.BEGINNING for r in last3)
            and level_rank > 0):
        return DEMOTE

    # Promote: a strong majority over the window, with floor/time/ceiling guards.
    window = recent[:PROMOTE_WINDOW]
    hits = sum(1 for r in window if comprehension.meets_bar(r))
    if (n_graded >= FLOOR_N
            and hits >= PROMOTE_HITS
            and weeks_active >= MIN_WEEKS
            and level_rank < top_rank):
        return PROMOTE

    return HOLD
