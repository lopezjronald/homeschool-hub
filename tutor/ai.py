"""Server-side Anthropic client for mastery grading.

The grader sends a rubric + the child's work to Claude and gets back a mastery
level plus rubric-referenced feedback. It never assigns letter/percent grades,
and it never finalizes — the parent reviews and can override before finalizing.

The API key lives only in ``settings.ANTHROPIC_API_KEY`` (an env var). When no
key is set the grader is disabled and the UI says so.
"""

import json

from django.conf import settings

from . import mastery

SYSTEM_PROMPT = """You are a supportive homeschool teaching assistant that assesses a child's work \
against a rubric using MASTERY levels, never letter grades or percentages.

Use exactly these mastery levels: no_evidence, beginning, developing, proficient, mastered.
Judge at the child's grade level. Be specific and reference the rubric. Keep feedback warm and \
encouraging for a young learner, and actionable for the parent.

Respond with ONLY a JSON object (no prose, no markdown fences) matching this shape:
{
  "level": "<one of: no_evidence|beginning|developing|proficient|mastered>",
  "summary": "<one or two sentences on how the work measured against the rubric>",
  "criteria": [
    {"criterion": "<short rubric point>", "met": true, "comment": "<specific note>"}
  ],
  "encouragement": "<one warm sentence addressed to the child>",
  "kid_highlights": [
    "<2-3 short bullets addressed directly to the child at their reading level: what they did well, and ONE gentle thing to try next time. Never mention the mastery level, points, or grades.>"
  ],
  "parent_pointers": [
    "<3-4 short, concrete pointers addressed to the PARENT or TEACHER (not the child) for helping this child with THIS concept interactively, so they don't rely only on this AI feedback. Draw on the lesson objectives and the specific things this child got right or wrong. Cover, across the bullets: the likely sticking point, a good question to ask the child, a hands-on way to reinforce it, and a suggested next step. Be specific to the work — reference what they actually did.>"
  ]
}"""


COACH_PROMPT = """You are a warm writing coach for a homeschooled child working on a ROUGH draft. \
Your job is to help them improve their own writing before the final draft — never to rewrite it for them.

Speak directly to the child at their grade level. Never mention grades, levels, points, or scores. \
Never write sentences for them; give directions they can act on themselves ("try adding…", "read this \
sentence out loud…"). Be encouraging: this is a draft, and drafts are supposed to be improved.

Respond with ONLY a JSON object (no prose, no markdown fences) matching this shape:
{
  "praise": "<one specific, genuine sentence about what's working in THEIR words>",
  "suggestions": [
    "<2-3 short, concrete, kid-actionable suggestions to make the draft better>"
  ]
}"""


class GraderNotConfigured(Exception):
    """Raised when no Anthropic API key is configured."""


class GraderError(Exception):
    """Raised when the API call or response parsing fails."""


def is_configured():
    """True if an Anthropic API key is available."""
    return bool(getattr(settings, "ANTHROPIC_API_KEY", ""))


def _make_client():
    import anthropic

    # These calls run INSIDE a web request and Heroku hard-kills requests at 30s.
    # So: a tight timeout and NO SDK retries — a retry would stack a second
    # attempt on top of the first and blow past 30s, killing the request before
    # the assessment is saved (the child then "never sees results"). On failure
    # we fail fast; the feedback page re-fires the (idempotent) grade on reload.
    return anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY, timeout=24.0, max_retries=0,
    )


def grading_model():
    """Model used for the in-request grader. Defaults to Opus, but a deployment
    under a hard request-time budget (e.g. Heroku's 30s cap) can set TUTOR_MODEL
    to a faster model like claude-sonnet-5 so grading reliably finishes in time."""
    return getattr(settings, "TUTOR_MODEL", "claude-opus-4-8")


def _build_user_prompt(rubric, answers, grade_level, subject, objectives=""):
    parts = [
        f"Subject: {subject}",
        f"Child's grade level: {grade_level}",
    ]
    if objectives:
        parts.append(f"Lesson objectives:\n{objectives}")
    parts.append(f"Rubric:\n{rubric}")
    parts.append(f"The child's work / answers:\n{answers}")
    parts.append("Assess the work against the rubric and return the JSON described above.")
    return "\n\n".join(parts)


def _parse_response(text):
    """Parse the model's JSON, tolerating accidental markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if "```" in cleaned[3:] else cleaned
        cleaned = cleaned.removeprefix("json").strip().strip("`").strip()
    try:
        data = json.loads(cleaned)
    except (ValueError, TypeError) as exc:
        raise GraderError(f"Could not parse the AI response as JSON: {exc}")
    level = data.get("level")
    if level not in mastery.LEVELS:
        raise GraderError(f"AI returned an unknown mastery level: {level!r}")
    highlights = data.get("kid_highlights", [])
    if not isinstance(highlights, list):
        highlights = []
    pointers = data.get("parent_pointers", [])
    if not isinstance(pointers, list):
        pointers = []
    return {
        "level": level,
        "summary": data.get("summary", ""),
        "criteria": data.get("criteria", []),
        "encouragement": data.get("encouragement", ""),
        "kid_highlights": [str(h) for h in highlights if str(h).strip()],
        "parent_pointers": [str(p) for p in pointers if str(p).strip()],
    }


def grade_work(*, rubric, answers, grade_level, subject, objectives="", client=None):
    """Grade a piece of work against a rubric. Returns a parsed result dict.

    ``client`` is injectable so tests can supply a fake Anthropic client.
    """
    if not is_configured():
        raise GraderNotConfigured("Anthropic API key is not configured.")

    if client is None:
        client = _make_client()

    user_prompt = _build_user_prompt(rubric, answers, grade_level, subject, objectives)
    try:
        response = client.messages.create(
            model=grading_model(),
            max_tokens=2500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:  # noqa: BLE001 — surface any API/transport error uniformly
        raise GraderError(str(exc))

    text = next((b.text for b in response.content if getattr(b, "type", None) == "text"), "")
    if not text:
        raise GraderError("The AI returned an empty response.")
    return _parse_response(text)


WORD_HELP_MODEL = "claude-haiku-4-5"  # tiny, fast, cheap — right tool for a word lookup

WORD_HELP_PROMPT = (
    "You help a young student find a better or more interesting word while writing. "
    "Given ONE word and the student's grade level, list a few common words with a "
    "similar meaning that a child at that grade already knows and could use instead.\n"
    "Rules: only real, common, age-appropriate SINGLE words (no phrases, no proper "
    "nouns); 3 to 6 of them; never include the original word; if the input is not a "
    "normal English word, return an empty list.\n"
    'Respond with ONLY a JSON array of lowercase words, e.g. ["glad","cheerful","joyful"].'
)


def suggest_words(word, grade_level="", client=None):
    """A few kid-friendly alternatives for ``word`` (or []). Uses a small fast model
    (not the grader), so it stays cheap and quick for an on-demand word lookup."""
    word = (word or "").strip()
    if not word or not is_configured():
        return []
    if client is None:
        client = _make_client()
    user_prompt = "Word: %s\nStudent grade level: %s" % (word, grade_level or "elementary")
    try:
        response = client.messages.create(
            model=WORD_HELP_MODEL,
            max_tokens=120,
            system=WORD_HELP_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception:  # noqa: BLE001 — degrade to no suggestions
        return []
    text = next((b.text for b in response.content if getattr(b, "type", None) == "text"), "")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if "```" in cleaned[3:] else cleaned
        cleaned = cleaned.removeprefix("json").strip().strip("`").strip()
    try:
        data = json.loads(cleaned)
    except (ValueError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    low = word.lower()
    out = []
    for w in data:
        w = str(w).strip().lower()
        if w and w != low and w.replace("'", "").replace("-", "").isalpha() and w not in out:
            out.append(w)
    return out[:6]


def review_draft(*, draft, assignment, grade_level, subject, client=None):
    """Coach a child's ROUGH draft: praise + 2-3 actionable suggestions.

    Formative, not summative — no level, no grade, never rewrites the child's
    work. Returns {"praise": str, "suggestions": [str, ...]}.
    """
    if not is_configured():
        raise GraderNotConfigured("Anthropic API key is not configured.")
    if client is None:
        client = _make_client()

    user_prompt = "\n\n".join([
        f"Subject: {subject}",
        f"Child's grade level: {grade_level}",
        f"The writing assignment:\n{assignment}",
        f"The child's rough draft:\n{draft}",
        "Coach this draft and return the JSON described above.",
    ])
    try:
        response = client.messages.create(
            model=grading_model(),
            max_tokens=1000,
            system=COACH_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:  # noqa: BLE001 — surface any API/transport error uniformly
        raise GraderError(str(exc))

    text = next((b.text for b in response.content if getattr(b, "type", None) == "text"), "")
    if not text:
        raise GraderError("The AI returned an empty response.")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if "```" in cleaned[3:] else cleaned
        cleaned = cleaned.removeprefix("json").strip().strip("`").strip()
    try:
        data = json.loads(cleaned)
    except (ValueError, TypeError) as exc:
        raise GraderError(f"Could not parse the AI response as JSON: {exc}")
    suggestions = data.get("suggestions", [])
    if not isinstance(suggestions, list):
        suggestions = []
    return {
        "praise": str(data.get("praise", "")),
        "suggestions": [str(s) for s in suggestions if str(s).strip()][:3],
    }
