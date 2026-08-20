"""Saxon Pre-Algebra Lesson 100 — Matrices.

Reviews Lesson 75, and only Lesson 75 — the book's own first page lists nothing
else. That is also the hook, and Saxon names it himself: *matrix* was defined in
75 as the rows and columns of pixels on a screen, and Lesson 100 keeps that exact
definition and starts doing arithmetic on it.

Two moves, both mechanical. The determinant of a 2 x 2 (Example 100.1, three
parts) and adding or subtracting corresponding cells (Example 100.2, two parts).
Saxon's own body text is five sentences long; almost everything on the child's
page below is the *contrast* between those two moves and the sign traps that sit
inside each of them — which is where the errors block below says a child actually
goes wrong.

Judgement calls, all of them about how the page is typed rather than what it
teaches:

* The Rule reaches this file from the PDF as four loose letters — a, b, c, d —
  with the bracket layout lost. It is read as a top row of `a b` over a bottom
  row of `c d` — the standard convention. The book's own answers cannot settle
  it: a 2 x 2 determinant is unchanged by transposing, so the transposed reading
  (`b` bottom-left, `c` top-right) produces -2, 16 and 0 just as well, and is in
  fact the reading that matches the book's printed `0(3) - 2(1)` and
  `3(7) - 5(1)` letter for letter. The convention is adopted anyway; the only
  consequence a child ever sees is that Saxon's own bc line is then written
  back-to-front (`2(1)` where the letters say `1(2)`), which the page flags,
  more than once, as the same two numbers multiplied.
* A block's `math` field renders as a single line with no line breaks, and the
  book prints its matrices as a typeset square. So matrices are written here as
  `[0 1 ; 2 3]`, the semicolon standing in for the row break. That notation is
  not Saxon's, so the Translation block says so plainly, and a real two-row
  matrix is also shown properly as a table block so she sees the shape at least
  once.
* `det` is likewise this page's word, not the book's. Saxon puts the box itself
  on the left of the equals sign (`a) 0 1 / 2 3 = 0(3) - 2(1) = -2`); written on
  one line that reads as though four numbers equal -2, which they do not. Her
  page says where the word came from.
* The book's solution builds the second product from the bottom-left up —
  `0(3) - 2(1)`, not `ad - bc` in letter order. Both are kept side by side, the
  Rule as stated and the book's own arithmetic beside it, because a child who
  cannot match the two lines decides one of them is wrong.
* No tool block. None of the six widgets (grid, ratiobar, scislide, chart,
  binary, triangle) is a matrix, and a coordinate grid pressed into service as a
  2 x 2 box would teach a wrong thing about what the cells mean. Lessons 78, 82
  and 85 carry no tool either.
* Saxon's own words fix the order for one case only: "a 2 x 2 matrix (2 rows by
  2 columns)". Rows-first as a general convention is this page's claim and is
  made as this page's claim. It is also made next to the one place it looks
  broken — Lesson 75 wrote a screen as 1600 × 1200, which is columns first —
  because she has read Lesson 75 and can find the clash on her own.
* The errors block needs a determinant where `bc` beats `ad` that the page has
  not already worked — Example 100.1a is the other one, `0(3) - 2(1)` — and the
  book's only one is practice problem 2100. Following Lesson 83, that problem is
  not reproduced: the block works the twin `[1 4 ; 3 7]` instead, so the sign
  trap in her own practice set is still hers to walk into.
* Cell names are written `a = 0 → b = 1 → ...`. Four assignments separated by
  spaces alone read as one chain of equalities to the repo's arithmetic sweep,
  which then reports the lesson as broken; the arrow is how the other lessons
  already separate independent statements on one line.
* Saxon never says what a determinant is *for*, so neither does this page — the
  real answer is years of algebra away and inventing a use here would be a
  different lesson. What the page chases instead is the one thing Example 100.1c
  genuinely shows: two identical rows force the determinant to 0. That is the
  reveal, and every number in it is checkable by a twelve-year-old.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_100 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 100 · Pre-Algebra",
        "title": "A matrix is a box of numbers. Where a number sits is part of "
                 "what it means.",
        "thesis": "Four numbers in a square, and two things you are allowed to do "
                  "to them. **Squeeze one box down into a single number** — that "
                  "is the determinant. Or **add two boxes together cell by cell** "
                  "and get another box. The whole lesson is those two moves and "
                  "the difference between them.",
        "formula": "det [a b ; c d]  =  ad - bc",
        "roles": [
            {"tone": "start", "name": "the cell — a number and its address",
             "text": "Every number in a matrix has a position: which row, which "
                     "column. Move the same number to a different cell and you "
                     "have a different matrix. The address is not decoration."},
            {"tone": "move",
             "name": "the diagonals — the only place cells meet in one box",
             "text": "Adding never travels: each cell pairs with the cell at the "
                     "same address in the other box. The determinant is the only "
                     "move that travels, and it travels on the slant. That is "
                     "what makes it a different question."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody puts numbers in a box",
        "paragraphs": [
            "Take a photograph on your phone and zoom in until it falls apart into "
            "coloured squares. You did this in Lesson 75. Each square is a pixel, "
            "and the colour of each pixel is stored as a number — so a single "
            "ordinary photo is somewhere around two million numbers sitting in a "
            "drawer together.",
            "Now here is the problem the phone has. You tap one spot on the screen "
            "and it has to find the number for *that* pixel. It cannot read two "
            "million numbers looking for the right one; you would still be waiting. "
            "It does not have to. It knows the number it wants is in row 812, "
            "column 1,140, and it goes **straight there**.",
            "That only works because the numbers are not in a pile. They are in a "
            "**grid**, and every number's position is a permanent part of its "
            "meaning. That grid is a matrix. Saxon's definition is one line long: "
            "*a two-dimensional array consisting of rows and columns of numbers.*",
            "Because so much of what a computer does is store and fetch numbers by "
            "position, it is worth being able to treat a whole box as **one "
            "thing** — to add two boxes, or to ask a box a question and get one "
            "number back. That is what this lesson is. Two moves, and neither of "
            "them is hard arithmetic.",
            "One honest warning before you start. Your book does not tell you what "
            "a determinant is *for*, and this page will not invent a use for it "
            "either. What it will do is show you the pattern that produces one, and "
            "then chase down something that pattern quietly tells you — Example "
            "100.1c is hiding it, and the drop-down at the bottom of this page asks "
            "you about it.",
            "You have met the word before. In **Lesson 75** a matrix was the rows "
            "and columns of pixels on a screen. Same word, same definition, and now "
            "you start doing arithmetic with it.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Two words, and the size is said rows first",
        "paragraphs": [
            "A **matrix** is a two-dimensional array: rows and columns of numbers. "
            "Two-dimensional means it goes two ways — across and down — and that is "
            "the whole of the restriction.",
            "An **array** is the same idea with the restriction lifted. Like a "
            "matrix, but not limited to two dimensions. That is the word computers "
            "actually use for storing data, and it is why this lesson lives in a "
            "chapter that keeps talking about screens.",
            "You say a matrix's size **rows first**. So a *2 × 2 matrix* is 2 rows "
            "by 2 columns, which is four numbers — and that parenthesis is your "
            "book's own, printed right beside the words *2 x 2 matrix*.",
            "Pin that down now, because you have already met a size written the "
            "other way round. In **Lesson 75** a screen was *1600 × 1200*: 1,600 "
            "pixels across, and 1,200 rows going down. A screen's size is quoted "
            "across-then-down. A matrix's size is said rows first. At 2 × 2 both "
            "readings hand you the same square, so nothing can go wrong today — "
            "which is why today is when to fix the habit.",
            "This lesson never goes past 2 × 2. The book says so, and then says the "
            "other half of it too — much larger matrices exist and people work with "
            "them all the time. You are being handed the smallest one on purpose, "
            "so the pattern is visible.",
            "One more word, and it is the book's own: each position in the matrix is "
            "a **cell**. Not the number — the *position*. A number's cell is part of "
            "what that number means here, in the same way that the 4 in 42 and the 4 "
            "in 24 are the same digit doing two different jobs.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Don't read me the numbers yet. Point at the top-left one and "
                "tell me its address — which row, which column. Now point at the "
                "bottom-right one and do the same. Good. Now here's the real "
                "question: if I took those two numbers and swapped them over, would "
                "it still be the same matrix? No. Same four numbers, different box. "
                "That's the whole reason this thing has a name.\"",
    }),

    (B.KIND_TABLE, {
        "caption": "The four cells of a 2 × 2 matrix, and the letters the Rule uses "
                   "to name them",
        "headers": ["", "column 1 (left)", "column 2 (right)"],
        "rows": [
            {"cells": ["row 1 (top)", "a", "b"], "emphasis": True},
            {"cells": ["row 2 (bottom)", "c", "d"], "emphasis": True},
        ],
        "note": "Those four letters are not mathematics. They are **names for "
                "positions** — `a` is whatever number happens to be sitting "
                "top-left, `d` is whatever is sitting bottom-right. In Example "
                "100.1a the box is `[0 1 ; 2 3]`, so a = 0, b = 1, c = 2 and d = 3. "
                "Read a, b, c, d in order and you are reading the matrix the way you "
                "read a page: across the top row, then across the bottom one. Now "
                "notice the one thing this table exists to show you — **a and d sit "
                "diagonally opposite each other, and so do b and c.** Hold on to "
                "that, because the determinant is built out of exactly those two "
                "pairs and nothing else.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "The determinant: four numbers in, one number out",
        "paragraphs": [
            "Here is the Rule, and it is the only new rule in Lesson 100. **The "
            "determinant of a 2 × 2 matrix of the form `[a b ; c d]` equals "
            "`ad - bc`.**",
            "Read it as a set of instructions rather than a formula. Multiply the "
            "pair that runs top-left to bottom-right. Multiply the pair that runs "
            "the other way. Subtract the second from the first. Done.",
            "Two things about that subtraction are worth saying out loud now, "
            "because both of them cost marks later. **The order is fixed** — `ad` "
            "first, `bc` taken away from it, never the other way round. And the "
            "answer is allowed to come out **negative, or zero**. Example 100.1 has "
            "one of each, which is not an accident on Saxon's part.",
            "The other thing to notice is the **shape** of what you get. You put a "
            "box in and one number came out. That is a genuinely different kind of "
            "operation from anything else in this lesson, and keeping the two "
            "straight is most of the work: a determinant answers with **one "
            "number**, and adding two matrices answers with **a matrix**.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "det [a b ; c d]  =  ad - bc",
        "note": "Two multiplications and one subtraction. Your book writes the "
                "second product starting from the bottom instead — `0(3) - 2(1)` in "
                "Example 100.1a, where the rule in letters would say `0(3) - 1(2)`. "
                "Those are the same two numbers multiplied, because 1 × 2 and 2 × 1 "
                "are the same thing, so **both lines are right** and you can say it "
                "whichever way you find easier. What you may not swap is **which "
                "product comes first**. That one is not a matter of taste.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves for a determinant",
        "steps": [
            {"label": "Name the four cells before you multiply anything.",
             "detail": "Say them out loud in order: a, b, c, d — across the top, "
                       "then across the bottom. It takes three seconds and it is the "
                       "step that stops you multiplying the wrong pair.",
             "math": "[0 1 ; 2 3]   →   a = 0   →   b = 1   →   c = 2   →   d = 3"},
            {"label": "Multiply the down-right diagonal. That is ad.",
             "detail": "Top-left times bottom-right. Write the product down; do not "
                       "hold it in your head while you work out the other one."},
            {"label": "Multiply the other diagonal. That is bc.",
             "detail": "Top-right times bottom-left. Your book starts this one from "
                       "the bottom-left and writes `2(1)`; same two numbers, same "
                       "answer. Write this product down too, next to the first."},
            {"label": "Subtract — first product minus second.",
             "detail": "`ad - bc`, in that order, every time. If the second product "
                       "is the bigger one, your answer is **negative**, and that is "
                       "a real answer, not a sign you made a mistake.",
             "math": "0(3) - 2(1)  =  0 - 2  =  -2"},
        ],
        "after": "Then check the **shape** of what you are holding. A determinant is "
                 "one number. If you have written down a box of four, you answered a "
                 "different question from the one you were asked — go back and look "
                 "at whether the problem said *find the determinant* or *add*.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 100.1a — the determinant of [0 1 ; 2 3]",
        "equation": "det [0 1 ; 2 3]   ·   top row 0 1, bottom row 2 3",
        "steps": [
            {"label": "Look first",
             "text": "Four numbers, and one of them is a **0**. That zero is about "
                     "to wipe out one of the two products completely, which makes "
                     "this the gentlest possible first example — there is really "
                     "only one multiplication to do. Notice it before you start, so "
                     "the 0 in the middle of your working does not look like a "
                     "mistake."},
            {"label": "Step 1 · name the cells",
             "text": "Across the top row, then across the bottom row. Nothing is "
                     "being calculated here. You are just deciding which number is "
                     "playing which part, and it is the step that stops you "
                     "multiplying the wrong pair.",
             "math": "a = 0   →   b = 1   →   c = 2   →   d = 3"},
            {"label": "Step 2 · multiply the down-right diagonal",
             "text": "`a` times `d` — top-left times bottom-right. Zero times "
                     "anything is zero, so this product is gone before it starts.",
             "math": "a × d  =  0(3)  =  0"},
            {"label": "Step 3 · multiply the other diagonal",
             "text": "`b` times `c` — top-right times bottom-left. Your book writes "
                     "this line as `2(1)`, starting from the bottom-left corner "
                     "instead of the top-right. Same two numbers, same product. If "
                     "your page and this one disagree about which order they are "
                     "written in, neither is wrong.",
             "math": "b × c  =  1(2)  =  2      (the book writes it 2(1) = 2)"},
            {"label": "Step 4 · subtract, first minus second",
             "text": "Zero, take away two. Not two take away zero — the order in the "
                     "rule is not a suggestion. The answer is negative, and negative "
                     "is fine.",
             "math": "0(3) - 2(1)  =  0 - 2  =  -2"},
            {"label": "Step 5 · check the shape",
             "text": "One number came out of a box of four. That is exactly what a "
                     "determinant is supposed to do, so the answer looks the way it "
                     "should. It is worth doing this check every single time, "
                     "because the second half of this lesson answers with a box "
                     "instead and the two questions look almost identical on paper.",
             "math": "det [0 1 ; 2 3]  =  -2"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "100.1b and 100.1c",
        "question": "Find the determinants of  b) [3 1 ; 5 7]   and   c) [2 1 ; 2 1].",
        "steps": [
            {"label": "b) Name the cells first, same as before",
             "text": "Across the top, then across the bottom. No zeros to help you "
                     "this time, so both multiplications are real ones.",
             "math": "a = 3   →   b = 1   →   c = 5   →   d = 7"},
            {"label": "b) Both diagonals, then subtract",
             "text": "Down-right first: 3 times 7. Then the other one: your book "
                     "writes it `5(1)`, which is 5. Twenty-one take away five.",
             "math": "3(7) - 5(1)  =  21 - 5  =  16"},
            {"label": "c) Now the same recipe on a box that looks odd",
             "text": "a = 2, b = 1, c = 2, d = 1. Do not stop to think about why the "
                     "rows look the way they do — run the recipe exactly as you did "
                     "twice already and see what comes out.",
             "math": "a = 2   →   b = 1   →   c = 2   →   d = 1"},
            {"label": "c) The two products come out identical",
             "text": "Down-right: 2 times 1 is 2. The other diagonal: 2 times 1 is "
                     "also 2. Subtract and there is nothing left. **Zero is a "
                     "perfectly good determinant** — it is an answer, not a failure "
                     "to find one.",
             "math": "2(1) - 2(1)  =  2 - 2  =  0"},
            {"label": "Both answers, side by side",
             "text": "Two boxes went in and two single numbers came out — one of "
                     "them positive, one of them zero, and neither of them a box. "
                     "That is the shape a determinant question always gives "
                     "back. Hold both of them in view for a second, because the "
                     "next half of this lesson answers with a box instead.",
             "math": "det [3 1 ; 5 7]  =  16   →   det [2 1 ; 2 1]  =  0"},
            {"label": "Then stop and look at c) again",
             "text": "Something about that particular box forced the two products to "
                     "be the same number, and it was not luck. Look at "
                     "`[2 1 ; 2 1]` for ten seconds and see whether you can say what "
                     "it was. The drop-down near the bottom of this page asks you "
                     "exactly that, so decide on your answer before you open it."},
        ],
        "answer": "16   ·   0",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "Adding two matrices: four little sums, and the cells never mix",
        "paragraphs": [
            "The second half of the lesson is easier than the first, and Saxon says "
            "so in his own solution: *addition and subtraction is simply a matter of "
            "finding the sum or difference between corresponding cells.*",
            "**Corresponding** is the load-bearing word. Top-left goes with "
            "top-left. Top-right with top-right. Bottom-left with bottom-left, "
            "bottom-right with bottom-right. Four separate little sums, done in four "
            "separate places, and the answers stay where you found them.",
            "So nothing crosses over. The top-left number of one matrix never meets "
            "the bottom-right number of the other — which is worth saying because "
            "the determinant is the one place in this lesson where numbers *do* meet "
            "on the diagonal, and it is the half you did first. Adding never "
            "travels: every number stays at its own address. The determinant is "
            "the only move that travels, and it travels on the slant.",
            "And the answer is a **matrix**, the same size as the two you started "
            "with. Two 2 × 2 boxes in, one 2 × 2 box out. If you finish an addition "
            "problem holding a single number, you have answered the determinant "
            "question by accident.",
            "For subtraction there is one extra thing to be careful about, and it "
            "is the same thing you are careful about in ordinary subtraction: **the "
            "order matters.** The first matrix minus the second, cell by cell. Swap "
            "them and every number in your answer changes sign — except a cell that "
            "came out 0, which has no sign to flip.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Put your hand over both matrices so only the two top-left "
                "corners show. What's the sum of just those two? Write it in the "
                "top-left corner of your answer and nowhere else. Now uncover "
                "the two top-right corners and do that pair. You're doing four tiny "
                "problems, not one big one — and the thing to watch for is a number "
                "moving house.\"",
    }),

    (B.KIND_TABLE, {
        "caption": "Example 100.2a, done one cell at a time: "
                   "[0 1 ; 2 3] + [2 1 ; 2 1]",
        "headers": ["cell", "from the first matrix", "from the second matrix",
                    "what goes in that cell of the answer"],
        "rows": [
            {"cells": ["top left", "0", "2", "0 + 2 = 2"], "emphasis": True},
            {"cells": ["top right", "1", "1", "1 + 1 = 2"]},
            {"cells": ["bottom left", "2", "2", "2 + 2 = 4"]},
            {"cells": ["bottom right", "3", "1", "3 + 1 = 4"], "emphasis": True},
            {"cells": ["the answer", "—", "—", "[2 2 ; 4 4]"]},
        ],
        "note": "Take the four answers in the last column and fold them back into "
                "a box: 2 and 2 in the top row, 4 and 4 in the bottom row. That is "
                "the whole method, written out at its slowest. Now look at what is "
                "**not** in "
                "this table — there is no row where a number from one matrix meets a "
                "number from a different cell of the other. Every row here stays "
                "inside one address. That is what *corresponding* means, and it is "
                "the entire difference between this half of the lesson and the "
                "determinant half.",
    }),

    (B.KIND_WORKED, {
        "number": "100.2",
        "question": "Add or subtract:  a) [0 1 ; 2 3] + [2 1 ; 2 1]   "
                    "b) [3 1 ; 5 7] - [0 1 ; 2 3]",
        "steps": [
            {"label": "First, notice that you have seen all of these boxes before",
             "text": "`[0 1 ; 2 3]`, `[2 1 ; 2 1]` and `[3 1 ; 5 7]` are the same "
                     "three matrices whose determinants you found in Example 100.1. "
                     "Saxon reused them deliberately. Same boxes, completely "
                     "different question — which is the cleanest possible reminder "
                     "that the *question* decides what you do, not the numbers."},
            {"label": "a) Four sums, one per cell",
             "text": "Top-left with top-left: 0 + 2. Top-right with top-right: "
                     "1 + 1. Bottom-left: 2 + 2. Bottom-right: 3 + 1. Write the four "
                     "additions out in their places first and only then work them "
                     "out — that middle line is the book's own, and it is what stops "
                     "a number wandering into the wrong cell.",
             "math": "[0+2  1+1 ; 2+2  3+1]  =  [2 2 ; 4 4]"},
            {"label": "b) Subtraction, and the order is not negotiable",
             "text": "The first matrix is the one you take *from*. So it is 3 - 0 in "
                     "the top-left, not 0 - 3. Then 1 - 1, then 5 - 2, then 7 - 3. "
                     "Same four positions, same care.",
             "math": "[3-0  1-1 ; 5-2  7-3]  =  [3 0 ; 3 4]"},
            {"label": "Check the shape of both answers",
             "text": "Each one is a **matrix**, 2 rows by 2 columns, four numbers. "
                     "That is what an addition or subtraction question gives back. "
                     "If either of your answers is a single number, you found a "
                     "determinant instead — which is the right arithmetic done to "
                     "the wrong question."},
        ],
        "answer": "[2 2 ; 4 4]   ·   [3 0 ; 3 4]",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Two of the lines below are **this page's shorthand, not your "
                 "book's**, and it is only fair to say which. Your book prints each "
                 "matrix as a proper square of numbers with a bracket around it. A "
                 "line of typing here has to fit on one line, so it gets written "
                 "flat, with a semicolon where the row break should be. The "
                 "vocabulary in the rest of the table is Saxon's own — with one "
                 "caveat. The comparison with a screen, in the 2 × 2 row, is this "
                 "page's point and not his: your book says *2 rows by 2 columns* "
                 "about this matrix, and stops there.",
        "rows": [
            {"symbol": "matrix", "plain": "a two-dimensional array: rows and columns "
                                          "of numbers. Also defined in Lesson 75",
             "example": "a screen's pixels"},
            {"symbol": "array", "plain": "like a matrix, but NOT limited to two "
                                         "dimensions. What computers store data in",
             "example": "rows, columns and layers"},
            {"symbol": "cell", "plain": "one position in the matrix — the address, "
                                        "not the number sitting at it",
             "example": "the top-left cell"},
            {"symbol": "2 × 2", "plain": "2 rows by 2 columns. A matrix's size is "
                                         "said rows first — a screen's is not",
             "example": "four cells"},
            {"symbol": "[0 1 ; 2 3]", "plain": "THIS PAGE'S shorthand for a matrix "
                                               "written flat: the semicolon is the "
                                               "break between the two rows",
             "example": "top 0 1, bottom 2 3"},
            {"symbol": "a b c d", "plain": "names for the four positions: a "
                                           "top-left, b top-right, c bottom-left, "
                                           "d bottom-right",
             "example": "in [0 1 ; 2 3], a = 0"},
            {"symbol": "determinant", "plain": "the single number a 2 × 2 matrix "
                                               "gives you when you do ad - bc to it",
             "example": "16"},
            {"symbol": "det", "plain": "THIS PAGE'S way of writing 'the determinant "
                                       "of'. Your book puts the box itself on the "
                                       "left of the equals sign instead",
             "example": "det [3 1 ; 5 7] = 16"},
            {"symbol": "ad - bc", "plain": "multiply the down-right diagonal, then "
                                           "take away the down-left one",
             "example": "0(3) - 2(1) = -2"},
            {"symbol": "0(3)", "plain": "0 times 3. The brackets mean multiply — "
                                        "there is no new operation hiding in them",
             "example": "0"},
        ],
        "after": "The one to be careful with is `[2 2 ; 4 4]`. That is **one** "
                 "matrix, not two — the semicolon is a line break, not a divider "
                 "between two boxes. When you write your own working, write the "
                 "matrices as proper squares the way your book does. The flat "
                 "version exists here only because this page cannot stack lines the "
                 "way a printed page can.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Adding the two products instead of subtracting them.",
             "wrong": "0(3) + 2(1)  =  0 + 2  =  2",
             "right": "0(3) - 2(1)  =  0 - 2  =  -2",
             "note": "**2 instead of -2.** The rule contains exactly one minus sign "
                     "and it is doing all the work — `ad - bc`. Everything else in "
                     "the line is multiplication, so the hand gets into a rhythm of "
                     "combining and combines the wrong way at the end. Say the rule "
                     "as a sentence before you write it: *multiply, multiply, then "
                     "take the second one away.*"},
            {"name": "Multiplying across the rows instead of down the diagonals.",
             "wrong": "0(1) - 2(3)  =  0 - 6  =  -6",
             "right": "0(3) - 2(1)  =  0 - 2  =  -2",
             "note": "**-6 instead of -2.** Reading across is what you do with every "
                     "other line of type you have ever met, so the eye does it here "
                     "for free. A determinant reads **on the slant**: `a` pairs with "
                     "`d`, and `b` pairs with `c`. Draw the two diagonal lines "
                     "lightly across the box in pencil before you multiply anything "
                     "and this mistake becomes almost impossible to make."},
            {"name": "Taking the smaller product from the bigger, out of habit.",
             "wrong": "det [1 4 ; 3 7]  =  12 - 7  =  5",
             "right": "det [1 4 ; 3 7]  =  1(7) - 3(4)  =  7 - 12  =  -5",
             "note": "**5 instead of -5** — the right size and the wrong sign, which "
                     "is the hardest kind of wrong answer to catch. Years of "
                     "arithmetic have trained you to put the bigger number first, "
                     "and here you may not. `ad` goes first even when it is the "
                     "smaller one. One of today's four problems is built exactly "
                     "like this one, so you will meet it within the hour."},
            {"name": "Subtracting the two matrices the wrong way round.",
             "wrong": "[0-3  1-1 ; 2-5  3-7]  =  [-3 0 ; -3 -4]",
             "right": "[3-0  1-1 ; 5-2  7-3]  =  [3 0 ; 3 4]",
             "note": "Every sign flipped except the 0, and the answer still looks "
                     "tidy enough to hand in — the top-right cell is 1 - 1 either "
                     "way round, and it is printed identically on both lines above. "
                     "In Example 100.2b the **first** matrix is the one you take "
                     "from, exactly like ordinary subtraction — 7 - 3 is not 3 - 7. "
                     "Whichever matrix is written first in the question stays first "
                     "in every one of the four little subtractions."},
            {"name": "Answering an add-or-subtract question with a single number.",
             "wrong": "[0 1 ; 2 3] + [2 1 ; 2 1]  =  0+1+2+3+2+1+2+1  =  12",
             "right": "[0 1 ; 2 3] + [2 1 ; 2 1]  =  [2 2 ; 4 4]",
             "note": "**12 instead of a matrix.** This one comes from doing the "
                     "determinant half first and getting used to a box turning into "
                     "a number. Adding does not do that. Two boxes go in and **one "
                     "box comes out**, the same size as the ones you started with. "
                     "Before you write your final line, ask which shape the question "
                     "wanted — one number, or four."},
        ],
    }),

    (B.KIND_REVEAL, {
        "prompt": "Example 100.1c came out to 0. Look at [2 1 ; 2 1] again and work "
                  "out what it is about those four numbers that forced the answer to "
                  "be zero. Then build a different 2 × 2 matrix you are sure has a "
                  "determinant of 0 — without doing any arithmetic to check.",
        "answer": "**Its two rows are identical.** Watch what that does to the "
                  "rule:   →   a = 2   →   b = 1   →   c = 2   →   d = 1   →   "
                  "ad = 2 × 1 = 2   →   bc = 1 × 2 = 2   →   "
                  "the two products are the same pair of numbers multiplied in the "
                  "other order, so the subtraction has "
                  "nothing left to do   →   2 - 2 = 0   →   That is not luck and it "
                  "is not special to these numbers. Copy any top row into the bottom "
                  "row and the same thing happens: [7 4 ; 7 4] gives "
                  "7 × 4 - 4 × 7 = 28 - 28 = 0.   →   It works the other way up too. "
                  "Copy a **column** instead of a row — [5 5 ; 9 9] — and you get "
                  "5 × 9 - 5 × 9 = 45 - 45 = 0.   →   So you can build one to order "
                  "in about four seconds: write any two numbers, write the same two "
                  "underneath, and you are holding a matrix whose determinant is 0 "
                  "before you multiply a thing. **A repeated row or a repeated "
                  "column always kills the determinant.**",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A **matrix** is a two-dimensional array — rows and columns of numbers. "
            "Same word and same definition as Lesson 75's grid of pixels. An "
            "**array** is the same idea without the two-dimension limit, and it is "
            "what computers store data in.",
            "Say a matrix's size **rows first**: 2 × 2 means 2 rows by 2 columns, "
            "four cells. A screen's size is quoted the other way round — Lesson "
            "75's 1600 × 1200 was 1,600 across and 1,200 down. This lesson never "
            "goes bigger than 2 × 2, but much bigger matrices exist.",
            "A **cell** is a position, not a number. Where a number sits is part of "
            "what it means — move it and you have a different matrix.",
            "**Determinant of [a b ; c d] = ad - bc.** Down-right diagonal first, "
            "then take away the down-left one.",
            "**Subtract in that order, always.** `ad - bc`, even when `bc` is the "
            "bigger product. A determinant is allowed to be negative, and allowed "
            "to be zero.",
            "Add and subtract by **corresponding cells** — top-left with top-left, "
            "and so on. Four separate little sums, and nothing crosses over.",
            "Matrix subtraction runs **first matrix minus second**, cell by cell. "
            "Swap them and every non-zero number in your answer flips sign.",
            "Check the **shape** of your answer against the question. A determinant "
            "gives back **one number**; adding or subtracting gives back **a "
            "matrix**. The two questions look nearly identical on the page.",
            "Two identical rows — or two identical columns — always give a "
            "determinant of **0**. That is what Example 100.1c is really showing "
            "you.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 100 first. If it didn't quite land, this is here to fix "
    "that. Two new words — one of them you already half know from Lesson 75 — and "
    "two things you can do to a box of four numbers: squeeze it down into a single "
    "number, or add two boxes together cell by cell. Also — this is Lesson 100. "
    "Your book stops to say so, and it's right to."
)

PARENT_CONTENT = """## The big idea

Lesson 100 is short, mechanical and easy to get right. The genuinely new idea in
it is not the arithmetic.

The idea is that **a matrix is a single mathematical object made of several
numbers, and where a number sits is part of what it means.** Saxon's definition is
one line — *"a two-dimensional array consisting of rows and columns of numbers"* —
and it is the same word she already met in **Lesson 75**, where a screen was rows
and columns of pixels. He puts *array* beside it: like a matrix, but not limited to
two dimensions, and it is the word for what computer programs actually store data
in. His reason for teaching this at all is stated plainly: computers retrieve and
store data in matrices, so a few basic relationships are worth knowing.

Then two moves, both easy.

**The determinant.** `ad - bc`, where a, b, c, d are simply the four positions read
across the top row and then across the bottom. Multiply the down-right diagonal,
multiply the down-left one, subtract the second from the first. Example 100.1 gives
three of them and Saxon has chosen them carefully — one comes out **negative**
(`-2`), one **positive** (`16`), and one **zero** (`0`). If she thinks a negative or
a zero means she made an error, she will unpick correct work.

**Addition and subtraction.** Saxon's own sentence is the whole method: *addition
and subtraction is simply a matter of finding the sum or difference between
corresponding cells.* Top-left with top-left, top-right with top-right. Four little
sums in four separate places.

The contrast between those two moves is the only real conceptual trap here, and it
is worth saying to her out loud: **a determinant turns one matrix into one number;
adding turns two matrices into another matrix.** They also treat the diagonal in
opposite ways — the determinant is the *only* place in this lesson where the
top-left number ever meets the bottom-right one. Adding never travels — each cell
pairs with the cell at the same address in the other matrix. The determinant is the
only move that travels, and it travels on the slant.

**About the notation on her page.** Her book prints each matrix as a proper square
of four numbers. A web page's equation lines are single lines, so matrices are
written flat there as `[0 1 ; 2 3]`, with the semicolon standing in for the row
break, and the word `det` in front where the book simply puts the box on the left of
the equals sign. Both of those are this page's shorthand, not Saxon's, and her
Translation block says so in as many words. Ask her to write her own working as
proper squares, the way the book does.

One more small thing worth honouring. The book stops on this page to congratulate
her on reaching Lesson 100 and tells her to finish strong. Read that line to her.
It is the only one of its kind in the guide.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Write any four numbers in a square. Ask: **"If I swap the top-left one with the
   bottom-right one, is it still the same matrix?"** You want *no*. Same four
   numbers, different box. That single answer is the definition doing its job, and
   it is worth more than the words "two-dimensional array."
2. Point at each cell in turn and have her give you its **address** — row and
   column, in that order. Then ask: **"How would you describe the size of this
   thing?"** You want *2 by 2*, and if she says it the other way round, that is fine
   here and will not be fine later: a matrix's size is said rows first. If she
   objects that Lesson 75 wrote a screen as 1600 × 1200 — 1,600 across, 1,200 down —
   she is right, and she has found the one place the two conventions differ. A
   screen is quoted across-then-down; a matrix is not. Her own page says so.
3. Draw the two diagonals across the box in pencil. **"Which two numbers are on this
   line? And on this one?"** Then give her the rule as a sentence rather than a
   formula: *multiply that pair, multiply the other pair, take the second away from
   the first.* Do Example 100.1a together — the `0` makes it almost free.
4. Now go straight to Example 100.1c, `[2 1 ; 2 1]`, and let her get **0**. Ask:
   **"Is zero an answer, or did something go wrong?"** She needs to hear that it is
   an answer. Then leave the question hanging — *why* did that box give zero? — and
   send her to the drop-down at the bottom of her page, which asks exactly that.
   Make her commit to a guess before she opens it.
5. For the second half, put two matrices side by side and cover everything except
   the two top-left corners with your hand. **"What's the sum of just those two?"**
   Move the hand to the next pair, three more times. Then ask the question that
   separates the two halves of the lesson: **"How many numbers are in your
   answer?"** Four. A
   determinant gave her one. Same boxes — Example 100.2 reuses the exact matrices
   from 100.1 — completely different shape of answer, and the *question* is what
   decides which.

If she is lost anywhere, it is almost certainly step 3. Go back to the pencilled
diagonals; a determinant mistake is either a pair chosen wrongly or the two
products mishandled once she has them — added instead of taken away, or taken
away the wrong way round — and the pairs are the half you can see from across the
table.

## The classic mix-ups, with the exact wrong answer each one produces

- **Adding the two products.** `0(3) + 2(1)` gives **2** instead of **-2**. The rule
  has exactly one minus sign in it and it is doing all the work. Fix: say it as a
  sentence — *multiply, multiply, then take the second one away.*
- **Multiplying across the rows.** `0(1) - 2(3)` gives **-6** instead of **-2**.
  Reading across is what she does with every other line of type in her life. Fix:
  pencil the two diagonals onto the box before multiplying anything.
- **Bigger product first.** On a box like `[1 4 ; 3 7]` she writes `12 - 7` = **5**
  instead of `7 - 12` = **-5**. Right size, wrong sign, hardest to catch. `ad` goes
  first even when it is the smaller one. One of today's four practice problems is
  built exactly like this, so leave it for her rather than working it together.
- **Subtracting the matrices backwards.** On Example 100.2b she computes
  `[0-3  1-1 ; 2-5  3-7]` = **[-3 0 ; -3 -4]** instead of **[3 0 ; 3 4]**. Every
  sign flipped except the 0, and it still looks tidy. Fix: the matrix written
  first in the question stays first in all four little subtractions.
- **A single number where a matrix belongs.** She sums all eight numbers on Example
  100.2a and writes **12** instead of **[2 2 ; 4 4]**. This is the determinant half
  bleeding into the addition half. Fix: before the last line, ask what shape the
  question wanted — one number, or four.
- **Treating 0 or a negative as a failure.** She gets `-2` or `0` and starts over.
  Both are real determinants, and Saxon put one of each into Example 100.1 on
  purpose.

## What to watch her do

Watch her **hands**, in this order:

1. **Does she label the four cells before she multiplies?** You want to see a, b, c,
   d written on or beside the box, or at least her finger touching each in turn. A
   child who starts multiplying immediately is choosing pairs by eye, and by eye is
   how rows get multiplied instead of diagonals.
2. **Does her pencil draw the diagonals?** Two light strokes across the box. This is
   the most diagnostic thing on the page — you can see it from across the table, and
   a child who draws them essentially cannot make mix-up 2.
3. **Does she write both products down before subtracting?** Watch for one product
   held in her head while she works out the other. That is where the order of the
   subtraction gets lost, because by the time she writes anything she is holding two
   loose numbers with no memory of which was which.
4. **On the addition, does her hand stay inside one cell at a time?** The correct
   movement is four separate little stops, each one landing in the matching position
   of the answer. A hand that roams is a number about to move house.
5. **At the very end, does she look back at the question?** The tell is a glance up
   before the final line. She is checking whether she was asked for one number or for
   a box, and that glance is the habit worth more than any of the arithmetic here.

Getting `16` is not what to watch for. The arithmetic in this lesson is easy enough
that she can be right for the wrong reason all afternoon. The diagonals and the
final glance are what survive a matrix bigger than 2 × 2.

## Extend it

- **Ask her to make one that gives zero**, before she reads the drop-down. If she
  can hand you `[7 4 ; 7 4]` and say why, she has got hold of something real: a
  repeated row, or a repeated column, always kills the determinant. Then ask the
  harder follow-up — *can you make one that gives zero WITHOUT repeating a row?*
  (`[1 2 ; 2 4]` does it: `1 × 4 - 2 × 2 = 0`.) That one is a genuine puzzle and she
  is not expected to find it quickly.
- **Practice problem 4 is the one to do out loud.** `[4 5 ; 3 4] - [4 4 ; 4 4]`
  gives **[0 1 ; -1 0]** — the bottom-left cell is `3 - 4 = -1`, and a child who has
  been adding cheerfully for ten minutes will often write `1`. Negative numbers
  inside a matrix are perfectly ordinary and she should see one today.
- **Show her a spreadsheet.** Open anything with rows and columns and point at the
  cell reference in the corner. That is Saxon's word exactly, and the whole reason
  spreadsheets work at all is the idea in Idea 1 of her page.
- **Ask what a 3-D array would look like.** Saxon defines *array* as "not limited to
  two dimensions" and then drops it. Rows, columns, and layers stacked behind each
  other — a video is one (rows, columns, and frames in time). She is not being tested
  on it; meeting the idea is the point of the definition being there at all.

## Where this sits

DIVE Lesson 100, *Matrices*. Reviews **Lesson 75**, and that is the only lesson the
book's own first page lists.

**Lesson 75 is the one to revisit if the word itself is the problem** — that is
where a matrix was first defined, as the rows and columns of pixels that make up a
screen, and where "1600 × 1200" first meant 1,200 rows of 1,600. Note the ordering
there: a screen's size is quoted across-then-down, while a matrix's size is said
rows first, and her page names that difference so the two lessons do not look like
they contradict each other. Lesson 100 changes nothing about the definition. It
just starts doing arithmetic to the box.

Practice problems 1 through 4 are the new material: two determinants
(`[1 2 ; 0 4]` and `[1 4 ; 3 6]`) and one addition and one subtraction. Everything
after problem 4 is review from earlier lessons and is not touched by this page.

**Proficient** looks like: finds the determinant of a 2 × 2 with the numbers in
front of her, and adds two matrices cell by cell, given time.
**Mastered** looks like: keeps the sign right without being reminded when `bc` is
the bigger product, subtracts matrices in the stated order, and never hands back a
single number where a matrix was asked for — or the reverse.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 100 (matrices — determinants, adding "
            "and subtracting) — idempotent.")

    LESSON_NUMBER = 100
    TITLE = "Matrices — A Box of Numbers, and Two Things You Can Do to It"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
