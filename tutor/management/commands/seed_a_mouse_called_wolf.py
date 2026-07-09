"""Seed Violet's Blackbird 'A Mouse Called Wolf' course (idempotent).

Mirrors the Blackbird & Company guide's five-week SHAPE (Read → Journal →
Acquire → Recollect → Explore, then Glean) and reading schedule, but every
question, vocabulary set, writing prompt, and TEACHER ANSWER KEY here is
original work grounded in the novel — not transcribed from the copyrighted
guide. The Journal uses per-character boxes; comprehension sets carry an
answer_key for teacher reference (never shown to the student).

Run:  python manage.py seed_a_mouse_called_wolf --for-user ronald
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint, get_blueprint
from core.utils import get_active_family
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet


MASTERY_NOTE = (
    "\n\nAssess mastery, not perfection — Beginning · Developing · Proficient · "
    "Mastered. Reward complete, thoughtful, creative work."
)

JOURNAL_INTRO = (
    "As you read, keep a reading journal. For each character below, jot bullet-point "
    "notes about WHO they are — what they look like, how they act, think, and feel — "
    "not just what they do (that goes under Plot). Then note the Setting and the main "
    "events of the Plot."
)
JOURNAL_RUBRIC = (
    "## Teacher notes — Journal\n"
    "- Characters: notes describe who a character IS (looks, personality, feelings).\n"
    "- Setting: where and when the story happens, with a few sensory details.\n"
    "- Plot: the main events in order — reminders, not a full retelling.\n"
    "- Bullet points are perfect for this grade." + MASTERY_NOTE
)

VOCAB_INTRO = (
    "Vocabulary builds your reading power. For each word, write what it means in your "
    "own words. Using a dictionary is welcome — then use the word in a sentence about "
    "the story if you can."
)
VOCAB_RUBRIC = (
    "## Teacher notes — Vocabulary\n"
    "Accept any clear, correct meaning in the child's own words. Bonus for a sentence "
    "that fits the story." + MASTERY_NOTE
)
VOCAB_HINT = "Look it up if you're unsure — then say it in your own words."

RECOLLECT_INTRO = (
    "Show what you remember and understand from this section's reading. Answer in "
    "complete sentences. It's fine to look back at the book to be sure."
)
RECOLLECT_RUBRIC = (
    "## Teacher notes — Comprehension\n"
    "See the answer key below (teacher reference only — never shown to the student). "
    "Accept answers that capture the key idea, even if worded differently." + MASTERY_NOTE
)

WRITING_INTRO = (
    "Time to write! Plan first, then write a rough draft, then read it out loud and "
    "make it better. Aim for a clear beginning, middle, and end."
)
WRITING_RUBRIC = (
    "## Teacher notes — Writing\n"
    "Look for a clear topic, details that support it, and a sense of completeness. "
    "Celebrate voice and creativity; gently coach spelling and punctuation." + MASTERY_NOTE
)

DISCUSSION_INTRO = (
    "Lead these aloud with your student — no writing required. These questions have no "
    "single right answer; ask 'why?' and 'where in the book?' to press for reasons and "
    "examples."
)
DISCUSSION_RUBRIC = (
    "## Teacher notes — Discussion\n"
    "Assess the quality of thinking, not agreement. Look for reasons grounded in the "
    "story and a willingness to explain." + MASTERY_NOTE
)

SOCRATIC_INTRO = (
    "A Socratic story-grammar seminar — lead these aloud. Walk the elements: setting, "
    "characters, conflict, plot, and theme. Keep pressing back to the book for evidence."
)
SOCRATIC_RUBRIC = (
    "## Teacher notes — Socratic Seminar\n"
    "Grounded (points to the book), reasoned (gives a because), and connected (links "
    "conflict to theme). This is oral — celebrate thinking out loud." + MASTERY_NOTE
)

GLEAN_INTRO = (
    "You've finished the book — now GLEAN! Choose one (or more) final project to show "
    "what the story means to you:\n\n"
    "1. **New song** — Write a short song or poem that Wolf might sing to Mrs Honeybee.\n"
    "2. **Epilogue** — What happens next for Wolf and Mrs Honeybee? Write the next chapter.\n"
    "3. **House map** — Draw and label Mrs Honeybee's house: where Wolf lives, where the "
    "piano is, and where they make music.\n"
    "4. **My special talent** — Make a poster about a gift YOU have, the way Wolf can sing.\n"
    "5. **Thank-you letter** — Write a letter from Mrs Honeybee to Wolf.\n"
    "6. **Act it out** — Perform or record your favorite scene."
)
GLEAN_RUBRIC = (
    "## Teacher notes — Glean\n"
    "A finished project with a clear plan and a personal connection to the story. "
    "Reward effort, creativity, and reflection." + MASTERY_NOTE
)


# ---------------------------------------------------------------------------
# Original, book-grounded content. Comprehension answer keys are TEACHER-ONLY.
# ---------------------------------------------------------------------------
SECTIONS = [
    {
        "number": 1,
        "chapters": "1–3",
        "characters": "Wolf · Wolf's mother · Mrs Honeybee",
        "vocab": ["scamper", "timid", "melody", "elderly", "whisker"],
        "recollect": [
            "Where do Wolf and his mouse family live?",
            "What is Wolf's full name, and whom is it named after?",
            "Who is Mrs Honeybee, and what does she love to do?",
            "What special thing does Wolf discover he can do?",
            "Why does Wolf's mother want him to be careful?",
        ],
        "answer_key": (
            "## Answer key — Section 1 (Chapters 1–3)  ·  teacher reference only\n"
            "1. Under the floorboards of Mrs Honeybee's house.\n"
            "2. Wolfgang Amadeus Mouse — 'Wolf' for short — named after the composer Mozart.\n"
            "3. An elderly widow who lives alone; she loves to play the piano.\n"
            "4. He can sing — he can match the tunes Mrs Honeybee plays.\n"
            "5. A mouse in a person's house faces dangers (being seen, traps); she wants him safe."
        ),
        "writing_prompt": (
            "Wolf discovers he has a special talent. Write about a talent or special "
            "thing YOU can do — what it is, and how it makes you feel."
        ),
        "discussion": [
            ("character", "Wolf is the smallest in his family. Does being small make him weaker, or could it be a strength? Why?"),
            ("theme", "Mrs Honeybee lives all alone. How do you think she feels — and how can music keep someone company?"),
            ("setting", "What would it be like to live hidden under the floorboards? How would that change what you notice about the world?"),
            ("application", "Wolf's mother warns him to be careful. When is it wise to be cautious, and when is it good to be brave?"),
        ],
        "socratic": [
            ("character", "Who is the story mostly about? What do you already like or wonder about Wolf?",
             "The main character is the protagonist — the one we follow."),
            ("setting", "Where and when does the story happen? Find two details that make Mrs Honeybee's house feel real.",
             "Think about sounds, rooms, the piano, day or night."),
            ("conflict", "What does Wolf want — and what might make it hard or risky to get it?",
             "Every story is a struggle. Name the wish and the danger."),
        ],
    },
    {
        "number": 2,
        "chapters": "4–6",
        "characters": "Wolf · Mrs Honeybee",
        "vocab": ["astonish", "delighted", "cautious", "companion", "tune"],
        "recollect": [
            "How does Mrs Honeybee first realize that a mouse is singing?",
            "Instead of chasing Wolf away, how does Mrs Honeybee treat him?",
            "What name does Mrs Honeybee give the little mouse?",
            "How do Wolf and Mrs Honeybee make music together?",
            "Why is a friendship between them surprising?",
        ],
        "answer_key": (
            "## Answer key — Section 2 (Chapters 4–6)  ·  teacher reference only\n"
            "1. She hears him singing along with her piano and is astonished a mouse can sing.\n"
            "2. She welcomes him — she talks to him kindly and offers him food.\n"
            "3. 'Wolf.'\n"
            "4. She plays the piano and Wolf sings along to the tunes.\n"
            "5. People usually treat mice as pests; a lonely woman and a singing mouse becoming friends is unexpected."
        ),
        "writing_prompt": (
            "Wolf and Mrs Honeybee become unlikely friends. Write about a friendship "
            "between two very different characters — real or made up."
        ),
        "discussion": [
            ("theme", "What makes a good friend? Which of those qualities do Wolf and Mrs Honeybee show each other?"),
            ("character", "Mrs Honeybee could have been frightened of a mouse. Why do you think she chooses kindness instead?"),
            ("plot", "What has changed for Wolf now that Mrs Honeybee knows he can sing?"),
            ("application", "Have you ever become friends with someone very different from you? What did you learn?"),
        ],
        "socratic": [
            ("character", "How is Mrs Honeybee different from what a mouse would expect of a human? Point to what she says or does.",
             "Watch closely how she treats Wolf."),
            ("plot", "What is the most important thing that happens in these chapters? Why does it matter?",
             "Look for the moment everything changes."),
            ("theme", "What big idea about friendship is the story beginning to show?",
             "Theme is the truth the story wants you to feel."),
        ],
    },
    {
        "number": 3,
        "chapters": "7–9",
        "characters": "Wolf · Mrs Honeybee",
        "vocab": ["grateful", "startle", "gentle", "faint", "treasure"],
        "recollect": [
            "How has the friendship between Wolf and Mrs Honeybee grown by now?",
            "What are some ways Mrs Honeybee takes care of Wolf?",
            "How does Wolf feel about Mrs Honeybee?",
            "Why does Wolf's singing mean so much to Mrs Honeybee?",
            "What dangers or worries are still there in the background for a tiny mouse?",
        ],
        "answer_key": (
            "## Answer key — Section 3 (Chapters 7–9)  ·  teacher reference only\n"
            "1. They spend time together often — she plays, he sings — and they trust and enjoy each other.\n"
            "2. She feeds him, talks with him, and treasures his singing.\n"
            "3. He loves and trusts her; she has become like a dear friend or family.\n"
            "4. It fills her lonely days with joy and company.\n"
            "5. He is still a very small creature in a big world, where accidents and dangers can happen."
        ),
        "writing_prompt": (
            "Describe a perfect day for Wolf and Mrs Honeybee. Use your five senses — "
            "what do they see, hear, smell, taste, and touch?"
        ),
        "discussion": [
            ("theme", "How can a very small creature make a big difference in someone's life?"),
            ("character", "How does Wolf show love and courage, even though he is tiny?"),
            ("style", "This is a story about music. How does music make the book feel special?"),
            ("application", "Who is someone in your life you could bring joy to, the way Wolf does for Mrs Honeybee?"),
        ],
        "socratic": [
            ("character", "How has Wolf grown or changed since the beginning of the story?",
             "Compare the Wolf of Chapter 1 with the Wolf now."),
            ("conflict", "What could threaten this happy friendship? What are you worried might happen?",
             "Good stories build toward a problem."),
            ("theme", "What is the story saying about love between two very different friends?",
             "Connect their friendship to the big idea."),
        ],
    },
    {
        "number": 4,
        "chapters": "10–12",
        "characters": "Wolf · Mrs Honeybee",
        "vocab": ["emergency", "rescue", "helpless", "courage", "recover"],
        "recollect": [
            "What frightening thing happens to Mrs Honeybee?",
            "Why is she in such danger after it happens?",
            "How does Wolf help save Mrs Honeybee?",
            "What does Wolf's rescue show about him?",
            "How does the story end for Wolf and Mrs Honeybee?",
        ],
        "answer_key": (
            "## Answer key — Section 4 (Chapters 10–12)  ·  teacher reference only\n"
            "1. She falls and hurts herself and cannot get up.\n"
            "2. She is helpless on the floor, alone, and unable to reach help.\n"
            "3. He bravely raises the alarm and gets help so that she is found and cared for.\n"
            "4. That even the smallest creature can be brave and do something great — love makes him courageous.\n"
            "5. Mrs Honeybee recovers, and their friendship continues; Wolf's courage saved his dear friend."
        ),
        "writing_prompt": (
            "Wolf is small but very brave. Write about a time you — or someone you know — "
            "were brave, even when it was scary. What happened, and how did it feel?"
        ),
        "discussion": [
            ("conflict", "What was the biggest problem in the whole story, and how was it solved?"),
            ("character", "Wolf is tiny, yet he becomes a hero. What makes someone a real hero?"),
            ("theme", "What is the most important lesson this story teaches? Do you agree with it?"),
            ("application", "How can YOU be brave or helpful to someone who needs you?"),
        ],
        "socratic": [
            ("plot", "What is the climax — the most exciting turning-point moment of the whole story?",
             "It's the moment everything depends on."),
            ("character", "How does Wolf prove that being small doesn't mean being unimportant?",
             "Point to what he does at the end."),
            ("theme", "What does 'A Mouse Called Wolf' say about friendship, courage, and kindness? Argue for the big idea you think matters most.",
             "Connect the ending back to the whole story."),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the Blackbird 'A Mouse Called Wolf' course for a child (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True, help="Username who owns the curriculum.")
        parser.add_argument("--child-name", default="Violet", help="Child to place in the course.")

    @transaction.atomic
    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        blueprint = get_blueprint("blackbird_a_mouse_called_wolf")
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
            raise CommandError(f"No child named '{options['child_name']}' found for {user.username}.")
        first_lesson = Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=1, order=1,
        )
        _, placed = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum, defaults={"current_lesson": first_lesson},
        )

        set_count = q_count = 0
        for section in SECTIONS:
            n, chs = section["number"], section["chapters"]
            journal = self._lesson(curriculum, n, 2)
            acquire = self._lesson(curriculum, n, 3)
            recollect = self._lesson(curriculum, n, 4)
            explore = self._lesson(curriculum, n, 5)

            # Journal — per-character boxes + setting + plot.
            s, q = self._seed_set(
                journal, family,
                title=f"Section {n} · Journal",
                reading=chs,
                intro=JOURNAL_INTRO,
                rubric=JOURNAL_RUBRIC,
                questions=[
                    ("character",
                     "CHARACTERS — for each person below, note who they are: what they "
                     "look like, and how they act, think, and feel.",
                     "Bullet points are perfect! Describe who each character IS — not what they do.",
                     {"response_type": Question.TYPE_CHARACTERS, "passage": section["characters"]}),
                    ("setting",
                     "SETTING — where and when is this part of the story happening? Add a "
                     "few details that make the place feel real.",
                     "Rooms, sounds, the piano, day or night, the mouse world under the floor."),
                    ("plot",
                     "PLOT — what are the main things that happen in this section?",
                     "Major events only — short reminders, not a retelling."),
                ],
            )
            set_count += s; q_count += q

            # Acquire — vocabulary.
            s, q = self._seed_set(
                acquire, family,
                title=f"Section {n} · Vocabulary",
                reading=chs,
                intro=VOCAB_INTRO,
                rubric=VOCAB_RUBRIC,
                questions=[("vocabulary", f"Define: **{word}**", VOCAB_HINT) for word in section["vocab"]],
            )
            set_count += s; q_count += q

            # Recollect — comprehension (teacher answer key attached).
            s, q = self._seed_set(
                recollect, family,
                title=f"Section {n} · Comprehension",
                reading=chs,
                intro=RECOLLECT_INTRO,
                rubric=RECOLLECT_RUBRIC,
                questions=[("comprehension", prompt, "") for prompt in section["recollect"]],
                answer_key=section["answer_key"],
            )
            set_count += s; q_count += q

            # Explore — writing.
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Writing",
                reading=chs,
                intro=WRITING_INTRO,
                rubric=WRITING_RUBRIC,
                questions=[
                    ("application",
                     f"ROUGH DRAFT — {section['writing_prompt']}",
                     "Just get your ideas down — the polishing comes next."),
                    ("application",
                     "FINAL DRAFT — read your rough draft out loud, fix what you can, then "
                     "write your best version here.",
                     "Check your capital letters, periods, and spelling."),
                ],
            )
            set_count += s; q_count += q

            # Explore — discussion (teacher-led).
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Discussion",
                reading=chs,
                intro=DISCUSSION_INTRO,
                rubric=DISCUSSION_RUBRIC,
                questions=[(cat, prompt, "") for cat, prompt in section["discussion"]],
                mode=QuestionSet.MODE_DISCUSSION,
            )
            set_count += s; q_count += q

            # Explore — Socratic story-grammar seminar (teacher-led).
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Socratic Seminar",
                reading=chs,
                intro=SOCRATIC_INTRO,
                rubric=SOCRATIC_RUBRIC,
                questions=section["socratic"],
                mode=QuestionSet.MODE_DISCUSSION,
            )
            set_count += s; q_count += q

        # Whole-book literature standard: Story-Grammar Seminar + grade-level Toolbox.
        from tutor import literature

        s, q = literature.apply_literature_standard(curriculum, child.grade_level, family=family)
        set_count += s; q_count += q

        # Glean — final project.
        glean = self._lesson(curriculum, 5, 1)
        s, q = self._seed_set(
            glean, family,
            title="Section 5 · Glean: Final Project",
            reading="",
            intro=GLEAN_INTRO,
            rubric=GLEAN_RUBRIC,
            questions=[
                ("application",
                 "Which project (1–6) did you choose — and why does it fit you?",
                 "Pick the one you'd be most excited to make."),
                ("application",
                 "Make your plan: list your steps, what you need, and what 'finished' will look like.",
                 "A good plan has a few clear steps and a finish line."),
                ("application",
                 "When your project is done, reflect: what did it help you understand about "
                 "the story? What are you proudest of?",
                 "Tell the truth about what was fun and what was hard."),
            ],
        )
        set_count += s; q_count += q

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {set_count} question sets, {q_count} questions. "
            f"{child.first_name} placed at {'Section 1: Read' if placed else 'existing progress (kept)'}."
        ))

    # -- helpers -------------------------------------------------------------

    def _lesson(self, curriculum, chapter_number, order):
        return Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=chapter_number, order=order,
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
        # has already answered (that would orphan their saved response).
        stale = qset.questions.filter(order__gt=len(questions))
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {
                int(k) for k, v in (sheet.answers or {}).items() if str(v).strip() and k.isdigit()
            }
        stale.exclude(pk__in=answered).delete()
        return 1, count
