"""Saxon Pre-Algebra Lesson 80 — More on Linear Functions: Horizontal and
Vertical Lines.

Reviews Lessons 12, 23, 68, 70, 73, 74, 77 and 79. Lesson 12 is the one that
matters most here: horizontal, vertical, perpendicular. Everything else in the
lesson is one sentence long.

This is the lesson the father asked for by name. He could teach substituting x
and reading off y; he could not teach "the slope intercept technique." The answer
this lesson gives is a relief rather than a new technique — for these two lines
you do not use y = mx + b at all. You read one number off one axis and write it
down.

Two of Saxon's three examples are diagrams (80.1 is a lettered figure, 80.2 and
80.3 are graphs). The figures are not in the digitized text, so 80.1 is restated
as endpoint COORDINATES that give Saxon's own answers — AE and LJ horizontal, BK
vertical — and 80.2 / 80.3 describe their graphs in words, keeping the source's
numbers (y = 4, x = 1, x = -2, Choice B) exactly.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Practice problems are reworded rather than transcribed.

    python manage.py seed_saxon_80 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 80 · Pre-Algebra",
        "title": "The two lines you don't need y = mx + b for",
        "thesis": "A flat line and an upright line are each **one number long**. "
                  "Find the number where the line crosses an axis, write the letter "
                  "that never changes in front of it, and you are finished.",
        "formula": "y = b        x = c",
        "roles": [
            {"tone": "start", "name": "flat  →  y = b",
             "text": "Every point sits at the same height. Slope 0. Read the number "
                     "off the y-axis."},
            {"tone": "move", "name": "upright  →  x = c",
             "text": "Every point sits the same distance across. Slope undefined. "
                     "Read the number off the x-axis."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why these two lines get their own rule",
        "paragraphs": [
            "Think about a thermostat holding a room at 68 degrees. An hour goes by, "
            "then another, then another — and the temperature does not move. If you "
            "graph that, the dots march sideways at the same height forever. That is "
            "a **horizontal** line: something that refuses to change no matter how "
            "much of the other thing you pile on.",
            "Now think about a wall. Every brick in it is the same distance from the "
            "front door — the bottom brick, the top brick, all of them. Only the "
            "height changes. That is a **vertical** line: one place, all the way up.",
            "Up to now every line you have graphed was **slanted** — it went across "
            "*and* up. Saxon calls a slanted line **oblique**, and `y = mx + b` was "
            "built for oblique lines. These two are not oblique, and here is the good "
            "news your video did not stop to say out loud: **you do not use "
            "y = mx + b for them at all.** No m to work out, no b to hunt for, no "
            "substituting. You find one number and you write it down.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Three kinds of line, and only one of them is complicated",
        "paragraphs": [
            "**Horizontal** means flat — left to right across the page, like the "
            "horizon. **Vertical** means upright — straight up and down, like a "
            "flagpole. **Oblique** is Saxon's word for slanted: neither flat nor "
            "upright.",
            "Horizontal and vertical lines are **perpendicular** to each other — they "
            "meet at a perfect square corner. You met that back in Lesson 12, and it "
            "is worth holding onto, because it is why one of them has the tamest "
            "slope possible and the other has no slope at all.",
            "So before you write anything, ask one question about the line in front "
            "of you: *flat, upright, or slanted?* Flat and upright are today. Slanted "
            "is every lesson you have already done.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Lay a pencil flat on the table, pointing left and right. Now walk "
                "your finger from one end to the other. You went sideways — but did "
                "you go UP at all? No. That 'no' is the zero, and it's the whole "
                "lesson. Now stand the pencil straight up and walk your finger up it. "
                "You went up plenty — but how far ACROSS? Zero again. Only this time "
                "the zero landed underneath, and you can't divide by zero.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "start",
        "title": "Horizontal: the slope is 0, so the equation is just y = b",
        "paragraphs": [
            "Slope is *how far up* over *how far across* — `m = Δy / Δx`. The little "
            "triangle Δ just means **the change in**.",
            "Take any two points on a flat line, say (−4, 3) and (4, 3). Both are at "
            "height 3, so the change in y is **zero**. The change in x is 8. Zero "
            "divided by eight is zero — and zero divided by *anything* is zero. So "
            "every horizontal line has slope **0**.",
            "Now watch what that does to `y = mx + b`. If m is 0, then `mx` is `0·x`, "
            "which is 0 no matter what x is. The whole first term disappears and you "
            "are left with `y = b`. The line **is** its own height, and b is the "
            "number where it crosses the y-axis.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "m  =  Δy / Δx  =  0 / Δx  =  0",
        "note": "Read it left to right: the change in y is 0, so the whole fraction is "
                "0, so the slope is 0. The bottom number never mattered — **zero over "
                "anything is zero.**",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "move",
        "title": "Vertical: the slope is undefined, so we don't use y = mx + b at all",
        "paragraphs": [
            "Do the same thing to an upright line. Take (2, 5) and (2, −3). The change "
            "in y is 8. The change in x is **zero** — you never moved across.",
            "Now the zero is on the **bottom** of the fraction: `m = Δy / 0`. And you "
            "cannot divide by zero. Not \"it equals zero,\" not \"it equals infinity\" "
            "— there is no answer at all. Mathematicians call that **undefined**, and "
            "undefined is not a number.",
            "This is the part worth slowing down for. If m is not a number, you cannot "
            "put it into `y = mx + b`. The formula is not hard here — it is *unusable*. "
            "So Saxon does not use it. A vertical line is described by the one thing "
            "that stays put: `x = c`, where c is the number where it crosses the "
            "x-axis. That number has a name — the **x-intercept**.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, every time, both kinds",
        "steps": [
            {"label": "Flat, upright, or slanted?",
             "detail": "If it is slanted, you are in an older lesson and you need "
                       "y = mx + b. If it is flat or upright, keep going — this is "
                       "about to be short."},
            {"label": "Find the letter that never changes.",
             "detail": "On a flat line every point has the same **y**. On an upright "
                       "line every point has the same **x**. Check two points and see "
                       "which coordinate repeats."},
            {"label": "Read the number where the line crosses an axis.",
             "detail": "A flat line crosses the **y-axis** — read it there. An upright "
                       "line crosses the **x-axis** — read it there. This is the "
                       "opposite axis from the one you might expect, and it is where "
                       "most mistakes happen."},
            {"label": "Write letter = number. Stop.",
             "detail": "No m. No b. No plus sign. Nothing else belongs on the line.",
             "math": "flat → y = 4        upright → x = 1"},
        ],
        "after": "Saxon says it in one sentence, and it is worth memorising word for "
                 "word: *equations for horizontal and vertical lines equal the value "
                 "where they cross the axis.*",
    }),

    (B.KIND_WORKED, {
        "number": "80.1",
        "question": "Four lines are drawn through these pairs of endpoints. Which are "
                    "horizontal, which are vertical, and which are oblique? "
                    "A(−4, 3) to E(4, 3) · L(−3, −4) to J(5, −4) · "
                    "B(2, 5) to K(2, −3) · C(−5, −2) to D(3, 4)",
        "steps": [
            {"label": "Ask what refuses to change",
             "text": "For each pair, subtract to find Δy (how far up) and Δx (how far "
                     "across). Whichever one comes out **0** names the line. You may "
                     "write a line's name in either order — AE and EA are the same "
                     "line."},
            {"label": "AE and LJ — the y never moves",
             "text": "Both ends of AE sit at height 3. Both ends of LJ sit at "
                     "height −4. Neither one ever leaves its height, so both are flat.",
             "math": "AE:  Δy = 3 − 3 = 0        LJ:  Δy = (−4) − (−4) = 0"},
            {"label": "BK — the x never moves",
             "text": "Both ends of BK sit 2 across. It climbs from −3 up to 5 without "
                     "ever going sideways, so it is upright.",
             "math": "BK:  Δx = 2 − 2 = 0"},
            {"label": "CD — neither change is zero",
             "text": "It moves across **and** up, so it is neither. That is a slanted "
                     "line — oblique — and it is the kind y = mx + b was made for.",
             "math": "CD:  Δx = 3 − (−5) = 8   →   Δy = 4 − (−2) = 6"},
        ],
        "answer": "AE and LJ are horizontal · BK is vertical · CD is oblique",
    }),

    (B.KIND_WORKED, {
        "number": "80.2",
        "question": "Write the equation of each line. a) A flat line that crosses the "
                    "y-axis at 4. b) An upright line that crosses the x-axis at 1.",
        "steps": [
            {"label": "a) which letter is stuck?",
             "text": "It is flat, so every point on it is at the same height. The "
                     "**y** is stuck. The x is free to be anything."},
            {"label": "a) read the crossing number",
             "text": "It crosses the y-axis at 4, so that stuck height is 4. Write the "
                     "stuck letter, an equals sign, and the number.",
             "math": "flat, crosses the y-axis at 4   →   y = 4"},
            {"label": "b) which letter is stuck?",
             "text": "It is upright, so every point on it is the same distance across. "
                     "The **x** is stuck. The y is free."},
            {"label": "b) read the crossing number",
             "text": "It crosses the x-axis at 1. Same move, other letter, other axis.",
             "math": "upright, crosses the x-axis at 1   →   x = 1"},
        ],
        "answer": "y = 4   ·   x = 1",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 80.3 — which graph is x = −2?",
        "equation": "x  =  −2",
        "steps": [
            {"label": "Look first",
             "text": "You are given four graphs and asked which one this equation "
                     "belongs to. Do not look at the pictures yet. Read the "
                     "**equation** — it already tells you everything."},
            {"label": "Step 1 · which letter is nailed down?",
             "text": "The equation mentions **x** and nothing else. So x is stuck at "
                     "−2, and y is never mentioned, which means y is free to be "
                     "anything at all.",
             "math": "x = −2   (y can be anything)"},
            {"label": "Step 2 · a free y means up and down",
             "text": "Every point that fits has an x of −2 and any y you like. Say a "
                     "few out loud. They stack into a single column — an upright line.",
             "math": "(−2, −3)   (−2, 0)   (−2, 4)   (−2, 5)"},
            {"label": "Step 3 · now pick the picture",
             "text": "You want the graph that goes straight up and down and crosses "
                     "the x-axis two units **left** of the origin. Rule the others "
                     "out on purpose: an upright line at +2 is on the wrong side, a "
                     "flat line through −2 has the letters swapped, and a slanted "
                     "line is oblique. That leaves **Choice B**.",
             "math": "vertical, x-intercept −2   →   Choice B"},
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, in plain English",
        "intro": "Saxon writes this lesson almost entirely in symbols. None of them "
                 "mean anything new — here is each one said out loud.",
        "rows": [
            {"symbol": "Δ", "plain": "the change in — subtract to find it",
             "example": "Δy = second y − first y"},
            {"symbol": "m", "plain": "the slope: how far up over how far across",
             "example": "m = Δy / Δx"},
            {"symbol": "Δy = 0", "plain": "the height never changed → flat",
             "example": "3 − 3 = 0"},
            {"symbol": "Δx = 0", "plain": "it never went sideways → upright",
             "example": "2 − 2 = 0"},
            {"symbol": "y = b", "plain": "y is always b, whatever x does",
             "example": "y = 4"},
            {"symbol": "x = c", "plain": "x is always c, whatever y does",
             "example": "x = 1"},
            {"symbol": "x-intercept",
             "plain": "where a line crosses the x-axis",
             "example": "x = 1 crosses at (1, 0)"},
            {"symbol": "y-intercept",
             "plain": "where a line crosses the y-axis",
             "example": "y = 4 crosses at (0, 4)"},
            {"symbol": "oblique", "plain": "slanted — neither flat nor upright",
             "example": "y = 2x + 1"},
            {"symbol": "undefined",
             "plain": "not a number at all — the arithmetic cannot be done",
             "example": "5 ÷ 0"},
        ],
        "after": "A vertical line has **no y-intercept** — it may never cross the "
                 "y-axis at all. That is exactly why Saxon defines it by its "
                 "*x*-intercept instead.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Swapping the letters — the big one.",
             "wrong": "upright line through 4 on the x-axis → y = 4",
             "right": "upright line through 4 on the x-axis → x = 4",
             "note": "Ask which letter **never changes**, not which axis you are "
                     "looking at. On an upright line the x is the one stuck at 4, so x "
                     "is the letter that gets written down."},
            {"name": "Giving a horizontal line the undefined slope.",
             "wrong": "horizontal: m = Δy/Δx = 6/0 = undefined",
             "right": "horizontal: m = 0/6 = 0",
             "note": "The two lines are constantly traded for each other. Anchor it "
                     "with the pencil: **flat means the top of the fraction is 0**, "
                     "and zero on top is a perfectly good answer — zero."},
            {"name": "Calling a vertical line's slope 0.",
             "wrong": "vertical: m = 0",
             "right": "vertical: m is undefined",
             "note": "Zero is a number and undefined is not. A slope of 0 means a line "
                     "that goes nowhere upward — the flat one. The upright line has no "
                     "slope at all, which is a different sentence."},
            {"name": "Forcing it into y = mx + b anyway.",
             "wrong": "x = 2  →  y = 0x + 2",
             "right": "x = 2",
             "note": "That answer is a horizontal line at height 2 — the exact "
                     "opposite of what was asked. There is no m for a vertical line to "
                     "put in the formula, so the formula does not get used."},
            {"name": "Reading the number off the wrong axis.",
             "wrong": "flat line through (0, −3)  →  x = −3",
             "right": "flat line through (0, −3)  →  y = −3",
             "note": "A flat line crosses the **y**-axis; an upright line crosses the "
                     "**x**-axis. It feels backwards, so say it out loud every time "
                     "until it stops feeling that way."},
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "The two lines side by side — the whole lesson on one card",
        "headers": ["", "Horizontal (flat)", "Vertical (upright)"],
        "rows": [
            {"cells": ["what never changes", "y — the height", "x — the distance across"],
             "emphasis": True},
            {"cells": ["so this change is zero", "Δy = 0", "Δx = 0"], "emphasis": True},
            {"cells": ["slope  m = Δy/Δx", "zero on top → m = 0",
                       "zero underneath → undefined"]},
            {"cells": ["equation", "y = b", "x = c"]},
            {"cells": ["b or c is read from", "the y-axis (y-intercept)",
                       "the x-axis (x-intercept)"]},
            {"cells": ["use y = mx + b?", "you could, with m = 0 — but don't bother",
                       "no — there is no m to use"]},
        ],
        "note": "The shaded rows are the cause and every row under them is the effect. "
                "If she can say which change is zero, the rest of the card follows "
                "without being memorised.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "y = 3 and x = 3 both use the number 3. How are they different?",
        "answer": "`y = 3` is **flat**: it crosses the y-axis at 3 and its slope is "
                  "**0**. `x = 3` is **upright**: it crosses the x-axis at 3 and its "
                  "slope is **undefined**. Draw both and you get a perfect square "
                  "corner — they are perpendicular, and they cross each other at "
                  "(3, 3). Same number, completely different line.",
    }),

    (B.KIND_TOOL, {
        "title": "Graph paper — build the lines yourself and read off their equations",
        "intro": "Tap the grid to drop a point; tap a point again to take it away. "
                 "Plot the five points listed underneath, then look for what all five "
                 "have in common.",
        "widget": "grid",
        # No `choices` here on purpose. The family buttons offer x, x², √x and the
        # rest — curved function families, none of which is a horizontal or a
        # vertical line. Offering them would let a correct answer be marked wrong,
        # which is the one thing this tool must never do.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "table": [[-4, 3], [-2, 3], [0, 3], [3, 3], [5, 3]],
                   "label": "graph paper for horizontal and vertical lines"},
        "after": "First table: **(−4, 3)  (−2, 3)  (0, 3)  (3, 3)  (5, 3)**. Every "
                 "single y is 3, so the equation is **y = 3** — and sure enough the "
                 "row of dots crosses the y-axis at 3.\n\n"
                 "Now press **Clear** and plot **(2, −4)  (2, −1)  (2, 0)  (2, 3)  "
                 "(2, 5)**. This time every x is 2, so the equation is **x = 2**. Say "
                 "its slope out loud before you move on.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Flat line:** every y is the same. Slope **0**. Equation **y = b**.",
            "**Upright line:** every x is the same. Slope **undefined** — not 0, not "
            "steep, not a number.",
            "Zero on **top** of the fraction gives 0. Zero **underneath** gives "
            "undefined. That one difference is the entire lesson.",
            "*Equations for horizontal and vertical lines equal the value where they "
            "cross the axis.* Read the number, write the stuck letter in front of it, "
            "stop.",
            "`y = mx + b` belongs to **oblique** (slanted) lines. A vertical line has "
            "no m, so it never gets that form.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 80 first. If it didn't quite click, this is here to fix "
    "that — and to let you play with it. Good news up front: these are the two "
    "lines where you do not need y = mx + b at all. You find one number, write one "
    "letter in front of it, and you're done."
)

PARENT_CONTENT = """## The big idea

Every line she has graphed so far was **oblique** — slanted — and `y = mx + b`
was built for those. Lesson 80 hands her the two lines that break the pattern,
and the relief is that they need *less* machinery, not more.

- **Horizontal (flat).** Nothing changes vertically, so `Δy = 0`, so
  `m = 0 / Δx = 0`. With m = 0 the `mx` term vanishes and all that is left is
  **`y = b`**.
- **Vertical (upright).** Nothing changes horizontally, so `Δx = 0`, so
  `m = Δy / 0` — **undefined**, which is not a number. There is no m to substitute,
  so `y = mx + b` is not merely hard here, it is unusable. Saxon replaces it with
  **`x = c`**, where c is the **x-intercept**.

Saxon's own one-line summary is the thing to memorise, and it covers both cases at
once: *equations for horizontal and vertical lines equal the value where they cross
the axis.*

This is the piece the video skipped: she does not need the slope-intercept
*technique* today. She needs to identify which coordinate is frozen and read one
number off one axis.

## Teach it out loud in five minutes

Say these in order, and ask the question at each step. A pencil on the table does
most of the work.

1. Lay a pencil **flat**, pointing left and right. **"Walk your finger from this
   end to that end. How far UP did you go?"** — wait for "none." *"That zero is the
   slope. Flat lines have a slope of zero."*
2. Write `m = Δy / Δx` and put a **0** on top with any number underneath.
   **"What's zero divided by eight?"** — zero. *"And zero divided by anything else?"*
   Still zero. *"So it doesn't even matter how long the line is."*
3. Now the key question: **"If m is zero, what does the `mx` part of `y = mx + b`
   turn into?"** — nothing. *"So the equation collapses to `y = b`. The line is just
   its own height."*
4. Stand the pencil **straight up**. **"Walk your finger up it. How far ACROSS did
   you go?"** — zero again. *"But this time the zero is on the bottom."* Then:
   **"What's five divided by zero?"** Let her actually try. The honest answer is
   that it cannot be done — undefined. *"Undefined isn't a number, so there's no m
   to put in the formula. That's why vertical lines get their own: `x = c`."*
5. Draw axes. Draw a flat line through 4 and an upright line through 1.
   **"Which number would you write down for each one — and which letter goes in
   front of it?"** That single question is the whole lesson, and it is the one to
   come back to all week.

## The classic mix-ups

Each of these produces a specific wrong answer. Watch for the exact string.

- **Letters swapped.** Upright line through 4 on the x-axis, and she writes
  **`y = 4`** instead of `x = 4`. This is the most common error in the set by a wide
  margin. The fix is the question "which letter never changes?", not "which axis am
  I looking at?"
- **Slopes swapped.** She writes **"`y = 4` has an undefined slope"** and
  **"`x = 2` has slope 0."** Exactly backwards. Anchor with the pencil: flat puts
  the zero on **top** (fine — the answer is 0), upright puts it **underneath**
  (undefined).
- **Undefined treated as zero.** For `x = 2` she writes **`m = 0`**. Zero is a
  number; undefined is the absence of one. Different sentences.
- **Forcing slope-intercept.** For a vertical line she writes **`y = 0x + 2`**.
  That is a horizontal line at height 2 — the exact opposite of what was asked.
- **Wrong axis.** A flat line through (0, −3) written as **`x = −3`**. Flat lines
  cross the y-axis; upright lines cross the x-axis. It feels backwards to almost
  everyone, so have her say it aloud each time.

## What to watch her do

Watch her **hands**, not her answer.

- Before she writes anything, does a finger travel **along the line** while she
  checks two points? The habit you want is visible: she touches two points, says
  "the y never changed," and only then writes `y = 4`. A child who writes the first
  number she sees will be right half the time and will not know which half.
- Watch **which axis she looks at**. Writing a horizontal line's equation, her eyes
  and finger should go to the **y-axis**. If they go to the x-axis she has the pair
  swapped, and she will miss roughly half the problems no matter how well she
  understands the idea.
- On the tool, watch whether she **says the slope out loud** for the `x = 2` line
  before moving on. If "undefined" does not come out of her mouth easily, that is
  the sentence to rehearse — it is what the test question is really asking.

## Extend it

- **"What is the equation of the x-axis itself?"** (`y = 0`.) **"And the y-axis?"**
  (`x = 0`.) Most students find this genuinely startling, and it proves she has the
  rule rather than a memorised pair of examples.
- Ask for the horizontal line through (3, 5) — `y = 5` — and the vertical line
  through the same point — `x = 3`. Then: where do they cross, and what angle do
  they make? (At (3, 5); a square corner. Perpendicular, straight out of Lesson 12.)
- For a stretch: **"Is `x = 2` even a function?"** It is not — one x with endlessly
  many y values. That connects straight back to the domain-and-range work in the
  review lessons, and it is a satisfying thing for a 12-year-old to be able to
  argue.

## Where this sits

Pairs with **DIVE Lecture 80**. Reviews Lessons **12, 23, 68, 70, 73, 74, 77 and
79**. If the trouble is remembering which word means flat, go back to **12**. If
the trouble is slope itself — what `Δy / Δx` is even measuring — go back to **68**
and **70**.

**Proficient** looks like: given a graph or a description, she writes the correct
equation and names the slope, with the card in front of her.
**Mastered** looks like: she does it without the card, and can *say why* — "there's
no change in x, so you'd be dividing by zero, so there's no slope."
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 80 (horizontal and vertical lines) — idempotent."

    LESSON_NUMBER = 80
    TITLE = "Flat Lines and Upright Lines — Horizontal and Vertical"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
