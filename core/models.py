import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    """A charter school, state program, co-op, or other oversight body."""

    ORG_TYPE_CHOICES = [
        ("charter", "Charter School"),
        ("state_program", "State Program"),
        ("co_op", "Co-op"),
        ("private", "Private"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=200)
    org_type = models.CharField(max_length=20, choices=ORG_TYPE_CHOICES)
    requires_teacher_oversight = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_org_type_display()})"


class Family(models.Model):
    """A household unit that groups parents, teachers, and students."""

    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="families",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "families"

    def __str__(self):
        return self.name


class FamilyMembership(models.Model):
    """Links a user to a family with a specific role."""

    # Two roles a household can grant, plus an internal one. A co-parent is a
    # "parent"; a guardian who may only look is a "teacher". The labels people
    # read live on the invite form — see core.forms.TeacherInviteForm — because
    # what someone is CALLED and what they may DO are different questions.
    ROLE_CHOICES = [
        ("parent", "Parent — full access"),
        ("teacher", "Teacher or guardian — view only"),
        ("admin", "Admin"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_memberships",
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "family"],
                name="unique_user_family",
            ),
        ]
        ordering = ["family", "role"]

    def __str__(self):
        return f"{self.user} - {self.family} ({self.get_role_display()})"


class Invitation(models.Model):
    """An email invitation to join a Family with a given role."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (EXPIRED, "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    role = models.CharField(max_length=20, default="teacher")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    resent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "family"],
                condition=models.Q(status="pending"),
                name="unique_pending_invite_per_email_family",
            ),
        ]
        ordering = ["-created_at"]

    # Retired roles keep an entry so an old invitation still reads as something
    # rather than as a blank in the pending list.
    ROLE_LABELS = {
        "parent": "Parent",
        "teacher": "Teacher or guardian",
        "admin": "Admin",
        "guardian": "Teacher or guardian",
        "grandparent": "Teacher or guardian",
    }

    def __str__(self):
        return f"Invite {self.email} → {self.family} ({self.status})"

    @property
    def role_display(self):
        return self.ROLE_LABELS.get(self.role, self.role.title())

    @property
    def is_expired(self):
        max_age = getattr(settings, "INVITE_MAX_AGE_DAYS", 7)
        return timezone.now() > self.created_at + timedelta(days=max_age)

    @property
    def is_resendable(self):
        """True if invite is pending and not expired."""
        return self.status == self.PENDING and not self.is_expired


class HandoffRecipient(models.Model):
    """Somebody a handoff can be sent to — saved, not retyped.

    Typing an address every time is how a child's school record ends up in a
    stranger's inbox because of one wrong character. A short list you pick from
    removes that failure entirely, and it is a short list: the other parent, and
    perhaps a grandparent.

    `phone` is stored for the CLIPBOARD version, so a number can be dialled or
    pasted alongside the message. Nothing in this app sends a text — see
    ``core.handoff``.
    """

    family = models.ForeignKey(
        "core.Family", on_delete=models.CASCADE, related_name="handoff_recipients",
    )
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(
        max_length=40, blank=True,
        help_text="Only for your own reference when texting — the app never "
                  "sends to it.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} <{self.email or self.phone}>"


class Handoff(models.Model):
    """One handover message: what was sent, when, and to whom.

    KEPT EVEN WHEN NOTHING IS SENT. A draft records the window it covers, which
    is what lets the next handoff start where this one stopped without anybody
    remembering a date.

    The record is also the point. The co-parenting literature is consistent that
    a plain account of what was communicated — and when — is what keeps these
    arrangements calm, and it protects the person who sent it. So this stores
    the message body verbatim rather than regenerating it later: what was sent
    is a different question from what the data says today.
    """

    DRAFT = "draft"
    SENT = "sent"
    STATUS_CHOICES = [(DRAFT, "Draft"), (SENT, "Sent")]

    family = models.ForeignKey(
        "core.Family", on_delete=models.CASCADE, related_name="handoffs",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="handoffs_sent",
    )
    covers_since = models.DateTimeField()
    covers_until = models.DateTimeField()
    note = models.TextField(blank=True)
    body = models.TextField(
        blank=True,
        help_text="The message as it was sent, kept verbatim.",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to = models.CharField(
        max_length=400, blank=True,
        help_text="Where it actually went, recorded at send time.",
    )
    copied_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When it was copied for texting. Copying is not sending, and "
                  "the record should not claim otherwise.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Handoff {self.covers_since:%d %b} → {self.covers_until:%d %b} ({self.status})"

    @property
    def was_delivered(self):
        """Emailed, or copied for a text. Either counts as handed over."""
        return bool(self.sent_at or self.copied_at)
