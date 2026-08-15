"""Seed Kaylin's Operation Lexicon: Emily Dickinson (idempotent).

The book runs each week over THREE DAYS, and so does this:

    Day 1   two words   copy the word + definition, copy Dickinson, write your own
    Day 2   two words   the same three steps
    Day 3   the week's most interesting word and why, then a micro-story

One Lesson per week, three QuestionSets inside it — the week stays the unit of
progress, the way the guide numbers itself.

The words, definitions and quotations are NOT stored on the questions. They are
rendered from tutor.dickinson at request time, so correcting a definition never
means re-seeding.

    python manage.py seed_lexicon_kaylin --for-user ronald
    python manage.py seed_lexicon_kaylin --for-user ronald --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.dickinson import CURRICULUM_NAME, WEEKS, words_for_day
from tutor.models import Question, QuestionSet, ResponseSheet

# WHICH PORTIONS SHE WRITES BY HAND.
#
# The copying is the whole point of this guide — it lists handwriting practice
# and "contemplative attention to detail" among the skills it teaches, and a
# copied line typed at a keyboard practises neither. So both copy steps take the
# pen, and so does the sentence she composes for each word: in the book it sits
# in the same block, on the same page, and it is one sentence.
#
# Day 3 is typed. It is a 150-word micro-story that wants revising — moving
# words around, cutting, trying a different opening — and that is real work by
# hand and easy at a keyboard. The point there is the writing, not the letters.
#
# Flipping any portion is a one-line change here; nothing else keys on it.
WRITTEN_BY_HAND = {
    "copy_definition": True,
    "copy_example": True,
    "own_sentence": True,
    "favorite_word": False,
    "micro_story": False,
}


def _type(portion):
    return (Question.TYPE_HANDWRITING if WRITTEN_BY_HAND[portion]
            else Question.TYPE_TEXT)


RUBRIC = """## Operation Lexicon — how this is checked

- **The copying** is checked for accuracy and care: every word, every dash, every
  capital exactly as Dickinson wrote it. Her punctuation is not decoration — the
  em dashes are the poem breathing.
- **Your own sentence** uses the word the way it actually means, in a sentence
  that could only be about this word. A sentence that would work with any word
  in its place hasn't used it.
- **The micro-story** carries as many of the week's words as it can hold without
  straining, and still reads as a story.

Grade-7 mastery: Beginning → Developing → Proficient → Mastered.
"""

DAY3_FAVORITE = ("Which word did you find most interesting this week, and why "
                 "did you choose it?")
DAY3_STORY = ("Now use as many of this week's words as you can in an imaginative "
              "micro-story of about 150 words. Use one of the story-starters, or "
              "an idea of your own.")


def lesson_title(week):
    return "Week %d · %s" % (week["number"], ", ".join(
        w["word"] for w in week["words"]))


def set_title(week, day):
    return "Week %d · Day %d" % (week["number"], day)


class Command(BaseCommand):
    help = "Seed Operation Lexicon: Emily Dickinson (23 weeks, 3 days each)."

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
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=CURRICULUM_NAME,
            defaults={"subject": "Language Arts", "grade_level": "G07",
                      "family": family},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk}")

        chapter, _ = Chapter.objects.get_or_create(
            curriculum=curriculum, number=1,
            defaults={"title": "An ABCeDarian"},
        )

        sets = questions = 0
        for week in WEEKS:
            lesson, _ = Lesson.objects.update_or_create(
                chapter=chapter, order=week["number"],
                defaults={
                    "number": week["number"],
                    "title": lesson_title(week),
                    "objectives": (
                        "Four words from Dickinson's lexicon: %s. Copy each word, "
                        "its definition and her lines by hand; craft a sentence of "
                        "your own for each; then write the week's micro-story."
                        % ", ".join(w["word"] for w in week["words"])
                    ),
                },
            )
            if options["dry_run"]:
                self.stdout.write(
                    "  Week %2d: %s — would build 3 days, 14 questions"
                    % (week["number"], week["letter"]))
                continue

            for day in (1, 2, 3):
                qset = self._day_set(lesson, family, week, day)
                questions += self._fill(qset, week, day)
                sets += 1

            self.stdout.write(
                "  Week %2d: %-6s %s"
                % (week["number"], week["letter"],
                   ", ".join(w["word"] for w in week["words"])))

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — nothing written."))
            return

        first = Lesson.objects.filter(chapter=chapter).order_by("order").first()
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first},
        )
        self.stdout.write(self.style.SUCCESS(
            "Seeded %d days across %d weeks, %d questions. %s %s."
            % (sets, len(WEEKS), questions, child.first_name,
               "placed at week 1" if made else "kept at existing progress")
        ))

    def _day_set(self, lesson, family, week, day):
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson, title=set_title(week, day),
            defaults={
                "family": family,
                # The words, definitions and quotations are rendered from
                # tutor.dickinson at request time — see portal_questions.
                "intro": "",
                "rubric": RUBRIC,
                "status": QuestionSet.APPROVED,
            },
        )
        return qset

    def _fill(self, qset, week, day):
        """Build one day's questions. Order is the book's order."""
        order = 0
        if day in (1, 2):
            for entry in words_for_day(week, day):
                word = entry["word"]
                lines = "lines" if entry["example_kind"] == "poem" else "sentence"
                for portion, prompt in (
                    ("copy_definition",
                     "%s — copy the word and the definition." % word),
                    ("copy_example",
                     "%s — copy the %s from Dickinson." % (word, lines)),
                    ("own_sentence",
                     "%s — craft a sentence of your own." % word),
                ):
                    order += 1
                    Question.objects.update_or_create(
                        question_set=qset, order=order,
                        defaults={
                            "category": "writing",
                            "response_type": _type(portion),
                            "prompt": prompt,
                            "passage": "",
                        },
                    )
        else:
            for portion, prompt in (("favorite_word", DAY3_FAVORITE),
                                    ("micro_story", DAY3_STORY)):
                order += 1
                Question.objects.update_or_create(
                    question_set=qset, order=order,
                    defaults={
                        "category": "writing",
                        "response_type": _type(portion),
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
