"""Spelling OS — pattern-based spelling for Grade 3.

Words are taught by PATTERN, not as a memorised weekly list, and they never
"expire" on a Friday test: every word a child meets becomes a card in a Leitner
box and keeps coming back until she has spelled it correctly across several
spaced sessions.

The scheduler itself is ``lingua.schedulers.leitner`` — pure logic, no ORM, and
written to be reused (see its docstring). Only the card row lives here, keyed to
a Student rather than lingua's Learner, so Spanish and spelling stay independent.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class SpellingWeek(models.Model):
    """One week of the scope & sequence: a pattern, its rule, and its words."""

    number = models.PositiveIntegerField(unique=True, help_text="Week 1..36")
    unit = models.CharField(max_length=100, help_text="e.g. 'Foundation Repair'")
    pattern = models.CharField(max_length=120, help_text="e.g. 'ai / ay'")
    rule = models.TextField(help_text="The rule, in words a third grader can read.")
    sort_buckets = models.JSONField(
        default=list, blank=True,
        help_text="Column headings for the word sort, e.g. ['ai (middle)', 'ay (end)'].",
    )

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Week {self.number}: {self.pattern}"

    @property
    def pattern_words(self):
        return self.words.filter(is_heart=False)

    @property
    def heart_words(self):
        return self.words.filter(is_heart=True)


class SpellingWord(models.Model):
    """One word, with the sentence it is dictated in.

    ``is_heart`` marks an irregular high-frequency word that cannot be sounded
    out — it has to be known by sight, and the tricky part is called out rather
    than left for the child to fail at.
    """

    week = models.ForeignKey(SpellingWeek, on_delete=models.CASCADE, related_name="words")
    word = models.CharField(max_length=40)
    sentence = models.CharField(
        max_length=200,
        help_text="Dictation sentence. Uses only patterns taught by this week.",
    )
    is_heart = models.BooleanField(default=False)
    tricky_part = models.CharField(
        max_length=120, blank=True,
        help_text="For heart words: which bit breaks the rule, e.g. \"ai says /e/\".",
    )
    audio_url = models.URLField(
        blank=True, max_length=500,
        help_text="Baked pronunciation of the word (spelling_audio). Blank falls "
                  "back to the browser's own voice.",
    )
    sentence_audio_url = models.URLField(
        blank=True, max_length=500,
        help_text="Baked reading of the dictation sentence.",
    )
    audio_voice = models.CharField(
        max_length=40, blank=True,
        help_text="Which Polly voice was baked, so a voice change is visible.",
    )
    sort_bucket = models.PositiveSmallIntegerField(
        default=0,
        help_text="Index into the week's sort_buckets — which column this word "
                  "belongs under in the word sort. Heart words ignore it.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["week__number", "is_heart", "order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["week", "word"], name="unique_word_per_week"),
        ]

    def __str__(self):
        return self.word


class SpellingCard(models.Model):
    """One child's Leitner card for one word.

    ``box`` and ``due`` are the whole scheduler state. A correct answer promotes
    the card one box; a miss drops it straight back to box 1 — non-punitive, just
    "see it again tomorrow". Mastery is reaching the top box, which takes four
    correct answers spread over time rather than one lucky Friday.
    """

    MAX_BOX = 5
    # Days a card waits in each box. Matches the spelling spec's intervals; the
    # shared Leitner scheduler's own defaults are tuned for Spanish vocabulary.
    INTERVALS = {1: 0, 2: 2, 3: 5, 4: 14, 5: 45}

    child = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="spelling_cards")
    word = models.ForeignKey(SpellingWord, on_delete=models.CASCADE, related_name="cards")
    box = models.PositiveSmallIntegerField(default=1)
    due = models.DateField(default=timezone.localdate, db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)
    misses = models.PositiveIntegerField(default=0)
    last_missed_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due", "id"]
        constraints = [
            models.UniqueConstraint(fields=["child", "word"], name="unique_card_per_child_word"),
        ]

    def __str__(self):
        return f"{self.child.first_name} · {self.word.word} (box {self.box})"

    @property
    def is_mastered(self):
        return self.box >= self.MAX_BOX

    @property
    def is_trouble(self):
        """Worth drilling in the car. Three misses is a pattern, not a slip."""
        return self.misses >= 3

    def record(self, correct, *, today=None):
        """Apply one answer. Returns True if this answer mastered the word."""
        today = today or timezone.localdate()
        was_mastered = self.is_mastered
        self.attempts += 1
        if correct:
            self.correct += 1
            self.box = min(self.box + 1, self.MAX_BOX)
        else:
            self.misses += 1
            self.last_missed_on = today
            self.box = 1
        self.due = today + timedelta(days=self.INTERVALS[self.box])
        self.save()
        return self.is_mastered and not was_mastered


class SpellingSession(models.Model):
    """One completed activity, for the streak and the parent's weekly glance."""

    LEARN, SORT, QUIZ, DICTATION = "learn", "sort", "quiz", "dictation"
    KIND_CHOICES = [
        (LEARN, "Learn the pattern"),
        (SORT, "Word sort"),
        (QUIZ, "Hear-and-type quiz"),
        (DICTATION, "Sentence dictation"),
    ]

    child = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="spelling_sessions")
    week = models.ForeignKey(
        SpellingWeek, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sessions")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    on_date = models.DateField(default=timezone.localdate, db_index=True)
    asked = models.PositiveIntegerField(default=0)
    right = models.PositiveIntegerField(default=0)
    missed_words = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-on_date", "-created_at"]

    def __str__(self):
        return f"{self.child.first_name} · {self.get_kind_display()} · {self.on_date}"

    @property
    def score_display(self):
        return f"{self.right}/{self.asked}" if self.asked else "—"


class SpellingPlacement(models.Model):
    """Where a child is in the 36 weeks, and whether she can see it yet."""

    child = models.OneToOneField(
        "students.Student", on_delete=models.CASCADE, related_name="spelling_placement")
    current_week = models.PositiveIntegerField(default=1)
    started_on = models.DateField(default=timezone.localdate)
    is_active = models.BooleanField(
        default=True, help_text="Off hides spelling from her portal entirely.")
    repeat_flagged_on = models.DateField(
        null=True, blank=True,
        help_text="Set when a week was repeated because too much was still in box 1.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="spelling_placements")

    def __str__(self):
        return f"{self.child.first_name} · week {self.current_week}"
