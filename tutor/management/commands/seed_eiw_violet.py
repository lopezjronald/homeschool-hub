"""Seed Violet's Essentials in Writing (Grade 3) forms (idempotent).

Builds the EIW Level 3 curriculum and turns the workbook exercises into
interactive portal forms: "underline / circle / mark" exercises become
mouse-drawing MARKUP questions (she draws right on the sentence), while
fill-in-the-blank, short-answer, and writing exercises become typed answers —
all autosaving as she works.

Examples:
    python manage.py seed_eiw_violet --for-user ronald
    python manage.py seed_eiw_violet --for-user ronald --child-name Violet
"""

import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet

from ._eiw_content import EXERCISES, LESSON_TITLES

# kind -> (category, response_type, kid-facing label)
KIND_MAP = {
    "sentence-editing": ("editing", Question.TYPE_MARKUP, "Mark the sentences"),
    # fill-blank renders as a CLOZE: the passage with real inline input boxes at
    # each blank — not a wall of underscores over one big textarea.
    "fill-blank": ("grammar", Question.TYPE_CLOZE, "Fill in the blanks"),
    "short-answer": ("grammar", Question.TYPE_TEXT, "Practice"),
    "paragraph-writing": ("writing", Question.TYPE_TEXT, "Write"),
    "multiple-choice": ("grammar", Question.TYPE_TEXT, "Choose the answer"),
}

MARKUP_INTRO_HINT = (
    " ✏️ Use a pen and draw right on the sentence — underline, circle, or cross "
    "out. Pick a color, and use Undo or Erase all if you need to fix something!"
)

RUBRIC = """## Essentials in Writing — how this is checked

- **Editing & grammar:** the right words are marked (underlined / circled / crossed
  out) and any punctuation or capitalization follows the rule taught in this lesson.
- **Writing:** complete sentences with a clear subject and predicate, on topic, with
  capital letters and end punctuation — neat and readable.

Grade-3 mastery: Beginning → Developing → Proficient → Mastered.
"""


class Command(BaseCommand):
    help = "Seed Violet's Essentials in Writing 3 forms (markup + typed). Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True)
        parser.add_argument("--child-name", default="Violet")

    @transaction.atomic
    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        blueprint = get_blueprint("essentials_in_writing_3")
        family = get_active_family(user)
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=blueprint["name"],
            defaults={"subject": blueprint["subject"], "grade_level": blueprint["grade_level"], "family": family},
        )
        chapters, lessons = apply_blueprint(curriculum, blueprint)
        self.stdout.write(f"{'Created' if created else 'Using'} curriculum #{curriculum.pk} "
                          f"({chapters} sections, {lessons} lessons).")

        child = Student.objects.filter(parent=user, first_name__iexact=options["child_name"]).first()
        if child is None:
            raise CommandError(f"No child named '{options['child_name']}' found.")
        first_lesson = Lesson.objects.get(chapter__curriculum=curriculum, chapter__number=1, order=1)
        _, placed = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum, defaults={"current_lesson": first_lesson},
        )

        lessons_by_number = {
            lsn.number: lsn
            for lsn in Lesson.objects.filter(chapter__curriculum=curriculum)
            if lsn.number is not None
        }

        set_count = q_count = markup_count = 0
        for lesson_num in sorted(EXERCISES):
            lesson_row = lessons_by_number.get(lesson_num)
            if lesson_row is None:
                continue
            title_base = LESSON_TITLES.get(lesson_num, f"Lesson {lesson_num}")
            used = {}
            for exercise in EXERCISES[lesson_num]:
                category, response_type, label = KIND_MAP.get(
                    exercise["kind"], ("grammar", Question.TYPE_TEXT, "Practice"),
                )
                is_markup = response_type == Question.TYPE_MARKUP
                # Some writing practice ALSO asks her to circle/underline parts of
                # the sentence SHE writes → a write-then-markup box (type it, then
                # draw right on it).
                wants_writemark = bool(
                    response_type == Question.TYPE_TEXT
                    and re.search(r"\b(circle|underline)\b", exercise["instructions"], re.I)
                )
                title = f"Lesson {lesson_num} · {title_base} — {label}"
                used[title] = used.get(title, 0) + 1
                if used[title] > 1:
                    title = f"{title} ({used[title]})"
                intro = exercise["instructions"] + (
                    MARKUP_INTRO_HINT if is_markup or wants_writemark else ""
                )

                qset, _ = QuestionSet.objects.update_or_create(
                    lesson=lesson_row, title=title,
                    defaults={
                        "family": family,
                        "reading": "",
                        "intro": intro,
                        "rubric": RUBRIC,
                        "status": QuestionSet.APPROVED,
                    },
                )
                for order, item in enumerate(exercise["items"], start=1):
                    if is_markup:
                        defaults = {
                            "category": category,
                            "response_type": Question.TYPE_MARKUP,
                            "passage": item,
                            "prompt": "",
                        }
                    elif response_type == Question.TYPE_CLOZE and re.search(r"_{3,}", item):
                        # The blanked text becomes the passage; each underscore
                        # run renders as an inline input box.
                        defaults = {
                            "category": category,
                            "response_type": Question.TYPE_CLOZE,
                            "passage": item,
                            "prompt": "",
                        }
                    elif wants_writemark:
                        defaults = {
                            "category": category,
                            "response_type": Question.TYPE_WRITE_MARKUP,
                            "passage": "",
                            "prompt": item,
                        }
                    else:
                        defaults = {
                            "category": category,
                            "response_type": Question.TYPE_TEXT,
                            "passage": "",
                            "prompt": item,
                        }
                    Question.objects.update_or_create(
                        question_set=qset, order=order, defaults=defaults,
                    )
                    q_count += 1
                    markup_count += 1 if is_markup else 0
                # prune stale questions that have no saved answer
                stale = qset.questions.filter(order__gt=len(exercise["items"]))
                answered = set()
                for sheet in ResponseSheet.objects.filter(question_set=qset):
                    answered |= {int(k) for k, v in (sheet.answers or {}).items()
                                 if str(v).strip() and k.isdigit()}
                stale.exclude(pk__in=answered).delete()
                set_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {set_count} question sets, {q_count} questions "
            f"({markup_count} draw-on-the-sentence). {child.first_name} placed at "
            f"{'Lesson 1' if placed else 'existing progress (kept)'}."
        ))
