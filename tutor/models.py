import json

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
    ai_kid_highlights = models.JSONField(
        default=list, blank=True,
        help_text="Short child-facing bullets shown on the portal feedback page.",
    )

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
    def is_auto(self):
        """True if this draft came from the portal's submit-time grading agent."""
        return self.graded_by_id is None

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

    MODE_STUDENT = "student"
    MODE_DISCUSSION = "discussion"
    MODE_CHOICES = [
        (MODE_STUDENT, "Student form (child fills out)"),
        (MODE_DISCUSSION, "Teacher-led discussion (oral; not submitted)"),
    ]

    lesson = models.ForeignKey(
        "curricula.Lesson",
        on_delete=models.CASCADE,
        related_name="question_sets",
    )
    mode = models.CharField(
        max_length=12,
        choices=MODE_CHOICES,
        default=MODE_STUDENT,
        help_text="Student forms appear in the child's portal; discussion sets appear "
                  "only in the parent/teacher discussion guide.",
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
    answer_key = models.TextField(
        blank=True,
        help_text="Reference answers (Markdown) the AI grader checks against; never "
                  "shown to the student.",
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
        # writing-curriculum categories (Essentials in Writing)
        ("grammar", "Grammar"),
        ("editing", "Editing"),
        ("writing", "Writing"),
    ]

    TYPE_TEXT = "text"
    TYPE_MARKUP = "markup"
    TYPE_CHARACTERS = "characters"
    TYPE_MATCHING = "matching"
    TYPE_FILL_BLANK = "fill_blank"
    TYPE_CLOZE = "cloze"
    RESPONSE_TYPES = [
        (TYPE_TEXT, "Typed answer"),
        (TYPE_MARKUP, "Mark up the sentence (draw)"),
        (TYPE_CHARACTERS, "A box per character"),
        (TYPE_MATCHING, "Match words to numbered definitions"),
        (TYPE_FILL_BLANK, "Fill in the blank from a word bank"),
        (TYPE_CLOZE, "Fill in the blanks with your own words"),
    ]

    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    order = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="comprehension")
    prompt = models.TextField()
    response_type = models.CharField(max_length=10, choices=RESPONSE_TYPES, default=TYPE_TEXT)
    passage = models.TextField(
        blank=True,
        help_text="For markup questions: the sentence/text the child draws on. "
                  "For character questions: the character names, separated by '·'.",
    )
    hint = models.TextField(
        blank=True,
        help_text="A gentle scaffold shown to the child on demand.",
    )

    @property
    def is_markup(self):
        return self.response_type == self.TYPE_MARKUP

    @property
    def is_characters(self):
        return self.response_type == self.TYPE_CHARACTERS

    @property
    def is_matching(self):
        return self.response_type == self.TYPE_MATCHING

    @property
    def is_fill_blank(self):
        return self.response_type == self.TYPE_FILL_BLANK

    @property
    def is_cloze(self):
        return self.response_type == self.TYPE_CLOZE

    @property
    def supports_draft_coach(self):
        """True if the writing coach can review this answer as a draft.

        Rough drafts in the literature guides carry a "ROUGH DRAFT" marker;
        Essentials-in-Writing paragraph work is category "writing".
        """
        if self.response_type != self.TYPE_TEXT:
            return False
        return "ROUGH DRAFT" in (self.prompt or "").upper() or self.category == "writing"

    @property
    def cloze_segments(self):
        """Split a cloze passage at underscore runs into text/blank segments.

        Returns [{"text": …, "blank": None|index}, …] — a blank segment carries
        the input's index; text segments carry the words around it.
        """
        import re

        segments = []
        idx = 0
        pos = 0
        for m in re.finditer(r"_{3,}", self.passage or ""):
            if m.start() > pos:
                segments.append({"text": (self.passage[pos:m.start()]), "blank": None})
            segments.append({"text": "", "blank": idx})
            idx += 1
            pos = m.end()
        rest = (self.passage or "")[pos:]
        if rest:
            segments.append({"text": rest, "blank": None})
        return segments

    @property
    def cloze_blank_count(self):
        return sum(1 for s in self.cloze_segments if s["blank"] is not None)

    @property
    def character_names(self):
        """Character names for a character question (from ``passage``).

        Accepts '·', '•', or newline separators; trims and drops blanks.
        """
        raw = self.passage or ""
        for sep in ("·", "•", "\n"):
            raw = raw.replace(sep, "\x00")
        return [name.strip() for name in raw.split("\x00") if name.strip()]

    @property
    def vocab_data(self):
        """Parsed exercise data for matching/fill-blank questions (from ``passage``).

        Matching:   {"words": […], "definitions": [{"n": 1, "text": …, "word": …}, …]}
        Fill-blank: {"words": […], "sentences": [{"text": "… ______ …", "word": …}, …]}
        Returns {} if the JSON is missing or malformed — templates must degrade.
        """
        try:
            data = json.loads(self.passage or "")
        except (ValueError, TypeError):
            return {}
        return data if isinstance(data, dict) else {}

    @property
    def fill_blank_sentences(self):
        """Fill-blank sentences pre-split at the blank for easy templating."""
        out = []
        for s in self.vocab_data.get("sentences", []):
            if not isinstance(s, dict):
                continue
            before, _sep, after = str(s.get("text", "")).partition("______")
            out.append({"before": before, "after": after, "word": s.get("word", "")})
        return out

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
    draft_feedback = models.JSONField(
        default=dict, blank=True,
        help_text="Writing-coach feedback per question id: {qid: {praise, suggestions, at}}.",
    )
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
        """Format the Q&A as readable text for the work log / grader.

        Markup answers are drawing strokes, not prose, so they're summarized as
        the sentence plus whether the child annotated it. Character answers are a
        per-character map, so each character is listed with what the child wrote.
        """
        lines = []
        for q in self.question_set.questions.all():
            raw = str(self.answer_for(q)).strip()
            if q.is_markup:
                marked = "yes" if raw and raw != "[]" else "no"
                answer = f'[marked up the sentence "{q.passage}" — annotated: {marked}]'
            elif q.is_characters:
                answer = self._format_characters(raw)
            elif q.is_matching:
                answer = self._format_matching(raw, q)
            elif q.is_fill_blank:
                answer = self._format_fill_blank(raw, q)
            elif q.is_cloze:
                answer = self._format_cloze(raw, q)
            else:
                answer = raw or "(no answer)"
            lines.append(f"Q{q.order} [{q.get_category_display()}]: {q.prompt}")
            lines.append(f"A: {answer}")
            lines.append("")
        return "\n".join(lines).strip()

    @staticmethod
    def _format_characters(raw):
        """Render a character answer ({name: text} JSON) as readable lines."""
        try:
            data = json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            data = {}
        if not isinstance(data, dict) or not data:
            return "(no answer)"
        parts = [f"{name}: {text}" for name, text in data.items() if str(text).strip()]
        return "\n" + "\n".join(parts) if parts else "(no answer)"

    @staticmethod
    def _parse_json_answer(raw):
        try:
            data = json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            data = {}
        return data if isinstance(data, dict) else {}

    @classmethod
    def _format_matching(cls, raw, question):
        """Render a matching answer ({"matches": {word: n}, "tries": N})."""
        data = cls._parse_json_answer(raw)
        matches = data.get("matches") or {}
        if not isinstance(matches, dict) or not matches:
            return "(no answer)"
        defs = {
            d.get("n"): d.get("text", "")
            for d in question.vocab_data.get("definitions", [])
            if isinstance(d, dict)
        }
        parts = [
            f"{word} → {n} ({defs.get(n, '?')}) ✓"
            for word, n in matches.items()
        ]
        tries = data.get("tries")
        if isinstance(tries, int) and tries:
            parts.append(f"({tries} wrong tr{'y' if tries == 1 else 'ies'} along the way)")
        return "\n" + "\n".join(parts)

    @classmethod
    def _format_fill_blank(cls, raw, question):
        """Render a fill-blank answer ({"blanks": {index: word}, "tries": N})."""
        data = cls._parse_json_answer(raw)
        blanks = data.get("blanks") or {}
        if not isinstance(blanks, dict) or not blanks:
            return "(no answer)"
        sentences = question.vocab_data.get("sentences", [])

        def _idx(key):
            try:
                return int(key)
            except (ValueError, TypeError):
                return -1

        parts = []
        for key in sorted(blanks, key=_idx):           # sentence order, not completion order
            word = blanks[key]
            i = _idx(key)
            try:
                sentence = sentences[i].get("text", "") if i >= 0 else "?"
            except (IndexError, AttributeError, TypeError):
                sentence = "?"
            parts.append(f"{sentence.replace('______', f'[{word}]')} ✓")
        tries = data.get("tries")
        if isinstance(tries, int) and tries:
            parts.append(f"({tries} wrong tr{'y' if tries == 1 else 'ies'} along the way)")
        return "\n" + "\n".join(parts)

    @classmethod
    def _format_cloze(cls, raw, question):
        """Render a cloze answer ({"blanks": {index: text}}) — the passage with
        the child's words dropped into their blanks."""
        data = cls._parse_json_answer(raw)
        blanks = data.get("blanks") or {}
        if not isinstance(blanks, dict) or not any(str(v).strip() for v in blanks.values()):
            return "(no answer)"
        out = []
        for seg in question.cloze_segments:
            if seg["blank"] is None:
                out.append(seg["text"])
            else:
                word = str(blanks.get(str(seg["blank"]), "")).strip()
                out.append(f"[{word}]" if word else "[   ]")
        return "\n" + "".join(out)
