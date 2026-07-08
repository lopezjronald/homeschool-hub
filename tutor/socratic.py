"""The Socratic question standard — CenterForLit "Teaching the Classics" ladder.

A generic, book-agnostic list of story-grammar questions, graded by depth so it
can be applied to ANY story at the reader's level. This is the reusable
foundation for literature discussion across every book and grade; individual
book seeds add novel-specific questions on top of these.

Each element maps to a Question.category. Each question is (code, band, text):
- ``code``  — its number in the Teaching the Classics Socratic List (provenance).
- ``band``  — depth: 1 = early elementary, 2 = upper elementary, 3 = middle school+.
- ``text``  — a kid-facing wording of the question.

Story-grammar elements: Context · Setting · Characters · Conflict · Plot ·
Theme · Literary Devices (style).
"""

# element key -> Question.category (see tutor.models.Question.CATEGORY_CHOICES)
ELEMENT_CATEGORY = {
    "context": "context",
    "setting": "setting",
    "characters": "character",
    "conflict": "conflict",
    "plot": "plot",
    "theme": "theme",
    "devices": "style",
}

ELEMENT_ORDER = ["context", "setting", "characters", "conflict", "plot", "theme", "devices"]

ELEMENT_HINT = {
    "context": "Ground it before you read: who wrote it, when, and what was the world like then?",
    "setting": "Setting is more than a place — it's the time, the weather, the mood, and the kind of people.",
    "characters": "Describe who a character IS (traits), then point to what they say and do that proves it.",
    "conflict": "Every story is a struggle. Name what the main character wants and what stands in the way.",
    "plot": "Walk the story chart: exposition → rising action → climax → falling action → resolution.",
    "theme": "Theme is the big idea the whole story is really about — a truth it wants you to feel.",
    "devices": "How did the author build it? Look for symbols, foreshadowing, irony, and word-music.",
}

SOCRATIC_LIST = {
    "context": [
        ("18", 1, "Who wrote this story?"),
        ("20a", 2, "When did the author live? What was happening in the world then?"),
        ("19a", 2, "Where did the author live? Might that have shaped the story?"),
        ("21", 3, "What do you think the author believed about people or the world? What in the story shows it?"),
    ],
    "setting": [
        ("1b", 1, "Where does the story happen — the country, the city, or somewhere else?"),
        ("2c", 1, "In what season does the story take place? How can you tell?"),
        ("1d", 2, "What is the mood of the place — cheerful and sunny, or dark and bleak? Which words create that feeling?"),
        ("1h", 2, "Among what kind of people is the story set? Are they hopeful or downtrodden — and why?"),
        ("2e", 2, "In what time of life are the main characters — children, teenagers, or grown-ups?"),
        ("1f", 3, "Would you want to climb into this book and live in its world, or does it repel you? Why?"),
    ],
    "characters": [
        ("3", 1, "Who is the story mostly about? Who is the main character (the protagonist)?"),
        ("3d", 1, "What does the main character look like?"),
        ("3f", 2, "List words that describe the main character. What things they say or do make you choose those words?"),
        ("3k", 2, "What do the other characters think or say about the main character?"),
        ("4a", 2, "Is there a character who works against the main character (an antagonist)? Who, and how?"),
        ("3i", 3, "How has the main character grown or changed by the end? What changed them?"),
    ],
    "conflict": [
        ("5a", 1, "Finish the sentence: this story is about the main character trying to ______."),
        ("6a", 1, "Why can't the main character get what they want right away? What's in the way?"),
        ("5c", 2, "Is the struggle with something OUTSIDE the character (a person, nature, danger)?"),
        ("5e", 2, "Is there a struggle INSIDE the character — in their mind or heart? Describe it."),
        ("5f", 3, "Do the character's goals change during the story? How, and why?"),
        ("6h", 3, "How would you name the main conflict — person vs. person, vs. self, vs. nature, vs. society, or vs. fate?"),
    ],
    "plot": [
        ("8a", 1, "What are the big events that happen because of the conflict (the rising action)?"),
        ("9a", 1, "How is the main problem finally solved? Does the character get what they were after?"),
        ("8d", 2, "What outside forces — weather, a journey, sickness, war, a season — crank up the tension?"),
        ("10", 2, "What is the CLIMAX — the turning-point moment the whole story builds toward?"),
        ("9e", 2, "Does the main character solve their own problem, or does someone help?"),
        ("10d", 3, "How does the ending change each character? Who is different, and how?"),
    ],
    "theme": [
        ("13a", 1, "In one sentence, what is the big idea this story is really about?"),
        ("11e", 2, "Where does a character say out loud what they've learned or what they believe?"),
        ("13d", 3, "What answer does this story suggest to the question, 'What is a good life?'"),
        ("13g", 3, "Do you agree with what the story seems to say is true? Why or why not?"),
    ],
    "devices": [
        ("14a", 1, "Does the author use fun sounds — words that sound like what they mean (onomatopoeia), or repeated sounds?"),
        ("16e", 2, "Does the author give human feelings to animals or things (personification)? Where?"),
        ("17h", 2, "Does the author drop hints about what's coming later (foreshadowing)? Find one."),
        ("17a", 3, "What SYMBOLS appear — objects or images that stand for a bigger idea? What do they mean?"),
        ("17d", 3, "Is there IRONY — where what happens is the opposite of what you'd expect? Where?"),
        ("22a", 3, "What GENRE is this (adventure, fantasy, realistic fiction, historical)? How can you tell?"),
    ],
}


def band_for_level(level_code):
    """Map a Student.grade_level code (e.g. 'G03', 'G07') to a depth band 1-3."""
    try:
        n = int(str(level_code).lstrip("G") or 0)
    except (TypeError, ValueError):
        n = 4
    if n <= 3:
        return 1
    if n <= 6:
        return 2
    return 3


def questions_for(level_code, elements=None, include_deeper=True):
    """Return [(category, text, hint)] from the standard for a reader's level.

    Includes every question whose band is at or below the reader's band (so a
    7th grader also revisits the foundational questions). Pass ``elements`` to
    limit which story-grammar elements are covered.
    """
    band = band_for_level(level_code)
    picked = []
    for element in (elements or ELEMENT_ORDER):
        rows = SOCRATIC_LIST.get(element, [])
        hint = ELEMENT_HINT.get(element, "")
        category = ELEMENT_CATEGORY.get(element, "theme")
        for _code, qband, text in rows:
            if qband <= band or (include_deeper and qband == band + 1 and band >= 2):
                picked.append((category, text, hint))
    return picked
