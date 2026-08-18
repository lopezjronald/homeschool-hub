"""Seed Kaylin's One True Sentence, Volume C3: Tools of Style #3 (idempotent).

The publisher places this volume at Grades 6-8 ("Level 3"), so it is
Kaylin's, not Violet's — C1, which is already live, is Grades 4-5. Twenty weeks,
one rhetorical device each — Antanagoge through Asterismos — and each week is a
lesson page and a practice page, the way the book is laid out.

THE SHAPE IS NOT C1's, and that is why this has its own seed rather than a
rename of seed_onetrue_violet:

  - There is no "Sentence 2" anywhere in this volume, and so no second set of
    noticing questions. One Example box per week IS the model she copies.
  - Each lesson carries TWO copy tasks, not one: task 1 copies the device's
    EXPLANATION, task 4 copies the example sentence. Both take the pen.
  - The tasks are the guide's own numbered list, in print order, with the copy
    task restored to its printed position (it always follows "read the example
    silently", which is index 2 in every one of the twenty weeks).
  - Practice is always a single group of five.

    python manage.py seed_onetrue3_kaylin --for-user ronald
    python manage.py seed_onetrue3_kaylin --for-user ronald --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet
from tutor.onetrue3 import CURRICULUM_NAME, WEEKS

# WHICH PORTIONS SHE WRITES BY HAND.
#
# Both copy tasks: copying is why the book puts the text in front of her, and
# typed it is transcription at a keyboard rather than noticing how a sentence is
# built.
#
# Her five sentences are handwritten too, matching her Dickinson volume — the
# composing is the practice. That is the one debatable call here: typed, the AI
# grader could tell her whether a sentence REALLY uses polysyndeton rather than
# merely containing conjunctions. Flip "own_sentences" to False if that feedback
# is worth more than the handwriting.
#
# The noticing and rewriting tasks in between are typed, so the grader can read
# them and say whether she actually understood the device.
WRITTEN_BY_HAND = {
    "copy_explanation": True,
    "copy_example": True,
    "notice": False,
    "own_sentences": True,
}

# The printed task that copies the explanation always leads the list, and the
# one that copies the example always follows "read the example silently".
COPY_EXPLANATION_INDEX = 0
READ_SILENTLY_INDEX = 2


def _type(portion, default=Question.TYPE_TEXT):
    return Question.TYPE_HANDWRITING if WRITTEN_BY_HAND[portion] else default


RUBRIC = """## One True Sentence #3 — how this is checked

- **The copying** is checked for accuracy and care: the explanation and the
  example sentence exactly as printed, punctuation and capitals included.
- **The tasks** are about whether she can find this week's device at work and
  say what it is doing — and, where the task asks, rewrite the sentence without
  it and judge which reads better.
- **Her own sentences** each have to really use the device. A sentence that
  reads the same with the device removed has not used it.

Grade-7 mastery: Beginning → Developing → Proficient → Mastered.
"""

LESSON_SET = "Week %d · %s"
PRACTICE_SET = "Week %d · %s — now you try!"


class Command(BaseCommand):
    help = "Seed One True Sentence C3: Tools of Style #3 (20 weeks)."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True)
        parser.add_argument("--child-name", default="Kaylin")
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

        if options["dry_run"]:
            # Before any writes.
            for week in WEEKS:
                self.stdout.write("  Week %2d: %-16s %d tasks · %d sentences"
                                  % (week["number"], week["topic"],
                                     len(week["questions_one"]) + 1,
                                     sum(g["count"] for g in week["practice"])))
            self.stdout.write(self.style.WARNING(
                "Dry run — nothing written. Would seed %d weeks, %d sets."
                % (len(WEEKS), len(WEEKS) * 2)))
            return

        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=CURRICULUM_NAME,
            defaults={"subject": "Language Arts", "grade_level": "G07",
                      "family": family},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk}")

        chapter, _ = Chapter.objects.get_or_create(
            curriculum=curriculum, number=1,
            defaults={"title": "Tools of Style #3"},
        )

        sets = questions = 0
        for week in WEEKS:
            lesson, _ = Lesson.objects.update_or_create(
                chapter=chapter, order=week["number"],
                defaults={
                    "number": week["number"],
                    "title": "Week %d · %s" % (week["number"], week["topic"]),
                    "objectives": (
                        "%s. Copy the explanation and the example sentence by "
                        "hand, work through the guide's tasks, then craft five "
                        "sentences of your own." % week["topic"]
                    ),
                },
            )
            for kind in ("lesson", "practice"):
                qset = self._set(lesson, family, week, kind)
                questions += self._fill(qset, week, kind)
                sets += 1
            self.stdout.write("  Week %2d: %s" % (week["number"], week["topic"]))

        first = Lesson.objects.filter(chapter=chapter).order_by("order").first()
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first},
        )
        self.stdout.write(self.style.SUCCESS(
            "Seeded %d sets across %d weeks, %d questions. %s %s."
            % (sets, len(WEEKS), questions, child.first_name,
               "placed at week 1" if made else "kept at existing progress")
        ))

    @staticmethod
    def set_title(week, kind):
        fmt = LESSON_SET if kind == "lesson" else PRACTICE_SET
        return fmt % (week["number"], week["topic"])

    def _set(self, lesson, family, week, kind):
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson, title=self.set_title(week, kind),
            defaults={
                "family": family,
                # The explanation and the example are rendered from
                # tutor.onetrue3 at request time — see portal_questions.
                "intro": "",
                "rubric": RUBRIC,
                "status": QuestionSet.APPROVED,
                "reading": "",
                "mode": QuestionSet.MODE_STUDENT,
            },
        )
        return qset

    def _tasks(self, week):
        """The week's tasks in the guide's printed order.

        The transcription lifted the copy-the-example task out into
        `copy_instruction`; it belongs immediately after "read the example
        silently", which is where the book prints it.
        """
        out = []
        for i, prompt in enumerate(week["questions_one"]):
            portion = "copy_explanation" if i == COPY_EXPLANATION_INDEX else "notice"
            hint = ("Copy it exactly as it is printed — that is how you notice "
                    "how it is built."
                    if i == COPY_EXPLANATION_INDEX else
                    "Look back at the example sentence above; the answer is in "
                    "how it is put together.")
            out.append((portion, prompt, hint))
            if i == READ_SILENTLY_INDEX:
                out.append(("copy_example", week["copy_instruction"],
                            "Every word, every mark, exactly as printed."))
        return out

    def _fill(self, qset, week, kind):
        order = 0
        if kind == "lesson":
            for portion, prompt, hint in self._tasks(week):
                order += 1
                Question.objects.update_or_create(
                    question_set=qset, order=order,
                    defaults={
                        "category": "writing" if portion.startswith("copy")
                                    else "grammar",
                        "response_type": _type(portion),
                        "prompt": prompt,
                        "hint": hint,
                        "passage": "",
                    },
                )
        else:
            for group in week["practice"]:
                ask, _, rest = group["instruction"].partition("\n")
                for n in range(1, group["count"] + 1):
                    order += 1
                    head = "Sentence %d of %d" % (n, group["count"])
                    prompt = "%s — %s" % (head, ask) if n == 1 else head
                    if n == 1 and rest:
                        prompt = "%s\n%s" % (prompt, rest)
                    Question.objects.update_or_create(
                        question_set=qset, order=order,
                        defaults={
                            "category": "writing",
                            "response_type": _type("own_sentences"),
                            "prompt": prompt,
                            "hint": ("Write it by hand. Make sure the device is "
                                     "really doing something — a sentence that "
                                     "reads the same without it hasn't used it."),
                            "passage": "",
                        },
                    )
        self._prune(qset, order)
        return order

    @staticmethod
    def _prune(qset, keep_through):
        """Drop questions past the end that nobody has answered."""
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()
