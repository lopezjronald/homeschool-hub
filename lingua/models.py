"""Lingua core models — the extractable learner domain.

D-03 (load-bearing): NO ForeignKey from lingua to any host model, EVER. The
learner is a host ``students.Student`` referenced by a plain ``host_student_id``
integer, resolved at display time through the UserDirectory adapter (LGA-17).
FKs *within* lingua are ordinary CASCADE relations.
"""

from django.conf import settings
from django.db import models, transaction

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
    action = models.CharField(max_length=40, db_index=True)
    target_type = models.CharField(max_length=40, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    summary = models.CharField(max_length=200, blank=True, help_text="Short human line — no child free-text.")
    metadata = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-ts"]
        indexes = [models.Index(fields=["action", "ts"])]

    def __str__(self):
        return f"{self.action} @ {self.ts:%Y-%m-%d %H:%M}"

    @classmethod
    def record(cls, action, *, actor_type="system", actor_id=None, target_type="",
               target_id=None, summary="", metadata=None, ip=None):
        """Write one audit event. ``action`` must be in ACTIONS (closed vocab).
        Pass only structured facts — NEVER a prompt, answer, or child free-text."""
        if action not in cls.ACTIONS:
            raise ValueError(f"Unknown audit action: {action!r}")
        return cls.objects.create(
            action=action, actor_type=actor_type, actor_id=actor_id,
            target_type=target_type, target_id=target_id,
            summary=(summary or "")[:200], metadata=metadata or {}, ip=ip,
        )
