"""Saxon Pre-Algebra Lesson 92 — More on Derivatives and Tangent Lines;
Calculus and the Study of Speed.

Reviews Lessons 5, 35, 81, 89 and 90. The book's own page one says **No New
Rules or Definitions** — the entire lesson is one formula, `f'(x) = 2x`, and the
three things it lets you do.

Lesson 81 is the main hook and it is a seeded lesson in this course, so the page
leans on it by name: 81 is where Δy/Δx became "the rate of change", where the
x² curve was drawn, and where she saw the left branch coming back down (which is
what Ex. 92.1b's negative answer is). Lesson 90 is the hook for the 0.01 — the
small step and the `f'(x)` notation came from there, and L92's own text points at
90 for its "approaches a limit" sentence too. Lesson 5 is the sequence skill the
page-one chart runs on: read four, predict the fifth. Lesson 35 is what 92B
measures itself against — average speed over a long interval, versus speed at an
instant.

Lessons 88–91 are all seeded in this course, so the page hooks onto them by name.
Lesson 89 — titled "Infinitesimals and the Limit" — is where *infinitesimal* and
*limit* were taught in the first place (`dx`, the symbol for what Δx shrinks to,
is Lesson 90's), and those are the two hardest words on
this page, so the limit box names 89 as their home while keeping the source's own
attribution of the sentence to Lesson 90. Lesson 91 is where P.S. 91.4 was worked,
which is the chart's fourth row, so the recap credits Lessons 90 **and** 91 rather
than handing all four rows to 90 — the source's own reference column does not.

Two judgement calls:

* The brief for this lesson named it "Calculus and the Study of Motion". The DIVE
  guide's own page-one heading and its 92B section heading both read "Calculus
  and the Study of **Speed**", so the page and the Material title use Speed.
* The source says only that the chart's slopes are "about double the input
  values". This page adds one observation on top of that, in Idea 1 and in the
  limit box: the leftover 0.01 is the same size as the Δx that was used. That is
  arithmetic on the book's own four numbers (2.01 − 2 = 0.01), not new theory,
  and it is what makes "shrink the step and the leftover goes with it" land as a
  reason rather than an assertion. No algebra is derived from it — the limit stays
  at the book's own intuitive level of "what the answers head towards".

The source has one figure: the page-2 graph of f(x)=x² with y=2x−1 tangent at
(1,1). Its contents are fully stated in the surrounding text, so it is DRAWN here
rather than described — a KIND_TOOL grid with `curve: "x^2"` and three `locked`
points that all sit on y = 2x − 1 ((0,−1), (1,1), (2,3)), `readonly` so the Undo
and Clear buttons — which wipe the curve layer — are never rendered. Practice
problems 7, 8, 14 and 16 carry figures too; those are not reproduced and she
works them from her book.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_92 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 92 · Pre-Algebra",
        "title": "Stop estimating. There is a formula.",
        "thesis": "Every slope you estimated in Lessons 81 and 90 was heading "
                  "somewhere. Today it arrives. For f(x) = x², the rate of change "
                  "at **any** point is **2x** — exact, not close — and that number "
                  "is the slope of the line that just touches the curve there.",
        "formula": "if f(x) = x², then f'(x) = 2x",
        "roles": [
            {"tone": "start", "name": "f(x) — where the curve is",
             "text": "Put a number in, get the height out. f(5) = 25 says the curve "
                     "sits 25 above x = 5. This is the function you have had all "
                     "along."},
            {"tone": "move", "name": "f'(x) — how fast it is changing there",
             "text": "A second function, built out of the first. Put a number in and "
                     "get a **slope** out. f'(5) = 10 says that at x = 5 the curve is "
                     "climbing ten times faster than x is."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody needed this: the needle on the dashboard",
        "paragraphs": [
            "A car covers 120 miles and it takes two hours. Divide, and the trip ran "
            "at 60 miles per hour. That is a true answer, and it is also a poor "
            "description of almost every minute of the drive — there was a stop for "
            "fuel, a crawl through a town, a long stretch at seventy.",
            "Now look at the dashboard. The needle is answering a different question "
            "entirely. Not *how fast on average*, but **how fast right now**. In "
            "Lesson 35 you worked out the first kind. This lesson is the second kind.",
            "And there is something genuinely awkward about the second question. To "
            "get a speed you divide a distance by a time — you need two moments. But "
            "*right now* is one moment. There is no gap to divide by, and you cannot "
            "divide by nothing.",
            "The way round it is what you have been doing since Lesson 81, and it is "
            "worth seeing laid out plainly: stand at one point, measure across a gap, "
            "then make the gap smaller, then smaller again, and watch where the "
            "answers are heading. Stay at x = 1. In Lesson 81 the gap was 1 and the "
            "answer came out 3. In Lesson 90 you shrank the gap to 0.01 and got 2.01. "
            "Shrink it again, to 0.001, and you get 2.001. Those are creeping up on "
            "**2** and getting closer every time.",
            "Today you stop creeping and write the thing down. For f(x) = x², the rate "
            "of change at any point at all is **2x**. No gap, no estimate, no whole "
            "calculation to redo every time the x changes. One formula.",
            "That formula has a name — the **derivative** — and it has a picture: it "
            "is the slope of the line that just touches the curve at that one point. "
            "And it answers the dashboard question, which is the last thing this "
            "lesson does.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "Line up four answers you already have, and read the pattern",
        "paragraphs": [
            "Your book does something unusual on page 1. It does not teach you "
            "anything. It **collects** work you have already done.",
            "In Lessons 81 and 90 you found Δy/Δx for f(x) = x² over and over. In "
            "Lesson 90 you shrank the step right down to Δx = 0.01, and the slope you "
            "got was following a line that is *almost* a tangent line. Your book is "
            "careful with that word and you should be too: **almost**. Not quite a "
            "tangent line. Very close to one.",
            "Four of those answers are scattered across four different places — Ex. "
            "90.1, Lesson 90 itself, Practice Set 90.1, Practice Set 91.4. Put them "
            "in one column and something jumps out.",
            "The book tells you where it got this move from: **Lesson 5**, and "
            "sequence problems like Ex. 5.9 and 5.10. You were handed four numbers and "
            "asked for the fifth. This is exactly that, except the numbers happen to "
            "be slopes.",
            "Read down them: 2.01, 4.01, 6.01, 8.01. Up by 2 every time, so the next "
            "one is **10.01** — and your book asks you straight out whether you can "
            "see that.",
            "Now read each one against its own x instead. 2.01 sits beside 1. 4.01 "
            "sits beside 2. Every answer is **double its input**, with a hundredth "
            "left over on the end.",
            "That leftover hundredth is worth staring at for a second. It is 0.01 — "
            "the same size as the step you took. Each of these estimates overshoots "
            "by exactly the width of the gap you measured across, which is going to "
            "matter in about thirty seconds.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "The lesson's own chart — every Δx = 0.01 slope you have already "
                   "found, in one place",
        "headers": ["x-value input to f(x) = x²", "Δy/Δx at x, for Δx = 0.01",
                    "where you did it"],
        "rows": [
            {"cells": ["1", "2.01", "Ex. 90.1"]},
            {"cells": ["2", "4.01", "Lesson 90"]},
            {"cells": ["3", "6.01", "P.S. 90.1"]},
            {"cells": ["4", "8.01", "P.S. 91.4"]},
            {"cells": ["5", "?", "— this row is yours"], "emphasis": True},
        ],
        "note": "The last row is a question mark in your book too, and the whole page "
                "turns on it. Cover the **x** column with your hand and read what you "
                "can see: 2.01, 4.01, 6.01, 8.01, going up by 2, so the missing one is "
                "**10.01**.\n\n"
                "The right-hand column is not decoration. Every answer in the middle "
                "column is a problem you have already worked, on a page you still "
                "have. Nothing in this chart is being asserted at you — it is your own "
                "arithmetic, gathered up.",
    }),

    (B.KIND_SAY, {
        "text": "\"Read me the middle column. Just the four numbers. ... Good. What's "
                "it going up by each time? ... So what's the fifth one? ... Now read "
                "them in pairs, the x and the answer together — one, two-point-oh-one. "
                "Two, four-point-oh-one. What happens to the left-hand number on its "
                "way across? ... Right, it doubles. And it picks up a hundredth. So "
                "where do you suppose that hundredth came from?\"",
    }),

    (B.KIND_MATH, {
        "display": "2.01 → 2      4.01 → 4      6.01 → 6      8.01 → 8",
        "note": "That line is your book's own, and it is what the word **limit** "
                "means here. Ask what happens when Δx stops being 0.01 and shrinks "
                "towards an **infinitesimal** — a step too small to write down, "
                "called **dx**. *Infinitesimal* and *limit* are Lesson 89's words; "
                "**dx** is the symbol Lesson 90 gave you for what Δx is heading "
                "towards — and this is all three doing a job. Your book's answer, and it points back at Lesson 90 for "
                "it: the slope approaches a **limit**.\n\n"
                "You can see why in the numbers. The hundredth on the end is the last "
                "trace of the gap you were measuring across. Shrink the gap and the "
                "hundredth goes with it. What is left is double the input, exactly — "
                "**2, 4, 6, 8** out of **1, 2, 3, 4**.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "if f(x) = x², then f'(x) = 2x",
        "paragraphs": [
            "Double the input. At every point, every time. Written in the notation you "
            "met in Lesson 90: **if f(x) = x², then f'(x) = 2x**.",
            "Now say what your book says next, because it is what makes the page worth "
            "reading. You have just built a **single formula** for the derivative — "
            "the true rate of change, **not an estimate** — at ANY point on "
            "f(x) = x².",
            "Look at what that replaces. To find the rate at x = 7 the old way you "
            "would choose a small Δx, work out f(7) and f(7.01), subtract twice, "
            "divide, and land on 14.01 — which is close and is not the answer. The new "
            "way is `2 × 7`.",
            "**f'(x) is a function.** That is your book's own instruction: *treat "
            "f'(x) like a function and evaluate it.* It has an input and an output "
            "like every other function you have met. Put a number in the slot, get a "
            "number out. The only unusual thing is what comes out — not a height, a "
            "**slope**.",
            "And notice which way round this went. Normally the more accurate answer "
            "is the one that costs more work. Here the exact answer is **easier** than "
            "the estimate ever was, and your book points that out. That is what a "
            "formula buys you.",
            "One sentence to hold onto, because the whole rest of the lesson hangs off "
            "it: **the derivative is the slope of a tangent line at a particular "
            "instant. It describes how the function is changing at that instant.**",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "92.1",
        "question": "Find f'(x) for the following locations on f(x) = x²:   "
                    "a) x = 5    b) x = -1",
        "steps": [
            {"label": "Write the formula down before you do anything else",
             "text": "Both parts run on the same one line, so put it at the top of "
                     "your work: **if f(x) = x², then f'(x) = 2x**. Your book opens "
                     "both a) and b) that way, and so do the two lines below. Copying "
                     "it out is what stops your hand reaching for x² out of habit."},
            {"label": "a) put 5 in the slot",
             "text": "Treat f' exactly the way you treat f. Wherever the x is, the 5 "
                     "goes. Two times five.",
             "math": "f'(x) = 2x   →   f'(5) = 2(5) = 10"},
            {"label": "a) say what the 10 actually is",
             "text": "At the single point x = 5, the curve is climbing **ten times "
                     "faster than x is**, and 10 is the slope of the line that just "
                     "touches the curve there. It is not a height. The height at "
                     "x = 5 is 25, and that is a different question with a different "
                     "answer."},
            {"label": "b) put -1 in the slot, minus sign and all",
             "text": "Same formula, negative input. Keep the brackets — they are what "
                     "carry the sign through.",
             "math": "f'(x) = 2x   →   f'(-1) = 2(-1) = -2"},
            {"label": "b) a negative answer here is not a mistake",
             "text": "It says the curve is heading **down** at x = -1. You have "
                     "already seen this: on the graph of x² in Lesson 81, everything "
                     "to the left of zero comes back down. f'(-1) = -2 is that picture "
                     "written as a number."},
        ],
        "answer": "f'(5) = 2(5) = 10   ·   f'(-1) = 2(-1) = -2",
    }),

    (B.KIND_TABLE, {
        "caption": "Two functions, one curve — where it is, and how fast it is "
                   "changing there",
        "headers": ["x", "f(x) = x²   (the height)", "f'(x) = 2x   (the slope there)"],
        "rows": [
            {"cells": ["-1", "1", "-2"], "emphasis": True},
            {"cells": ["1", "1", "2"], "emphasis": True},
            {"cells": ["2", "4", "4"], "emphasis": True},
            {"cells": ["3", "9", "6"]},
            {"cells": ["5", "25", "10"], "emphasis": True},
        ],
        "note": "Read across any row and you get two completely different facts about "
                "the same point: how high the curve is, and how steeply it is "
                "climbing. **The tick mark is the entire difference on the page**, and "
                "it changes the question.\n\n"
                "The **x = 2** row is the one to be careful with. The height and the "
                "slope both come out 4, and that is a coincidence, not a rule — it is "
                "the only row here where the two columns agree, and it comes back in "
                "Example 92.3 with units attached to it. The four shaded rows are the "
                "ones the worked examples use — x = 5 and x = -1 in Ex. 92.1, x = 1 in "
                "Ex. 92.2, x = 2 in Ex. 92.3.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "start",
        "title": "If it really is the slope of a line, that line has an equation",
        "paragraphs": [
            "Your book asks the obvious question out loud, which is a good habit to "
            "steal. *We keep saying the derivative is the slope of a tangent line. If "
            "that is true, then the line must have an equation, right?* Well — yes. It "
            "does.",
            "A **tangent line** is a line that touches the curve at one point and runs "
            "in the same direction the curve is running right there. Touching, and "
            "matching direction.",
            "And you already know how to build a line. A line needs exactly two "
            "things: a **slope**, and one **point** it goes through. You have both "
            "sitting in front of you. The derivative hands you the slope. The function "
            "hands you the point.",
            "The form is the one you have been using since Lesson 70 — problem 14 on "
            "today's practice set is a Lesson 70 problem asking which graph is "
            "`y = 3x - 2`, so it is in front of you today anyway. **y = mx + b**: m is "
            "the slope, b is where the line crosses the y-axis.",
            "Put the slope in and only **b** is left unknown, and one substitution "
            "finds it. That is the whole of Example 92.2.",
            "One warning about b, because it catches nearly everybody. b is **not** "
            "the y of your point. b is the height of the line at x = 0, and your point "
            "is almost never sitting at x = 0. You have to substitute and solve for "
            "it.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe",
        "title": "Four moves to a tangent line, and only one of them is new",
        "steps": [
            {"label": "Get the slope from the derivative.",
             "detail": "The question says *tangent at x = 1*, so the slope is f'(1). "
                       "For f(x) = x² that is 2x with a 1 in the slot. **This is the "
                       "only step that needs today's lesson.** Everything after it you "
                       "could already do.",
             "math": "f'(x) = 2x   →   f'(1) = 2(1) = 2"},
            {"label": "Get the point from the function.",
             "detail": "Same x, but through f this time: f(1) = 1² = 1, so the line "
                       "passes through **(1, 1)**. Example 92.2 hands you both the "
                       "slope and the point in the question — but they came from "
                       "somewhere, and it is worth knowing where."},
            {"label": "Write y = mx + b and drop the slope in.",
             "detail": "Before any other arithmetic. Nothing is solved yet; you are "
                       "setting out the shape of the answer so there is somewhere for "
                       "the b to land.",
             "math": "y = 2x + b"},
            {"label": "Substitute the point, solve for b, then write the line out.",
             "detail": "The point's x goes in the x slot and the point's y goes in the "
                       "y slot — **both of them**. Then it is one subtraction. Put the "
                       "b you found back into the line you set up in step 3.",
             "math": "1 = 2(1) + b   →   b = -1   →   y = 2x - 1"},
        ],
        "after": "Then do the check your book asks for, because it is a real one and "
                 "it takes a minute: **graph f(x) = x² and y = 2x - 1 on the same "
                 "axes.** The line should touch the curve at (1, 1) and nowhere else. "
                 "That picture is drawn for you further down this page.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 92.2 — the equation of the tangent line at x = 1",
        "equation": "f(x) = x²   ·   tangent at x = 1   ·   slope 2, through (1, 1)",
        "steps": [
            {"label": "Look first",
             "text": "This question is generous — it tells you the slope is 2 and the "
                     "point is (1, 1) before you start. Do not let that hide where "
                     "they came from. Your book's own sentence: **the slope = 2 "
                     "because f'(x) = 2x, and f'(1) = 2(1) = 2.** And the point is "
                     "(1, 1) because f(1) = 1² = 1. Everything after this line is "
                     "Lesson 70 algebra."},
            {"label": "Step 1 · write the standard form for the equation of a line",
             "text": "Before any numbers go anywhere. This is your book's first move "
                     "and it is a good one: set out the shape of the answer, then fill "
                     "it in.",
             "math": "y = mx + b"},
            {"label": "Step 2 · ask what you know",
             "text": "Your book's own words here are *think \"what do I know?\"* You "
                     "know the slope is 2, and m is the slope. So the m gets replaced "
                     "and nothing else does — the b stays a letter because you do not "
                     "know it yet.",
             "math": "y = 2x + b"},
            {"label": "Step 3 · use the point to find b",
             "text": "The line passes through (1, 1). That sentence means: when x is "
                     "1, y is 1. So substitute **1 for x and 1 for y**, and the only "
                     "letter still standing is b.",
             "math": "1 = 2(1) + b"},
            {"label": "Step 4 · solve",
             "text": "Two times one is two. Take 2 off both sides. Your book lines "
                     "the -2 up underneath the 2 on the page, which is worth copying "
                     "— it is how you see that the same thing happened to both sides.",
             "math": "1 = 2 + b   →   take 2 off both sides   →   -1 = b"},
            {"label": "Step 5 · put b back and write the line",
             "text": "b is -1, so the `+ b` on the end of `y = 2x + b` becomes -1. "
                     "Watch the sign as it lands: a negative b is written as a minus.",
             "math": "y = 2x - 1"},
            {"label": "Step 6 · check it",
             "text": "Your book says to check by graphing, and that picture is just "
                     "below. There is also a five-second check with no graph at all: "
                     "put x = 1 into your line and see whether y really comes out 1. "
                     "If your line does not pass through the point you were given, "
                     "something went wrong at step 3.",
             "math": "2(1) - 1 = 1   ✓"},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "The check your book asks for",
        "intro": "The green curve is `f(x) = x²`. The three hollow dots are all points "
                 "on the line you just found, `y = 2x - 1`: at x = 0 the line is at "
                 "**-1**, at x = 1 it is at **1**, at x = 2 it is at **3**. They are "
                 "the figure, not your answer, so a stray tap cannot knock one "
                 "off.\n\nLay a ruler — or the straight edge of a pencil — across all "
                 "three dots. That straight edge is the tangent line.",
        "widget": "grid",
        # The page-2 figure, DRAWN rather than described: its contents are stated in
        # full by the surrounding text ("graph f(x)=x² and y=2x-1 ... the line touches
        # f(x)=x² at (1,1)"). `readonly` removes the control bar, which matters here
        # because Undo and Clear both wipe the curve layer and would erase the
        # parabola she was sent here to look at; `locked` keeps the three dots out of
        # everything that edits. The window is 8 wide and 8 tall so the squares stay
        # square — a stretched picture would make the touch at (1,1) look like a
        # crossing — and it is tight enough that one grid square is a real unit she
        # can count with her eye.
        "config": {"view": {"xmin": -3, "xmax": 5, "ymin": -3, "ymax": 5},
                   "points": [[0, -1], [1, 1], [2, 3]],
                   "locked": True,
                   "curve": "x^2",
                   "readonly": True,
                   "label": "f(x) = x² with three points of the tangent line "
                            "y = 2x - 1, which touches at (1, 1)"},
        "after": "Two questions, and answer both out loud before you open the "
                 "drop-down. **One:** at x = 0 and at x = 2, how far below the curve "
                 "does your ruler sit? **Two:** does that straight edge ever cross the "
                 "curve, or does it only touch it?",
    }),

    (B.KIND_REVEAL, {
        "prompt": "With the ruler laid across the three dots — how far below the curve "
                  "is it at x = 0 and at x = 2, and does it ever cross?",
        "answer": "**One square at each, and it never crosses.** At x = 0 the curve is "
                  "at 0 and the line is at -1, so the gap is 1.   →   At x = 2 the "
                  "curve is at 4 and the line is at 3, so the gap is 1 again.   →   At "
                  "x = 1 the gap closes to 0, and that single point is where they "
                  "meet.   →   Step one square either side of the touching point and "
                  "the curve has pulled away by the same amount both ways.\n\n"
                  "Everywhere else on this picture the line stays **below** the curve. "
                  "It touches at (1, 1) and never cuts through — but that is a fact "
                  "about **this** curve, not about the word. What makes the line the "
                  "tangent is that at (1, 1) it is running in exactly the direction "
                  "the curve is running, and that is why its slope is a fair answer to "
                  "the question *how fast is the curve climbing at exactly x = 1*.",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "move",
        "title": "Same mathematics, different letters — and now it is a speed",
        "paragraphs": [
            "Section 92B changes the subject to something you can watch happen. A ball "
            "is moving, and its **position** after t seconds is `x(t) = t²`. At 1 "
            "second it is 1 metre along. At 2 seconds, 4 metres. At 3 seconds, 9.",
            "Read that list again. The ball is not merely moving — it is **speeding "
            "up**. It covered 1 metre during the first second and 5 metres during the "
            "third. So *how fast is the ball going* has no single answer for the whole "
            "trip. It only has an answer at a moment.",
            "In **Lesson 35** you first put speed and rate together, and what you found "
            "there was **average** speed across a long interval — total distance over "
            "total time. That is the honest answer to a question about a whole "
            "journey. It is the wrong tool for *right now*.",
            "Your book's line, and it is the point of the whole section: **the slope "
            "is the rate of change.** Speed is a rate. So a speed is a slope, and a "
            "speed at one instant is a derivative.",
            "Now look at how little actually changes in the mathematics. `x(t) = t²` "
            "is the same shape as `f(x) = x²` — an input, squared. So the derivative "
            "is the same: double the input. Your book writes it out as **if x(t) = t², "
            "then x'(t) = dx/dt = 2t**.",
            "**Watch the letters, because they have swapped jobs.** In the first half "
            "of this lesson x was the *input*. Here x is the **output** — it is the "
            "position, measured in metres — and **t** is the input, the time in "
            "seconds. A letter is a label for what a quantity *is*, not for where it "
            "sits in the sentence.",
            "`dx/dt` is a second way of writing the very same derivative, and it says "
            "out loud what a derivative is: **the change in x per change in t**. "
            "Metres per second. A derivative's unit is always the output's unit over "
            "the input's unit, which is why this example's answer ends in *mps* and "
            "not in metres.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "92.3",
        "question": "The position (x) of a ball with respect to time (t) is given by "
                    "the following equation: x(t) = t². If x is in meters, and t is in "
                    "seconds, find the speed of the ball, in meters per second (mps), "
                    "at t = 2 seconds. In other words, find x'(2).",
        "steps": [
            {"label": "Recognise the shape before you do anything",
             "text": "Your book's solution opens by writing down the thing you already "
                     "have: **if f(x) = x², then f'(x) = 2x**. Then it says "
                     "*likewise*. The ball's equation is that same shape wearing "
                     "different letters, so the same rule covers it.",
             "math": "f(x) = x²   →   f'(x) = 2x"},
            {"label": "Write the derivative in the ball's own letters",
             "text": "Input squared, so the derivative is double the input — and here "
                     "the input is t. Your book writes the result two ways on one "
                     "line, because both notations get used: **x'(t)** and **dx/dt**. "
                     "They are the same thing.",
             "math": "x(t) = t²   →   x'(t) = dx/dt = 2t"},
            {"label": "Put 2 in the slot",
             "text": "The question asks for the speed at t = 2 seconds, then translates "
                     "itself for you — *in other words, find x'(2)*. Two times two.",
             "math": "x'(2) = 2(2) = 4"},
            {"label": "Attach the unit, and say what the number is not",
             "text": "Four **metres per second**. Be careful right here: the ball's "
                     "*position* at t = 2 is also 4, because 2² = 4. Those are two "
                     "different facts — the ball is 4 metres from where it started, "
                     "and at that instant it is travelling at 4 metres per second. The "
                     "numbers matching is bad luck, not meaning. At t = 3 they part "
                     "company: 9 metres, 6 mps.",
             "math": "x(2) = 4 m      ·      x'(2) = 4 mps"},
        ],
        "answer": "x'(2) = 4 mps",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "This lesson is written almost entirely in marks. None of them is "
                 "complicated, and several are things you already own under different "
                 "names. Here is each one said out loud.",
        "rows": [
            {"symbol": "f(x)", "plain": "a function — put an x in, get a height out",
             "example": "f(3) = 9"},
            {"symbol": "f'(x)", "plain": "read \"f prime of x\" — the DERIVATIVE. Put "
                                         "an x in, get the SLOPE at that x out",
             "example": "f'(3) = 6"},
            {"symbol": "'", "plain": "the prime mark. A tick that means \"the "
                                     "derivative of\". Not an apostrophe, not a foot "
                                     "mark",
             "example": "f'  ·  x'"},
            {"symbol": "Δx", "plain": "the change in x — the size of the step you "
                                      "chose to measure across",
             "example": "Δx = 0.01"},
            {"symbol": "Δy / Δx", "plain": "the slope across a whole stretch: rise "
                                           "over run (Lesson 81)",
             "example": "2.01"},
            {"symbol": "dx", "plain": "an infinitesimal — a step too small to write "
                                      "down. What Δx is heading towards",
             "example": "Δx → dx"},
            {"symbol": "dx / dt", "plain": "another way to write the derivative: the "
                                           "change in x per change in t",
             "example": "dx/dt = 2t"},
            {"symbol": "limit", "plain": "the value the answers are heading towards as "
                                         "the step shrinks",
             "example": "2.01 → 2"},
            {"symbol": "tangent line", "plain": "a line that touches the curve at one "
                                                "point and runs the same direction the "
                                                "curve does there",
             "example": "y = 2x - 1"},
            {"symbol": "derivative", "plain": "the slope of that tangent line — the "
                                              "true rate of change at one instant",
             "example": "f'(x) = 2x"},
            {"symbol": "y = mx + b", "plain": "standard form of a line: m is the "
                                              "slope, b is where it crosses the y-axis",
             "example": "y = 2x - 1"},
            {"symbol": "x(t)", "plain": "position at time t. Here x is the OUTPUT "
                                        "(metres) and t is the input (seconds)",
             "example": "x(2) = 4 m"},
            {"symbol": "mps", "plain": "meters per second — the unit a speed comes in",
             "example": "x'(2) = 4 mps"},
        ],
        "after": "The two easiest to mix up are `f(x)` and `f'(x)`. One tick mark is "
                 "the whole visible difference, and it changes the question "
                 "completely: one asks *where is the curve*, the other asks *how fast "
                 "is it changing*. Read the tick out loud every single time — say "
                 "\"f prime of five,\" not \"f of five\" — and you will stop losing it.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Squaring when the derivative says double.",
             "wrong": "f'(5) = 5² = 25",
             "right": "f'(x) = 2x   →   f'(5) = 2(5) = 10",
             "note": "**25 instead of 10.** f and f' are two different functions "
                     "living on the same curve. f(5) = 25 is how *high* the curve is "
                     "above x = 5; f'(5) = 10 is how *steeply* it is climbing there. "
                     "The habit that fixes it: write `f'(x) = 2x` at the top of your "
                     "work before you substitute anything, exactly as your book does "
                     "in both halves of Ex. 92.1."},
            {"name": "Losing the minus sign on a negative input.",
             "wrong": "f'(-1) = 2(1) = 2",
             "right": "f'(-1) = 2(-1) = -2",
             "note": "**2 instead of -2**, and the sign is the entire content of the "
                     "answer. Keep the brackets when you substitute — `2(-1)` carries "
                     "the sign, `2 -1` invites you to read a subtraction. And do not "
                     "distrust a negative derivative: it means the curve is going "
                     "**down** there, which is exactly what x² does left of zero."},
            {"name": "Taking b straight from the point.",
             "wrong": "the line passes through (1, 1), so b = 1   →   y = 2x + 1",
             "right": "1 = 2(1) + b   →   b = -1   →   y = 2x - 1",
             "note": "**y = 2x + 1 instead of y = 2x - 1.** b is the height of the "
                     "line at **x = 0**, and (1, 1) is not on the y-axis. There is a "
                     "free check on this one: put x = 1 into your finished line. "
                     "`2(1) + 1 = 3`, and 3 is not the 1 you were promised, so the "
                     "line misses the point it was supposed to touch."},
            {"name": "Handing in the estimate instead of the derivative.",
             "wrong": "f'(1) = 2.01",
             "right": "f'(1) = 2(1) = 2",
             "note": "**2.01 instead of 2.** 2.01 was Lesson 90's *estimate*, taken "
                     "across a gap of 0.01, and your book calls the line it belongs to "
                     "*almost* a tangent line. Almost. The derivative is the number "
                     "those estimates were heading towards, and it is the only one "
                     "with no leftover on the end."},
            {"name": "Answering \"find the equation\" with the slope.",
             "wrong": "the tangent line at x = 1 is   2",
             "right": "the tangent line at x = 1 is   y = 2x - 1",
             "note": "The derivative gives you **one of the two numbers a line needs**. "
                     "A question that says *find the equation* wants a y = something, "
                     "with an x in it. Read the question again after you have finished "
                     "working — a correct slope handed in for an equation question is "
                     "still a wrong answer, and it is a common one."},
            {"name": "Reading a position as a speed.",
             "wrong": "x(2) = 2² = 4, so the ball is going 4 mps",
             "right": "x'(t) = 2t   →   x'(2) = 2(2) = 4 mps",
             "note": "This one is dangerous because **the number comes out right**. At "
                     "t = 2 the ball is 4 metres along *and* travelling at 4 metres per "
                     "second, and a method that confuses the two scores full marks "
                     "today and fails tomorrow. Test yourself at another moment: at "
                     "t = 3 the position is 9 m and the speed is 6 mps. At t = 3.5 — "
                     "which is practice problem 3 — the position is 12.25 m and the "
                     "speed is 7 mps."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "Your Δx = 0.01 estimates, from Lessons 90 and 91, ran **2.01, 4.01, 6.01, "
            "8.01** for x = 1, 2, 3, 4. Double the input, plus the size of the step "
            "you took.",
            "As Δx shrinks towards an infinitesimal **dx**, those slopes approach a "
            "**limit**: 2, 4, 6, 8. Double the input, exactly, with nothing left over.",
            "**If f(x) = x², then f'(x) = 2x.** One formula for the true rate of "
            "change — not an estimate — at ANY point on the curve.",
            "**f'(x) is a function.** Feed it a number the same way you feed f a "
            "number. What comes out is a slope, not a height.",
            "A **derivative is the slope of a tangent line at a particular instant.** "
            "It says how the function is changing right there.",
            "A negative derivative is not an error. f'(-1) = -2 means the curve is "
            "heading **down** at x = -1.",
            "Tangent line, in four moves: slope from **f'(a)**, point from **f(a)**, "
            "write **y = mx + b**, substitute the point and solve for b. At x = 1 on "
            "x², that is **y = 2x - 1**.",
            "**b is not the y of your point.** b is the height of the line at x = 0, "
            "so you substitute and solve for it every time.",
            "Different letters, identical mathematics: **x(t) = t²  →  x'(t) = "
            "dx/dt = 2t**. In that one, x is the output and t is the input.",
            "Speed is a rate, so a speed is a slope. Lesson 35 gave you **average** "
            "speed across an interval; a derivative gives you the speed at an "
            "**instant** — x'(2) = 4 mps.",
            "A position and a speed are different quantities even when the numbers "
            "match. At t = 2 the ball is at 4 **metres** and moving at 4 **metres per "
            "second**.",
            "The book's own page one: **No New Rules or Definitions.** Everything here "
            "is Lessons 5, 35, 81, 89 and 90, gathered into one formula.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 92 first. If it didn't quite land, this is here to fix that — "
    "and there's a graph near the bottom you can lay a ruler across. Two things to "
    "hold on to. First: all that estimating in Lessons 81 and 90 was heading "
    "somewhere, and today it arrives as one formula — if f(x) = x², then f'(x) = 2x. "
    "Second: that formula is the slope of a line, so the line has an equation, and "
    "when the function is a ball's position the slope is its speed."
)

PARENT_CONTENT = """## The big idea

The book's first page says **No New Rules or Definitions**, and it means it. The
whole lesson is one formula and the three things it lets her do.

**92A gets the formula, and it gets it by pattern rather than by proof.** Saxon
collects the Δx = 0.01 estimates she has already worked — `2.01, 4.01, 6.01, 8.01`
at x = 1, 2, 3, 4 — into one chart and asks her to read it as a **Lesson 5
sequence**: four numbers given, predict the fifth. She should get `10.01`. Then it
asks the real question: what happens as Δx shrinks towards an infinitesimal, `dx`?
The slopes *approach a limit*. `2.01` becomes `2`, `4.01` becomes `4`, and so on.
The leftovers vanish and what is left is **double the input**, which is the
formula: **if f(x) = x², then f'(x) = 2x**.

Keep Saxon's own carefulness about the word *almost*. With Δx = 0.01 the line she
was working with is **almost** a tangent line, not quite one. The derivative is
what the almosts were heading towards. A child who reports `2.01` as the
derivative has missed the one idea on the page.

**Then three uses, one per example.**

- **Ex. 92.1** — the formula is a function, so evaluate it. `f'(5) = 2(5) = 10`,
  and `f'(-1) = 2(-1) = -2`. Saxon's instruction is literally *treat f'(x) like a
  function and evaluate*.
- **Ex. 92.2** — if a derivative is the slope of a tangent line, that line has an
  equation. Slope `2` from `f'(1)`, point `(1, 1)`, then `y = mx + b` →
  `y = 2x + b` → `1 = 2(1) + b` → `b = -1` → **`y = 2x - 1`**.
- **Ex. 92.3** — the same 2x with different letters and a unit on the end. A ball's
  position is `x(t) = t²`, so `x'(t) = dx/dt = 2t`, and at t = 2 seconds the speed
  is **4 mps**.

**92B is the payoff and it is worth naming out loud.** In **Lesson 35** she found
average speed across a long interval. A derivative gives her the speed at an
*instant* — the difference between "we averaged 60 mph" and the needle on the
dashboard. Saxon's sentence for it is *the slope is the rate of change*.

One vocabulary trap in 92B that is entirely the book's doing and worth pre-empting:
**x changes jobs.** In 92A, x is the input. In 92.3, `x` is the *output* — the
position in metres — and `t` is the input. Her page says this plainly; say it once
yourself too.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step. Have her page open at
the chart.

1. Cover the x column with your hand so only the four answers show. **"Read me
   these four numbers."** `2.01, 4.01, 6.01, 8.01`. **"What's it going up by? So
   what's the fifth one?"** She says `10.01` and she has just done the first page of
   the lesson without you. Name it: *that's a Lesson 5 sequence.*
2. Uncover the x column. **"Now read them in pairs — one and two-point-oh-one, two
   and four-point-oh-one. What's happening to the left number on its way across?"**
   You want *doubling*, and *plus a bit*.
3. **"Where did the hundredth come from?"** From `Δx = 0.01` — the size of the step.
   Then the question that is the whole lesson: **"so what if the step were
   smaller?"** Smaller leftover. **"And if it were unimaginably small?"** Gone. Write
   `2.01 → 2` on paper and say Saxon's word for it: the slope approaches a **limit**.
4. Write **`f'(x) = 2x`** and ask for `f'(5)`. Then `f'(-1)` — watch for the minus.
   Then the question that separates the two functions: **"and what's f(5)?"** `25`.
   **"So which one is the slope?"** If she can answer that, Idea 2 has landed.
5. For the tangent line, ask before you teach: **"A line needs two things. What are
   they, and where would you get each one?"** Slope and a point; f' gives the slope,
   f gives the point. Then let her run Ex. 92.2 and finish at the graph on her page —
   make her lay an actual ruler across the three dots.

If she is lost, it is almost always at step 3. Do not re-explain the formula; go
back to the chart and shrink the step with her — 0.1, then 0.01, then 0.001 — and
ask what the leftover is doing each time.

## The classic mix-ups, with the exact wrong answer each one produces

- **Squaring instead of doubling.** `f'(5) = 25` instead of **10**. She has applied
  f where the question asked for f'. Fix: `f'(x) = 2x` written at the top of the
  page before any substituting, which is what Saxon does in both halves of Ex. 92.1.
- **Minus sign dropped.** `f'(-1) = 2` instead of **-2**. Fix: brackets when
  substituting — `2(-1)`, not `2 -1`. And tell her a negative derivative is a real
  answer: the curve is going *down* at x = -1, which is the left branch of x² she
  saw graphed in Lesson 81.
- **b copied from the point.** `y = 2x + 1` instead of **`y = 2x - 1`**. Fix: b is
  the line's height at x = 0. Free check — put x = 1 into her line; if it does not
  give y = 1, the line misses the point it was meant to touch.
- **The estimate reported as the derivative.** `f'(1) = 2.01` instead of **2**. Fix:
  Saxon's own word — with Δx = 0.01 that line is *almost* a tangent line. The
  derivative has no leftover on the end.
- **Slope handed in for "find the equation."** She writes **2** where the question
  wanted **`y = 2x - 1`**. A correct number answering the wrong question. Fix: read
  the question again *after* finishing the work.
- **Position read as speed.** On Ex. 92.3 she computes `x(2) = 4` and calls it the
  speed. **The number is right**, which is why this one survives. Fix: test her at
  another instant — at t = 3 the position is `9 m` and the speed is `6 mps`, and the
  method that "worked" now gives 9.

## What to watch her do

Watch her **paper**, not her answers. Not one of these six scores a right answer
anywhere in this practice set — every wrong method a Lesson 92 problem can reach
lands on a visibly wrong number. The one place a wrong method still scores is
**Ex. 92.3** on her page, where the position and the speed are both 4.

1. **Does `f'(x) = 2x` get written down before she substitutes?** Saxon writes it
   twice in Ex. 92.1 — once for each part — and that is not padding. A child who
   substitutes straight into her head is the child who squares.
2. **Do brackets appear around the negative?** You want to see `2(-1)` on the page.
   `2 -1` is where the minus sign goes to die.
3. **On the tangent line, does `y = mx + b` appear before any number?** That is
   Saxon's first move and it is the diagnostic one. A child who writes `y = 2x - 1`
   straight down has copied the shape of the worked example rather than built it.
4. **Does she substitute BOTH coordinates?** Watch for the line `1 = 2(1) + b`
   appearing. If only the x goes in, there is nothing to solve and she will guess b.
5. **On Ex. 92.3, does a unit reach the answer line?** `4` is not the answer here; `4
   mps` is. The unit is the only thing on her page distinguishing the speed from the
   position, and both are 4.

## Extend it

- **Practice problem 2 is Ex. 92.2 mirrored.** Tangent at `x = -1`, slope `-2`,
  through `(-1, 1)`. It comes out **`y = -2x - 1`** — same b, opposite slope. Have
  her graph it against the picture on her page and notice the two lines are mirror
  images across the y-axis. If she gets that one unaided, the recipe has landed.
- **Practice problem 3 is Ex. 92.3 with a decimal.** `x'(3.5) = 2(3.5)` = **7 mps**.
  Then ask for the *position* at the same instant — `3.5² = 12.25 m` — and make her
  say aloud which is which. That is the position-versus-speed mix-up inoculated.
- **The best question on the whole page is practice problem 12.** It is a Lesson 81
  problem: `f(8) = 64`, `f(10) = 100`, find Δy/Δx. She gets `36 ÷ 2` = **18**. Now
  ask what today's formula says the slope is at x = 8 (**16**) and at x = 10
  (**20**). The 18 sits exactly halfway between them — it is the average across the
  stretch, not the rate at either end. That is the entire difference between Lesson
  81 and Lesson 92 in one line, and it is worth two minutes.
- **A puzzle to leave open.** The ball's speed is `2t`, which is itself a function of
  time. Ask what you would get if you took the derivative *of the speed*. Do not
  answer it. She has everything she needs to be curious and nothing she needs to
  resolve it, and that is the right place to leave a child before calculus.

## The figures

- **The graph on page 2** — `f(x) = x²` with `y = 2x - 1` touching it at `(1, 1)`.
  Her page **draws it**: the parabola, plus three read-only dots at `(0, -1)`,
  `(1, 1)` and `(2, 3)`, all three of which sit on the tangent line. She is asked to
  lay a ruler across them, then to say how far below the curve it runs at x = 0 and
  x = 2 (one square each) and whether it ever crosses (it does not). The drop-down
  under it checks her. Everything drawn there is stated in the book's own text, so
  nothing has been guessed at.
- **Nothing else in the taught pages.** Apart from that graph — which belongs to
  Ex. 92.2's *check your work* — Ex. 92.1 and the ball in 92B are pure text in the
  source, so no number on her page has been read off a picture: everything drawn
  here is worked from the book's own equations.
- **Practice problems 7, 8, 14 and 16 carry figures** (a discontinuous function, a
  sphere, four candidate graphs, a shape to find the perimeter of) and none of them
  are reproduced here. Have her book open beside her for those four.

## Where this sits

DIVE Lesson 92, *More on Derivatives and Tangent Lines; Calculus and the Study of
Speed*. Reviews **Lessons 5, 35, 81, 89 and 90**.

- **Lesson 81** is the one to revisit if the derivative feels like it came from
  nowhere. Δy/Δx, "calculus is the mathematical study of rates of change", and the
  graph of x² all started there, and this lesson's page-one chart is that same
  method run four times over with a smaller step — the fifth row is the one she
  predicts rather than works.
- **Lesson 90** is the one for the `0.01`. The small step and the `f'(x)` notation
  came from there, and Saxon points back at 90 for *approaches a limit* as well —
  every number in the chart is Lesson 90's or Lesson 91's work, and the reference
  column says which.
- **Lesson 5** is the sequence skill the chart runs on: read four, predict the
  fifth. Saxon names Ex. 5.9 and 5.10 specifically.
- **Lesson 35** is what 92B measures itself against — average speed across a long
  interval, which is the thing a derivative is *not*.
- **Lesson 89** is the one for the words. *Infinitesimal* and *limit* were her
  first real calculus there — `dx`, the symbol for what Δx heads towards, is
  Lesson 90's — and they are exactly what the shrinking `0.01` on this
  page is doing. If the limit box reads as hand-waving, that lesson is where it was
  argued properly. Practice problem 7 is a Lesson 89 problem — a discontinuous
  function, with a figure that is not reproduced here — so work that one from her
  book.

**Proficient** looks like: evaluates `f'(x) = 2x` at a given x, including a negative
one, and produces the tangent line's equation when the slope and the point are
handed to her.
**Mastered** looks like: gets the slope and the point herself from `f'` and `f`,
solves for b rather than copying it, and can say what the derivative *means* at that
point — "the curve is climbing ten times faster than x is here" — including on
Ex. 92.3, where she keeps the position and the speed apart even though both are 4.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 92 (derivatives, tangent lines, and "
            "speed) — idempotent.")

    LESSON_NUMBER = 92
    TITLE = ("The Slope Right There — More on Derivatives and Tangent Lines; "
             "Calculus and the Study of Speed")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
