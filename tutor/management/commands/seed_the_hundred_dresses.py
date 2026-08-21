"""Seed Violet's Blackbird 'The Hundred Dresses' course (idempotent).

    python manage.py seed_the_hundred_dresses --for-user ronald

Follows the family's purchased Blackbird & Company Literature Discovery Guide
(Level 3): the five-week shape (Read → Journal → Acquire → Recollect → Explore,
then Glean), the guide's own vocabulary exercises, comprehension questions,
writing prompts and discussion questions. Teacher answer keys ride on each set's
``answer_key`` and are never shown to the student; the official Blackbird key is
linked as a teacher-only CurriculumResource.

Content lives in ``tutor/hundred_dresses.py`` so this file stays about the
plumbing. The same shape as ``seed_a_mouse_called_wolf`` and
``seed_rickshaw_girl`` — same series, same level, same child.

ONE DIFFERENCE WORTH KNOWING. This guide's Glean is already hands-on — dress
designs in watercolour, a diorama, a recited speech — so unlike A Mouse Called
Wolf it needs no no-writing alternative added beside it. Option 3 is the one to
point her at.
"""

import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import (Curriculum, CurriculumPlacement, CurriculumResource,
                              Lesson)
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.hundred_dresses import GLEAN_OPTIONS, SECTIONS
from tutor.models import Question, QuestionSet, ResponseSheet

MASTERY_NOTE = (
    "\n\nAssess mastery, not perfection — Beginning · Developing · Proficient · "
    "Mastered. The guide awards full points for complete, creative work that goes "
    "beyond the basic requirements."
)

JOURNAL_INTRO = (
    "As you read, keep a reading journal. For each character below, jot "
    "bullet-point notes about WHO they are — what they look like, how they act, "
    "think and feel — not just what they do (that goes under Plot). Then note the "
    "Setting and the main events of the Plot."
)
JOURNAL_RUBRIC = (
    "## Teacher notes — Journal (4 points: Characters 2 · Setting 1 · Plot 1)\n"
    "- Characters: notes describe who a character IS (looks, personality, feelings).\n"
    "- Setting: where and when the story happens, plus how it matters.\n"
    "- Plot: the main events in order — reminders, not a full retelling.\n"
    "- Bullet points are perfect at this level." + MASTERY_NOTE
)

ACQUIRE_INTRO = (
    "Match each word to its meaning, then use the same words to finish the "
    "sentences. Use a dictionary if you need help."
)
ACQUIRE_RUBRIC = (
    "## Teacher notes — Acquire (2 points)\n"
    "Both exercises are the guide's own and mark themselves. The point is not "
    "the definitions but meeting the words again in a new sentence." + MASTERY_NOTE
)

RECOLLECT_INTRO = (
    "Answer the following questions using complete sentences. You may refer to "
    "both the book and your journal notes."
)
RECOLLECT_RUBRIC = (
    "## Teacher notes — Recollect (3 points)\n"
    "Checking basic understanding, not interpretation. A complete sentence that "
    "answers the question is full marks; noting the page it came from is a good "
    "habit worth praising." + MASTERY_NOTE
)

WRITING_INTRO = (
    "Write a complete paragraph on the topic below. Remember a topic sentence, "
    "several supporting sentences, and a concluding sentence. Plan it in the "
    "rough draft, then write the whole thing out as your final draft."
)
WRITING_RUBRIC = (
    "## Teacher notes — Explore: Writing (4 points)\n"
    "One paragraph, planned then written out. Look for a topic sentence, "
    "supporting sentences that actually support it, and a concluding sentence — "
    "and for a real answer to the question rather than a safe one. Spelling and "
    "handwriting matter less than whether she said something true."
    + MASTERY_NOTE
)

DISCUSSION_INTRO = (
    "Think about and talk through these together. There are no single right "
    "answers — this is the part of the week where the story gets argued about."
)
DISCUSSION_RUBRIC = (
    "## Teacher notes — Explore: Discussion (3 points)\n"
    "Teacher-led and spoken. This book is about standing by while somebody is "
    "teased, so several of these questions land close to home; the useful answer "
    "is the honest one, not the tidy one. Award the points for engaging."
    + MASTERY_NOTE
)

GLEAN_INTRO = (
    "You finished the book — now GLEAN! Complete one (or more) of the guide's "
    "final project options:\n\n"
    + "\n".join(f"{i}. {opt}" for i, opt in enumerate(GLEAN_OPTIONS, start=1))
)
GLEAN_RUBRIC = (
    "## Teacher notes — Glean (20 points)\n"
    "A finished project with a clear plan and a personal connection to the story. "
    "Reward effort, creativity and reflection.\n\n"
    "**This guide's options are already hands-on** — ten dress designs in "
    "watercolour, a diorama, a speech learned by heart — so there is no need to "
    "invent a no-writing alternative the way A Mouse Called Wolf needed. Option 3 "
    "is the one to point her at.\n\n"
    "If she works on paper, photograph it and upload it to this section: the "
    "photo prints in her report the same as anything drawn on screen."
    + MASTERY_NOTE
)


def _matching_passage(matching):
    return json.dumps({
        "words": matching["words"],
        "definitions": [
            {"n": n, "text": text, "word": word}
            for n, text, word in matching["definitions"]
        ],
    })


def _fill_blank_passage(matching, fill_blank):
    return json.dumps({
        "words": matching["words"],
        "sentences": [{"text": text, "word": word} for text, word in fill_blank],
    })


def _acquire_answer_key(section):
    match_lines = [
        f"{word} = {n} ({text})"
        for n, text, word in section["matching"]["definitions"]
    ]
    blank_lines = [
        f"{i}. {word}" for i, (_text, word) in enumerate(section["fill_blank"], start=1)
    ]
    return (
        "## Answer key — Acquire  ·  teacher reference only\n"
        "**Match the word to its number**\n"
        + "\n".join(f"- {line}" for line in match_lines)
        + "\n\n**Fill in the blank**\n"
        + "\n".join(f"- {line}" for line in blank_lines)
    )


def _recollect_answer_key(section):
    lines = [
        f"{i}. **{prompt}**\n   {answer}"
        for i, (prompt, answer) in enumerate(section["recollect"], start=1)
    ]
    return (
        f"## Answer key — Section {section['number']} comprehension  ·  "
        "teacher reference only\n"
        "Suggested answers. Cross-check the official Blackbird key linked in "
        "Resources — a child who answers differently but correctly is correct.\n\n"
        + "\n\n".join(lines)
    )


class Command(BaseCommand):
    help = "Seed the Blackbird 'The Hundred Dresses' Level 3 course for a child."

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

        blueprint = get_blueprint("blackbird_hundred_dresses")
        family = get_active_family(user)
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user,
            name=blueprint["name"],
            defaults={
                "subject": blueprint["subject"],
                "grade_level": blueprint["grade_level"],
                "family": family,
            },
        )
        chapters, lessons = apply_blueprint(curriculum, blueprint)
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk} "
            f"({chapters} sections, {lessons} lessons)."
        )

        child = Student.objects.filter(
            parent=user, first_name__iexact=options["child_name"],
        ).first()
        if child is None:
            raise CommandError(
                f"No child named '{options['child_name']}' found for {user.username}.")
        first_lesson = Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=1, order=1)
        _, placed = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first_lesson})

        set_count = q_count = 0
        for section in SECTIONS:
            n, reading = section["number"], section["title"]
            journal = self._lesson(curriculum, n, 2)
            acquire = self._lesson(curriculum, n, 3)
            recollect = self._lesson(curriculum, n, 4)
            explore = self._lesson(curriculum, n, 5)

            s, q = self._seed_set(
                journal, family,
                title=f"Section {n} · Journal",
                reading=reading,
                intro=JOURNAL_INTRO,
                rubric=JOURNAL_RUBRIC,
                questions=[
                    ("character",
                     "CHARACTERS — as you read, note interesting, important and new "
                     "things you learn about the characters. Describe such things as "
                     "their personality and appearance, including details about the "
                     "way they act, think and feel.",
                     "Bullet points are perfect! Describe who each character IS — "
                     "not what they do.",
                     # A "·"-separated STRING, not a list. `passage` is a
                     # TextField, so handing it a list stores its repr and she
                     # gets one box labelled "['Peggy', 'Wanda']".
                     {"response_type": Question.TYPE_CHARACTERS,
                      "passage": " · ".join(section["characters"])}),
                    ("setting",
                     "SETTING — as you read, note where the story is happening. "
                     "Explain how the setting is significant to the story and "
                     "include any descriptive details you find.",
                     "Room 13, the school, the muddy road up to Boggins Heights, "
                     "the time of year."),
                    ("plot",
                     "PLOT — summarize what happens in this section of the story.",
                     "The big events, in order. Reminders, not a retelling."),
                ],
            )
            set_count += s; q_count += q

            s, q = self._seed_set(
                acquire, family,
                title=f"Section {n} · Vocabulary",
                reading=reading,
                intro=ACQUIRE_INTRO,
                rubric=ACQUIRE_RUBRIC,
                questions=[
                    ("vocabulary",
                     "Write in the number of the correct definition for each word.",
                     "Use a dictionary if a word is new to you.",
                     {"response_type": Question.TYPE_MATCHING,
                      "passage": _matching_passage(section["matching"])}),
                    ("vocabulary",
                     "Fill in each blank with the best word from your vocabulary list.",
                     "Each word gets used exactly once.",
                     {"response_type": Question.TYPE_FILL_BLANK,
                      "passage": _fill_blank_passage(section["matching"],
                                                     section["fill_blank"])}),
                ],
                answer_key=_acquire_answer_key(section),
            )
            set_count += s; q_count += q

            s, q = self._seed_set(
                recollect, family,
                title=f"Section {n} · Comprehension",
                reading=reading,
                intro=RECOLLECT_INTRO,
                rubric=RECOLLECT_RUBRIC,
                questions=[("comprehension", prompt, "")
                           for prompt, _answer in section["recollect"]],
                answer_key=_recollect_answer_key(section),
            )
            set_count += s; q_count += q

            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Writing",
                reading=reading,
                intro=WRITING_INTRO,
                rubric=WRITING_RUBRIC,
                questions=[
                    ("writing", section["writing"],
                     "Plan each part in your rough draft, then write it all out as "
                     "one paragraph in the final draft. Read it out loud — your ears "
                     "catch what your eyes miss.",
                     {"response_type": Question.TYPE_PARAGRAPH}),
                ],
            )
            set_count += s; q_count += q

            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Discussion",
                reading=reading,
                intro=DISCUSSION_INTRO,
                rubric=DISCUSSION_RUBRIC,
                questions=[("discussion", prompt, "")
                           for prompt in section["discussion"]],
                mode=QuestionSet.MODE_DISCUSSION,
            )
            set_count += s; q_count += q

        # The app's whole-book literature standard, same as her other books.
        from tutor import literature

        s, q = literature.apply_literature_standard(
            curriculum, child.grade_level, family=family)
        set_count += s; q_count += q

        glean = self._lesson(curriculum, 5, 1)
        s, q = self._seed_set(
            glean, family,
            title="Section 5 · Glean: Final Project",
            reading="",
            intro=GLEAN_INTRO,
            rubric=GLEAN_RUBRIC,
            questions=[
                ("application",
                 "Which project option (1–6) did you choose — and why does it fit you?",
                 "Pick the one you'd be most excited to make."),
                ("application",
                 "Make your plan: list your steps, what you need, and what "
                 "'finished' will look like.",
                 "A good plan has a few clear steps and a finish line."),
                ("application",
                 "When your project is done, reflect: what did it help you "
                 "understand about the story? What are you proudest of?",
                 "Tell the truth about what was fun and what was hard."),
            ],
        )
        set_count += s; q_count += q

        # ...and the hands-on option, ALONGSIDE the printed six. This guide's
        # own option 3 is ten dress designs on a photocopier; this is that, in
        # the app, with three more pieces around it.
        from tutor import glean_handson

        book = glean_handson.BOOKS["hundred_dresses"]
        s, q = self._seed_set(
            glean, family,
            title="Section 5 · Glean: %s (hands-on)" % book["title"],
            reading="",
            intro=book["intro"],
            rubric=book["rubric"],
            questions=glean_handson.questions("hundred_dresses"),
        )
        set_count += s; q_count += q

        CurriculumResource.objects.get_or_create(
            curriculum=curriculum,
            url="https://blackbirdandcompany.com/information-for-parents-and-teachers/answer-keys/the-hundred-dresses/",
            defaults={
                "label": "Blackbird Answer Key",
                "resource_type": CurriculumResource.ANSWER_KEY,
                "teacher_only": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {set_count} question sets, {q_count} questions. "
            f"{child.first_name} "
            f"{'placed at Section 1' if placed else 'placed at existing progress (kept)'}."
        ))

    # -- plumbing ------------------------------------------------------------

    def _lesson(self, curriculum, chapter_number, order):
        return Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=chapter_number,
            order=order,
        )

    def _seed_set(self, lesson, family, *, title, reading, intro, rubric, questions,
                  mode=QuestionSet.MODE_STUDENT, answer_key=""):
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson,
            title=title,
            defaults={
                "family": family,
                "intro": intro,
                "reading": reading,
                "rubric": rubric,
                "answer_key": answer_key,
                "status": QuestionSet.APPROVED,
                "mode": mode,
            },
        )
        count = 0
        for i, item in enumerate(questions, start=1):
            category, prompt, hint = item[0], item[1], item[2]
            extra = item[3] if len(item) > 3 else {}
            Question.objects.update_or_create(
                question_set=qset,
                order=i,
                defaults={
                    "category": category, "prompt": prompt, "hint": hint,
                    "response_type": extra.get("response_type", Question.TYPE_TEXT),
                    "passage": extra.get("passage", ""),
                },
            )
            count += 1
        # Drop stale questions beyond the current list — but never one a child
        # has already answered.
        stale = qset.questions.filter(order__gt=len(questions))
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {
                int(k) for k, v in (sheet.answers or {}).items()
                if str(v).strip() and k.isdigit()
            }
        stale.exclude(pk__in=answered).delete()
        return 1, count
