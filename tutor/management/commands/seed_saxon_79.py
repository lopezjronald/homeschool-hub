"""Saxon Pre-Algebra Lesson 79 — Creating a Linear Equation from a Graph.

Reviews Lessons 68, 70, 73, 74 and 77. Lesson 70 is the hook and it is the
strongest one available: 70 is *equation in, picture out* — the slope-intercept
graphing the parent already taught her at the table. Lesson 79 is that same road
driven the other way. The book's own first page says it: "No New Rules or
Definitions." Nothing here is new; it is the same two numbers, found instead of
used.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. The practice-set graphs are figures that cannot be reproduced here,
so the tool block ships its own line — built to the book's own promise that every
Lesson 79 slope is an integer or a simple fraction and every intercept an integer.

    python manage.py seed_saxon_79 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

# The line on the practice board: y = -0.5x + 1. Every lattice point it passes
# through inside a -6..6 window, so she has seven dots to walk between and never
# has to guess whether the line "really" goes through one.
PRACTICE_LINE = [[-6, 4], [-4, 3], [-2, 2], [0, 1], [2, 0], [4, -1], [6, -2]]

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 79 · Pre-Algebra",
        "title": "Reading the equation off the picture",
        "thesis": "A graph and an equation are the **same line** wearing different "
                  "clothes. You already know how to go from the equation to the "
                  "picture. Today you go from the picture to the equation.",
        "formula": "y = mx + b",
        "roles": [
            {"tone": "start", "name": "b — where it starts",
             "text": "The height of the line where it crosses the up-and-down axis. "
                     "You read it. You do not work it out."},
            {"tone": "move", "name": "m — how it moves",
             "text": "Rise over run. From b, count how far up or down the line goes, "
                     "then how far right, to reach the next corner it passes through."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why you would want the equation when you already have the graph",
        "paragraphs": [
            "A graph is a picture, and a picture only knows about the part of the "
            "world that fits on the paper. Ask it what happens when x is 40 and it "
            "has nothing to say — the paper ran out long before that.",
            "The equation is that same line written as a **rule**, and a rule works "
            "anywhere. Once somebody hands you `y = 0.5x - 1`, you can answer "
            "questions the picture was never big enough to answer.",
            "So that is the job: someone gives you a line, you give back the rule "
            "that made it. Two numbers, and both of them can be read straight off "
            "the paper.",
            "And here is the part worth knowing before you start. **You have already "
            "done this, in the other direction.** When you picked an x, put it in, "
            "got a y out and made a dot — that was a rule turning into a picture. "
            "Today the picture turns back into the rule. Same road, driven the other "
            "way.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "You have done this before, backwards",
        "paragraphs": [
            "In Lesson 70 you started with an equation — take `y = 2x + 1` as our "
            "stand-in for it, since the book names Ex. 70.1 and 70.2 without "
            "reprinting them here. You put a dot on the axis at the intercept, counted "
            "the slope out from there, and drew the line. Equation in, picture out.",
            "Every step of that has a partner going the other way. The dot you "
            "*placed* is a dot you can now *read*. The staircase you *walked* to draw "
            "the line is a staircase you can now *count*.",
            "Which is why the book's first page says **no new rules and no new "
            "definitions**. There is genuinely nothing new in this lesson. It is the "
            "same two numbers, found instead of used.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Remember how we picked an x, put it in, got a y out, and that gave "
                "us a dot? We were turning a rule into a picture. Now I'm going to "
                "show you a picture and you're going to tell me the rule. There are "
                "only two things to find: where it crosses, and how steep it is.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "start",
        "title": "Find b first. It is sitting right there.",
        "paragraphs": [
            "`b` is not something you calculate. It is a **place you look**. Find "
            "where the line crosses the up-and-down axis, read the number off, and "
            "you are a third of the way done.",
            "Check the sign while your eyes are there. Above the middle, b is "
            "positive. Below it, b is negative. That one glance is what catches you "
            "later if you write the equation down wrong.",
            "This is why the book says to write `y = mx + b` down **before** you look "
            "at the graph. Two empty boxes give your eyes somewhere to go. A blank "
            "page gives them nothing.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "move",
        "title": "m is a staircase you walk",
        "paragraphs": [
            "Put your finger on the crossing point you just found. Now find the next "
            "corner **to the right** that the line goes exactly through — a place "
            "where it passes through the crossing of two grid lines, not near it.",
            "Then say the move the book's way, **rise first, then run**. How far up or "
            "down from b? That is the **rise**. How far right? That is the **run**. "
            "And `m = rise / run`.",
            "The run always goes to the right, never to the left. Do it that way every "
            "single time and the sign looks after itself: a line that climbs hands you "
            "a positive rise, a line that falls hands you a negative one.",
            "Then walk it once more, starting from where you landed. If the second "
            "staircase gives you the same fraction, you counted right. The book asks "
            "for that check and it takes about four seconds.",
            "One more promise from the book, and it is a useful one: in **every** "
            "Lesson 79 problem the slope is an **integer** or a simple fraction, and "
            "the intercept is an **integer**. An integer is a whole number carrying "
            "its sign, so −2 and −1 count just as much as 3 and 0. That makes it a "
            "self-check: `m = 0.37` is not an unusual answer. It is a wrong one.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Five moves, the same way every time",
        "steps": [
            {"label": "Write the standard form down first.",
             "detail": "`y = mx + b`, before you look at the graph at all. That is the "
                       "book's own first instruction, and the reason is not neatness — "
                       "it is that two empty boxes give your eyes a job."},
            {"label": "Find where the line crosses the up-and-down axis.",
             "detail": "Read the number off and write it in. That is **b**. Notice "
                       "whether it sits above or below the middle."},
            {"label": "From that point, rise up or down to the next corner, then right.",
             "detail": "A *corner* means a spot where the line passes exactly through "
                       "the crossing of two grid lines. Not near one. Through one. Say "
                       "the move in the book's order every time — rise first, then run."},
            {"label": "Count the rise, then the run.",
             "detail": "Up is positive, down is negative, and the run is always "
                       "positive because the run always goes right. "
                       "**m = rise / run** — then simplify it."},
            {"label": "Walk it once more to check.",
             "detail": "From the point you just landed on, do the same staircase "
                       "again. The same fraction twice means you counted right."},
        ],
        "after": "Then fill the two blanks in and **look back at the picture**. A line "
                 "that climbs must have a positive m; a line that falls must have a "
                 "negative one. If your equation and the picture disagree, the picture "
                 "is right.",
    }),

    (B.KIND_MATH, {
        "display": "y = mx + b",
        "note": "Write this line down **before** you look at the graph. Every single "
                "time. It is the first thing the book tells you to do, and it is the "
                "one habit that stops m and b from swapping places.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 79.1a — a line that climbs",
        "equation": "crosses the y-axis at (0, -1)   ·   also passes through (2, 0)",
        "steps": [
            {"label": "Look first",
             "text": "The book prints a graph here and this page cannot reprint it, so "
                     "the two things your eyes would pick off it are written along the "
                     "top instead — it crosses at (0, −1), and it also goes through "
                     "(2, 0). Open your book to Ex. 79.1a and look at the real one "
                     "while you read this. Both of those facts are things you *see*, "
                     "before you count anything: it cuts the up-and-down axis "
                     "**below** the middle, and it **climbs** as you move right — so "
                     "the slope is going to come out positive."},
            {"label": "Step 1 · write the form",
             "text": "Nothing to do with this graph yet. This is the page-setup move, "
                     "and it gives you two blanks to fill.",
             "math": "y = mx + b"},
            {"label": "Step 2 · read b off the axis",
             "text": "The line crosses the up-and-down axis one square **below** the "
                     "middle. So b is −1. No arithmetic — you looked, and there it was.",
             "math": "b = -1  →  y = mx - 1"},
            {"label": "Step 3 · walk the staircase",
             "text": "Start your finger at (0, −1). Go **up 1**, then **right 2**. You "
                     "land on (2, 0), and that point is on the line. Rise 1, run 2. No "
                     "subtracting — you counted squares.",
             "math": "m = rise / run = 1/2 = 0.5"},
            {"label": "Step 4 · do it again to check",
             "text": "From (2, 0), up 1 and right 2 again lands you on (4, 1) — still "
                     "on the line. Same fraction. That is the book's own check, and it "
                     "is how you find a miscount before it becomes a wrong answer.",
             "math": "m = rise / run = 1/2 = 0.5"},
            {"label": "Step 5 · fill in the blanks",
             "text": "m is 0.5, b is −1. Put them where they go — **m against the x, b "
                     "on its own** — and check it against the picture. Positive slope "
                     "for a climbing line. It agrees.",
             "math": "y = 0.5x - 1"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "79.1b",
        "question": "The book shows this one as a graph, which this page cannot "
                    "reprint — so here are the two things that graph tells you. The "
                    "line crosses the y-axis at (0, 2) and passes through (1, 0). "
                    "Write its equation.",
        "steps": [
            {"label": "Write the form",
             "text": "Same first move as always.",
             "math": "y = mx + b"},
            {"label": "Read b",
             "text": "It cuts the up-and-down axis **above** the middle, at 2. That is "
                     "b, and it cost you nothing.",
             "math": "b = 2  →  y = mx + 2"},
            {"label": "Which way does it lean?",
             "text": "It **falls** as you move right, so m is going to be negative. "
                     "Decide that now, before you count — then your answer has "
                     "something to agree with."},
            {"label": "Walk the staircase",
             "text": "From (0, 2), go **down 2**, then **right 1**. You land on (1, 0), "
                     "which is on the line. Down means the rise is negative.",
             "math": "m = rise / run = -2/1 = -2"},
            {"label": "Fill in the blanks",
             "text": "A negative m for a falling line. The equation and the picture "
                     "agree, so you are done.",
             "math": "y = -2x + 2"},
        ],
        "answer": "y = -2x + 2",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Saxon says the whole lesson in about five characters. Here is what "
                 "each of them is short for.",
        "rows": [
            {"symbol": "y = mx + b", "plain": "the standard form — the shape you write "
                                              "every one of these answers in",
             "example": "y = 0.5x - 1"},
            {"symbol": "b", "plain": "where the line crosses the y-axis (the "
                                     "up-and-down one)",
             "example": "b = -1"},
            {"symbol": "m", "plain": "how steep it is, and which way it leans",
             "example": "m = 0.5"},
            {"symbol": "rise", "plain": "how far UP (+) or DOWN (-) you walked",
             "example": "up 1  →  rise = 1"},
            {"symbol": "run", "plain": "how far RIGHT you walked — always right",
             "example": "right 2  →  run = 2"},
            {"symbol": "m = rise / run", "plain": "steepness is a fraction: up over "
                                                  "across",
             "example": "1/2 = 0.5"},
        ],
        "after": "`m` and `b` are labels somebody picked a long time ago and they mean "
                 "nothing on their own. What matters is where they sit: **m is always "
                 "stuck against the x, and b always stands alone.**",
    }),

    (B.KIND_TABLE, {
        "caption": "What the picture is telling you, and where to look for it",
        "headers": ["you want…", "where you look", "how you read it"],
        "rows": [
            {"cells": ["b", "the y-axis — the up-and-down one",
                       "read the number straight off"], "emphasis": True},
            {"cells": ["the sign of m", "the whole line, at a glance",
                       "climbs to the right = positive; falls = negative"],
             "emphasis": True},
            {"cells": ["rise", "from b, straight up or down", "up is +, down is −"]},
            {"cells": ["run", "then straight right",
                       "always positive — you always walk right"]},
            {"cells": ["m", "the two counts you just made",
                       "rise over run, then simplify"]},
        ],
        "note": "The two shaded rows are things you **see**. The other three you "
                "**count**. Doing the seeing first is what makes the counting "
                "checkable — you already know what sign the answer has to have.",
    }),

    (B.KIND_TOOL, {
        "title": "Read one off yourself",
        "intro": "Seven dots are on the board and every one of them sits on the same "
                 "straight line. They are drawn hollow because they are the question — "
                 "they are fixed, so you cannot rub one out by accident. Switch to the "
                 "✏️ Pen and draw the line through them if that helps you see it. Then "
                 "do the job: find where it crosses the up-and-down axis, walk the "
                 "staircase, and write the equation. Click anywhere to drop a dot of "
                 "your own — yours come out solid, and Undo and Clear only take yours "
                 "away.",
        "widget": "grid",
        # `points`, not `table` — these are drawn FOR her. The lesson is reading a
        # line that is already there, so a table she has to plot herself would be
        # the previous lesson's exercise, not this one's. No `choices`: those name
        # function FAMILIES (x, x², √x), which is Lesson 73's vocabulary and would
        # tell her "that doesn't fit" for every button on a line like this one.
        # `locked` because these seven dots ARE the question: without it a stray
        # tap deletes one, and Undo/Clear wipe the only line she has to read.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "points": PRACTICE_LINE,
                   "locked": True,
                   "label": "a straight line to read an equation from"},
        "after": "Two questions, in this order. **Where does it cross the up-and-down "
                 "axis?** Then: **from there, if you walk right 2, do you go up or "
                 "down, and by how much?** Write `y = mx + b` on paper first. The "
                 "answer is in the drop-down below — but predict before you open it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "What is the equation of the line on the board?",
        "answer": "`y = -0.5x + 1`. It crosses the up-and-down axis at **1**, so "
                  "`b = 1`. From (0, 1), walk **right 2** and you land on (2, 0) — "
                  "which is **down 1**. So the rise is −1, the run is 2, and "
                  "`m = -1/2 = -0.5`. Last check: the line falls as it goes right and "
                  "−0.5 is negative, so the equation and the picture agree.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Reading the staircase upside down — run over rise.",
             "wrong": "up 1 and right 2  →  m = 2",
             "right": "up 1 and right 2  →  m = 1/2 = 0.5",
             "note": "**Rise goes on top.** It is the word that comes first and the "
                     "number that goes first. Quick catch: if your slope is a much "
                     "bigger number than the line looks steep, you flipped it."},
            {"name": "Losing the minus sign on a line that falls.",
             "wrong": "down 2 and right 1  →  m = 2",
             "right": "down 2 and right 1  →  m = -2/1 = -2",
             "note": "The run always goes to the **right**, and then down means the "
                     "rise is negative and the sign takes care of itself. Look at the "
                     "picture before you write it down: a falling line cannot have a "
                     "positive m."},
            {"name": "Reading b off the wrong axis.",
             "wrong": "it crosses the x-axis at 2  →  b = 2",
             "right": "it crosses the y-axis at -1  →  b = -1",
             "note": "`b` lives on the **y**-axis, the up-and-down one. Both crossings "
                     "are sitting in the same picture and the wrong one is easy to "
                     "grab. Put your finger on the vertical axis first, every time."},
            {"name": "Counting the staircase to a point the line only passes near.",
             "wrong": "from (0, 2) to a spot near (0.5, 0.8)  →  m = -1.2/0.5 = -2.4",
             "right": "from (0, 2) to (1, 0)  →  m = -2/1 = -2",
             "note": "That stop is half a square along, where the line is not going "
                     "through a corner, so the height had to be guessed. The book "
                     "promises "
                     "every slope in this lesson is an integer or a simple fraction. "
                     "**A decimal like -2.4 is not an answer, it is a symptom.** Keep "
                     "going right until you land exactly on a crossing of two grid "
                     "lines — here that is (1, 0)."},
            {"name": "Swapping m and b when you finally write the equation.",
             "wrong": "b = -1  →  m = 0.5  →  y = -x + 0.5",
             "right": "b = -1  →  m = 0.5  →  y = 0.5x - 1",
             "note": "`m` is stuck to the x. `b` stands alone. Writing `y = mx + b` at "
                     "the top of the page before you look at the graph is the whole "
                     "defence against this, which is exactly why the book puts it "
                     "first."},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "Practice 6",
        "question": "Graph this data, write the exact linear equation that fits it, "
                    "then find f(3).   x: -2, -1, 0, 2, 5   ·   y: -1, 0, 1, 3, 6",
        "steps": [
            {"label": "Plot the five pairs",
             "text": "(-2, -1)  (-1, 0)  (0, 1)  (2, 3)  (5, 6). They fall in a "
                     "perfectly straight line, so this is an **exact** equation — not "
                     "a **trendline** like the one in Ex. 77.1. That is the book's own "
                     "word, and the book says so in the question."},
            {"label": "Read b straight out of the table",
             "text": "One row already has x = 0. The y sitting beside it **is** the "
                     "y-intercept, because x = 0 is precisely where the line crosses "
                     "that axis. You did not even need the graph for this one."},
            {"label": "Walk from one row to the next",
             "text": "From (0, 1) to (2, 3): **up 2**, then **right 2**. Rise over run, "
                     "then simplify."},
            {"label": "Put the two numbers in",
             "text": "m is 1 and b is 1. A slope of 1 means the line climbs one square "
                     "for every square right — and `1x` is just written `x`.",
             "math": "b = 1  →  m = 2/2 = 1  →  y = x + 1"},
            {"label": "Now answer what was actually asked",
             "text": "The question wanted `f(3)`, not the equation. `f(3)` means: what "
                     "comes out when x is 3? Put 3 in and turn the handle.",
             "math": "y = 3 + 1 = 4  →  f(3) = 4"},
        ],
        "answer": "y = x + 1   ·   f(3) = 4",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "This is Lesson 70 run **backwards**. There you had the equation and drew "
            "the picture; here you have the picture and write the equation.",
            "**Write `y = mx + b` first**, before you look at anything.",
            "**b is a place, not a calculation.** Find where the line crosses the "
            "up-and-down axis and read it off.",
            "**m = rise / run** — rise first, and the run always goes to the "
            "**right**. Up is positive, down is negative.",
            "Climbing line → positive m. Falling line → negative m. Check your answer "
            "against the picture before you write it down.",
            "Every slope in this lesson is an **integer** or a simple fraction, and "
            "every intercept is an **integer** — and integers carry their sign, so "
            "`m = -2` and `b = -1` are exactly the kind of answer the book means. "
            "**A messy decimal means you counted to the wrong point**, not that the "
            "answer is messy.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 79 first. If it didn't quite click, this is here to fix "
    "that — and there's a graph you can click on. This one is the exact reverse of "
    "the slope-intercept graphing you already did: instead of turning an equation "
    "into a line, you look at a line and write down its equation."
)

PARENT_CONTENT = """## The big idea

This lesson is **Lesson 70 run backwards** — and that is the whole hook. In 70 she
took `y = mx + b`, marked the intercept, counted the slope out from it and drew the
line. That is the part you already taught her at the table. In 79 the line is
already drawn and she has to hand back the two numbers.

There are only two, and both are *read* rather than *calculated*:

- **b** — where the line crosses the y-axis. She looks; she does not work it out.
- **m** — rise over run. Finger on the intercept, find the next point to the
  **right** where the line goes exactly through a corner of the graph paper, and say
  the move in Saxon's order: how far up (+) or down (−) first, then how far right.

The book's own first page says **"No New Rules or Definitions."** Say that to her.
It is true, and it takes the fear out of the page.

One promise worth quoting to her, because it converts into a self-check: every
slope in Lesson 79 is an integer or a simple fraction, and every y-intercept is an
integer. So a slope of 0.37 is not a hard answer — it is a wrong one, and it means
she counted to a point the line only passes *near*. Say **integer**, not "whole
number": Saxon's integers include the negatives, and this lesson's own examples
answer `m = -2` and `b = -1`. If she hears "whole number" she will start rejecting
her own correct answers.

**About the figures on her page.** Example 79.1's two graphs, and practice problems
179 and 279, are pictures in her DIVE book and cannot be reprinted here. So each
worked example is given as the two facts the picture shows — the crossing point and
one more point the line goes exactly through — and it says so on her page. Have the
book open beside her so she is reading a real graph while she works the example.
The clickable board further down is a line of ours, built to the book's own promise;
it is practice, not one of the book's problems.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Draw axes and a line — any line, but make it go through corners. Say:
   **"Remember when we picked an x, put it in, and got a y? That was a rule turning
   into a picture. I'm going to do it backwards now."**
2. Write `y = mx + b` at the top of the page *before* pointing at the graph. Ask:
   **"What are the only two things we don't know?"** — you want "m and b." That is
   the entire lesson in one answer.
3. Point at the y-axis. **"Where does the line cross this one?"** Wait. Whatever
   number she says, write it in the b slot. Then say the important part out loud:
   *"Notice we didn't calculate anything. We just looked."*
4. Put her finger on that crossing point. **"Find the next corner over to the right
   that the line goes exactly through. How far up or down did you go, and how far
   right?"** Ask it in that order — up-or-down first — because that is the order
   Saxon says it in both worked examples, and it is the order on her page. Write it
   as a fraction with the up-or-down number on **top**. Do not give her the words
   "rise over run" until after she has counted once — the counting is the idea, the
   words are the label.
5. Before she writes the final equation, ask the checking question: **"Is the line
   going uphill or downhill?"** Uphill means m is positive; downhill means negative.
   Then have her walk the staircase a second time from the new point. Same fraction
   means she counted right. That check is Saxon's own and it takes four seconds.

If she gets stuck, go back to step 3 and re-do it on a line where b is **negative**.
That is the version that separates children who understand it from children who
pattern-matched the first example.

## The classic mix-ups, with the exact wrong answer each one produces

- **Run over rise.** Up 1 and right 2, and she writes **m = 2** instead of
  **m = 1/2**. Fix: rise goes on top — it is the word that comes first and the
  number that goes first. Fast catch: if the slope number is much bigger than the
  line looks steep, she flipped it.
- **The lost minus sign.** Down 2 and right 1, and she writes **m = 2** instead of
  **m = −2**, giving `y = 2x + 2` instead of `y = -2x + 2`. Fix: the run always goes
  right, never left; then "down" is what makes it negative and the sign takes care
  of itself.
- **b read off the x-axis.** On the line `y = 0.5x - 1` she sees it cross the
  horizontal axis at 2 and writes **b = 2**, producing `y = 0.5x + 2`. Both
  crossings are in the same picture and the wrong one is easy to grab. Fix: finger
  on the *vertical* axis first, every time.
- **Counting to a point the line only passes near** — she stops half a square along
  and guesses the height, which on `y = -2x + 2` produces a slope like **−2.4**. The
  decimal is the tell. Have her keep going right until she lands exactly on a
  crossing of two grid lines.
- **m and b swapped.** She finds b = −1 and m = 0.5 and writes **y = -x + 0.5**.
  Fix: m is stuck to the x; b stands alone. Writing `y = mx + b` before looking at
  the graph is the whole defence.

## What to watch her do

Watch her **hands**, in this order:

1. Does the pencil write `y = mx + b` *before* it points at the graph? If she starts
   by staring at the line, she is guessing, and the guessing is what produces the
   swapped m and b later.
2. When she finds the slope, does her finger actually **travel** — up, then right —
   or does it hover over two points while she does it in her head? The travelling is
   what makes the sign reliable. In-the-head slope is where the minus signs go to
   die.
3. Does her finger always go **right**? If it wanders left, stop her there. Walking
   left is legal mathematics and a reliable source of sign errors for a beginner.
4. Does she look back at the picture after writing the equation? You want a visible
   glance up at the line and a nod. That glance is the entire error-checking system
   this lesson gives her.

Getting the right answer is not the thing to watch for. She can get a right answer
by luck on a line with a positive integer slope. The four habits above are what
survive contact with a negative fraction.

## Extend it

- Give her a **horizontal** line and ask for its equation. The rise is 0, so
  `m = 0/run = 0` and the equation is just `y = b`. It looks like a trick and it is
  not, and working it out from the rules she already has is very satisfying.
- Then give her a **vertical** line and let her discover that the run is 0 — and you
  cannot divide by 0. Its slope is **undefined** (that is the word, not "no slope"),
  and that line cannot be written as `y = mx + b`. She is not expected to know this
  yet; meeting it as a puzzle rather than a rule is worth far more than being told.
- Hand her two dots on paper with no line drawn and ask for the equation. Same job,
  one step harder, and it is what Lesson 77 and the practice-set data problem are
  quietly training her for.

## Where this sits

DIVE Lesson 79. Reviews Lessons 68, 70, 73, 74 and 77. **Lesson 70 is the one to
revisit if she is lost** — it is the slope-intercept graphing you already did with
her, and 79 is literally that process reversed. Lesson 77 (writing an equation to
model a situation) is the one the data-table practice problem leans on.

**Proficient** looks like: correct equation from a graph with a positive integer
slope and a positive intercept, given time.
**Mastered** looks like: gets the negative fractional slopes right too, and checks
the sign against the picture *without being asked* before writing the answer down.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 79 (linear equation from a graph) — idempotent."

    LESSON_NUMBER = 79
    TITLE = "Reading the Equation Off the Picture — a Linear Equation from a Graph"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
