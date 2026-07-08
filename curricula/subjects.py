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
