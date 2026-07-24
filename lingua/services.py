"""lingua orchestration + wiring.

Business logic lives here: views -> services -> ORM. No repository layer and no
custom managers (D-05) — the Django QuerySet is the repository. This module also
holds the composition helper that resolves the host-provided AIClient adapter
from settings, so lingua never imports the adapter (or tutor) directly.
"""
import json

from django.conf import settings
from django.db import transaction
from django.utils.module_loading import import_string

from .models import AuditEvent, Learner, Story
from .ports import AIClient
from .prompts import CRITIC_SYSTEM, STORY_SYSTEM


def delete_learner_for_student(host_student_id):
    """Purge the lingua Learner (+ cascaded lingua rows) for a host Student that
    was deleted. Idempotent — safe to call when no Learner exists.

    D-03 means no FK/cascade links a Student to lingua, so the host must call this
    explicitly from its delete path; ``lingua_prune_orphans`` is the scheduled
    backstop for any inline call that didn't run. Returns the rows-deleted count.
    """
    deleted, _ = Learner.objects.filter(host_student_id=host_student_id).delete()
    return deleted


def get_ai_client() -> AIClient:
    """Instantiate the host-bound AIClient adapter named in LINGUA["AI_CLIENT"].

    The dotted path is the ONLY reference to the host adapter from the lingua
    side; swapping that setting swaps the provider with zero lingua changes.
    Services take ``ai_client=None`` and fall back to this, so tests inject a
    fake implementing ``ports.AIClient``.
    """
    dotted = settings.LINGUA["AI_CLIENT"]
    return import_string(dotted)()


def _parse_json(text):
    """Parse a model's JSON OBJECT reply, tolerating accidental markdown fences
    (mirrors tutor.ai._parse_response). Raises on non-JSON or a non-object."""
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if "```" in cleaned[3:] else cleaned
        cleaned = cleaned.removeprefix("json").strip().strip("`").strip()
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object from the model")
    return data


def _tokens(usage):
    return (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)


def generate_story(*, theme_hint, level, ai_client=None):
    """Generate one leveled Spanish story via the AIClient port (D-48).
    Returns {"title", "body", "usage"}. Raises on an unparseable reply."""
    ai = ai_client or get_ai_client()
    user = f"Theme: {theme_hint}\nLevel: {level}\nWrite the story now."
    result = ai.generate(system=STORY_SYSTEM, user=user, max_tokens=800)
    data = _parse_json(result.text)
    return {
        "title": str(data.get("title", "")).strip(),
        "body": str(data.get("body", "")).strip(),
        "usage": result.usage or {},
    }


def critique_story(*, title, body, level, ai_client=None):
    """LLM-critic pre-filter (D-49): rate a generated story for naturalness,
    correctness, and level fit. Returns {"passed": bool, "flags": [str], "usage"}."""
    ai = ai_client or get_ai_client()
    user = f"Level: {level}\nTitle: {title}\nStory:\n{body}\n\nReview it now."
    result = ai.generate(system=CRITIC_SYSTEM, user=user, max_tokens=400)
    data = _parse_json(result.text)
    return {
        "passed": bool(data.get("passed", False)),
        "flags": [str(f) for f in data.get("flags", []) if str(f).strip()],
        "usage": result.usage or {},
    }


def create_story_draft(*, theme, level, ai_client=None):
    """Generate a story, run the LLM-critic pre-filter, and persist a Story (D-48/49/50).

    Critic-PASSED drafts land PENDING (ready for the parent's batch approval);
    FLAGGED drafts land DRAFT with the flags recorded, so the human queue only
    surfaces pre-vetted candidates — the mitigation for the accepted vetting risk.
    On an AI/parse failure, records an ``ai.generate_failed`` audit event (that
    write is outside the persist transaction so it survives the re-raise) and
    re-raises. On success, the Story + ``ai.generate_completed`` event commit
    together, with summed token usage for the cost ceiling (D-52/57).
    ``theme`` is a lingua.Theme instance.
    """
    ai = ai_client or get_ai_client()
    try:
        story = generate_story(theme_hint=theme.name, level=level, ai_client=ai)
        review = critique_story(
            title=story["title"], body=story["body"], level=level, ai_client=ai,
        )
    except Exception as exc:  # noqa: BLE001 — log the failure, then re-raise
        AuditEvent.record(
            "ai.generate_failed", actor_type=AuditEvent.AI,
            target_type="Theme", target_id=theme.pk,
            summary=f"generation failed: {type(exc).__name__}",
            metadata={"level": level, "error": type(exc).__name__},
        )
        raise
    tokens = _tokens(story["usage"]) + _tokens(review["usage"])
    with transaction.atomic():
        obj = Story.objects.create(
            title=story["title"] or "(sin título)",
            body=story["body"],
            level=level,
            theme=theme,
            source=Story.SOURCE_GENERATED,
            status=Story.PENDING if review["passed"] else Story.DRAFT,
            critic_passed=review["passed"],
            critic_flags=review["flags"],
        )
        AuditEvent.record(
            "ai.generate_completed", actor_type=AuditEvent.AI,
            target_type="Story", target_id=obj.pk,
            summary=f"generated {level} ({'passed' if review['passed'] else 'flagged'})",
            metadata={"critic_passed": review["passed"], "level": level,
                      "flag_count": len(review["flags"]), "tokens": tokens},
        )
    return obj
