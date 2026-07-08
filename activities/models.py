from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class ExternalActivity(models.Model):
    """A link to an outside program the family uses (e.g. School of Rock, CodaKid).

    Household-wide when ``student`` is blank, or tied to one child. Carries an
    optional reminder ``cadence`` + check-in state (last_logged_at / snoozed_until
    / is_muted) that drives the login-time "did they do it?" nudge.
    """

    CADENCE_NONE = "none"
    CADENCE_DAILY = "daily"
    CADENCE_WEEKLY = "weekly"
    CADENCE_CHOICES = [
        (CADENCE_NONE, "No reminder"),
        (CADENCE_DAILY, "Daily"),
        (CADENCE_WEEKLY, "Weekly"),
    ]
    CADENCE_DAYS = {CADENCE_DAILY: 1, CADENCE_WEEKLY: 7}

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="external_activities",
    )
    family = models.ForeignKey(
        "core.Family", on_delete=models.SET_NULL, null=True, blank=True, related_name="activities",
    )
    student = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="activities", help_text="Leave blank for a whole-family activity.",
    )
    title = models.CharField(max_length=200, help_text="e.g. 'Guitar', 'Drums', 'Coding'")
    provider = models.CharField(max_length=120, blank=True, help_text="e.g. 'School of Rock', 'CodaKid'")
    url = models.URLField(help_text="The program's login/home page.")
    emoji = models.CharField(max_length=8, default="🎯")
    cadence = models.CharField(max_length=10, choices=CADENCE_CHOICES, default=CADENCE_NONE)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # check-in / reminder state (HH-93)
    last_logged_at = models.DateField(null=True, blank=True)
    snoozed_until = models.DateField(null=True, blank=True)
    is_muted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["provider", "title"]
        verbose_name_plural = "external activities"

    def __str__(self):
        return self.display_label

    @property
    def display_label(self):
        if self.provider and self.title:
            return f"{self.provider} — {self.title}"
        return self.provider or self.title or self.url

    @property
    def is_due(self):
        """True if a reminder is due today (cadence elapsed, not muted/snoozed)."""
        if self.is_muted or self.cadence == self.CADENCE_NONE or not self.is_active:
            return False
        today = timezone.localdate()
        if self.snoozed_until and self.snoozed_until > today:
            return False
        if self.last_logged_at is None:
            return True
        return self.last_logged_at + timedelta(days=self.CADENCE_DAYS[self.cadence]) <= today
