"""Seed Violet's Blackbird & Company "Rickshaw Girl" course (idempotent).

Digitises the family's purchased Level 3 Literature Discovery Guide for private
use, in the guide's own five-part shape and its own exercise formats:

    Section N · Journal        characters (a box each) · setting · plot
    Section N · Vocabulary     match the definitions, then fill the blanks
    Section N · Comprehension  seven questions, complete sentences
    Section N · Writing        rough draft (three-part paragraph) → final draft
    Section N · Discussion     teacher-led, no writing
    Section 5 · Final Project  choose one or more of the guide's options

Every exercise type here already existed in the app — characters, matching,
fill-blank, and the three-part paragraph are exactly what the Level 3 pages ask
for — so the portal keeps the guide's format rather than flattening it into text
boxes.

    python manage.py seed_rickshaw_girl --for-user ronald
    python manage.py seed_rickshaw_girl --for-user ronald --dry-run
"""

import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet
from tutor.rickshaw import (
    BOOK, CURRICULUM_NAME, FINAL_PROJECT_INTRO, FINAL_PROJECT_OPTIONS,
    HOW_IT_RUNS, JOURNAL_NOTE, SECTIONS,
)

# WHICH PORTIONS SHE WRITES BY HAND.
#
# The guide asks for the final draft in her own hand — "recopy your final
# version here using your best penmanship" — so that one takes the pen. The
# rough draft is typed because it is meant to be revised, and everything else is
# typed so the grader can read it and give her feedback.
WRITTEN_BY_HAND = {
    "journal": False,
    "rough_draft": False,
    "final_draft": True,
}


def _type(portion, default=Question.TYPE_TEXT):
    return Question.TYPE_HANDWRITING if WRITTEN_BY_HAND[portion] else default


MASTERY_NOTE = (
    "\n\n> **Mastery mapping:** Accomplished → Mastered · Proficient → Proficient "
    "· Basic → Developing · Limited/Poor → Beginning."
)

JOURNAL_RUBRIC = """## Blackbird grading — Journal

Notes are **bullet-point phrases**, not essays.

- **Characters** describe who a character IS — appearance, personality,
  background, strengths, weaknesses — not what he does. What a character does is
  plot information.
- **Setting** names the broad, general aspects: historical time period and
  geographic location, plus details like the room, the weather, the season, the
  time of day.
- **Plot** gives simple reminders of the major events. Do not retell the story.""" + MASTERY_NOTE

VOCAB_RUBRIC = """## Blackbird grading — Acquire (vocabulary)

- Each word matched to the **right** definition.
- Each blank filled with the word that actually fits the sentence — including
  changing its ending where the sentence needs it.""" + MASTERY_NOTE

COMPREHENSION_RUBRIC = """## Blackbird grading — Recollect

- Every question answered in **complete sentences**.
- Answers are **accurate to the book**. She may refer to both the book and her
  journal notes.""" + MASTERY_NOTE

WRITING_RUBRIC = """## Blackbird grading — Explore: Writing

A complete paragraph with a **topic sentence**, several **supporting sentences**,
and a **concluding sentence**.

- **Accomplished:** creatively focuses on the topic, logical progression of
  ideas, varied sentence structure, interesting transitions and strong word
  choice.
- **Proficient:** focuses on the topic with adequate support; transitions and
  word choice adequate but not creative.
- **Basic:** topic addressed but unclear; support weak; sentences stagnant.

Judge the writing from the typed final draft — that is the version the
grader can read. The handwritten recopy is penmanship: judge the letters,
not the content, and only a person can do that.""" + MASTERY_NOTE

DISCUSSION_RUBRIC = """## Blackbird — Explore: Discussion

Springboard questions with no single right answer. Lead them aloud; press for
reasons and for examples from the book. Nothing to submit."""

JOURNAL_INTRO = (
    "As you read, jot bullet-point notes about WHO each person is — what they "
    "look like, how they act, think and feel — not just what they do (that goes "
    "under Plot). Then where it happens, then the big events."
)


class Command(BaseCommand):
    help = "Seed Rickshaw Girl (Blackbird Level 3): 4 sections + a final project."

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
            # Before any writes.
            for s in SECTIONS:
                self.stdout.write(
                    "  Section %d: %-26s %d vocab · %d comprehension · %d discussion"
                    % (s["number"], s["chapters"], len(s["vocab"]),
                       len(s["comprehension"]), len(s["discussion"])))
            self.stdout.write("  Section 5: Final Project       %d options"
                              % len(FINAL_PROJECT_OPTIONS))
            self.stdout.write(self.style.WARNING("Dry run — nothing written."))
            return

        # The blueprint is what A Mouse Called Wolf uses — same publisher, same
        # level, same child — so the two courses get an identical Read → Journal
        # → Acquire → Recollect → Explore skeleton instead of two shapes that
        # only look alike. It also puts this course inside audit_content's
        # lesson-plan drift check, which is keyed on having a blueprint at all.
        blueprint = get_blueprint("blackbird_rickshaw_girl")
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=blueprint["name"],
            defaults={"subject": blueprint["subject"],
                      "grade_level": blueprint["grade_level"],
                      "family": family},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk}")
        apply_blueprint(curriculum, blueprint)

        sets = questions = 0
        for section in SECTIONS:
            n = section["number"]
            # Blueprint lesson order: 1 Read · 2 Journal · 3 Acquire ·
            # 4 Recollect · 5 Explore — the sibling's numbering exactly.
            for order, build in ((2, self._journal), (3, self._vocabulary),
                                 (4, self._comprehension), (5, self._writing),
                                 (5, self._discussion)):
                lesson = self._lesson(curriculum, n, order)
                s, q = build(lesson, family, section)
                sets += s
                questions += q
            self.stdout.write("  Section %d: %s" % (n, section["chapters"]))

        s, q = self._final_project(curriculum, family)
        sets += s
        questions += q
        self.stdout.write("  Section 5: Final Project")

        first = self._lesson(curriculum, 1, 1)
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first},
        )
        self.stdout.write(self.style.SUCCESS(
            "Seeded %d sets, %d questions across %d sections + the final project. "
            "%s %s." % (sets, questions, len(SECTIONS), child.first_name,
                        "placed at section 1" if made else
                        "kept at existing progress")
        ))

    # -- builders ----------------------------------------------------------

    def _set(self, lesson, family, title, *, intro, rubric, questions,
             mode=None, reading=""):
        # Written unconditionally. Omitting them when they are empty meant the
        # Final Project set — the only one that passes neither — could keep a
        # tampered mode forever, and a set stuck in discussion mode is invisible
        # to her and cannot be restored by re-seeding.
        defaults = {
            "family": family,
            "intro": intro,
            "rubric": rubric,
            "status": QuestionSet.APPROVED,
            "reading": reading,
            "mode": mode or QuestionSet.MODE_STUDENT,
        }
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson, title=title, defaults=defaults)
        for order, (category, prompt, hint, extra) in enumerate(questions, start=1):
            fields = {"category": category, "prompt": prompt, "hint": hint,
                      "response_type": Question.TYPE_TEXT, "passage": ""}
            fields.update(extra or {})
            Question.objects.update_or_create(
                question_set=qset, order=order, defaults=fields)
        self._prune(qset, len(questions))
        return 1, len(questions)

    def _journal(self, lesson, family, section):
        return self._set(
            lesson, family, "Section %d · Journal" % section["number"],
            reading=section["chapters"],
            intro=JOURNAL_INTRO,
            rubric=JOURNAL_RUBRIC,
            questions=[
                ("character",
                 "CHARACTERS — note interesting and important things you learn "
                 "about each person below: their personality and appearance, and "
                 "details about the way they act, think, and feel.",
                 "Bullet points are perfect! Describe who each person IS — not "
                 "what they do. What they do goes under Plot.",
                 {"response_type": _type("journal", Question.TYPE_CHARACTERS),
                  "passage": "\n".join(section["characters"])}),
                ("setting",
                 "SETTING — note where the story is happening. Explain how the "
                 "setting is significant to the story and include any descriptive "
                 "details you find.",
                 "Country, time of year, weather, time of day — and why the place "
                 "matters to what happens.",
                 {"response_type": _type("journal")}),
                ("plot",
                 "PLOT — summarize what happens in this section of the story.",
                 "Just the big events, in order. Don't retell the whole thing.",
                 {"response_type": _type("journal")}),
            ],
        )

    def _vocabulary(self, lesson, family, section):
        words = [w for w, _ in section["vocab"]]
        by_number = {n: w for w, n in section["vocab"]}
        matching = {
            "words": words,
            "definitions": [
                {"n": i + 1, "text": text, "word": by_number[i + 1]}
                for i, text in enumerate(section["definitions"])
            ],
        }
        # The fill-in bank offers what actually fits the blanks, which is NOT
        # always the printed word list: two of section 4's sentences want
        # "scolded" and "labored" where the list prints "scold" and "labor".
        # The dropdown is built from this bank, so keying a blank to a word the
        # bank doesn't carry makes that row impossible — she would pick the only
        # sensible option, be told she is wrong, and never be able to finish.
        # The MATCHING exercise above keeps the printed list; only this one bends.
        answers = [word for _sentence, word in section["blanks"]]
        bank = sorted(set(answers), key=lambda w: (
            # keep the printed order where the answer is just an inflection
            next((i for i, p in enumerate(words) if w.startswith(p)), len(words)), w))
        fill = {
            "words": bank,
            # The widget's blank marker is six underscores; content stores three.
            "sentences": [
                {"text": sentence.replace("___", "______"), "word": word}
                for sentence, word in section["blanks"]
            ],
        }
        missing = [w for w in answers if w not in bank]
        if missing:
            raise CommandError(
                "Section %d: fill-blank answers %r are not in the bank %r — "
                "those rows could never be answered."
                % (section["number"], missing, bank))
        return self._set(
            lesson, family, "Section %d · Vocabulary" % section["number"],
            reading=section["chapters"],
            intro="Vocabulary builds your reading power. Match every word to its "
                  "meaning first — then use those same words to fill in the "
                  "blanks. Use a dictionary if you need help; the paper kind is "
                  "best.",
            rubric=VOCAB_RUBRIC,
            questions=[
                ("vocabulary",
                 "Match each word to the meaning that fits it.",
                 "Tap a word, then tap its meaning. Start with the ones you are "
                 "sure of — that leaves fewer to puzzle over.",
                 {"response_type": Question.TYPE_MATCHING,
                  "passage": json.dumps(matching)}),
                ("vocabulary",
                 "Now use those words to fill in the blanks."
                 + (" Two of these need the word's ending changed — those forms "
                    "are in the list for you." if bank != words else ""),
                 "Read the whole sentence out loud with your word in it. If it "
                 "sounds wrong, try another.",
                 {"response_type": Question.TYPE_FILL_BLANK,
                  "passage": json.dumps(fill)}),
            ],
        )

    def _comprehension(self, lesson, family, section):
        return self._set(
            lesson, family, "Section %d · Comprehension" % section["number"],
            reading=section["chapters"],
            intro="Answer using complete sentences. You may refer to both the "
                  "book and your journal notes.",
            rubric=COMPREHENSION_RUBRIC,
            # No per-question nudge here: the reference course has none, and the
            # only thing one could say ("look back at the book, answer in a whole
            # sentence") is already the intro directly above. Seven identical
            # nudges teach her the 💡 is not worth tapping — which costs her on
            # the journal and vocabulary pages, where they genuinely help.
            questions=[("comprehension", prompt, "", None)
                       for prompt in section["comprehension"]],
        )

    def _writing(self, lesson, family, section):
        return self._set(
            lesson, family, "Section %d · Writing Exercise" % section["number"],
            reading=section["chapters"],
            intro="Write a complete paragraph based on the topic below. Remember "
                  "to include a topic sentence, several supporting sentences, and "
                  "a concluding sentence.",
            rubric=WRITING_RUBRIC,
            questions=[
                ("application",
                 "ROUGH DRAFT — %s" % section["writing_prompt"],
                 "Just get your thoughts down — the polish comes next. One box "
                 "at a time.",
                 {"response_type": _type("rough_draft", Question.TYPE_PARAGRAPH),
                  "passage": json.dumps({"sections": [
                      "Introduction / Topic Sentence",
                      "Supporting Sentences",
                      "Concluding Sentence"]})}),
                # The paragraph widget above already ends in a typed final
                # draft, and that typed version is what gets graded — the AI is
                # told it cannot read handwriting. So this is named for what it
                # actually is: the guide's penmanship recopy, not a second
                # place to compose.
                ("application",
                 "BEST HANDWRITING — now recopy your finished paragraph here by "
                 "hand, using your best penmanship. Copy it exactly as you "
                 "polished it above; this one is for the writing itself.",
                 "Take your time and form each letter carefully. There is room "
                 "to keep going — the paper grows as you write.",
                 {"response_type": _type("final_draft")}),
            ],
        )

    def _discussion(self, lesson, family, section):
        return self._set(
            lesson, family, "Section %d · Discussion" % section["number"],
            reading=section["chapters"],
            intro="Think about and discuss these together — nothing to write. "
                  "Press for reasons and for examples from the book.",
            rubric=DISCUSSION_RUBRIC,
            questions=[("discussion", prompt, "", None)
                       for prompt in section["discussion"]],
            mode=QuestionSet.MODE_DISCUSSION,
        )

    @staticmethod
    def _lesson(curriculum, chapter_number, order):
        return Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=chapter_number,
            order=order)

    def _final_project(self, curriculum, family):
        lesson = self._lesson(curriculum, 5, 1)
        # Scaffolded the way the sibling course does it: she picks, she plans,
        # she reflects — three short questions with a nudge on each. The earlier
        # version asked "which option did you choose?" BEFORE showing her the
        # options, in one 233-word prompt of scheduling admin.
        options = "\n".join(
            "%d. **%s** — %s" % (i, name, text)
            for i, (name, text) in enumerate(FINAL_PROJECT_OPTIONS, start=1))
        return self._set(
            lesson, family, "Section 5 · Glean: Final Project",
            intro="You finished the book — now GLEAN! Pick a project below and "
                  "make something. This one is yours: take your time and enjoy "
                  "it.\n\n" + options,
            rubric="## Blackbird — Glean\n\nA final project: research, writing "
                   "and hands-on work drawing on different aspects of the story. "
                   "Judge the care and the thinking, not the neatness of the "
                   "craft." + MASTERY_NOTE,
            questions=[
                ("application",
                 "Which project did you choose, and why that one?",
                 "There is no wrong pick — choose the one you actually want to "
                 "make.",
                 None),
                ("application",
                 "What is your plan? What will you need, and what is your first "
                 "step?",
                 "Think about materials, and where you will do it. A plan makes "
                 "starting easier.",
                 None),
                ("application",
                 "When it is finished — what did you make, and what surprised you?",
                 "Come back and fill this in after you finish. Tell me the part "
                 "you are proudest of.",
                 None),
            ],
        )

    @staticmethod
    def _prune(qset, keep_through):
        """Drop questions past the end that nobody has answered."""
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()
