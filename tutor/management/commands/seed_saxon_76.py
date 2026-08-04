"""Saxon Pre-Algebra Lesson 76 — Domain and Range from Graphs; Dividing Terms
and Canceling.

Two topics in one lesson, so two IDEA blocks and two runs of worked examples.

Reviews Lessons 14, 26, 39, 61, 62, 66 and 73. Lesson 73 is the hook: she already
knows the seven function shapes by their faces, so 76A is not a new skill so much
as a new *question* asked of a face she can already recognise — how far does it
reach sideways, and how far does it reach up and down.

The figures in the DIVE guide are pictures this file cannot see, so every graph in
Examples 76.1 and 76.2 is rewritten from the guide's own SOLUTION text into words
that stand on their own: which parent shape it is, where its ends sit, and whether
each end is a filled or a hollow dot. No picture is described that was not
described first by the source.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_76 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

# The parent shapes from Lesson 73 that have something interesting to say about
# domain and range. `a^x` is here on purpose: Practice Set 76.2 hands her a curve
# that "never touches or crosses the x-axis", and this is that curve.
SHAPES = ["x", "x^2", "sqrt", "|x|", "1/x", "a^x"]

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 76 · Pre-Algebra",
        "title": "Sideways tells you the inputs. Up and down tells you the outputs.",
        "thesis": "A graph is a **picture of a machine**. Sweep left to right and you "
                  "have read every number it accepts. Sweep up and down and you have "
                  "read every number it can produce. You never solve anything.",
        "formula": "domain ↔        range ↕",
        "roles": [
            {"tone": "start", "name": "domain — sideways",
             "text": "Every x the graph actually covers. Read it left to right."},
            {"tone": "move", "name": "range — up and down",
             "text": "Every f(x) the graph actually reaches. Read it bottom to top."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone asks these two questions",
        "paragraphs": [
            "Think about the vending machine in a hallway. It takes quarters and "
            "dollar bills. It does not take buttons, and it does not take a fifty. "
            "And whatever you feed it, what falls out is a drink — never a sandwich, "
            "never your money back.",
            "Nobody prints that on the front of the machine. You work it out by "
            "looking at it. The list of things it will accept, and the list of things "
            "it can hand back, are two different lists — and knowing them is how you "
            "avoid standing there pushing a button that was never going to work.",
            "A function is a machine like that. The list of things you are allowed to "
            "put in is called the **domain**. The list of things that can come out is "
            "called the **range**.",
            "Here is the part the symbols hide. A graph is a *picture* of the machine, "
            "so you can read both lists straight off it. Nothing gets solved. Nothing "
            "gets substituted. You look sideways, then you look up and down.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 2, "tone": "start",
        "title": "Same question, asked twice, in two directions",
        "paragraphs": [
            "Every dot on a graph is a pair of instructions: go **across** this far, "
            "then go **up** this far. Across is the x you put in. Up is the f(x) that "
            "came back out.",
            "So if you want the inputs, put your finger at the far left and drag it "
            "right along the bottom. Ask: *where does the graph start, and where does "
            "it quit?* That answer is the domain.",
            "Then do exactly the same thing up the side, from the bottom to the top. "
            "*Where does it start, and where does it quit?* That answer is the range.",
            "Two sweeps. The same question both times. That really is the whole "
            "method — the only thing left is deciding what counts as \"quits\".",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Put your finger on the far left of the graph and drag it right. "
                "Tell me where the graph starts and where it quits — that's the "
                "domain. Now do it again, bottom to top, up the side. That's the "
                "range. And if your finger runs off the edge of the paper while the "
                "graph is still going, that direction is 'forever.'\"",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Five moves, every graph, same order",
        "steps": [
            {"label": "Sweep left to right.",
             "detail": "Find the leftmost point of the graph and the rightmost point. "
                       "Those two x values are the ends of the domain."},
            {"label": "At each end, ask: does it stop, or run off the edge?",
             "detail": "**Off the edge means forever.** Saxon says so explicitly: if "
                       "the line or curve touches an edge of the grid, assume it keeps "
                       "going that way and never stops."},
            {"label": "If it stops, look at the dot.",
             "detail": "A **filled** dot means that value is included, so you write "
                       "≤ or ≥. A **hollow** dot means it is left out, so you write "
                       "< or >. (That is Lesson 26 coming back.)"},
            {"label": "Now sweep bottom to top and do steps 1–3 again.",
             "detail": "Lowest point the graph reaches, highest point it reaches. Same "
                       "two questions about edges and dots. That gives you the range."},
            {"label": "Write it with the right letter.",
             "detail": "The domain is about inputs, so it is written with **x**. The "
                       "range is about outputs, so it is written with **f(x)**."},
        ],
        "after": "One warning about step 4 that catches nearly everyone: the range is "
                 "everything the graph *reaches*, not just what is happening at the "
                 "two ends. A graph that dips in the middle reaches the bottom of "
                 "that dip.",
    }),

    (B.KIND_TRANSLATION, {
        "title": "Saxon's shorthand, decoded",
        "intro": "None of this is new mathematics. It is compact notation for "
                 "sentences you can already say out loud.",
        "rows": [
            {"symbol": "R", "plain": "all the real numbers — every number on the "
                                     "number line, with no gaps",
             "example": "domain = all R"},
            {"symbol": "all R", "plain": "the graph runs off both side edges; every "
                                         "input works", "example": "a straight line"},
            {"symbol": "R≥0", "plain": "the real numbers from zero upward, zero "
                                       "included", "example": "√x lives here"},
            {"symbol": "≤", "plain": "less than or equal to — this endpoint IS "
                                     "included", "example": "a filled-in dot"},
            {"symbol": "<", "plain": "less than — this endpoint is NOT included",
             "example": "a hollow dot"},
            {"symbol": "−2 ≤ x < 4", "plain": "x starts at −2, counts −2 itself, and "
                                              "stops just short of 4",
             "example": "read it left to right"},
            {"symbol": "f(x)", "plain": "the output — the very same thing as y",
             "example": "range: −1 ≤ f(x) < 2"},
        ],
        "after": "The domain sentence is written about **x** and the range sentence is "
                 "written about **f(x)**. Swapping those two letters is the single "
                 "fastest way to get a right answer marked wrong.",
    }),

    (B.KIND_WORKED, {
        "number": "76.1",
        "question": "Three graphs, each one a parent shape from Lesson 73. Find the "
                    "domain and range of each.",
        "steps": [
            {"label": "a) a straight line that runs off all four edges",
             "text": "It has no breaks and no endpoints. Sweep sideways: it is still "
                     "going when it leaves the grid on both sides, so every input "
                     "works. Sweep up and down: same story. **Every** real number is "
                     "both an input and an output.",
             "math": "domain = range = all R"},
            {"label": "b) the square root curve, starting at the origin",
             "text": "This one sits entirely in Quadrant I. It begins at (0, 0) and "
                     "climbs off the grid to the right and upward. It never appears "
                     "left of zero and never dips below zero — so zero and the "
                     "positives, both directions.",
             "math": "domain = range = R≥0"},
            {"label": "c) the parabola, lifted so its bottom sits at y = 2",
             "text": "Both arms leave through the top of the grid, but they lean "
                     "outward as they go — the left arm is still travelling in the "
                     "−x direction and the right arm in the +x direction. So sideways "
                     "it covers everything; up and down it never gets below 2.",
             "math": "domain = all R, range = R≥2"},
        ],
        "answer": "domain = range = all R · domain = range = R≥0 · "
                  "domain = all R, range = R≥2",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 76.2a — a graph that actually stops",
        "equation": "a straight piece of graph, filled dot at (−2, −1), "
                    "hollow dot at (4, 2), and nothing beyond either one",
        "steps": [
            {"label": "Look first",
             "text": "This one does **not** run off the edges. It has two visible "
                     "ends, and the ends are drawn differently: one is filled in and "
                     "one is hollow. That difference is the entire question."},
            {"label": "Step 1 · sweep left to right",
             "text": "The leftmost point sits above x = −2. The rightmost sits above "
                     "x = 4. So the inputs run from −2 to 4 and no further."},
            {"label": "Step 2 · read the two dots",
             "text": "Left end **filled** — −2 is in. Right end **hollow** — 4 is out. "
                     "Say it aloud: \"greater than or equal to −2, and less than 4.\"",
             "math": "domain: −2 ≤ x < 4"},
            {"label": "Step 3 · sweep bottom to top",
             "text": "The lowest the graph ever gets is f(x) = −1, down at the filled "
                     "end. The highest is f(x) = 2, up at the hollow end. Nothing "
                     "below, nothing above."},
            {"label": "Step 4 · read the dots again",
             "text": "The bottom end is the filled one, so −1 is in. The top end is "
                     "the hollow one, so 2 is out. **Same two dots, second question.**",
             "math": "range: −1 ≤ f(x) < 2"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "76.2b",
        "question": "A V-shaped graph. Its bottom point sits at (0, 0). Its left end "
                    "is a hollow dot at (−4, 5); its right end is a filled dot at "
                    "(4, 4). Find the domain and range.",
        "steps": [
            {"label": "Sweep left to right",
             "text": "Leftmost x is −4 and it is **hollow**, so −4 is left out. "
                     "Rightmost x is 4 and it is **filled**, so 4 counts.",
             "math": "domain: −4 < x ≤ 4"},
            {"label": "Sweep bottom to top",
             "text": "Do not read the ends only. Between them the graph dives all the "
                     "way down to its point at f(x) = 0 — that is the lowest output "
                     "there is, and in this course the **vertex counts**. The highest "
                     "output is 5, up at the hollow end, so 5 is left out.",
             "math": "range: 0 ≤ f(x) < 5"},
        ],
        "answer": "domain: −4 < x ≤ 4 · range: 0 ≤ f(x) < 5",
    }),

    (B.KIND_TOOL, {
        "title": "Read the domain and range off the shapes you already know",
        "intro": "Tap a shape and it draws itself. Before you look at the answers "
                 "underneath, do the two sweeps out loud: finger along the bottom "
                 "first, then up the side. Remember that anything touching an edge of "
                 "the grid keeps going forever.",
        "widget": "grid",
        # `reference` — a gallery, not an exercise. Without it every tap answers
        # "plot the points from the table first" for a block that has no table.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "choices": SHAPES, "reference": True,
                   "label": "parent function shapes, for reading domain and range"},
        "after": "Answers, in the order of the buttons. **x**: domain all R, range all "
                 "R. **x²**: domain all R, range R≥0. **√x**: domain R≥0, range R≥0. "
                 "**|x|**: domain all R, range R≥0 — and note the sharp vertex at the "
                 "bottom is included. **1/x**: every real number *except* 0, for both "
                 "— it never touches either axis. **aˣ**: domain all R, but the range "
                 "is only the numbers **above** zero, because the curve creeps toward "
                 "the x-axis forever and never lands on it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "In 76.2b the two ends were at f(x) = 5 and f(x) = 4. So why is the "
                  "range 0 ≤ f(x) < 5 and not 4 ≤ f(x) < 5?",
        "answer": "Because the range is everything the graph **reaches**, not just "
                  "what is happening at its two ends. Between those ends the V dives "
                  "down to its point at zero, so it passes through every output from "
                  "0 up to 5 on the way. And zero itself is included: **for graphs in "
                  "this course, the vertex — the bottom of a V or a U — counts as part "
                  "of the range.** That is a house rule worth writing on your paper.",
    }),

    (B.KIND_TABLE, {
        "caption": "What each kind of end means",
        "headers": ["what you see at the end", "what it means", "how you write it"],
        "rows": [
            {"cells": ["filled-in dot", "that value IS included", "≤  or  ≥"],
             "emphasis": True},
            {"cells": ["hollow dot", "that value is NOT included", "<  or  >"],
             "emphasis": True},
            {"cells": ["the graph touches the edge of the grid",
                       "it keeps going that way forever", "all R (no endpoint at all)"]},
            {"cells": ["the bottom of a V or a U",
                       "the lowest output the graph reaches", "≤ — the vertex counts"]},
        ],
        "note": "The last row is a **house rule** for this course, not a law of "
                "mathematics: Shormann Pre-Algebra includes the vertex in the range. "
                "Write it on your paper so you are not deciding it fresh every time.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 2, "tone": "move",
        "title": "Second topic: cancel first, and terms that looked different match",
        "paragraphs": [
            "Sometimes you cannot add two terms because they do not look alike — and "
            "the only reason they do not look alike is that nobody has tidied them up "
            "yet. `3a` and `6ab²/b²` are the same size of thing. You just cannot see "
            "it while the b's are still sitting there.",
            "Canceling is division you do by crossing out. `b²` over `b²` is 1, so it "
            "vanishes. Lesson 39 did this same job with the quotient rule for "
            "exponents; canceling is that rule done by eye instead of by subtraction.",
            "**The trap is what you are allowed to cancel.** You may only cross out "
            "something that is multiplied all the way across the top *and* all the way "
            "across the bottom. `4a²b / ab` works because the top `a²b` is secretly "
            "`a × ab` — so the `ab` matches and goes. Never cancel one piece out of a "
            "sum.",
            "Then, and only then, add the like terms. Watch your invisible ones: after "
            "the canceling, `6ab²/b²` is `6a`, not `6`.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Don't add anything yet. First go through and cross out every "
                "matching factor you can see — top and bottom, top and bottom. Now "
                "read me what's left. Do they look like the same kind of thing now? "
                "Good. NOW add them.\"",
    }),

    (B.KIND_WORKED, {
        "number": "76.3a",
        "question": "Simplify by adding like terms:   3a + 6ab²/b² + 4a²b/ab",
        "steps": [
            {"label": "Second term first",
             "text": "There is a b² on the top and a b² on the bottom. They divide to "
                     "1, so both disappear and the a is left behind.",
             "math": "6ab²/b² = 6a"},
            {"label": "Third term: make the match visible",
             "text": "The bottom is ab, and there is no ab on top — until you notice "
                     "that a²b **is** a × ab. Rewrite it that way and the ab cancels.",
             "math": "4a²b/ab = 4 × (a × ab)/ab = 4a"},
            {"label": "Now everything matches, so add",
             "text": "All three terms are plain a terms. Add the numbers in front and "
                     "keep the a.",
             "math": "3a + 6a + 4a = 13a"},
        ],
        "answer": "13a",
    }),

    (B.KIND_WORKED, {
        "number": "76.3b",
        "question": "Simplify by adding like terms:   3a² − 5a³b/b + 4a³b/ab",
        "steps": [
            {"label": "Second term: a lone b over a lone b",
             "text": "One b on top, one b on the bottom. Gone.",
             "math": "−5a³b/b = −5a³"},
            {"label": "Third term: same trick as before, one power higher",
             "text": "The bottom is ab again. This time a³b is a² × ab, so the ab "
                     "cancels and a² is what survives.",
             "math": "4a³b/ab = 4 × (a² × ab)/ab = 4a²"},
            {"label": "Rearrange, then add only what genuinely matches",
             "text": "Now you have an a² term, an a³ term and another a² term. The two "
                     "a² terms are like terms. The a³ term is **not** — it stays "
                     "exactly as it is.",
             "math": "3a² + 4a² − 5a³ = 7a² − 5a³"},
        ],
        "answer": "7a² − 5a³",
    }),

    (B.KIND_MATH, {
        "display": "3a  +  6ab²/b²  +  4a²b/ab     =     3a + 6a + 4a     =     13a",
        "note": "Cancel, *then* add. In the middle line the three terms finally look "
                "like each other — and that middle line is the only reason the last "
                "one is allowed to happen.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Reading the domain up and down instead of sideways.",
             "wrong": "76.2a domain: −1 ≤ x < 2",
             "right": "76.2a domain: −2 ≤ x < 4",
             "note": "Those numbers, −1 and 2, are the *range*. Domain is a sideways "
                     "question — always. Drag your finger along the bottom, never up "
                     "the side, when you are answering it."},
            {"name": "Flipping the filled and hollow dots.",
             "wrong": "−2 < x ≤ 4",
             "right": "−2 ≤ x < 4",
             "note": "**Filled means it counts.** Say it out loud at each end before "
                     "you write anything: \"filled, so it's in — hollow, so it's out.\""},
            {"name": "Leaving the vertex out of the range.",
             "wrong": "0 < f(x) < 5",
             "right": "0 ≤ f(x) < 5",
             "note": "The bottom of the V is a real output — the graph genuinely "
                     "reaches it. In this course the vertex is included, so it takes "
                     "the ≤."},
            {"name": "Stopping the domain at the edge of the paper.",
             "wrong": "domain: −6 ≤ x ≤ 6",
             "right": "domain = all R",
             "note": "The grid has edges; the function does not. If the curve is still "
                     "going when it leaves the picture, it goes forever. Only a dot "
                     "stops a graph."},
            {"name": "Canceling a term instead of a factor.",
             "wrong": "4a²b/ab = 4ab",
             "right": "4a²b/ab = 4a",
             "note": "You may only cross out something multiplied across the *whole* "
                     "top and the *whole* bottom. Rewrite a²b as a × ab first, so you "
                     "can see the matching ab before you cross it out."},
            {"name": "Adding the exponents when adding like terms.",
             "wrong": "3a² + 4a² = 7a⁴",
             "right": "3a² + 4a² = 7a²",
             "note": "Exponents get added when you **multiply**. Adding like terms "
                     "only touches the numbers in front — three of something plus four "
                     "of that same something is seven of it."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Domain is sideways. Range is up and down.** Same question, two "
            "directions.",
            "Touches the edge of the grid → it goes on **forever** → all R that way.",
            "**Filled dot = in = ≤.  Hollow dot = out = <.**",
            "The range is everything the graph *reaches*, not just its two ends — and "
            "the **vertex counts**.",
            "Write the domain about `x` and the range about `f(x)`.",
            "For the second half: **cancel factors, never terms** — then add the like "
            "terms, and don't lose your invisible ones.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 76 first. If it didn't quite click, this is here to fix "
    "that — and to let you play with it. Two things today: reading a function's "
    "domain and range straight off its picture (no solving at all), and canceling "
    "so that terms which looked different turn out to be like terms after all."
)

PARENT_CONTENT = """## The big idea

Two separate topics share this lesson. Teach them as two things, in two sittings if
you can — they have nothing to do with each other.

**76A — domain and range from a graph.** She is not solving anything. She is
*reading*. Sweep left to right: that is the **domain** (the inputs). Sweep bottom to
top: that is the **range** (the outputs). The only judgement calls are at the ends:

- The graph **touches an edge of the grid** → it goes on forever that way → `all R`.
- The graph **stops at a filled dot** → that value is included → `≤` or `≥`.
- The graph **stops at a hollow dot** → that value is left out → `<` or `>`.
- **House rule for this course:** the vertex — the bottom of a V or a U — is
  *included* in the range. Saxon says so explicitly. Write it on her paper.

The three parent shapes from Example 76.1, which she already knows by face from
Lesson 73: a straight line gives `domain = range = all R`; the square root curve
gives `domain = range = R≥0`; the parabola lifted to sit on y = 2 gives
`domain = all R` but `range = R≥2`.

**76B — canceling.** Terms that look different can be the same kind of thing once
you cancel. `3a + 6ab²/b² + 4a²b/ab` becomes `3a + 6a + 4a`, which is **13a**. The
one rule that matters: you may only cancel a **factor** — something multiplied
across the whole top and the whole bottom. `4a²b/ab` works because `a²b` is `a × ab`.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. **"What does a vending machine take, and what does it give back?"** Let her
   answer. *"Those are two different lists. Every machine has two lists. In maths
   they're called the domain and the range."* Do this before any symbol appears —
   this is the part the video skipped.
2. Draw a straight line right across a sheet, off both edges. **"Put your finger on
   the far left and drag it right. Where does this line start? Where does it quit?"**
   She should say it doesn't. *"Right — so every number works. That's 'all R'."*
3. Now draw a short piece of line with a **filled** blob at the left end and a
   **hollow** circle at the right. **"Which end counts?"** Tell her plainly: filled
   means in, hollow means out. Have her say it out loud twice. This is worth more
   drill than anything else in the lesson.
4. Draw a V sitting on the x-axis with its two ends up in the air. **"What's the
   smallest number this graph ever reaches?"** She will often say one of the end
   values. Point at the bottom of the V. *"It goes down to here in the middle. The
   range is everything it touches, not just the ends."*
5. Switch topics. Write `6ab²/b²` and ask **"What can you cross out?"** Then write
   `4a²b/ab` and ask the same. When she is stuck, write `a²b` as `a × ab` and ask
   again — she will see it. Finish with **"Now do they look like the same kind of
   thing? Then add them."**

## The classic mix-ups, with what she'll actually write

- **Domain read up and down.** For 76.2a she writes `−1 ≤ x < 2` — those are the
  *range* numbers with an x in front. The fix is physical, not verbal: her finger
  must move along the bottom while she answers the domain.
- **Filled and hollow flipped.** She writes `−2 < x ≤ 4` instead of `−2 ≤ x < 4`.
  Have her touch each dot and say "in" or "out" before she writes the line.
- **Vertex left out.** She writes `0 < f(x) < 5` instead of `0 ≤ f(x) < 5`. She has
  applied the hollow-circle logic to a place where there is no circle at all.
- **Range read from the two ends only.** For 76.2b she writes `4 ≤ f(x) < 5`, using
  the two endpoint heights and forgetting the graph dives to 0 between them.
- **Domain stopped at the edge of the paper** — `−6 ≤ x ≤ 6` instead of `all R`.
  The grid has edges; the function doesn't.
- **Canceling a term, not a factor** — `4a²b/ab = 4ab`. And its cousin, adding
  exponents while adding like terms: `3a² + 4a² = 7a⁴` instead of `7a²`.

## What to watch her do

Watch her **hands, in this order**: finger along the bottom edge first, then up the
side. If she is staring at the middle of the graph and thinking, she is trying to
*work it out* — and there is nothing to work out. The sweep is the method, and when
it becomes automatic the whole topic takes ten seconds per problem.

Second thing to watch: does she **touch each endpoint dot** before writing the
inequality? A child who points at the dot and says "filled, so it's in" almost never
gets the symbol backwards. A child who writes from memory of the shape does, about
half the time.

On the canceling half, watch whether she **crosses things out before she adds**. If
her pencil goes straight to the addition, she is guessing which terms are alike
instead of finding out.

## Extend it

Draw her a graph with a *break* in it — a curve that exists from −5 to −1 and again
from 1 to 5, with nothing in between — and ask for the domain. The honest answer is
two pieces joined by "or", and having to say that out loud teaches her what the
domain actually is better than any continuous graph can. (Lesson 66A did the
discontinuous case; this lesson deliberately stayed continuous.)

Then, for the second half, hand her `5x²y/xy + 3x` and let her discover that it is
`8x`. Nothing new — but it is the first time canceling has paid her back with a
one-term answer, and that lands.

## Where this sits

**DIVE Lecture 76.** Reviews Lessons 14, 26, 39, 61, 62, 66 and 73. If she is lost,
the two to revisit are **26** (the inequality symbols and the open/closed circle
convention — that is where `≤` versus `<` was taught) and **73** (the seven function
shapes; 76A asks a new question about faces she met there). **39** is the quotient
rule for exponents, which is the second half of this lesson in different clothing.

**Proficient** looks like: reads the domain and range off a graph with endpoints,
gets the symbols the right way round with a moment's thought, and cancels correctly
when told to cancel.
**Mastered** looks like: does the two sweeps without being prompted, says "that one's
hollow so it's out" as she writes, remembers the vertex is included, and cancels
*before* trying to add without being reminded.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 76 (domain and range from graphs; "
            "dividing terms and canceling) — idempotent.")

    LESSON_NUMBER = 76
    TITLE = ("Sideways and Up-and-Down — Domain and Range from Graphs, "
             "and Canceling to Find Like Terms")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
