from django.conf import settings
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["subject", "name"]
        verbose_name_plural = "curricula"

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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["doc_type", "title"]

    def __str__(self):
        return self.title


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

    def progress(self):
        """Return {done, total, pct}.

        Progress follows the work the child actually turns in: a non-opener lesson
        counts as done once the child has submitted a student sheet for it. The
        ``current_lesson`` pointer is kept only as a floor, so a child a parent
        placed mid-curriculum still gets credit for the lessons skipped past even
        before they submit anything new. (The pointer alone never advances on its
        own, which is why progress must be derived from submitted work.)
        """
        ids = self._progress_lesson_ids()
        total = len(ids)
        if not total:
            return {"done": 0, "total": 0, "pct": 0}

        # Floor: everything before the placement pointer is treated as complete.
        floor = ids.index(self.current_lesson_id) if self.current_lesson_id in ids else 0

        # Completed by work: non-opener lessons in this curriculum the child has
        # turned in a student sheet for. Imported here to avoid a circular import
        # (tutor models reference curricula at module load time).
        from tutor.models import QuestionSet, ResponseSheet

        completed_lesson_ids = set(
            ResponseSheet.objects.filter(
                child_id=self.child_id,
                status=ResponseSheet.SUBMITTED,
                question_set__mode=QuestionSet.MODE_STUDENT,
                question_set__lesson_id__in=ids,
            ).values_list("question_set__lesson_id", flat=True)
        )
        completed = sum(1 for lid in ids if lid in completed_lesson_ids)

        done = min(max(floor, completed), total)
        pct = round(done / total * 100)
        return {"done": done, "total": total, "pct": pct}

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
