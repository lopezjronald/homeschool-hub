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
  ]
}"""


class GraderNotConfigured(Exception):
    """Raised when no Anthropic API key is configured."""


class GraderError(Exception):
    """Raised when the API call or response parsing fails."""


def is_configured():
    """True if an Anthropic API key is available."""
    return bool(getattr(settings, "ANTHROPIC_API_KEY", ""))


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
    return {
        "level": level,
        "summary": data.get("summary", ""),
        "criteria": data.get("criteria", []),
        "encouragement": data.get("encouragement", ""),
        "kid_highlights": [str(h) for h in highlights if str(h).strip()],
    }


def grade_work(*, rubric, answers, grade_level, subject, objectives="", client=None):
    """Grade a piece of work against a rubric. Returns a parsed result dict.

    ``client`` is injectable so tests can supply a fake Anthropic client.
    """
    if not is_configured():
        raise GraderNotConfigured("Anthropic API key is not configured.")

    if client is None:
        import anthropic

        # Bounded timeout: the kid feedback page waits on this call inside a
        # web request, and Heroku hard-kills requests at 30s.
        client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY, timeout=25.0, max_retries=1,
        )

    user_prompt = _build_user_prompt(rubric, answers, grade_level, subject, objectives)
    try:
        response = client.messages.create(
            model=getattr(settings, "TUTOR_MODEL", "claude-opus-4-8"),
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:  # noqa: BLE001 — surface any API/transport error uniformly
        raise GraderError(str(exc))

    text = next((b.text for b in response.content if getattr(b, "type", None) == "text"), "")
    if not text:
        raise GraderError("The AI returned an empty response.")
    return _parse_response(text)
