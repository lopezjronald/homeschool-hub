"""Saxon Pre-Algebra Lesson 71 — Proportion Word Problems, Part II:
Ratios Involving Totals, Including Percent. Reviews Lessons 16, 37, 66.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_71 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 71 · Pre-Algebra",
        "title": "When the ratio doesn't tell you how many",
        "thesis": "A ratio tells you the size of the **slices**. Add the slices "
                  "together and you get the **whole pizza** — and that total is the "
                  "number this lesson is really about.",
        "formula": "3 : 4   →   total 7",
        "roles": [
            {"tone": "move", "name": "the parts",
             "text": "3 red for every 4 blue. Not 3 hats — 3 for every 4."},
            {"tone": "start", "name": "the total",
             "text": "3 + 4 = 7. Out of every 7 hats, 3 are red."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why you'd ever need this",
        "paragraphs": [
            "Someone tells you the school store has 3 red hats for every 4 blue "
            "ones. That does **not** tell you how many hats there are. There could "
            "be 7, or 70, or 700 — the ratio is the same either way.",
            "But the moment somebody counts *one* real number — say, 60 red hats — "
            "the ratio locks everything else in place. This lesson is how you get "
            "from that one real number to any of the others, including the total.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 2, "tone": "start",
        "title": "The total is hiding in the ratio already",
        "paragraphs": [
            "3 : 4 does not just mean \"3 red, 4 blue.\" It also means the hats come "
            "in **groups of 7** — 3 red and 4 blue in every group.",
            "That 7 is the number you were never given but always had. Write it down "
            "**first**, before you touch anything else. Almost every mistake in this "
            "lesson comes from skipping that one line.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Three reds and four blues — how many hats is that altogether? "
                "Seven. Good. So every time you grab a group, you're grabbing seven "
                "hats. Write the seven down.\"",
    }),

    (B.KIND_TABLE, {
        "caption": "The ratio box — the total row is the whole lesson",
        "headers": ["", "Ratio", "Actual"],
        "rows": [
            {"cells": ["Red", "3", "60"]},
            {"cells": ["Blue", "4", "?"]},
            {"cells": ["TOTAL", "7", "?"], "emphasis": True},
        ],
        "note": "Fill the Ratio column from the problem. Fill in the one Actual "
                "number you were given. Add the ratio column to get the total row — "
                "then the box tells you what to compare with what.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 2, "tone": "move",
        "title": "One group is worth the same everywhere",
        "paragraphs": [
            "If 3 ratio-units of red are worth 60 real hats, then **one** ratio-unit "
            "is worth 20. And if one unit is worth 20, then all 7 units are worth "
            "140.",
            "That is the whole calculation. The proportion is just a tidy way of "
            "writing it down.",
        ],
    }),

    (B.KIND_TOOL, {
        "title": "Slide it until the red row says 60",
        "intro": "Every row moves together, because every row is the same number of "
                 "groups. Watch what the TOTAL does.",
        "widget": "ratiobar",
        "config": {
            "parts": [{"name": "Red", "ratio": 3, "tone": "move"},
                      {"name": "Blue", "ratio": 4, "tone": "start"}],
            "target": {"name": "Red", "actual": 60},
            "maxScale": 25, "scale": 1,
        },
        "after": "Notice you never chose the total — it came along for the ride. "
                 "That is what makes this work.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe (from Lesson 16)", "title": "Three questions, every time",
        "steps": [
            {"label": "What am I solving for?",
             "detail": "Say it in words and give it a letter. *The total number of "
                       "hats, T.* Include the unit — you will need it at the end."},
            {"label": "What do I know?",
             "detail": "Fill the box. Ratio column from the problem, the one Actual "
                       "number you were given, then **add the ratio column** to get "
                       "the total row."},
            {"label": "Set up the proportion, cross multiply, solve.",
             "detail": "Match the row you know against the row you want.",
             "math": "3/7 = 60/T"},
        ],
        "after": "Then check the unit. *140* is not an answer. *140 hats* is.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 71.1 — 3 red for every 4 blue, and 60 reds. How many hats?",
        "equation": "red : blue  =  3 : 4        60 reds",
        "steps": [
            {"label": "Step 1 · what am I solving for?",
             "text": "The **total** number of hats. Call it T."},
            {"label": "Step 2 · what do I know?",
             "text": "Red is 3, blue is 4, so a group is 7. And 3 ratio-units of red "
                     "are 60 real hats.",
             "math": "Red 3 → 60    Blue 4 → ?    TOTAL 7 → T"},
            {"label": "Step 3 · match the row I know to the row I want",
             "text": "Red against total, on both sides.",
             "math": "3/7 = 60/T"},
            {"label": "Cross multiply",
             "text": "Multiply across the diagonals.",
             "math": "3T = 7 × 60 = 420"},
            {"label": "Solve, and say the unit",
             "text": "Divide both sides by 3.",
             "math": "T = 420 / 3 = 140 hats"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "71.2",
        "question": "Water is 8 parts oxygen to 1 part hydrogen by mass. In 270 g of water, how much is hydrogen?",
        "steps": [
            {"label": "Solving for", "text": "The **mass of the hydrogen**, in grams."},
            {"label": "The trap", "text": "The 270 g is the *water* — and water is the "
                                          "**total**, because it is the oxygen and the "
                                          "hydrogen put together."},
            {"label": "The box", "math": "O 8    H 1    TOTAL 9 → 270 g"},
            {"label": "Proportion", "math": "1/9 = H/270"},
            {"label": "Cross multiply and solve", "math": "9H = 270    →    H = 30"},
        ],
        "answer": "30 grams of hydrogen",
    }),

    (B.KIND_WORKED, {
        "number": "71.3",
        "question": "A bag holds apples and oranges. 20% are apples. There are 32 oranges. How many pieces of fruit altogether?",
        "steps": [
            {"label": "First move", "text": "If 20% are apples then **80% are "
                                            "oranges** — percents in a bag always add "
                                            "to 100. Write that down before anything "
                                            "else."},
            {"label": "The box", "math": "apples 20%    oranges 80% → 32    TOTAL 100% → T"},
            {"label": "Proportion", "math": "80/100 = 32/T"},
            {"label": "Cross multiply and solve", "math": "80T = 3200    →    T = 40"},
        ],
        "answer": "40 pieces of fruit",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Why is the percent version the same lesson?",
        "answer": "Because **100 is just the total**. A percent problem already hands "
                  "you the total row — it is always 100 — so you only have to work out "
                  "the missing part. `20 : 80` and `1 : 4` are the same ratio; the "
                  "percent version has simply already added them up for you.",
    }),

    (B.KIND_ERRORS, {
        "title": "The four mistakes almost everyone makes",
        "items": [
            {"name": "Comparing a part to the OTHER part instead of to the total.",
             "wrong": "3/4 = 60/T  →  T = 80",
             "right": "3/7 = 60/T  →  T = 140",
             "note": "This is the big one, and it is dangerous because **80 feels "
                     "fine**. Nothing about it looks wrong. The only defence is "
                     "writing the total row down before you set up anything."},
            {"name": "Forgetting the other percent.",
             "wrong": "20% apples, 32 oranges  →  20/100 = 32/T",
             "right": "20% apples means 80% oranges  →  80/100 = 32/T",
             "note": "Write the complement the moment you read the percent."},
            {"name": "Cross multiplying the wrong diagonal.",
             "wrong": "3/7 = 60/T  →  3 × 60 = 7T",
             "right": "3/7 = 60/T  →  3 × T = 7 × 60",
             "note": "Top-left times bottom-right, top-right times bottom-left. Draw "
                     "the X with your finger if it helps."},
            {"name": "Answering with a bare number.",
             "wrong": "T = 30",
             "right": "30 grams of hydrogen",
             "note": "Saxon takes marks for this, and it is a good habit anyway — "
                     "*30 what?*"},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Add the ratio parts first.** 3 : 4 means groups of 7.",
            "The number you were given goes in the Actual column next to its own "
            "ratio number.",
            "Compare the row you **know** with the row you **want** — usually a part "
            "against the total.",
            "A percent problem already has its total: it is 100.",
            "Finish with the unit.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 71 first. If it didn't quite click, this is here to fix "
    "that. The whole lesson is one move: a ratio like 3 : 4 secretly tells you "
    "about groups of 7 — and once you write that 7 down, everything else falls out."
)

PARENT_CONTENT = """## The big idea

A ratio gives the **relative** sizes of the parts. Adding the parts gives the size
of a whole *group*, and that group total is what you compare against when the
question asks for a total.

- **3 : 4, and 60 reds.** Ratio total 7. So `3/7 = 60/T`, `3T = 420`, **T = 140 hats**.
- **O : H = 8 : 1 by mass, 270 g of water.** Water *is* the total. `1/9 = H/270`,
  **H = 30 g**.
- **20% apples, 32 oranges.** So 80% oranges. `80/100 = 32/T`, **T = 40**.

## Teach it out loud in five minutes

1. Put three red things and four blue things on the table. **"How many altogether?"**
   — seven. *"That's a group. Every time we get more hats, we get another group of
   seven."*
2. Make a second group. **"How many red now? How many altogether?"** — 6 and 14.
3. *"So if I told you there were 60 red hats, how many groups is that?"* — twenty.
   **"And how many hats?"** — she can often get 140 with no algebra at all.
4. Now show the box, and say: *"The algebra is just how we write down what you
   already did."* That order matters — the intuition first, the notation second.
5. For the percent one, ask only: **"If 20% are apples, what are the rest?"** That
   single question is the whole difficulty.

## The classic mix-ups, with what she'll actually write

- **`3/4 = 60/T` giving 80.** She compares red to blue instead of red to total. It
  is the most common error in the lesson and it is nasty because **80 looks
  perfectly reasonable** — there is nothing to catch her eye. The fix is a habit,
  not a check: write the TOTAL row before setting up the proportion.
- **Using 20 instead of 80** in the percent problem.
- **Cross multiplying the wrong diagonal.**
- **Answering "30"** instead of "30 grams." Saxon marks this.

## What to watch her do

Not the answer — **whether she writes the total row first.** If she starts writing
a proportion before that row exists, stop her there. That is the entire lesson, and
it is visible from across the table.

## Help her hands-on

Use actual objects for the first one. Ratios are one of the last topics where
physical grouping still helps a 12-year-old, and grouping 3-and-4 into a bundle of
7 makes the "total" idea obvious in a way the box never will on its own.

## Extend it

Give her a problem where she is told the **total** and asked for a part — the
reverse direction. Then one where the ratio has three parts (2 : 3 : 5, total 10),
which is the same move and looks much harder until she tries it.

## Where this sits

DIVE Lesson 71. Reviews Lessons 16 (the three-question routine), 37 and 66 (setting
up and solving proportions). If she is lost on the *setup* rather than the total,
Lesson 66 is the one to revisit.

**Proficient**: gets the total right with the box in front of her.
**Mastered**: writes the total row unprompted, and catches herself when a part-to-part
setup would have been easier to write.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 71 (ratios with totals) — idempotent."

    LESSON_NUMBER = 71
    TITLE = "When the Ratio Doesn't Tell You How Many — Ratios with Totals"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
