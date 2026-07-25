"""Comprehension scale + check-kind selection (F-01, LGA-52).

A comprehension check produces a low-stakes SIGNAL on a small ordered scale — never a
grade shown to the child (D-53). The advancement rule (LGA-67) consumes a window of
these signals. The scale mirrors the host mastery ladder in spirit but is defined here
so lingua stays extractable (no host import, D-04).
"""
from . import profiles

# Ordered comprehension results (ascending). PENDING is a non-signal: an open answer
# awaiting parent review, excluded from the advancement window until graded.
PENDING = "pending"
BEGINNING = "beginning"
DEVELOPING = "developing"
PROFICIENT = "proficient"
STRONG = "strong"

SCALE = [BEGINNING, DEVELOPING, PROFICIENT, STRONG]  # excludes PENDING
RESULT_CHOICES = [
    (PENDING, "Awaiting review"),
    (BEGINNING, "Beginning"),
    (DEVELOPING, "Developing"),
    (PROFICIENT, "Proficient"),
    (STRONG, "Strong"),
]
PROFICIENT_BAR = PROFICIENT  # the "understood it" threshold (advancement, LGA-67)

# Check kinds. Recognition (picture-match) auto-grades; open kinds (retell / short
# answer) start PENDING for parent review.
PICTURE_MATCH = "picture_match"
RETELL = "retell"
SHORT_ANSWER = "short_answer"
KIND_CHOICES = [
    (PICTURE_MATCH, "Picture match"),
    (RETELL, "Retell"),
    (SHORT_ANSWER, "Short answer"),
]
AUTO_GRADED_KINDS = {PICTURE_MATCH}  # unambiguous recognition can auto-grade (F-01)


def rank(result):
    """0-based position on SCALE ('beginning'->0). -1 for PENDING/unknown."""
    return SCALE.index(result) if result in SCALE else -1


def is_signal(result):
    """True for a graded result (on SCALE) — PENDING is not yet a signal."""
    return result in SCALE


def meets_bar(result):
    """True if the result is at/above the proficient bar (a 'got it' signal)."""
    return rank(result) >= rank(PROFICIENT_BAR)


def check_kind_for(track_profile):
    """The comprehension check kind for a band (F-01): recognition (picture-match) for
    the youngest, retell for older kids, short-answer for teens/adults."""
    if track_profile == profiles.KIDS_EARLY:
        return PICTURE_MATCH
    if track_profile == profiles.KIDS_OLDER:
        return RETELL
    return SHORT_ANSWER
