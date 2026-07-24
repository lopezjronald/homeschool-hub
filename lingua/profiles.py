"""Track-profile constants (D-34/35/36, D-64/65/66).

Profiles are Python constants, NOT a DB table — this is a lookup of defaults for
two children, mirroring the ``tutor/mastery.py`` constants pattern. Per-learner
state (which profile, and the two independent axes ``support_level`` and
``content_ceiling``) is stored on ``lingua.LearnerProfile``; this module only
supplies the DEFAULTS that seed it.

Two independent axes (D-64):
  * support_level  -> how much adult scaffolding + the SESSION-LENGTH CAP (D-66:
    the cap is a function of support_level, NOT of content level).
  * content_ceiling -> how far up the L1..L8 ladder the learner may progress.
A PARENT_MEDIATED learner may still have an unrestricted ceiling (D-65).
"""

# --- track profiles -------------------------------------------------------
KIDS_EARLY = "KIDS_EARLY"   # ~6-9
KIDS_OLDER = "KIDS_OLDER"   # ~10-13
TEEN = "TEEN"               # ~14-17
ADULT = "ADULT"             # 18+

TRACK_CHOICES = [
    (KIDS_EARLY, "Kids — early (6-9)"),
    (KIDS_OLDER, "Kids — older (10-13)"),
    (TEEN, "Teen (14-17)"),
    (ADULT, "Adult (18+)"),
]

# v1 ships only the two kid profiles; the enum carries all four so adding
# TEEN/ADULT later is a data change, not a schema change (D-36).
V1_ACTIVE = {KIDS_EARLY, KIDS_OLDER}

# --- support level (axis 1) ----------------------------------------------
PARENT_MEDIATED = "PARENT_MEDIATED"
GUIDED = "GUIDED"
INDEPENDENT = "INDEPENDENT"

SUPPORT_CHOICES = [
    (PARENT_MEDIATED, "Parent-mediated"),
    (GUIDED, "Guided"),
    (INDEPENDENT, "Independent"),
]

# D-66: session-length cap is set by support_level, never by content level.
SUPPORT_SESSION_MINUTES = {
    PARENT_MEDIATED: 10,
    GUIDED: 18,
    INDEPENDENT: 25,
}

# --- content ceiling (axis 2): the L1..L8 ladder (D-29) -------------------
LADDER = [f"L{i}" for i in range(1, 9)]  # L1..L8
LEVEL_CHOICES = [(lvl, lvl) for lvl in LADDER]


def level_rank(level):
    """0-based rank of a ladder level ('L1'->0). -1 if unknown."""
    return LADDER.index(level) if level in LADDER else -1


# --- per-track DEFAULTS (seed values only) -------------------------------
# scheduler: which SRS runs (D-31/32). grader: who rates a review card.
PROFILES = {
    KIDS_EARLY: {
        "scheduler": "leitner",
        "support_level": PARENT_MEDIATED,
        "default_ceiling": "L1",
        "max_active_items": 15,
        "picture_first": True,
        "grader": "parent",
        "output_pressure": "none",
        "explicit_grammar": False,
    },
    KIDS_OLDER: {
        "scheduler": "fsrs",
        "support_level": GUIDED,
        "default_ceiling": "L2",
        "max_active_items": 30,
        "picture_first": False,
        "grader": "self",
        "output_pressure": "light",
        "explicit_grammar": True,
    },
    TEEN: {
        "scheduler": "fsrs",
        "support_level": INDEPENDENT,
        "default_ceiling": "L3",
        "max_active_items": 40,
        "picture_first": False,
        "grader": "self",
        "output_pressure": "moderate",
        "explicit_grammar": True,
    },
    ADULT: {
        "scheduler": "fsrs",
        "support_level": INDEPENDENT,
        "default_ceiling": "L3",
        "max_active_items": 50,
        "picture_first": False,
        "grader": "self",
        "output_pressure": "moderate",
        "explicit_grammar": True,
    },
}


def defaults_for(track_profile):
    """The seed defaults for a track profile (raises KeyError if unknown)."""
    return PROFILES[track_profile]


def session_minutes_for(support_level):
    """Session-length cap in minutes for a support level (D-66)."""
    return SUPPORT_SESSION_MINUTES[support_level]
