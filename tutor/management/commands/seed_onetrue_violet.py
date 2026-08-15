"""Seed Violet's One True Sentence: Tools of Style (idempotent).

The book gives each week a lesson page and a practice page, so each week here is
one Lesson with two QuestionSets:

    Lesson    copy the model sentence, then notice how it works
    Practice  "Now you try!" — her own sentences using this week's tool

The explanations, the model sentences and their citations are NOT stored on the
questions. They are rendered from tutor.onetrue at request time, so fixing a
sentence never means re-seeding.

    python manage.py seed_onetrue_violet --for-user ronald
    python manage.py seed_onetrue_violet --for-user ronald --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet
from tutor.onetrue import CURRICULUM_NAME, WEEKS

# WHICH PORTIONS SHE WRITES BY HAND.
#
# "Copy Sentence 1" is copywork — the whole reason the book puts a Caldecott
# sentence in front of her is that she should write it out slowly enough to
# notice how it is built. Typed, that is transcription practice at a keyboard.
#
# Her own sentences are handwritten too. She is nine and a slow typist; five
# sentences hunted out on a keyboard is an endurance test that has nothing to do
# with sentence craft, and the book gives her ruled lines for exactly this.
#
# The noticing questions in between are typed. They are short — often a word or
# a phrase — and typing them means the grader can actually read them and give
# her feedback on whether she spotted the device.
#
# Flipping any portion is a one-line change here; nothing else keys on it.
WRITTEN_BY_HAND = {
    "copy_sentence": True,
    "notice": False,
    "own_sentences": True,
}


def _type(portion):
    return (Question.TYPE_HANDWRITING if WRITTEN_BY_HAND[portion]
            else Question.TYPE_TEXT)


RUBRIC = """## One True Sentence — how this is checked

- **The copying** is checked for accuracy and care: the sentence exactly as its
  author wrote it, punctuation and capitals included.
- **The noticing questions** are about whether she can find this week's tool at
  work in someone else's sentence, and say what it is doing there.
- **Her own sentences** each have to actually use the week's tool — not merely
  contain a word that could belong to it. A sentence that would read the same
  with the tool removed has not used it.

Grade-3 mastery: Beginning → Developing → Proficient → Mastered.
"""

LESSON_SET = "Week %d · %s"
PRACTICE_SET = "Week %d · %s — now you try!"


class Command(BaseCommand):
    help = "Seed One True Sentence: Tools of Style (20 weeks, lesson + practice)."

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

        if options["dry_run"]:
            # Before any writes — a dry run that creates the curriculum and 20
            # lessons and then says "nothing written" is worse than no dry run.
            for week in WEEKS:
                self.stdout.write("  Week %2d: %-24s (%s)" % (
                    week["number"], week["topic"],
                    week["sentence_one"]["citation"]))
            self.stdout.write(self.style.WARNING(
                "Dry run — nothing written. Would seed %d weeks, %d sets."
                % (len(WEEKS), len(WEEKS) * 2)))
            return

        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=CURRICULUM_NAME,
            defaults={"subject": "Language Arts", "grade_level": "G03",
                      "family": family},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk}")

        chapter, _ = Chapter.objects.get_or_create(
            curriculum=curriculum, number=1,
            defaults={"title": "Tools of Style"},
        )

        sets = questions = 0
        for week in WEEKS:
            lesson, _ = Lesson.objects.update_or_create(
                chapter=chapter, order=week["number"],
                defaults={
                    "number": week["number"],
                    "title": "Week %d · %s" % (week["number"], week["topic"]),
                    "objectives": (
                        "%s. Copy the model sentence from %s by hand, find the "
                        "tool at work in it, then craft your own."
                        % (week["topic"], week["sentence_one"]["citation"])
                    ),
                },
            )
            for kind in ("lesson", "practice"):
                qset = self._set(lesson, family, week, kind)
                questions += self._fill(qset, week, kind)
                sets += 1
            self.stdout.write("  Week %2d: %-24s (%s)" % (
                week["number"], week["topic"],
                week["sentence_one"]["citation"]))

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
                # The explanation and the sentences are rendered from
                # tutor.onetrue at request time — see portal_questions.
                "intro": "",
                "rubric": RUBRIC,
                "status": QuestionSet.APPROVED,
            },
        )
        return qset

    def _fill(self, qset, week, kind):
        order = 0
        if kind == "lesson":
            order += 1
            Question.objects.update_or_create(
                question_set=qset, order=order,
                defaults={
                    "category": "writing",
                    "response_type": _type("copy_sentence"),
                    "prompt": week["copy_instruction"],
                    "passage": "",
                },
            )
            for prompt in week["questions_two"] + week["questions_one"]:
                order += 1
                Question.objects.update_or_create(
                    question_set=qset, order=order,
                    defaults={
                        "category": "grammar",
                        "response_type": _type("notice"),
                        "prompt": prompt,
                        "passage": "",
                    },
                )
        else:
            for group in week["practice"]:
                pair = group.get("paired")
                for n in range(1, group["count"] + 1):
                    for label in (pair or (None,)):
                        order += 1
                        prompt = "%s — %d" % (group["instruction"], n)
                        if label:
                            prompt = "%s — %d (%s)" % (
                                group["instruction"], n, label)
                        Question.objects.update_or_create(
                            question_set=qset, order=order,
                            defaults={
                                "category": "writing",
                                "response_type": _type("own_sentences"),
                                "prompt": prompt,
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
