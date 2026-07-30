"""Lingua core models — the extractable learner domain.

D-03 (load-bearing): NO ForeignKey from lingua to any host model, EVER. The
learner is a host ``students.Student`` referenced by a plain ``host_student_id``
integer, resolved at display time through the UserDirectory adapter (LGA-17).
FKs *within* lingua are ordinary CASCADE relations.
"""

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from . import comprehension, profiles


class Learner(models.Model):
    """A language learner. Maps 1:1 to a host ``students.Student`` via a plain
    integer id (NOT a ForeignKey) so the module stays extractable (D-03)."""

    # NOT a ForeignKey. Resolve name/level via lingua.integrations.directory.
    host_student_id = models.IntegerField(
        unique=True,
        db_index=True,
        help_text="students.Student.pk on the host. Deliberately not an FK (D-03).",
    )
    language = models.CharField(max_length=8, default="es")
    variant = models.CharField(max_length=16, default="es-MX")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["host_student_id"]

    def __str__(self):
        # No host import — identify by the plain id (name comes from the adapter).
        return f"Learner<host_student_id={self.host_student_id}>"

    ALLOWED_OVERRIDES = {"language", "variant", "support_level", "content_ceiling"}

    @classmethod
    @transaction.atomic
    def create_for_host_student(cls, host_student_id, track_profile, **overrides):
        """Create a Learner + its LearnerProfile, seeded from the track's
        DEFAULTS (profiles.PROFILES). ``overrides`` may set language / variant /
        support_level / content_ceiling independently of the defaults (D-64/65).
        Unknown override keys raise, to catch typos before the service layer."""
        unknown = set(overrides) - cls.ALLOWED_OVERRIDES
        if unknown:
            raise ValueError(f"Unknown override(s): {sorted(unknown)}")
        defaults = profiles.defaults_for(track_profile)
        cfg = getattr(settings, "LINGUA", {})
        learner = cls.objects.create(
            host_student_id=host_student_id,
            language=overrides.get("language", cfg.get("DEFAULT_LANGUAGE", "es")),
            variant=overrides.get("variant", cfg.get("DEFAULT_VARIANT", "es-MX")),
        )
        LearnerProfile.objects.create(
            learner=learner,
            track_profile=track_profile,
            support_level=overrides.get("support_level", defaults["support_level"]),
            content_ceiling=overrides.get("content_ceiling", defaults["default_ceiling"]),
        )
        return learner


class LearnerProfile(models.Model):
    """Per-learner pedagogical config as two INDEPENDENT axes (D-64):
    ``support_level`` (scaffolding + session cap) and ``content_ceiling``
    (how far up the L1..L8 ladder). The track profile only seeds these."""

    learner = models.OneToOneField(
        Learner, on_delete=models.CASCADE, related_name="profile",
    )
    track_profile = models.CharField(max_length=16, choices=profiles.TRACK_CHOICES)
    support_level = models.CharField(max_length=16, choices=profiles.SUPPORT_CHOICES)
    content_ceiling = models.CharField(max_length=4, choices=profiles.LEVEL_CHOICES)
    # Debounce anchor for the D-67 "testing above defaults" parent nudge: the reading-
    # session count when the nudge was last shown (None = never). Nudge again only
    # after ~5 more sessions, so it never nags.
    last_nudge_reading_count = models.IntegerField(null=True, blank=True, default=None)
    # Absence pause (D-66/N-05, LGA-62): while now < paused_until, no reviews surface,
    # so a declared break (vacation/illness) doesn't accrue a due-now backlog. On
    # return, the daily cap bounds intake so the backlog drains over several sessions.
    paused_until = models.DateTimeField(null=True, blank=True, default=None)
    # Per-DAY review-intake counter (D-66/N-05, LGA-62): reviews completed on
    # ``reviews_served_on`` (local date). daily_review_queue subtracts this from the cap
    # so a re-query within a day can't drain the whole overdue backlog — it drains over
    # DAYS. Reset when the local date rolls over.
    reviews_served_on = models.DateField(null=True, blank=True, default=None)
    reviews_served_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.track_profile}/{self.support_level}/{self.content_ceiling}"

    @property
    def session_minutes(self):
        """Hard session-length cap — a function of support_level, NOT of the
        content level (D-66): harder material never lengthens the session."""
        return profiles.session_minutes_for(self.support_level)


class AuditEvent(models.Model):
    """An audit trail of DECISIONS and data-touching events — never payloads (D-57).

    We deliberately do NOT store prompts, model outputs, or child free-text here:
    logging those would duplicate child data into a second store and undercut D-52.
    An event records WHO did WHAT to WHICH record, plus small structured metadata
    (model name, token counts, level proposed-vs-final). No FK to Learner or any
    host model, so the trail survives the subject's deletion (the point of audit)
    and stays extractable (D-03)."""

    # actor types
    PARENT, CHILD, SYSTEM, AI = "parent", "child", "system", "ai"
    ACTOR_CHOICES = [
        (PARENT, "Parent"), (CHILD, "Child"), (SYSTEM, "System"), (AI, "AI"),
    ]

    # Closed action vocabulary — record() rejects anything else, so a typo can't
    # silently create an un-queryable action. Grow this set deliberately.
    ACTIONS = {
        "ai.generate_requested", "ai.generate_completed", "ai.generate_failed",
        "content.approved", "content.rejected",
        "learner.created", "learner.deleted", "learner.advanced",
        "data.exported", "data.purged",
    }

    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    actor_type = models.CharField(max_length=8, choices=ACTOR_CHOICES, default=SYSTEM)
    actor_id = models.IntegerField(null=True, blank=True, help_text="Host user id or Student id — never a name.")
    action = models.CharField(max_length=40)  # covered by the (action, ts) composite index
    target_type = models.CharField(max_length=40, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    summary = models.CharField(max_length=200, blank=True, help_text="Short human line — no child free-text.")
    metadata = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-ts"]
        indexes = [models.Index(fields=["action", "ts"])]

    def __str__(self):
        when = f"{self.ts:%Y-%m-%d %H:%M}" if self.ts else "unsaved"
        return f"{self.action} @ {when}"

    # Max length of any string value in metadata — structured facts are short
    # (model names, token counts). Longer = someone smuggling a payload (D-57).
    METADATA_STR_MAX = 200

    @classmethod
    def record(cls, action, *, actor_type="system", actor_id=None, target_type="",
               target_id=None, summary="", metadata=None, ip=None):
        """Write one audit event. ``action`` must be in ACTIONS (closed vocab).
        Pass only structured facts — NEVER a prompt, answer, or child free-text.
        Long string values in ``metadata`` are rejected to enforce that (D-57)."""
        if action not in cls.ACTIONS:
            raise ValueError(f"Unknown audit action: {action!r}")
        metadata = metadata or {}
        for key, value in metadata.items():
            if isinstance(value, str) and len(value) > cls.METADATA_STR_MAX:
                raise ValueError(
                    f"Audit metadata[{key!r}] is too long — the audit trail stores "
                    f"decisions, not payloads (D-57)."
                )
        return cls.objects.create(
            action=action, actor_type=actor_type, actor_id=actor_id,
            target_type=target_type, target_id=target_id,
            summary=(summary or "")[:200], metadata=metadata, ip=ip,
        )


class AiUsage(models.Model):
    """Monthly AI token accounting for the cost ceiling (D-52/57, LGA-29).

    One aggregate row per calendar month (``period`` = "YYYY-MM"). Story generation
    is operator content-authoring (not per-child), so a single monthly total is the
    right grain. ``services.record_ai_usage`` accumulates tokens here after each AI
    call; ``services.ai_budget_exceeded`` reads it to hard-stop new generation once
    the estimated spend reaches ``LINGUA["MONTHLY_COST_CEILING_USD"]``."""

    period = models.CharField(max_length=7, unique=True, help_text='Calendar month, "YYYY-MM".')
    input_tokens = models.PositiveBigIntegerField(default=0)
    output_tokens = models.PositiveBigIntegerField(default=0)
    calls = models.PositiveIntegerField(default=0)
    # Illustration generations this month (LGA-71). Priced per-image (not per-token),
    # folded into the same monthly ceiling so image spend can't blow the cap either.
    images = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period"]

    def __str__(self):
        return f"AiUsage<{self.period}: {self.input_tokens}in/{self.output_tokens}out>"


class PhonicsRule(models.Model):
    """One Spanish-specific decoding rule for the seeded phonics mini-lesson (F-04,
    LGA-64) — ñ, ll, rr, j, g/gu, silent h, pure vowels, accents. Content-only (no
    learner FK); seeded idempotently by ``seed_phonics``. Not a subsystem: synced-audio
    reading is already implicit phonics for Spanish's shallow orthography."""

    pattern = models.CharField(max_length=12, unique=True)
    title = models.CharField(max_length=80)
    tip = models.CharField(max_length=240)
    example = models.CharField(max_length=120, help_text="Practice words for decoding.")
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "pattern"]

    def __str__(self):
        return f"PhonicsRule<{self.pattern}>"


class Theme(models.Model):
    """A content theme for the age-banded rotation (D-51, N-01). The daily plan
    draws a learner's next-story choices from active themes matching their band."""

    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    age_band = models.CharField(max_length=16, choices=profiles.TRACK_CHOICES)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["age_band", "name"]

    def __str__(self):
        return self.name


class Story(models.Model):
    """A leveled Spanish reading text. Content-bearing, so it carries ``language``
    (D-02). Only AI-generated stories and public-domain texts are ever stored/
    rendered — never copyrighted book text (D-47).

    The draft→approve lifecycle lives on ``status`` (one table, mirroring the
    host's Material pattern) rather than a separate ContentDraft: AI drafts land
    as PENDING_APPROVAL, a parent approves, and only APPROVED stories are servable
    (D-48/49/50). ``approved_by`` is a plain host user id — NO FK (D-03)."""

    DRAFT, PENDING, APPROVED, REJECTED = (
        "draft", "pending_approval", "approved", "rejected",
    )
    STATUS_CHOICES = [
        (DRAFT, "Draft"), (PENDING, "Pending approval"),
        (APPROVED, "Approved"), (REJECTED, "Rejected"),
    ]
    SOURCE_GENERATED, SOURCE_PUBLIC_DOMAIN = "generated", "public_domain"
    SOURCE_CHOICES = [
        (SOURCE_GENERATED, "AI-generated"), (SOURCE_PUBLIC_DOMAIN, "Public domain"),
    ]

    language = models.CharField(max_length=8, default="es")
    variant = models.CharField(max_length=16, default="es-MX")
    title = models.CharField(max_length=200)
    body = models.TextField()
    level = models.CharField(max_length=4, choices=profiles.LEVEL_CHOICES)
    theme = models.ForeignKey(
        Theme, null=True, blank=True, on_delete=models.SET_NULL, related_name="stories",
    )
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_GENERATED)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=DRAFT)  # covered by the (status, level) index
    # LLM-critic pre-filter results (D-49), populated by the generation pipeline.
    critic_passed = models.BooleanField(null=True, blank=True)
    critic_flags = models.JSONField(default=list, blank=True)
    # Frequency-band leveling signal (D-25, LGA-44) — soft, atop the hand/requested
    # level: what level the text reads as, and its out-of-band (rare) words.
    suggested_level = models.CharField(max_length=4, blank=True)
    flagged_words = models.JSONField(default=list, blank=True)
    out_of_band_pct = models.FloatField(default=0.0)
    # Per-story illustration "art contract" (LGA-71): a small locked visual bible —
    # {character_block, setting, tone} — extracted once by the image pipeline and
    # appended to every beat's prompt so the character/look stays consistent across
    # a story's images. Empty until img_build fills it. No child PII (D-52).
    art_contract = models.JSONField(default=dict, blank=True)
    # Approval (D-49/50). approved_by is a plain host user id — NO FK (D-03).
    approved_by = models.IntegerField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "level"])]

    def __str__(self):
        return f"{self.title} ({self.level}, {self.status})"

    @property
    def is_servable(self):
        """Only approved content is ever shown to a learner (D-49)."""
        return self.status == self.APPROVED

    def audio_hash(self, voice, engine, provider="polly"):
        """Content-addressed hash of THIS story's current body in a given voice
        (LGA-37). Changes whenever the body/voice/engine changes, so a baked asset
        can be checked for staleness."""
        from . import assets
        return assets.content_hash(self.body, provider=provider, voice=voice, engine=engine)

    def current_audio(self, voice, engine, provider="polly"):
        """The fresh StoryAudio for (voice, engine), or None if it's missing or
        stale (i.e. the story text changed since it was baked)."""
        want = self.audio_hash(voice, engine, provider=provider)
        return self.audios.filter(
            voice=voice, engine=engine, provider=provider, content_hash=want,
        ).first()

    def image_hash(self, beat, *, model=None, aspect=None):
        """Content-addressed hash for ONE illustration beat of this story (LGA-71) —
        over the image model, the fixed house style, this story's character block, the
        aspect ratio, and the beat's scene text. Changes whenever any of those change,
        so a baked image can be checked for staleness."""
        from django.conf import settings
        from . import assets, illustrate
        model = model or settings.LINGUA.get("IMAGE_MODEL", "")
        aspect = aspect or settings.LINGUA.get("ILLUSTRATION_ASPECT", illustrate.DEFAULT_ASPECT)
        contract = self.art_contract or {}
        scene = illustrate.scene_from_beat(beat["text"])
        return assets.image_content_hash(
            model=model, style=illustrate.HOUSE_STYLE,
            character_block=contract.get("character_block", ""),
            setting=contract.get("setting", ""), tone=contract.get("tone", ""),
            aspect=aspect, scene=scene,
        )

    def current_image(self, beat, *, model=None, aspect=None):
        """The fresh StoryImage for a beat, or None if missing or stale (the story
        text or art contract changed since it was baked)."""
        want = self.image_hash(beat, model=model, aspect=aspect)
        return self.images.filter(beat_index=beat["index"], content_hash=want).first()

    @transaction.atomic
    def approve(self, host_user_id):
        """Parent approves this story for serving. Records an audit event (D-57).
        Atomic so the status change and its audit trail commit together."""
        self.status = self.APPROVED
        self.approved_by = host_user_id
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        AuditEvent.record(
            "content.approved", actor_type=AuditEvent.PARENT, actor_id=host_user_id,
            target_type="Story", target_id=self.pk, summary=f"approved {self.level}",
        )

    @transaction.atomic
    def reject(self, host_user_id):
        """Parent rejects this draft. Clears any prior approval provenance and
        records an audit event (D-57)."""
        self.status = self.REJECTED
        self.approved_by = None
        self.approved_at = None
        self.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        AuditEvent.record(
            "content.rejected", actor_type=AuditEvent.PARENT, actor_id=host_user_id,
            target_type="Story", target_id=self.pk, summary=f"rejected {self.level}",
        )


class StoryAudio(models.Model):
    """A baked read-along asset for a Story in one voice (LGA-37, D-16/D-21/N-04).

    Content-addressed: ``content_hash`` = assets.content_hash(story.body, provider,
    voice, engine). When the story text or voice changes the hash changes, so a stale
    row is detectable (``is_current``) and re-baked by ``tts_build``; the old R2 object
    is simply orphaned. One row per (story, voice, engine), updated in place on
    regenerate. The flat timing JSON (D-21) is stored INLINE — it's small and the
    reader embeds it in the CSP-clean page (no cross-origin fetch), so only the larger
    mp3 lives in R2 (``audio_key``, LGA-36). The FK to Story is a lingua-internal
    CASCADE — no FK to any host model (D-03)."""

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="audios")
    provider = models.CharField(max_length=16, default="polly")
    voice = models.CharField(max_length=32)
    engine = models.CharField(max_length=16, default="neural")
    content_hash = models.CharField(max_length=64, db_index=True)
    audio_key = models.CharField(max_length=200, help_text="R2 object key for the mp3.")
    timings = models.JSONField(default=dict, blank=True, help_text="Flat read-along timing JSON (D-21).")
    duration_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["story_id", "voice"]
        constraints = [
            # provider is a first-class identity axis (it's in content_hash,
            # current_audio, and is_current), so it belongs in the uniqueness key
            # too — this lets a future edge-tts asset (D-17/18) coexist with the
            # Polly one for the same (story, voice, engine).
            models.UniqueConstraint(
                fields=["story", "voice", "engine", "provider"],
                name="uniq_story_voice_engine_provider",
            ),
        ]

    def __str__(self):
        return f"StoryAudio<story={self.story_id} {self.voice}/{self.engine}>"

    @property
    def is_current(self):
        """True if this asset was baked from the story's CURRENT text (not stale)."""
        return self.content_hash == self.story.audio_hash(
            self.voice, self.engine, provider=self.provider,
        )


class StoryImage(models.Model):
    """One illustrated-storybook picture for a Story beat (LGA-71, D-16/N-04).

    One image per 1–2 sentences (a "beat"). Content-addressed exactly like StoryAudio:
    ``content_hash`` = assets.image_content_hash(model, house style, character block,
    aspect, beat scene). Editing the story text, the art contract, or the house style
    changes the hash → a stale row is detectable (``is_current``) and re-baked by
    ``img_build``; the old R2 object is orphaned. One row per (story, beat_index,
    model), updated in place on regenerate. The image bytes live on the public R2
    read-along path (LGA-36); ``prompt`` is kept for the AI-content disclosure and
    reproducibility. FK to Story is a lingua-internal CASCADE — no host FK (D-03)."""

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="images")
    beat_index = models.IntegerField(help_text="0-based index of the 1–2 sentence beat.")
    content_hash = models.CharField(max_length=64, db_index=True)
    image_key = models.CharField(max_length=200, help_text="R2 object key for the image.")
    model = models.CharField(max_length=64, blank=True, help_text="Image model id (disclosure).")
    prompt = models.TextField(blank=True, help_text="Exact prompt sent (disclosure/repro).")
    alt_text = models.CharField(max_length=300, blank=True, help_text="The sentences it depicts.")
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["story_id", "beat_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["story", "beat_index", "model"],
                name="uniq_story_beat_model",
            ),
        ]

    def __str__(self):
        return f"StoryImage<story={self.story_id} beat={self.beat_index}>"

    @property
    def is_current(self):
        """True if this image was baked from the story's CURRENT beats + contract."""
        from django.conf import settings
        from . import illustrate
        max_beats = settings.LINGUA.get("ILLUSTRATION_MAX_BEATS", 8)
        beat = next(
            (b for b in illustrate.beats(self.story.body, max_beats=max_beats)
             if b["index"] == self.beat_index),
            None,
        )
        if beat is None:
            return False
        return self.content_hash == self.story.image_hash(beat, model=self.model or None)


class StoryRecording(models.Model):
    """A PRIVATE audio recording of a learner reading a story aloud (LGA-73).

    Parent-only, opt-in, deletable. Stored in the PRIVATE default media store (signed,
    expiring URLs), NEVER on the public read-along path, and NEVER sent to any AI/TTS.
    This is a deliberate, parent-requested exception to the D-55 "no stored recordings"
    default: that stance guards against building voiceprints/surveillance for external
    users; for a private family it's the parent's own record of their child reading,
    their data and their choice. FK to Learner is a lingua-internal CASCADE (D-03);
    Story is SET_NULL so a recording survives its story being deleted."""

    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="recordings",
    )
    story = models.ForeignKey(
        Story, on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
    )
    audio_key = models.CharField(max_length=200, help_text="PRIVATE media key (signed URL).")
    content_type = models.CharField(max_length=64, blank=True)
    seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["learner", "created_at"])]

    def __str__(self):
        return f"StoryRecording<learner={self.learner_id} story={self.story_id}>"


class LibraryBook(models.Model):
    """A curated REAL, physical Spanish-language library book (LGA-75). Seeded content
    (never user-authored — the app stopped inventing stories; this points parents at
    actual books to borrow), grouped by grade for the PARENT-ONLY library browser.
    Sourced from across the Spanish-speaking world. No FK to any host model (D-03)."""

    PK, K = "PK", "K"
    GRADE_CHOICES = [
        (PK, "Pre-K"), (K, "Kindergarten"), ("1", "1st grade"), ("2", "2nd grade"),
        ("3", "3rd grade"), ("4", "4th grade"), ("5", "5th grade"), ("6", "6th grade"),
        ("7", "7th grade"), ("8", "8th grade"),
    ]
    GRADE_ORDER = [PK, K, "1", "2", "3", "4", "5", "6", "7", "8"]

    # Which ladder a book belongs to. NATIVE books are graded for native speakers —
    # the right *target*, but not the right starting point for an English-L1 beginner.
    # CI (comprehensible-input / TPRS) novellas are written FOR learners with tiny
    # controlled vocabularies and are age-neutral, so a 12-year-old isn't handed a
    # board book; they're the practical primary ladder. ADULT is the parent's own
    # track; FREE is public-domain/no-cost reading.
    NATIVE, CI, ADULT, FREE = "native", "ci", "adult", "free"
    TRACK_CHOICES = [
        (NATIVE, "By grade"), (CI, "For learners"),
        (ADULT, "Adult track"), (FREE, "Free online"),
    ]
    TRACK_ORDER = [CI, NATIVE, ADULT, FREE]   # CI first: it's the beginner's ladder
    TRACK_ICONS = {NATIVE: "📚", CI: "🚀", ADULT: "☕", FREE: "🌐"}
    TRACK_BLURBS = {
        CI: ("Start here. These are written FOR learners — tiny controlled vocabularies "
             "(~100–350 words), heavy repetition and glossaries, and they're age-neutral, "
             "so a 12-year-old isn't handed a board book. Read one, then a native title "
             "from a lower grade, then the next one."),
        NATIVE: ("Graded for NATIVE speakers — the target to grow into, and wonderful "
                 "read-alouds meanwhile. Each band lists what books at that level look like."),
        ADULT: "Dad's parallel ladder, easiest to hardest, with CEFR levels.",
        FREE: "Complete texts you can read online right now, at no cost.",
    }

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=64, blank=True, help_text="Author/origin, e.g. México, España.")
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True,
                             help_text="Native-track grade; blank for CI/adult/free books.")
    track = models.CharField(max_length=8, choices=TRACK_CHOICES, default=NATIVE)
    level_label = models.CharField(max_length=40, blank=True,
                                   help_text="CI level ('Level 1', 'Novice-low') or adult stage ('Etapa 1 · A1–B1').")
    tense = models.CharField(max_length=40, blank=True,
                             help_text="CI novellas: which verb tense(s) the book uses — the real leveling axis.")
    isbn = models.CharField(max_length=20, blank=True)
    is_translation = models.BooleanField(
        default=False, help_text="True if translated INTO Spanish (vs originally Spanish).")
    url = models.URLField(blank=True, help_text="Free/public-domain full text, when available.")
    note = models.CharField(max_length=300, blank=True, help_text="One line: theme + why it's good.")
    language = models.CharField(max_length=8, default="es")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["grade", "title"]
        indexes = [models.Index(fields=["grade"])]
        constraints = [
            models.UniqueConstraint(fields=["title", "author", "grade", "track"],
                                    name="uniq_book_title_author_grade_track"),
        ]

    def __str__(self):
        return f"{self.title} ({self.grade})"

    @property
    def grade_rank(self):
        try:
            return self.GRADE_ORDER.index(self.grade)
        except ValueError:
            return len(self.GRADE_ORDER)


class BookLogEntry(models.Model):
    """A child's PHYSICAL-book reading-log entry (LGA-75) — a real book they finished,
    logged from the kid portal or by a parent (both portals show the log). Either
    references a catalog :class:`LibraryBook` or carries a free-text title/author (a
    book not in the catalog). FK to Learner is a lingua-internal CASCADE (D-03); book is
    SET_NULL and the title/author are snapshotted so the entry survives a catalog edit
    or delete."""

    LOVED, OK, MEH = "loved", "ok", "meh"
    ENJOYED_CHOICES = [(LOVED, "¡Me encantó!"), (OK, "Estuvo bien"), (MEH, "Más o menos")]
    KID, PARENT = "kid", "parent"
    BY_CHOICES = [(KID, "Kid"), (PARENT, "Parent")]

    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="book_logs")
    book = models.ForeignKey(
        LibraryBook, on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
    )
    title = models.CharField(max_length=200, blank=True, help_text="Snapshot / custom title.")
    author = models.CharField(max_length=200, blank=True)
    read_on = models.DateField()
    enjoyed = models.CharField(max_length=8, choices=ENJOYED_CHOICES, blank=True)
    note = models.CharField(max_length=500, blank=True)
    logged_by = models.CharField(max_length=8, choices=BY_CHOICES, default=KID)
    # Id of the mirrored host work-log record (LGA-76). A PLAIN INT, never a FK — the
    # book log must stay extractable (D-03); the host adapter owns the other side.
    host_worklog_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-read_on", "-created_at"]
        indexes = [models.Index(fields=["learner", "read_on"])]

    def __str__(self):
        return f"BookLogEntry<learner={self.learner_id} {self.display_title!r}>"

    @property
    def display_title(self):
        return (self.book.title if self.book else self.title) or ""

    @property
    def display_author(self):
        return (self.book.author if self.book else self.author) or ""

    @property
    def enjoyed_emoji(self):
        return {self.LOVED: "😀", self.OK: "🙂", self.MEH: "😐"}.get(self.enjoyed, "📖")


class ReadingSession(models.Model):
    """One reading of a story by a learner — the atom behind the reading-volume hero
    metric (D-60/61): cumulative words read + minutes of comprehensible input. FK to
    Learner is a lingua-internal CASCADE; Story is SET_NULL so the history (the words
    the child already read) survives the story being deleted — you don't un-read a
    story. No FK to any host model (D-03)."""

    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="reading_sessions",
    )
    story = models.ForeignKey(
        Story, on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
    )
    words = models.IntegerField(default=0)
    seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["learner", "created_at"])]

    def __str__(self):
        return f"ReadingSession<learner={self.learner_id} words={self.words}>"


class ComprehensionCheck(models.Model):
    """A low-stakes after-reading comprehension check (F-01, LGA-52). Its ``result`` is
    a signal on the comprehension scale (lingua.comprehension) that the advancement
    rule (LGA-67) consumes. Recognition checks (picture-match) auto-grade at creation;
    open checks (retell / short-answer) start PENDING for parent review — the child's
    free text is never stored here and never sent to AI (D-53), only the parent's
    resulting rating. FKs are lingua-internal (D-03); Story is SET_NULL so the signal
    history survives a deleted story. ``reviewed_by`` is a plain host user id (no FK)."""

    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="comprehension_checks",
    )
    story = models.ForeignKey(
        Story, on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
    )
    kind = models.CharField(max_length=16, choices=comprehension.KIND_CHOICES)
    result = models.CharField(
        max_length=12, choices=comprehension.RESULT_CHOICES, default=comprehension.PENDING)
    reviewed_by = models.IntegerField(null=True, blank=True)  # host user id, no FK (D-03)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["learner", "created_at"])]

    def __str__(self):
        return f"ComprehensionCheck<learner={self.learner_id} {self.kind}={self.result}>"


class MilestoneAward(models.Model):
    """A comprehension/volume milestone a learner has crossed — the warm celebration
    engine (D-60/61). Tied to WORDS READ and WORDS KNOWN only — never streaks or
    accuracy (streaks punish sick days). Unique per (learner, kind, threshold) so a
    milestone is celebrated exactly once. FK to Learner is a lingua-internal CASCADE
    (D-03)."""

    WORDS, KNOWN = "words", "known"
    KIND_CHOICES = [(WORDS, "Words read"), (KNOWN, "Words known")]

    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="milestones",
    )
    kind = models.CharField(max_length=8, choices=KIND_CHOICES)
    threshold = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["learner", "kind", "threshold"],
                name="uniq_learner_kind_threshold",
            ),
        ]

    def __str__(self):
        return f"MilestoneAward<learner={self.learner_id} {self.kind}={self.threshold}>"


class ListeningResource(models.Model):
    """A curated external listening item — a YouTube video/playlist/channel of leveled
    comprehensible Spanish input (F-02/N-02, LGA-55/56). Content-only (no learner FK),
    seeded by ``seed_listening``. We reuse the curated-external-link + minutes-check-in
    PATTERN (not a TTS listening library) but keep it lingua-OWNED rather than FK-ing the
    host ``activities.ExternalActivity``, so the module stays extractable (D-03/D-04).
    Nothing copyrighted is stored — only a link + metadata (embed/link out)."""

    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=120, blank=True, help_text="e.g. 'Dreaming Spanish'.")
    url = models.URLField(help_text="Curated YouTube video/playlist/channel URL.")
    age_band = models.CharField(max_length=16, choices=profiles.TRACK_CHOICES)
    level = models.CharField(max_length=4, choices=profiles.LEVEL_CHOICES)
    visual_support = models.BooleanField(
        default=True, help_text="Strong pictures/gestures/animation aid comprehension.")
    minutes = models.PositiveIntegerField(default=5, help_text="Rough length, for the check-in default.")
    transcript = models.TextField(blank=True, help_text="Optional transcript reveal (LGA-57).")
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["age_band", "order", "id"]

    def __str__(self):
        return f"ListeningResource<{self.age_band}:{self.title}>"


class ListeningSession(models.Model):
    """One logged listening check-in by a learner (F-02/N-02, LGA-55/57) — the atom of
    the listening half of the "minutes of comprehensible input" hero metric (D-60/61).
    Mirrors ReadingSession: learner CASCADE (lingua-internal, D-03); resource SET_NULL so
    the minutes already logged survive a curated item being removed."""

    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="listening_sessions",
    )
    resource = models.ForeignKey(
        "ListeningResource", on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
    )
    minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["learner", "created_at"])]

    def __str__(self):
        return f"ListeningSession<learner={self.learner_id} min={self.minutes}>"


class ReviewItem(models.Model):
    """One spaced-repetition card behind the pluggable scheduler port (D-30, LGA-58).

    ONE table serves both schedulers — Leitner (KIDS_EARLY) and FSRS (KIDS_OLDER):
    ``scheduler`` names which one owns this card and ``scheduler_state`` (JSON) is its
    SOURCE OF TRUTH. ``due`` is a mirrored, indexed column derived from that state so
    "what's due" is a single indexed query regardless of scheduler (never two tables).
    ``paused_until`` is a per-CARD pause primitive (a card paused past its due date is
    skipped by ``due_review_items`` until then) — reserved for future per-card use; it is
    NOT the LGA-62 return-flood mechanism, which is handled at the learner level by
    ``LearnerProfile.paused_until`` + the per-day ``daily_review_cap``. The target is a
    generic (kind, ref) pair — no FK to a vocab/question row — to keep the SRS
    scheduler-agnostic and extractable (D-03/D-30).

    NOTE for LGA-60: the FSRS ``scheduler_state`` blob schema is owned by the FSRS
    scheduler; pin ``fsrs==6.x`` there to keep that JSON stable."""

    LEITNER, FSRS = "leitner", "fsrs"
    SCHEDULER_CHOICES = [(LEITNER, "Leitner"), (FSRS, "FSRS")]

    VOCAB, QUESTION = "vocab", "question"
    TARGET_CHOICES = [(VOCAB, "Vocabulary"), (QUESTION, "Question")]

    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="review_items",
    )
    target_kind = models.CharField(max_length=16, choices=TARGET_CHOICES, default=VOCAB)
    target_ref = models.CharField(
        max_length=128, help_text="Generic target id (e.g. a normalized word) — no FK (D-30).")
    scheduler = models.CharField(max_length=8, choices=SCHEDULER_CHOICES, default=LEITNER)
    scheduler_state = models.JSONField(default=dict, blank=True)  # source of truth for the scheduler
    due = models.DateTimeField(db_index=True)                     # mirrored from state, for querying
    paused_until = models.DateTimeField(null=True, blank=True)    # per-card pause primitive (reserved)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["learner", "target_kind", "target_ref"],
                name="uniq_review_item_per_target",
            ),
        ]
        indexes = [models.Index(fields=["learner", "due"])]

    def __str__(self):
        return f"ReviewItem<learner={self.learner_id} {self.target_kind}:{self.target_ref} due={self.due:%Y-%m-%d}>"


class KnownWord(models.Model):
    """A word the learner has been credited as knowing — LingQ's known-words idea and
    the warm hero counter (D-60/61). Unique per (learner, word) so the count can never
    double-count. Credited from reading exposure / SRS mastery / tap-a-word (later)."""

    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="known_words",
    )
    word = models.CharField(max_length=64)  # normalized form (dedup-friendly)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["word"]
        constraints = [
            models.UniqueConstraint(fields=["learner", "word"], name="uniq_learner_word"),
        ]

    def __str__(self):
        return f"KnownWord<learner={self.learner_id} {self.word!r}>"


class TutorPacket(models.Model):
    """Homework / materials from a live tutor (italki, etc.) for the kid portal
    (LGA-85). Content-only with an optional ``host_student_id`` filter (plain int,
    NOT an FK — D-03) so a packet can be Kaylin-only without coupling to
    ``students.Student``. File lives on the default (private) storage — same
    pattern as host CurriculumDocument."""

    title = models.CharField(max_length=200)
    source = models.CharField(
        max_length=120, blank=True,
        help_text="e.g. 'italki · Juan Cárdenas'.",
    )
    body = models.TextField(
        blank=True,
        help_text="Practice phrases, one per line. Shown on the packet page and Escuchar.",
    )
    file = models.FileField(
        upload_to="lingua/tutor/%Y/%m/", blank=True, null=True,
        help_text="Optional teacher handout (DOCX/PDF).",
    )
    host_student_id = models.IntegerField(
        null=True, blank=True, db_index=True,
        help_text="students.Student.pk when packet is for one child; blank = all learners.",
    )
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"TutorPacket<{self.title}>"

    def phrase_lines(self):
        """Non-blank practice lines from ``body`` (skip # comment lines)."""
        lines = []
        for raw in (self.body or "").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                lines.append(line)
        return lines


class AudioClip(models.Model):
    """A single baked utterance (word / letter name / phrase) for tap-to-hear
    (LGA-84 / LGA-86). Content-addressed like StoryAudio: hash of text + voice +
    engine + provider. No timings — single words/phrases don't need them. Baked
    at authoring time only (never per request)."""

    text = models.CharField(max_length=240)
    provider = models.CharField(max_length=16, default="polly")
    voice = models.CharField(max_length=32)
    engine = models.CharField(max_length=16, default="neural")
    content_hash = models.CharField(max_length=64, db_index=True)
    audio_key = models.CharField(max_length=200, help_text="R2 object key for the mp3.")
    duration_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["text"]
        constraints = [
            models.UniqueConstraint(
                fields=["text", "voice", "engine", "provider"],
                name="uniq_clip_text_voice_engine_provider",
            ),
        ]

    def __str__(self):
        return f"AudioClip<{self.text!r}>"

    @property
    def is_current(self):
        from . import assets
        expected = assets.content_hash(
            self.text, provider=self.provider, voice=self.voice, engine=self.engine,
        )
        return self.content_hash == expected


class AlphabetTile(models.Model):
    """One letter or digraph on the Escuchar alphabet chart (LGA-86): A–Z, ñ, ll, rr.
    ``spoken`` is what Polly says (letter name); ``example`` is an optional practice
    word shown under the tile. Content-only; audio comes from AudioClip rows."""

    LETTER, DIGRAPH = "letter", "digraph"
    KIND_CHOICES = [(LETTER, "Letter"), (DIGRAPH, "Digraph")]

    symbol = models.CharField(max_length=4, unique=True, help_text="Displayed glyph, e.g. ñ or ll.")
    spoken = models.CharField(max_length=40, help_text="What to synthesize, e.g. 'eñe' or 'elle'.")
    example = models.CharField(max_length=40, blank=True, help_text="Optional example word.")
    kind = models.CharField(max_length=8, choices=KIND_CHOICES, default=LETTER)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "symbol"]

    def __str__(self):
        return f"AlphabetTile<{self.symbol}>"


class Pathway(models.Model):
    """Ordered Camino trail for an age band (LGA-88). Content-only catalog — no host
    FKs (D-03). One active pathway per band is typical; ``order`` breaks ties."""

    slug = models.SlugField(max_length=64, unique=True)
    title = models.CharField(max_length=120)
    age_band = models.CharField(max_length=16, choices=profiles.TRACK_CHOICES)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "pathways"

    def __str__(self):
        return f"Pathway<{self.slug}>"


class PathwayStep(models.Model):
    """One stop on a Pathway (LGA-88). Opaque ``(kind, target_ref)`` like ReviewItem —
    no FKs to stories/packets so the overlay stays extractable (D-03). Completion is
    derived in ``pathway_status``, not stored here."""

    STORY, STORY_LEVEL, PHONICS, LISTEN = "story", "story_level", "phonics", "listen"
    TUTOR_PACKET, REVIEW, LINK = "tutor_packet", "review", "link"
    KIND_CHOICES = [
        (STORY, "Story"),
        (STORY_LEVEL, "Story level"),
        (PHONICS, "Phonics"),
        (LISTEN, "Listen"),
        (TUTOR_PACKET, "Tutor packet"),
        (REVIEW, "Review"),
        (LINK, "Link"),
    ]

    pathway = models.ForeignKey(Pathway, on_delete=models.CASCADE, related_name="steps")
    order = models.IntegerField(default=0)
    title = models.CharField(max_length=160)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    target_ref = models.CharField(
        max_length=128, blank=True,
        help_text="Opaque target (story pk, L1, packet pk, URL name, …).",
    )
    pass_rule = models.JSONField(
        default=dict, blank=True,
        help_text="Optional completion hints, e.g. {\"min_stories\": 1}.",
    )
    optional = models.BooleanField(
        default=False,
        help_text="Optional steps never block unlock of later required steps.",
    )

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["pathway", "order"], name="uniq_pathway_step_order",
            ),
        ]

    def __str__(self):
        return f"PathwayStep<{self.pathway_id}:{self.order} {self.kind}>"
