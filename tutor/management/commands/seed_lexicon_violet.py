"""Seed Violet's Operation Lexicon: Traits of Character (idempotent).

ONE PAGE PER WEEK, the way the printed guide lays it out: the ten words and
what they mean at the top, the ten sentences under them, and "what amazed you"
at the end. Splitting a week into three separate items made her navigate
between parts of a single spread, which the book never asks of her.

So each week is one QuestionSet:

    Q1-10   finish the sentence about this person (cloze)
    Q11-13  three things that amazed you (handwritten)

The word list is not stored on the page — it is rendered from tutor.lexicon at
request time, so fixing a definition doesn't mean re-seeding.

    python manage.py seed_lexicon_violet --for-user ronald
    python manage.py seed_lexicon_violet --for-user ronald --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.lexicon import CURRICULUM_NAME, WEEKS
from tutor.models import Material, Question, QuestionSet, ResponseSheet

RUBRIC = """## Operation Lexicon — how this is checked

- **Finish the sentences:** the word chosen actually fits the person and the
  sentence. Several words could be grammatically fine; only one matches what
  the story showed about them.
- **What amazed you:** written by hand, in complete sentences, about *this*
  person — not a general comment. Spelling counts less than having a real
  thought and writing it legibly.

Grade-3 mastery: Beginning → Developing → Proficient → Mastered.
"""

HANDWRITING_PROMPTS = [
    "Amazing thing #1",
    "Amazing thing #2",
    "Amazing thing #3",
]


def set_title(week):
    return f"Week {week['number']} · {week['person']} — {week['role']}"


class Command(BaseCommand):
    help = "Seed Operation Lexicon: Traits of Character (one page per week)."

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
            if options["dry_run"]:
                self.stdout.write(
                    f"  Week {week['number']:>2}: {week['person']} — would build "
                    f"one page of {len(week['sentences']) + 3} questions")
                continue

            qset, _ = QuestionSet.objects.update_or_create(
                lesson=lesson, title=set_title(week),
                defaults={
                    "family": family,
                    # The word list, the book and the instructions are rendered
                    # from tutor.lexicon at request time — see portal_questions.
                    "intro": "",
                    "rubric": RUBRIC,
                    "status": QuestionSet.APPROVED,
                },
            )

            order = 0
            for text, _answer in week["sentences"]:
                order += 1
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
            for prompt in HANDWRITING_PROMPTS:
                order += 1
                Question.objects.update_or_create(
                    question_set=qset, order=order,
                    defaults={
                        "category": "writing",
                        "response_type": Question.TYPE_HANDWRITING,
                        "prompt": prompt,
                        "passage": "",
                    },
                )
                questions += 1
            self._prune(qset, order)
            sets += 1

            # The first cut split each week across a Material and two sets.
            # Sweep those away so she isn't left with three stale half-pages
            # beside the real one — but never take work she has done with them.
            self._retire_superseded(lesson, keep_title=set_title(week))

            self.stdout.write(
                f"  Week {week['number']:>2}: {week['person']} — one page, "
                f"{order} questions")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — nothing written."))
            return

        first = Lesson.objects.filter(chapter=chapter).order_by("order").first()
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first},
        )
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {sets} weekly pages, {questions} questions. "
            f"{child.first_name} "
            f"{'placed at week 1' if made else 'kept at existing progress'}."
        ))

    def _retire_superseded(self, lesson, keep_title):
        """Remove the earlier three-part shape for this week.

        Scoped to shared (not child-pinned) sets on THIS lesson, and it stops at
        anything a child has invested in — a submitted sheet is what lesson
        completion counts, so deleting one would roll her progress backwards.
        """
        for old in QuestionSet.objects.filter(
            lesson=lesson, mode=QuestionSet.MODE_STUDENT, child__isnull=True,
        ).exclude(title=keep_title):
            if self._has_work(old):
                self.stdout.write(self.style.WARNING(
                    f"    kept '{old.title}' — she has work in it"))
                continue
            old.delete()
        # The "meet the words" Material is now the page's own header.
        Material.objects.filter(
            lesson=lesson, title__startswith="Week ",
            title__endswith="meet the words",
        ).delete()

    @staticmethod
    def _has_work(qset):
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            if sheet.is_submitted or sheet.work_entry_id or sheet.draft_feedback:
                return True
            if any(str(v).strip() for v in (sheet.answers or {}).values()):
                return True
        return False

    @staticmethod
    def _prune(qset, keep_through):
        """Drop questions past the end that nobody has answered."""
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()
