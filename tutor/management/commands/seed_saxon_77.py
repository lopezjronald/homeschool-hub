"""Saxon Pre-Algebra Lesson 77 — More on Linear Functions: Creating a Linear
Equation to Solve a Problem. Reviews Lessons 68, 70, 73, 74.

The hook Saxon itself names: in Lesson 68 the POINTS came from the equation; from
Lesson 74 onward the EQUATION comes from the points. This is the first lesson
where she builds the rule rather than being handed it — so the lesson is really
about the two numbers that make a line, which is the exact part the video left
her father unable to teach.

No new rules or definitions in the source. Everything here is y = mx + b said
slowly, plus substitution she has already been shown at the kitchen table.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Practice problems are reworded rather than transcribed.

    python manage.py seed_saxon_77 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 77 · Pre-Algebra",
        "title": "This time you build the equation",
        "thesis": "Every graphing lesson so far handed you the equation and asked "
                  "for points. **Today the points come first**, and the equation is "
                  "the thing you make.",
        "formula": "y  =  0.1065x − 21.122",
        "roles": [
            {"tone": "start", "name": "b — where it starts",
             "text": "The height of the line when x is 0. Read it straight off the "
                     "table; there is nothing to calculate."},
            {"tone": "move", "name": "m — how fast it climbs",
             "text": "How much y moves every time x moves 1. Up, divided by across."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone builds an equation out of data",
        "paragraphs": [
            "Somebody hangs weights on a spring and writes down how far it stretches. "
            "200 grams. 400 grams. 600 grams. Then the question arrives: *what about "
            "700?* Nobody hung 700 grams. Nobody measured it.",
            "You have two choices. Go and hang a 700 gram weight — or notice that the "
            "stretch is climbing at a **steady rate**, write down the rule it is "
            "climbing by, and let the rule answer for you.",
            "That rule is a linear equation. Weather, medicine doses, fuel, prices — "
            "people build an equation from the measurements they *have* so it can "
            "tell them about the ones they don't. Building it is the whole lesson.",
            "The spring at the top of this lesson gave the equation "
            "`y = 0.1065x − 21.122`, where x is the mass in grams and y is how far "
            "the spring stretched in millimetres. Every number on this page comes "
            "from that one line, or from a table of five points further down.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Backwards from every lesson before this",
        "paragraphs": [
            "In Lesson 68 you were handed something like `y = 2x + 1`. You made a "
            "little table of x's, worked out each y, plotted the dots and drew a line "
            "through them. The **points came out of the equation**, so of course they "
            "sat on the line perfectly — they were made from it.",
            "Turn that around. Someone hands you the measurements and you work out "
            "the equation. The **equation comes out of the points**. Saxon says this "
            "outright, and it is the whole reason this lesson exists.",
            "One honest warning that comes with real data: it will not sit exactly on "
            "your line. Some measurements land a little above, some a little below. "
            "That is not you doing it wrong — that is what measuring is like. The "
            "line follows the *trend*. (Lesson 97 teaches the proper way to fit one; "
            "the spring equation here was made by a computer.)",
            "The five-point table in this lesson is different: Saxon promises it fits "
            "**exactly**. So when you check your equation against it, every point "
            "should land dead on.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Forget the letters for a second. If I'm going to draw you a line, "
                "you only have to tell me two things: where does it start, and how "
                "steep is it? That's it — that's a whole line. The steepness is how "
                "far up it goes every time you step one across. The start is how high "
                "it is before you've gone anywhere. Everything today is those two "
                "things wearing letters: m for the steepness, b for the start.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "Two numbers make a line",
        "paragraphs": [
            "Think of a staircase. To describe it completely you need the height it "
            "starts at, and the size of one step. Nothing else. Every stair after "
            "that is forced.",
            "**Where it starts** is the y value when x is 0 — you have gone nowhere "
            "sideways yet, so this is the height you began at. The book calls it "
            "**b**, the y-intercept. If your table has a row where x is 0, that row "
            "*is* b. No work.",
            "**How fast it climbs** is how much y goes up each time x goes across by "
            "1. The book calls it **m**, the slope. Pick two points, ask *how far "
            "up?* and *how far across?*, and divide: up over across.",
            "Then you write the two numbers into the shape `y = mx + b`. The climb "
            "multiplies the x, because the further across you go the more times you "
            "climb. The start just gets added on at the end, because you had it "
            "before you moved at all.",
            "That sentence — *the climb multiplies the x, the start is added on* — is "
            "worth reading twice. It is the piece the lecture goes past quickly.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, every time",
        "steps": [
            {"label": "Read b off the table.",
             "detail": "Find the row where **x is 0** and take its y. Both tables in "
                       "this lesson hand it to you. Write `b = ` and the number "
                       "before you do anything else."},
            {"label": "Pick two points and measure the climb.",
             "detail": "Any two will do when the data fits exactly. How far **up** "
                       "from the first to the second, and how far **across**?",
             "math": "m = Δy / Δx"},
            {"label": "Write the equation with your two numbers in it.",
             "detail": "The climb goes in front of the x. The start goes on the end.",
             "math": "y = m x + b"},
            {"label": "Check it on a row you did not use.",
             "detail": "Put that row's x into your equation. Did you get that row's "
                       "y? For an exact table it must match. For real measurements it "
                       "only has to come close."},
        ],
        "after": "**Then** answer the question actually asked — which is nearly "
                 "always *find f(something)*. That part is the next idea.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "Once you have the equation, it is a machine",
        "paragraphs": [
            "`f(700)` looks like something new. It is not. It means: **put 700 where "
            "the x is, and work out what comes out.** That is all. You have done this "
            "with y already; `f` is just a name for the machine so you can say which "
            "one you fed.",
            "So `f(x) = 0.1065x − 21.122` and `y = 0.1065x − 21.122` are the same "
            "sentence written twice. Asking for `f(700)` is asking for the y when x "
            "is 700.",
            "Two cautions when you feed it. **Multiply before you subtract** — the "
            "equation means (0.1065 × x) − 21.122, never 0.1065 × (x − 21.122). And "
            "when the answer comes out, **say what it is**: millimetres, grams, "
            "dollars. A bare number is not an answer.",
            "Saxon adds something worth hearing: do not get tangled up in the physics "
            "of springs. You have been given a function, given an input, and asked "
            "for the output. That is the job.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "77.1",
        "question": "The spring line is y = 0.1065x − 21.122, where x is the mass in "
                    "grams and y is the stretch in millimetres. How far does it "
                    "stretch under a 700 g mass? Round to 3 d.p.",
        "steps": [
            {"label": "What you have",
             "text": "A function, and an input of 700. In function language the "
                     "question is *find f(700)* — nothing more."},
            {"label": "Put 700 where the x is",
             "text": "Every x in the equation becomes 700. There is only one.",
             "math": "f(700) = 0.1065 × 700 − 21.122"},
            {"label": "Multiply first",
             "text": "Multiplication happens before subtraction. Always.",
             "math": "0.1065 × 700 = 74.55"},
            {"label": "Then subtract, and say the unit",
             "math": "74.55 − 21.122 = 53.428"},
        ],
        "answer": "53.428 mm",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 77.2 — five points in, one equation out",
        "equation": "(−2, 1)    (−1, 1.5)    (0, 2)    (3, 3.5)    (8, 6)",
        "steps": [
            {"label": "Look first",
             "text": "Five points and no equation anywhere. Saxon says this one fits "
                     "**exactly** — every point sits on the line — so any two of them "
                     "will give you the same slope."},
            {"label": "Step 1 · read b off the table",
             "text": "Look for the row where x is 0. Its y is 2. That is the height "
                     "the line starts at, so b is 2. You calculated nothing.",
             "math": "b = 2"},
            {"label": "Step 2 · how far up?",
             "text": "Take (0, 2) and (3, 3.5). The y went from 2 up to 3.5. That "
                     "rise is Δy — 'delta y', meaning the change in y.",
             "math": "Δy = 3.5 − 2 = 1.5"},
            {"label": "Step 3 · how far across?",
             "text": "Over the same two points, the x went from 0 across to 3.",
             "math": "Δx = 3 − 0 = 3"},
            {"label": "Step 4 · divide, up over across",
             "text": "The line climbs 1.5 for every 3 across — so half a step up for "
                     "every one step across.",
             "math": "m = 1.5 / 3 = 0.5"},
            {"label": "Step 5 · write it",
             "text": "The climb multiplies the x. The start gets added on.",
             "math": "y = 0.5x + 2"},
            {"label": "Step 6 · check it on a row you did not use",
             "text": "Try (8, 6), which you never touched. Put in 8 and see whether 6 "
                     "comes out. It does — the equation is right.",
             "math": "0.5 × 8 + 2 = 6"},
            {"label": "Step 7 · now answer what was asked",
             "text": "The question wanted f(7). Put 7 where the x is.",
             "math": "f(7) = 0.5 × 7 + 2 = 3.5 + 2 = 5.5"},
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "None of these are new ideas. They are short ways of writing things "
                 "you can already say in English.",
        "rows": [
            {"symbol": "y = mx + b", "plain": "climb times x, plus where it started",
             "example": "y = 0.5x + 2"},
            {"symbol": "b", "plain": "the y when x is 0 — the start", "example": "b = 2"},
            {"symbol": "m", "plain": "how much y moves when x moves 1",
             "example": "m = 0.5"},
            {"symbol": "Δ", "plain": "'delta' — change in",
             "example": "Δy is the change in y"},
            {"symbol": "Δy / Δx", "plain": "how far up, over how far across",
             "example": "1.5 / 3 = 0.5"},
            {"symbol": "f(x) = 0.1065x − 21.122", "plain": "the same sentence as y = …",
             "example": "the machine, named f"},
            {"symbol": "f(700)", "plain": "what comes out when you feed it 700",
             "example": "53.428 mm"},
        ],
        "after": "`f(700)` is **not** f multiplied by 700. `f` is the name of the "
                 "machine; the number in the brackets is what you put in.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Dividing across by up instead of up by across.",
             "wrong": "m = 3 / 1.5 = 2",
             "right": "m = 1.5 / 3 = 0.5",
             "note": "Slope is **rise over run** — the up part goes on top. Say "
                     "\"over\" out loud as you write it: change in y, *over*, change "
                     "in x. This one is nasty because 2 looks like a perfectly "
                     "respectable slope."},
            {"name": "Putting the two numbers in each other's slots.",
             "wrong": "y = 2x + 0.5",
             "right": "y = 0.5x + 2",
             "note": "**m multiplies the x. b stands alone on the end.** If the "
                     "starting height ended up glued to the x, swap them."},
            {"name": "Subtracting before multiplying.",
             "wrong": "0.1065 × (700 − 21.122) = 72.301",
             "right": "0.1065 × 700 − 21.122 = 53.428",
             "note": "That mistake is off by nearly 19 mm and it looks quite "
                     "plausible. There are no brackets in the equation, so the "
                     "multiplication happens first."},
            {"name": "Reading f as a number to multiply by.",
             "wrong": "f(700) = f × 700",
             "right": "f(700) = 0.1065 × 700 − 21.122",
             "note": "See the Translation table. `f` names the machine; the brackets "
                     "hold what you feed it."},
            {"name": "Expecting real measurements to sit exactly on the line.",
             "wrong": "a point misses the line → \"my equation must be wrong\"",
             "right": "a point misses the line → that is what real data does",
             "note": "For the spring data, points above and below the line are "
                     "**normal** — the line follows the trend. For the five-point "
                     "table it is different: that one is exact, so a miss really does "
                     "mean a mistake. Know which kind you are holding."},
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Example 77.2's points, with the climb between each pair",
        "headers": ["x", "y", "across (Δx)", "up (Δy)", "Δy / Δx"],
        "rows": [
            {"cells": ["-2", "1", "—", "—", "—"]},
            {"cells": ["-1", "1.5", "1", "0.5", "0.5"]},
            {"cells": ["0", "2", "1", "0.5", "0.5"], "emphasis": True},
            {"cells": ["3", "3.5", "3", "1.5", "0.5"]},
            {"cells": ["8", "6", "5", "2.5", "0.5"]},
        ],
        "note": "Read down the last column: **0.5 every single time**, whichever pair "
                "you use. That unchanging number is what makes it a straight line, "
                "and it is m. The shaded row is the one that hands you b for free.",
    }),

    (B.KIND_MATH, {
        "display": "y  =  m x  +  b",
        "note": "Two numbers is the whole line. **m** — how fast it climbs. "
                "**b** — where it starts. Find those two and you have written the "
                "equation.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Same spring, same equation, but an 850 g mass. How far does it "
                  "stretch? (Round to 3 d.p. — work it out before you open this.)",
        "answer": "**69.403 mm.** Put 850 where the x is: `0.1065 × 850 = 90.525`, "
                  "then `90.525 − 21.122 = 69.403`. Multiply first, subtract second, "
                  "and finish with the unit — *69.403* on its own is not an answer, "
                  "*69.403 mm* is.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**The points came first this time.** You are building the equation, not "
            "using one you were handed.",
            "Two numbers make a line: **b**, where it starts (the y when x is 0), and "
            "**m**, how fast it climbs (Δy / Δx — up over across).",
            "Write them into `y = mx + b`. The climb multiplies the x; the start is "
            "added on.",
            "Check your equation on a point you did not use.",
            "`f(700)` means **put 700 where the x is**. Multiply first, then subtract.",
            "Real data only *follows* the line. An exact table sits *on* it. Say the "
            "unit either way.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 77 first. If it didn't quite click, this is here to fix "
    "that. Everything you've graphed until now started with an equation and ended "
    "with points — this one goes the other way. You get the points, and you build "
    "the equation, out of just two numbers you can find on the table."
)

PARENT_CONTENT = """## The big idea

Two numbers describe any straight line, and this lesson is her first time
**finding them instead of being given them**.

- **b — where it starts.** The y value when x is 0. If the table has an x = 0 row,
  that row *is* b. No calculation.
- **m — how fast it climbs.** Change in y divided by change in x, from any two
  points. Up over across.
- Write them into `y = mx + b`, check on a point you didn't use, then answer the
  question — which is almost always *find f(something)*, i.e. substitute.

The two examples in the source:

- **Ex. 77.1** — the spring. `y = 0.1065x − 21.122`. `f(700) = 0.1065 × 700 −
  21.122 = 74.55 − 21.122` = **53.428 mm**. She is *given* the equation here; the
  only skill is substituting, which you have already taught her.
- **Ex. 77.2** — five points, `(−2, 1) (−1, 1.5) (0, 2) (3, 3.5) (8, 6)`. The
  (0, 2) row gives b = 2. Using (0, 2) and (3, 3.5): Δy = 1.5, Δx = 3, so
  m = 0.5. The equation is **y = 0.5x + 2**, and `f(7) = 3.5 + 2` = **5.5**.

Saxon's own hook, and the thing to say to her: in Lesson 68 the *points* were made
from the equation; from Lesson 74 on, the *equation* is made from the points.

## Teach it out loud in five minutes

Say these in this order, and ask the one question at each step before moving on.

1. Hang something stretchy off a pencil — a rubber band, a hair tie, a sock. Put
   one book in it. **"If one book stretches it this much, what will two books
   do?"** She'll say twice as much. *"Right. That steady climb is what makes it a
   line — and that climb is one of the two numbers we need."*
2. Draw a staircase on paper, three steps. **"How far up is one step? How far
   across?"** Say up 1, across 2. *"Up over across. That's the slope. Every line
   is a staircase and m is the size of its step."*
3. Point at where the staircase begins, on the left edge. **"How high is it before
   you've gone anywhere at all?"** *"That's b. The height when x is nothing."*
4. Now the real table. Show her the five points and ask **only** this: **"Which
   row gives you b with no work at all?"** Wait. Let it be uncomfortable. You want
   her to find the x = 0 row herself, because that is the move she'll reuse for
   the rest of algebra.
5. **"Pick any two rows. How far up? How far across?"** She gets 0.5. Then: **"Now
   pick a different two."** She gets 0.5 again. That surprise is the lesson — the
   climb is the same everywhere, which is exactly what "straight" means.
6. *"So write it: y = 0.5x + 2."* Then hand it back to what you already taught
   her: **"Now what's f(7)?"** She knows this part. Let her finish strong.

## The classic mix-ups, with what she'll actually write

- **`m = 3 / 1.5 = 2`** — run over rise instead of rise over run. It gives the
  equation `y = 2x + 2`, which misses every point except (0, 2). Dangerous because
  2 is a perfectly ordinary-looking slope; nothing about it screams wrong. The fix
  is verbal, not careful: make her say *"up, over, across"* while she writes it.
- **`y = 2x + 0.5`** — the right two numbers in each other's slots. Ask "which one
  is the step size?" The step size is the one touching the x.
- **`0.1065 × (700 − 21.122) = 72.301`** — subtracting before multiplying. Wrong
  by nearly 19 mm. There are no brackets in the equation; the multiplication goes
  first.
- **`f(700) = f × 700`** — reading f as a number. If she does this once she'll do
  it all year. Correct it the first time: f is the *name of the machine*.
- **"The point isn't on my line, so I did it wrong."** True for Ex. 77.2, which is
  exact — false for the spring data, where real measurements scatter either side
  of the trend. She needs to know which kind of problem she's holding.
- **Answering `53.428`** with no unit. Saxon takes marks for it.

## What to watch her do

Watch her **hands**, not her answer.

- On the slope: does her finger land on two rows and physically count across, then
  up? Or does she stare at the numbers and try to do it in her head? The counting
  is the skill. In-the-head is where the flipped fraction comes from.
- Does she **write b down first**, before touching the slope? If she starts hunting
  for the slope before b exists on the paper, stop her there — the x = 0 row is
  free information and skipping it is what makes the problem feel hard.
- Which two points does she pick? If she always grabs the two adjacent rows, hand
  her a table where the convenient pair isn't next to each other and see whether
  she still knows she may pick *any* two.
- At the end: does she go back and check a point she didn't use, without being
  asked? That is the habit this lesson is buying.

## Extend it

- **Do the actual experiment.** Rubber band, a ruler taped to the wall, four
  household weights (cans are labelled in grams). Measure, tabulate, build the
  equation, predict a fifth weight, then hang it and see. That *is* Ex. 77.1, in
  your kitchen, and it is the moment the topic stops being symbols.
- Ask what the two numbers **mean** in the spring problem: m = 0.1065 mm of
  stretch per gram hung. Then b = −21.122 mm — a negative stretch, which is
  nonsense for a real spring. **Ask her why.** The honest answer is that the line
  was fitted where the measurements actually live, not out at zero, so it has no
  business being trusted there. That is a genuinely grown-up idea and she can
  reach it.
- Give her the same table with one point deliberately nudged off, and ask whether
  the equation should change. (No — one stray point doesn't rewrite the trend.)

## Where this sits

DIVE Lecture 77. Reviews Lessons 68 and 70 (graphing an equation you were given —
the exact reverse of today), 73 (function families and `f(x)` notation) and 74
(spotting a linear trend in data and estimating its slope). If she is lost, **74
is the one to go back to** — Lesson 77 is Lesson 74 finished.

Note for you: the source shows the spring data as a scatter graph with a computer-
fitted trendline. Everything on her page comes from the equation and the printed
table instead, so nothing depends on being able to see that picture.

**Proficient** looks like: finds b from the table, gets m right with the recipe in
front of her, writes `y = mx + b` and substitutes correctly.
**Mastered** looks like: picks any two points without worrying about which,
checks the equation on an unused point unprompted, and can say what m *means* in
the units of the problem — "about a tenth of a millimetre for every gram."
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 77 (creating a linear equation) — idempotent."

    LESSON_NUMBER = 77
    TITLE = "This Time You Build the Equation — Creating a Linear Equation to Solve a Problem"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
