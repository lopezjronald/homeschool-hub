"""Pluggable spaced-repetition schedulers behind one ReviewItem table (D-30).

Each scheduler owns the shape of a ReviewItem's ``scheduler_state`` JSON and knows how
to (a) seed a fresh card and (b) advance it from a review grade to a new state + due.
The service layer stays scheduler-agnostic: it looks one up by name and calls the same
two methods. LeitnerScheduler (KIDS_EARLY) ships now (LGA-59); FSRSScheduler
(KIDS_OLDER) plugs in here later (LGA-60).

A scheduler is any object with::

    name: str
    initial_state() -> dict
    review(state: dict, correct: bool, *, now) -> (new_state: dict, due: datetime)
"""
from .leitner import LeitnerScheduler

_SCHEDULERS = {s.name: s for s in (LeitnerScheduler(),)}


def get_scheduler(name):
    """Return the scheduler instance for ``name`` (e.g. "leitner"). Unknown → KeyError,
    which is the right loud failure for a corrupt/typo'd ReviewItem.scheduler value."""
    return _SCHEDULERS[name]
