import json

from django.conf import settings
from django.core.validators import FileExtensionValidator
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
    KIND_PAGES = "pages"                # the printed source pages, as scans

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
        (KIND_PAGES, "Source pages"),
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
    TYPE_HANDWRITING = "handwriting"
    TYPE_SELF_EVAL = "self_eval"
    TYPE_CHOICE = "choice"
    TYPE_ORDER = "order"
    TYPE_DRAWING = "drawing"
    TYPE_PHOTO = "photo"
    RESPONSE_TYPES = [
        (TYPE_TEXT, "Typed answer"),
        (TYPE_MARKUP, "Mark up the sentence (draw)"),
        (TYPE_CHARACTERS, "A box per character"),
        (TYPE_MATCHING, "Match words to numbered definitions"),
        (TYPE_FILL_BLANK, "Fill in the blank from a word bank"),
        (TYPE_CLOZE, "Fill in the blanks with your own words"),
        (TYPE_PARAGRAPH, "Paragraph: rough draft (sections) → final draft"),
        (TYPE_WRITE_MARKUP, "Write a sentence, then mark it up (draw)"),
        (TYPE_HANDWRITING, "Handwriting: write it by hand on ruled lines"),
        (TYPE_SELF_EVAL, "Self-evaluation: rate each component, and note why"),
        (TYPE_CHOICE, "Multiple choice: pick one, or pick several"),
        (TYPE_ORDER, "Put the steps in order"),
        (TYPE_DRAWING, "Draw it: the picture IS the answer"),
        (TYPE_PHOTO, "Make it: photograph what you made"),
    ]

    # The three-point scale a self-evaluation offers, and the components it rates,
    # when the question does not carry its own. Override per-question with passage
    # JSON {"items": [...], "scale": [...]}.
    DEFAULT_SELF_EVAL_SCALE = ["Excellent", "Satisfactory", "Needs to Improve"]

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
    def is_handwriting(self):
        """Written by hand with a finger or pen, not typed.

        Third-grade writing IS handwriting — asking her to type it trades the
        skill being practised for keyboard hunting. The strokes are stored the
        same way markup strokes are, so the parent's work browser and the
        printed report replay them.
        """
        return self.response_type == self.TYPE_HANDWRITING

    @property
    def is_drawing(self):
        """The answer IS a picture — she draws it, there is nothing to read.

        Same stroke engine and same stored shape as handwriting, so the parent's
        work browser and the printed report replay it with no new code. What
        differs is the paper: a tall unruled surface and a full box of colours,
        because ruled lines and three pencils are for writing on.
        """
        return self.response_type == self.TYPE_DRAWING

    @property
    def is_photo(self):
        """She made a real thing and photographed it.

        The drawing type covers a picture made ON the screen. This covers work
        that was never on a screen at all — clay, paint, card, a thing built on
        the kitchen table — which is the only honest way to set a project whose
        whole point is making something with her hands.
        """
        return self.response_type == self.TYPE_PHOTO

    @property
    def accepts_photo(self):
        """Can she answer this step with a photograph of something real?

        Always true for a making step. Also true for a DRAWING step that opts in
        with {"allow_photo": true}, because a comic page is very often better on
        paper than on a tablet — and every hands-on project already promises in
        its intro that she can photograph each piece.
        """
        if self.is_photo:
            return True
        return bool(self.is_drawing and self.vocab_data.get("allow_photo"))

    @property
    def drawing_height(self):
        """How tall her paper is. A poster needs more room than a doodle."""
        try:
            return max(200, min(900, int(self.vocab_data.get("height", 420))))
        except (TypeError, ValueError, OverflowError):   # 1e400 -> inf -> int() raises
            return 420

    # A box of pencils, not the three greys handwriting gets. First is selected.
    DRAWING_COLOURS = [
        ("Black", "#222222"), ("Red", "#D64545"), ("Orange", "#E07B39"),
        ("Yellow", "#E8B93B"), ("Green", "#1E7A50"), ("Blue", "#2B6CB0"),
        ("Purple", "#7A4FA3"), ("Pink", "#D96BA0"), ("Brown", "#8B5E34"),
    ]

    @property
    def drawing_colours(self):
        """The palette for a drawing question, overridable per question."""
        chosen = self.vocab_data.get("colours")
        if isinstance(chosen, list) and chosen:
            pairs = [c for c in chosen
                     if isinstance(c, (list, tuple)) and len(c) == 2]
            if pairs:
                return [{"name": str(n), "hex": str(h)} for n, h in pairs]
        return [{"name": n, "hex": h} for n, h in self.DRAWING_COLOURS]

    @property
    def is_write_markup(self):
        return self.response_type == self.TYPE_WRITE_MARKUP

    @property
    def offers_answer_mode(self):
        """Whether to offer "type it or write it" on this question.

        Only for plain typed answers, and only where there is real writing to
        do — a one-word vocabulary answer does not need a pen, and a pen is
        slower for it. Set per question with passage JSON {"answer_mode": true}.
        """
        return (self.response_type == self.TYPE_TEXT
                and self.vocab_data.get("answer_mode") is True)

    @property
    def is_choice(self):
        """Pick one answer, or pick several.

        Studies Weekly is mostly multiple choice, several questions carrying a
        map or a photograph, and one asking her to pick every picture that
        shows human geography. Options live in passage JSON:

            {"options": [{"key": "a", "text": "...", "image": "weekly/..."}],
             "multi": false}

        Gradeable without the AI — see ``choice_correct`` — so a ten-question
        check does not cost a model call.
        """
        return self.response_type == self.TYPE_CHOICE

    @property
    def is_order(self):
        """Put these in the right order.

        Studies Weekly calls it "sorting": five steps of a process, printed
        scrambled, and she numbers them. Stored as {"steps": [...]} in printed
        (scrambled) order with {"correct": [...]} holding them in the right one.
        """
        return self.response_type == self.TYPE_ORDER

    @property
    def order_steps(self):
        """The steps as printed — scrambled — in the order she first sees them."""
        steps = self.vocab_data.get("steps")
        return [str(s) for s in steps] if isinstance(steps, list) else []

    @property
    def order_positions(self):
        """1..n, for the number picker beside each step."""
        return list(range(1, len(self.order_steps) + 1))

    @property
    def order_correct(self):
        """The steps in the right order."""
        right = self.vocab_data.get("correct")
        return [str(s) for s in right] if isinstance(right, list) else []

    @property
    def choice_options(self):
        """The options as printed, in order. Empty if the JSON is malformed —
        the template must degrade rather than render a question with no answers."""
        opts = self.vocab_data.get("options")
        if not isinstance(opts, list):
            return []
        out = []
        for i, o in enumerate(opts):
            if not isinstance(o, dict):
                continue
            out.append({
                "key": str(o.get("key") or chr(97 + i)),
                "text": str(o.get("text") or ""),
                "image": str(o.get("image") or ""),
            })
        return out

    @property
    def choice_has_images(self):
        """True when the options ARE pictures — lay them out as a grid, not a list."""
        return any(o["image"] for o in self.choice_options)

    @property
    def choice_is_multi(self):
        """True when more than one option is expected — 'which ARE examples'."""
        return bool(self.vocab_data.get("multi"))

    @property
    def choice_correct(self):
        """The option keys that count as right, as a set."""
        raw = self.vocab_data.get("correct")
        if isinstance(raw, str):
            raw = [raw]
        return {str(k) for k in raw} if isinstance(raw, list) else set()

    @property
    def figure(self):
        """A picture the question is ABOUT — a map to read, a source to study.

        Distinct from an option's image: this one sits above the question and
        is not an answer. Static path, from passage JSON {"figure": "..."}.
        """
        return str(self.vocab_data.get("figure") or "")

    @property
    def figure_caption(self):
        return str(self.vocab_data.get("figure_caption") or "")

    @property
    def is_self_eval(self):
        """She judges her own draft against a list of components.

        The writing guides all reach this step — read it aloud a second time,
        rate each part, note how you would strengthen it — and it is the step
        that turns a rough draft into a final one. It is HER judgement, not a
        graded answer — ``ResponseSheet._format_self_eval`` labels it as her own
        judgement so the grader does not mark her down for naming a weakness.
        """
        return self.response_type == self.TYPE_SELF_EVAL

    @property
    def self_eval_items(self):
        """The components she rates, in printed order.

        From passage JSON {"items": [...]}; empty if the question carries none,
        which the template must degrade on rather than render an empty form.
        """
        items = self.vocab_data.get("items")
        if isinstance(items, list):
            return [str(i) for i in items if str(i).strip()]
        return []

    @property
    def self_eval_scale(self):
        """The rating options, from passage JSON {"scale": [...]}."""
        scale = self.vocab_data.get("scale")
        if isinstance(scale, list) and scale:
            return [str(s) for s in scale]
        return list(self.DEFAULT_SELF_EVAL_SCALE)

    @property
    def self_eval_wants_notes(self):
        """Whether each component gets a "how would you strengthen this?" line.

        The rating form does; the blueprint checklist does not — the book prints
        thirty bare checkboxes there, and thirty note fields would turn a
        two-minute check into a chore and bury the ratings that matter.
        Suppress with passage JSON {"notes": false}.
        """
        return self.vocab_data.get("notes", True) is not False

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
    def paragraph_section_rows(self):
        """How tall each rough-draft box should be, in rows.

        From passage JSON {"section_rows": [...]}. The fallback is the shape the
        template used to hardcode — a short opener, a tall middle, a short close
        — which is right for a three-part paragraph and wrong for anything else:
        the essay's three BODY paragraphs are eight sentences each, and two of
        them were being handed a two-row box.
        """
        rows = self.vocab_data.get("section_rows")
        sections = self.paragraph_sections
        if isinstance(rows, list) and len(rows) == len(sections):
            try:
                return [max(2, int(r)) for r in rows]
            except (TypeError, ValueError):
                pass
        return [4 if i == 1 else 2 for i in range(len(sections))]

    @property
    def paragraph_boxes(self):
        """(label, rows) per rough-draft section, paired for the template.

        Django templates cannot index one list by another's loop counter, and
        the near-miss (`|slice:forloop.counter0`) silently yields nothing — so
        the pairing is done here where it can be tested.
        """
        return [{"label": label, "rows": rows} for label, rows
                in zip(self.paragraph_sections, self.paragraph_section_rows)]

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

    # HOW the section was completed. Some of this work is done on paper — the
    # guide is a paper book — and a photo or scan of it IS the work. A paper
    # section still becomes SUBMITTED and still lands in the work log; this
    # field is what tells the report to show the file instead of the answers.
    ON_SCREEN = "on_screen"
    ON_PAPER = "on_paper"
    COMPLETION_CHOICES = [
        (ON_SCREEN, "Answered on screen"),
        (ON_PAPER, "Done on paper, uploaded"),
    ]
    completion_mode = models.CharField(
        max_length=20, choices=COMPLETION_CHOICES, default=ON_SCREEN)

    # The project itself: a photo of her page, a scan, a PDF, a document.
    # ONE owner for the file — the sheet. The work-log entry does NOT get a
    # copy, so deleting one cannot leave the other pointing at a dead key.
    PROJECT_EXTENSIONS = (".png", ".jpg", ".jpeg", ".heic", ".webp",
                          ".pdf", ".doc", ".docx")
    PROJECT_MAX_BYTES = 25 * 1024 * 1024
    attachment = models.FileField(
        upload_to="projects/%Y/%m/",
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=[e.lstrip(".") for e in PROJECT_EXTENSIONS])],
        help_text="A photo, scan, PDF or document of the finished work.",
    )
    attachment_uploaded_at = models.DateTimeField(null=True, blank=True)
    # Set when a parent says the uploaded work counts. Completion needs BOTH
    # a file and this — an upload on its own is not a finished section, and a
    # tick on its own has nothing behind it.
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_response_sheets",
    )

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

    @property
    def is_on_paper(self):
        return self.completion_mode == self.ON_PAPER

    @property
    def has_project_file(self):
        return bool(self.attachment)

    @property
    def awaiting_approval(self):
        """She has handed something in and it needs a parent's eye."""
        return self.has_project_file and not self.is_submitted

    @property
    def project_filename(self):
        import os

        return os.path.basename(self.attachment.name) if self.attachment else ""

    @property
    def project_is_image(self):
        """True if the upload can be shown inline rather than linked.

        HEIC is excluded deliberately: browsers do not render it, so an <img>
        would be a broken icon in the middle of the printed report.
        """
        import os

        if not self.attachment:
            return False
        ext = os.path.splitext(self.attachment.name)[1].lower()
        return ext in (".png", ".jpg", ".jpeg", ".webp")

    def answer_for(self, question):
        return (self.answers or {}).get(str(question.pk), "")

    @property
    def answered_count(self):
        answers = self.answers or {}
        n = sum(1 for v in answers.values() if self._counts_as_answered(v))
        # A photographed answer lives in its own table, not in `answers`, so the
        # sum above cannot see it. This number renders as "N of M answered"
        # directly above a Turn-it-in button she cannot undo, so a making
        # project would have read "0 of 6" with every step finished.
        if self.pk is None:
            return n                       # unsaved sheet: no photos can exist yet
        photo_question_ids = set(self.photos.values_list("question_id", flat=True))
        n += sum(1 for qid in photo_question_ids
                 if not self._counts_as_answered(answers.get(str(qid), "")))
        return n

    @staticmethod
    def _counts_as_answered(raw):
        """Is this stored answer finished, not merely started?

        "Not empty" is the rule for almost everything, and it stays the rule —
        changing it for every widget would move the number under children who
        are part-way through a page right now.

        An ORDERING answer is the exception because it says so itself: it stores
        one slot per step with "" where she has not placed one, so a sort with
        one number in it is visibly unfinished. It has to be read that way,
        because this count renders as "N of M answered" directly above a
        "Turn it in" button she cannot undo.
        """
        text = str(raw).strip()
        if not text:
            return False
        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            return True
        if isinstance(data, dict) and isinstance(data.get("order"), list):
            return bool(data["order"]) and all(
                str(slot).strip() for slot in data["order"])
        return True

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
        if question.is_handwriting:
            return self._format_handwriting(raw, question)
        if question.is_drawing:
            return self._format_drawing(raw)
        if question.is_photo:
            return self._format_photo(question)
        if question.is_self_eval:
            return self._format_self_eval(raw, question)
        if question.is_choice:
            return self._format_choice(raw, question)
        if question.is_order:
            return self._format_order(raw, question)
        # A text question whose answer holds strokes: she chose "write it"
        # on the answer-mode picker. The response_type was fixed when the
        # question was authored, so the shape of what she actually wrote is
        # the only thing that can tell us.
        if question.response_type == question.TYPE_TEXT and self._looks_drawn(raw):
            return self._format_handwriting(raw, question)
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

    def _format_photo(self, question):
        n = self.photos.filter(question=question).count()
        if not n:
            return "(nothing photographed yet)"
        return "[photographed what she made: %d %s]" % (n, "photo" if n == 1 else "photos")

    def photos_for(self, question):
        """Her photographs for one question, oldest first."""
        return list(self.photos.filter(question=question))

    def answer_replay(self, question):
        """Her drawn work for one question, redrawn — or None if she drew nothing.

        The text rendering from ``answer_display`` says what the marks were read
        as; this is the marks themselves. A report of a mark-the-sentence
        exercise that shows only prose about the marks isn't showing the work.
        """
        if not (question.is_markup or question.is_write_markup
                or question.is_handwriting or question.is_drawing):
            # …unless she used the answer-mode picker and wrote it by hand on a
            # question that was authored for typing. The marks are the answer
            # either way, and the reports have to show them.
            if not (question.response_type == question.TYPE_TEXT
                    and self._looks_drawn(str(self.answer_for(question)).strip())):
                return None
        from .markup import replay_for
        return replay_for(str(self.answer_for(question)).strip(), question)

    @property
    def _handwriting_orders(self):
        return [q.order for q in self.question_set.questions.all()
                if q.response_type == Question.TYPE_HANDWRITING]

    @property
    def is_handwritten_only(self):
        """True when every answer on this sheet was written by hand."""
        types = {q.response_type for q in self.question_set.questions.all()}
        return bool(types) and types == {Question.TYPE_HANDWRITING}

    @staticmethod
    def _plain(text):
        """A prompt's words, without its Markdown.

        Prompts are authored in Markdown because the child's page renders them.
        This transcript is PLAIN TEXT — it goes to the work log, to the grader,
        and onto the parent's mastery page — so the markers leak: "**Blank A**"
        and "## Let's write" appear as themselves in the middle of a
        question a parent is reading to decide a mastery level.

        Deliberately literal rather than a Markdown round-trip: it must never
        drop a word, and a question that genuinely contains an asterisk should
        keep it.
        """
        out = str(text or "")
        # Asterisks only. Underscores are NOT emphasis in these prompts — they
        # are the printed blank: "A ___A___ question guides inquiry" would come
        # out as "A _A_ question", which is a different question.
        for marker in ("***", "**"):
            out = out.replace(marker, "")
        # Leading heading hashes only — a mid-sentence "#3" is not a heading.
        lines = [line.lstrip("#").lstrip() if line.lstrip().startswith("#")
                 else line for line in out.split("\n")]
        return "\n".join(lines).strip()

    def as_worklog_text(self):
        """Format the Q&A as readable text for the work log / grader."""
        lines = []
        for q in self.question_set.questions.all():
            lines.append("Q%d [%s]: %s"
                         % (q.order, q.get_category_display(),
                            self._plain(q.prompt)))
            lines.append(f"A: {self.answer_display(q)}")
            lines.append("")
        text = "\n".join(lines).strip()
        # Say plainly that there is nothing to read. Without this the grader
        # gets "[handwritten answer — 2 pen stroke(s)]" against a rubric asking
        # for complete sentences and a real thought, and scores her on writing it
        # never saw. A MIXED sheet needs this just as much: a Lexicon week is ten
        # typed sentences plus three handwritten ones, and only the ten are
        # readable.
        # Whatever it is told here, it must not be repeated to the child. The
        # child-facing fields are hers to read, and "a grown-up will have to read
        # your writing" lands on a nine-year-old as "what you did was no good".
        privately = (
            " Say this in the summary and the parent pointers only — never in "
            "the encouragement or the child-facing highlights, and never tell "
            "the child anything about her handwriting being unreadable."
        )
        hand = self._handwriting_orders
        if self.is_handwritten_only:
            text = (
                "NOTE TO THE GRADER: every answer here was written BY HAND on the "
                "page and cannot be read as text. Do not judge the content, "
                "spelling, or sentence structure — you cannot see it. Report that "
                "this work is handwritten and needs a person's eyes, and return a "
                'level of "no_evidence" for me to set myself.' + privately
                + "\n\n" + text
            )
        elif hand:
            which = ", ".join(f"Q{o}" for o in hand)
            text = (
                f"NOTE TO THE GRADER: {which} were written BY HAND on the page "
                "and cannot be read as text. Grade only the other questions. Do "
                "not judge the content, spelling, or sentence structure of the "
                "handwritten ones — you cannot see them — and report that they "
                "need a person's eyes." + privately + "\n\n" + text
            )
        return text

    @classmethod
    def _format_drawing(cls, raw):
        """The picture IS the answer, so say a picture is there — and nothing more.

        Without this the stored stroke array reached the grader, the parent's
        work browser and the printed report as raw JSON, which reads as if she
        had answered in gibberish. There is no text to recover: a drawing
        question never asked for any.
        """
        strokes, _marks, _unread = cls._parse_markup(raw)
        if strokes:
            # "Below" is true on the parent's page and the report, where the
            # replay sits under this line. The grader gets text only, so it is
            # told plainly that there is nothing here to read.
            return ("[a drawing — %d pen stroke(s). The picture itself is on "
                    "her page and in the report; there are no words to read "
                    "here, so do not mark it for any.]" % len(strokes))
        # A question can change instrument under an answer she already gave, the
        # same way Operation Lexicon's writing boxes did. Her typed words are
        # still in the sheet; "(nothing drawn yet)" would hide work she did.
        typed = str(raw or "").strip()
        if not typed:
            return "(nothing drawn yet)"
        try:
            json.loads(typed)
        except (ValueError, TypeError):
            return typed
        return "(nothing drawn yet)"

    @classmethod
    def _format_handwriting(cls, raw, question):
        """There is no text to read back — the writing IS the answer.

        Says how much she wrote rather than pretending to transcribe it: a
        grader who sees "(no answer)" for a full page of handwriting would mark
        her down for work she did.
        """
        strokes, _marks, _unread = cls._parse_markup(raw)
        if strokes:
            return f"[handwritten answer — {len(strokes)} pen stroke(s); see the drawing]"
        # A question can change instrument under an answer she already gave —
        # Operation Lexicon's three writing boxes were typed for a few days. Her
        # words are still sitting in the sheet; reporting "nothing written" would
        # hide work she did from the grader, the work browser and the report.
        typed = str(raw or "").strip()
        if not typed:
            return "(nothing written yet)"
        try:
            json.loads(typed)
        except ValueError:
            # Not JSON at all, so it can only be something she typed. Testing
            # the first character instead would hand "[]" and "null" back as if
            # they were her sentence — both are stroke payloads that parsed to
            # nothing, and _parse_markup accepts a bare array as a legacy shape.
            return typed
        return "(nothing written yet)"

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
    def _looks_drawn(raw):
        """True if a stored answer is a stroke payload rather than words."""
        text = (raw or "").strip()
        if not text.startswith("{"):
            return False
        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            return False
        return isinstance(data, dict) and isinstance(data.get("strokes"), list)

    @classmethod
    def _format_order(cls, raw, question):
        """Render a sorted answer ({"order": ["step", …]}) with its verdict.

        A slot she left empty arrives as "" or — from answers saved before the
        widget stopped leaving its array sparse — as null. Both mean "she did
        not place one here", and both must say so: str(None) is the truthy
        string "None", which printed as "1. None" on the charter report.
        """
        data = cls._parse_json_answer(raw)
        got = data.get("order") if isinstance(data, dict) else None
        if not isinstance(got, list):
            return "(no answer)"
        got = ["" if g is None else str(g) for g in got]
        if not [g for g in got if g.strip()]:
            return "(no answer)"
        lines = ["%d. %s" % (i + 1, g or "(left blank)")
                 for i, g in enumerate(got)]
        right = question.order_correct
        if right:
            lines.append("[%s]" % ("correct" if got == right else
                                   "not correct — the order is: "
                                   + " → ".join(right)))
        return "\n".join(lines)

    @classmethod
    def _format_choice(cls, raw, question):
        """Render a chosen answer ({"picked": ["a", "c"]}) as words, not letters.

        A grader handed "a, c" has to go and find what a and c were; handed the
        option text it can say something useful. The right/wrong mark comes from
        the question itself, so a ten-question check needs no model call.
        """
        data = cls._parse_json_answer(raw)
        picked = data.get("picked") if isinstance(data, dict) else None
        if not isinstance(picked, list):
            picked = [raw] if raw else []
        picked = [str(k) for k in picked if str(k).strip()]
        if not picked:
            return "(no answer)"
        by_key = {o["key"]: o for o in question.choice_options}
        shown = []
        for k in picked:
            o = by_key.get(k)
            label = o["text"] if o and o["text"] else (
                "the picture labelled %s" % k if o else k)
            shown.append("%s) %s" % (k, label))
        out = "; ".join(shown)
        correct = question.choice_correct
        if correct:
            got = set(picked) == correct
            want = ", ".join(sorted(correct))
            out += "   [%s — the answer is %s]" % (
                "correct" if got else "not correct", want)
        return out

    @classmethod
    def _format_self_eval(cls, raw, question):
        """Render a self-evaluation answer ({"ratings": {...}, "notes": {...}}).

        Keys are the item's index as a string, matching the widget. The output
        says plainly that this is HER judgement of her own draft, because a
        grader handed a bare list of "Needs to Improve" will otherwise mark her
        down for the very honesty the exercise is asking for — the guide's point
        here is noticing what to strengthen, not having nothing to strengthen.
        """
        data = cls._parse_json_answer(raw)
        ratings = data.get("ratings") if isinstance(data, dict) else None
        notes = data.get("notes") if isinstance(data, dict) else None
        ratings = ratings if isinstance(ratings, dict) else {}
        notes = notes if isinstance(notes, dict) else {}
        items = question.self_eval_items
        lines = []
        for i, label in enumerate(items):
            rating = str(ratings.get(str(i), "")).strip()
            note = str(notes.get(str(i), "")).strip()
            if not rating and not note:
                continue
            row = "%d. %s — %s" % (i + 1, label, rating or "(not rated)")
            if note:
                row += " · note: %s" % note
            lines.append(row)
        if not lines:
            return "(no answer)"
        return ("[self-evaluation of her own draft — her judgement, not "
                "answers to be marked right or wrong]\n" + "\n".join(lines))

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
        except (TypeError, ValueError, OverflowError):   # 1e400 -> inf -> int() raises
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


class AnswerPhoto(models.Model):
    """A photograph of something she MADE, answering one question (HH-199).

    Answers normally live in ResponseSheet.answers, a JSONField — which can hold
    a drawing's strokes but cannot hold a file. A project whose steps are "build
    this, photograph it" therefore needs its own table.

    MANY per question, deliberately. One slot would force a single shot of a
    made object, and the front and the back of a dust jacket are two different
    photographs. Mirrors curricula.LessonWork, which solved the same problem for
    work done on paper.
    """

    PHOTO_EXTENSIONS = (".png", ".jpg", ".jpeg", ".heic", ".webp")
    PHOTO_MAX_BYTES = 25 * 1024 * 1024
    MAX_PER_QUESTION = 6

    sheet = models.ForeignKey(
        ResponseSheet, on_delete=models.CASCADE, related_name="photos",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answer_photos",
    )
    image = models.ImageField(
        upload_to="answer_photos/%Y/%m/",
        validators=[FileExtensionValidator(
            allowed_extensions=[e.lstrip(".") for e in PHOTO_EXTENSIONS])],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return "photo for q%s" % self.question_id

    @property
    def filename(self):
        import os

        return os.path.basename(self.image.name) if self.image else ""

    @property
    def is_viewable(self):
        """HEIC uploads fine but no browser draws it, so it must never reach an
        <img> — it would print as a broken icon in the middle of her report."""
        import os

        if not self.image:
            return False
        return os.path.splitext(self.image.name)[1].lower() != ".heic"
