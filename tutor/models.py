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
    ai_parent_pointers = models.JSONField(
        default=list, blank=True,
        help_text="Parent/teacher-facing coaching pointers (how to help with the "
                  "concept) shown on the review page — never shown to the child.",
    )

    parent_override_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)
    final_level = models.CharField(max_length=20, choices=mastery.CHOICES, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # One assessment per piece of work. This was enforced only by a row lock
            # taken on the shared WorkLogEntry during grading, which does not cover a
            # management command, a shell fix-up, or a future caller that forgets it —
            # and prod had already accumulated a work entry with THREE assessments.
            # A duplicate shows the parent two mastery levels for one piece of work
            # and double-counts it in the charter report's distribution and trends.
            models.UniqueConstraint(
                fields=["work_entry"], name="unique_assessment_per_work_entry",
            ),
        ]

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
    SKILL_LESSON = "lesson"
    SKILL_CHOICES = [
        (SKILL_MANGA, "Manga"),
        (SKILL_COMIC, "Comic"),
        (SKILL_FLASHCARDS, "Flashcards"),
        (SKILL_DRILL, "Drill"),
        (SKILL_LESSON, "Illustrated lesson"),
    ]

    # How manga dialogue is laid out. "band" keeps every speech line in a
    # reserved strip under the art, so text can never cover a character (the
    # robust default, per professional lettering practice). "float" overlays
    # balloons on the art and is only safe when the art reserves negative space.
    LAYOUT_BAND = "band"
    LAYOUT_FLOAT = "float"
    LAYOUT_CHOICES = [
        (LAYOUT_BAND, "Reserved dialogue band (text below the art)"),
        (LAYOUT_FLOAT, "Floating balloons (text over the art)"),
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
    manga_text_layout = models.CharField(
        max_length=10,
        choices=LAYOUT_CHOICES,
        default=LAYOUT_BAND,
        help_text="How manga dialogue renders: in a reserved band under each panel "
                  "(never covers the art) or as balloons floating over the art "
                  "(only use when the art reserves empty space for them).",
    )
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

    @property
    def has_blocks(self):
        """True once the material is built from lesson blocks (see LessonBlock)."""
        return self.blocks.exists()


class LessonBlock(models.Model):
    """One piece of a taught lesson — a heading, a worked example, a tool.

    The structural twin of MangaPanel, and for the same reason. A Material's
    ``student_content`` renders ESCAPED (there is no ``|safe`` anywhere in this
    codebase, deliberately), so a rich lesson cannot be stored as HTML and handed
    to a child. Instead the lesson is stored as ordered rows of typed data and the
    template supplies the markup — the same trade manga panels make.

    ``kind`` is a closed vocabulary and ``data`` is its payload. The seeding
    command validates both, so an unknown kind fails loudly at seed time rather
    than rendering as nothing on a child's screen.

    The shape follows the lesson template this course standardised on: say WHY it
    exists before any symbol, number the ideas, give the parent the words to say,
    show the recipe, work examples, translate the textbook's shorthand, then name
    the mistakes everyone makes.
    """

    KIND_MASTHEAD = "masthead"          # the one formula, roles colour-coded
    KIND_PURPOSE = "purpose"            # why anyone does this, in plain words
    KIND_IDEA = "idea"                  # "Idea 1 of 2" — a numbered section
    KIND_SAY = "say"                    # "Say it to her like this:"
    KIND_STEPS = "steps"                # the recipe, numbered
    KIND_WORKED = "worked_example"      # a worked example, statically laid out
    KIND_STEPPER = "stepper"            # a worked example you click through
    KIND_TRANSLATION = "translation"    # textbook shorthand -> plain English
    KIND_ERRORS = "errors"              # wrong line above right line
    KIND_TABLE = "table"                # ratio box, percent box, x-y table
    KIND_MATH = "math"                  # one centred equation
    KIND_REVEAL = "reveal"              # <details> — predict, then check
    KIND_TOOL = "tool"                  # an interactive widget
    KIND_RECAP = "recap"                # the closing rule

    KIND_CHOICES = [
        (KIND_MASTHEAD, "Masthead"),
        (KIND_PURPOSE, "Why this exists"),
        (KIND_IDEA, "Idea"),
        (KIND_SAY, "Say it like this"),
        (KIND_STEPS, "The recipe"),
        (KIND_WORKED, "Worked example"),
        (KIND_STEPPER, "Step-through example"),
        (KIND_TRANSLATION, "Translation"),
        (KIND_ERRORS, "Error patterns"),
        (KIND_TABLE, "Table"),
        (KIND_MATH, "Equation"),
        (KIND_REVEAL, "Predict then check"),
        (KIND_TOOL, "Interactive tool"),
        (KIND_RECAP, "Recap"),
    ]

    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="blocks",
    )
    order = models.PositiveIntegerField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["material", "order"], name="unique_lesson_block_order",
            ),
        ]

    def __str__(self):
        return f"{self.material.title} — block {self.order} ({self.kind})"

    @property
    def config_dom_id(self):
        """Element id for this block's json_script config payload.

        A property rather than template string-building because Django template
        filters take one argument and cannot concatenate; json_script needs the id
        handed to it whole.
        """
        return f"tool-config-{self.pk}"


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
    TYPE_PARAGRAPH = "paragraph"
    TYPE_WRITE_MARKUP = "write_markup"
    RESPONSE_TYPES = [
        (TYPE_TEXT, "Typed answer"),
        (TYPE_MARKUP, "Mark up the sentence (draw)"),
        (TYPE_CHARACTERS, "A box per character"),
        (TYPE_MATCHING, "Match words to numbered definitions"),
        (TYPE_FILL_BLANK, "Fill in the blank from a word bank"),
        (TYPE_CLOZE, "Fill in the blanks with your own words"),
        (TYPE_PARAGRAPH, "Paragraph: rough draft (sections) → final draft"),
        (TYPE_WRITE_MARKUP, "Write a sentence, then mark it up (draw)"),
    ]

    # The rough-draft sections a paragraph question shows by default (the standard
    # workbook shape); override per-question with passage JSON {"sections": [...]}.
    DEFAULT_PARAGRAPH_SECTIONS = [
        "Introduction / Topic Sentence",
        "Supporting Sentences",
        "Concluding Sentence",
    ]

    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    order = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="comprehension")
    prompt = models.TextField()
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPES, default=TYPE_TEXT)
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
    def markup_lines(self):
        """The passage split into lines of numbered words, for the drawing surface.

        Each word is rendered in its own span so the browser can report where it
        sits. Without that the passage is one text blob and a stroke is just
        coordinates over nothing — which is why a marked-up sentence used to reach
        the grader as "annotated: yes" and nothing more. With per-word boxes the
        same strokes can be read back as "underlined 'quickly'".

        Index is global across lines so it identifies a word in the whole passage,
        not its position on a line.
        """
        lines, index = [], 0
        for raw in (self.passage or "").splitlines():
            words = []
            for word in raw.split():
                words.append({"i": index, "text": word})
                index += 1
            lines.append(words)
        return lines

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
    def is_paragraph(self):
        return self.response_type == self.TYPE_PARAGRAPH

    @property
    def is_write_markup(self):
        return self.response_type == self.TYPE_WRITE_MARKUP

    @property
    def paragraph_sections(self):
        """Labeled rough-draft sections for a paragraph question.

        Configurable via passage JSON ``{"sections": [...]}``; falls back to the
        standard three-part paragraph shape from the workbook.
        """
        try:
            data = json.loads(self.passage or "")
            sections = data.get("sections")
            if isinstance(sections, list) and sections:
                return [str(s) for s in sections]
        except (ValueError, TypeError, AttributeError):
            pass
        return list(self.DEFAULT_PARAGRAPH_SECTIONS)

    @property
    def supports_draft_coach(self):
        """True if the writing coach can review this answer as a draft.

        Paragraph questions always coach (the rough-draft sections); otherwise
        rough drafts in the literature guides carry a "ROUGH DRAFT" marker and
        Essentials-in-Writing paragraph work is category "writing".
        """
        if self.is_paragraph:
            return True
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

    def answer_display(self, question):
        """A readable rendering of the child's answer to one question.

        Handles every response type: markup (a note that they drew on the
        sentence), characters/matching/fill-blank/cloze (their structured
        answer, made readable), and plain text. Used by both the work-log text
        and the parent's read-only work browser.
        """
        raw = str(self.answer_for(question)).strip()
        if question.is_markup:
            return self._format_markup(raw, question)
        if question.is_characters:
            return self._format_characters(raw)
        if question.is_matching:
            return self._format_matching(raw, question)
        if question.is_fill_blank:
            return self._format_fill_blank(raw, question)
        if question.is_cloze:
            return self._format_cloze(raw, question)
        if question.is_paragraph:
            return self._format_paragraph(raw, question)
        if question.is_write_markup:
            data = self._parse_json_answer(raw)
            if data:
                text = str(data.get("text", "")).strip()
                marked = bool(data.get("strokes"))
                if text:
                    return f"{text}  [marked up the sentence: {'yes' if marked else 'no'}]"
                return "[marked up the sentence, no words typed]" if marked else "(no answer)"
            return raw or "(no answer)"  # legacy plain-text answer from before this was a markup box
        return raw or "(no answer)"

    def answer_replay(self, question):
        """Her drawn work for one question, redrawn — or None if she drew nothing.

        The text rendering from ``answer_display`` says what the marks were read
        as; this is the marks themselves. A report of a mark-the-sentence
        exercise that shows only prose about the marks isn't showing the work.
        """
        if not (question.is_markup or question.is_write_markup):
            return None
        from .markup import replay_for
        return replay_for(str(self.answer_for(question)).strip(), question)

    def as_worklog_text(self):
        """Format the Q&A as readable text for the work log / grader."""
        lines = []
        for q in self.question_set.questions.all():
            lines.append(f"Q{q.order} [{q.get_category_display()}]: {q.prompt}")
            lines.append(f"A: {self.answer_display(q)}")
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
        return "\n".join(parts) if parts else "(no answer)"

    @staticmethod
    def _parse_json_answer(raw):
        try:
            data = json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            data = {}
        return data if isinstance(data, dict) else {}

    @classmethod
    def _format_paragraph(cls, raw, question):
        """Render a paragraph answer ({"rough": [...], "final": "..."}).

        The FINAL draft is the graded answer; the rough sections come along as
        planning notes so the parent can see her process (they aren't the grade).
        """
        data = cls._parse_json_answer(raw)
        final = str(data.get("final", "")).strip()
        rough = data.get("rough")
        notes = []
        if isinstance(rough, list):
            for i, label in enumerate(question.paragraph_sections):
                val = str(rough[i]).strip() if i < len(rough) and rough[i] is not None else ""
                if val:
                    notes.append(f"{label}: {val}")
        if not final and not notes:
            # A legacy plain-text answer (a text question converted to paragraph,
            # before the widget re-saved it as structured JSON) isn't this shape.
            # Show it rather than losing her writing to "(no answer)"; a truly
            # empty or empty-structured answer still reads "(no answer)".
            stripped = (raw or "").strip()
            if not stripped:
                return "(no answer)"
            try:
                structured = isinstance(json.loads(stripped), dict)
            except (ValueError, TypeError):
                structured = False
            return "(no answer)" if structured else stripped
        lines = [f"Final draft: {final}" if final else "Final draft: (not written yet)"]
        if notes:
            lines.append("[planning notes (not graded) — " + "; ".join(notes) + "]")
        return "\n".join(lines)

    @staticmethod
    def _parse_markup(raw):
        """(strokes, marks, unread) from a markup answer, old shape or new.

        Answers saved before the marks existed are a bare list of strokes. Those
        can never be read back — the word positions they were drawn over are gone
        — so they keep the old behaviour of reporting only that she drew.
        """
        try:
            data = json.loads(raw or "")
        except (ValueError, TypeError):
            return [], [], 0
        if isinstance(data, list):
            return data, [], 0
        if not isinstance(data, dict):
            return [], [], 0
        raw_marks = data.get("marks")
        # A non-list here is a 500 on every page that renders the answer.
        marks = ([m for m in raw_marks if isinstance(m, dict)]
                 if isinstance(raw_marks, list) else [])
        # Autosave accepts whatever the client posts, and this is parsed inside the
        # transaction that turns the work in — so a junk `unread` must degrade, not
        # raise, or a child cannot submit at all.
        try:
            unread = int(data.get("unread") or 0)
        except (TypeError, ValueError):
            unread = 0
        strokes = data.get("strokes")
        return (strokes if isinstance(strokes, list) else []), marks, unread

    @classmethod
    def _format_markup(cls, raw, question):
        """Render a drawn-on sentence as something a grader can actually mark.

        This used to return only "annotated: yes" — the grader could see that she
        had drawn but not what she marked, so every mark-the-sentence exercise was
        ungradeable. Now the child's own marks are named.

        Unread strokes are reported rather than hidden. A stroke the reader could
        not classify is not a wrong answer, and the grader is told so explicitly
        so it doesn't penalise her for the reader's limits.
        """
        strokes, marks, unread = cls._parse_markup(raw)
        if not strokes:
            return f'[nothing marked on "{question.passage}"]'

        parts = []
        by_kind = {}
        for m in marks:
            word = str(m.get("word", "")).strip()
            kind = str(m.get("kind", "")).strip()
            if word and kind:
                by_kind.setdefault(kind, []).append(word)
        for kind in ("underlined", "circled", "crossed out"):
            words = by_kind.get(kind)
            if words:
                parts.append(f"{kind} {', '.join(chr(34) + w + chr(34) for w in words)}")

        if parts:
            body = "; ".join(parts)
            if unread:
                body += f" (plus {unread} other mark(s), not machine-readable)"
            return f'[on "{question.passage}" she {body}]'
        return (f'[she drew {len(strokes)} mark(s) on "{question.passage}"; none were '
                f"machine-readable]")

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
        return "\n".join(parts)

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
        return "\n".join(parts)

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
        return "".join(out)


class AiSpend(models.Model):
    """Monthly AI spend ledger for the tutor path (HH-145).

    One aggregate row per calendar month (``period`` = "YYYY-MM"). ``tutor.spend``
    accumulates here at the provider seam — the instant the API responds, before
    any parse can fail — and reads it back to hard-stop new calls once the month's
    estimated spend reaches ``settings.TUTOR_MONTHLY_COST_CEILING_USD``.

    Cost is stored as ``micro_usd`` (millionths of a dollar, integer) rather than
    derived from the token totals later, because tutor calls two model tiers whose
    prices differ by more than 10x: a month of "1M input tokens" could be $1 or $15
    depending on the mix, so the only accurate moment to price a call is when it is
    made. Integer micro-dollars also keep the running total exact under concurrent
    F() increments, which a float would not.

    The token columns are kept for reporting — they are what an invoice can be
    reconciled against — but they are NOT what the ceiling reads.
    """

    period = models.CharField(max_length=7, unique=True, help_text='Calendar month, "YYYY-MM".')
    input_tokens = models.PositiveBigIntegerField(default=0)
    output_tokens = models.PositiveBigIntegerField(default=0)
    calls = models.PositiveIntegerField(default=0)
    micro_usd = models.PositiveBigIntegerField(
        default=0, help_text="Accumulated estimated cost in millionths of a USD.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period"]

    def __str__(self):
        return f"AiSpend<{self.period}: ${self.micro_usd / 1_000_000:.2f}, {self.calls} calls>"
