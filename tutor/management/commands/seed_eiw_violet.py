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

import json
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet

from ._eiw_content import (
    EXERCISES, LESSON_TITLES, TEACH_NOTES,
    antecedent_model_html, pronoun_list_html,
)

# kind -> (category, response_type, kid-facing label)
KIND_MAP = {
    "sentence-editing": ("editing", Question.TYPE_MARKUP, "Mark the sentences"),
    # fill-blank renders as a CLOZE: the passage with real inline input boxes at
    # each blank — not a wall of underscores over one big textarea.
    "fill-blank": ("grammar", Question.TYPE_CLOZE, "Fill in the blanks"),
    "short-answer": ("grammar", Question.TYPE_TEXT, "Practice"),
    "paragraph-writing": ("writing", Question.TYPE_TEXT, "Write"),
    "multiple-choice": ("grammar", Question.TYPE_TEXT, "Choose the answer"),
    # A tap-to-pair exercise: ONE question, not one per row. The workbook prints
    # these as a column of blanks beside a lettered answer bank, which flattens
    # into a single list of items — and seeding that list as separate questions
    # turns the answer bank itself into four unanswerable questions.
    "matching": ("grammar", Question.TYPE_MATCHING, "Match them up"),
}

MARKUP_INTRO_HINT = (
    " ✏️ Use a pen and draw right on the sentence — underline, circle, or cross "
    "out. Pick a color, and use Undo or Erase all if you need to fix something!"
)

def build_intro(exercise, wants_pen_hint):
    """Assemble what the child reads before she starts.

    Order matters: the thing she has to DO goes first and in bold. The workbook
    prints the definition and the worked example above every exercise, but when
    all of it was concatenated into one paragraph the actual instruction
    ("Underline the pronouns") ended up buried mid-blob and got missed.
    """
    parts = [f"**{exercise['instructions'].strip()}**"]

    note = TEACH_NOTES.get(exercise.get("teach"))
    if note:
        parts.append(note)

    model = exercise.get("model")
    if model:
        parts.append(antecedent_model_html(*model))

    if exercise.get("visual") == "pronoun-list":
        parts.append(pronoun_list_html())

    if wants_pen_hint:
        parts.append(MARKUP_INTRO_HINT.strip())

    return "\n\n".join(parts)


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
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report which superseded sets would be removed, without removing "
                 "them. Worth doing first against live data.",
        )

    @staticmethod
    def _prune_questions(qset, *, keep_through):
        """Drop questions past ``keep_through`` that nobody has answered.

        Answers are keyed by question pk, so deleting an answered question would
        strand a child's response with nothing to render it against.
        """
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()

    @staticmethod
    def _has_work(qset):
        """True if a child has anything invested in this set.

        Deliberately wider than "has typed an answer". A SUBMITTED sheet is what
        lesson completion counts, so deleting one rolls the lesson back to
        not-done and moves the child's "What's Next" pointer backwards — even if
        every answer box was left blank, which is exactly what a child does with
        a broken exercise. A linked work-log entry or saved coach feedback is
        likewise work she did.
        """
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            if sheet.is_submitted or sheet.work_entry_id or sheet.draft_feedback:
                return True
            if any(str(v).strip() for v in (sheet.answers or {}).values()):
                return True
        return False

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

        dry_run = options.get("dry_run", False)
        set_count = q_count = markup_count = 0
        for lesson_num in sorted(EXERCISES):
            lesson_row = lessons_by_number.get(lesson_num)
            if lesson_row is None:
                continue
            title_base = LESSON_TITLES.get(lesson_num, f"Lesson {lesson_num}")
            used = {}
            produced = set()
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
                # An explicit label beats the generic kind label. Six exercises in
                # one lesson all called "Mark the sentences (n)" tell the child
                # nothing about whether to underline, circle, or rewrite — which is
                # the one thing she needs to know before she starts.
                label = exercise.get("label") or label
                title = f"Lesson {lesson_num} · {title_base} — {label}"
                used[title] = used.get(title, 0) + 1
                if used[title] > 1:
                    title = f"{title} ({used[title]})"
                produced.add(title)
                intro = build_intro(exercise, is_markup or wants_writemark)

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
                if response_type == Question.TYPE_MATCHING:
                    # One question for the whole grid. `items` are (row, answer)
                    # pairs; `options` is the pool the child taps, kept in the
                    # workbook's printed order.
                    pairs = exercise["items"]
                    Question.objects.update_or_create(
                        question_set=qset, order=1,
                        defaults={
                            "category": category,
                            "response_type": Question.TYPE_MATCHING,
                            # The instruction is already the set's intro; repeating
                            # it as the prompt renders it twice on the page.
                            "prompt": "",
                            "passage": json.dumps({
                                "words": exercise["options"],
                                "definitions": [
                                    {"n": n, "text": row, "word": answer}
                                    for n, (row, answer) in enumerate(pairs, start=1)
                                ],
                            }),
                        },
                    )
                    q_count += 1
                    # Same answered-question guard the text path uses below: a
                    # matching set that ever sheds rows must not take a child's
                    # saved answers with them.
                    self._prune_questions(qset, keep_through=1)
                    set_count += 1
                    continue

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
                self._prune_questions(qset, keep_through=len(exercise["items"]))
                set_count += 1

            # Retitling an exercise (e.g. Lesson 7 moving from "Choose the answer"
            # to "Match them up") would otherwise leave the old set beside the new
            # one, since sets are keyed on title — and the old one is the broken
            # one. Drop what this run no longer produces.
            #
            # Scoped to what THIS seeder owns: a teacher-led discussion set or a
            # per-child set was put there by something else, and can never have a
            # ResponseSheet to protect it (discussion sets are excluded from the
            # child's portal), so an unscoped sweep would delete them every run.
            superseded = (
                QuestionSet.objects
                .filter(lesson=lesson_row, mode=QuestionSet.MODE_STUDENT, child__isnull=True)
                .exclude(title__in=produced)
            )
            for old in superseded:
                if self._has_work(old):
                    self.stdout.write(self.style.WARNING(
                        f"Kept superseded set '{old.title}' — a child has work in it."
                    ))
                    continue
                # Say what went. This runs against live data and the deletion is
                # not reversible, so "it silently vanished" is not something anyone
                # should have to reconstruct afterwards.
                self.stdout.write(self.style.WARNING(
                    f"Removed superseded set '{old.title}' "
                    f"({old.questions.count()} questions, no saved work)."
                ))
                if not dry_run:
                    old.delete()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {set_count} question sets, {q_count} questions "
            f"({markup_count} draw-on-the-sentence). {child.first_name} placed at "
            f"{'Lesson 1' if placed else 'existing progress (kept)'}."
        ))
