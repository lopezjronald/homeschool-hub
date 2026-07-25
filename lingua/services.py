"""lingua orchestration + wiring.

Business logic lives here: views -> services -> ORM. No repository layer and no
custom managers (D-05) — the Django QuerySet is the repository. This module also
holds the composition helper that resolves the host-provided AIClient adapter
from settings, so lingua never imports the adapter (or tutor) directly.
"""
import json

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Max, Q, Sum
from django.utils.module_loading import import_string

from . import assets, audio, cognates, leveling, storage
from .models import AuditEvent, KnownWord, Learner, ReadingSession, Story, StoryAudio, Theme
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


def rotate_themes(age_band, count=3):
    """Bounded "pick 1 of N" theme choices for an age band (D-51, N-01).

    Returns the band's active themes ordered least-covered first — by number of
    APPROVED (servable) stories, then name for a stable tie-break — capped at
    ``count`` (default 3). Rotation is usage-driven, not random: as a theme
    accrues approved stories it sinks in priority, so the choice set keeps
    surfacing under-served themes and the corpus balances out instead of piling
    onto one favourite. Feeds both the daily plan's bounded choice and the
    generator's "top up the thinnest theme" decision. APPROVED (not total) is the
    right signal for both: pending/rejected drafts aren't servable content, so a
    theme with only unapproved drafts should still rank as under-covered.
    Returns fewer than ``count`` when the band has fewer active themes, and []
    for a non-positive ``count``.
    """
    if count <= 0:
        return []
    approved = Q(stories__status=Story.APPROVED)
    return list(
        Theme.objects.filter(age_band=age_band, active=True)
        .annotate(n_approved=Count("stories", filter=approved))
        # slug (unique) is the final tiebreak so the order is fully deterministic
        # even if two same-band themes shared a name and an approved-count.
        .order_by("n_approved", "name", "slug")[:count]
    )


def next_theme(age_band):
    """The single least-covered active theme for a band, or None if the band has
    no active themes. Used by the generator to top up the thinnest theme first."""
    themes = rotate_themes(age_band, count=1)
    return themes[0] if themes else None


def bake_story_audio(story, *, voice=None, engine=None, provider="polly",
                     link_only=False, force=False, client=None):
    """Bake (or link) the read-along audio asset for one story in one voice (LGA-38).

    Full mode (local authoring, off the web dyno per N-05): synthesize via Polly,
    upload the mp3 to the public read-along path, upload the timing JSON too (so a
    later prod ``--link-only`` run can rebuild the row without Polly), and upsert the
    StoryAudio row with inline timings. ``link_only`` (prod): NO synthesis — read the
    timings back from the public store and upsert the row pointing at the
    already-uploaded mp3.

    Idempotent by content hash: if a current (non-stale) StoryAudio exists and not
    ``force``, returns ``(existing, "skipped")``. Otherwise returns
    ``(StoryAudio, "baked"|"linked")``. Raises (TTSError / OSError) on failure — the
    command is batch-resilient and catches per story. ``client`` injects a fake Polly
    for tests.
    """
    voice = voice or settings.LINGUA.get("TTS_VOICE", "Mia")
    engine = engine or settings.LINGUA.get("TTS_ENGINE", "neural")
    existing = story.current_audio(voice, engine, provider=provider)
    if existing and not force:
        return existing, "skipped"
    digest = story.audio_hash(voice, engine, provider=provider)
    keys = assets.asset_keys(digest)
    if link_only:
        timings = storage.read_timings(keys["timings"])
        action = "linked"
    else:
        out = audio.synthesize_story(story.body, voice=voice, engine=engine, client=client)
        storage.save_audio(keys["audio"], out["audio"])
        storage.save_timings(keys["timings"], out["timings"])
        timings = out["timings"]
        action = "baked"
    words = timings.get("words") or []
    duration_ms = words[-1]["e_ms"] if words else 0
    obj, _ = StoryAudio.objects.update_or_create(
        story=story, voice=voice, engine=engine, provider=provider,
        defaults={"content_hash": digest, "audio_key": keys["audio"],
                  "timings": timings, "duration_ms": duration_ms},
    )
    return obj, action


def record_reading(learner, story, *, seconds=0):
    """Log one reading of ``story`` by ``learner`` — a ReadingSession carrying the
    story's word count + time spent (D-60/61). The atom behind the reading-volume
    hero metric; call it when a read completes (the kid reader, E-08)."""
    words = len((story.body or "").split())
    return ReadingSession.objects.create(
        learner=learner, story=story, words=words, seconds=max(0, int(seconds or 0)),
    )


def credit_known_word(learner, word):
    """Credit ``learner`` with knowing ``word`` (stored normalized). Idempotent per
    word — the known-words counter never double-counts (D-60/61). Returns
    ``(KnownWord | None, created)``; a blank/punctuation-only word is a no-op.

    Canonicalize on the word's letter-run only (via cognates.WORD_RE) BEFORE folding
    case/diacritics, so "gato" / "gato." / "¡Gató!" all collapse to one entry — a bare
    normalize() would leave punctuation attached and leak duplicates. Capped to the
    field's 64 chars so an overlong token can't DataError on Postgres."""
    m = cognates.WORD_RE.search(word or "")
    norm = cognates.normalize(m.group())[:64] if m else ""
    if not norm:
        return None, False
    return KnownWord.objects.get_or_create(learner=learner, word=norm)


def reading_totals(learner):
    """The learner's warm, non-competitive hero metric (D-60/61): cumulative words
    read, minutes of comprehensible input, distinct stories, and known-words count.
    No streaks — a milestone, not a scoreboard.

    ``words_read``/``minutes``/``known_words`` are monotonic. ``stories`` counts
    distinct NON-deleted stories (Story FK is SET_NULL), so deleting a story — a rare
    admin action — drops it from the breadth count while the words already read stay
    counted; that's an accepted trade of keeping history without snapshotting ids."""
    agg = learner.reading_sessions.aggregate(
        words=Sum("words"), secs=Sum("seconds"), stories=Count("story", distinct=True),
    )
    return {
        "words_read": agg["words"] or 0,
        "minutes": round((agg["secs"] or 0) / 60),
        "stories": agg["stories"] or 0,
        "known_words": learner.known_words.count(),
    }


def pick_reread(learner, *, cap=3, exclude_story_ids=None):
    """Pick a previously-read story to resurface — the reread-first slot of the Daily
    Plan and the highest-leverage CI lever (N-01): rereading known stories cuts content
    demand 2-3x while delivering comprehensible input.

    Eligible = stories this learner has already read, still APPROVED (servable), under
    the per-story ``cap`` of total reads, and not in ``exclude_story_ids``. Rotation:
    resurface the one read LEAST RECENTLY, so the known set cycles instead of repeating
    a favourite (guards boredom). Returns a Story or None (nothing eligible yet).
    """
    exclude = set(exclude_story_ids or [])
    rows = (
        learner.reading_sessions.filter(story__isnull=False)
        .values("story")
        .annotate(reads=Count("id"), last=Max("created_at"))
        .filter(reads__lt=cap)
        # least-recently-read first → rotation; story id tiebreaks ties for a fully
        # deterministic pick (equal timestamps otherwise order arbitrarily per-DB).
        .order_by("last", "story")
    )
    for row in rows:
        if row["story"] in exclude:
            continue
        story = Story.objects.filter(pk=row["story"], status=Story.APPROVED).first()
        if story:  # skip any that fell out of APPROVED since it was read
            return story
    return None


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
    # Soft leveling signal (D-25/LGA-44): what level the text reads as + rare words.
    # A soft signal must never lose or block a paid-for story, so degrade on failure.
    try:
        lvl = leveling.analyze(story["body"])
    except Exception:  # noqa: BLE001 — leveling is advisory, not a gate
        lvl = {"suggested_level": None, "out_of_band_pct": 0.0, "out_of_band_words": []}
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
            suggested_level=lvl["suggested_level"] or "",
            flagged_words=lvl["out_of_band_words"],
            out_of_band_pct=lvl["out_of_band_pct"],
        )
        AuditEvent.record(
            "ai.generate_completed", actor_type=AuditEvent.AI,
            target_type="Story", target_id=obj.pk,
            summary=f"generated {level} ({'passed' if review['passed'] else 'flagged'})",
            metadata={"critic_passed": review["passed"], "level": level,
                      "flag_count": len(review["flags"]), "tokens": tokens},
        )
    return obj
