"""Saxon Pre-Algebra Lesson 83 — More on Linear Functions: Linear Inequalities.

Reviews Lessons 26, 79, 80 and 82. Lesson 79 is the hook and it is the strong
one: 79 taught her to read `m` and `b` off a drawn line, and 83 is that same job
with two extra questions asked first — is the line dashed or solid, and which
side is shaded. Nothing about finding the slope or the intercept changes. The
book's own solution says it out loud: "Solve just like problems from Lesson 79,
except here you have an inequality symbol."

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. The book's pages are not copied here. Where the book prints a graph
this page REDRAWS it with the grid widget from the facts the book's own solution
states — Example 83.1a is dashed / shaded below / crosses at 2 / slope 1, and
83.1b is solid / shaded above / crosses at 1 / slope -2, and those facts pin the
picture down completely. The two lattice points the steps land on, (1, 3) in
83.1a and (1, -1) in 83.1b, are NOT named by the book: they follow from the slope
and intercept it does name, and on this page she reads them off the redrawn
board rather than being told them.

Example 83.2's four answer choices and practice problem 383's four choices are
not reproduced: 83.2 is worked as far as the inequality (which is what decides
the choice), and 383 appears here as the same question with a different constant,
so the problem in her practice set survives for her to do.

The clickable board ships its own inequality, deliberately the one combination
NONE of the book's three examples draws (solid line, shaded below), so no worked
example can be pattern-matched into a rule.

    python manage.py seed_saxon_83 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

# The inequality on the practice board: y ≤ 0.5x + 1.
#
# Chosen for three reasons. The slope is gentle enough that the whole boundary
# stays inside a -6..6 window, so the dashes-versus-solid question is decided by
# looking rather than by squinting at a corner. It passes through (0, 1) and
# (2, 2), both lattice points, so the Lesson 79 staircase lands exactly. And
# solid-with-shading-below is the one pairing NONE of the book's three examples
# draws: 83.1a is dashed/below, 83.1b is solid/above, and 83.2 is dashed/above —
# so a child who has quietly decided that "dashed goes with below" gets caught
# here rather than on a test.
BOARD = {"m": 0.5, "b": 1, "op": "le", "ask": True}

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 83 · Pre-Algebra",
        "title": "When the answer is a whole region, not a line",
        "thesis": "An equation draws a **line**. An inequality shades a whole "
                  "**side** of it. Same two numbers as Lesson 79 — you just have two "
                  "more questions to answer first: is the line dashed or solid, and "
                  "which side is shaded?",
        "formula": "y < mx + b   ·   y ≤ mx + b   ·   y > mx + b   ·   y ≥ mx + b",
        # These two fields are rendered plain, with no markdown pass — so the
        # emphasis is written in CAPITALS. Asterisks here would reach her as
        # literal asterisks, on the two sentences that ARE the lesson.
        "roles": [
            {"tone": "start", "name": "the line — dashed or solid",
             "text": "Dashed means the line itself is NOT part of the answer "
                     "(< and >). Solid means it IS (≤ and ≥)."},
            {"tone": "move", "name": "the shading — above or below",
             "text": "Greater than means shaded ABOVE the line. So less than "
                     "means shaded BELOW it."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone would want a whole region instead of a line",
        "paragraphs": [
            "Say you have twenty dollars. Notebooks are two dollars each and pens "
            "are one dollar each. How many can you buy?",
            "There is no single answer, and that is the point. Four notebooks and "
            "twelve pens works. Two notebooks and three pens works, and leaves money "
            "in your pocket. Nine notebooks and four pens does not. What you actually "
            "have is a **whole collection of answers that work**, and one edge where "
            "you spend exactly twenty and not a cent more.",
            "Draw that on graph paper and the edge is a line — the exact-twenty "
            "line. Everything you can afford is the **region** on one side of it. "
            "That region is the answer, and a line on its own cannot say it.",
            "So this lesson gives you a way to write a region down. It is the same "
            "`y = mx + b` you already know, with the equals sign swapped for one of "
            "four symbols. The symbol is what turns one line into one half of the "
            "whole page.",
            "And here is the part worth knowing before you start. **You already know "
            "how to find m and b.** That was Lesson 79 and it does not change one "
            "bit here. Everything new in this lesson is about the *picture* — two "
            "questions you ask before you count anything.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "A line is a fence. An inequality is the field.",
        "paragraphs": [
            "When you graph `y = x + 2` you get a line, and only the points sitting "
            "exactly on it are answers. Nothing else counts.",
            "When you graph `y < x + 2` the line is still there — but now it is a "
            "**fence**, and the answer is the entire field on one side of it. Every "
            "point in that field, all the way to the edge of the paper and past it. "
            "There are infinitely many, so nobody lists them. You shade them.",
            "That is the whole change, and the book says so on its first page: a "
            "linear equation represents a **line**, a linear inequality represents a "
            "**region**. Same fence in both pictures. The inequality just also tells "
            "you which field, and whether the fence itself is in it.",
            "So a finished answer here has three pieces of information in it, not "
            "two. Where the fence is (that is `b`), which way it leans (that is `m`), "
            "and which symbol goes in the middle — because the symbol is carrying "
            "*both* of the new facts at once.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"An equals sign means the answer is exactly on the line. Any other "
                "symbol means the answer is a whole side of the page. Look at the "
                "picture and tell me two things before you tell me any numbers: is "
                "that line dashed or solid, and is the shading above it or below it?\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "start",
        "title": "The line: dashed or solid asks one question only",
        "paragraphs": [
            "**Is the fence itself part of the field?**",
            "If it is not, the line is drawn **dashed** — broken up, so it looks like "
            "a boundary you are not allowed to stand on. That is `<` and `>`. The "
            "book's word for why: those inequalities \"don't include the value.\"",
            "If it is, the line is drawn **solid**. That is `≤` and `≥`, which you "
            "read as \"less than **or equal to**\" and \"greater than **or equal to**.\" "
            "The \"or equal to\" half is exactly the points sitting on the line, and a "
            "solid line is how the picture says they count.",
            "So the bar underneath the symbol and the solidness of the line are the "
            "same fact written twice. A bar under the symbol ⇄ a line with no gaps in "
            "it. Once you see them as one thing you stop having to remember them as "
            "two.",
            "This page asks you to read this half **first**, before you look at the "
            "shading — because it is decided by the line alone, so nothing else in "
            "the picture can confuse it. That is a habit, not a law. Saxon's own "
            "printed solutions happen to mention the shading first and the line "
            "second, and the answer comes out the same either way. What matters is "
            "that you answer the two questions **separately**, not which one you "
            "answer first.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "move",
        "title": "The shading: memorize one half and the other is free",
        "paragraphs": [
            "The book gives you one sentence to memorize, and it is deliberately only "
            "half the rule: **\"greater than means shaded above.\"**",
            "Memorize that one. Then, in the book's own words, \"by default you'll "
            "remember that less than means shaded below.\" One fact, not two — the "
            "other one is what is left over.",
            "It also makes sense if you look at it. `y > x + 2` says: *my y is bigger "
            "than the line's y at that same x*. Bigger y means higher up the page. So "
            "the answers sit **above** the line. Being higher up **is** what greater "
            "means, once y is by itself on the left.",
            "That last phrase is doing real work. \"Greater than means above\" is only "
            "true when **y is alone on the left-hand side**. If the problem hands you "
            "something like `x + y > 2`, y is not alone yet, and you have no business "
            "reading the picture until it is. Rearrange first. Every time.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Six moves, the same way every time",
        "steps": [
            {"label": "Write the standard form down first, with a blank where the "
                      "symbol goes.",
             "detail": "`y ▢ mx + b`, before you look at the graph. **Standard form** "
                       "is Saxon's own name for it — \"the standard form is therefore "
                       "y < mx + b\" — the same words Lesson 79 used and the words "
                       "your practice set will use, so it is worth saying out loud. "
                       "Three empty boxes now instead of two, and the symbol box is "
                       "the one that is actually new, so give it somewhere to live."},
            {"label": "Look at the LINE. Dashed or solid?",
             "detail": "Dashed → the symbol has **no bar**, so it is `<` or `>`. "
                       "Solid → the symbol **has a bar**, so it is `≤` or `≥`. You "
                       "have now cut four choices down to two, and you have not "
                       "looked at the shading yet."},
            {"label": "Look at the SHADING. Above or below?",
             "detail": "Above → **greater** than. Below → **less** than. That is the "
                       "book's memorized half and its leftover half. Two choices "
                       "down to one: you now know the symbol exactly."},
            {"label": "Write that symbol into the blank.",
             "detail": "Do it now, while you are still looking at the picture that "
                       "told you. Everything from here is Lesson 79 and it will pull "
                       "your attention onto the numbers."},
            {"label": "Read b, then walk the staircase for m.",
             "detail": "Exactly as in Lesson 79, and nothing about it changes here. "
                       "`b` is where the line crosses the up-and-down axis — you look, "
                       "you do not calculate. Then from that point: **rise first, then "
                       "run**, and the run always goes right. **m = rise / run**."},
            {"label": "Read your answer back against the picture, both halves.",
             "detail": "Point at the line and say \"dashed, so no bar — yes.\" Point at "
                       "the shading and say \"above, so greater than — yes.\" Two "
                       "checks, four seconds, and they catch the two mistakes this "
                       "lesson actually produces."},
        ],
        "after": "If the question gives you **words or an equation instead of a "
                 "graph** — \"the sum of all x + y values greater than 2\" — then there "
                 "is one move before all of this: get **y alone on the left**. Until y "
                 "is by itself, \"greater than means above\" is not a rule you are "
                 "allowed to use.",
    }),

    (B.KIND_MATH, {
        "display": "y = mx + b   →   y < mx + b",
        "note": "The equals sign is the only thing that changed, and it changed the "
                "answer from a line into half a page. Write `y ▢ mx + b` down before "
                "you look at the graph — same habit as Lesson 79, one more blank.",
    }),

    (B.KIND_TOOL, {
        "title": "The graph for Example 83.1a",
        "intro": "Here is the graph your book prints for 83.1a. It is not a copy of "
                 "the book's page — it is **redrawn** from what the book's own "
                 "solution says the picture shows: a dashed line, the region below it "
                 "shaded, crossing the up-and-down axis at 2. There is nothing to "
                 "click on this one; it is the question, not a toy. Open your book "
                 "beside it and check that the two pictures agree, then work the "
                 "steps underneath while you look at it.",
        "widget": "grid",
        # A GIVEN figure. `readonly` strips the controls entirely, so there is no
        # Undo or Clear to wipe the drawing she is supposed to be reading — the
        # same protection `locked` gives the given dots in Lessons 77 and 79.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "inequality": {"m": 1, "b": 2, "op": "lt"},
                   "readonly": True,
                   "label": "Example 83.1a: a dashed line crossing at 2, shaded below"},
    }),

    (B.KIND_STEPPER, {
        "title": "Example 83.1a — dashed, and shaded below",
        "equation": "dashed line   ·   shaded below   ·   crosses the y-axis at 2",
        "steps": [
            {"label": "Look first",
             "text": "Everything you need is on the board just above. The three facts "
                     "along the top of these steps are the ones the book's own "
                     "solution names; the rest you read off the picture yourself. "
                     "Notice how much of the work is **looking**: two of those three "
                     "facts are not numbers at all."},
            {"label": "Step 1 · write the standard form",
             "text": "Nothing to do with this graph yet. Three blanks, and the middle "
                     "one is the new one.",
             "math": "y ▢ mx + b"},
            {"label": "Step 2 · look at the line",
             "text": "It is **dashed**. So the line itself is not part of the answer, "
                     "which means no bar under the symbol. You are down to `<` or `>` "
                     "and you have not thought about the shading once.",
             "math": "dashed  →  < or >"},
            {"label": "Step 3 · look at the shading",
             "text": "It is shaded **below** the line. Greater than means above, so "
                     "less than means below — and below is what you are looking at. "
                     "The symbol is `<`. Write it into the blank right now.",
             "math": "y < mx + b"},
            {"label": "Step 4 · read b off the axis",
             "text": "From here on this is Lesson 79 and nothing is new. The line "
                     "crosses the up-and-down axis at 2, so b is 2. You looked; you "
                     "did not work it out.",
             "math": "b = 2  →  y < mx + 2"},
            {"label": "Step 5 · walk the staircase for m",
             "text": "Start your finger at (0, 2) on the board above. Go **up 1**, "
                     "then **right 1**, and you land on (1, 3) — check it: the line "
                     "goes exactly through that corner. Rise 1, run 1.",
             "math": "m = rise / run = 1/1 = 1"},
            {"label": "Step 6 · fill it in and check both halves",
             "text": "A slope of 1 is written as plain `x`, not `1x`. Now read it back "
                     "against the picture twice: dashed line, no bar under the symbol "
                     "— agrees. Shaded below, less-than symbol — agrees.",
             "math": "y < x + 2"},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "The graph for Example 83.1b",
        "intro": "The same again for 83.1b — **redrawn**, not copied, from what the "
                 "book's solution says its picture shows: a solid line, the region "
                 "above it shaded, crossing the up-and-down axis at 1. Look at it "
                 "before you read a single step, and say the two facts out loud.",
        "widget": "grid",
        # Given figure, `readonly` for the same reason as 83.1a's board.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "inequality": {"m": -2, "b": 1, "op": "ge"},
                   "readonly": True,
                   "label": "Example 83.1b: a solid line crossing at 1, shaded above"},
    }),

    (B.KIND_WORKED, {
        "number": "83.1b",
        # `question` is rendered plain, with no markdown pass, so emphasis here is
        # written in CAPITALS — asterisks would show up as asterisks in an <h2>.
        "question": "The board just above is the graph your book prints for 83.1b, "
                    "redrawn from the book's own description of it: the line is "
                    "SOLID, the region ABOVE it is shaded, and it crosses the y-axis "
                    "at 1. Write the inequality.",
        "steps": [
            {"label": "Write the standard form",
             "text": "Same first move as always. Blank in the middle.",
             "math": "y ▢ mx + b"},
            {"label": "Look at the line",
             "text": "**Solid.** The book's reason: \"the solid line means we include "
                     "values on the line.\" So the symbol carries a bar — `≤` or `≥`.",
             "math": "solid  →  ≤ or ≥"},
            {"label": "Look at the shading",
             "text": "Shaded **above**. Greater than means shaded above — that is the "
                     "one sentence you memorized. Put it together with the bar and "
                     "there is exactly one symbol left.",
             "math": "y ≥ mx + b"},
            {"label": "Read b",
             "text": "It crosses the up-and-down axis at 1. That is b, and it cost you "
                     "nothing.",
             "math": "b = 1  →  y ≥ mx + 1"},
            {"label": "Which way does it lean?",
             "text": "It **falls** as you move right, so m is going to be negative. "
                     "Decide that before you count, so your answer has something to "
                     "agree with."},
            {"label": "Walk the staircase",
             "text": "From (0, 1) on the board above, go **down 2**, then **right 1**, "
                     "and you land on (1, -1) — a corner the line goes exactly "
                     "through, so check it with your finger. Down makes the rise "
                     "negative; the run always goes right, so it stays positive.",
             "math": "m = rise / run = -2/1 = -2"},
            {"label": "Fill it in and check both halves",
             "text": "Negative m for a falling line — agrees. Solid line, bar under "
                     "the symbol — agrees. Shaded above, greater-than — agrees. Three "
                     "for three, so you are done.",
             "math": "y ≥ -2x + 1"},
        ],
        "answer": "y ≥ -2x + 1",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Saxon writes this whole lesson in about six characters. Here is what "
                 "each one is short for, and which half of the picture it is talking "
                 "about.",
        "rows": [
            {"symbol": "y ▢ mx + b",
             "plain": "Saxon's STANDARD FORM — the shape every answer in this lesson "
                      "gets written in, with the box where the symbol goes",
             "example": "y < x + 2"},
            {"symbol": "<",
             "plain": "strictly less than — DASHED line, shaded BELOW",
             "example": "y < x + 2   (Ex. 83.1a)"},
            {"symbol": "≤",
             "plain": "less than OR EQUAL TO — SOLID line, shaded BELOW",
             "example": "y ≤ 0.5x + 1   (the board below)"},
            {"symbol": ">",
             "plain": "strictly greater than — DASHED line, shaded ABOVE",
             "example": "y > -x + 2   (Ex. 83.2)"},
            {"symbol": "≥",
             "plain": "greater than OR EQUAL TO — SOLID line, shaded ABOVE",
             "example": "y ≥ -2x + 1   (Ex. 83.1b)"},
            {"symbol": "a dashed line",
             "plain": "the points ON the line are NOT answers",
             "example": "goes with < and >"},
            {"symbol": "a solid line",
             "plain": "the points ON the line ARE answers",
             "example": "goes with ≤ and ≥"},
            {"symbol": "x + y > 2",
             "plain": "not the shape yet — y is not alone, so you may not read the "
                      "picture from it",
             "example": "rearranges to  y > -x + 2"},
        ],
        "after": "The bar under the symbol and the solidness of the line are **the "
                 "same fact**. So are \"greater\" and \"above\". Two facts total, each "
                 "written in two places — which is why a finished answer can always be "
                 "checked against the picture twice.",
    }),

    (B.KIND_TABLE, {
        "caption": "All four symbols, and the picture each one draws",
        "headers": ["symbol", "the line", "the shading", "this lesson's example"],
        "rows": [
            {"cells": ["<", "dashed", "below", "y < x + 2"], "emphasis": True},
            {"cells": ["≤", "solid", "below", "y ≤ 0.5x + 1"]},
            {"cells": [">", "dashed", "above", "y > -x + 2"]},
            {"cells": ["≥", "solid", "above", "y ≥ -2x + 1"], "emphasis": True},
        ],
        "note": "The two shaded rows are the two graphs the book asks you to **read**, "
                "83.1a and 83.1b. Look at what they have in common: **nothing**. One "
                "is dashed and below, the other solid and above — so anyone who works "
                "only those two can walk away believing dashed always goes with "
                "below. It does not, and the third row proves it: `>` is dashed and "
                "shaded above, and that is Example 83.2 — though you got there by "
                "rearranging a sentence, not by looking at a picture. The second row, "
                "`≤`, is the one pairing the book never draws at all. That is exactly "
                "what the clickable board further down is.",
    }),

    (B.KIND_WORKED, {
        "number": "83.2",
        "question": "\"Which of the following graphs represents the sum of all x + y "
                    "values greater than 2?\" The book offers four graphs, which this "
                    "page cannot reprint — so answer the question underneath the "
                    "question instead: what inequality would the right graph have to "
                    "be showing, and what would it look like? (Saxon's answer is "
                    "Choice B.)",
        "steps": [
            {"label": "Turn the sentence into symbols",
             "text": "\"The sum of x and y\" is `x + y`. \"Greater than 2\" is `> 2`. "
                     "The book asks the same thing of you: \"Do you see the question is "
                     "asking us to graph x + y > 2?\"",
             "math": "x + y > 2"},
            {"label": "Stop. It is not in the shape yet.",
             "text": "y is not alone on the left, so **none** of the picture rules "
                     "apply yet. This is the moment the whole problem turns on, and it "
                     "is why the book says to \"be observant and realize that x + y > 2 "
                     "is just a different form\" of what you already know."},
            {"label": "Add -x to both sides",
             "text": "The same move you have made on equations since Lesson 26 — "
                     "whatever you do to one side you do to the other. On the left, "
                     "-x and +x cancel and leave y by itself. Adding does **not** "
                     "flip the symbol; only multiplying or dividing by a negative does "
                     "that, which is the Lesson 82 rule.",
             "math": "-x + x + y > -x + 2  →  y > -x + 2"},
            {"label": "Now read the picture off it",
             "text": "`>` with no bar, so the line is **dashed**. `>` is greater than, "
                     "so the shading is **above**. Then the two numbers: b is 2 and m "
                     "is -1. The book's own description of Choice B — \"the dashed line "
                     "with a slope = -1 and y-intercept = 2\" — is exactly those four "
                     "things.",
             "math": "y > -x + 2"},
        ],
        "answer": "y > -x + 2",
    }),

    (B.KIND_TOOL, {
        "title": "Read one off yourself",
        "intro": "An inequality is already drawn on the board: a boundary line and a "
                 "shaded region. Nothing here can be rubbed out — the picture is the "
                 "question, so it stays put. Look, and answer the two questions in "
                 "order. **Is the line dashed or solid?** Then: **is the shading above "
                 "the line or below it?** Only then pick one of the four buttons "
                 "underneath. If you get it wrong the board tells you which half to go "
                 "back and look at — and if both halves are wrong it names the line "
                 "one, because that is the half to settle first. Then do one more "
                 "thing on your own: pick a point off the picture with your eye — say "
                 "(4, 0) — and say out loud whether it is inside the answer or "
                 "outside it.",
        "widget": "grid",
        # No `points` and no `table`: this lesson is not about plotting. The
        # question IS the drawn region, and the `inequality` key is what draws it.
        # `ask` puts the four symbols under the board and — the reason for using it
        # here — names WHICH half she got wrong, dashed-versus-solid or
        # above-versus-below. "Try again" would teach her nothing, because the two
        # halves are two independent facts and a child usually has one of them right.
        # `readonly` because Undo and Clear both empty the layer the region and the
        # boundary are drawn into, and nothing redraws them: one stray tap and the
        # question itself is gone until she reloads the page. It leaves the four
        # answer buttons alone — they are appended outside the control row.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "inequality": BOARD,
                   "readonly": True,
                   "label": "a linear inequality to name"},
        "after": "Then finish the job the buttons do not do: find **b** and **m** the "
                 "Lesson 79 way and write the whole inequality out on paper. It crosses "
                 "the up-and-down axis in an obvious place. From there walk the "
                 "staircase exactly as step 5 says — **rise first, then run**. Go "
                 "**up 1**. You are not back on the line yet, so keep walking right "
                 "until you are, and count how far you went: that count is the run, "
                 "and this time it is not 1. The answer is in the drop-down below — "
                 "predict before you open it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "What is the inequality shown on the board?",
        "answer": "`y ≤ 0.5x + 1`. Three separate reads, in this order. **One:** the "
                  "line is **solid**, so the boundary belongs to the answer and the "
                  "symbol carries a bar — ≤ or ≥. **Two:** the shading sits **below** "
                  "the line, and below means less than, so it is ≤. **Three:** now read "
                  "the line itself exactly the way you did in Lesson 79. It crosses the "
                  "up-and-down axis at 1, so `b` is 1. From (0, 1) go **up 1** — you are "
                  "at (0, 2) and not on the line yet — then **right 2**, and you land on "
                  "(2, 2), which is back on it. So the rise is 1, the run is 2, and `m` "
                  "is one half — 0.5. Put the three together and you have `y ≤ 0.5x + 1`. "
                  "Notice what this one is: **solid and shaded below**. Not one of the "
                  "book's three examples looks like that.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Dashed line, but she writes the symbol with a bar.",
             "wrong": "dashed line, shaded below  →  y ≤ x + 2",
             "right": "dashed line, shaded below  →  y < x + 2",
             "note": "The bar under the symbol means \"or equal to\" — the points **on** "
                     "the line. A dashed line is the picture saying those points do "
                     "not count. Bar and solid line are one fact; you cannot have one "
                     "without the other."},
            {"name": "Solid line, but she writes the strict symbol.",
             "wrong": "solid line, shaded above  →  y > -2x + 1",
             "right": "solid line, shaded above  →  y ≥ -2x + 1",
             "note": "Same fact the other way round. A solid line has no gaps, which "
                     "is the picture saying the boundary is included, which is the "
                     "bar. Decide this half **before** you look at the shading, so "
                     "the two questions cannot contaminate each other."},
            {"name": "Getting the line right and the side backwards.",
             "wrong": "solid line, shaded above  →  y ≤ -2x + 1",
             "right": "solid line, shaded above  →  y ≥ -2x + 1",
             "note": "This is the one the memorized sentence exists for: **greater "
                     "than means shaded above**. Say it, then take the other one for "
                     "free. Quick catch: put your finger on a shaded point well above "
                     "the line and ask whether its y is bigger or smaller than the "
                     "line's."},
            {"name": "Reading the picture off x + y > 2 without rearranging.",
             "wrong": "x + y > 2  →  slope 1, intercept 2  →  y > x + 2",
             "right": "x + y > 2  →  -x + x + y > -x + 2  →  y > -x + 2",
             "note": "The slope is **-1**, not 1, and the wrong version leans the "
                     "opposite way from the right one. \"Greater than means above\" and "
                     "\"b is where it crosses\" are only true once **y is alone on the "
                     "left**. Until then you are reading numbers off a sentence that "
                     "is not in the right shape."},
            {"name": "Flipping the symbol while rearranging.",
             "wrong": "x + y > 2  →  y < -x + 2",
             "right": "x + y > 2  →  y > -x + 2",
             "note": "This comes from Lesson 82 half-remembered. The flip rule is "
                     "real, but it fires only when you **multiply or divide by a "
                     "negative**. Adding -x to both sides is adding, so nothing flips. "
                     "The wrong version shades the whole opposite half of the page."},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "383's twin",
        "question": "Problem 383 in your practice set asks which graph represents the "
                    "sum of all x + y values greater than or equal to -1. That one "
                    "stays yours to do, so it is not worked here. Worked here instead "
                    "is its twin, the same question with a different number: which "
                    "graph represents the sum of all x + y values greater than or "
                    "equal to 3? Write it in standard form, then describe exactly what "
                    "the right graph has to look like.",
        "steps": [
            {"label": "Sentence into symbols",
             "text": "\"The sum of x and y\" is `x + y`. \"Greater than or equal to 3\" "
                     "is `≥ 3` — and the words **or equal to** are already telling you "
                     "the line will be solid, before you have done any algebra at all.",
             "math": "x + y ≥ 3"},
            {"label": "Get y alone",
             "text": "Add -x to both sides, exactly as in 83.2. Adding does not flip "
                     "the symbol, so it is still `≥` when you are done.",
             "math": "-x + x + y ≥ -x + 3  →  y ≥ -x + 3"},
            {"label": "Describe the graph you are looking for",
             "text": "`≥` has a bar, so the line is **solid**. `≥` is greater than, so "
                     "the shading is **above**. b is 3, so it crosses the up-and-down "
                     "axis three squares **above** the middle. m is -1, so it **falls** "
                     "one square for every square right. Four facts, and the right "
                     "graph is the one that is all four.",
             "math": "y ≥ -x + 3"},
            {"label": "Now go and do 383",
             "text": "383 is this, with -1 where the 3 is. Not one step of the method "
                     "changes — the only thing that moves is where the line crosses. "
                     "Work it on paper first, then find the choice in your book that "
                     "matches all four of your facts."},
        ],
        "answer": "y ≥ -x + 3",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "An equation is a **line**. An inequality is a **region** — a whole side "
            "of the page, with the line as its fence.",
            "Write the **standard form** — **`y ▢ mx + b`** — first, before you look "
            "at anything. Saxon's own word for it, same habit as Lesson 79, one more "
            "blank.",
            "**Dashed line → `<` or `>`** (the line is not included). "
            "**Solid line → `≤` or `≥`** (it is). The bar under the symbol and the "
            "solidness of the line are the same fact.",
            "Memorize one sentence only: **\"greater than means shaded above.\"** Less "
            "than means below comes free.",
            "Finding **b** and **m** has not changed at all since Lesson 79. b is "
            "where it crosses the up-and-down axis; **m = rise / run**, rise first, "
            "and the run always goes right.",
            "If y is **not alone on the left** — `x + y > 2` — rearrange before you "
            "read anything off a picture. Adding to both sides never flips the "
            "symbol; only multiplying or dividing by a negative does.",
            "Check your answer against the picture **twice**: once for the line, once "
            "for the shading. Those are the only two things this lesson adds, so "
            "those are the only two new ways to be wrong.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 83 first. If it didn't quite click, this is here to fix that "
    "— and there are graphs on the page to read, including one you answer with a "
    "button. Good news up front: finding the slope "
    "and the y-intercept is exactly what you did in Lesson 79, and none of it "
    "changes. Everything new is about the picture — whether the line is dashed or "
    "solid, and which side of it is shaded."
)

PARENT_CONTENT = """## The big idea

Lesson 83 adds **two yes/no questions** to a job she already knows how to do. That
is the whole lesson, and saying it that way takes most of the fear out of it.

The job she already knows is Lesson 79: look at a drawn line, read `b` off the
y-axis, walk the staircase for `m`. The book's own solution says it in one line —
*"Solve just like problems from Lesson 79, except here you have an inequality
symbol."* Nothing about finding the two numbers changes.

What is new is that the answer is no longer a line. It is a **region** — a whole
side of the page — and to name it she has to read two more things off the picture:

- **Is the line dashed or solid?** Dashed means the points on the line are *not*
  answers, and that is `<` and `>`. Solid means they *are*, and that is `≤` and
  `≥`. The bar under the symbol and the solidness of the line are the same fact
  written twice.
- **Is the shading above the line or below it?** Saxon gives one sentence to
  memorize — **"greater than means shaded above"** — and then explicitly says the
  other half comes for free: *"by default you'll remember that less than means
  shaded below."* Teach one, not two.

The trap sitting inside this lesson is in the two graphs the book asks her to
*read*: 83.1a (dashed, shaded **below**) and 83.1b (solid, shaded **above**). They
differ in *both* halves, so a child can finish both, get both right, and walk away
believing dashed always goes with below. It does not. The book's third example,
83.2, is dashed and shaded **above** — but she reaches that one by rearranging
`x + y > 2`, not by looking at a picture, so it rarely dislodges the theory. The
combination the book never draws at all is **solid with the shading below**, and
the clickable board on her page is deliberately that one. If you do nothing else
with this page, do that board with her.

**About the figures on her page.** Her DIVE book's pages are not copied here.
Where the book prints a graph, her page **redraws** it from the facts the book's
own solution states about it — 83.1a: dashed, shaded below, crosses at 2, slope 1;
83.1b: solid, shaded above, crosses at 1, slope −2. Those facts fix the picture
completely, so the boards she reads are the same graphs, but they are our drawing
and not the book's: have her book open beside her and let her check that the two
agree. Two coordinates the steps land on, (1, 3) and (1, −1), are *not* stated
anywhere in the book — they follow from the slope and intercept that are, and on
her page she reads them off the redrawn board rather than being handed them.
Example 83.2's four answer choices and practice problem 383's four choices are not
reproduced at all: 83.2 is worked as far as the inequality, which is what decides
the choice, and 383 appears on her page as the same question with a different
number, so the problem in her practice set is still hers to do.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Start with money, not symbols. **"You have twenty dollars. Notebooks are two
   dollars, pens are one dollar. How many can you buy?"** Let her give an answer.
   Then ask: **"Is that the only answer?"** That "no" is the entire lesson — the
   answer is a *collection*, not a point, and a line cannot say it.
2. Draw axes and a line. Say: **"This line is the fence. Everything on this side of
   it works."** Shade one side with the flat of a pencil. Ask: **"How many points
   are shaded?"** You want something like "loads" or "infinite." Good. That is why
   nobody lists them.
3. Now the first new question. Point at the line and ask: **"Is the fence itself
   part of the answer — can you stand on it?"** Then tell her the convention: if
   yes we draw it solid, if no we draw it dashed. Draw both, side by side, so she
   sees the difference before she has to name it.
4. The second new question, and this is the one to make her recite. Say: **"Greater
   than means shaded above."** Have her say it back. Then ask: **"So what does less
   than mean?"** — you want "below," worked out rather than memorized. Do not give
   her both sentences. The second one is the reward for holding the first.
5. Now hand her `y ≥ -2x + 1` and ask her to *draw* it, not read it. Watch which
   part she hesitates on. Then reverse it: cover the equation, point at her own
   drawing, and ask **"what are the two things you'd tell me about this picture
   before any numbers?"** Dashed-or-solid, above-or-below. That is the answer you
   are drilling.

If she is lost, go back to **Lesson 79** and do two of those — pure line-reading,
no shading, no symbols. Nine times out of ten the trouble is not the inequality at
all; it is that reading `m` off a graph was still shaky and the new questions have
tipped it over.

One extra to have ready: `x + y > 2` (Example 83.2). She may not see that it is the
same kind of thing. The move is to add −x to both sides until y is alone. Say it
plainly: **until y is by itself on the left, "greater than means above" is not a
rule she is allowed to use.**

## The classic mix-ups, with the exact wrong answer each one produces

- **Dashed line, but she writes a bar.** On 83.1a she writes **y ≤ x + 2** instead
  of **y < x + 2**. Fix: a bar means "or equal to," which means the points on the
  line; a dashed line is the picture saying they do not count.
- **Solid line, but she writes the strict symbol.** On 83.1b she writes
  **y > -2x + 1** instead of **y ≥ -2x + 1**. Same fact backwards. Have her settle
  this half *before* she looks at the shading at all.
- **Right line, wrong side.** She sees solid and shaded above and writes
  **y ≤ -2x + 1** instead of **y ≥ -2x + 1**. This is what the memorized sentence
  is for. Fast catch: put a finger on a shaded point well above the line and ask
  whether its y is bigger or smaller than the line's.
- **Reading the picture off `x + y > 2` without rearranging.** She takes the 1 and
  the 2 straight out of the sentence and writes **y > x + 2** — slope 1 instead of
  −1, so the line leans the opposite way and the shading is wrong too. Fix: y alone
  on the left first, always.
- **Flipping the symbol while rearranging.** Half-remembered Lesson 82: she writes
  **y < -x + 2** instead of **y > -x + 2**, shading the entire opposite half of the
  page. The flip rule is real but it fires only when you **multiply or divide by a
  negative**. Adding −x to both sides is adding. Nothing flips.

## What to watch her do

Watch her **hands and her eyes**, in this order:

1. Does the pencil write `y ▢ mx + b` — with a gap — *before* she looks at the
   graph? If she starts by staring at the picture, the symbol becomes the last
   thing she thinks about instead of the first, and it is what she will get wrong.
2. **Does she settle the two questions separately — a finger on the line, then a
   finger on the shaded region?** Her page teaches line first, and it is a good
   order to hold; Saxon's own printed solutions happen to read the shading first,
   and either order gives the same answer, so do not correct her for that. What
   you are watching for is a finger that goes straight to the shading and never
   comes back to the line — that is a skipped question, and she will end up
   guessing the line style from the side she is on.
3. When she reads the slope, does her finger actually **travel** — up or down
   first, then right — or does she hover and do it in her head? In-the-head slope
   is where minus signs go to die, and that has not changed since Lesson 79.
4. After she writes the answer, **does she look back up at the picture twice?**
   You want two distinct glances and two small nods: one for the line, one for the
   shading. One glance means she checked one half.
5. On the board on her page, watch what she does *before* pressing a button. If she
   presses a symbol immediately, stop her and make her say the two facts out loud
   first. The buttons are there to confirm a decision, not to make one.

A right answer is not what you are watching for here. With only four symbols she
can be right by luck one time in four, and the two graphs the book asks her to
read differ in both halves, so a wrong theory can survive both of them. The habits
above are what survive contact with the pairings she has not seen drawn.

## Extend it

- Give her a **solid line shaded below** (`y ≤ 0.5x + 1` — the one on her board)
  and then a **dashed line shaded above** (`y > 2x - 3`). Solid-and-below is the
  pairing the book never draws at all; dashed-and-above she has met only as
  algebra, in 83.2, and never as a picture to read. Doing both out loud is what
  kills the "dashed goes with below" theory for good.
- Hand her a point and an inequality — say (4, 0) and `y ≤ 0.5x + 1` — and ask
  whether the point is an answer. She can settle it two ways: put x = 4 in and
  compare, or find (4, 0) on the board with her eye and see whether it lands
  inside the shading. (The board is a picture, not a sketchpad — there is nothing
  to click on it, so this one is done by looking.) Getting
  the same verdict twice is the moment the picture and the algebra become one
  thing for her.
- Ask what `y ≥ 2` looks like with no x in it at all. That is **Lesson 80's
  horizontal line** as a fence, with everything above it shaded. She has every
  piece she needs and will probably still be surprised it works.
- Go back to the twenty dollars. Two-dollar notebooks and one-dollar pens gives
  `2x + y ≤ 20`, and it is worth pointing out that this one is not even in the
  shape yet. It is also the moment to ask why the region stops at the axes: you
  cannot buy a negative number of pens. Real problems come with extra fences.

## Where this sits

DIVE Lesson 83. Reviews Lessons 26, 79, 80 and 82. **Lesson 79 is the one to
revisit if she is lost** — reading `m` and `b` off a graph is most of the work
here and none of it changed. **Lesson 82** (two-step equations and inequalities)
is where the "flip the sign when you multiply or divide by a negative" rule came
from, and it is the rule she is most likely to misfire in this lesson. **Lesson
80** (horizontal and vertical lines) is worth a mention because a horizontal fence
is the easiest inequality there is. Lesson 26 is the far-back reference the book
points to for the inequality symbols themselves.

**Proficient** looks like: given a graph, gets the symbol and both numbers right
for the two combinations the book demonstrates.
**Mastered** looks like: gets solid-shaded-below and dashed-shaded-above right
too, rearranges `x + y > 2` without being prompted, and checks the line and the
shading as two separate checks *without being asked*.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 83 (linear inequalities) — idempotent."

    LESSON_NUMBER = 83
    TITLE = "When the Answer Is a Whole Region — Linear Inequalities"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
