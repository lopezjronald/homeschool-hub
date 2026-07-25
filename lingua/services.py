"""lingua orchestration + wiring.

Business logic lives here: views -> services -> ORM. No repository layer and no
custom managers (D-05) — the Django QuerySet is the repository. This module also
holds the composition helper that resolves the host-provided AIClient adapter
from settings, so lingua never imports the adapter (or tutor) directly.
"""
import json

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Max, Q, Sum
from django.utils import timezone
from django.utils.module_loading import import_string

from . import (
    advancement, assets, audio, cognates, comprehension, leveling, profiles, safety,
    schedulers, storage,
)
from .models import (
    AiUsage, AuditEvent, ComprehensionCheck, KnownWord, Learner, MilestoneAward,
    PhonicsRule, ReadingSession, ReviewItem, Story, StoryAudio, Theme,
)
from .ports import AIClient
from .prompts import CRITIC_SYSTEM, STORY_SYSTEM


def get_or_create_learner(host_student_id, track_profile):
    """Get, or first-time provision, the Learner for a host student (D-03: keyed by a
    plain int, no FK). Idempotent — the kid portal calls this on entry, so a Student
    becomes a Learner the first time they open Lingua. The host chooses the track
    profile (it knows the child's age); lingua just seeds the profile defaults."""
    learner = Learner.objects.filter(host_student_id=host_student_id).first()
    if learner:
        return learner
    try:
        return Learner.create_for_host_student(host_student_id, track_profile)
    except IntegrityError:
        # A concurrent first-entry (double-tap / prefetch / two tabs) won the race and
        # inserted the row — host_student_id is unique, so recover its Learner instead
        # of 500-ing. create_for_host_student is @transaction.atomic, so its failed
        # insert rolled back cleanly.
        return Learner.objects.get(host_student_id=host_student_id)


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
    # Clamp to one day: a hostile/garbage POST of a huge value would overflow
    # ReadingSession.seconds (int4 on Postgres) and 500; no real read exceeds 86,400s.
    return ReadingSession.objects.create(
        learner=learner, story=story, words=words,
        seconds=max(0, min(int(seconds or 0), 86_400)),
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


# Conservative beginner reading rate (words/min) used to estimate a story's session
# time when no baked audio duration is available. Slow on purpose — over-estimating
# time fills FEWER items into the cap, which is the safe direction (D-66).
READING_WPM = 40


def _story_minutes(story):
    """Estimated minutes to read a story: the baked audio duration if any voice has
    been synthesized, else word-count / READING_WPM. Always >= 1."""
    sa = story.audios.first()
    if sa and sa.duration_ms:
        return max(1, round(sa.duration_ms / 60000))
    return max(1, round(len((story.body or "").split()) / READING_WPM))


def _servable_stories(ceiling, exclude):
    """APPROVED stories at/near a content ceiling (levels L1..ceiling), hardest-first
    (nearest the ceiling = i+1), excluding ``exclude`` pks."""
    rank = profiles.level_rank(ceiling)
    allowed = profiles.LADDER[:rank + 1] if rank >= 0 else [ceiling]
    return (
        Story.objects.filter(status=Story.APPROVED, level__in=allowed)
        .exclude(pk__in=exclude)
        .order_by("-level", "-created_at")  # nearest ceiling, then newest
    )


def build_daily_plan(learner):
    """Assemble today's session for a learner (F-06, D-66, N-01).

    Reading-first: a reread (the highest-leverage CI lever) then a new story at/near
    the content ceiling, with narrow reading (prefer the reread's theme for
    continuity). The per-support-level session cap is a HARD limit — content difficulty
    never lengthens the session (D-66): the first reading item is always offered (never
    an empty session), and further items are added only while they fit under the cap,
    so harder/longer content yields FEWER items, never more time. Also returns a
    bounded 'pick 1 of 3' next-story choice (autonomy, N-01).

    Returns a plain dict (no persistence) the portal page renders. Listening / vocab /
    activity slots arrive with E-06 / E-07.
    """
    profile = learner.profile
    cap = profile.session_minutes
    ceiling = profile.content_ceiling
    read_ids = set(learner.reading_sessions.values_list("story_id", flat=True))
    read_ids.discard(None)

    reread = pick_reread(learner)
    planned = {reread.pk} if reread else set()
    new_story = _pick_new_story(
        ceiling, exclude=read_ids | planned,
        prefer_theme=reread.theme_id if reread else None,
    )

    # Always offer the first reading item; gate the rest by the hard cap (D-66).
    items, used = [], 0
    for kind, story in (("reread", reread), ("new", new_story)):
        if story is None:
            continue
        minutes = _story_minutes(story)
        if items and used + minutes > cap:
            break
        items.append({"kind": kind, "story": story, "minutes": minutes})
        used += minutes

    if not items and read_ids:
        # Every servable story is read AND at the reread cap: resurface the
        # least-recently-read one ignoring the cap, so an engaged learner is never
        # dead-ended with a false "no stories yet" message (N-01).
        fallback = pick_reread(learner, cap=10 ** 9)
        if fallback:
            items.append({"kind": "reread", "story": fallback,
                          "minutes": _story_minutes(fallback)})
            used = items[0]["minutes"]

    picked = {i["story"].pk for i in items}
    choices = list(_servable_stories(ceiling, exclude=read_ids | picked)[:3])
    return {
        "learner_id": learner.pk,
        "cap_minutes": cap,
        "estimated_minutes": used,
        "ceiling": ceiling,
        "items": items,
        "choices": choices,
    }


def _pick_new_story(ceiling, exclude, prefer_theme=None):
    """A new (unread) APPROVED story at/near the ceiling; prefer ``prefer_theme`` for
    narrow-reading continuity, else the nearest-ceiling story overall."""
    qs = _servable_stories(ceiling, exclude)
    if prefer_theme is not None:
        in_theme = qs.filter(theme_id=prefer_theme).first()
        if in_theme:
            return in_theme
    return qs.first()


# Warm, comprehension/volume milestones (D-60/61) — NEVER streaks or accuracy.
WORDS_MILESTONES = [100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
KNOWN_MILESTONES = [10, 25, 50, 100, 250, 500, 1000]


def award_milestones(learner):
    """Award any reading-volume / known-words milestones the learner has newly crossed
    (D-60/61 — volume & comprehension, never streaks/accuracy). Idempotent: each
    (kind, threshold) is granted once. Returns the newly-awarded MilestoneAwards,
    most-significant first, for the portal to celebrate."""
    totals = reading_totals(learner)
    newly = []
    for kind, total, thresholds in (
        (MilestoneAward.WORDS, totals["words_read"], WORDS_MILESTONES),
        (MilestoneAward.KNOWN, totals["known_words"], KNOWN_MILESTONES),
    ):
        for threshold in thresholds:
            if total >= threshold:
                award, created = MilestoneAward.objects.get_or_create(
                    learner=learner, kind=kind, threshold=threshold)
                if created:
                    newly.append(award)
    newly.sort(key=lambda a: a.threshold, reverse=True)
    return newly


def record_comprehension(learner, story, kind, result=None):
    """Record an after-reading comprehension check (F-01, LGA-52). The grade path is
    driven by ``kind``, not by whether a result was passed: a recognition kind
    (AUTO_GRADED_KINDS, e.g. picture-match) MUST carry a valid auto-grade result; an
    open kind (retell/short-answer) ALWAYS lands PENDING for parent review — any result
    passed for an open kind is ignored, so an open answer can never skip review and leak
    an ungraded signal into advancement (D-53/F-01). Only the rating is stored, never
    the child's free text. Returns the ComprehensionCheck."""
    if kind not in dict(comprehension.KIND_CHOICES):
        raise ValueError(f"Unknown comprehension kind: {kind!r}")
    if kind in comprehension.AUTO_GRADED_KINDS:
        if not comprehension.is_signal(result):
            raise ValueError(f"Auto-graded kind {kind!r} requires a valid result, got {result!r}")
        final = result
    else:
        final = comprehension.PENDING  # open kind → parent grades later
    return ComprehensionCheck.objects.create(
        learner=learner, story=story, kind=kind, result=final,
    )


def grade_comprehension(check, result, *, reviewed_by):
    """Parent-review an open (PENDING) comprehension check, setting its rating (D-53).
    Returns the updated check; raises on an unknown result."""
    if not comprehension.is_signal(result):
        raise ValueError(f"Unknown comprehension result: {result!r}")
    check.result = result
    check.reviewed_by = reviewed_by
    check.save(update_fields=["result", "reviewed_by", "updated_at"])
    return check


def recent_comprehension(learner, n=5):
    """The learner's last ``n`` GRADED comprehension results, newest first — the signal
    window the advancement rule (LGA-67) consumes. PENDING checks are excluded (not yet
    a signal)."""
    return list(
        learner.comprehension_checks
        .exclude(result=comprehension.PENDING)
        .order_by("-created_at", "-id")  # -id tiebreaks same-instant checks (deterministic)
        .values_list("result", flat=True)[:n]
    )


def advancement_recommendation(learner):
    """A transparent, small-N-safe level recommendation for a learner (D-64, LGA-67) —
    a RECOMMENDATION only, never auto-applied (a parent confirms via apply_advancement).
    Returns {"action": promote|demote|hold, "from_level", "to_level"}."""
    profile = learner.profile
    graded = learner.comprehension_checks.exclude(result=comprehension.PENDING)
    recent = recent_comprehension(learner, n=advancement.PROMOTE_WINDOW)
    first = graded.order_by("created_at").values_list("created_at", flat=True).first()
    weeks_active = (timezone.now() - first).days / 7 if first else 0
    rank = profiles.level_rank(profile.content_ceiling)
    top_rank = len(profiles.LADDER) - 1
    action = advancement.evaluate(
        recent, n_graded=graded.count(), weeks_active=weeks_active,
        level_rank=rank, top_rank=top_rank,
    )
    to_level = profile.content_ceiling
    if action == advancement.PROMOTE:
        to_level = profiles.LADDER[rank + 1]
    elif action == advancement.DEMOTE:
        to_level = profiles.LADDER[rank - 1]
    return {"action": action, "from_level": profile.content_ceiling, "to_level": to_level}


@transaction.atomic
def apply_advancement(learner, to_level, *, host_user_id):
    """Apply a PARENT-CONFIRMED level change (never auto, D-64). Sets content_ceiling
    and writes an audit event (D-57). Raises on an invalid ladder level."""
    if to_level not in profiles.LADDER:
        raise ValueError(f"Not a ladder level: {to_level!r}")
    profile = learner.profile
    old = profile.content_ceiling
    profile.content_ceiling = to_level
    profile.save(update_fields=["content_ceiling", "updated_at"])
    AuditEvent.record(
        "learner.advanced", actor_type=AuditEvent.PARENT, actor_id=host_user_id,
        target_type="Learner", target_id=learner.pk, summary=f"{old} -> {to_level}",
        metadata={"from": old, "to": to_level},
    )
    return profile


def nudge_testing_above_defaults(learner):
    """Parent-only, debounced nudge that a learner may be ready to test ABOVE their
    default track (D-67): consistently STRONG over the last window, and not shown within
    the last ~5 reading sessions. NEVER child-visible. Call mark_nudge_shown when the
    parent view displays it."""
    recent = recent_comprehension(learner, n=advancement.PROMOTE_WINDOW)
    if len(recent) < advancement.PROMOTE_WINDOW or any(r != comprehension.STRONG for r in recent):
        return False
    last = learner.profile.last_nudge_reading_count
    return last is None or (learner.reading_sessions.count() - last) >= advancement.NUDGE_DEBOUNCE_SESSIONS


def mark_nudge_shown(learner):
    """Anchor the D-67 nudge debounce at the current reading-session count."""
    profile = learner.profile
    profile.last_nudge_reading_count = learner.reading_sessions.count()
    profile.save(update_fields=["last_nudge_reading_count", "updated_at"])


def phonics_rules():
    """The active Spanish phonics rules for the mini-lesson (F-04, LGA-64), ordered."""
    return list(PhonicsRule.objects.filter(active=True))


MAX_ACTIVE_LEITNER_ITEMS = 15   # deck-size cap for the young Leitner learner (D-31)


def add_review_item(learner, target_ref, *, target_kind=ReviewItem.VOCAB,
                    scheduler=ReviewItem.LEITNER, now=None):
    """Add a card to the learner's deck, seeded by the chosen scheduler and due now
    (LGA-59). Idempotent per (learner, kind, ref) — a repeat target returns the
    existing card unchanged. For Leitner, enforces the <=15 active-deck cap so a young
    child isn't overwhelmed (D-31): at the cap, returns None and adds nothing."""
    now = now or timezone.now()
    if (scheduler == ReviewItem.LEITNER
            and ReviewItem.objects.filter(learner=learner, scheduler=ReviewItem.LEITNER)
            .count() >= MAX_ACTIVE_LEITNER_ITEMS):
        return None
    sched = schedulers.get_scheduler(scheduler)
    item, _ = ReviewItem.objects.get_or_create(
        learner=learner, target_kind=target_kind, target_ref=target_ref,
        defaults={"scheduler": scheduler, "scheduler_state": sched.initial_state(), "due": now},
    )
    return item


def grade_review_item(item, correct, *, now=None):
    """Apply a review grade to a card via its scheduler (LGA-59). ``correct`` comes from
    a parent tap (got-it/missed) or an auto-graded recognition match — the scheduler
    handles both identically. A miss is non-punitive (Leitner resets to box 1)."""
    now = now or timezone.now()
    sched = schedulers.get_scheduler(item.scheduler)
    item.scheduler_state, item.due = sched.review(item.scheduler_state, correct, now=now)
    item.save(update_fields=["scheduler_state", "due", "updated_at"])
    return item


def auto_grade_recognition(item, chosen, correct, *, now=None):
    """Auto-grade an unambiguous recognition card (tap the matching picture) without a
    parent (D-31): the tap is objectively right/wrong. A miss just resets the box."""
    return grade_review_item(item, chosen == correct, now=now)


def due_review_items(learner, *, now=None):
    """The learner's due spaced-repetition cards, soonest-first — the single indexed
    "what's due" query that serves BOTH schedulers (D-30, LGA-58). A card is due when
    ``due <= now`` and it isn't paused past now (``paused_until`` null or already
    elapsed). Ordering falls back to id so equal-due cards are stable."""
    now = now or timezone.now()
    return list(
        ReviewItem.objects.filter(learner=learner, due__lte=now)
        .filter(Q(paused_until__isnull=True) | Q(paused_until__lte=now))
        .order_by("due", "id")
    )


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


class CostCeilingExceeded(Exception):
    """The monthly AI cost ceiling is reached; new generation is paused (D-52, LGA-29)."""


def _current_period():
    return timezone.now().strftime("%Y-%m")


def estimated_cost_usd(input_tokens, output_tokens):
    """Estimate USD for a token count from the configured per-million-token prices."""
    L = settings.LINGUA
    return (input_tokens / 1_000_000) * L["AI_PRICE_INPUT_PER_MTOK"] + \
           (output_tokens / 1_000_000) * L["AI_PRICE_OUTPUT_PER_MTOK"]


def month_to_date_cost_usd():
    """Estimated AI spend for the current calendar month (0.0 if nothing recorded)."""
    row = AiUsage.objects.filter(period=_current_period()).first()
    return estimated_cost_usd(row.input_tokens, row.output_tokens) if row else 0.0


def ai_budget_exceeded():
    """True once month-to-date spend reaches the ceiling — the hard-stop gate (D-52)."""
    return month_to_date_cost_usd() >= settings.LINGUA["MONTHLY_COST_CEILING_USD"]


def record_ai_usage(usage):
    """Accumulate one AI call's tokens into the current month (LGA-29). Atomic F()
    increment so concurrent authoring can't lose a call; tolerates missing counts."""
    it = (usage or {}).get("input_tokens") or 0
    ot = (usage or {}).get("output_tokens") or 0
    period = _current_period()
    AiUsage.objects.get_or_create(period=period)
    AiUsage.objects.filter(period=period).update(
        input_tokens=F("input_tokens") + it,
        output_tokens=F("output_tokens") + ot,
        calls=F("calls") + 1,
        updated_at=timezone.now(),
    )


def generate_story(*, theme_hint, level, ai_client=None):
    """Generate one leveled Spanish story via the AIClient port (D-48).
    Returns {"title", "body", "usage"}. Raises on an unparseable reply."""
    ai = ai_client or get_ai_client()
    safety.assert_no_pii(theme_hint, where="story generation")  # D-52 (LGA-31)
    # Fence the untrusted theme hint so it can't inject instructions (LGA-30, D-53).
    user = f"Level: {level}\n{safety.fence(theme_hint, 'theme')}\nWrite the story now."
    result = ai.generate(system=STORY_SYSTEM, user=user, max_tokens=800)
    record_ai_usage(result.usage)  # bill the instant the provider responds — before any parse can fail (LGA-29)
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
    safety.assert_no_pii(title, body, where="critic review")  # D-52 (LGA-31)
    # Fence the untrusted title/body so a story that says "mark this passed" can't
    # hijack the critic — the load-bearing safeguard (LGA-30, D-49/D-53).
    user = (
        f"Level: {level}\n{safety.fence(title, 'title')}\n"
        f"{safety.fence(body, 'story')}\n\nReview it now."
    )
    result = ai.generate(system=CRITIC_SYSTEM, user=user, max_tokens=400)
    record_ai_usage(result.usage)  # bill the instant the provider responds — before any parse can fail (LGA-29)
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
    # Hard-stop BEFORE spending: once the month's estimated spend hits the ceiling,
    # no new generation runs until next month (D-52/57, LGA-29).
    if ai_budget_exceeded():
        raise CostCeilingExceeded(
            f"Lingua monthly AI cost ceiling (${settings.LINGUA['MONTHLY_COST_CEILING_USD']}) "
            "reached; story generation is paused until next month."
        )
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
    # Usage is recorded inside generate_story/critique_story the instant each provider
    # call returns, so a later parse/persist failure never loses real spend (LGA-29).
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
