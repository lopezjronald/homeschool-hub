"""Saxon Pre-Algebra Lesson 97 — Linear Regression and Best Fit.

Reviews Lessons 51, 65, 68, 73, 74, 77 and 92. Lesson 77 is the hook the source
names itself: the spring-and-mass equation `y = 0.1065x - 21.122` came out of a
spreadsheet doing linear regression on scattered data, and 97 finally says what
that machine was. Lesson 74 is the second hook — she already met a *trend* there
and estimated its slope from the two dots farthest apart, and 74's own warning
("a short run exaggerates it") is 97's "make a large triangle" said a different
way. Lesson 92 supplies the last step, point-slope: slope plus one point gives b.
The book's first page says **No New Rules** and prints exactly one definition.

Five judgement calls, all visible on her page:

* THE FIGURE. Example 97.1's scatter plot is an image this file cannot see. Only
  three things about it are stated in words — the line passes through **(1, 2)**
  and **(6, 12)**, the slope triangle is labelled **10** and **5**, and the true
  regression line is **y = 2.17x - 0.6**. Nothing else is reproduced or guessed.
  The page says so plainly and hands her the book's own instruction: lay paper on
  the graph and trace it. The tool shows the two named points and nothing more.
* "Ex. 74.4". Page 1 credits the linear trend to Lesson 74, Ex. 74.4. In the
  seeded Lesson 74, Ex. 74.4 is the *pie graph* and Ex. 74.5 is the scatterplot
  with the trend and its slope. Her page therefore says "Lesson 74" without
  pinning an example number; the parent guide notes the mismatch so nobody
  hunts for it.
* "POINT-SLOPE". Page 2 credits the method to Lesson 92 and prints the name in
  quotation marks — the "point-slope" method. The seeded Lesson 92 teaches
  exactly that move and never once uses the phrase. Her page therefore
  introduces the term in the book's own quotation marks and says plainly that
  Lesson 92 called it something else; the parent guide spells the mismatch out,
  the same way it does for 74.4.
* THE SMALL-TRIANGLE ARITHMETIC in the reveal (one square of misreading costs
  50% on a run of 1 and 10% on a run of 5) is NOT printed in the book. It is
  built here to make the book's own "a large triangle helps reduce the error of
  estimating" concrete, and the reveal says out loud that it is an add-on.
* THE 8%. Comparing the estimate m = 2 against the true m = 2.17 gives 7.8% or
  8.5% depending which you divide by — "about 8%" either way. That arithmetic is
  ours, on the book's two numbers, and exists only to cash the book's own promise
  that being 25% out is fine. No percentage is quoted for the y-intercept: 0
  against -0.6 makes a percentage meaningless, and saying "100% wrong" would
  contradict the reassurance the book is trying to give.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_97 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 97 · Pre-Algebra",
        "title": "Draw the line first. Then read the equation off it.",
        "thesis": "Real measurements never land exactly on a line. So you draw the "
                  "line that comes **closest to all of them at once**, and then you "
                  "do the two jobs you already know: slope from a triangle, then b "
                  "from one point.",
        "formula": "Δy / Δx = 10 / 5 = 2   →   2 = 2(1) + b   →   y = 2x",
        "roles": [
            {"tone": "start", "name": "the line — your eye puts it there",
             "text": "Nobody computes it this year. You look at the cloud of dots and "
                     "draw the straight line that fits them best. The book asks for "
                     "**intuition**, in that word, and it means it."},
            {"tone": "move", "name": "the equation — you read it off the line",
             "text": "Once the line exists it is an ordinary line. Big triangle for "
                     "the slope, one point on the line for b, and you are done. Both "
                     "halves are old work."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why the dots never sit on the line",
        "paragraphs": [
            "Hang a weight on a spring and measure how far it stretches. Hang a "
            "heavier one and measure again. Do it eight or ten times and plot the "
            "results. You will get a run of dots climbing steadily up the page — and "
            "not one of them will sit exactly on a straight line.",
            "That is not because the spring is badly behaved. Springs are one of the "
            "most obedient things in physics. It is because your ruler has a "
            "thickness, your eye reads it from a slight angle, the weights are not "
            "quite what the label says, and the table you are working on is not "
            "perfectly level. Every real measurement carries a little error, and "
            "**there is no way to measure it away**.",
            "Here is the good news, and it is the reason this lesson exists: the "
            "errors are usually small enough that the pattern is still obvious. You "
            "can look at the dots and see, with no arithmetic at all, that they are "
            "heading up in a straight line. The pattern survives the mess.",
            "You have met this before. In **Lesson 74** you saw dots that nearly "
            "followed a line and learned to call that a **trend**. In **Lesson 77** "
            "you worked with data from a science experiment on springs, and used its "
            "equation to predict values nobody had measured.",
            "What was never explained is where that equation came from. It was not "
            "somebody's eye. A spreadsheet ran a pile of statistical formulas over "
            "the scattered data and produced **one** line — not a good line, *the* "
            "line. Lesson 97 gives that machine its name, and then asks you to do the "
            "job by hand.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "y  =  0.1065x  -  21.122",
        "note": "Lesson 77's spring equation, and the reason for today. Look at those "
                "decimals: **nobody's eye produces 0.1065**. That equation came out "
                "of a spreadsheet running linear regression over data that was "
                "scattered, exactly like the data in this lesson. You are not "
                "expected to understand the statistical formulas this year — the book "
                "says so — only to know that they exist and what they do.",
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Linear regression: there is exactly one best line, and it can be found",
        "paragraphs": [
            "The book gives one definition today and it is worth reading slowly. "
            "**Linear regression** is *the method of finding a straight line that "
            "best approximates a set of points on a graph.*",
            "The word doing the work in that sentence is **best**. Not *a* line that "
            "goes near the dots — there are thousands of those. Linear regression "
            "finds the **one, and only one** line that fits a set of data better than "
            "every other line in existence. That is a strong claim and it is true.",
            "You are not going to do it that way this year. In Algebra 1 you will "
            "type the data into a spreadsheet and let it compute the real regression "
            "line. Today you use your **intuition** — the book's own word — and get a "
            "feel for where the line belongs.",
            "So the honest name for what you produce today is an **estimate of the "
            "line of best fit**. It is a real answer, not a placeholder, and at the "
            "end of this lesson you will get to see how close a careful eye actually "
            "gets.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Look at the dots and don't touch the pencil yet. Are they heading "
                "somewhere in a straight line? Good — now where would you *put* that "
                "line? Not through your two favourite dots. Through the middle of the "
                "whole crowd, so it's close to as many of them as you can get. Draw "
                "it edge to edge, right across the graph. Now we can start doing "
                "maths to it.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "Best fit means best for all of them — not best for the first two",
        "paragraphs": [
            "The book names the trap directly, so learn it before you make it. If you "
            "draw your line through the **first two points only**, the line will fit "
            "the rest of the data poorly.",
            "It is an easy mistake to make because two points feel like enough. Two "
            "points always determine exactly one line, so drawing that line feels "
            "like an answer rather than a guess. But a best-fit line is not answering "
            "*which line goes through these two dots*. It is answering **which line "
            "is closest to all of them at once**, and the first two dots get no vote "
            "beyond the one everybody else gets.",
            "A useful feel — this is not a rule the book prints, it is just what a "
            "good line tends to look like: the dots end up split roughly evenly, some "
            "a little above your line and some a little below, and none of them "
            "miles away. If every dot on the right-hand end is sitting above your "
            "line, your line is too flat. Tilt it and look again.",
            "The book's own test is simpler and better: **draw the big triangle**. "
            "If your line really does fit the data, a triangle stretching most of the "
            "way across the graph will sit sensibly among the dots. If you have drawn "
            "a line through two friends and abandoned everyone else, the big triangle "
            "makes that obvious at a glance.",
            "One more thing about that triangle, and you already know it. In Lesson "
            "74 you were told to take the two points **farthest apart** when you "
            "estimated a trend's slope, because a short run exaggerates any error. "
            "Same idea, same reason. A large triangle reduces the error of "
            "estimating.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Draw, then slope, then b — in that order",
        "steps": [
            {"label": "Draw the line before you calculate anything.",
             "detail": "Pencil and a straight edge, right across the graph. If you "
                       "are reading the graph on a screen, do what the book says: "
                       "**lay a piece of paper over it and trace the dots**, then "
                       "draw on your tracing. You cannot estimate a slope off a line "
                       "that does not exist yet."},
            {"label": "Make a large triangle on YOUR line.",
             "detail": "Pick two spots on the line you drew, as far apart as the "
                       "graph allows. Drop straight down from the higher one and go "
                       "straight across from the lower one — that is the triangle. "
                       "Big on purpose: it is what keeps a slightly misread square "
                       "from wrecking the slope."},
            {"label": "Slope = Δy over Δx.",
             "detail": "The upright side of the triangle is the **rise**, the flat "
                       "side is the **run**, and the slope is rise divided by run. "
                       "Same subtraction you have done since Lesson 74. Rise on top.",
             "math": "Δy / Δx = (12 - 2) / (6 - 1) = 10 / 5 = 2"},
            {"label": "Write y = mx + b with the slope filled in and b still blank.",
             "detail": "You now have half an equation. `y = 2x + b`. This is the "
                       "moment people stop and think they are finished — they are "
                       "not, and b is not automatically zero."},
            {"label": "Find b the way you did in Lesson 92.",
             "detail": "Your book calls this the \"point-slope\" method, quotation "
                       "marks and all. Do not go looking for that name in Lesson 92 — "
                       "it is not there. What is there is this exact move: *write "
                       "y = mx + b, drop the slope in, substitute a point, solve for "
                       "b.* Same method, new label. So: pick a point that lies **on, "
                       "or very close to, your line** — which point is up to you, and "
                       "the book says so. Put its x and y into the half-equation and "
                       "solve the one-step equation that falls out.",
             "math": "2 = 2(1) + b   →   b = 0"},
        ],
        "after": "Then expect to disagree with the answer key, and do not panic about "
                 "it. The book puts this in writing: you are **estimating** a line "
                 "you think fits best, so expect some error — *don't be surprised if "
                 "your answer is as much as 25% different than the value given. It's "
                 "okay if it is.* A different pair of eyes draws a slightly different "
                 "line. That is not a mistake, it is what an estimate means.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 97.1, part one — draw the line and read its slope",
        "equation": "the graph is in your book   ·   your line passes through (1, 2) and (6, 12)",
        "steps": [
            {"label": "Look first",
             "text": "The question says: draw a line through the data that you think "
                     "best fits it, then write the equation of that line. Notice the "
                     "order — the drawing comes first and the algebra second. The "
                     "scatter of dots itself is printed in your book and is not "
                     "reproduced on this page, so have the book open. If you are "
                     "reading it on a screen, the book's own suggestion is to lay "
                     "paper on the screen and trace the graph before you draw."},
            {"label": "Step 1 · draw your version of the best-fitting line",
             "text": "By eye, through the middle of the data, edge to edge. Yours "
                     "will not be identical to anyone else's and it is not supposed "
                     "to be. What matters is that it is close to **all** the dots — "
                     "not threaded neatly through the two on the left."},
            {"label": "Step 2 · build a large triangle on the line",
             "text": "The book's triangle runs from (1, 2) up to (6, 12), which is "
                     "most of the width of the graph. Its two sides are labelled "
                     "**10** going up and **5** going across — those two numbers are "
                     "printed on the figure in your book, and they are the rise and "
                     "the run.",
             "math": "from (1, 2)   to   (6, 12)      rise 10      run 5"},
            {"label": "Step 3 · why the triangle is drawn that big",
             "text": "A large triangle helps reduce the error of estimating, and it "
                     "does something else as well: it shows you whether you really "
                     "drew a best-fit line or not. A line pushed through the first "
                     "two points only fits the rest of the data badly, and stretching "
                     "a triangle right across the graph is what makes that visible."},
            {"label": "Step 4 · divide rise by run",
             "text": "Straight subtraction, then one division. This is the same rise "
                     "over run you used on the fish trend in Lesson 74 — nothing has "
                     "changed except that you drew the line yourself this time.",
             "math": "Δy / Δx = (12 - 2) / (6 - 1) = 10 / 5 = 2"},
            {"label": "Step 5 · write down what you have so far",
             "text": "Half an equation, and it is worth physically writing the `+ b` "
                     "so the missing piece is staring at you. Part two finds it.",
             "math": "y = 2x + b"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "97.1 (continued)",
        "question": "You have y = 2x + b. Now find the y-intercept and write the "
                    "equation of the line.",
        "steps": [
            {"label": "Pick a point on or near the line",
             "text": "The book is relaxed about which one: *what you choose for a "
                     "point is arbitrary — just try to pick a point that lies on, or "
                     "close to, the line.* That last part is the whole condition. The "
                     "point has to belong to **your line**, because your line is what "
                     "you are writing the equation of. In this example the line "
                     "passes through (1, 2), so use it.",
             "math": "use (1, 2):    x = 1   and   y = 2"},
            {"label": "Substitute both numbers into the half-equation",
             "text": "This is the point-slope method from Lesson 92 and Ex. 92.2. "
                     "There is one difference from how you did it there, and it is "
                     "worth naming: in Lesson 92 the line was handed to you. Here you "
                     "had to **create** the line, find its slope, and only then hunt "
                     "for a point to use.",
             "math": "2 = 2(1) + b"},
            {"label": "Do the multiplying on the right",
             "text": "2 times 1. Nothing subtle. The equation is now a one-step "
                     "equation of the kind you have been solving since long before "
                     "this chapter.",
             "math": "2 = 2 + b"},
            {"label": "Solve for b",
             "text": "Subtract 2 from both sides and b is on its own. It comes out "
                     "**zero** — which means this particular line goes straight "
                     "through the origin. That is a fact about this line, not a rule "
                     "about best-fit lines, and the very next one you draw will "
                     "almost certainly have a b that is not zero.",
             "math": "b = 0"},
            {"label": "Write the equation",
             "text": "Put m and b back into `y = mx + b`. Then tidy it: `+ 0` on the "
                     "end is true but nobody writes it, so the answer is just y = 2x.",
             "math": "y = 2x + 0    →    y = 2x"},
        ],
        "answer": "y = 2x",
    }),

    (B.KIND_MATH, {
        "display": "2 = 2(1) + b     →     2 = 2 + b     →     b = 0",
        "note": "Three short lines, and they are the step almost everybody skips. "
                "Here the answer is **zero**, which makes skipping it feel free — you "
                "would have written `y = 2x` either way. It is not free. The book's "
                "own regression line on this very data has **b = -0.6**, and the next "
                "graph you meet will have a line that crosses the y-axis somewhere "
                "awkward. Write `+ b` down before you know what it is, put a point "
                "from your line in, and solve. Every time, including the times you "
                "can already see the answer.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "How close did your eye get?",
        "paragraphs": [
            "This is the part of the lesson that pays you back. The book takes the "
            "same data and runs the **actual** linear regression method on it — the "
            "statistical formulas, the spreadsheet, the one and only line that best "
            "fits those points. Its equation is `y = 2.17x - 0.6`.",
            "Now compare. Your estimate was `y = 2x`. The true slope is **slightly "
            "larger** than your 2. The true y-intercept is **slightly below** your 0. "
            "The book's own summary of that comparison is the sentence to take away: "
            "*if we make a good estimate, we can get pretty close to finding the line "
            "of best fit.*",
            "It is worth being precise about how close. On the slope, 2 against 2.17 "
            "is about **8 percent** out. The book's rule is that up to **25 percent** "
            "different is fine — so a careful eye landed comfortably inside the "
            "allowance, with room to spare.",
            "Which means your answer disagreeing with the answer key is **not** "
            "evidence that you did it wrong. On every other lesson this year a "
            "different answer meant a mistake. Not here. Estimating is the "
            "instruction, and two people estimating honestly will get two slightly "
            "different lines.",
            "What would be evidence of a mistake is a slope that is wildly out — "
            "5 instead of 2, or a negative number when the dots climb. That is not a "
            "different estimate, that is a different picture, and it usually means "
            "the rise and run got swapped or the line went through two dots and "
            "ignored the rest.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Your line against the real one — the book prints both",
        "headers": ["", "the line you drew by eye", "the true regression line"],
        "rows": [
            {"cells": ["how it was found", "your intuition and a large triangle",
                       "statistical formulas in a spreadsheet"]},
            {"cells": ["slope, m", "2", "2.17"], "emphasis": True},
            {"cells": ["y-intercept, b", "0", "-0.6"], "emphasis": True},
            {"cells": ["the equation", "y = 2x", "y = 2.17x - 0.6"]},
            {"cells": ["how many lines like it exist", "as many as there are people "
                       "with pencils", "exactly one"]},
        ],
        "note": "Read the two middle rows the way the book does: the true slope is "
                "**slightly larger** than the estimate, and the true y-intercept sits "
                "**slightly below** it. The y-intercept is not worth "
                "turning into a percentage — 0 and -0.6 are both small numbers near "
                "the axis, and percentages of nearly-nothing are noise. Look at the "
                "last row instead, because it is the point of the whole lesson: your "
                "line is one of many reasonable answers, and the regression line is "
                "**the** answer. Being close to it with a pencil is a genuinely good "
                "result.",
    }),

    (B.KIND_TOOL, {
        "title": "Draw the line yourself",
        "intro": "Graph paper with the two points the book names already on it, drawn "
                 "**hollow** so you can tell them from anything you add — those are "
                 "given, and they cannot be moved or deleted. The rest of the scatter "
                 "is in your book and not on this page. Read the other dots off your "
                 "book and click them in here (they land filled and solid), or skip "
                 "that and work with the two you have.",
        "widget": "grid",
        # A SQUARE window on purpose. If x spanned 8 units and y spanned 15, the
        # widget would stretch them to the same 440px board and a slope of 2 would
        # LOOK like a slope of 1 — which is fatal in the one lesson whose entire
        # method is judging a line by eye. -1..13 on both axes keeps the cells
        # square, holds both named points, and still shows the strip below zero
        # where the true regression line's -0.6 intercept lives.
        "config": {
            "view": {"xmin": -1, "xmax": 13, "ymin": -1, "ymax": 13},
            "points": [[1, 2], [6, 12]],
            "locked": True,
        },
        "after": "Press **Pen** and do three things in order. **One:** draw your "
                 "best-fit line straight through both hollow dots, edge to edge — "
                 "that is the line from Example 97.1. **Two:** draw the large "
                 "triangle under it, across from (1, 2) to (6, 2) and then up to "
                 "(6, 12), and count the squares: 5 across, 10 up. **Three:** draw a "
                 "*tiny* triangle on the same line — across 1 and up 2 — and look at "
                 "how few squares you have to count. Keep that picture in your head "
                 "for the question below, and answer it out loud before you open it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Both triangles sit on the same line, so both give a slope of 2. So "
                  "why does the book insist on the large one?",
        "answer": "**Because the run divides your mistake.** Suppose your eye is off "
                  "by a single square when you read the rise — which is an ordinary "
                  "amount to be off by on a hand-drawn line.   →   On the large "
                  "triangle: 11 / 5 = 2.2 instead of 2. You are 0.2 out, about 10%.   "
                  "→   On the tiny triangle: 3 / 1 = 3 instead of 2. You are 1 out, "
                  "**50%**.   →   Same eye, same mistake, five times the damage — and "
                  "5 is exactly the run. The error in your slope is the error in your "
                  "rise divided by the run, so a long run shrinks it and a short run "
                  "magnifies it. That is why Lesson 74 told you to take the two "
                  "points farthest apart, and it is why the book's triangle here "
                  "stretches most of the way across the graph. (This arithmetic is "
                  "not printed in your book — the book just says a large triangle "
                  "reduces the error. It is here so you can see the reason rather "
                  "than take it on trust.)",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Drawing the line through the first two points.",
             "wrong": "line through dot 1 and dot 2, then the slope off that",
             "right": "line through the middle of all the dots, then the slope off that",
             "note": "The book calls this one out by name: a line drawn through the "
                     "first two points only *would fit poorly to the rest of the "
                     "data*. Two points do determine a line, which is exactly why "
                     "this feels like an answer instead of a guess. Test yourself "
                     "with the big triangle — if it lands nowhere near the dots on "
                     "the right, you drew a two-dot line."},
            {"name": "Reading the slope off a tiny triangle.",
             "wrong": "run 1, rise misread by one square   →   3 / 1 = 3",
             "right": "run 5, the book's own triangle   →   10 / 5 = 2",
             "note": "**3 instead of 2** — a 50% error out of one misread square. Make "
                     "the very same slip on a run of 5 and you get 11 / 5 = 2.2, which "
                     "is 10% out instead of 50%. Your reading error is divided by the "
                     "run, so a short run exaggerates it. Lesson 74 gave you this "
                     "warning already, in the form *take the two points farthest "
                     "apart*."},
            {"name": "Run over rise.",
             "wrong": "Δx / Δy = 5 / 10 = 0.5",
             "right": "Δy / Δx = 10 / 5 = 2",
             "note": "**0.5 instead of 2** — and notice that they are reciprocals, "
                     "which is the signature of this mistake. Rise goes on top, "
                     "always. Say it out loud as a sentence before you write the "
                     "fraction: *how far up, divided by how far across.* Then check "
                     "it against the picture — a line climbing that steeply cannot "
                     "have a slope of a half."},
            {"name": "Assuming b is zero.",
             "wrong": "y = 2x, because it came out that way last time",
             "right": "2 = 2(1) + b   →   2 = 2 + b   →   b = 0, this time",
             "note": "Example 97.1 is a trap in this one specific way: its b really "
                     "**is** 0, so a child who skipped the substitution gets the "
                     "right answer and learns the wrong habit. The very next line you "
                     "draw will have a b that is not zero — the book's own regression "
                     "line has b = -0.6 — and then skipping the step costs you the "
                     "whole question. Do the substitution every single time, even "
                     "when you can guess the answer."},
            {"name": "Substituting a point that is not on your line.",
             "wrong": "grab any dot on the graph and plug it in",
             "right": "use a point that lies on, or very close to, the line you drew",
             "note": "You are finding the y-intercept **of your line**, so the point "
                     "has to belong to your line. Grab a stray dot sitting one square "
                     "above it and your b comes out exactly 1 too big — the error "
                     "transfers straight across, because b is just what is left after "
                     "you subtract mx. Which point you choose is genuinely arbitrary, "
                     "as the book says. Whether it sits on the line is not."},
            {"name": "Thinking you are wrong because you do not match the key.",
             "wrong": "\"the key says 2.17 and I got 2, so I've made a mistake\"",
             "right": "2 against 2.17 is about 8% out, and the book allows up to 25%",
             "note": "Everywhere else this year, an answer that did not match the key "
                     "was a wrong answer. Not here — and the reason is sitting in the "
                     "instruction, because you were asked to **estimate** a line. Two "
                     "careful people draw two slightly different ones. That is not a "
                     "licence, though. A slope of 5 when the dots say 2 is still an "
                     "error: the allowance covers the small gap between two honest "
                     "lines, not a line drawn without looking."},
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "The first three are new today. The rest are old friends from "
                 "Lessons 74, 77 and 92, plus some of the book's own shorthand — and "
                 "the lesson leans on all of them without stopping to reintroduce "
                 "them.",
        "rows": [
            {"symbol": "linear regression",
             "plain": "the method of finding the straight line that best approximates "
                      "a set of points on a graph — there is exactly ONE such line",
             "example": "y = 2.17x - 0.6"},
            {"symbol": "line of best fit",
             "plain": "the line linear regression finds. This year you ESTIMATE it "
                      "by eye instead of computing it",
             "example": "y = 2x is her estimate of it"},
            {"symbol": "trendline",
             "plain": "what a spreadsheet calls the regression line once it has drawn "
                      "it onto the graph for you",
             "example": "the line on page 3 of the lesson"},
            {"symbol": "Δy", "plain": "the change in y — the RISE, the upright side of "
                                      "your triangle (Δ is the Greek letter delta, "
                                      "and it means 'the change in')",
             "example": "12 - 2 = 10"},
            {"symbol": "Δx", "plain": "the change in x — the RUN, the flat side of "
                                      "your triangle",
             "example": "6 - 1 = 5"},
            {"symbol": "m", "plain": "the slope — Δy over Δx, how steeply the line "
                                     "climbs",
             "example": "m = 2"},
            {"symbol": "b", "plain": "the y-intercept — the height of the line where "
                                     "it crosses the y-axis, which is where x = 0",
             "example": "b = 0"},
            {"symbol": "(1, 2)", "plain": "an ordered pair: x first, then y. Across 1, "
                                          "then up 2",
             "example": "x = 1, y = 2"},
            {"symbol": "1 d.p.", "plain": "round the final answer to one decimal place "
                                          "(d.p. = decimal places)",
             "example": "2.17 → 2.2"},
            {"symbol": "(C)", "plain": "calculator allowed on this problem — a "
                                       "permission, not an instruction",
             "example": "593. (C) ..."},
        ],
        "after": "The one that changes meaning today is **estimate**. Everywhere else "
                 "in this book an estimate is a rough guess you make on the way to an "
                 "exact answer. Here the estimate **is** the answer — the exact one "
                 "needs statistics you have not been taught yet — so an estimate is "
                 "something to do carefully, with a straight edge and a large "
                 "triangle, not quickly.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Linear regression** finds the one straight line that best fits a set "
            "of points. Exactly one line, and a spreadsheet can compute it.",
            "Real data never sits exactly on a line, because every measurement "
            "carries error. The errors are usually small enough that the pattern is "
            "still obvious — that is the whole reason this works.",
            "This year you **estimate** the line by eye. In Algebra 1 you will "
            "compute it properly with a spreadsheet.",
            "**Draw the line first.** Then the slope, then b. In that order, every "
            "time.",
            "Best fit means best for **all** the dots. A line through the first two "
            "points fits the rest badly — the book says so itself.",
            "**Make the triangle large.** Your reading error gets divided by the run, "
            "so a long run shrinks it. Same warning as Lesson 74's *take the two "
            "points farthest apart*.",
            "Slope is **Δy over Δx** — rise on top. 10 / 5 = 2, not 5 / 10.",
            "Find b by putting a point that lies **on your line** into y = mx + b and "
            "solving. That is the Lesson 92 move — the one this book calls "
            "\"point-slope\" — and b is not automatically zero just because it was in "
            "Example 97.1.",
            "Your answer is allowed to be **up to 25% different** from the key. That "
            "is the book's own rule, and it applies here because you were asked to "
            "estimate — not everywhere else.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 97 first. If it didn't quite land, this is here to fix that "
    "— and there is graph paper near the bottom to draw on. Have the book open, "
    "because Example 97.1's scatter of dots lives there and not on this page. One "
    "thing to hold on to: today the drawing comes first and the algebra second, and "
    "your answer is allowed to differ from the key."
)

PARENT_CONTENT = """## The big idea

Two sentences carry the lesson. **Real data never lands exactly on a line, and
there is nevertheless exactly one line that fits it best.** Finding that line is
called **linear regression** — the book's single definition today, and its page one
says **No New Rules**.

She is not going to compute it. The book is explicit and unusually relaxed about
this: *"In Lesson 97, you will simply use your intuition and get a feel for where to
draw a best-fitting line through a set of data."* The spreadsheet version arrives in
Algebra 1. So today's method is: **draw the line by eye, then read the equation off
it** — and both halves of that reading are old work. Slope is rise over run from
Lesson 74; finding `b` from the slope plus one point is the Lesson 92 move, the one
this lesson calls the "point-slope" method.

**Example 97.1** is the whole lesson. She draws her line, builds a large triangle on
it, and gets `Δy/Δx = (12-2)/(6-1) = 10/5 = 2`. Then `y = 2x + b`, substitute the
point `(1, 2)`, and `2 = 2(1) + b` gives `b = 0`, so the answer is **y = 2x**.

Then the payoff, and it is the part worth making sure she reads. The book runs the
real regression on the same data and prints **y = 2.17x - 0.6**. Her `y = 2x` is
about **8%** off on the slope, against a stated allowance of **25%**. The book's own
line: *"don't be surprised if your answer is as much as 25% different than the value
given. It's okay if it is!"*

That allowance is the thing most likely to confuse her, because it contradicts every
other lesson this year. Say it out loud in your own voice: **this is the one kind of
problem where a different answer is not a wrong answer.** But it is an allowance, not
a licence — a slope of 5 where the dots say 2 is still an error, and worth naming as
such.

**About the figure.** Example 97.1's scatter plot is an image, and her page does not
reproduce it. Only three things about that graph are stated in the lesson's own
words, and those three are all her page uses: the line passes through `(1, 2)` and
`(6, 12)`, the triangle's sides are labelled `10` and `5`, and the true regression
line is `y = 2.17x - 0.6`. Nothing else has been guessed at. **She needs the book
open beside her** — and note that the book itself suggests laying paper over a screen
and tracing the graph, which is a good habit and worth doing together once.

**A small bookkeeping note.** Page one credits the linear trend to *"Lesson 74 and
Ex. 74.4."* In her seeded Lesson 74, Example 74.4 is the pie graph and Example
**74.5** is the scatterplot with the trend and its slope. Her page therefore says
"Lesson 74" without pinning a number. If she goes hunting for 74.4 expecting dots,
send her to 74.5.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Before opening anything: **"If you measured the same spring ten times, would you
   get the same number every time?"** You want *no.* Then: **"Is the spring broken?"**
   You want *no* again. That is idea one — the wobble is in the measuring, not in the
   world — and she can get there without you.
2. Open her book to the Example 97.1 graph and cover it with your hand except for the
   dots. Ask: **"Where would you put a line?"** Let her point with a finger before any
   pencil comes out. Then the question that matters: **"Why not through those first
   two dots?"** You want something like *because then it misses the rest.* That is the
   book's own objection, in her words.
3. Have her draw it, then say: **"Now make me a triangle under your line — as big as
   the paper allows."** Do not explain why yet. Ask instead: **"What would happen if
   you'd made a little one?"** The reveal on her page has the arithmetic if she wants
   it: one misread square costs 10% on a run of 5 and 50% on a run of 1.
4. **"Slope?"** You want `10/5 = 2`, and you want her saying *rise over run* out loud
   while she writes it. Then: **"So the equation is...?"** If she says `y = 2x`, stop
   her — that is guessing, and it happens to be right, which is worse. Make her write
   `y = 2x + b` with the `+ b` visible on the page.
5. **"Give me a point on your line."** She should offer `(1, 2)`. Then `2 = 2(1) + b`,
   `b = 0`, `y = 2x`. Finish with the comparison: show her the book's `y = 2.17x -
   0.6` and ask **"how did you do?"** — and then answer it for her, because it is the
   sentence she should leave with: *pretty close, and pretty close is what was asked
   for.*

If she is lost, it is almost never the algebra. Go back to step 2 and make her point
at where the line goes with her finger, three times, on three different scatters.

## The classic mix-ups, with the exact wrong answer each one produces

- **The two-dot line.** She threads the line through the first two dots and the slope
  comes off that. The book flags this itself: the line then *"would fit poorly to the
  rest of the data."* Fix: build the big triangle and look at where it lands relative
  to the dots on the right.
- **A tiny slope triangle.** One misread square on a run of 1 gives `3/1` = **3**
  instead of 2 — a **50%** error. The same slip on the book's run of 5 gives `11/5` =
  **2.2**, about **10%**. Her reading error is divided by the run. This is Lesson 74's
  *take the two points farthest apart* wearing a different hat.
- **Run over rise.** `5/10` = **0.5** instead of **2**. The two are reciprocals, which
  is the tell. Fix: make her look at the line and ask whether something that steep
  could possibly climb half a square per step.
- **Skipping the substitution because b "looks like" zero.** Example 97.1's `b` really
  is 0, so a child who never substitutes gets full marks and learns nothing. Watch for
  it here specifically, because the habit fails on the very next problem — the book's
  own regression line has `b = -0.6`.
- **Substituting a point that is not on her line.** A stray dot one square above the
  line makes `b` exactly 1 too big, because `b` is just what is left after subtracting
  `mx`. The book says the choice of point is *arbitrary*; it also says *"pick a point
  that lies on, or close to, the line."* Both halves matter.
- **Believing she is wrong because she does not match 2.17.** She got `y = 2x`, the
  key says `y = 2.17x - 0.6`, and she rubs it out. This is the mix-up most likely to
  actually happen and the easiest to prevent — tell her about the 25% before she
  starts, not after.

## What to watch her do

Watch her **hands**, in this order:

1. **Does a straight edge come out before the pencil starts calculating?** A best-fit
   line drawn freehand wobbles, and a wobbling line has no single slope. Ruler, or the
   edge of the book.
2. **Does the line run the full width of the graph, or does it stop at the last dot?**
   A short line invites a short triangle, and a short triangle is where the error
   comes from. This is visible from across the room.
3. **How big is the triangle?** This is the single most diagnostic thing on the page.
   If she is counting three squares across, the slope she reports is close to
   meaningless even when it happens to be right.
4. **Does she write `+ b` down?** Watch for the pencil going straight from `m = 2` to
   `y = 2x`. Even when the answer is right, that is a guess, and Example 97.1 rewards
   it. Stop her and make the `b` appear on the paper before it is found.
5. **When her answer differs from the key, what does her face do?** If she reaches for
   the eraser, the 25% rule has not landed and no amount of correct arithmetic will
   fix that. Say it again.

Getting `y = 2x` is not what to watch for. She can get `y = 2x` by using the two
points the book hands her and never drawing a line at all. The drawing, the size of
the triangle, and the visible `+ b` are the three habits that survive a graph where
nothing is given.

## Extend it

- **Do practice problem 197 with her out loud.** It is Example 97.1 with real meaning
  attached: the graph estimates light as a percentage of surface sunlight at
  increasing depths in a lake, and the problem's own hint offers the two points
  `(0, 100)` and `(5, 15)`. Slope is `(15-100)/(5-0)` = `-85/5` = **-17**. The
  y-intercept is free this time — `(0, 100)` already sits on the y-axis, so `b = 100`
  with no substitution needed — giving **y = -17x + 100**. Two things worth saying:
  the slope is *negative* because light dies with depth, and it means **17% of the
  surface light is lost per metre**. Slopes have units, and that sentence is what the
  graph was for.
- **Practice problem 692 is this lesson in a calculus costume.** *Find the equation of
  the tangent line at x = 8 on f(x) = x². The line would have a slope of 16 and pass
  through the point (8, 64).* That is slope-plus-one-point, exactly part two of
  Example 97.1: `64 = 16(8) + b`, `64 = 128 + b`, `b = -64`, so **y = 16x - 64**. If
  she can see that 692 and 97.1 are the same problem, she has got the transferable
  thing out of this lesson.
- **Two different eyes, one graph.** Draw your own best-fit line on a copy of the same
  scatter and work out your equation independently, then compare. The point is not who
  is closer. It is that two careful people got two different answers and *both were
  doing it right* — which is the fact this lesson most needs to be felt rather than
  read.
- **Where does the 25% come from?** Worth leaving open rather than answering. Ask her
  what she would do if her line and yours disagreed by a lot — is there a way to
  decide which is better without being told the answer? That question is precisely
  what linear regression was invented to settle, and meeting it as a puzzle is worth
  more than the formula.

## Where this sits

DIVE Lesson 97, *Linear Regression and Best Fit*. Reviews **Lessons 51, 65, 68, 73,
74, 77 and 92** — page one lists them.

- **Lesson 74** is the one to revisit if the *idea* of a trend has gone. That is where
  she first met dots that nearly follow a line, and where she was told to estimate a
  slope from the two points farthest apart — which is the same advice as today's
  "make a large triangle."
- **Lesson 77** is the one to revisit if she wants to know what a regression line is
  *for*. Its spring equation `y = 0.1065x - 21.122` is a real regression output, and
  97 is finally naming the process that produced it.
- **Lesson 92** is the one to revisit if part two is what is stopping her rather than
  part one. That is slope-plus-one-point-gives-`b`, and the only new wrinkle here is
  that she has to invent the line first. **A naming snag, the same kind as the 74.4
  one:** page 2 calls this the *"point-slope"* method — in quotation marks, which is
  the book's own hedge — and credits Lesson 92 for it. Her Lesson 92 page never uses
  the phrase; there it is simply *write `y = mx + b`, drop the slope in, substitute
  the point, solve for `b`.* The cross-reference itself is exactly right: Ex. 92.2 is
  the tangent at `x = 1`, slope 2 through `(1, 1)`, giving `1 = 2(1) + b` and
  `b = -1` — the identical move on different numbers. Only the label is new, and her
  page says so. Worth separating out loud: *"is it deciding where the line goes that
  you don't like, or the algebra afterwards?"* Those need different help.
- **Lesson 73** is seeded too, and it is the other page worth having open. That is
  where she learned to plot a handful of points and let her eye name the shape,
  rather than joining the dots with a ruler and announcing the answer. Today's lesson
  runs on the same *look before you calculate* habit, pointed at the opposite case:
  here the dots really are heading in a straight line, so the ruler is the right
  instrument this time — 73 is where she learned not to assume that. If `y = mx + b`
  itself is what has gone soft rather than the drawing, 73's own guide sends you
  further back again, to Lessons 68 and 70.
- **Lessons 51, 65 and 68** are listed on the book's own first page but sit outside
  this course's seeded lessons, and this guide has not read them — so nothing here
  describes what is in them. Lesson 97's pages do not lean on them; if the review list
  matters to you, her book is the place to look.

One thing to be ready for that is not in the lesson text at all: **the practice set
has started previewing calculus.** Problem 494 asks her to estimate the area under a
line by counting squares, 692 is a tangent line, and 989 is a limit at a
discontinuity. Lesson 97 teaches none of those and does not need to — they are
deliberately intuitive at this stage. If she asks, the honest answer is that these are
first looks at ideas she will meet properly in a later course.

**Proficient** looks like: draws a sensible best-fit line, gets a slope from a
reasonable triangle, and finds `b` by substitution when reminded that `b` exists.
**Mastered** looks like: makes the triangle large without being told, writes `+ b`
before she knows what it is, and does not flinch when her answer differs from the
key — because she can say why estimating means it should.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 97 (linear regression and best fit) "
            "— idempotent.")

    LESSON_NUMBER = 97
    TITLE = "Draw the Line First — Linear Regression and Best Fit"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
