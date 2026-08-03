"""Saxon Pre-Algebra Lesson 73 — Functions with Graphing: Nonlinear Functions.

Reviews Lessons 51, 58, 62, 68 and 70 — which means it reviews the y = mx + b work
the parent already taught her by graphing. That is the hook: she does not meet
"nonlinear" cold, she meets it as the cousins of a family she already knows.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_73 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

SEVEN = ["x", "x^2", "x^3", "|x|", "sqrt", "1/x", "a^x"]

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 73 · Pre-Algebra",
        "title": "Not everything goes in a straight line",
        "thesis": "Every function family has a **shape** — a face you learn to "
                  "recognize. Once you know the faces, you can look at a handful of "
                  "points and say which family they came from.",
        "formula": "f(x)  =  y",
        "roles": [
            {"tone": "start", "name": "f(x) is just y",
             "text": "Two names for the same thing. f(x) is not f times x."},
            {"tone": "move", "name": "the shape is the clue",
             "text": "Plot a few points, look at the shape, name the family."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone learns the shapes",
        "paragraphs": [
            "Suppose someone hands you five dots on graph paper and asks what rule "
            "made them. You could guess forever. But if you know what each family "
            "*looks* like, you only have to recognize it — the way you recognize a "
            "friend's face without measuring it.",
            "That is the whole job today. You are not solving anything. You are "
            "learning to **recognize seven shapes**, and then matching a set of "
            "points to the one it belongs to.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 2, "tone": "start",
        "title": "You already know one of the families",
        "paragraphs": [
            "Last time, every function you drew came out a **straight line**. The "
            "*m* tilted it and the *b* slid it up and down, but it was always a line.",
            "That family is `f(x) = x`. Today you meet its cousins — the ones that "
            "**bend**. Same idea as before: put in an x, get out a y, plot the dot. "
            "The only difference is that the dots stop lining up straight.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"You know how y = mx + b always drew a line? These are the other "
                "families — the ones that curve. Same rule, put in x and get out y. "
                "You're just learning what each one looks like.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 2, "tone": "move",
        "title": "The seven faces",
        "paragraphs": [
            "Here they are. Do not memorize them by staring — draw each one once, "
            "then you will know it.",
            "Watch the **left-hand side** of each. That is where the families give "
            "themselves away.",
        ],
    }),

    (B.KIND_TOOL, {
        "title": "The family album",
        "intro": "Tap each shape to draw it. Look at what the left side does.",
        "widget": "grid",
        # `reference` — this one is a gallery, not an exercise. Without it, every
        # tap answered "plot the points from the table first" for a block that
        # has no table.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "choices": SEVEN, "reference": True,
                   "label": "the seven function shapes"},
        "after": "`x` is the straight one you already know. `x²` makes a U. `x³` "
                 "makes an S. `|x|` makes a sharp V. `√x` only exists on the right. "
                 "`1/x` is two pieces that never touch the axes. `aˣ` creeps along "
                 "and then explodes.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Three moves, every time",
        "steps": [
            {"label": "Draw the axes yourself.",
             "detail": "Rough is fine. Saxon says so, and it is true — a sketch you "
                       "drew tells you more than a perfect one you didn't."},
            {"label": "Plot every point in the table.",
             "detail": "Across first, then up or down. (x, y) — x is the one that "
                       "comes first, and it goes sideways."},
            {"label": "Look at the shape and name the family.",
             "detail": "Do not join the dots with straight lines. Let your eye see "
                       "the curve they are sitting on."},
        ],
        "after": "Then check the **left-hand side** — that is where x² and x³ part "
                 "company, and it is the mistake almost everyone makes.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 73.1 — where do these points come from?",
        "equation": "(-2, 4)   (-1, 1)   (0, 0)   (1, 1)   (2, 4)",
        "steps": [
            {"label": "Look first",
             "text": "Nothing is drawn yet. Read the table. Notice the y values: "
                     "4, 1, 0, 1, 4. They come **down** to zero and go back **up**."},
            {"label": "Step 1 · plot them",
             "text": "Put all five dots on the grid. Take your time with the "
                     "negative x values — those are the ones that tell you the most."},
            {"label": "Step 2 · look at the shape",
             "text": "Both arms point **up**. The bottom is round, sitting at the "
                     "origin. It is symmetric — the left side mirrors the right."},
            {"label": "Step 3 · name it",
             "text": "That is a **U**. The family is `f(x) = x²`.",
             "math": "check: (-2)² = 4 ✓   (-1)² = 1 ✓   2² = 4 ✓"},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "Now you do it",
        "intro": "Plot these five points, then pick the family you think they belong "
                 "to. The true curve will draw itself through your dots — or miss "
                 "them, which tells you just as much.",
        "widget": "grid",
        # y runs to +-9 because the table reaches -8 and 8. A 6-high grid would
        # have asked her to plot a point that is not on the paper.
        "config": {"view": {"xmin": -9, "xmax": 9, "ymin": -9, "ymax": 9},
                   "choices": SEVEN, "table": [[-2, -8], [-1, -1], [0, 0], [1, 1], [2, 8]],
                   "label": "plot the table and name the family"},
        "after": "Table: **(-2, -8)  (-1, -1)  (0, 0)  (1, 1)  (2, 8)**. "
                 "Use the pen if you want to sketch your guess first.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Which family was that second table?",
        "answer": "`f(x) = x³`. The giveaway is the **left-hand side**: it goes "
                  "*down* to −8, while x² would have sent it *up* to +4. "
                  "An S shape through the origin, not a U.",
    }),

    (B.KIND_TABLE, {
        "caption": "x² and x³ agree on the right and disagree on the left",
        "headers": ["x", "x²", "x³"],
        "rows": [
            {"cells": ["-2", "4", "-8"], "emphasis": True},
            {"cells": ["-1", "1", "-1"], "emphasis": True},
            {"cells": ["0", "0", "0"]},
            {"cells": ["1", "1", "1"]},
            {"cells": ["2", "4", "8"]},
        ],
        "note": "The shaded rows are the whole difference. On the right they look "
                "the same; on the **left** one goes up and the other goes down.",
    }),

    (B.KIND_TRANSLATION, {
        "title": "What f(x) actually means",
        "intro": "Saxon starts writing `f(x)` where it used to write `y`. Nothing "
                 "new is happening — it is the same thing with a different label.",
        "rows": [
            {"symbol": "y = x²", "plain": "put in x, get out y", "example": "y = 9 when x = 3"},
            {"symbol": "f(x) = x²", "plain": "the same sentence", "example": "f(3) = 9"},
            {"symbol": "f(3)", "plain": "what comes out when x is 3", "example": "9"},
        ],
        "after": "`f(x)` is **not** f times x. The f is the name of the machine and "
                 "the x is what you feed it.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Joining the dots with straight lines.",
             "wrong": "five dots + a ruler → \"it's linear\"",
             "right": "five dots → let your eye find the curve",
             "note": "Five points are five clues, not a picture. That is exactly "
                     "why the tool above draws the real curve afterwards."},
            {"name": "Confusing x² and x³.",
             "wrong": "(-2, -8) → x²",
             "right": "(-2, -8) → x³",
             "note": "**Check the negative side.** x² sends both arms up. x³ sends "
                     "the left arm down. That one check settles it every time."},
            {"name": "Confusing |x| with x².",
             "wrong": "a V → x²",
             "right": "a V → |x|",
             "note": "A V has a **sharp corner** at the bottom. A parabola is round."},
            {"name": "Plotting (x, y) backwards.",
             "wrong": "(2, 4) → across 4, up 2",
             "right": "(2, 4) → across 2, up 4",
             "note": "x comes first in the pair and first on the alphabet. Across, "
                     "then up."},
            {"name": "Reading f(x) as multiplication.",
             "wrong": "f(3) = f × 3",
             "right": "f(3) = the output when x is 3",
             "note": "See the Translation section above."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "`f(x)` and `y` are the same thing.",
            "Plot the points, then look — do **not** join them with straight lines.",
            "**The left-hand side is the discriminator.** x² goes up on both sides; "
            "x³ goes down on the left.",
            "A V is sharp. A U is round.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 73 first. If it didn't quite click, this is here to fix "
    "that — and to let you play with it. You already know one function family: the "
    "straight lines from y = mx + b. Today you meet the ones that bend, and learn "
    "to recognize each one by its shape."
)

PARENT_CONTENT = """## The big idea

She has to **recognize seven shapes** and match a table of points to one of them.
That is the whole lesson — no solving, no algebra. It is a visual memory task
wearing a maths hat, and it goes much better if you treat it that way.

The hook that makes it feel connected rather than random: *every function she has
graphed so far came out a straight line.* Those were all one family. Today she
meets the cousins.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. **"What did every graph you drew last week look like?"** — wait for "a line."
   *"Right. All of those were one family. Today you meet the ones that bend."*
2. Draw axes. Say **"Give me a number."** Square it out loud, plot the dot. Do it
   for 2, then −2. *"Look — both went UP."*
3. Now cube the same two. *"This time the negative one went DOWN. That's the
   difference. That's the whole trick."*
4. Show her the V of |x| and the U of x². **"What's different?"** — you want
   "one's pointy." That is the right answer and it is enough.
5. Hand her the second table and let her use the tool. **Do not** tell her the
   answer; let the curve draw itself through her dots.

## The classic mix-ups, with what she'll actually write

- **x² and x³ confused.** She sees (−2, −8) and writes x². The fix is not "be
  careful" — it is one habit: **always look at the negative side first.** x²
  sends both arms up, x³ sends the left arm down.
- **Joining the dots with a ruler**, then announcing it is linear. Five points
  are five clues, not a picture.
- **A V called a parabola.** A V has a sharp corner. Ask her to trace the bottom
  with her finger — she will feel the difference.
- **Plotting (2, 4) as across 4, up 2.** Very common under time pressure.
- **Reading f(3) as "f times 3."** If she does this once she will do it for a
  year. Correct it the first time: f is the *name of the machine*.

## What to watch her do

Not whether she gets the right family — whether she **checks the left-hand side**
before answering. That single habit is what this lesson is buying, and it is
visible from across the table: does she look at the negative x values, or does she
answer from the right half of the graph alone?

## Help her hands-on

Graph paper and a pencil beat the screen for this one, at least once. Have her
draw all seven shapes on a single sheet and pin it up. Making the reference is
what memorizes it; owning one someone else made does nothing.

## Extend it

Give her a table that fits **more than one** family — say just (0, 0) and (1, 1),
which fits x, x², x³, |x| and √x all at once — and ask which it is. The right
answer is *"you can't tell yet, give me another point."* That is a genuinely
valuable thing for a 12-year-old to be able to say, and the tool backs her up: if
her points still fit several families it names them and asks for another point,
rather than picking one and calling her wrong.

## Where this sits

DIVE Lesson 73. Reviews Lessons 51, 58, 62, 68 and 70 — if she is lost, 68 and 70
are the ones to revisit, because they are the y = mx + b graphing you already did
together.

**Proficient** looks like: names x², x³ and |x| correctly from a table, given time.
**Mastered** looks like: does it quickly, and *says why* — "the left side goes
down, so it's cubed."
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 73 (nonlinear functions) — idempotent."

    LESSON_NUMBER = 73
    TITLE = "Not Everything Goes in a Straight Line — Nonlinear Functions"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
