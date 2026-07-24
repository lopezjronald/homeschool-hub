"""Lingua core models — the extractable learner domain.

D-03 (load-bearing): NO ForeignKey from lingua to any host model, EVER. The
learner is a host ``students.Student`` referenced by a plain ``host_student_id``
integer, resolved at display time through the UserDirectory adapter (LGA-17).
FKs *within* lingua are ordinary CASCADE relations.
"""

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from . import profiles


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
        "learner.created", "learner.deleted",
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
