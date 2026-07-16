"""Seed Violet's Blackbird 'A Mouse Called Wolf' course (idempotent).

Follows the family's purchased Blackbird & Company Literature Discovery Guide
(Level 3) for private family use: the five-week shape (Read → Journal →
Acquire → Recollect → Explore, then Glean), the guide's reading schedule,
vocabulary exercises (match-the-number + fill-in-the-blank, replicating the
workbook page), comprehension/discussion/writing prompts, and the guide's
grading weights. Teacher answer keys ride on each set's ``answer_key`` (never
shown to the student); the official Blackbird key is linked as a teacher-only
CurriculumResource.

Run:  python manage.py seed_a_mouse_called_wolf --for-user ronald
"""

import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from curricula.models import Curriculum, CurriculumPlacement, CurriculumResource, Lesson
from curricula.services import apply_blueprint, get_blueprint
from core.utils import get_active_family
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet


MASTERY_NOTE = (
    "\n\nAssess mastery, not perfection — Beginning · Developing · Proficient · "
    "Mastered. The guide awards full points for complete, creative work that goes "
    "beyond the basic requirements."
)

JOURNAL_INTRO = (
    "As you read, keep a reading journal. For each character below, jot bullet-point "
    "notes about WHO they are — what they look like, how they act, think, and feel — "
    "not just what they do (that goes under Plot). Then note the Setting and the main "
    "events of the Plot."
)
JOURNAL_RUBRIC = (
    "## Teacher notes — Journal (4 points: Characters 2 · Setting 1 · Plot 1)\n"
    "Guide section weights (20 pts): Read 4 · Journal 4 · Acquire 2 · Recollect 3 · "
    "Explore 7 (Writing 4, Discussion 3). Award the Read points for completing the "
    "section's reading.\n"
    "- Characters: notes describe who a character IS (looks, personality, feelings).\n"
    "- Setting: where and when the story happens, plus how it matters to the story.\n"
    "- Plot: the main events in order — reminders, not a full retelling.\n"
    "- Bullet points are perfect at this level." + MASTERY_NOTE
)

ACQUIRE_RUBRIC = (
    "## Teacher notes — Acquire (2 points)\n"
    "Both halves are self-checking: the matching locks in when correct, and each "
    "blank locks when the right word is chosen. The answer key below is for your "
    "reference." + MASTERY_NOTE
)

RECOLLECT_INTRO = (
    "Answer the following questions using complete sentences. You may refer to both "
    "the book and your Journal notes."
)
RECOLLECT_RUBRIC = (
    "## Teacher notes — Recollect (3 points)\n"
    "Suggested answers are in the key below (teacher reference only — never shown to "
    "the student). Accept answers that capture the key idea in the child's own words. "
    "The official Blackbird answer key is linked under the curriculum's Resources." + MASTERY_NOTE
)

WRITING_INTRO = (
    "Write a complete paragraph based on the topic below. Remember to include a topic "
    "sentence, several supporting sentences, and a concluding sentence."
)
WRITING_RUBRIC = (
    "## Teacher notes — Writing (4 points)\n"
    "The guide's writing scale:\n"
    "- **Accomplished (4)** — creatively focuses on the topic; logical progression "
    "with supporting details; varied sentences; strong word choice; mature conventions.\n"
    "- **Proficient (3)** — focused with adequate support; mostly logical progression; "
    "some sentence variety; adequate transitions; general command of conventions.\n"
    "- **Basic (2.5)** — topic addressed but unclear; weak support and progression; "
    "stagnant sentences; average word choice; partial command of conventions.\n"
    "- **Limited (2)** — topic barely addressed; weak organization; fragments and "
    "run-ons; poor transitions and word choice." + MASTERY_NOTE
)

DISCUSSION_INTRO = (
    "Think about and discuss the following questions aloud together — no writing "
    "required. Press for reasons and examples from the book."
)
DISCUSSION_RUBRIC = (
    "## Teacher notes — Discussion (3 points)\n"
    "Assess the quality of thinking, not agreement: reasons grounded in the story and "
    "a willingness to explain." + MASTERY_NOTE
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
    "You finished the book — now GLEAN! Complete one (or more) of the guide's final "
    "project options:\n\n"
    "1. **Composer compare** — Listen to music by Schubert, Beethoven, and Mozart. "
    "Which composer do you prefer? Write a paragraph describing what you like about "
    "this composer and why — be as specific as possible.\n"
    "2. **Mozart** — Research and write a paragraph about the life of Mozart. Include "
    "any pictures you can find of him.\n"
    "3. **Grand piano** — Research and write a paragraph about grand pianos. Make a "
    "drawing of a grand piano and label the parts.\n"
    "4. **Your name** — Research the history and meaning of your own name. Interview "
    "your parents. Were you named after someone? Does your name have a special "
    "meaning? Write a paragraph about your findings.\n"
    "5. **Musical terms** — Look up and write the music-related definitions of: "
    "ballad, bass, carol, composer, discordant, key, measure, melody, opus, reprise, "
    "rhythm, scales, solo, sonata."
)
GLEAN_RUBRIC = (
    "## Teacher notes — Glean (20 points)\n"
    "A finished project with a clear plan and a personal connection to the story. "
    "Reward effort, creativity, and reflection." + MASTERY_NOTE
)


# ---------------------------------------------------------------------------
# Content from the family's purchased guide (private family use).
# Matching: (number, definition, word) triples exactly as printed — the fixed
# numbering IS the answer key. Fill-blank: (sentence with ______, word).
# Comprehension keys are suggested answers; the official key is linked in
# Resources for cross-checking.
# ---------------------------------------------------------------------------
SECTIONS = [
    {
        "number": 1,
        "chapters": "1–3",
        "characters": "Wolfgang Amadeus Mouse · Mary (Mrs Honeybee)",
        "matching": {
            "words": ["ordinary", "venture", "gleam", "edible", "dwindle", "curiosity"],
            "definitions": [
                (1, "eagerness to know about something", "curiosity"),
                (2, "able to be eaten", "edible"),
                (3, "common or plain", "ordinary"),
                (4, "a risky task", "venture"),
                (5, "to decrease little by little", "dwindle"),
                (6, "to shine", "gleam"),
            ],
        },
        "fill_blank": [
            ("I want you to polish the table until you make the surface ______.", "gleam"),
            ("Maria did not want an ______ dress for the party, she wanted a fancy one.", "ordinary"),
            ("If you do not buy more rabbit food, the supply will slowly ______.", "dwindle"),
            ("The brave explorers must ______ into the dark forest to begin their quest.", "venture"),
            ("Many things that are ______ do not taste very good.", "edible"),
            ("Due to his ______, Frank liked to ask many questions.", "curiosity"),
        ],
        "recollect": [
            "Why does Wolfgang's mother want to give him an important sounding name?",
            "Why does Wolfgang feel unhappy when his brothers and sisters are playing?",
            "What does Wolfgang's mother believe he is going to grow up to be?",
            "Why does Wolfgang keep returning home after each nightly scrounge?",
            "Why does Wolfgang like the evening recital best?",
            "Why does Wolfgang's mother become annoyed with him?",
            "What danger does Wolfgang's singing arouse?",
        ],
        "recollect_key": (
            "1. To make up for his small size — an important-sounding name for the "
            "smallest of the litter.\n"
            "2. His brothers and sisters mock his size with a teasing rhyme, and it "
            "hurts his feelings.\n"
            "3. An important mouse — with a name like that, she believes he will grow "
            "up to be somebody.\n"
            "4. He returns home for safety — back to the nest and his mother.\n"
            "5. Because in the evening he is rested and alert, so he can enjoy the "
            "music best.\n"
            "6. She grows frustrated with his singing and his dream of being a "
            "singing mouse.\n"
            "7. His singing draws the CAT toward the living room — deadly danger for "
            "a mouse."
        ),
        "writing_prompt": (
            "Write a paragraph about Wolfgang Amadeus Mouse. Be sure to include details "
            "you have learned about this character in your reading."
        ),
        "discussion": [
            ("theme", "Wolf was given a great name. Can someone without a great name be great? Can a great name help someone be great? What are some qualities of greatness? In the future, if people look back and think of you as great, where would you want that greatness to come from?"),
            ("application", "Do you feel that your name suits you? If you had to choose a famous name for yourself, what name would you choose, and why?"),
            ("character", "For what three reasons did Wolfgang's brothers and sisters tease him? How did their teasing make him feel about his name? Have you ever teased someone in this way? If you have, how do you think it made them feel? How did you feel?"),
            ("theme", "What is jealousy? Why were Wolf's brothers and sisters jealous of him? How does it feel to be jealous? How does jealousy make others feel?"),
            ("character", "How does Wolfgang communicate his despair to his mother? How did Wolfgang's mother encourage him? Have you ever felt hopeless? Who encouraged you?"),
            ("application", "Wolfgang had a seemingly ridiculous dream — to be a singing mouse. Even his mother could not believe this for her son. Yet, in the end, to the great surprise of Wolfgang, what became of his dream? Have you ever hoped to do or be something that seemed out of your reach?"),
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
        "characters": "Wolfgang Amadeus Mouse · Mrs. Honeybee",
        "matching": {
            "words": ["nuzzle", "obvious", "taut", "widow", "composer", "encounter"],
            "definitions": [
                (1, "easily seen or understood", "obvious"),
                (2, "a woman whose husband had died", "widow"),
                (3, "to rub with the nose", "nuzzle"),
                (4, "a person who writes music", "composer"),
                (5, "pulled tight", "taut"),
                (6, "to meet somebody unexpectedly", "encounter"),
            ],
        },
        "fill_blank": [
            ("It was ______ from the mess that he hadn't cleaned his room yet.", "obvious"),
            ("The puppy liked to ______ people with its wet nose to show it liked them.", "nuzzle"),
            ("The choir director at our church recently became a ______ after her husband died.", "widow"),
            ("The kite string was so ______ we thought it might break at any moment.", "taut"),
            ("The close ______ with the bat made everyone scream.", "encounter"),
            ("The ______ wanted to write music that would make people get up and dance.", "composer"),
        ],
        "recollect": [
            "When Wolfgang's mother is listening to his song for the first time, what danger does she sense?",
            "How do Wolfgang and his mother escape the danger?",
            "How are they rescued in the end?",
            "How does Mrs. Honeybee feel about animals?",
            "Who are Mrs. Honeybee's favorite classical composers?",
            "What do Mrs. Honeybee and Wolfgang's mother have in common?",
            "What treat does Mrs. Honeybee use to show Wolfgang that she is not a threat?",
        ],
        "recollect_key": (
            "1. The cat — she senses it is about to attack while Wolfgang sings.\n"
            "2. They escape by darting INTO the piano's insides, where the cat can't "
            "reach them.\n"
            "3. Mrs Honeybee opens the piano and discovers them, letting them out.\n"
            "4. She has compassion for all creatures — she would never hurt an animal, "
            "even a mouse.\n"
            "5. Brahms, Beethoven, and Mozart.\n"
            "6. Both are widows — each has lost her husband.\n"
            "7. Chocolate — she offers it to show him she can be trusted."
        ),
        "writing_prompt": (
            "Wolfgang and his mother react differently to being trapped inside the "
            "piano. Write a paragraph comparing and contrasting their reactions."
        ),
        "discussion": [
            ("character", "Wolfgang did not crumble in the face of danger but exhibited bravery and hope when trapped in the piano. How did his bravery pay off? Have you ever been afraid? How did you respond to your fear?"),
            ("character", "Instead of wallowing in her loneliness, Mrs. Honeybee comes up with a plan for change. What is her plan and does it succeed? Have you ever been lonely? How did you solve the problem?"),
            ("theme", "Mrs. Honeybee realizes that she must ease Wolfgang's fear and become friends with him before they can share their common love for music. What are some of the many rewards of friendship? What are your experiences with friendship? Have you ever become friends with someone who scared or intimidated you at first?"),
            ("application", "Do you believe that music can influence your mood? Why or why not?"),
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
        "characters": "Wolfgang Amadeus Mouse · Mary (Mrs Honeybee)",
        "matching": {
            "words": ["coward", "deceive", "discordant", "mingle", "scheme", "umbrage"],
            "definitions": [
                (1, "offense or resentment", "umbrage"),
                (2, "music that sounds unpleasant", "discordant"),
                (3, "to mix together", "mingle"),
                (4, "someone easily frightened", "coward"),
                (5, "to hide the truth", "deceive"),
                (6, "a plan of action", "scheme"),
            ],
        },
        "fill_blank": [
            ("The out-of-tune guitar was so ______ I had to cover my ears.", "discordant"),
            ("Everybody used to think Brad was a ______ until they saw him jump off the high dive platform into the pool.", "coward"),
            ("Brenda tried to ______ him by telling a lie about what really happened.", "deceive"),
            ("The robber had a ______ to break out of jail, but he was caught as soon as he tried to escape.", "scheme"),
            ("The hostess of the party loved to ______ with her guests to get to know them all better.", "mingle"),
            ("My grandmother took ______ at the fact that I wiped my cheek off after she kissed it.", "umbrage"),
        ],
        "recollect": [
            "What is the name of the song Mrs. Honeybee plays while Wolfgang is standing over middle C?",
            "Why, after many nights, does Mrs. Honeybee withhold Wolfgang's treat?",
            "What does Wolfgang challenge his mother to do?",
            "What does Wolfgang decide to do when Mrs. Honeybee does not show up to accompany him on the piano?",
            "Who does Wolfgang encounter when he walks into the kitchen?",
            "Why doesn't Mrs. Honeybee show up to play the piano?",
            "How did Wolfgang attract the attention of the policeman?",
        ],
        "recollect_key": (
            "1. \"You're the Top\" — she plays it while Wolfgang stands over middle C.\n"
            "2. She withholds the treat until he performs — he must sing to earn it.\n"
            "3. To join him up on top of the piano.\n"
            "4. He goes searching for her through the house.\n"
            "5. The cat — who runs away in fear.\n"
            "6. She has broken her ankle and cannot come.\n"
            "7. He sings the word \"help\" — the song tells the policeman something "
            "is wrong."
        ),
        "writing_prompt": (
            "Write a paragraph about Mrs. Honeybee. Be sure to include details you have "
            "learned about her in your reading."
        ),
        "discussion": [
            ("character", "Wolfgang's mother is humiliated when she tries to sing. Was Wolfgang intending to embarrass his mother? Was his mother truly being set up to be humiliated or was that just her perception?"),
            ("character", "Why do you think Wolfgang is trusting of Mrs. Honeybee while his mother is not? Have you ever mistrusted anyone? In the end, did you gain trust for that person? If so, how?"),
            ("application", "If you were Wolfgang, how would you have tried to help Mrs. Honeybee when she fell? Do you think that animals and humans can communicate? If you have a pet, how do you communicate with it?"),
            ("application", "When Wolf encounters Ginger the cat in the kitchen, he is emboldened by the fact that Ginger runs away in fear. Is there something you are afraid of, and what might help you overcome this fear?"),
        ],
        "socratic": [
            ("character", "How has Wolf grown or changed since the beginning of the story?",
             "Compare the Wolf of Chapter 1 with the Wolf now."),
            ("conflict", "What could threaten this happy friendship? What are you worried might happen?",
             "Good stories build toward a problem."),
            ("theme", "What is the story saying about courage in small creatures?",
             "Connect Wolf's bravery to the big idea."),
        ],
    },
    {
        "number": 4,
        "chapters": "10–11",
        "characters": "Wolfgang Amadeus Mouse · Mary (Mrs Honeybee)",
        "matching": {
            "words": ["inspire", "precocious", "ration", "senile", "instinct", "pity"],
            "definitions": [
                (1, "very advanced or mature", "precocious"),
                (2, "a fixed amount", "ration"),
                (3, "a strong natural urge", "instinct"),
                (4, "to influence or motivate", "inspire"),
                (5, "feeling sad for someone or something", "pity"),
                (6, "a decline due to old age", "senile"),
            ],
        },
        "fill_blank": [
            ("Everyone said Emily was ______ when she started doing algebra at her fifth birthday party.", "precocious"),
            ("The girl felt ______ over the wounded baby bird.", "pity"),
            ("Birds fly south for the winter because it is their ______ to survive.", "instinct"),
            ("The hikers ate a small ______ of their food each day to make sure it would last for the entire trip.", "ration"),
            ("Old Mrs. Smith told such silly jokes that everyone thought she was ______, when actually, she was just a poor joke teller.", "senile"),
            ("Reading stories about knights and dragons would ______ him to become a brave soldier.", "inspire"),
        ],
        "recollect": [
            "What does Wolfgang try to do while Mrs. Honeybee is in the hospital?",
            "What qualities of Wolfgang's first composition move and captivate Mary?",
            "What does Wolfgang name his first composition?",
            "What is the first thing Mrs. Honeybee does when she arrives home?",
            "How does Wolfgang help Mrs. Honeybee fall asleep?",
            "What is Mrs. Honeybee's opinion of Wolfgang's composition?",
            "What does Mrs. Honeybee give Wolfgang at the very end of the story?",
        ],
        "recollect_key": (
            "1. He tries to compose an original song of his own while she is away.\n"
            "2. Its lightness and joyful quality — it moves and captivates her.\n"
            "3. The \"Swallow Sonata\".\n"
            "4. She goes straight to the piano.\n"
            "5. He sings her a Chopin lullaby until she drifts off.\n"
            "6. She recognizes it as a real, significant piece of music.\n"
            "7. A name honoring the young composer Mozart — Wolfgang Amadeus.\n"
            "(Question 7 was reconstructed from a damaged page of our copy; the "
            "official Blackbird key is linked under Resources.)"
        ),
        "writing_prompt": (
            "Write a paragraph about something that has made your heart sing. Use your "
            "passion for this topic to persuade your audience to become interested in "
            "this topic as well."
        ),
        "discussion": [
            ("application", "When Wolfgang tries to compose a song, he is unsuccessful at first. Have you ever tried to learn or do something new, only to find that it wasn't easy? Why is it important not to give up when something is hard?"),
            ("style", "How is Wolfgang inspired for his musical composition? In what other ways might artists be inspired to create? If you know any artists, ask them what inspires them."),
            ("character", "Although his mother is not musical, she is moved when listening to Wolfgang's composition. What is she moved by? Has music ever affected you in this way?"),
            ("theme", "While Wolfgang and Mrs. Honeybee do not communicate in the same verbal language, they manage to understand each other. How do they accomplish this? Can you think of a way that you communicate without words?"),
        ],
        "socratic": [
            ("plot", "What is the climax — the most exciting turning-point moment of the whole story?",
             "It's the moment everything depends on."),
            ("character", "How does Wolf prove that being small doesn't mean being unimportant?",
             "Point to what he does when Mrs Honeybee needs him."),
            ("theme", "What does 'A Mouse Called Wolf' say about friendship, courage, and using your gift? Argue for the big idea you think matters most.",
             "Connect the ending back to the whole story."),
        ],
    },
]


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
        "Matching:\n" + "\n".join(sorted(match_lines)) + "\n\n"
        "Fill in the blank:\n" + "\n".join(blank_lines)
    )


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

            # Journal — per-character boxes + setting + plot (guide weights 2/1/1).
            s, q = self._seed_set(
                journal, family,
                title=f"Section {n} · Journal",
                reading=chs,
                intro=JOURNAL_INTRO,
                rubric=JOURNAL_RUBRIC,
                questions=[
                    ("character",
                     "CHARACTERS — as you read, note interesting, important and new "
                     "things you learn about the characters. Describe such things as "
                     "their personality and appearance, including details about the way "
                     "they act, think and feel.",
                     "Bullet points are perfect! Describe who each character IS — not what they do.",
                     {"response_type": Question.TYPE_CHARACTERS, "passage": section["characters"]}),
                    ("setting",
                     "SETTING — as you read, note where the story is happening. Explain "
                     "how the setting is significant to the story and include any "
                     "descriptive details you find.",
                     "Rooms, sounds, the piano, day or night, the mouse world under the floor."),
                    ("plot",
                     "PLOT — summarize what happens in this section of the story.",
                     "Major events only — short reminders, not a retelling."),
                ],
            )
            set_count += s; q_count += q

            # Acquire — the workbook page: match the number, then fill the blanks.
            s, q = self._seed_set(
                acquire, family,
                title=f"Section {n} · Vocabulary",
                reading=chs,
                intro="Vocabulary builds your reading power. Match each word first — "
                      "then use the same words to fill in the blanks.",
                rubric=ACQUIRE_RUBRIC,
                answer_key=_acquire_answer_key(section),
                questions=[
                    ("vocabulary",
                     "Match each word with the number of its correct definition. "
                     "Use a dictionary if you need help.",
                     "Tap a word, then tap the definition that matches it. Green means got it!",
                     {"response_type": Question.TYPE_MATCHING,
                      "passage": _matching_passage(section["matching"])}),
                    ("vocabulary",
                     "Fill in each blank with the best word from your vocabulary list.",
                     "Each word gets used exactly once.",
                     {"response_type": Question.TYPE_FILL_BLANK,
                      "passage": _fill_blank_passage(section["matching"], section["fill_blank"])}),
                ],
            )
            set_count += s; q_count += q

            # Recollect — the guide's comprehension questions (suggested key attached).
            s, q = self._seed_set(
                recollect, family,
                title=f"Section {n} · Comprehension",
                reading=chs,
                intro=RECOLLECT_INTRO,
                rubric=RECOLLECT_RUBRIC,
                questions=[("comprehension", prompt, "") for prompt in section["recollect"]],
                answer_key=(
                    f"## Answer key — Section {n} comprehension  ·  teacher reference only\n"
                    + section["recollect_key"]
                ),
            )
            set_count += s; q_count += q

            # Explore — writing: ONE paragraph exercise that mirrors the guide's two
            # pages — a rough draft split into Topic/Supporting/Concluding sections,
            # then a final draft she writes it all into.
            s, q = self._seed_set(
                explore, family,
                title=f"Section {n} · Writing",
                reading=chs,
                intro=WRITING_INTRO,
                rubric=WRITING_RUBRIC,
                questions=[
                    ("writing",
                     section["writing_prompt"],
                     "Plan each part in your rough draft, then write it all out as one "
                     "paragraph in the final draft. Read it out loud — your ears catch "
                     "what your eyes miss.",
                     {"response_type": Question.TYPE_PARAGRAPH}),
                ],
            )
            set_count += s; q_count += q

            # Explore — the guide's discussion questions (teacher-led).
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

            # Explore — Socratic story-grammar seminar (the app's literature standard).
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

        # Glean — the guide's final project options.
        glean = self._lesson(curriculum, 5, 1)
        s, q = self._seed_set(
            glean, family,
            title="Section 5 · Glean: Final Project",
            reading="",
            intro=GLEAN_INTRO,
            rubric=GLEAN_RUBRIC,
            questions=[
                ("application",
                 "Which project option (1–5) did you choose — and why does it fit you?",
                 "Pick the one you'd be most excited to make."),
                ("application",
                 "Make your plan: list your steps, what you need, and what 'finished' will look like.",
                 "A good plan has a few clear steps and a finish line."),
                ("application",
                 "When your project is done, reflect: what did it help you understand "
                 "about the story? What are you proudest of?",
                 "Tell the truth about what was fun and what was hard."),
            ],
        )
        set_count += s; q_count += q

        # Teacher-reference answer-key link (never shown to the student).
        CurriculumResource.objects.get_or_create(
            curriculum=curriculum,
            url="https://blackbirdandcompany.com/information-for-parents-and-teachers/answer-keys/a-mouse-called-wolf/",
            defaults={
                "label": "Blackbird Answer Key",
                "resource_type": CurriculumResource.ANSWER_KEY,
                "teacher_only": True,
                "order": 0,
            },
        )

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
