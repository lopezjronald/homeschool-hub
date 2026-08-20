"""Seed Kaylin's Poetry: Small Forms (idempotent).

Twelve sections, one small form each. Every section runs the guide's own
method — the same four steps it repeats form after form:

    1. Craft a detailed sentence (or sentences) and count the syllables
    2. Edit it toward the form's count — underline what's strong, cut, swap
    3. Rewrite it with the poetic slash marking the line breaks
    4. Title it, and write out the final poem with proper line breaks

Step 4 is the LINE # / SYLLABLES grid: the portal renders one input per line of
the form, labelled with its target count, with a live syllable check as she
types. The answer is stored as plain lines of text (title first), so the
grader, the work browser and the printed report need nothing new to read it.

The ORIGINAL guide pages for each section are attached to her page from
static/poetry/<slug>/ — the worked examples are in the author's own
handwriting, and she should see the real thing.

    python manage.py seed_poetry_kaylin --for-user ronald
    python manage.py seed_poetry_kaylin --for-user ronald --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet
from tutor.poetry import CURRICULUM_NAME, SECTIONS, total_syllables

RUBRIC = """## Poetry: Small Forms — how this is checked

- **The form is the assignment.** Count the syllables line by line against the
  pattern. Close counts on the way through are fine; the final poem should fit.
- **The steps show the work**: a real starting sentence, a visible edit, the
  slash marking her line-break decisions. A final poem with no path to it means
  the method was skipped.
- **Image over rhyme.** The guide is explicit: never sacrifice an idea to force
  a rhyme.

Grade-7 mastery: Beginning → Developing → Proficient → Mastered.
"""


def _steps(section):
    """The guide's four steps, worded for this form."""
    name = section["name"]
    total = total_syllables(section)
    pattern = section["pattern"]
    lines = len(pattern)

    if section["slug"] == "sevenling":
        # The guide's own method for this form is NOT one-idea-per-line: craft
        # two sentences, edit each into a list of three, then land the twist.
        return [
            ("application",
             "Craft two detailed sentences about one subject — each sentence "
             "holding three things (a list of three).",
             "Two sentences, three things in each. The guide's example uses an "
             "animal — anything with three-part detail works."),
            ("application",
             "Rewrite your sentences. Underline what's strong; tighten each "
             "list until its three things stand out cleanly.",
             "Each stanza will be one list of three. Cut anything that isn't "
             "one of the three."),
            ("application",
             "Use the poetic slash to break each sentence into its three "
             "lines — then write one more line: the twist.",
             "The twist is line 7: an unexpected reveal that changes how the "
             "six lines read."),
            ("application",
             "Create a title and write out the final poem with the proper "
             "line breaks.",
             "Three lines, three lines, then the twist on its own."),
        ]
    if section.get("free_shape"):
        step1 = ("Craft two or three detailed sentences that describe snapshots "
                 "of one moment — images the reader can see and hear.")
        step2 = ("Rewrite your sentences. Underline the strong images and active "
                 "verbs; strike out anything that isn't pulling weight.")
        step3 = ("Use the poetic slash to break your sentences into short lines "
                 "wherever an image should stand on its own.")
    elif total is None:
        step1 = ("Craft %d simple sentences — each one a single complete idea "
                 "about one subject." % lines)
        step2 = ("Rewrite your sentences. Underline what's strong, strike out "
                 "what's unnecessary, and tighten each idea to one clean line.")
        step3 = ("Put your lines in order and use the poetic slash to mark where "
                 "each one ends.")
    else:
        step1 = ("Craft a detailed sentence describing a snapshot of a moment"
                 "%s, and count the syllables."
                 % (" in nature" if section["slug"] in ("haiku", "lune") else ""))
        about = "about %d" % total if section.get("approximate") else "%d" % total
        step2 = ("Rewrite your sentence. Underline strong images and active "
                 "verbs. Edit to increase or reduce the number of syllables to "
                 "%s — strike out words that are unnecessary, substitute words, "
                 "play with word forms, change tense." % about)
        step3 = ("Rewrite your edited sentence and use the poetic slash to add "
                 "line breaks according to %s form." % name)
    step4 = ("Create a title and write out the final poem with the proper line "
             "breaks.")
    return [
        ("application", step1,
         "Start with something real that you actually saw or felt — detail "
         "first, form later."),
        ("application", step2,
         "Say it out loud and count on your fingers. Every cut should make the "
         "picture sharper."),
        ("application", step3,
         "The slash / marks where a line will end. Break where the image turns."),
        ("application", step4,
         "One line per box. The counter is a check — your own count wins, so "
         "clap it out if they disagree."),
    ]


class Command(BaseCommand):
    help = "Seed Poetry: Small Forms (12 sections, one form each)."

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
            for s in SECTIONS:
                total = total_syllables(s)
                self.stdout.write("  Section %2d: %-11s %s" % (
                    s["number"], s["name"],
                    "%d syllables" % total if total else "no syllable rule"))
            self.stdout.write(self.style.WARNING("Dry run — nothing written."))
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
            defaults={"title": "A Journey Through the Small Forms of Poetry"},
        )

        sets = questions = 0
        for section in SECTIONS:
            n = section["number"]
            lesson, _ = Lesson.objects.update_or_create(
                chapter=chapter, order=n,
                defaults={
                    "number": n,
                    "title": "Section %d · %s" % (n, section["name"]),
                    "objectives": (
                        "%s — %s. Read the guide's pages, then craft one of "
                        "your own by the four steps."
                        % (section["name"], section["subtitle"])
                    ),
                },
            )
            qset, _ = QuestionSet.objects.update_or_create(
                lesson=lesson, title="Section %d · %s" % (n, section["name"]),
                defaults={
                    "family": family,
                    # Definition, pattern and the original pages are rendered
                    # from tutor.poetry at request time — see portal_questions.
                    "intro": "",
                    "rubric": RUBRIC,
                    "status": QuestionSet.APPROVED,
                    "mode": QuestionSet.MODE_STUDENT,
                    "reading": "the guide's %s pages (attached below)"
                               % section["name"],
                },
            )
            order = 0
            for category, prompt, hint in _steps(section):
                order += 1
                Question.objects.update_or_create(
                    question_set=qset, order=order,
                    defaults={
                        "category": category,
                        "response_type": Question.TYPE_TEXT,
                        "prompt": prompt,
                        "hint": hint,
                        "passage": "",
                    },
                )
                questions += 1
            self._prune(qset, order)
            sets += 1
            self.stdout.write("  Section %2d: %s" % (n, section["name"]))

        first = Lesson.objects.filter(chapter=chapter).order_by("order").first()
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first},
        )
        self.stdout.write(self.style.SUCCESS(
            "Seeded %d sections, %d questions. %s %s."
            % (sets, questions, child.first_name,
               "placed at section 1" if made else "kept at existing progress")
        ))

    @staticmethod
    def _prune(qset, keep_through):
        """Drop questions past the end that nobody has answered."""
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()
