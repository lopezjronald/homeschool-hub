from django.conf import settings
from django.db import models

from . import mastery


class MasteryAssessment(models.Model):
    """An AI-assisted, parent-finalized mastery assessment of a work log entry.

    The AI proposes a level + feedback; the parent may override before
    finalizing. The AI never finalizes on its own.
    """

    DRAFT = "draft"
    FINALIZED = "finalized"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (FINALIZED, "Finalized"),
    ]

    work_entry = models.ForeignKey(
        "worklog.WorkLogEntry",
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    lesson = models.ForeignKey(
        "curricula.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessments",
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mastery_assessments",
    )

    rubric = models.TextField(help_text="The criteria the work is judged against.")
    answers = models.TextField(help_text="The child's work / answers that were assessed.")

    ai_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)
    ai_summary = models.TextField(blank=True)
    ai_criteria = models.JSONField(default=list, blank=True)
    ai_encouragement = models.TextField(blank=True)

    parent_override_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)
    final_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Assessment of {self.work_entry} ({self.get_status_display()})"

    @property
    def effective_level(self):
        """The level that counts: the finalized level, else the AI's proposal."""
        return self.final_level or self.ai_level

    @property
    def meets_bar(self):
        """True if the effective level is Proficient or above."""
        return mastery.meets_bar(self.effective_level)

    @property
    def badge_class(self):
        """Badge class for the effective (final-or-AI) level."""
        return mastery.BADGE.get(self.effective_level, "bg-secondary")

    @property
    def ai_badge_class(self):
        """Badge class for the AI-proposed level."""
        return mastery.BADGE.get(self.ai_level, "bg-secondary")


class Material(models.Model):
    """A two-layer learning material for a lesson (authored manually, not by AI).

    ``student_content`` is what the child sees (e.g. a comic script);
    ``parent_content`` is a teaching guide for the parent. A material is only
    visible to a student once it is approved.
    """

    SKILL_MANGA = "manga"
    SKILL_COMIC = "comic"
    SKILL_FLASHCARDS = "flashcards"
    SKILL_DRILL = "drill"
    SKILL_CHOICES = [
        (SKILL_MANGA, "Manga"),
        (SKILL_COMIC, "Comic"),
        (SKILL_FLASHCARDS, "Flashcards"),
        (SKILL_DRILL, "Drill"),
    ]

    DRAFT = "draft"
    APPROVED = "approved"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (APPROVED, "Approved"),
    ]

    lesson = models.ForeignKey(
        "curricula.Lesson",
        on_delete=models.CASCADE,
        related_name="materials",
    )
    child = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materials",
    )
    family = models.ForeignKey(
        "core.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materials",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_materials",
    )
    title = models.CharField(max_length=200)
    skill_type = models.CharField(max_length=20, choices=SKILL_CHOICES, default=SKILL_MANGA)
    student_intro = models.TextField(
        blank=True,
        help_text="A short, grade-level explanation for the child of what this lesson is "
                  "about — shown with the manga.",
    )
    student_content = models.TextField(help_text="What the child sees (e.g. a comic script).")
    parent_content = models.TextField(blank=True, help_text="Teaching guide (Markdown) for the parent.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_approved(self):
        return self.status == self.APPROVED

    @property
    def visible_to_student(self):
        """A material only reaches the student once approved."""
        return self.is_approved

    @property
    def has_pages(self):
        """True once the material has illustrated panels (a real visual manga)."""
        return self.panels.exists()


class MangaPanel(models.Model):
    """One illustrated panel of a Material's manga page.

    The artwork is an AI-generated image (Replicate), stored durably as a
    committed static file (``image_path``) for authored curriculum manga, or in
    media/object storage (``image``) for uploads. ``bubbles`` is a list of
    speech/thought/caption/sfx overlays positioned as percentages over the art,
    so the page renders with CSS — no plain-text script.
    """

    SPAN_NORMAL = "normal"
    SPAN_WIDE = "wide"
    SPAN_TALL = "tall"
    SPAN_FULL = "full"
    SPAN_CHOICES = [
        (SPAN_NORMAL, "Normal"),
        (SPAN_WIDE, "Wide (2 columns)"),
        (SPAN_TALL, "Tall (2 rows)"),
        (SPAN_FULL, "Full width"),
    ]

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="panels",
    )
    order = models.PositiveIntegerField(help_text="Reading order within the page.")
    image = models.FileField(upload_to="manga/%Y/%m/", blank=True)
    image_path = models.CharField(
        max_length=300,
        blank=True,
        help_text="Path under static/ for committed panel art (e.g. 'manga/number-besties/p1.png').",
    )
    alt = models.CharField(max_length=300, blank=True, help_text="Accessible description of the art.")
    span = models.CharField(max_length=10, choices=SPAN_CHOICES, default=SPAN_NORMAL)
    caption = models.CharField(max_length=400, blank=True, help_text="Narrator caption box.")
    bubbles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of {speaker, text, kind, x, y} overlays (x/y are 0-100 percentages).",
    )
    prompt = models.TextField(blank=True, help_text="The image-gen prompt used to draw this panel.")

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["material", "order"],
                name="unique_panel_order_per_material",
            ),
        ]

    def __str__(self):
        return f"{self.material.title} — panel {self.order}"

    @property
    def has_art(self):
        return bool(self.image_path or self.image)


class QuestionSet(models.Model):
    """A set of Socratic/comprehension questions a child answers for a lesson.

    Authored per-lesson (e.g. a Blackbird & Company reading session). The
    ``rubric`` (Markdown) travels with the set so the parent — or the AI
    grader — assesses submissions against the curriculum's own standard.
    Like ``Material``, a set only reaches the student once approved.
    """

    DRAFT = "draft"
    APPROVED = "approved"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (APPROVED, "Approved"),
    ]

    lesson = models.ForeignKey(
        "curricula.Lesson",
        on_delete=models.CASCADE,
        related_name="question_sets",
    )
    child = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="question_sets",
        help_text="Optional: pin this set to one child; blank = any child placed in the curriculum.",
    )
    family = models.ForeignKey(
        "core.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="question_sets",
    )
    title = models.CharField(max_length=200)
    intro = models.TextField(
        blank=True,
        help_text="Kid-facing instructions shown above the questions.",
    )
    reading = models.CharField(
        max_length=200,
        blank=True,
        help_text="What to read first, e.g. 'Chapters 3–4'.",
    )
    rubric = models.TextField(
        blank=True,
        help_text="Markdown rubric used when assessing responses.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lesson__chapter__number", "lesson__order", "id"]

    def __str__(self):
        return self.title

    @property
    def is_approved(self):
        return self.status == self.APPROVED


class Question(models.Model):
    """One question in a QuestionSet, tagged with its Socratic category."""

    # CenterForLit-style story-grammar categories + plain comprehension.
    CATEGORY_CHOICES = [
        ("comprehension", "Comprehension"),
        ("context", "Context"),
        ("conflict", "Conflict"),
        ("plot", "Plot"),
        ("setting", "Setting"),
        ("character", "Character"),
        ("theme", "Theme"),
        ("style", "Style"),
        ("application", "Application"),
        ("vocabulary", "Vocabulary"),
    ]

    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    order = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="comprehension")
    prompt = models.TextField()
    hint = models.TextField(
        blank=True,
        help_text="A gentle scaffold shown to the child on demand.",
    )

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["question_set", "order"],
                name="unique_question_order_per_set",
            ),
        ]

    def __str__(self):
        return f"{self.question_set.title} — Q{self.order}"


class ResponseSheet(models.Model):
    """A child's answers to a QuestionSet — autosaved as they type, then submitted.

    ``answers`` maps question id (as a string) to the child's text. On submit a
    WorkLogEntry is created so the response lands in the family's durable
    record and can be assessed via the existing mastery flow.
    """

    DRAFT = "draft"
    SUBMITTED = "submitted"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (SUBMITTED, "Submitted"),
    ]

    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    child = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="response_sheets",
    )
    answers = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    work_entry = models.ForeignKey(
        "worklog.WorkLogEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="response_sheets",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question_set", "child"],
                name="unique_response_sheet_per_child_set",
            ),
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.child} — {self.question_set.title} ({self.get_status_display()})"

    @property
    def is_submitted(self):
        return self.status == self.SUBMITTED

    def answer_for(self, question):
        return (self.answers or {}).get(str(question.pk), "")

    @property
    def answered_count(self):
        return sum(1 for v in (self.answers or {}).values() if str(v).strip())

    def as_worklog_text(self):
        """Format the Q&A as readable text for the work log / grader."""
        lines = []
        for q in self.question_set.questions.all():
            answer = self.answer_for(q).strip() or "(no answer)"
            lines.append(f"Q{q.order} [{q.get_category_display()}]: {q.prompt}")
            lines.append(f"A: {answer}")
            lines.append("")
        return "\n".join(lines).strip()
