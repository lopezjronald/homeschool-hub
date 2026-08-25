from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Curriculum(models.Model):
    """A curriculum/subject that a parent teaches."""

    # Grade choices matching students.Student.GRADE_CHOICES
    GRADE_CHOICES = [
        ("PREK", "Pre-K"),
        ("K", "Kindergarten"),
        ("G01", "1st Grade"),
        ("G02", "2nd Grade"),
        ("G03", "3rd Grade"),
        ("G04", "4th Grade"),
        ("G05", "5th Grade"),
        ("G06", "6th Grade"),
        ("G07", "7th Grade"),
        ("G08", "8th Grade"),
        ("G09", "9th Grade"),
        ("G10", "10th Grade"),
        ("G11", "11th Grade"),
        ("G12", "12th Grade"),
    ]

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="curricula",
    )
    family = models.ForeignKey(
        "core.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curricula",
    )
    name = models.CharField(
        max_length=200,
        help_text="e.g., 'Singapore Math 5A' or 'American History'",
    )
    subject = models.CharField(
        max_length=100,
        help_text="e.g., 'Math', 'Science', 'Reading'",
    )
    grade_level = models.CharField(
        max_length=4,
        choices=GRADE_CHOICES,
        blank=True,
        help_text="Optional grade level for this curriculum",
    )
    website_url = models.URLField(
        blank=True,
        default="",
        help_text="Optional link to the curriculum's website",
    )
    is_online = models.BooleanField(
        default=False,
        help_text="This subject is done on an external website (e.g. Beast Academy, "
                  "DIVE). The child's portal launches out to the website instead of "
                  "showing in-app lessons.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Off means the girls can't see it — either it's queued up for later "
                  "or it's finished. Everything is kept either way.",
    )
    archived_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Set when a course is finished and retired. This is what separates "
                  "'not started yet' from 'done' — both are switched off, but only one "
                  "of them is ever coming back.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # One switch decides visibility (is_active — the gate every portal query already
    # honours); archived_at records WHY it is off. A shelf full of "deactivated"
    # courses can't tell you which are upcoming and which are behind you.
    STATE_IN_USE = "in_use"
    STATE_READY = "ready"
    STATE_ARCHIVED = "archived"
    STATE_LABELS = {
        STATE_IN_USE: "In use",
        STATE_READY: "Ready to start",
        STATE_ARCHIVED: "Archived",
    }

    @property
    def state(self):
        if self.is_active:
            return self.STATE_IN_USE
        return self.STATE_ARCHIVED if self.archived_at else self.STATE_READY

    @property
    def state_label(self):
        return self.STATE_LABELS[self.state]

    @property
    def is_archived(self):
        return self.state == self.STATE_ARCHIVED

    @property
    def is_ready_to_start(self):
        """Loaded ahead of time and waiting — not started, not finished."""
        return self.state == self.STATE_READY

    class Meta:
        ordering = ["subject", "name"]
        verbose_name_plural = "curricula"

    def save(self, **kwargs):
        """Switching a course on always drops the archive stamp.

        The invariant lives here rather than in the toggle view because the edit
        form and the admin can both set is_active directly. Without it you can
        save a row that is visible AND archived, which makes the shelf counts
        report courses that no filter will ever return.
        """
        if self.is_active and self.archived_at is not None:
            self.archived_at = None
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                # Materialise first: Django accepts a generator here, and testing
                # membership on one would consume it and drop every other field.
                update_fields = list(update_fields)
                if "archived_at" not in update_fields:
                    update_fields.append("archived_at")
                kwargs["update_fields"] = update_fields
        super().save(**kwargs)

    def __str__(self):
        return self.name

    @property
    def is_external(self):
        """True when this is an online subject the portal should launch out to."""
        return bool(self.is_online and self.website_url)

    def get_related_assignments_count(self):
        """Return count of related assignments, or 0 if Assignment model doesn't exist yet."""
        # Placeholder for HH-26: when Assignment model exists with FK to Curriculum,
        # this will return the count. For now, safely return 0.
        if hasattr(self, "assignments"):
            return self.assignments.count()
        return 0

    @property
    def has_structure(self):
        """True if this curriculum has been populated with chapters/lessons."""
        return self.chapters.exists()


class Chapter(models.Model):
    """A chapter/unit within a curriculum's scope & sequence."""

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                fields=["curriculum", "number"],
                name="unique_chapter_number_per_curriculum",
            ),
        ]

    def __str__(self):
        return f"Chapter {self.number}: {self.title}"


class Lesson(models.Model):
    """A lesson within a chapter (including openers, practices, and reviews)."""

    TYPE_OPENER = "opener"
    TYPE_LESSON = "lesson"
    TYPE_PRACTICE = "practice"
    TYPE_REVIEW = "review"
    TYPE_CHOICES = [
        (TYPE_OPENER, "Chapter Opener"),
        (TYPE_LESSON, "Lesson"),
        (TYPE_PRACTICE, "Practice"),
        (TYPE_REVIEW, "Review"),
    ]

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    order = models.PositiveIntegerField(
        help_text="Sequence within the chapter (openers first).",
    )
    number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Printed lesson number; blank for openers/reviews.",
    )
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_LESSON,
    )
    objectives = models.TextField(blank=True)

    class Meta:
        ordering = ["chapter__number", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["chapter", "order"],
                name="unique_lesson_order_per_chapter",
            ),
        ]

    def __str__(self):
        return f"{self.chapter.curriculum.name} · {self.code}"

    @property
    def code(self):
        """Short reference, e.g. 'Ch 2, L6', 'Ch 2 Opener', or 'Review 1'."""
        if self.lesson_type == self.TYPE_OPENER:
            return f"Ch {self.chapter.number} Opener"
        if self.lesson_type == self.TYPE_REVIEW:
            return self.title
        if self.number:
            return f"Ch {self.chapter.number}, L{self.number}"
        return self.title


class CurriculumDocument(models.Model):
    """A source document (instructor guide, textbook, etc.) for a curriculum.

    Stored in R2 in production and local media in development. This is the source
    the Teacher agent will read to ground its help (curriculum ingest track).
    """

    TYPE_INSTRUCTOR = "instructor_guide"
    TYPE_TEXTBOOK = "textbook"
    TYPE_WORKBOOK = "workbook"
    TYPE_TESTS = "tests"
    TYPE_OTHER = "other"
    TYPE_CHOICES = [
        (TYPE_INSTRUCTOR, "Instructor's Guide"),
        (TYPE_TEXTBOOK, "Textbook"),
        (TYPE_WORKBOOK, "Workbook"),
        (TYPE_TESTS, "Tests"),
        (TYPE_OTHER, "Other"),
    ]

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(max_length=200)
    doc_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_OTHER,
    )
    file = models.FileField(upload_to="curriculum_docs/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_curriculum_documents",
    )
    # ---- the child-facing booklet -----------------------------------------
    # A source PDF is usually a TEACHER edition: Violet's Studies Weekly issue
    # carries the marked answer key on pages 8-9 and the teacher's lesson plans,
    # with their answers, on 11-19. So a child never gets `file`. She gets
    # `student_file`, which is a NEW pdf holding only the whitelisted pages,
    # built at ingest time. Fail-closed: no whitelist, no booklet.
    student_pages = models.CharField(
        max_length=100, blank=True,
        help_text="Pages of the source PDF a child may see, 1-based — e.g. "
                  "'23-26' or '1-4,9'. Blank means she sees nothing.",
    )
    student_file = models.FileField(
        upload_to="booklets/%Y/%m/", blank=True,
        help_text="Generated: just the student_pages, extracted. Never the "
                  "source file — that is the teacher edition.",
    )
    student_label = models.CharField(
        max_length=200, blank=True,
        help_text="What the child sees it called, e.g. \"This week's issue\".",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["doc_type", "title"]

    def __str__(self):
        return self.title

    @property
    def child_visible(self):
        """Only a document with an extracted file AND a whitelist is offered."""
        return bool(self.student_pages.strip() and self.student_file)

    @property
    def child_label(self):
        return self.student_label or self.title

    @staticmethod
    def parse_pages(spec, page_count=None):
        """'23-26,9' -> [23, 24, 25, 26, 9], 1-based, de-duplicated in order.

        Raises ValueError on anything it cannot read rather than guessing: a
        misread spec here is the difference between four article pages and the
        answer key.
        """
        pages, seen = [], set()
        for part in str(spec or "").split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part.lstrip("-"):
                lo, _, hi = part.partition("-")
                try:
                    lo, hi = int(lo), int(hi)
                except ValueError:
                    raise ValueError(f"{part!r} is not a page range")
                if lo > hi:
                    raise ValueError(f"{part!r} counts backwards")
                span = range(lo, hi + 1)
            else:
                try:
                    span = [int(part)]
                except ValueError:
                    raise ValueError(f"{part!r} is not a page number")
            for n in span:
                if n < 1:
                    raise ValueError(f"page {n} — pages are numbered from 1")
                if page_count is not None and n > page_count:
                    raise ValueError(
                        f"page {n}, but the file has only {page_count}")
                if n not in seen:
                    seen.add(n)
                    pages.append(n)
        if not pages:
            raise ValueError("no pages given — a child would see nothing")
        return pages


class CurriculumPlacement(models.Model):
    """Where a child currently is in a curriculum (per-subject progress pointer).

    ``current_lesson`` is the lesson the child is working on now; everything
    before it in the scope & sequence is treated as completed. This enables
    subjects to advance at independent paces (per-subject acceleration).
    """

    child = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="placements",
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="placements",
    )
    current_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive placements hide this subject from this child's portal only "
                  "(siblings can keep the same curriculum).",
    )
    weekly_pace = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Project remaining lessons onto the family calendar at this many "
                  "per week (Mon–Fri). Blank = no due dates for this subject.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "curriculum"],
                name="unique_placement_per_child_curriculum",
            ),
        ]

    def __str__(self):
        return f"{self.child} — {self.curriculum.name}"

    def _progress_lesson_ids(self):
        """Ordered lesson ids counted toward progress (excludes chapter openers)."""
        return list(
            Lesson.objects
            .filter(chapter__curriculum_id=self.curriculum_id)
            .exclude(lesson_type=Lesson.TYPE_OPENER)
            .order_by("chapter__number", "order")
            .values_list("id", flat=True)
        )

    def resolved_lesson_ids(self):
        """(ordered_ids, resolved_set): non-opener lesson ids counted as done/passed —
        the UNION of (a) explicit LessonProgress completed OR skipped marks, (b) lessons
        with submitted student work, and (c) everything before the placement floor.
        Skipped lessons are 'resolved' so the bar advances past them (HH-141).

        Always reads fresh — callers mutate marks and re-ask within one request. A page
        that needs it more than once should compute it ONCE and pass the result to
        current_actionable_lesson()/progress() rather than caching it on the instance."""
        ids = self._progress_lesson_ids()
        id_set = set(ids)
        # (a) explicit parent marks — fetched ONCE with their status, so progress()
        # can derive the skipped count without a second COUNT query. order_by() clears
        # the model Meta ordering, which would otherwise join chapter on every read.
        self._marks = dict(
            LessonProgress.objects.filter(
                child_id=self.child_id, lesson_id__in=ids,
                status__in=(LessonProgress.COMPLETED, LessonProgress.SKIPPED),
            ).order_by().values_list("lesson_id", "status")
        )
        resolved = set(self._marks)
        # (b) submitted student work (imported here to avoid a circular import)
        from tutor.models import QuestionSet, ResponseSheet
        resolved |= set(
            ResponseSheet.objects.filter(
                child_id=self.child_id, status=ResponseSheet.SUBMITTED,
                question_set__mode=QuestionSet.MODE_STUDENT,
                question_set__lesson_id__in=ids,
            ).values_list("question_set__lesson_id", flat=True)
        )
        # (c) floor: everything before the placement pointer
        if self.current_lesson_id in id_set:
            resolved |= set(ids[: ids.index(self.current_lesson_id)])
        return ids, resolved & id_set

    def current_actionable_lesson(self, precomputed=None):
        """The first non-opener lesson that is NOT resolved (completed / skipped /
        submitted / below the floor) — the real 'what's next', passing over skips.
        Pass ``precomputed`` (a resolved_lesson_ids() result) to reuse that query."""
        ids, resolved = precomputed if precomputed is not None else self.resolved_lesson_ids()
        nxt = next((lid for lid in ids if lid not in resolved), None)
        return Lesson.objects.filter(pk=nxt).select_related("chapter").first() if nxt else None

    def progress(self, precomputed=None):
        """Return {done, total, pct, skipped}. 'done' counts resolved lessons (so a
        skip advances the bar); the explicit complete/skip marks (HH-141) union with
        submitted work + the placement floor, so literature/writing progress is
        unchanged when no marks exist while math gains a real manual signal. Pass
        ``precomputed`` (a resolved_lesson_ids() result) to reuse that query."""
        ids, resolved = precomputed if precomputed is not None else self.resolved_lesson_ids()
        total = len(ids)
        if not total:
            return {"done": 0, "total": 0, "pct": 0, "skipped": 0}
        # Derived from the marks resolved_lesson_ids already fetched — no extra query.
        skipped = sum(1 for st in self._marks.values() if st == LessonProgress.SKIPPED)
        done = len(resolved)
        return {"done": done, "total": total, "pct": round(done / total * 100),
                "skipped": skipped}

    def next_lesson(self):
        """The lesson after the current one, or None."""
        if not self.current_lesson_id:
            return None
        lessons = list(
            Lesson.objects
            .filter(chapter__curriculum_id=self.curriculum_id)
            .order_by("chapter__number", "order")
        )
        ids = [lsn.id for lsn in lessons]
        if self.current_lesson_id not in ids:
            return None
        idx = ids.index(self.current_lesson_id)
        return lessons[idx + 1] if idx + 1 < len(lessons) else None


class LessonProgress(models.Model):
    """Per-child status for a single lesson: the parent's manual complete/skip mark
    (HH-141). Absence of a row == not started. Rows are created only when a parent
    marks a lesson completed or skipped (or explicitly in-progress); skipped lessons
    are passed over when computing the child's current/next actionable lesson, which
    is exactly what lets a parent skip 'practice' lessons based on performance."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    STATUS_CHOICES = [
        (IN_PROGRESS, "In progress"),
        (COMPLETED, "Completed"),
        (SKIPPED, "Skipped"),
    ]

    child = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="lesson_progress",
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="progress",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=COMPLETED)
    note = models.CharField(
        max_length=300, blank=True,
        help_text="Optional reason, e.g. why a practice lesson was skipped.",
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lesson__chapter__number", "lesson__order"]
        constraints = [
            models.UniqueConstraint(
                fields=["child", "lesson"],
                name="unique_lesson_progress_per_child_lesson",
            ),
        ]

    def __str__(self):
        return f"{self.child} · {self.lesson.code} = {self.status}"


class CurriculumResource(models.Model):
    """A labeled external link attached to a curriculum (answer key, guide,
    read-aloud video, reference page, …). A shelf of links per book/subject.

    Distinct from CurriculumDocument (uploaded files → R2): this is just a URL.
    ``teacher_only`` marks resources — like answer keys — meant for the parent/
    teacher, never surfaced to a child.
    """

    ANSWER_KEY = "answer_key"
    GUIDE = "guide"
    VIDEO = "video"
    REFERENCE = "reference"
    OTHER = "other"
    TYPE_CHOICES = [
        (ANSWER_KEY, "Answer key"),
        (GUIDE, "Guide"),
        (VIDEO, "Video"),
        (REFERENCE, "Reference"),
        (OTHER, "Link"),
    ]
    TYPE_EMOJI = {
        ANSWER_KEY: "🔑", GUIDE: "📖", VIDEO: "🎬", REFERENCE: "📌", OTHER: "🔗",
    }

    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="resources",
    )
    label = models.CharField(max_length=200, help_text="e.g., 'Answer Key' or 'Read-aloud on YouTube'.")
    url = models.URLField()
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=OTHER)
    teacher_only = models.BooleanField(
        default=False, help_text="Keep this for the teacher — never show it to a child.",
    )
    notes = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.curriculum.name} — {self.label}"

    @property
    def emoji(self):
        return self.TYPE_EMOJI.get(self.resource_type, "🔗")


class LessonWork(models.Model):
    """A file of the child's finished work for ONE lesson.

    WHY THIS EXISTS SEPARATELY. The paper-copy upload built for the literature
    projects hangs off a ResponseSheet, which needs a QuestionSet. Saxon and
    Dimensions have none — they are lesson materials, not turn-in-able work — so
    a maths chapter test had nowhere to live except a Work Log entry, which ties
    it to a DATE rather than to Lesson 71. When a charter reviewer asks to see
    the work for a chapter, a date is the wrong index.

    The alternative — inventing an empty QuestionSet per maths lesson just to
    have something to attach a file to — was rejected: it would put a turn-in
    button in the child's portal for work she does on paper.

    Per CHILD as well as per lesson: two children can sit the same lesson, and
    the file belongs to whoever did it.
    """

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="work_uploads",
    )
    child = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="lesson_work",
    )
    family = models.ForeignKey(
        "core.Family", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lesson_work",
    )
    # Same envelope as the literature projects (tutor.ResponseSheet): one list of
    # extensions, one ceiling, so a parent does not learn two different rules for
    # "photograph the page you just did".
    WORK_EXTENSIONS = (".png", ".jpg", ".jpeg", ".heic", ".webp",
                       ".pdf", ".doc", ".docx")
    WORK_MAX_BYTES = 25 * 1024 * 1024

    file = models.FileField(
        upload_to="lesson_work/%Y/%m/",
        validators=[FileExtensionValidator(
            allowed_extensions=[e.lstrip(".") for e in WORK_EXTENSIONS])],
        help_text="A photo, scan, PDF or document of the finished work.",
    )
    caption = models.CharField(
        max_length=200, blank=True,
        help_text="Optional — e.g. 'Chapter 4 test' or 'practice set B'.",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.child} · {self.lesson} · {self.filename}"

    @property
    def filename(self):
        import os

        return os.path.basename(self.file.name) if self.file else ""

    @property
    def is_image(self):
        """True if it can be shown rather than merely linked.

        HEIC is excluded on purpose, matching ResponseSheet.project_is_image:
        browsers do not render it, so an <img> would be a broken icon in the
        middle of the printed charter report.
        """
        import os

        if not self.file:
            return False
        return os.path.splitext(self.file.name)[1].lower() in (
            ".png", ".jpg", ".jpeg", ".webp",
        )
