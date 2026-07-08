"""The mastery scale used across the tutor layer.

Assessment is mastery-based, never letter/percent grades. Proficient or above
is what unlocks advancement.
"""

NO_EVIDENCE = "no_evidence"
BEGINNING = "beginning"
DEVELOPING = "developing"
PROFICIENT = "proficient"
MASTERED = "mastered"

# Ordered from lowest to highest.
LEVELS = [NO_EVIDENCE, BEGINNING, DEVELOPING, PROFICIENT, MASTERED]

CHOICES = [
    (NO_EVIDENCE, "No evidence"),
    (BEGINNING, "Beginning"),
    (DEVELOPING, "Developing"),
    (PROFICIENT, "Proficient"),
    (MASTERED, "Mastered"),
]

# Bootstrap badge class per level, for the UI.
BADGE = {
    NO_EVIDENCE: "bg-secondary",
    BEGINNING: "bg-danger",
    DEVELOPING: "bg-warning text-dark",
    PROFICIENT: "bg-info text-dark",
    MASTERED: "bg-success",
}

# Proficient or above counts as "meeting the bar" (advancement signal).
ADVANCEMENT_BAR = PROFICIENT


def rank(level):
    """Numeric rank of a level (higher is better); -1 if unknown/blank."""
    return LEVELS.index(level) if level in LEVELS else -1


def meets_bar(level):
    """True if the level is Proficient or above."""
    return rank(level) >= rank(ADVANCEMENT_BAR)
