"""Saxon Pre-Algebra Lesson 94 — The Integral and Counting Squares;
Imaginary Numbers.

Reviews Lessons 30, 54, 78, 81, 84, 90 and 92. Two halves that share a page and
nothing else, so this is two short runs of blocks.

**Lesson 81 is the hook for the first half.** That is where calculus was defined
as the study of rates of change and where she first worked at Δx = 1, on the
points (2, 4) and (3, 9) of y = x². Lesson 90 narrowed Δx to 0.01 and Lesson 92
took it to the infinitesimal. The book's own framing of 94A is that the integral
walks the same road — but stops on the first rung, Δx = 1, which is why every
square is one wide and one tall and the whole method is counting them. **Lesson
78** supplies the reason anyone bothers: `d = rt` is two numbers multiplied, and
so is area, so one square of a speed-against-time graph is
`1 mph × 1 hour = 1 mile`. That mile is the book's own payoff and it is the
payoff here.

**Lesson 84 is the hook for the second half.** 84 taught that even roots may not
hold a negative inside — "no real number gives you ⁴√-16". Lesson 94 is the same
sentence from the other end: here is the name for what happens when you write one
down anyway. Lesson 54's product-of-square-roots rule is the mechanism the book
names for factoring the -1 out, and Lesson 30 is the original square-root
definition.

Judgement calls, most of them about what could not be seen:

* **Example 94.1's two graphs are figures and are not reproduced.** They do not
  need to be: the source's text states the equation of each line (`y = 5` and
  `y = x + 3`), the interval (x = 0 to 3), and each answer (15, and 12 whole +
  3 half = 13.5). Both examples are therefore built from the stated numbers, and
  a table rebuilds 94.1b column by column — 3 + 4 + 5 whole squares and one cut
  square per column — which reproduces the book's own 12-and-3 exactly. The
  child's page says in one sentence that the picture is in her book.
* **Example 94.2 a) and b) are printed as images and are NOT reconstructed.**
  Unlike Lesson 86, there is nothing to reconstruct from: the source prints a
  bare "a)" and "b)" and its solution lines for those two are images as well.
  What the source *does* state is the method ("use the product of square roots rule
  (Lesson 54) to first factor out √-1") and one complete worked instance of that
  method a few lines earlier in the body text — `√-36 → √-1 · √36 → 6i`. That one
  is worked here, and part c) (`11i² = 11(-1) = -11`) is worked here because it
  is printed in full. Her page tells her to do a) and b) from her book in the
  worked block's own question line — one sentence, addressed to her. The argument
  for why nothing was invented in their place is a maintainer's argument, so it
  lives in PARENT_CONTENT and not inside a child's solution steps.
* Practice problem 194 is also a figure, and its equation is NOT in the source.
  All the source states is that the function is horizontal and that the interval
  is x = 0 to 5, so no height is asserted anywhere on the page — the parent guide
  says to read the line's height off her own book rather than inventing one.
* The source's page-2 sentence "you know ⬚ = 2" lost its radicand in extraction.
  It is `√4` — the only reading consistent with the next sentence, "2 is a real
  number that we can locate on a number line" — and is written as √4 here.
* **The kayak takes the book's route, not a Riemann one.** The source goes
  straight from `d = rt` to area and never chops the trip into pieces "small
  enough that the rate barely moves". At Δx = 1 the rate moves a full 1 mph
  inside every piece, and a child following that sentence literally assigns one
  rate per hour and lands on 3 + 4 + 5 = 12 — which is mistake 2 in this page's
  own error block. So the purpose block and the reveal say what is true and
  checkable instead: each column is one hour, its area is that hour's miles
  (3.5, 4.5, 5.5), and those sum to the 13.5 the squares already gave.

The source's sentence about Euler being "a Christian man" is carried as the book
has it, in one clause, the same way Lesson 81's worldview passages were.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_94 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 94 · Pre-Algebra",
        "title": "Count the squares. Then meet a number you cannot point at.",
        "thesis": "Two halves, and neither one is hard. An **integral** is the area "
                  "under a graph, and at this stage finding it means counting "
                  "squares. Then **i** — a name somebody gave to √-1 so they could "
                  "stop writing it out.",
        "formula": "12 + 3(0.5) = 13.5        ·        √-36 = √-1 · √36 = 6i",
        "roles": [
            {"tone": "start", "name": "the integral — how much is under it",
             "text": "The derivative asked how *steep* a graph is. The integral asks "
                     "how much **area** sits underneath it. Same graph, opposite "
                     "question."},
            {"tone": "move", "name": "i — the square root of -1",
             "text": "No ordinary number times itself gives a negative. So the "
                     "square root of a negative gets a letter instead of a value, "
                     "and the letter is *i*."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "How far did you paddle, when your speed never sat still",
        "paragraphs": [
            "You are three hours down a river in a kayak. The watch on your wrist "
            "still shows how fast you are going right now, but the part that counts "
            "up the miles stopped working somewhere near the start. Every hour you "
            "glanced at it and said the number out loud: 3 miles an hour, then 4, "
            "then 5, then 6, as the river narrowed and the current picked you up. "
            "Somebody at the landing asks how far you came.",
            "You know a formula for this. **`d = rt`** — distance is rate times "
            "time, from Lesson 78. But `d = rt` wants *one* rate, and you do not "
            "have one. The speed was 3 at the start and 6 at the end and it never "
            "stopped changing in between.",
            "So you take the trip one hour at a time. In the first hour your speed "
            "climbed steadily from 3 to 4, so that hour is worth **3.5 miles** — "
            "halfway between the two. The second hour is worth 4.5 and the third is "
            "5.5. Add the three and you have 13.5 miles. That is it — that is the "
            "whole idea, and it has a name.",
            "Now draw it. Time across the bottom in hours, speed up the side in "
            "miles per hour. Each little square on that graph is 1 hour wide and 1 "
            "mile per hour tall, and multiplying its two sides gives **1 mile**. So "
            "the hours you were adding up are literally the **columns of squares** "
            "underneath the line — that first hour is three whole squares and a "
            "half, which is the 3.5 you just worked out — and the distance you "
            "travelled is the **area** under it.",
            "In Lessons 81, 90 and 92 you spent three whole lessons on the "
            "derivative — how steep a graph is, at one exact spot. The integral is "
            "the other half of calculus and it asks the opposite question. Not *how "
            "steep*. **How much.**",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 5, "tone": "start",
        "title": "Same road as the derivative — but this lesson stays on the first rung",
        "paragraphs": [
            "Your book puts the two halves of calculus side by side in one sentence: "
            "the derivative uses infinitesimals to calculate **rates of change**, and "
            "the integral uses infinitesimals to calculate **areas**. In particular, "
            "areas under the graphs of functions.",
            "You already know how the derivative got there, because you walked it. "
            "**Lesson 81** started simple, with Δx = 1 — two points on `y = x²` one "
            "whole step apart. **Lesson 90** squeezed that down to Δx = 0.01 and the "
            "line got very close to a tangent line. **Lesson 92** went all the way to "
            "the infinitesimal.",
            "Integrals follow the same process. Your book says so. But this lesson "
            "**only considers Δx = 1**, and that single decision is what makes today "
            "easy.",
            "Because if Δx = 1, every square is 1 unit wide. And the squares on graph "
            "paper are 1 unit tall. A square that is 1 by 1 has an area of **1** — so "
            "finding the area is not a calculation at all. It is a **count**.",
            "Your book puts an exclamation mark on it: *we really are just going to "
            "count squares!*",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Look at the shaded part of that graph. Don't calculate anything — "
                "there's nothing to calculate. Just count the squares inside it. If "
                "the line slices one of them in half, count that one as a half. Add "
                "up what you counted, and that number is the area. That is what the "
                "word *integral* means, at least for today.\"",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 94.1a — the area under y = 5, from x = 0 to 3",
        "equation": "y = 5        from x = 0 to x = 3        count squares",
        "steps": [
            {"label": "Look first",
             "text": "Your book prints this one as a graph with the region already "
                     "shaded for you, so have the book open — the picture is not "
                     "reprinted on this page. It does not need to be. The text tells "
                     "you everything: the line is **y = 5**, and the region runs from "
                     "**x = 0 to 3**. Two facts, and they are enough to draw the whole "
                     "thing yourself on any scrap of graph paper."},
            {"label": "Step 1 · read what kind of line it is",
             "text": "`y = 5` has no x in it. That means y is 5 no matter what x does "
                     "— a **flat, horizontal line**, five squares up, running straight "
                     "across. A flat top edge is the friendly case, because it lies "
                     "along the grid lines instead of cutting through them.",
             "math": "y = 5   at every x   →   a horizontal line 5 units up"},
            {"label": "Step 2 · count across",
             "text": "The region starts at x = 0 and stops at x = 3. That is **3 "
                     "columns** of squares. Count the columns, not the tick marks — "
                     "there are 4 tick marks from 0 to 3 and only 3 gaps between them, "
                     "and the squares live in the gaps.",
             "math": "x = 0 to 3   →   3 columns"},
            {"label": "Step 3 · count up",
             "text": "The region is everything **between the line and the x-axis** — "
                     "that is what *under* means here. From 0 up to 5 is 5 squares, "
                     "and because the line is flat, every single column is the same "
                     "5 tall.",
             "math": "y = 0 to 5   →   5 squares in every column"},
            {"label": "Step 4 · count the squares",
             "text": "Three columns, five squares each, and not one of them cut. You "
                     "may count them one at a time with a fingertip — that is exactly "
                     "what the book is asking for — or multiply, since a rectangle "
                     "lets you.",
             "math": "3 × 5 = 15 squares"},
            {"label": "Step 5 · write the answer with no units on it",
             "text": "The question says *units are not required, simply count "
                     "squares*. So the answer is a bare number. Resist the urge to "
                     "write cm² or in² after it — nobody told you what one square is "
                     "worth yet, and inventing a unit here would be making something "
                     "up.",
             "math": "area = 15"},
        ],
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 5, "tone": "move",
        "title": "A sloping top edge cuts squares in half",
        "paragraphs": [
            "Part b) of the same example changes one thing. The line is now "
            "**`y = x + 3`**, which does have an x in it, so it climbs — one square up "
            "for every square across. At x = 0 it is 3 units high; by x = 3 it is 6.",
            "That climb is the whole difference. A flat line runs *along* the grid "
            "lines. A sloping line runs **through** the squares, and a square with a "
            "line through it is not a whole square any more.",
            "Here the arithmetic stays kind, because this line rises exactly one for "
            "every one across. It enters each square it cuts at one corner and leaves "
            "at the opposite corner — so it cuts that square into two identical "
            "pieces. **Half a square is worth 0.5.**",
            "So the count arrives in two piles instead of one. Count the whole squares "
            "and write the number down. Count the cut squares and write *that* number "
            "down separately. Then turn the second pile into a value — three halves is "
            "3(0.5) = 1.5 — and add the piles together.",
            "Do not try to eyeball a square that looks about two-thirds full. At this "
            "stage the book only gives you lines that cut corner to corner, so every "
            "cut square is a clean half. If you ever find yourself squinting at a "
            "sliver, re-read the line's equation — you have probably mis-drawn it.",
            "One word in the question is worth noticing: it says **estimate** the "
            "area. For these two straight lines the count actually lands on the exact "
            "answer. The word is there because counting squares is a rough tool in "
            "general — send it at a curve and it only gets you close. The fix for "
            "that is smaller squares, which is the same shrinking you already watched "
            "the derivative do in Lessons 90 and 92. Integrals travel that road too. "
            "Just not today.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Example 94.1b, column by column — the book's shaded picture "
                   "rebuilt from its own numbers, since the picture itself is in your "
                   "book and not on this page",
        "headers": ["the column", "the line runs from … to …", "whole squares",
                    "cut squares"],
        "rows": [
            {"cells": ["x = 0 to 1", "y = 3  up to  y = 4", "3", "1"]},
            {"cells": ["x = 1 to 2", "y = 4  up to  y = 5", "4", "1"]},
            {"cells": ["x = 2 to 3", "y = 5  up to  y = 6", "5", "1"]},
            {"cells": ["all three", "y = 3  up to  y = 6", "12", "3"],
             "emphasis": True},
        ],
        "note": "Read one row at a time and you can rebuild the picture without it. In "
                "the first column the line sits between 3 and 4, so three whole "
                "squares fit underneath it and the fourth is the one it slices. Every "
                "column works the same way and each one holds exactly **one** cut "
                "square, because the line only ever crosses one square per column. "
                "Add the two right-hand columns down: **3 + 4 + 5 = 12** whole and "
                "**3** cut — which is the book's own count, word for word.",
    }),

    (B.KIND_WORKED, {
        "number": "94.1b",
        "question": "From x = 0 to 3, estimate the area under the linear function "
                    "y = x + 3. The region has been shaded for you. Units are not "
                    "required, simply count squares.",
        "steps": [
            {"label": "Read the line before you count anything",
             "text": "`y = x + 3` starts 3 units up and gains one unit of height for "
                     "every unit across. Check both ends: put x = 0 in and you get 3, "
                     "put x = 3 in and you get 6. That tells you the shaded region is "
                     "3 tall on its left edge and 6 tall on its right.",
             "math": "x = 0  →  y = 3          x = 3  →  y = 6"},
            {"label": "Count the whole squares",
             "text": "Go column by column rather than wandering around the shape — "
                     "wandering is how squares get counted twice. Three in the first "
                     "column, four in the second, five in the third.",
             "math": "3 + 4 + 5 = 12 whole squares"},
            {"label": "Count the cut squares separately",
             "text": "One per column, each one sliced corner to corner by the line. "
                     "Keep this number in its own pile. It is not worth the same as "
                     "the first pile and mixing them is the mistake this example "
                     "exists to teach.",
             "math": "3 half-squares"},
            {"label": "Turn the halves into a value",
             "text": "Three halves. Half of a square is 0.5, so multiply. This is the "
                     "line your book shows.",
             "math": "3(0.5) = 1.5"},
            {"label": "Add the two piles",
             "text": "Twelve whole squares plus one and a half more. Nothing clever "
                     "left to do.",
             "math": "12 + 1.5 = 13.5"},
            {"label": "Does that look like the right size of answer?",
             "text": "The region is 3 tall at one end and 6 tall at the other, so on "
                     "average it is somewhere around 4 and a half tall, over 3 across. "
                     "Four and a half threes is thirteen and a half. It agrees, and "
                     "that check takes five seconds.",
             "math": "4.5 × 3 = 13.5   →   area = 13.5"},
        ],
        "answer": "area = 13.5",
    }),

    (B.KIND_TOOL, {
        "title": "Build the picture your book has and this page does not",
        "intro": "Four hollow dots, at **(0, 3), (1, 4), (2, 5) and (3, 6)**. Those "
                 "are four points that the line `y = x + 3` passes through, worked out "
                 "the ordinary way by putting 0, 1, 2 and 3 in for x. They are the "
                 "given figure, so a stray tap cannot knock one off.\n\nNow do the "
                 "drawing. Switch to the pen and rule a line through all four dots. "
                 "Drop a line straight down from the first dot to the x-axis, and "
                 "another straight down from the last one. Shade what is inside. That "
                 "shape is Example 94.1b, and you built it instead of being handed it.",
        "widget": "grid",
        # Four points on y = x + 3, one per whole value of x across the example's own
        # interval — `locked` so they behave as the given figure and survive Undo and
        # Clear while she draws. NOT readonly: the pen is the entire point here, since
        # the source's shaded graph is a figure this page cannot reprint and drawing
        # it is the closest honest substitute. No `curve` — the widget's families are
        # shapes like x and x², and y = x + 3 is not one of them, so asking for a
        # curve would draw the wrong line. The window is 8 by 8 so the squares stay
        # square and a counted square really is a square.
        "config": {"view": {"xmin": -1, "xmax": 7, "ymin": -1, "ymax": 7},
                   "points": [[0, 3], [1, 4], [2, 5], [3, 6]],
                   "locked": True,
                   "label": "four points on the line y = x + 3: (0, 3), (1, 4), "
                            "(2, 5) and (3, 6)"},
        "after": "Three things to do once it is drawn, in this order. **Count the "
                 "whole squares in the left column** and check you get 3, then do the "
                 "other two columns and check you get 12 altogether. Then **find the "
                 "three squares your line cuts through** — one in each column, and no "
                 "column has two. Last, look hard at one of those cut squares: your "
                 "line went in at a corner and came out at the opposite corner, so the "
                 "piece above it and the piece below it are the **same size**. That is "
                 "why it counts as exactly a half and not roughly a half.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 5, "tone": "start",
        "title": "Why counting squares is worth a name",
        "paragraphs": [
            "Fair question: why would anybody ever want to do this? Your book answers "
            "it, and the answer is a formula you have had since **Lesson 78**.",
            "**`d = rt`.** Distance equals rate times time — two values multiplied "
            "together. Now think about what area is: length times length. Also two "
            "values multiplied together. Those are the same shape of arithmetic, and "
            "that is not a coincidence.",
            "So put real quantities on the two axes. Rate up the side, in miles per "
            "hour. Time across the bottom, in hours. One square on that graph is now "
            "1 mile per hour tall and 1 hour wide — and when you multiply its two "
            "sides, the *per hour* and the *hour* cancel each other out and leave you "
            "holding **1 mile**.",
            "That is the whole trick. **Each square counts as one mile of distance "
            "travelled.** Read the graph in Example 94.1b as speed against time and "
            "you are no longer counting squares at all. You are counting miles.",
            "Counting squares under a graph like this is called **integrating**, and "
            "your book says you will meet integrals properly in Algebra 1 and beyond. "
            "For now it wants exactly one thing from you: connect the word *integral* "
            "with counting squares under a graph.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "1 mile per hour   ×   1 hour   =   1 mile",
        "note": "That is one square, with its own two sides multiplied together. It is "
                "also why the area under a speed graph is a **distance** rather than "
                "just a number: the units on the two axes multiply the same way the "
                "sides do. Change what the axes measure and the squares change with "
                "them — gallons per hour against hours would give you **gallons**, "
                "dollars per day against days would give you **dollars**. The "
                "counting never changes. Only what a square is worth.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Take the graph from Example 94.1b and read it as your book "
                  "suggests: speed in miles per hour going up, time in hours going "
                  "across. So the kayak starts at 3 mph and is carried steadily up to "
                  "6 mph over three hours. How far did it travel — and why can you "
                  "not just use d = rt?",
        "answer": "**13.5 miles.** It is the same 13.5 you already counted, because "
                  "each square is 1 mph × 1 hour = 1 mile, so 13.5 squares is 13.5 "
                  "miles. You did the work in the worked example; all that changed is "
                  "what the squares are called.\n\n"
                  "And `d = rt` is no help on its own because **there is no single "
                  "r**. The speed was 3 at the start and 6 at the end and never held "
                  "still, so there is nothing to put in for the rate.   →   What the "
                  "integral does instead is measure the **area** under the line, one "
                  "column at a time. Each column is one hour of the trip — one unit "
                  "wide, which is the Δx = 1 this lesson stays at — and a column's "
                  "area is the miles you covered in that hour: 3.5, then 4.5, then "
                  "5.5, since the speed climbed steadily across each one.   →   "
                  "3.5 + 4.5 + 5.5 = 13.5   →   The same 13.5, reached from the other "
                  "side. Check it roughly as well: the speeds run from 3 to 6, so the "
                  "average is about 4.5, and 4.5 mph for 3 hours is 13.5 miles. All "
                  "three agree, which is a good sign that you have not misunderstood "
                  "what you counted.",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 5, "tone": "start",
        "title": "There is no real number that multiplies by itself to make -1",
        "paragraphs": [
            "Second half of the lesson, and it is one idea long.",
            "In **Lesson 84** you learned that odd roots will happily hold a negative "
            "inside and even roots will not — there is no real number that gives you "
            "`⁴√-16`. Lesson 94 is that same sentence approached from the other end. "
            "What if you write one down anyway?",
            "Start with a root you trust. `√4 = 2`. Finding a square root means asking "
            "*what times what* — the **same** number twice in a row — and 2 × 2 = 4. "
            "Two is a real number and you can put your finger on it on a number line.",
            "Now try `√-1`. What times what equals -1? If you said \"1 times -1\", "
            "that is not allowed — **both factors have to be the same number**. So try "
            "the two candidates properly: 1 × 1 = +1, and (-1) × (-1) = +1 as well. "
            "Both come out positive — and that is not a fluke about those two. "
            "Multiply **any** real number by itself and the answer is **never "
            "negative**. Start anywhere but zero and you land on a positive; start at "
            "zero and you land on zero. Nothing at all lands below.",
            "There is no real number you can multiply by itself to get -1. Not a hard "
            "one, not a decimal one, not one nobody has found yet. There is not one.",
            "So the book gives it a name instead of a value. An **imaginary number** "
            "is the result of taking the square root of a negative number, and the "
            "particular one √-1 gets the symbol **i**.",
            "\"Not real\" is not an insult here, it is a location. Real numbers live "
            "on the number line. You cannot plot `i` anywhere on that line — not "
            "between 0 and 1, not out past a million, nowhere — because no point on "
            "it squares to a negative. That is the entire reason for the word "
            "*imaginary*.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "i = √-1        i² = (√-1)(√-1) = -1",
        "note": "Two lines, and the first one is only a **swap**. `i` is not a "
                "discovery, it is shorthand: wherever you would have written √-1, "
                "write *i* instead. The second line is where the work is, and it "
                "follows from something you already have — squaring a square root "
                "hands you back whatever was under the radical, so squaring √-1 gives "
                "you -1. Learn the **second** line hardest. It is the one that turns "
                "something imaginary straight back into ordinary arithmetic — the "
                "moment you see `i²` you can write **-1** and get on with it.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe",
        "title": "Three moves for the square root of a negative",
        "steps": [
            {"label": "Split the minus sign off from the number.",
             "detail": "Every negative under a radical is that number multiplied by "
                       "-1, and the **product of square roots rule** from Lesson 54 "
                       "lets you write one root as two roots multiplied. Nothing "
                       "changes value. You have only made the -1 stand on its own "
                       "where you can get at it.",
             "math": "√-36  =  √-1 · √36"},
            {"label": "Replace √-1 with i.",
             "detail": "That is the whole job the letter was invented for. One "
                       "character instead of three, and the awkward part of the "
                       "problem is now a single symbol you can carry around."},
            {"label": "Simplify the ordinary root that is left, and write i after it.",
             "detail": "√36 is an everyday square root and comes out 6. Write the "
                       "number first and the *i* behind it — **6i**, not *i*6. That is "
                       "just how it is written, the same way you write 6x rather than "
                       "x6.",
             "math": "i · √36  =  i · 6  =  6i"},
        ],
        "after": "And if a problem hands you an **i²** instead of a radical, do not go "
                 "hunting for a root at all — there is nothing to factor. `i²` **is** "
                 "-1. Swap it in and finish the arithmetic like any other line. That "
                 "is all of Example 94.2c and it takes one step.",
    }),

    (B.KIND_WORKED, {
        "number": "94.2c, and the book's own √-36",
        "question": "Parts a) and b) of Example 94.2 are pictures in your book, so "
                    "work those two from the book — they want exactly the same moves "
                    "as the first problem here. These are the two the book prints in "
                    "words: simplify √-36, and then simplify 11i².",
        "steps": [
            {"label": "√-36 · split the -1 off",
             "text": "-36 is 36 times -1, and Lesson 54's rule lets you write one "
                     "square root as two multiplied. Take the -1 out on its own.",
             "math": "√-36 = √-1 · √36"},
            {"label": "√-36 · swap √-1 for i",
             "text": "Straight substitution. This is the step the letter exists for.",
             "math": "√-1 · √36 = i · √36"},
            {"label": "√-36 · finish the ordinary root",
             "text": "√36 is 6 — nothing imaginary about it. Number in front, *i* "
                     "behind. Your book's own line lands in the same place: replace "
                     "the √-1 with i and the √36 with 6, to get 6i.",
             "math": "i · √36 = i · 6 = 6i"},
            {"label": "11i² · there is no radical here",
             "text": "Look at what you have actually been given. No radical sign "
                     "anywhere — just an `i²`, and you know what `i²` is. Put -1 in "
                     "its place and the problem turns into arithmetic you could have "
                     "done two years ago.",
             "math": "11i² = 11(-1) = -11"},
            {"label": "Notice where the second answer landed",
             "text": "**-11 is an ordinary real number.** You can point at it on a "
                     "number line. It started with an imaginary piece in it and came "
                     "out real, which is worth noticing rather than shrugging at — the "
                     "*i* did not stay imaginary, because `i²` is by definition a real "
                     "-1. That is the fact doing the work, not a trick. Set the two "
                     "answers side by side and the difference shows: one still carries "
                     "an *i* and one does not.",
             "math": "√-36 = 6i        and        11i² = -11"},
        ],
        "answer": "√-36 = 6i        and        11i² = -11",
    }),

    (B.KIND_IDEA, {
        "n": 5, "of": 5, "tone": "move",
        "title": "Where the letter came from, and where these numbers turn up",
        "paragraphs": [
            "Why a letter, and why *that* letter? The symbol is **Leonhard Euler's**. "
            "He used *i* in place of √-1 because it was easier and faster when you are "
            "working through pages of calculation by hand, which is how all "
            "mathematics was done in the 1700s. Three characters down to one, ten "
            "thousand times over, is a real saving. Euler — a Christian man — is often "
            "considered the greatest mathematician who ever lived, and a great many of "
            "the symbols he settled on three hundred years ago are the ones you write "
            "today.",
            "So where do these numbers actually show up? In science and engineering, "
            "wherever negative values get measured. Your book's example is **AC** "
            "electricity — alternating current, the kind in the wires in your walls, "
            "which swings back and forth between positive and negative many times a "
            "second instead of flowing one way.",
            "Systems like that often need **complex numbers**, which carry a real part "
            "and an imaginary part together in one number. You are not asked to work "
            "with those yet. You are only asked to know the word.",
            "Which leaves the honest summary your book gives, and it is worth taking "
            "at face value. *Imaginary* is **just a word** used to describe these "
            "numbers. They are a little weird, because you cannot plot them on a "
            "number line. And you can always factor the imaginary part out. That is "
            "the whole of what Lesson 94 wants from you.",
            "One practical note for your practice set. The book says that in any "
            "problem referencing Example 94.2, an ***italicised* i** means Euler's "
            "notation — i = √-1 and i² = -1. That warning is there because *i* is also "
            "a perfectly ordinary letter to use as a variable, so the slant of the "
            "type is how the book tells you which one it means.",
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "This page has two vocabularies on it, one per half, and the book "
                 "introduces most of them in a single sentence each. Here is what "
                 "every one of them is short for.",
        "rows": [
            {"symbol": "integral", "plain": "the tool that finds the AREA under a "
                                            "graph. At this stage, doing one means "
                                            "counting squares",
             "example": "area = 13.5"},
            {"symbol": "integrating", "plain": "the act of doing it — your book's own "
                                               "word for counting these squares",
             "example": "counting squares under a graph"},
            {"symbol": "derivative", "plain": "the other half of calculus: the SLOPE "
                                              "of a graph right at a point "
                                              "(Lessons 81, 90, 92)",
             "example": "Δy / Δx"},
            {"symbol": "Δx = 1", "plain": "every square is one unit wide. Every "
                                          "integral in this lesson stays here",
             "example": "one square: 1 wide, 1 tall"},
            {"symbol": "infinitesimal", "plain": "unimaginably small but not zero — "
                                                 "what Δx shrinks to in real calculus "
                                                 "(Lesson 92). Named today, not used",
             "example": "Δx → 0"},
            {"symbol": "area under the graph", "plain": "the region between the line "
                                                        "and the x-axis, across the "
                                                        "stretch of x the question "
                                                        "names",
             "example": "from x = 0 to 3"},
            {"symbol": "half-square", "plain": "a square the line cut corner to "
                                               "corner. Worth 0.5, counted in its own "
                                               "pile",
             "example": "3(0.5) = 1.5"},
            {"symbol": "i", "plain": "Euler's letter for √-1. Printed in ITALICS it "
                                     "means this, not a variable",
             "example": "i = √-1"},
            {"symbol": "i²", "plain": "i times i, which is -1. Swap it for -1 the "
                                      "moment you see it",
             "example": "11i² = -11"},
            {"symbol": "√-36", "plain": "the square root of a negative — so an "
                                        "imaginary number, not a real one",
             "example": "6i"},
            {"symbol": "6i", "plain": "6 multiplied by i. Number in front, i behind, "
                                      "the same way you write 6x",
             "example": "√-36 = 6i"},
            {"symbol": "complex number", "plain": "one number carrying a real part and "
                                                  "an imaginary part at once — named "
                                                  "in this lesson, not worked in it",
             "example": "Algebra 2, not today"},
            {"symbol": "AC", "plain": "alternating current — household electricity, "
                                      "and where engineers actually meet these numbers",
             "example": "the wires in your walls"},
        ],
        "after": "The two easiest to confuse are `i` and `i²`, and they are confusable "
                 "on purpose. `i` is a thing you carry along to the end of the "
                 "answer. `i²` is a thing you **get rid of immediately** by writing "
                 "-1 in its place. If you can only remember one line from the second "
                 "half of this lesson, remember **i² = -1**.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Counting a cut square as a whole one.",
             "wrong": "12 whole + 3 cut   →   12 + 3 = 15",
             "right": "12 whole + 3 cut   →   12 + 3(0.5) = 13.5",
             "note": "**15 instead of 13.5.** The three squares the line runs through "
                     "are worth half each, not one each. The fix is mechanical: keep "
                     "the two piles in two different places on your paper and never "
                     "let a cut square get written down next to a whole one. Write "
                     "*12 whole* and *3 half* as separate lines before you add "
                     "anything."},
            {"name": "Forgetting the halves altogether.",
             "wrong": "3 + 4 + 5 = 12   →   area = 12",
             "right": "12 + 1.5 = 13.5",
             "note": "**12 instead of 13.5.** This one happens when the whole squares "
                     "get counted first and the answer feels finished. It always "
                     "leaves you **short**, because the halves you skipped were real "
                     "area. Before you write *area =*, ask one question: did the line "
                     "cut through any squares? If it slopes at all, the answer is yes."},
            {"name": "Treating a sloping top edge as if it were flat.",
             "wrong": "the line starts at 3, and it is 3 across   →   3 × 3 = 9",
             "right": "the line climbs 3 → 6   →   12 + 1.5 = 13.5",
             # The licence comes from the FLAT EDGE, not from the example
             # number. Tied to 94.1a it was false — practice problem 194, the
             # first in her own set, is a horizontal line where multiplying is
             # exactly right — and it contradicted two other places in this
             # same file that say so.
             "note": "**9 instead of 13.5.** Multiplying works whenever the top edge "
                     "is **flat** — `y = 5` is the same height everywhere, so 3 across "
                     "by 5 up really is the area, and the horizontal line in problem "
                     "194 works the same way. `y = x + 3` is 3 tall at one end and 6 "
                     "tall at the other, so there is no single height to multiply by. "
                     "That is precisely why the book has you count instead."},
            {"name": "Pulling the minus sign out through the radical.",
             "wrong": "√-36  =  -√36  =  -6",
             "right": "√-36  =  √-1 · √36  =  6i",
             "note": "**-6 instead of 6i**, and it is the most tempting mistake in "
                     "94B because -6 looks like a real answer. These are two different "
                     "questions. `-√36` says *take the root of 36, then make it "
                     "negative* — and -6 squared is +36, not -36. `√-36` asks for "
                     "something whose square is **-36**, and no real number does that. "
                     "The minus is trapped inside the radical; the only way it comes "
                     "out is as an *i*."},
            {"name": "Turning i² into +1.",
             "wrong": "11i² = 11(1) = 11",
             "right": "11i² = 11(-1) = -11",
             "note": "**11 instead of -11**, sign flipped, everything else perfect. "
                     "The instinct behind it — that a number times itself never comes "
                     "out negative — is correct for every *real* number: positive from "
                     "anywhere but zero, zero from zero. It is wrong for this one, and "
                     "that is the whole reason *i* had to be invented. **i² = -1**, by "
                     "definition, and there is nothing to work out."},
            {"name": "Answering √-1 = -1.",
             "wrong": "√-1 = -1",
             "right": "√-1 = i,   because (-1)(-1) = +1 and (1)(1) = +1",
             "note": "Test it the way you would test any square root: multiply the "
                     "answer by itself. -1 times -1 is **+1**, so -1 is not it. And 1 "
                     "times -1 does give -1, but those are two *different* numbers and "
                     "a square root needs the same number twice. Both real candidates "
                     "fail, which is exactly the argument your book makes on page 2."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "The **derivative** measures how steep a graph is. The **integral** "
            "measures how much **area** is under it. Same graph, opposite question.",
            "At this stage an integral is one thing: **count the squares**. Each "
            "square is 1 wide and 1 tall, so each one is worth 1.",
            "This lesson stays at **Δx = 1**. The derivative went 1 → 0.01 → "
            "infinitesimal across Lessons 81, 90 and 92; integrals travel the same "
            "road, but not today.",
            "A **flat** top edge gives whole squares. A **sloping** one cuts squares "
            "in half — count the halves in a separate pile and multiply by 0.5.",
            "Example 94.1b, all of it: **12 whole + 3 half → 12 + 1.5 = 13.5.**",
            "Counting squares under a graph is called **integrating**.",
            "Why it is worth doing: `d = rt` (Lesson 78) is two numbers multiplied and "
            "so is area. Speed up the side, time across, and **one square = 1 mph × "
            "1 hour = 1 mile**.",
            "There is **no real number** that multiplies by itself to make -1. Both "
            "factors would have to be the same number, and a **real** number times "
            "itself is **never negative** — positive from anywhere but zero, and "
            "zero from zero.",
            "**i = √-1**, and **i² = -1**. The second one is the one to know cold — "
            "it is a swap, not a calculation.",
            "Square root of a negative: **factor out √-1** using Lesson 54's product "
            "rule, swap it for *i*, simplify what is left. `√-36 = √-1 · √36 = 6i`.",
            "The minus sign cannot walk out through the radical. **`√-36` is 6i; "
            "`-√36` is -6.** Two different questions.",
            "An *italicised* **i** in a problem means Euler's i, not a variable. Your "
            "book says so on purpose.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 94 first. If it didn't quite land, this is here to fix that — "
    "and there's graph paper near the middle you can draw on. Two halves, and neither "
    "is hard. The first is counting squares under a graph, which is all an *integral* "
    "is for now. The second is one letter: *i*, the name for √-1, which exists because "
    "no ordinary number multiplied by itself comes out negative."
)

PARENT_CONTENT = """## The big idea

Two halves, unrelated to each other. Teach them as two short lessons on the same
afternoon, not one long one.

**94A — the integral.** The headline is a genuine piece of calculus and the method
is arithmetic a nine-year-old could do. Saxon says it plainly: the derivative uses
infinitesimals to find *rates of change*, and the integral uses them to find
*areas* — areas under the graphs of functions. Then it makes today easy by fixing
**Δx = 1** and going no further. If Δx is 1 then every square on the graph paper is
1 wide and 1 tall, so every square is worth 1, and finding the area is a **count**.
The book's own line, exclamation mark and all: *we really are just going to count
squares!*

Two examples, one flat line and one sloping one, and the sloping one is the lesson.
`y = 5` from x = 0 to 3 is a rectangle — 3 across, 5 up, **15** squares, none of
them cut. `y = x + 3` over the same interval climbs from 3 up to 6, so its top edge
runs *through* squares instead of along grid lines: **12 whole squares and 3
half-squares**, and `12 + 3(0.5)` = **13.5**. The line rises one for every one
across, so it enters each square it cuts at a corner and leaves at the opposite
corner, which is why every cut square is a clean half rather than a judgement call.

Then the payoff, which is the part worth slowing down for. Why bother counting? Her
page follows the book: `d = rt` from **Lesson 78** is two numbers multiplied, and so
is area. Put speed up the side in miles per hour and time across in hours, and one
square is `1 mph × 1 hour` = **1 mile**. The *per hour* cancels the *hour*. So the
13.5 she counted is 13.5 miles of road, and the reason you need an integral at all
is that `d = rt` wants a single rate and the speed never sat still. That connection
is the difference between a child who counted some squares and a child who knows
what an integral is for.

**94B — imaginary numbers.** One idea. Finding a square root means asking *what
times what*, with **both factors the same number**. `1 × 1 = +1`. `(-1) × (-1) =
+1`. A real number times itself is **never negative** — positive from anywhere but
zero, and zero from zero — so there is no real number whose square is -1, and
"1 times -1" is not a counter-example, because those are two different numbers. So
`√-1` gets a **name** instead of a value: **i**, and **i² = -1**.

The mechanical skill is three moves: factor out `√-1` using Lesson 54's
product-of-square-roots rule, swap it for *i*, simplify what is left. The book's own
worked instance is `√-36 = √-1 · √36 = 6i`. And when a problem shows her `i²` there
is no radical to factor at all — she writes -1 and finishes: `11i² = 11(-1) = -11`.

**About the figures, and what was and was not rebuilt.** Three things on her page
turn on this, and they are not all the same.

- **Example 94.1's two shaded graphs are pictures and are not reprinted.** They do
  not need to be — the source states both equations, the interval, and both answers
  in text. Both examples are built from those stated numbers, and her page has a
  table rebuilding 94.1b column by column (3, 4 and 5 whole squares, one cut square
  each) which reproduces the book's own 12-and-3 exactly. Have the book open beside
  her anyway so she sees the shading the question refers to.
- **Example 94.2 a) and b) are images, and nothing has been invented in their
  place.** Unlike some earlier lessons there was nothing to reconstruct from: the
  guide prints a bare "a)" and "b)" and its solution lines for those two are images
  as well. Her page says so and tells her to work a) and b) from her own book. What
  *is* on her page is the method the book states in words for them, plus the two
  parts that are printed in full: the body-text `√-36` and part c).
- **Practice problem 194 is a figure too.** It is the same kind of problem as
  Example 94.1a — a horizontal line — but over x = 0 to 5, and its height is only
  in the picture. Read the line's height off her book's graph; the answer is 5
  columns times that height, with nothing cut.

One small note about the guide's own typesetting: on page 2 the sentence "you know
___ = 2" lost the number under its radical sign. It is `√4`, which is the only
reading that fits the sentence after it. Her page says √4.

The book's page-one heading is worth reading to her: **No New Rules.** In a lesson
that says the words *integral* and *imaginary number* for the first time, that is a
reassuring thing for her to hear from the book rather than from you.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Draw a rectangle on graph paper, 3 across and 5 up, and shade it. Ask: **"How
   much space is inside that?"** She will multiply and say 15. Then: **"Now count
   them instead."** Let her actually count to 15 with a fingertip. Say out loud that
   she has just done an integral, and watch her not believe you. That disbelief is
   the right reaction and it is the whole hook.
2. Now draw `y = x + 3` over the same three columns and shade underneath. Ask:
   **"Can you multiply this one?"** You want *no, it's a different height at each
   end*. Do not supply the reason — wait for it. That single answer is why the
   counting method exists.
3. **"So count it."** Insist on column by column, left to right, out loud. When she
   reaches a square the line cuts through, stop her and ask: **"What's that one
   worth?"** You want *a half*. Then ask the better question: **"How do you know
   it's exactly a half and not nearly a half?"** — because the line went in at one
   corner and out at the opposite corner.
4. Now the payoff. **"Say the bottom axis is hours and the side axis is miles per
   hour. What is one square worth?"** Give her a moment; if it does not come, say
   *one mile per hour, for one hour* and let her finish it. **1 mile.** Then:
   **"So how far did the kayak go?"** — 13.5 miles. Close with the question that
   makes it matter: **"Why couldn't we just use d = rt?"** Because there is no one
   rate. That is the reason integrals exist and she can now say it herself.
5. Second half, and hold up one finger for the whole thing. Ask: **"What times
   what makes -1? Same number both times."** Let her try 1, then -1, and 0 if she
   thinks of it, and watch them come out +1, +1 and 0 — never below. Then say the
   sentence: *there isn't one — so we gave it a name instead.* Write `i = √-1` and
   `i² = -1`. Then hand her `11i²` and say nothing at all. If she writes -11
   without help, the second half has landed and you are done in four minutes.

If the first half is lost, go back to step 2 — the whole method exists because a
sloping edge has no single height.

## The classic mix-ups, with the exact wrong answer each one produces

- **Cut squares counted as whole ones.** `12 + 3` gives **15** instead of **13.5**.
  Fix: two piles, written on two separate lines — *12 whole*, *3 half* — before
  anything is added.
- **Halves forgotten entirely.** `3 + 4 + 5` = **12** instead of **13.5**. Always
  an answer that is too *small*. Fix: before writing "area =", ask whether the line
  cut through any squares at all.
- **A sloping edge multiplied like a flat one.** `3 × 3` = **9** instead of
  **13.5**. Multiplying is legal whenever the top edge is flat — 94.1a, and
  practice problem 194 as well — because `y = 5` is the same height everywhere
  and `y = x + 3` is not.
- **The minus pulled out through the radical.** `√-36` written as `-√36` = **-6**
  instead of **6i**. This is the big one in 94B because -6 looks like a real
  answer. Ask her to square it: (-6)(-6) = +36, not -36. Two different questions.
- **`i²` treated as +1.** `11i²` = **11** instead of **-11**. Sign flipped,
  everything else perfect. A real number times itself is never negative — positive
  from anywhere but zero, and zero from zero — which is exactly why *i* had to be
  invented.
- **`√-1` answered as -1.** Test it the way you test any root: (-1)(-1) = **+1**.
  And "1 times -1" fails the same-number requirement. Both candidates die, which is
  the book's own argument.

## What to watch her do

Watch her **hands**, in this order:

1. **Does her finger move along a column, or wander around the shape?** Column by
   column is the difference between a reliable count and one she has to redo. A
   wandering finger double-counts, and she will not be able to tell you where.
2. **Does she write "12 whole" and "3 half" on two lines, or one number?** This is
   the single most diagnostic thing on the first half. A child holding both piles
   in her head is a child who will add 12 and 3.
3. **On the cut squares — does she look at them, or count them from habit?** Ask
   her once to point at the two pieces of a cut square and say whether they are the
   same size. If she cannot, the "worth a half" rule is a rule she is obeying rather
   than one she believes, and it will not survive a line with a different slope.
4. **On `√-36`, does she write the `√-1 · √36` line down?** Watch for the middle
   step appearing on paper. A child who jumps straight to an answer is the child
   who writes -6, because the -1 never got separated out where she could see it.
5. **On `11i²`, does her pencil pause?** It should not. `i²` is a swap, not a
   calculation. A pause means she is trying to work something out, and there is
   nothing there to work out — which is worth saying to her out loud, because it is
   genuinely good news.

Getting 13.5 is not what to watch for. She can get 13.5 by copying the shape of the
worked example. The two-piles habit and the middle line on `√-36` are what survive a
problem with different numbers.

## Extend it

- **Give the squares a job.** Take the same 94.1b graph and re-label the axes three
  different ways: mph against hours (miles), gallons per hour against hours
  (gallons), dollars per day against days (dollars). Same 13.5 every time, three
  different answers to the question "13.5 of *what*". This is the idea underneath
  the whole first half and it costs two minutes.
- **Break the method on purpose.** Draw a curve — `y = x²` from her Lesson 81 page
  is right there — and ask her to count the squares under it. She will hit a square
  that is clearly not half and not whole, and get stuck. That stuck feeling is the
  correct one, and the answer is *smaller squares*, which is exactly what Lessons 90
  and 92 did to Δx from the other direction. Do not resolve it. Leaving it open is
  worth more.
- **A puzzle worth leaving open.** Problem 1084 on her practice set is `x² = 11`,
  which has two answers by Lesson 84's rule. Ask her what `x² = -11` would give.
  She is not expected to solve it — noticing that the answers would have to be
  imaginary is the entire point.
- **Problem 887 is an old friend.** It is the shrimp price table from Lesson 87 —
  budget `$500`, x-small shrimp, maximum whole pounds. Same row-and-column method,
  same estimate-then-divide-then-round-**down**. If she has forgotten it, her
  Lesson 87 page is the place to go, not this one.
- **Ask him about *i*.** Anyone who has done electrical work has met these. AC
  current is the book's own example and it is not a stretch — it is why engineers
  keep imaginary numbers in their pockets. Five minutes of "where do you use this"
  from an adult who has is worth more than another practice problem.

## Where this sits

DIVE Lesson 94, *The Integral and Counting Squares; Imaginary Numbers*. Reviews
**Lessons 30, 54, 78, 81, 84, 90 and 92**.

- **Lesson 81** is the one to revisit if the first half feels like it came from
  nowhere. That is where calculus was defined as the study of rates of change and
  where Δx = 1 first appeared. The integral is the same road with a different
  question on it.
- **Lessons 90 and 92** are the ones that explain why this lesson keeps saying *for
  now* — they are where Δx shrank to 0.01 and then to the infinitesimal. Integrals
  do that too, later.
- **Lesson 78** is the one to revisit if she cannot see why counting squares is
  worth anything: `d = rt` is the connection the book itself makes.
- **Lesson 84** is the one for the second half. It is where she learned that even
  roots refuse a negative inside; 94 is that same fact from the other end, with a
  name attached. **Lesson 54** is where the product-of-square-roots rule lives,
  which is the tool that factors the -1 out, and **Lesson 30** is the original
  square-root definition.

**Proficient** looks like: counts the squares under a flat line correctly, keeps
whole and half squares in separate piles on a sloping one, and can turn `√-36` into
`6i` and `11i²` into `-11` given time.
**Mastered** looks like: says *why* the halves are exactly halves, can explain what
one square is worth once the axes are labelled and why `d = rt` will not do the job
on its own, and does not write `-6` for `√-36` — because she can say out loud that
(-6)(-6) is +36.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 94 (the integral and counting squares; "
            "imaginary numbers) — idempotent.")

    LESSON_NUMBER = 94
    TITLE = "Count the Squares — The Integral, and Imaginary Numbers"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
