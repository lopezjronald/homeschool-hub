"""Shared subject → emoji mapping for tiles across the app.

Used by the curricula browser tiles and the student portal subject cards so
the same subject always wears the same friendly icon.
"""

# A gentle subject → emoji map for the tiles; unknown subjects get a book.
SUBJECT_EMOJI = {
    "math": "➗", "mathematics": "➗", "literature": "📖", "reading": "📚",
    "writing": "✍️", "english": "✍️", "language arts": "✍️", "grammar": "✍️",
    "science": "🔬", "history": "🏛️", "social studies": "🌍", "geography": "🗺️",
    "art": "🎨", "music": "🎵", "spelling": "🔤", "vocabulary": "🔤",
    "bible": "✝️", "logic": "🧩", "spanish": "🗣️", "coding": "💻",
}


def emoji_for(subject):
    """Return a friendly emoji for a subject name (book fallback)."""
    return SUBJECT_EMOJI.get((subject or "").strip().lower(), "📘")


def is_spelling(subject):
    """True for a spelling curriculum, where we deliberately DON'T help with
    spelling (no red squiggle, no synonym suggestions) — the child is meant to
    spell the words themselves."""
    return "spell" in (subject or "").strip().lower()


# Common synonyms folded to one canonical slug so the hours report, streak, and
# analytics group the way a parent expects. Keys are already lowercased and
# whitespace-collapsed; values are the canonical slug. The load-bearing entry is
# "spanish reading" -> "spanish": the lingua book mirror files its WorkLogEntry
# rows under "Spanish reading" (homeschool_hub/adapters/lingua_worklog.py), and
# they must group with the Spanish the child does, not spawn a second subject.
_SUBJECT_ALIASES = {
    "mathematics": "math", "maths": "math", "arithmetic": "math",
    "language arts": "writing", "english": "writing", "composition": "writing",
    "social studies": "history", "geography": "history",
    "espanol": "spanish", "español": "spanish", "spanish reading": "spanish",
}


def canonical(subject):
    """Normalize a free-text subject name to a stable slug for GROUPING.

    Case- and whitespace-insensitive, and folds common synonyms
    (``Mathematics`` -> ``math``; the lingua mirror's ``Spanish reading`` ->
    ``spanish``) so every engagement feature (streak, hours report, analytics)
    groups subjects the way a parent expects. An UNRECOGNIZED subject falls
    through to its own hyphenated slug rather than a catch-all bucket, so a
    genuinely new subject is never silently merged into another. Empty / ``None``
    -> ``""`` (the caller decides how to treat an entry with no subject).

    This is deliberately a read-time function over the free-text
    ``WorkLogEntry.subject``, not a normalized Subject entity — see the roadmap
    for why a Subject FK is deferred.
    """
    key = " ".join((subject or "").strip().lower().split())
    if not key:
        return ""
    return _SUBJECT_ALIASES.get(key, key).replace(" ", "-")
