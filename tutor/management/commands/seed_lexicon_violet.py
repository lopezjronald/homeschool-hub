"""Seed Violet's Operation Lexicon: Traits of Character (idempotent).

Ten weeks, ten remarkable people, a hundred words for describing character.
Each week becomes three pieces of work:

  1. Meet the words      — the ten words and what they mean (a Material)
  2. Finish the sentences — ten cloze sentences about that person
  3. What amazed you?     — three answers written BY HAND with the pen

The handwriting is the point of the third one. A third grader practising
writing should be forming letters, not hunting for keys, and the strokes replay
in the parent's work browser and print in the charter report.

    python manage.py seed_lexicon_violet --for-user ronald
    python manage.py seed_lexicon_violet --for-user ronald --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.models import Material, Question, QuestionSet, ResponseSheet

from ._lexicon_content import WEEKS

CURRICULUM_NAME = "Operation Lexicon: Traits of Character"

RUBRIC = """## Operation Lexicon — how this is checked

- **Finish the sentences:** the word chosen actually fits the person and the
  sentence. Several words could be grammatically fine; only one matches what
  the story showed about them.
- **What amazed you:** written by hand, in complete sentences, about *this*
  person — not a general comment. Spelling counts less than having a real
  thought and writing it legibly.

Grade-3 mastery: Beginning → Developing → Proficient → Mastered.
"""


def word_bank(week):
    return ", ".join(w for w, _d in week["words"])


class Command(BaseCommand):
    help = "Seed Operation Lexicon: Traits of Character. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True)
        parser.add_argument("--child-name", default="Violet")
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        child = Student.objects.filter(
            parent=user, first_name__iexact=options["child_name"]).first()
        if child is None:
            raise CommandError(f"No child named '{options['child_name']}'.")

        family = get_active_family(user)
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=CURRICULUM_NAME,
            defaults={"subject": "Language Arts", "grade_level": "G03",
                      "family": family},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk}")

        chapter, _ = Chapter.objects.get_or_create(
            curriculum=curriculum, number=1,
            defaults={"title": "Traits of Character"},
        )

        sets = questions = 0
        for week in WEEKS:
            lesson, _ = Lesson.objects.update_or_create(
                chapter=chapter, order=week["number"],
                defaults={
                    "number": week["number"],
                    "title": f"{week['person']} — {week['role']}",
                    "objectives": (
                        f"Read {week['book']}. Collect ten words that describe "
                        f"{week['person']}."
                    ),
                },
            )

            # --- 1. Meet the words -------------------------------------------
            body = [
                f"## Week {week['number']} · {week['person']} — {week['role']}",
                "",
                f"**Read or listen to:** *{week['book']}*  ",
                f"Written by {week['author']}"
                + (f", illustrated by {week['illustrator']}"
                   if week["illustrator"] != week["author"] else ""),
                "",
                "Listen to the story **twice** — once to enjoy it, once to notice "
                "what kind of person this was. Then meet this week's ten words.",
                "",
            ]
            for word, definition in week["words"]:
                body.append(f"- **{word}** — {definition}")
            body += [
                "",
                "Keep these ten in mind. Every sentence in the next task is about "
                f"{week['person']}, and every answer is one of these words.",
            ]
            if not options["dry_run"]:
                Material.objects.update_or_create(
                    lesson=lesson, title=f"Week {week['number']}: meet the words",
                    defaults={
                        "family": family,
                        "skill_type": Material.SKILL_LESSON,
                        "student_intro": (
                            f"Ten words that describe {week['person']}, "
                            f"{week['role'].lower()}."
                        ),
                        "student_content": "\n".join(body),
                        "parent_content": (
                            f"Read *{week['book']}* aloud (twice is the publisher's "
                            f"advice — the second listen is when the traits land). "
                            f"The ten words are all about {week['person']}, so the "
                            f"story has to come first or the sentences are guesswork."
                        ),
                        "status": Material.APPROVED,
                    },
                )

            # --- 2. Finish the sentences -------------------------------------
            title = f"Week {week['number']} · {week['person']} — finish the sentences"
            if not options["dry_run"]:
                qset, _ = QuestionSet.objects.update_or_create(
                    lesson=lesson, title=title,
                    defaults={
                        "family": family,
                        "intro": (
                            f"**Choose the best word to finish each sentence about "
                            f"{week['person']}.**\n\n"
                            f"Your ten words this week: *{word_bank(week)}*\n\n"
                            "More than one word might sound right. Pick the one that "
                            "matches what the story showed about this person."
                        ),
                        "rubric": RUBRIC,
                        "status": QuestionSet.APPROVED,
                    },
                )
                for order, (text, _answer) in enumerate(week["sentences"], start=1):
                    Question.objects.update_or_create(
                        question_set=qset, order=order,
                        defaults={
                            "category": "grammar",
                            "response_type": Question.TYPE_CLOZE,
                            "passage": text,
                            "prompt": "",
                        },
                    )
                    questions += 1
                self._prune(qset, len(week["sentences"]))
                sets += 1

            # --- 3. What amazed you? (handwritten) ---------------------------
            title = f"Week {week['number']} · {week['person']} — what amazed you?"
            if not options["dry_run"]:
                qset, _ = QuestionSet.objects.update_or_create(
                    lesson=lesson, title=title,
                    defaults={
                        "family": family,
                        "intro": (
                            f"**What are three things that amaze you about "
                            f"{week['person']}?**\n\n"
                            "Write each one by hand, in a whole sentence. Use your "
                            "finger or your pen."
                        ),
                        "rubric": RUBRIC,
                        "status": QuestionSet.APPROVED,
                    },
                )
                for order in (1, 2, 3):
                    Question.objects.update_or_create(
                        question_set=qset, order=order,
                        defaults={
                            "category": "writing",
                            "response_type": Question.TYPE_HANDWRITING,
                            "prompt": f"Amazing thing #{order}",
                            "passage": "",
                        },
                    )
                    questions += 1
                self._prune(qset, 3)
                sets += 1

            self.stdout.write(
                f"  Week {week['number']:>2}: {week['person']} — "
                f"{len(week['sentences'])} sentences + 3 handwritten"
            )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — nothing written."))
            return

        first = Lesson.objects.filter(chapter=chapter).order_by("order").first()
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first},
        )
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {sets} question sets, {questions} questions. "
            f"{child.first_name} {'placed at week 1' if made else 'kept at existing progress'}."
        ))

    @staticmethod
    def _prune(qset, keep_through):
        """Drop questions past the end that nobody has answered.

        Answers are keyed by question pk, so deleting an answered question would
        strand her work with nothing to render it against.
        """
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()
