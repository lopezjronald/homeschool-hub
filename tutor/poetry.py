"""Poetry: Small Forms — Blackbird & Company, for Kaylin.

Twelve small forms of poetry, one section each. Every section runs the same way:
a definition with the form's exact syllable pattern, a worked example in the
author's own handwriting, then YOUR TURN — craft a sentence, count the
syllables, edit to fit, break it with the poetic slash, and write out the final
poem on a LINE # / SYLLABLES grid.

TWO THINGS CARRY THIS CURRICULUM, and only one of them is code.

1. THE ORIGINAL PAGES ARE ATTACHED. Each section's spread is exported to
   static/poetry/<slug>/p1.jpg… and linked from her page. The guide's character
   is in its handwriting — the drafts, the struck-out words, the slashes drawn
   in by hand — and that cannot be recreated in HTML. She reads the real thing.

2. THE GRID IS BUILT. What the app CAN do better than paper is hold her to the
   form: one ruled line per line of the poem, each labelled with its target, and
   a live syllable count as she writes. `pattern` is that grid. A form with no
   syllable rule (gogyohka, free verse) carries a line count and no targets.

Transcribed by reading the rendered pages; the syllable tables come from each
section's own DEFINITION block, which is why they are exact rather than the
counts poetry sites usually quote.
"""

CURRICULUM_NAME = "Poetry: Small Forms"

EPIGRAPH = ("A poem begins in delight and ends in wisdom.", "Robert Frost")

# The guide's own framing, from "How This Guide is Organized".
HOW_IT_RUNS = (
    "Each section introduces one small form: what it is, where it came from, a "
    "worked example, and then your turn. The method is always the same — begin "
    "with a sentence, count its syllables, edit until it fits the form, then use "
    "the poetic slash to decide where the lines break."
)

POETIC_SLASH = (
    "When beginning ideas in the form of a sentence, the slash / is used to "
    "delineate where line breaks happen."
)

SECTIONS = [
    {
        "number": 1, "slug": "haiku", "name": "haiku", "subtitle": "writing nature",
        "pages": 5,
        "definition": "Haiku is a Japanese poetic form of 17 syllables — 3 lines "
                      "of 5, 7, and 5 syllables each. It is recognized by its "
                      "specific syllabic form and characterized by evoking "
                      "imagery from nature and focusing on a single moment in "
                      "time. While the rules have been bent a bit for English "
                      "translation, haiku is traditionally one thought.",
        "pattern": [5, 7, 5],
    },
    {
        "number": 2, "slug": "tanka", "name": "tanka", "subtitle": "celebrating mood",
        "pages": 5,
        "definition": "Tanka is a Japanese poem consisting of 5 lines. Lines 1 "
                      "and 3 each have 5 syllables, the remaining lines 2, 4, and "
                      "5, each have 7 syllables, for a total of 31, and giving a "
                      "complete picture of an event or mood. Traditional tanka "
                      "are one complete sentence and focus on human experience "
                      "and emotion.",
        "pattern": [5, 7, 5, 7, 7],
    },
    {
        "number": 3, "slug": "sijo", "name": "sijo", "subtitle": "singing poetic",
        "pages": 5,
        "definition": "Sijo is an ancient Korean poetic form, older even than "
                      "haiku. Sijo is a lyrical 3 line poem akin to a song. Each "
                      "line serves a specific purpose. Line 1 introduces the "
                      "theme (or topic), line 2 develops it and offers a turn (or "
                      "surprise), line 3 completes the theme (or topic), and "
                      "offers a twist.",
        # The guide gives an approximate meter totalling 45 rather than a fixed
        # count, so the grid shows a target range instead of a number.
        "pattern": [15, 15, 15],
        "approximate": True,
        "line_roles": ["introduce the theme", "develop it, and turn",
                       "complete it, with a twist"],
    },
    {
        "number": 4, "slug": "lune", "name": "lune", "subtitle": "american variation",
        "pages": 4,
        "definition": "Lune, better known as the American haiku, was first "
                      "created by the poet Robert Kelly in the 1960s. It is "
                      "similar to haiku but follows a syllabic pattern that "
                      "curves the opposite direction. Line 1 is 5 syllables, line "
                      "2 is 3 syllables, and line 3 is 5 syllables — 13 total. "
                      "With the middle line being shorter than the other two when "
                      "written out, the lune forms a crescent moon shape.",
        "pattern": [5, 3, 5],
    },
    {
        "number": 5, "slug": "cinquain", "name": "cinquain", "subtitle": "moody images",
        "pages": 4,
        "definition": "A cinquain is a five-line poem following a specific, "
                      "syllabic pattern. Each line steadily grows, leading the "
                      "reader to an abrupt ending. The poem should tell a story "
                      "which builds to a climax in the final two lines.",
        "pattern": [2, 4, 6, 8, 2],
    },
    {
        "number": 6, "slug": "senryu", "name": "senryū", "subtitle": "human interest",
        "pages": 4,
        "definition": "Senryū is inspired by haiku, following the same 3 line, 17 "
                      "syllable line break pattern (5-7-5). But a senryū focuses "
                      "on a human subject instead of nature and is often humorous. "
                      "Senryū poems are often rich with lively comedy.",
        "pattern": [5, 7, 5],
    },
    {
        "number": 7, "slug": "tricube", "name": "tricube", "subtitle": "whimsical threes",
        "pages": 5,
        "definition": "Tricube is a 3 stanza poem. Each of the 3 stanzas has 3 "
                      "lines, and each line has 3 syllables, for a total of 27 "
                      "syllables — simple math!",
        "pattern": [3] * 9,
        "stanza_every": 3,
    },
    {
        "number": 8, "slug": "nonet", "name": "nonet", "subtitle": "countdown syllables",
        "pages": 4,
        "definition": "A nonet is a nine-line poem with a decreasing number of "
                      "syllables in each line. Starting with 9 syllables in line "
                      "1, and ending with 1 syllable in line 9, it has a total of "
                      "45 syllables.",
        "pattern": [9, 8, 7, 6, 5, 4, 3, 2, 1],
    },
    {
        "number": 9, "slug": "shadorma", "name": "shadorma", "subtitle": "little syllables",
        "pages": 5,
        "definition": "Each stanza of a shadorma is made up of 6 lines — a sestet "
                      "— and can be repeated in as many stanzas as the poet wants. "
                      "Each line of the sestet follows the following syllabic "
                      "pattern, totaling 25.",
        # The guide prints 3-4-3-3-7-5 = 25 (verified on its own page); the
        # widely-quoted shadorma is 3-5-3-3-7-5 = 26. The book wins here, per
        # the house convention of following the printed guide.
        "pattern": [3, 4, 3, 3, 7, 5],
    },
    {
        "number": 10, "slug": "gogyohka", "name": "gogyohka", "subtitle": "one phrase",
        "pages": 4,
        "definition": "Gogyohka is a 5 line poem similar to the tanka but with no "
                      "syllabic restriction. Each line is simply one complete "
                      "idea.",
        # No syllable rule — five lines, one idea each.
        "pattern": [None] * 5,
    },
    {
        "number": 11, "slug": "sevenling", "name": "sevenling", "subtitle": "little twist",
        "pages": 5,
        "definition": "A sevenling is a seven-line poem divided into three "
                      "stanzas. Lines 1-3 form one stanza and should contain a "
                      "list of three things expressing one idea. Lines 4-6 form "
                      "the second stanza and should contain another list of "
                      "three, forming a second thought. Line 7 forms the third "
                      "stanza and should be the twist of the poem, an unexpected "
                      "reveal or surprise.",
        "pattern": [None] * 7,
        "line_roles": ["first of three", "second of three", "third of three",
                       "first of three", "second of three", "third of three",
                       "the twist"],
    },
    {
        "number": 12, "slug": "free-verse", "name": "free verse",
        "subtitle": "image snapshots", "pages": 4,
        "definition": "Free verse poetry is formed with sentences that are broken "
                      "into snapshots of imagery at points where the poet feels is "
                      "appropriate. With this form, a single sentence, broken into "
                      "short lines, forms a single stanza. These poems have no "
                      "rhyme scheme and no fixed meter. Free verse poems create "
                      "artistic moments with image and sound.",
        # She decides the shape; the grid gives room without prescribing it.
        "pattern": [None] * 6,
        "free_shape": True,
    },
]

# Day-3 style prompts the guide offers when nothing comes.
STARTERS = [
    "COURAGE is a lion…", "JOY is a flame…", "IDEAS are water…",
    "PEACE is a cumulus cloud…", "KINDNESS is a garden blooming…",
    "SELFISHNESS is a stone…",
]


def section_by_number(number):
    return next((s for s in SECTIONS if s["number"] == number), None)


def total_syllables(section):
    counts = [n for n in section["pattern"] if n]
    return sum(counts) if counts else None


def page_images(section):
    """The original guide pages for this section, as static paths."""
    return ["poetry/%s/p%d.jpg" % (section["slug"], n)
            for n in range(1, section["pages"] + 1)]
