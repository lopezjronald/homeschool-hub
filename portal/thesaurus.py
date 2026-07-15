"""Kid-friendly "better words" lookup for the student writing helper.

Backed by a small, fast model (see ``tutor.ai.suggest_words``) so the words are
age-appropriate — a plain thesaurus hands a 2nd grader "halcyon" for "happy".
Results are cached and every failure degrades to an empty list, so the writing
form never breaks. Called server-side, so the child's browser makes no
third-party request and each word is only looked up once.
"""

import re

from django.core.cache import cache

from tutor import ai

_WORD_RE = re.compile(r"^[A-Za-z][A-Za-z'\-]{1,38}$")
_CACHE_TTL = 60 * 60 * 24 * 7  # a week; a word's alternatives don't change


def synonyms(word, grade_level="", max_results=6):
    """Return up to ``max_results`` age-appropriate alternatives for ``word``."""
    word = (word or "").strip()
    if not _WORD_RE.match(word):
        return []
    key = "syn:%s:%s" % (grade_level, word.lower())
    cached = cache.get(key)
    if cached is not None:
        return cached
    words = ai.suggest_words(word, grade_level)[:max_results]
    if words:  # don't cache a transient empty result — let the next try re-fetch
        cache.set(key, words, _CACHE_TTL)
    return words
