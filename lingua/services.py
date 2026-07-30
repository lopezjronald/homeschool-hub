"""lingua orchestration + wiring.

Business logic lives here: views -> services -> ORM. No repository layer and no
custom managers (D-05) — the Django QuerySet is the repository. This module also
holds the composition helper that resolves the host-provided AIClient adapter
from settings, so lingua never imports the adapter (or tutor) directly.
"""
import json
import os
import tempfile

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Max, Q, Sum
from django.utils import timezone
from django.utils.module_loading import import_string

from . import (
    advancement, assets, audio, cognates, comprehension, illustrate, leveling,
    profiles, safety, schedulers, storage,
)
from .models import (
    AiUsage, AlphabetTile, AudioClip, AuditEvent, BookLogEntry, ComprehensionCheck,
    KnownWord, Learner, LibraryBook, ListeningResource, ListeningSession,
    MilestoneAward, Pathway, PathwayStep, PhonicsRule, ReadingSession, ReviewItem,
    Story, StoryAudio, StoryImage, StoryRecording, Theme, TutorPacket,
)
from .ports import AIClient, ImageClient
from .prompts import CRITIC_SYSTEM, STORY_SYSTEM


class BudgetExceeded(Exception):
    """Raised when the monthly AI/image cost ceiling is hit mid-batch (D-52, LGA-29/71)."""


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


# --- Curated library of real Spanish books + physical-book reading log (LGA-75) ---

def library_by_grade(*, region="", query=""):
    """NATIVE-track catalog grouped by grade in ladder order (Pre-K..8th). CI/adult/
    free books are ungraded by design and are browsed by track instead, so they are
    deliberately excluded here — this function answers "what's at each grade?".
    ``region`` filters by country (substring, case-insensitive); ``query`` searches
    title + author. Returns a list of {grade, label, books, count}."""
    qs = LibraryBook.objects.filter(track=LibraryBook.NATIVE)
    if region:
        qs = qs.filter(country__icontains=region)
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(author__icontains=query))
    label = dict(LibraryBook.GRADE_CHOICES)
    by_grade = {}
    for b in qs:
        by_grade.setdefault(b.grade, []).append(b)
    groups = []
    for g in LibraryBook.GRADE_ORDER:
        books = sorted(by_grade.get(g, []), key=lambda b: b.title.lower())
        if books:
            groups.append({"grade": g, "label": label.get(g, g),
                           "books": books, "count": len(books)})
    return groups


def library_countries():
    """Distinct non-blank countries present in the catalog (for the region filter)."""
    return sorted({c for c in LibraryBook.objects.exclude(country="")
                   .values_list("country", flat=True)})


def get_worklog_sink():
    """The host WorkLogSink adapter named in LINGUA["WORKLOG_SINK"], or None when
    unbound/misconfigured (mirroring is an enhancement, never a hard dependency)."""
    dotted = settings.LINGUA.get("WORKLOG_SINK")
    if not dotted:
        return None
    try:
        return import_string(dotted)()
    except Exception:  # noqa: BLE001 — a bad/absent adapter must not break book logging
        return None


def log_book(learner, *, book=None, title="", author="", read_on=None,
             enjoyed="", note="", logged_by=BookLogEntry.KID, worklog_sink=None):
    """Log a physical book a child finished (LGA-75). Either ``book`` (a catalog
    LibraryBook, whose title/author are snapshotted) or a free-text title. Returns the
    BookLogEntry, or None if there's nothing to log (no book and no title).

    The finished book is ALSO mirrored into the host work log through the WorkLogSink
    port (LGA-76), so it appears in the Work Log and the charter report. Mirroring is
    best-effort: if the sink is unbound or raises, the book log still succeeds."""
    from django.utils import timezone
    t = (book.title if book else title or "").strip()
    if not t:
        return None
    entry = BookLogEntry.objects.create(
        learner=learner, book=book,
        title=(book.title if book else t)[:200],
        author=((book.author if book else author) or "")[:200],
        read_on=read_on or timezone.localdate(),
        enjoyed=enjoyed if enjoyed in dict(BookLogEntry.ENJOYED_CHOICES) else "",
        note=(note or "")[:500],
        logged_by=logged_by if logged_by in dict(BookLogEntry.BY_CHOICES) else BookLogEntry.KID,
    )
    sink = worklog_sink if worklog_sink is not None else get_worklog_sink()
    if sink is not None:
        try:
            rec = sink.record_book(
                host_student_id=learner.host_student_id, title=entry.title,
                author=entry.author, read_on=entry.read_on, note=entry.note,
            )
        except Exception:  # noqa: BLE001 — never fail the child's log on a host hiccup
            rec = None
        if rec:
            entry.host_worklog_id = rec
            entry.save(update_fields=["host_worklog_id"])
    return entry


def book_logs(learner):
    """A learner's physical-book reading log (newest first), for both portals."""
    return list(learner.book_logs.select_related("book").all())


_BAND_GRADES = {
    profiles.KIDS_EARLY: ["PK", "K", "1", "2"],
    profiles.KIDS_OLDER: ["3", "4", "5", "6"],
}


def suggested_books(learner, *, limit=12):
    """A short list of NATIVE-track catalog books at the learner's band, for the kid
    portal's quick 'which book did you read?' picker (the child can still type any
    other title). Ordered by the ladder (Pre-K, K, 1, 2…) — NOT by the grade column,
    which sorts lexicographically ("1" < "2" < "K" < "PK") and would put the hardest
    books first."""
    band = getattr(getattr(learner, "profile", None), "track_profile", "")
    grades = _BAND_GRADES.get(band) or LibraryBook.GRADE_ORDER
    books = LibraryBook.objects.filter(track=LibraryBook.NATIVE, grade__in=grades)
    rank = {g: i for i, g in enumerate(LibraryBook.GRADE_ORDER)}
    return sorted(books, key=lambda b: (rank.get(b.grade, 99), b.title.lower()))[:limit]


def delete_book_log(learner, entry_id, *, worklog_sink=None):
    """Delete one of the learner's own book-log entries, and the host work-log record
    it was mirrored into (LGA-76) so the charter report doesn't keep an orphan.
    Returns True if removed."""
    entry = learner.book_logs.filter(pk=entry_id).first()
    if entry is None:
        return False
    host_id = entry.host_worklog_id
    entry.delete()
    if host_id:
        sink = worklog_sink if worklog_sink is not None else get_worklog_sink()
        if sink is not None:
            try:
                sink.remove(host_id)
            except Exception:  # noqa: BLE001 — best-effort cleanup
                pass
    return True


def band_for_dob(dob):
    """The track band a child of this birth date starts in: KIDS_EARLY under 10, else
    KIDS_OLDER; KIDS_EARLY when the DOB is unknown. The ONE definition — the host
    adapter delegates here rather than keeping its own copy."""
    if not dob:
        return profiles.KIDS_EARLY
    from datetime import date as _date
    today = _date.today()
    # exact calendar age (no leap-day drift from //365 near the boundary)
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return profiles.KIDS_OLDER if age >= 10 else profiles.KIDS_EARLY


def learner_for_child(child):
    """The Learner for a ``directory`` child row, provisioned on first use. ``child`` is
    a plain dict, not a host model — lingua never sees one (D-03/D-04)."""
    return get_or_create_learner(child["pk"], band_for_dob(child.get("date_of_birth")))


def forget_mirror(host_record_id):
    """Drop the book-log rows mirrored into a host record that no longer exists.

    The other half of :func:`delete_book_log`: the parent can also delete the entry
    from the host's own log, and without this the library page would keep showing the
    book as read, pointing at a work-log row that is gone. Deliberately does NOT call
    the sink back — the host record is already deleted. Returns the number removed."""
    if not host_record_id:
        return 0
    deleted, _ = BookLogEntry.objects.filter(host_worklog_id=host_record_id).delete()
    return deleted


# --- Illustrated storybook pictures (LGA-71) ---------------------------------

def get_image_client() -> ImageClient:
    """Instantiate the host-bound ImageClient adapter named in LINGUA["IMAGE_CLIENT"].
    Mirrors :func:`get_ai_client`; services take ``image_client=None`` and fall back to
    this, so tests inject a fake implementing ``ports.ImageClient``."""
    return import_string(settings.LINGUA["IMAGE_CLIENT"])()


def _aspect_ratio(aspect):
    """Parse "W:H" into ints (defaults to 4:3 on anything malformed)."""
    try:
        w, h = aspect.split(":")
        w, h = int(w), int(h)
        if w > 0 and h > 0:
            return w, h
    except (ValueError, AttributeError):
        pass
    return 4, 3


def _process_illustration(raw, aspect, *, max_width=1024):
    """Normalize generated bytes to the fixed aspect (center-crop) and encode as a
    reasonably-sized WebP. Returns ``(bytes, width, height)``. Enforcing the aspect
    here (not only in the prompt) keeps every reader image the same shape even if the
    model drifts. PIL is imported lazily — this runs only at authoring time."""
    from io import BytesIO
    from PIL import Image

    im = Image.open(BytesIO(raw)).convert("RGB")
    aw, ah = _aspect_ratio(aspect)
    target = aw / ah
    w, h = im.size
    if w / h > target:                      # too wide → crop the sides
        nw = int(round(h * target))
        x = (w - nw) // 2
        im = im.crop((x, 0, x + nw, h))
    elif w / h < target:                    # too tall → crop top/bottom
        nh = int(round(w / target))
        y = (h - nh) // 2
        im = im.crop((0, y, w, y + nh))
    if im.size[0] > max_width:
        nh = int(round(max_width * im.size[1] / im.size[0]))
        im = im.resize((max_width, nh), Image.LANCZOS)
    out = BytesIO()
    im.save(out, format="WEBP", quality=82, method=6)
    return out.getvalue(), im.size[0], im.size[1]


def ensure_art_contract(story, *, ai_client=None, force=False):
    """Fill ``story.art_contract`` (character block / setting / tone) via one AI call,
    once per story, so every beat's image prompt shares a consistent visual bible
    (LGA-71). Returns the contract. The story body is fenced (LGA-30) and PII-guarded
    (D-52); the call is billed to the monthly ceiling the instant the provider
    responds. No-op if a contract already exists (unless ``force``)."""
    if story.art_contract and not force:
        return story.art_contract
    if ai_budget_exceeded():
        raise BudgetExceeded("Monthly AI cost ceiling reached — art contract skipped.")
    ai = ai_client or get_ai_client()
    safety.assert_no_pii(story.body, where="art contract")  # D-52 (LGA-31)
    user = safety.fence(story.body, "story") + "\nDesign the visual bible now as JSON."
    result = ai.generate(system=illustrate.ART_CONTRACT_SYSTEM, user=user, max_tokens=400)
    record_ai_usage(result.usage)  # bill before any parse can fail (LGA-29)
    data = _parse_json(result.text)
    contract = {
        "character_block": str(data.get("character_block", "")).strip(),
        "setting": str(data.get("setting", "")).strip(),
        "tone": str(data.get("tone", "")).strip(),
    }
    story.art_contract = contract
    story.save(update_fields=["art_contract", "updated_at"])
    return contract


def _read_image_bytes(key):
    """Read image bytes back from the public store (used to anchor later beats)."""
    st = storage.readalong_storage()
    with st.open(key) as fh:
        return fh.read()


def bake_story_image(story, beat, *, image_client=None, reference_bytes=None, force=False):
    """Bake ONE illustration for a story beat (LGA-71), mirroring bake_story_audio.

    Idempotent by content hash: a current (non-stale) image for the beat returns
    ``(existing, "skipped")`` unless ``force``. Otherwise generates via the ImageClient
    port (passing ``reference_bytes`` — typically the story's first image — as a
    consistency anchor), center-crops to the fixed aspect, uploads the WebP to the
    public path, bills one image against the ceiling, and upserts the StoryImage row;
    returns ``(StoryImage, "baked")``. Raises BudgetExceeded before generating if the
    ceiling is hit, or the provider's error (caught per story by the command)."""
    existing = story.current_image(beat)
    if existing and not force:
        return existing, "skipped"
    if ai_budget_exceeded():
        raise BudgetExceeded("Monthly AI cost ceiling reached — illustration skipped.")
    img = image_client or get_image_client()
    aspect = settings.LINGUA.get("ILLUSTRATION_ASPECT", illustrate.DEFAULT_ASPECT)
    model = settings.LINGUA.get("IMAGE_MODEL", "")
    contract = story.art_contract or {}
    prompt = illustrate.build_art_prompt(
        beat["text"], character_block=contract.get("character_block", ""),
        setting=contract.get("setting", ""), tone=contract.get("tone", ""), aspect=aspect,
    )
    ref_paths, tmp_path = None, None
    if reference_bytes:
        fd, tmp_path = tempfile.mkstemp(suffix=".webp")
        with os.fdopen(fd, "wb") as fh:
            fh.write(reference_bytes)
        ref_paths = [tmp_path]
    try:
        raw = img.generate(prompt, reference_paths=ref_paths)
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    # Bill at the provider seam — the instant generation costs real money — BEFORE any
    # downstream step (PIL decode, R2 upload, row write) can fail and lose the count.
    # Mirrors record_ai_usage in the text path (LGA-29): a billed call must always be
    # counted, or the $25/mo hard-stop under-enforces.
    record_image_usage(1)
    data, w, h = _process_illustration(raw, aspect)
    digest = story.image_hash(beat, model=model, aspect=aspect)
    key = assets.image_key(digest)
    # On a force re-bake the prompt (hence the hash/key) can be unchanged while the
    # generated bytes differ (non-deterministic model), so overwrite rather than skip.
    storage.save_image(key, data, replace=force)
    obj, _ = StoryImage.objects.update_or_create(
        story=story, beat_index=beat["index"], model=model,
        defaults={"content_hash": digest, "image_key": key, "prompt": prompt,
                  "alt_text": beat["text"][:300], "width": w, "height": h},
    )
    return obj, "baked"


def bake_story_images(story, *, ai_client=None, image_client=None, force=False):
    """Bake every illustration for a story: ensure the art contract, then bake each
    beat in order, anchoring beats 1..n to the FIRST image for character consistency
    (LGA-71). Returns a summary dict. BudgetExceeded stops the batch (re-raised)."""
    ensure_art_contract(story, ai_client=ai_client)
    max_beats = settings.LINGUA.get("ILLUSTRATION_MAX_BEATS", 8)
    beat_list = illustrate.beats(story.body, max_beats=max_beats)
    baked = skipped = 0
    anchor = None
    for beat in beat_list:
        obj, action = bake_story_image(
            story, beat, image_client=image_client, reference_bytes=anchor, force=force,
        )
        baked += action == "baked"
        skipped += action == "skipped"
        if beat["index"] == 0:  # the FIRST image anchors every later beat (character consistency)
            try:
                anchor = _read_image_bytes(obj.image_key)
            except Exception:  # noqa: BLE001 — anchor is best-effort; degrade to no-anchor
                anchor = None
    return {"beats": len(beat_list), "baked": baked, "skipped": skipped}


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


# A story is "got it down" (¡lo domina!) — NO grading — when the child has read it at
# least this many times AND their best after-reading self-check on it was proficient+
# (the 😀 "¡Bien!" felt). Read count + this flag are what the parent tracks (LGA-72).
GOT_IT_DOWN_MIN_READS = 2


def story_got_it_down(reads, best_result):
    """True when a story is mastered enough to mark 'got it down': read >= the minimum
    and a proficient+ self-check. Pure so it's trivially testable."""
    return reads >= GOT_IT_DOWN_MIN_READS and comprehension.meets_bar(best_result or "")


def reading_list(learner):
    """Leveled reading list for a learner (LGA-72), modeled on a leveled-books list:
    every APPROVED story grouped by ladder level (L1..L8, only levels that have
    stories), each row carrying the learner's read count and a 'got it down' flag. Used
    by the kid's Biblioteca page and the parent progress page. Read-only; no grading."""
    reads_by_story = {
        r["story"]: r["n"]
        for r in learner.reading_sessions.filter(story__isnull=False)
        .values("story").annotate(n=Count("id"))
    }
    best_by_story = {}
    for sid, result in learner.comprehension_checks.filter(
        story__isnull=False
    ).values_list("story", "result"):
        if comprehension.rank(result) > comprehension.rank(
            best_by_story.get(sid, comprehension.PENDING)
        ):
            best_by_story[sid] = result

    by_level = {}
    for story in Story.objects.filter(status=Story.APPROVED).order_by("level", "title"):
        reads = reads_by_story.get(story.pk, 0)
        by_level.setdefault(story.level, []).append({
            "story": story,
            "reads": reads,
            "got_it_down": story_got_it_down(reads, best_by_story.get(story.pk)),
        })

    ceiling = getattr(getattr(learner, "profile", None), "content_ceiling", None)
    levels = []
    for lvl in profiles.LADDER:
        items = by_level.get(lvl)
        if not items:
            continue
        levels.append({
            "level": lvl,
            "descriptor": profiles.LEVEL_DESCRIPTORS.get(lvl, ""),
            "stories": items,
            "is_current": lvl == ceiling,
            "done": sum(1 for it in items if it["got_it_down"]),
            "total": len(items),
        })
    return levels


# --- Private child read-aloud recordings (LGA-73) ---------------------------

RECORDING_MAX_BYTES = 12 * 1024 * 1024  # ~12MB — a few minutes of opus; rejects abuse
_RECORDING_EXT = {"audio/webm": "webm", "audio/ogg": "ogg",
                  "audio/mp4": "m4a", "audio/mpeg": "mp3"}


def save_story_recording(learner, story, data, *, content_type="", seconds=0):
    """Save a child's read-aloud recording to the PRIVATE recordings store and create a
    StoryRecording (LGA-73). Never sent to any AI/TTS. Raises ValueError if recordings
    aren't configured, the content type isn't an accepted audio type, or the upload is
    empty/oversized. Returns the StoryRecording."""
    import uuid
    if not storage.recordings_enabled():
        raise ValueError("recordings not configured")
    ct = (content_type or "").split(";")[0].strip().lower()
    if ct not in _RECORDING_EXT:              # only real audio types, no arbitrary bytes
        raise ValueError("unsupported content type")
    if not data:
        raise ValueError("empty recording")
    if len(data) > RECORDING_MAX_BYTES:
        raise ValueError("recording too large")
    ext = _RECORDING_EXT[ct]
    key = f"{storage.RECORDING_PREFIX}/{uuid.uuid4().hex}.{ext}"
    stored_key = storage.save_recording(key, data)
    return StoryRecording.objects.create(
        learner=learner, story=story, audio_key=stored_key,
        content_type=(content_type or "")[:64],
        seconds=max(0, min(int(seconds or 0), 86_400)),
    )


def recordings_for(learner):
    """This learner's recordings, newest first, with the story preloaded (parent view)."""
    return list(learner.recordings.select_related("story").all())


def delete_story_recording(learner, recording_id):
    """Delete one of the learner's recordings (storage object + row). Scoped to the
    learner so a parent can only delete their own child's recordings. Returns True if
    something was deleted."""
    rec = learner.recordings.filter(pk=recording_id).first()
    if rec is None:
        return False
    storage.delete_recording(rec.audio_key)
    rec.delete()
    return True


def _normalize_word(word):
    """Canonical key for a Spanish word: the letter-run only (via cognates.WORD_RE) then
    case/diacritic-folded and capped to the 64-char field, so "gato" / "gato." / "¡Gató!"
    all collapse to one key. Returns "" for a blank/punctuation-only token. Shared by the
    known-words counter and the SRS capture so both use identical dedup keys."""
    m = cognates.WORD_RE.search(word or "")
    return cognates.normalize(m.group())[:64] if m else ""


def credit_known_word(learner, word):
    """Credit ``learner`` with knowing ``word`` (stored normalized). Idempotent per
    word — the known-words counter never double-counts (D-60/61). Returns
    ``(KnownWord | None, created)``; a blank/punctuation-only word is a no-op."""
    norm = _normalize_word(word)
    if not norm:
        return None, False
    return KnownWord.objects.get_or_create(learner=learner, word=norm)


# How a review card is presented (F-03, LGA-61) — derived from the scheduler (band),
# so no extra storage: picture-first for the youngest (Leitner), text/cloze+audio for
# older (FSRS). The review-session UI reads this to render the right card shape.
CARD_PICTURE, CARD_TEXT_CLOZE = "picture", "text_cloze"


def card_format_for(scheduler):
    """The card presentation format for a scheduler: picture vs text/cloze+audio."""
    return CARD_PICTURE if scheduler == ReviewItem.LEITNER else CARD_TEXT_CLOZE


def capture_word(learner, word, *, now=None):
    """Capture a word encountered while reading into the learner's review deck (F-03,
    LGA-61). Normalizes the word (so "Gato"/"gato." collapse — no duplicate cards),
    then adds a ReviewItem via the learner's band scheduler (picture-first for
    KIDS_EARLY, text/cloze for KIDS_OLDER). Idempotent and respects the Leitner deck
    cap. Returns the ReviewItem, or None for a blank word or when the deck is full."""
    normalized = _normalize_word(word)
    if not normalized:
        return None
    return add_review_item(learner, normalized, target_kind=ReviewItem.VOCAB, now=now)


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
    reading_minutes = round((agg["secs"] or 0) / 60)
    listen_minutes = learner.listening_sessions.aggregate(m=Sum("minutes"))["m"] or 0
    return {
        "words_read": agg["words"] or 0,
        # "minutes" is total comprehensible-INPUT minutes (reading + listening, D-60/61,
        # LGA-57); listening_minutes/reading_minutes give the breakdown.
        "minutes": reading_minutes + listen_minutes,
        "reading_minutes": reading_minutes,
        "listening_minutes": listen_minutes,
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


def phonics_example_words(example):
    """Split a PhonicsRule.example string ('mesa · piso · luna') into words."""
    if not example:
        return []
    return [w.strip() for w in example.replace("·", " ").split() if w.strip()]


def _clip_lookup(texts, *, voice=None, engine=None, provider="polly"):
    """Map exact text -> current AudioClip URL for the given voice (LGA-84)."""
    voice = voice or settings.LINGUA.get("TTS_VOICE", "Mia")
    engine = engine or settings.LINGUA.get("TTS_ENGINE", "neural")
    texts = [t for t in texts if t]
    if not texts:
        return {}
    out = {}
    for clip in AudioClip.objects.filter(
        text__in=texts, voice=voice, engine=engine, provider=provider,
    ):
        if clip.is_current:
            try:
                out[clip.text] = storage.public_url(clip.audio_key)
            except Exception:  # noqa: BLE001 — missing storage must not 500 the portal
                continue
    return out


def phonics_rules_with_audio(*, voice=None, engine=None):
    """Phonics rules with per-word tap targets + optional audio URLs (LGA-84).

    Each rule becomes ``{rule, words: [{text, audio_url|None}]}``. Missing clips
    degrade to plain text (no dead buttons).
    """
    rules = phonics_rules()
    all_words = []
    for rule in rules:
        all_words.extend(phonics_example_words(rule.example))
    urls = _clip_lookup(all_words, voice=voice, engine=engine)
    result = []
    for rule in rules:
        words = [{"text": w, "audio_url": urls.get(w)} for w in phonics_example_words(rule.example)]
        result.append({"rule": rule, "words": words})
    return result


def listening_resources(age_band):
    """Active curated listening items for a band, ordered (F-02/N-02, LGA-55/56)."""
    return list(ListeningResource.objects.filter(age_band=age_band, active=True))


def tutor_packets_for(host_student_id):
    """Active tutor packets visible to a host student (LGA-85).

    A packet with ``host_student_id`` NULL is shared; otherwise it must match.
    """
    return list(
        TutorPacket.objects.filter(active=True).filter(
            Q(host_student_id__isnull=True) | Q(host_student_id=host_student_id)
        )
    )


def tutor_packet_for(host_student_id, packet_id):
    """One visible TutorPacket or None (LGA-85)."""
    return (
        TutorPacket.objects.filter(pk=packet_id, active=True)
        .filter(Q(host_student_id__isnull=True) | Q(host_student_id=host_student_id))
        .first()
    )


def alphabet_tiles():
    """Active alphabet / digraph tiles in chart order (LGA-86)."""
    return list(AlphabetTile.objects.filter(active=True))


def alphabet_tiles_with_audio(*, voice=None, engine=None):
    """Alphabet tiles with spoken + example audio URLs when baked (LGA-86)."""
    tiles = alphabet_tiles()
    texts = []
    for t in tiles:
        texts.append(t.spoken)
        if t.example:
            texts.append(t.example)
    urls = _clip_lookup(texts, voice=voice, engine=engine)
    return [
        {
            "tile": t,
            "spoken_url": urls.get(t.spoken),
            "example_url": urls.get(t.example) if t.example else None,
        }
        for t in tiles
    ]


def practice_phrases_for(host_student_id, *, voice=None, engine=None):
    """Practice lines from visible tutor packets, with audio when baked (LGA-86)."""
    phrases = []
    for packet in tutor_packets_for(host_student_id):
        for line in packet.phrase_lines():
            phrases.append({"text": line, "packet_id": packet.pk, "audio_url": None})
    urls = _clip_lookup([p["text"] for p in phrases], voice=voice, engine=engine)
    for p in phrases:
        p["audio_url"] = urls.get(p["text"])
    return phrases


def bake_audio_clip(text, *, voice=None, engine=None, provider="polly",
                    link_only=False, force=False, client=None):
    """Bake or link one AudioClip (LGA-84/86). Idempotent by content hash.

    Returns ``(AudioClip, "baked"|"linked"|"skipped")``. ``link_only`` requires the
    mp3 already in the public store. Never call from a request path.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Cannot bake an empty clip.")
    voice = voice or settings.LINGUA.get("TTS_VOICE", "Mia")
    engine = engine or settings.LINGUA.get("TTS_ENGINE", "neural")
    digest = assets.content_hash(text, provider=provider, voice=voice, engine=engine)
    key = assets.clip_key(digest)
    existing = AudioClip.objects.filter(
        text=text, voice=voice, engine=engine, provider=provider,
    ).first()
    if existing and existing.content_hash == digest and not force:
        return existing, "skipped"
    if link_only:
        if not storage.readalong_storage().exists(key):
            raise FileNotFoundError(f"Clip asset missing for link-only: {key}")
        action = "linked"
    else:
        out = audio.synthesize_clip(text, voice=voice, engine=engine, client=client)
        storage.save_audio(key, out["audio"])
        action = "baked"
    obj, _ = AudioClip.objects.update_or_create(
        text=text, voice=voice, engine=engine, provider=provider,
        defaults={"content_hash": digest, "audio_key": key, "duration_ms": 0},
    )
    return obj, action


def clip_texts_to_bake(*, phonics=False, alphabet=False, phrases=False):
    """Collect unique texts that need AudioClip rows (authoring inventory)."""
    texts = []
    if phonics:
        for rule in PhonicsRule.objects.filter(active=True):
            texts.extend(phonics_example_words(rule.example))
    if alphabet:
        for tile in AlphabetTile.objects.filter(active=True):
            texts.append(tile.spoken)
            if tile.example:
                texts.append(tile.example)
    if phrases:
        for packet in TutorPacket.objects.filter(active=True):
            texts.extend(packet.phrase_lines())
    # Preserve order, drop dupes / blanks
    seen, out = set(), []
    for t in texts:
        t = (t or "").strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def record_listening(learner, resource, minutes):
    """Log a listening check-in — minutes of comprehensible input toward the hero metric
    (F-02/N-02, LGA-55/57). ``minutes`` is clamped to a sane 0..600 so a fat-fingered or
    hostile value can't inflate the metric. A 0-minute log is a no-op (returns None)."""
    mins = max(0, min(int(minutes or 0), 600))
    if mins == 0:
        return None
    return ListeningSession.objects.create(learner=learner, resource=resource, minutes=mins)


MAX_ACTIVE_LEITNER_ITEMS = 15   # deck-size cap for the young Leitner learner (D-31)


def scheduler_for_learner(learner):
    """Which SRS scheduler a learner uses (D-31/D-32): Leitner for the youngest band
    (parent-graded, picture-first), FSRS (two-button) for everyone older."""
    return (ReviewItem.LEITNER
            if learner.profile.track_profile == profiles.KIDS_EARLY
            else ReviewItem.FSRS)


def add_review_item(learner, target_ref, *, target_kind=ReviewItem.VOCAB,
                    scheduler=None, now=None):
    """Add a card to the learner's deck, seeded by their scheduler and due now (LGA-59).
    ``scheduler`` defaults to the learner's band scheduler (scheduler_for_learner).
    Idempotent per (learner, kind, ref) — a repeat target returns the existing card
    unchanged, even at the cap. For Leitner, enforces the <=15 active-deck cap so a
    young child isn't overwhelmed (D-31): at the cap, returns None and adds nothing."""
    now = now or timezone.now()
    scheduler = scheduler or scheduler_for_learner(learner)
    # Idempotent FIRST: an already-tracked target returns its existing card regardless
    # of the cap (LGA-61 auto-capture re-encounters known words at the cap constantly —
    # it must get the card back, not None).
    existing = ReviewItem.objects.filter(
        learner=learner, target_kind=target_kind, target_ref=target_ref).first()
    if existing:
        return existing
    # New card only: enforce the <=15 active Leitner deck cap so a young child is not
    # overwhelmed (D-31).
    if (scheduler == ReviewItem.LEITNER
            and ReviewItem.objects.filter(learner=learner, scheduler=ReviewItem.LEITNER)
            .count() >= MAX_ACTIVE_LEITNER_ITEMS):
        return None
    sched = schedulers.get_scheduler(scheduler)
    item, _ = ReviewItem.objects.get_or_create(  # get_or_create still guards a create race
        learner=learner, target_kind=target_kind, target_ref=target_ref,
        defaults={"scheduler": scheduler, "scheduler_state": sched.initial_state(), "due": now},
    )
    return item


def grade_review_item(item, correct, *, now=None):
    """Apply a review grade to a card via its scheduler (LGA-59). ``correct`` comes from
    a parent tap (got-it/missed) or an auto-graded recognition match — the scheduler
    handles both identically. A miss is non-punitive (Leitner resets to box 1).
    Strong correct vocab grades also credit KnownWord (LGA-89)."""
    now = now or timezone.now()
    sched = schedulers.get_scheduler(item.scheduler)
    item.scheduler_state, item.due = sched.review(item.scheduler_state, correct, now=now)
    item.save(update_fields=["scheduler_state", "due", "updated_at"])
    record_reviews_served(item.learner, now=now)   # count toward the per-day cap (LGA-62)
    if correct and item.target_kind == ReviewItem.VOCAB:
        _maybe_credit_known_from_review(item)
    return item


def _maybe_credit_known_from_review(item):
    """Credit KnownWord after a strong SRS hit (LGA-89): FSRS Good, or Leitner box
    at/above the warm-start threshold (same bar as graduate_to_fsrs)."""
    if item.scheduler == ReviewItem.FSRS:
        credit_known_word(item.learner, item.target_ref)
        return
    try:
        box = int((item.scheduler_state or {}).get("box", 1))
    except (TypeError, ValueError):
        return
    if box >= FSRS_WARM_START_BOX:
        credit_known_word(item.learner, item.target_ref)


def auto_grade_recognition(item, chosen, correct, *, now=None):
    """Auto-grade an unambiguous recognition card (tap the matching picture) without a
    parent (D-31): the tap is objectively right/wrong. A miss just resets the box.
    A missing tap (chosen is None) is a miss, never a None==None false 'correct'."""
    is_match = chosen is not None and chosen == correct
    return grade_review_item(item, is_match, now=now)


FSRS_WARM_START_BOX = 4   # Leitner box at/above which a graduating card is warm-started (D-64)


def graduate_to_fsrs(item, *, now=None):
    """Graduate a Leitner card to FSRS (D-64, LGA-63): keep the SAME ReviewItem + target,
    DISCARD the Leitner box, and start a FRESH FSRS Card. A well-known card (Leitner box
    >= FSRS_WARM_START_BOX) gets exactly ONE synthetic Good review as a warm-start so it
    isn't treated as brand-new; lower boxes start cold (due now for their first FSRS
    review). We NEVER convert box -> stability/difficulty arithmetically — just a fresh
    card plus at most one synthetic Good, so the warm-start is identical for every
    high box (no box-proportional math). No-op if the card is already FSRS."""
    if item.scheduler == ReviewItem.FSRS:
        return item
    now = now or timezone.now()
    try:
        box = int((item.scheduler_state or {}).get("box", 1))
    except (TypeError, ValueError):
        box = 1   # corrupt/non-numeric box -> start cold, never 500 a graduation
    fsrs = schedulers.get_scheduler(ReviewItem.FSRS)
    if box >= FSRS_WARM_START_BOX:
        state, due = fsrs.review(fsrs.initial_state(), True, now=now)  # one synthetic Good
    else:
        state, due = fsrs.initial_state(), now                        # cold: due now
    item.scheduler = ReviewItem.FSRS
    item.scheduler_state = state
    item.due = due
    item.save(update_fields=["scheduler", "scheduler_state", "due", "updated_at"])
    return item


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


def _reviews_served_today(profile, today):
    """How many reviews the learner has already completed on ``today`` (0 if the stored
    counter is for an earlier date — i.e. it has rolled over)."""
    return profile.reviews_served_count if profile.reviews_served_on == today else 0


def record_reviews_served(learner, n=1, *, now=None):
    """Count ``n`` completed reviews toward today's per-day cap (D-66/N-05, LGA-62).
    Resets the counter when the learner's LOCAL date rolls over."""
    now = now or timezone.now()
    today = timezone.localdate(now)
    profile = learner.profile
    if profile.reviews_served_on == today:
        profile.reviews_served_count += n
    else:
        profile.reviews_served_on = today
        profile.reviews_served_count = n
    profile.save(update_fields=["reviews_served_on", "reviews_served_count", "updated_at"])


def daily_review_queue(learner, *, now=None):
    """The bounded set of cards to review right now (D-66/N-05, LGA-62).

    Guards on top of ``due_review_items``: (1) during a declared absence
    (``profile.paused_until`` in the future) NOTHING surfaces — the break doesn't turn
    into a chore; (2) intake is a PER-DAY quota by support_level — the cap MINUS the
    reviews already completed today (``grade_review_item`` records each). So re-querying
    within a day can't keep pulling the next batch and drain a huge overdue backlog in
    one sitting; it drains over DAYS, resetting each local date."""
    now = now or timezone.now()
    profile = learner.profile
    if profile.paused_until and now < profile.paused_until:
        return []
    cap = profiles.daily_review_cap(profile.support_level)
    remaining = cap - _reviews_served_today(profile, timezone.localdate(now))
    if remaining <= 0:
        return []
    return due_review_items(learner, now=now)[:remaining]


def pause_reviews(learner, until):
    """Declare an absence: freeze the review queue until ``until`` (D-66/N-05)."""
    profile = learner.profile
    profile.paused_until = until
    profile.save(update_fields=["paused_until", "updated_at"])


def resume_reviews(learner):
    """End an absence pause early — reviews resume (capped) immediately."""
    profile = learner.profile
    profile.paused_until = None
    profile.save(update_fields=["paused_until", "updated_at"])


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
    """Estimated AI spend for the current calendar month (0.0 if nothing recorded) —
    text tokens PLUS per-image illustration spend, sharing the one ceiling (LGA-71)."""
    row = AiUsage.objects.filter(period=_current_period()).first()
    if not row:
        return 0.0
    image_cost = (row.images or 0) * settings.LINGUA.get("IMAGE_PRICE_PER_IMAGE_USD", 0.0)
    return estimated_cost_usd(row.input_tokens, row.output_tokens) + image_cost


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


def record_image_usage(n=1):
    """Accumulate ``n`` illustration generations into the current month (LGA-71).
    Atomic F() increment so a batch img_build can't lose a count; folded into the
    monthly cost ceiling via :func:`month_to_date_cost_usd`."""
    period = _current_period()
    AiUsage.objects.get_or_create(period=period)
    AiUsage.objects.filter(period=period).update(
        images=F("images") + int(n or 0),
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


# --- Camino pathway overlay (LGA-88) ---------------------------------------

PATH_LOCKED, PATH_AVAILABLE, PATH_COMPLETE = "locked", "available", "complete"


def pathway_for(learner):
    """Active Pathway for the learner's age band, or None."""
    band = getattr(getattr(learner, "profile", None), "track_profile", "")
    if not band:
        return None
    return (
        Pathway.objects.filter(age_band=band, active=True)
        .order_by("order", "id")
        .first()
    )


def _stories_read_at_level(learner, level):
    """Distinct approved-story pks at ``level`` the learner has read at least once."""
    return set(
        learner.reading_sessions.filter(story__level=level, story__isnull=False)
        .values_list("story_id", flat=True)
        .distinct()
    )


def _step_complete(learner, step):
    """Derive whether a PathwayStep is done from existing session/mastery data."""
    kind, ref = step.kind, (step.target_ref or "").strip()
    rule = step.pass_rule or {}

    if kind == PathwayStep.STORY:
        if not ref.isdigit():
            return False
        return learner.reading_sessions.filter(story_id=int(ref)).exists()

    if kind == PathwayStep.STORY_LEVEL:
        level = ref or "L1"
        min_stories = int(rule.get("min_stories", 1))
        return len(_stories_read_at_level(learner, level)) >= min_stories

    if kind == PathwayStep.PHONICS:
        # Soft: any reading engagement counts as having started sonidos station.
        return learner.reading_sessions.exists() or rule.get("soft", False)

    if kind == PathwayStep.LISTEN:
        return learner.listening_sessions.exists()

    if kind == PathwayStep.TUTOR_PACKET:
        # No open/ack model yet — only mark complete when pass_rule explicitly soft.
        if not rule.get("soft"):
            return False
        packets = tutor_packets_for(learner.host_student_id)
        if ref.isdigit():
            return any(p.pk == int(ref) for p in packets)
        return bool(packets)

    if kind == PathwayStep.REVIEW:
        min_known = int(rule.get("min_known", 1))
        return learner.known_words.count() >= min_known

    if kind == PathwayStep.LINK:
        return bool(rule.get("soft", False))

    return False


def _step_ceiling_ok(learner, step):
    """story_level steps stay locked until content_ceiling reaches that level."""
    if step.kind != PathwayStep.STORY_LEVEL:
        return True
    level = (step.target_ref or "").strip() or "L1"
    return profiles.level_rank(level) <= profiles.level_rank(learner.profile.content_ceiling)


def _step_visible(learner, step):
    """Hide Kaylin-only tutor steps when the packet isn't for this child."""
    if step.kind != PathwayStep.TUTOR_PACKET:
        return True
    ref = (step.target_ref or "").strip()
    packets = tutor_packets_for(learner.host_student_id)
    if ref.isdigit():
        return any(p.pk == int(ref) for p in packets)
    return bool(packets)


def pathway_status(learner):
    """Ordered Camino stops with derived locked/available/complete (LGA-88).

    Unlock: prior *required* steps must be complete; story_level also needs
    ``content_ceiling``. Optional steps never block later unlocks. Returns
    ``{"pathway": Pathway|None, "steps": [...], "next": dict|None, "hint": str}``.
    """
    pathway = pathway_for(learner)
    if pathway is None:
        return {"pathway": None, "steps": [], "next": None, "hint": ""}

    steps = list(pathway.steps.all())
    prior_required_done = True
    out = []
    next_available = None

    for step in steps:
        if not _step_visible(learner, step):
            continue
        complete = _step_complete(learner, step)
        ceiling_ok = _step_ceiling_ok(learner, step)
        if complete:
            status = PATH_COMPLETE
        elif prior_required_done and ceiling_ok:
            status = PATH_AVAILABLE
        else:
            status = PATH_LOCKED

        row = {
            "step": step,
            "status": status,
            "practicar": complete and step.kind in (
                PathwayStep.STORY, PathwayStep.STORY_LEVEL, PathwayStep.PHONICS,
                PathwayStep.LISTEN, PathwayStep.TUTOR_PACKET,
            ),
        }
        out.append(row)
        if status == PATH_AVAILABLE and next_available is None:
            next_available = row
        if not step.optional and not complete:
            prior_required_done = False

    hint = ""
    if next_available is not None:
        s = next_available["step"]
        hint = f"Siguiente en el camino: {s.title}"

    return {
        "pathway": pathway,
        "steps": out,
        "next": next_available,
        "hint": hint,
    }


def camino_plan_extras(learner):
    """Light Camino context for the Hoy page without mutating build_daily_plan."""
    status = pathway_status(learner)
    due = due_review_items(learner)
    return {
        "camino_hint": status.get("hint") or "",
        "review_due": len(due) > 0,
        "pathway_status": status,
    }
