"""The literature standard — ties ANY literature curriculum to the Socratic method.

Two reusable pieces, both graded to the reader's level:
1. A **literary-devices toolbox** — a catalog of literary tools (onomatopoeia,
   simile, metaphor, symbolism, irony, …) with kid-facing definitions, examples,
   and "find it in the book" questions, banded by grade.
2. ``apply_literature_standard(curriculum, level)`` — attaches, to any literature
   curriculum, two teacher-led discussion sets: a **Story-Grammar Seminar**
   (from ``tutor.socratic``) and the **Literary Toolbox** at that level.

Run it whenever a literature book is added (e.g. a Blackbird guide) so the book
is instantly tied to literary analysis, scaled by grade.
"""

from tutor import socratic

# key -> {band, name, definition, example, question}
# band: 1 = grades K-3, 2 = grades 4-6, 3 = grades 7-12 (cumulative).
LITERARY_DEVICES = {
    # --- Band 1: sounds & pictures (K-3) ---
    "onomatopoeia": {
        "band": 1, "name": "Onomatopoeia",
        "definition": "a word that sounds like the noise it names",
        "example": "buzz, splash, boom, meow",
        "question": "Find a word the author uses that SOUNDS like its meaning (like buzz or splash). What sound do you hear?",
    },
    "rhyme": {
        "band": 1, "name": "Rhyme",
        "definition": "words that end with the same sound",
        "example": "cat / hat, star / far",
        "question": "Are there words that rhyme (end with the same sound)? Read a rhyming pair out loud.",
    },
    "alliteration": {
        "band": 1, "name": "Alliteration",
        "definition": "words close together that start with the same sound",
        "example": "silly snakes slither",
        "question": "Can you find words next to each other that start with the same sound? Say them — do they feel fun or fast?",
    },
    "repetition": {
        "band": 1, "name": "Repetition",
        "definition": "a word or line repeated on purpose for effect",
        "example": "\"Run, run, as fast as you can!\"",
        "question": "Is there a word or line the author repeats? Why do you think they say it more than once?",
    },
    "simile": {
        "band": 1, "name": "Simile",
        "definition": "comparing two things using the words 'like' or 'as'",
        "example": "as brave as a lion; sparkled like stars",
        "question": "Find a comparison that uses 'like' or 'as'. What two things are being compared, and why?",
    },
    "personification": {
        "band": 1, "name": "Personification",
        "definition": "giving human actions or feelings to an animal, thing, or idea",
        "example": "the wind whispered; the sun smiled",
        "question": "Where does something that isn't a person (the wind, the sea, a tree) act like one? What does it do?",
    },
    "imagery": {
        "band": 1, "name": "Imagery (sensory language)",
        "definition": "words that paint a picture for your five senses",
        "example": "the warm, sticky, golden syrup",
        "question": "Find words that let you SEE, HEAR, SMELL, TASTE, or FEEL something. Which sense does it use?",
    },
    # --- Band 2: comparisons & structure (4-6) ---
    "metaphor": {
        "band": 2, "name": "Metaphor",
        "definition": "saying one thing IS another (a comparison without 'like' or 'as')",
        "example": "the classroom was a zoo",
        "question": "Find a spot where the author says one thing IS another. What does the comparison help you understand?",
    },
    "hyperbole": {
        "band": 2, "name": "Hyperbole",
        "definition": "a huge exaggeration you're not meant to take literally",
        "example": "I've told you a million times",
        "question": "Is there a giant exaggeration? What is the author really trying to say by stretching the truth?",
    },
    "idiom": {
        "band": 2, "name": "Idiom",
        "definition": "a phrase that means something different from its literal words",
        "example": "it's raining cats and dogs; break a leg",
        "question": "Find a phrase that doesn't mean exactly what the words say. What does it really mean?",
    },
    "foreshadowing": {
        "band": 2, "name": "Foreshadowing",
        "definition": "hints early on about what will happen later",
        "example": "dark clouds gathering before trouble",
        "question": "Did the author drop a hint about something that happens later? Point to the clue.",
    },
    "symbolism": {
        "band": 2, "name": "Symbolism",
        "definition": "an object or image that stands for a bigger idea",
        "example": "a dove for peace; a road for a journey",
        "question": "Is there an object that seems to stand for something bigger than itself? What idea does it carry?",
    },
    "mood": {
        "band": 2, "name": "Mood & tone",
        "definition": "the feeling the writing gives you, and the author's attitude",
        "example": "spooky, cozy, hopeful, tense",
        "question": "What FEELING does this part give you? Which words create that mood?",
    },
    "point_of_view": {
        "band": 2, "name": "Point of view",
        "definition": "who is telling the story (first person 'I' or third person 'he/she')",
        "example": "\"I ran…\" vs. \"She ran…\"",
        "question": "Who is telling this story? How would it change if a different character told it?",
    },
    # --- Band 3: analysis (7-12) ---
    "irony": {
        "band": 3, "name": "Irony",
        "definition": "when what happens is the opposite of what you'd expect (or what's said)",
        "example": "a fire station burning down",
        "question": "Find a moment of irony — where the outcome is the opposite of what's expected. Why is it powerful here?",
    },
    "allusion": {
        "band": 3, "name": "Allusion",
        "definition": "a reference to another famous story, person, or event",
        "example": "\"He met his Waterloo\"; a Bible reference",
        "question": "Does the author reference another well-known story, person, or event? What does knowing it add?",
    },
    "motif": {
        "band": 3, "name": "Motif",
        "definition": "an image or idea that keeps returning through the whole story",
        "example": "recurring light/dark; a repeated song",
        "question": "What image or idea keeps coming back? Trace it — how does its meaning grow each time?",
    },
    "flashback": {
        "band": 3, "name": "Flashback",
        "definition": "a scene that jumps back to an earlier time",
        "example": "a character remembering their childhood",
        "question": "Does the story jump back in time? What does that memory explain about the character now?",
    },
    "foil": {
        "band": 3, "name": "Foil",
        "definition": "a character whose contrast highlights another character's traits",
        "example": "a reckless friend beside a cautious hero",
        "question": "Is there a character who is the OPPOSITE of the main one? What does the contrast reveal?",
    },
    "satire": {
        "band": 3, "name": "Satire",
        "definition": "using humor or exaggeration to criticize something",
        "example": "a cartoon mocking greed",
        "question": "Is the author poking fun at something to make a point? What are they criticizing?",
    },
    "allegory": {
        "band": 3, "name": "Allegory",
        "definition": "a story whose characters and events stand for bigger real-world ideas",
        "example": "Animal Farm standing for a revolution",
        "question": "Could this whole story stand for something bigger — an idea about life or society? Explain.",
    },
    "theme_device": {
        "band": 3, "name": "Theme",
        "definition": "the deeper universal idea the whole story explores",
        "example": "'love costs something'; 'freedom vs. safety'",
        "question": "State the theme in one sentence. Which scenes prove the author believes it?",
    },
    "figurative": {
        "band": 3, "name": "Figurative language",
        "definition": "language that means more than the literal words (metaphor, symbol, imagery working together)",
        "example": "an extended comparison across a passage",
        "question": "Find a passage rich in figurative language. How do the images work together to create meaning?",
    },
}

DEVICE_ORDER = [
    "onomatopoeia", "rhyme", "alliteration", "repetition", "simile", "personification", "imagery",
    "metaphor", "hyperbole", "idiom", "foreshadowing", "symbolism", "mood", "point_of_view",
    "irony", "allusion", "motif", "flashback", "foil", "satire", "allegory", "theme_device", "figurative",
]

BAND_LABEL = {1: "K–3", 2: "grades 4–6", 3: "grades 7–12"}

STORY_GRAMMAR_INTRO = (
    "The Teaching-the-Classics ladder for the whole story — context, setting, characters, "
    "conflict, plot, theme, and literary devices — at your student's level. Lead these aloud; "
    "there's no single right answer. Use it as a capstone or dip into any element anytime."
)
TOOLBOX_INTRO = (
    "A teacher's toolbox of literary tools at your student's level. Introduce a tool, then go "
    "hunting for it together in the book — reading like a detective is how kids fall in love "
    "with HOW a story is made, not just what happens."
)
LITERATURE_RUBRIC = (
    "## Discussion — how to judge thinking (not agreement)\n\n"
    "- **Grounded:** answers point to specific scenes, details, or quotes.\n"
    "- **Names the tool:** the student can identify the element or device and say what it does.\n"
    "- **Reasoned:** takes a position and supports it; considers another view.\n"
    "- **Connected:** links how the author writes (devices) to what the story means (theme)."
)


def devices_for(level_code):
    """Literary devices appropriate at/below the reader's grade band."""
    band = socratic.band_for_level(level_code)
    return [LITERARY_DEVICES[k] for k in DEVICE_ORDER if LITERARY_DEVICES[k]["band"] <= band]


def toolbox_questions(level_code):
    """[(category, question, hint)] for the Literary Toolbox at this level."""
    out = []
    for device in devices_for(level_code):
        hint = f"{device['name']}: {device['definition']} (e.g. {device['example']})."
        out.append(("style", device["question"], hint))
    return out


def ensure_anchor_lesson(curriculum):
    """A dedicated 'Literature Study' chapter/lesson to hold whole-book seminars."""
    from curricula.models import Chapter, Lesson

    chapter, _ = Chapter.objects.get_or_create(
        curriculum=curriculum, number=900, defaults={"title": "Literature Study"},
    )
    lesson, _ = Lesson.objects.get_or_create(
        chapter=chapter, order=1,
        defaults={"number": None, "title": "Whole-Book Seminar", "lesson_type": Lesson.TYPE_REVIEW},
    )
    return lesson


def apply_literature_standard(curriculum, level_code, *, family=None, anchor_lesson=None):
    """Attach the Socratic Story-Grammar Seminar + Literary Toolbox (teacher-led,
    at ``level_code``) to a literature curriculum. Idempotent. Returns (sets, questions).
    """
    family = family if family is not None else curriculum.family
    lesson = anchor_lesson or ensure_anchor_lesson(curriculum)

    sets = questions = 0
    n = _make_discussion_set(
        lesson, family, "Story-Grammar Seminar", STORY_GRAMMAR_INTRO,
        socratic.questions_for(level_code),
    )
    sets += 1
    questions += n
    band = socratic.band_for_level(level_code)
    # Stable title (band label lives in the intro) so re-applying at a different
    # level updates the single toolbox in place instead of duplicating it.
    toolbox_intro = f"{TOOLBOX_INTRO} (Tuned for {BAND_LABEL[band]}.)"
    n = _make_discussion_set(lesson, family, "Literary Toolbox", toolbox_intro, toolbox_questions(level_code))
    sets += 1
    questions += n

    # Clean up any band-labelled toolbox left by an earlier version/run.
    from tutor.models import QuestionSet

    QuestionSet.objects.filter(lesson=lesson, title__startswith="Literary Toolbox (").delete()
    return sets, questions


def _make_discussion_set(lesson, family, title, intro, questions):
    from tutor.models import Question, QuestionSet

    qset, _ = QuestionSet.objects.update_or_create(
        lesson=lesson, title=title,
        defaults={
            "family": family,
            "intro": intro,
            "rubric": LITERATURE_RUBRIC,
            "status": QuestionSet.APPROVED,
            "mode": QuestionSet.MODE_DISCUSSION,
        },
    )
    for order, (category, prompt, hint) in enumerate(questions, start=1):
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
    qset.questions.filter(order__gt=len(questions)).delete()
    return len(questions)
