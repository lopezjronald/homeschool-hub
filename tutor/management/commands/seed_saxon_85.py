"""Saxon Pre-Algebra Lesson 85 — Addition and Subtraction with Mixed Measures;
Simplifying Complex Fractions.

Reviews Lessons 23 and 25. Lesson 25 is the hook for the first half (equivalent
measures: 12 in = 1 ft, 60 s = 1 min, 60 min = 1 hr) and Lesson 23 is the whole
of the second half (dividing a fraction by a fraction — invert and multiply).
The book's own first page says it: "No New Rules or Definitions."

Saxon's single trick for the first half is stated outright in the text and it is
what this page is built around: *think of the different measures as place
values.* An hours place, a minutes place, a seconds place — and you carry between
them exactly the way you carry between tens and ones. Only the number a column
fills up at changes.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Example 85.3 is printed as stacked fractions that cannot be
reproduced here, so it is rewritten with parentheses for each floor and ÷ for the
main bar, and the page says so where she reads it.

85B follows the book's WRITTEN method, not the shortcut: multiply above AND below
by the reciprocal of the denominator, cancel, simplify (src:96-100). The bottom
floor cancelling to 1 is why the shortcut is legal, and Saxon only licenses
skipping it at part c) — so the page shows the full line three times first. Every
worked line in Example 85.3 is written the long way; a page that only ever showed
`(a/b) · (d/c)` would leave her unable to recognise the book's own working.

    python manage.py seed_saxon_85 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 85 · Pre-Algebra",
        "title": "Measures in columns, and fractions stacked on fractions",
        "thesis": "A measure written in two or three units is a **number in "
                  "columns** — a feet column and an inches column, or an hours, "
                  "minutes and seconds column. You have added in columns for "
                  "years. The only thing that changes is the number a "
                  "column fills up at.",
        "formula": "50 in + 8 ft 3 in = 12 ft 5 in",
        "roles": [
            {"tone": "start", "name": "the big place",
             "text": "Feet. Hours. The column on the left. It gains a whole "
                     "group when a carry comes out of the column beside it, and "
                     "it gives one up when that column has to borrow."},
            {"tone": "move", "name": "the small place",
             "text": "Inches. Minutes and seconds. It is finished only when it "
                     "is under its limit: under 12 for inches, under 60 for "
                     "minutes and seconds."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone stacks measures into columns",
        "paragraphs": [
            "Some clocks have three hands — one for hours, one for minutes, one "
            "for seconds. When the doctor measures you, the number goes on the "
            "chart as feet and inches, not as a pile of inches. People write "
            "measurements in two or three units all the time, because that is "
            "how they are easiest to read.",
            "Then somebody asks a question that needs them added. One drive took "
            "2 hours 30 minutes 20 seconds and the next took 3 hours 40 minutes "
            "50 seconds — how long were you in the car? You cannot heap all six "
            "numbers together, because the seconds and the minutes and the hours "
            "are not the same size of thing.",
            "Saxon's answer is one sentence long, and it is the whole lesson: "
            "**think of the different measures as place values.** An hours "
            "place, a minutes place, a seconds place. Line them up, work each "
            "one on its own, and carry between them.",
            "The second half of the lesson is a different subject that happens "
            "to be on the same page. A **complex fraction** is a fraction with "
            "fractions inside it. That is also not new — it is Lesson 23's "
            "invert-and-multiply, with letters where the numbers used to be.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "A mixed measure is a number written in columns",
        "paragraphs": [
            "Take an ordinary number: 342. That is not one thing. It is 3 "
            "hundreds, 4 tens and 2 ones, sitting in three columns, and the "
            "columns have a rate — ten ones make one ten, ten tens make one "
            "hundred.",
            "Now look at `2 hr 30 min 20 s`. Same shape exactly. An hours "
            "column holding 2, a minutes column holding 30, a seconds column "
            "holding 20.",
            "There is one difference and it is the whole lesson. Ordinary "
            "columns fill up at ten. Seconds and minutes fill up at **60**. "
            "Inches fill up at **12**.",
            "So when you add two mixed measures, you do what you have always "
            "done: add each column straight down on its own, then go back and "
            "fix any column that went over. The fixing is called carrying, and "
            "you already know how to do it — just at ten instead of sixty.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Look at 3 hr 45 min. That isn't one number — it's two "
                "columns, an hours column and a minutes column, exactly like the "
                "tens and the ones in 34. So we add the columns separately, and "
                "then we tidy up. The only thing you have to remember is that "
                "this column doesn't fill up at ten. It fills up at sixty.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "A column is not finished until it is under its limit",
        "paragraphs": [
            "Here is the part that trips people, and it happens **before** you "
            "add anything. Saxon asks you to add `50 in + 8 ft 3 in`. One of "
            "those has columns and the other is a pile.",
            "So the pile has to be sorted. And there is more than one way to "
            "sort it. Every single one of these is genuinely 50 inches: "
            "`1 ft 38 in`, `2 ft 26 in`, `3 ft 14 in`, `4 ft 2 in`.",
            "Only the last one is **properly converted**. The other three still "
            "have whole feet hiding in the inches place — 38, 26 and 14 are all "
            "over 12, so there is at least one more foot in there that has not "
            "been moved across. `4 ft 2 in` is the one with nothing left to "
            "move.",
            "That gives you a test you can apply to any answer in this lesson, "
            "including your own: **is the small column under its limit?** "
            "Inches under 12. Minutes and seconds under 60. If not, you are not "
            "wrong yet — you are just not finished.",
            "Subtraction runs the same idea backwards. If the inches column at "
            "the top is too small to subtract from, you **borrow** one whole "
            "foot from the feet column and it arrives in the inches column as "
            "12 more inches. Same move as long subtraction, different rate.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe",
        "title": "Adding and subtracting mixed measures, the same way every time",
        "steps": [
            {"label": "Give every amount the same columns.",
             "detail": "If one line says `hr min s`, the other line needs all "
                       "three too. A column that is not written is a **zero** — "
                       "`60 hr` is really `60 hr 0 min 0 s`."},
            {"label": "Convert anything that arrived as a pile.",
             "detail": "`50 in` has no feet written at all. Ask how many whole "
                       "feet are inside it, and what is left over.",
             "math": "50 = 4 × 12 + 2"},
            {"label": "Stop converting only when the small column is under its limit.",
             "detail": "Inches under 12. Minutes and seconds under 60. "
                       "`3 ft 14 in` is a true amount and an unfinished one."},
            {"label": "Line the columns up and work each one on its own.",
             "detail": "Seconds under seconds, minutes under minutes, inches "
                       "under inches. Nothing crosses over yet."},
            {"label": "Carry left when a column goes over its limit.",
             "detail": "70 seconds is one whole minute with 10 seconds left "
                       "over. The whole minute moves into the column on the "
                       "left; the leftover stays.",
             "math": "70 - 60 = 10"},
            {"label": "Borrow right when a column is too small to subtract from.",
             "detail": "Take 1 from the column on the left and it arrives here "
                       "as a full group — 12 if it was a foot, 60 if it was an "
                       "hour or a minute.",
             "math": "3 + 12 = 15"},
            {"label": "Read your answer back and check every limit.",
             "detail": "One last look along the row. Any column still over its "
                       "limit means one more carry to do."},
        ],
        "after": "Subtraction comes with a free check and Saxon spells it out: "
                 "**add your answer back onto the number you subtracted.** You "
                 "should land exactly on the number you started with. It takes "
                 "about four seconds and it catches a bad borrow every time.",
    }),

    (B.KIND_TABLE, {
        "caption": "What each column fills up at",
        "headers": ["column", "it fills up at", "one full group moves left as",
                    "so a finished answer has"],
        "rows": [
            {"cells": ["seconds", "60 s", "1 min", "seconds under 60"]},
            {"cells": ["minutes", "60 min", "1 hr", "minutes under 60"]},
            {"cells": ["inches", "12 in", "1 ft", "inches under 12"]},
            {"cells": ["ones (an ordinary number)", "10", "1 ten",
                       "digits under 10"], "emphasis": True},
        ],
        "note": "The shaded row is the one you have done since first grade. "
                "Nothing about the **method** changes as you go up the table — "
                "only the number in the middle. That is the entire content of "
                "Lesson 85A, and it is why the book's first page says *No New "
                "Rules or Definitions*.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 85.1a — 50 in + 8 ft 3 in",
        "equation": "50 in  +  8 ft 3 in",
        "steps": [
            {"label": "Look first",
             "text": "One of these is written in columns and one is not. "
                     "`8 ft 3 in` has a feet column and an inches column. "
                     "`50 in` is a pile of inches with no feet column at all. "
                     "Nothing can line up until that pile is sorted into feet "
                     "and inches."},
            {"label": "Step 1 · how many whole feet are in 50 inches?",
             "text": "Twelve inches make one foot, so ask how many twelves fit "
                     "inside 50. Four of them do, and 2 inches are left over "
                     "that cannot make another foot.",
             "math": "50 = 4 × 12 + 2"},
            {"label": "Step 2 · write it with columns",
             "text": "Four whole feet in the feet place, 2 inches in the inches "
                     "place. And 2 is under 12, so this conversion is finished.",
             "math": "50 in = 4 ft 2 in"},
            {"label": "Step 3 · why not 3 ft 14 in?",
             "text": "Because `3 ft 14 in` really is 50 inches — the arithmetic "
                     "is fine, which is exactly what makes it dangerous. But 14 "
                     "is over 12, so there is still a whole foot sitting in the "
                     "inches place that belongs one column to the left. "
                     "`1 ft 38 in` and `2 ft 26 in` have the same problem. Only "
                     "`4 ft 2 in` has nothing left to move.",
             "math": "3 × 12 + 14 = 50"},
            {"label": "Step 4 · stack them and add each column",
             "text": "Feet under feet, inches under inches. Add the inches "
                     "column: 2 and 3. Then the feet column: 4 and 8. The two "
                     "columns never talk to each other.",
             "math": "2 + 3 = 5  →  4 + 8 = 12"},
            {"label": "Step 5 · check the small column",
             "text": "The inches place reads 5. That is under 12, so there is "
                     "nothing to carry and the answer is finished as it stands.",
             "math": "4 ft 2 in + 8 ft 3 in = 12 ft 5 in"},
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Example 85.1b as columns — 2 hr 30 min 20 s + 3 hr 40 min 50 s",
        "headers": ["", "hours place", "minutes place", "seconds place"],
        "rows": [
            {"cells": ["first time", "2", "30", "20"]},
            {"cells": ["+ second time", "3", "40", "50"]},
            {"cells": ["add each column straight down", "5", "70", "70"],
             "emphasis": True},
            {"cells": ["70 s is over 60 — carry 1 min, leave 10 s",
                       "5", "70 + 1 = 71", "10"]},
            {"cells": ["71 min is over 60 — carry 1 hr, leave 11 min",
                       "5 + 1 = 6", "11", "10"]},
            {"cells": ["the answer", "6", "11", "10"], "emphasis": True},
        ],
        "note": "Read **down** a column and it is ordinary addition. Read "
                "**across** the bottom row and it is `6 hr 11 min 10 s`. The two "
                "carries are the only difference between this and an ordinary "
                "column sum — and they happen at 60, not at 10. Notice the "
                "carries run right to left: the seconds are fixed before the "
                "minutes are looked at, because fixing the seconds is what puts "
                "the extra minute there.",
    }),

    (B.KIND_WORKED, {
        "number": "85.1b",
        "question": "Add.   2 hr 30 min 20 s  +  3 hr 40 min 50 s",
        "steps": [
            {"label": "Line the three columns up",
             "text": "Hours under hours, minutes under minutes, seconds under "
                     "seconds. Both amounts already have all three columns "
                     "written, so there is nothing to convert first."},
            {"label": "Add each column on its own",
             "text": "Do not think about carrying yet. Just add straight down, "
                     "three separate times. Seconds, then minutes, then hours.",
             "math": "20 + 50 = 70  →  30 + 40 = 70  →  2 + 3 = 5"},
            {"label": "Write the raw sum down and look at it",
             "text": "This is a true statement and a wrong-looking answer. Two "
                     "of the three columns are over their limit. Now you fix "
                     "them, starting from the right.",
             "math": "2 hr 30 min 20 s + 3 hr 40 min 50 s = 5 hr 70 min 70 s"},
            {"label": "Carry out of the seconds place",
             "text": "70 seconds is one whole minute with 10 seconds left over. "
                     "The whole minute moves left into the minutes column, and "
                     "the 10 stays behind.",
             "math": "70 - 60 = 10  →  5 hr 71 min 10 s"},
            {"label": "Carry out of the minutes place",
             "text": "The minutes column now reads 71 — the 70 it already had "
                     "plus the 1 that just arrived. 71 is over 60 as well, so "
                     "one whole hour moves left and 11 minutes stay. Your book "
                     "writes these two carries in one breath — *carry one "
                     "minute, which leaves 10 s; carry one hour, which leaves "
                     "10 min, plus the 1 carried min* — which is this step and "
                     "the one before it, said together. Same 11 minutes either "
                     "way.",
             "math": "71 - 60 = 11  →  6 hr 11 min 10 s"},
            {"label": "Check every column",
             "text": "10 seconds is under 60. 11 minutes is under 60. Nothing "
                     "left to carry, so this is the finished answer.",
             "math": "6 hr 11 min 10 s"},
        ],
        "answer": "6 hr 11 min 10 s",
    }),

    (B.KIND_WORKED, {
        "number": "85.2a",
        "question": "Subtract.   10 ft 3 in  -  6 ft 9 in",
        "steps": [
            {"label": "Try the small column first",
             "text": "Inches under inches: 3 take away 9. You cannot do it with "
                     "what is sitting there. That is the signal to borrow — and "
                     "it is the same signal you have always used in long "
                     "subtraction."},
            {"label": "Borrow one whole foot",
             "text": "Take 1 away from the 10 feet, leaving 9 feet. That one "
                     "foot is worth 12 inches, and it lands in the inches "
                     "column beside the 3 that is already there.",
             "math": "3 + 12 = 15  →  10 - 1 = 9"},
            {"label": "Rewrite the top line",
             "text": "Nothing has been added or lost. `10 ft 3 in` and "
                     "`9 ft 15 in` are the same length, written with the "
                     "columns arranged differently — which is the only reason "
                     "borrowing is allowed at all.",
             "math": "10 ft 3 in = 9 ft 15 in"},
            {"label": "Now subtract each column",
             "text": "Inches first: 15 take away 9. Then feet: 9 take away 6. "
                     "Neither column needs anything from the other any more.",
             "math": "15 - 9 = 6  →  9 - 6 = 3"},
            {"label": "Read it back and check the limit",
             "text": "6 inches is under 12, so the answer is finished. If you "
                     "want the check: add 6 ft 9 in back on and you should get "
                     "10 ft 3 in again.",
             "math": "9 ft 15 in - 6 ft 9 in = 3 ft 6 in"},
        ],
        "answer": "3 ft 6 in",
    }),

    (B.KIND_WORKED, {
        "number": "85.2b",
        "question": "Subtract.   60 hr  -  10 hr 5 min 23 s",
        "steps": [
            {"label": "Give the top line all three columns",
             "text": "`60 hr` has no minutes and no seconds written. A column "
                     "that is not written is a **zero**, not a gap — so the top "
                     "line is `60 hr 0 min 0 s`. Write the zeros in. They are "
                     "what you are about to borrow into.",
             "math": "60 hr 0 min 0 s"},
            {"label": "Try the seconds",
             "text": "0 take away 23. Nothing there to take from. So look one "
                     "column left to borrow — and the minutes column is 0 as "
                     "well. This is the case that catches people: the borrow "
                     "has to start two columns over."},
            {"label": "Borrow one hour into the minutes",
             "text": "Take 1 from the 60 hours, leaving 59 hours. That one hour "
                     "arrives in the minutes column as 60 minutes.",
             "math": "60 - 1 = 59  →  59 hr 60 min 0 s"},
            {"label": "Now borrow one minute into the seconds",
             "text": "Do it again, one column further right. Take 1 from the 60 "
                     "minutes, leaving 59 minutes. That one minute arrives in "
                     "the seconds column as 60 seconds. Now every column has "
                     "something in it.",
             "math": "60 - 1 = 59  →  59 hr 59 min 60 s"},
            {"label": "Subtract each column",
             "text": "Seconds, then minutes, then hours. Straight subtraction "
                     "now — all the hard work was the borrowing.",
             "math": "60 - 23 = 37  →  59 - 5 = 54  →  59 - 10 = 49"},
            {"label": "Check it with addition",
             "text": "Saxon offers this check on the page and it is worth "
                     "taking. Add your answer back onto what you subtracted. "
                     "You land on `59 hr 59 min 60 s` — and 60 seconds is one "
                     "whole minute, which makes the minutes 60, which is one "
                     "whole hour, which makes the hours 60. Right back where "
                     "you started.",
             "math": "49 hr 54 min 37 s + 10 hr 5 min 23 s = 59 hr 59 min 60 s = 60 hr"},
        ],
        "answer": "49 hr 54 min 37 s",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "move",
        "title": "A fraction stacked on a fraction is a division you already know",
        "paragraphs": [
            "New topic, same page. A fraction bar is a division sign wearing "
            "different clothes: `6/3` means 6 divided by 3, and always has.",
            "A **complex fraction** is one where the top, or the bottom, or "
            "both, are themselves fractions. It looks alarming stacked up on "
            "the page. It is not. The bar in the middle still means *divide*.",
            "In Lesson 23 you divided a fraction by a fraction by turning the "
            "bottom one upside down and multiplying instead — **invert and "
            "multiply**. That is still where you land here. But Saxon writes "
            "the move out in full on this page, and it is worth writing it his "
            "way at least a few times, because that is the form every worked "
            "line in your book is written in.",
            "Saxon numbers it as three steps: **1)** multiply above and below "
            "by the reciprocal of the denominator fraction, **2)** cancel "
            "common factors, **3)** simplify to one numerator and one "
            "denominator.",
            "*Above and below* is the part that looks new. Take the bottom "
            "fraction, turn it upside down — that is its **reciprocal** — and "
            "multiply **both floors** by it, the top one and the bottom one. "
            "Multiplying the top and the bottom of a fraction by the same thing "
            "never changes what it is worth, which is why you are allowed to.",
            "Then look at what the bottom floor became: a fraction times its "
            "own reciprocal. `(1/b) · (b/1)` is `b/b`, and `(c/d) · (d/c)` is "
            "`cd/dc`. The letters **cancel** and the bottom floor is left as "
            "**1** — every single time. Anything over 1 is itself, so what is "
            "left standing is the top floor alone: the numerator times the "
            "reciprocal. That is invert-and-multiply, and now you can see where "
            "it came from.",
            "The only new thing in Lesson 85B is letters where the numbers used "
            "to be, and Saxon says so outright: *the simplification process is "
            "identical.* Turning `c/d` upside down gives `d/c` whether c and d "
            "are numbers or letters.",
            "Two small habits make it painless. First: if the bottom is a lone "
            "letter with no fraction bar of its own, write it over 1 — `a` "
            "becomes `a/1` — so there is a fraction on both floors to work "
            "with. Nothing changes, because anything over 1 is itself.",
            "Second: know which bar is the main one. Saxon tells you exactly "
            "what to look for in part b) — the dividing bar is drawn **a little "
            "thicker** than the others. It is a small difference and you have "
            "to go looking for it on purpose, but it is how you tell that `x/y` "
            "is the top fraction and `a` is the bottom one. Saxon also says "
            "parentheses **might** be used in later problems to show the same "
            "thing, and on this page they always are.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "85.3",
        "question": "Simplify the complex fractions.   a) (1/a) divided by (1/b)   "
                    "b) (x/y) divided by a   c) (a/b) divided by (c/d)",
        "steps": [
            {"label": "First — what your book actually shows",
             "text": "Your book prints these as stacked fractions with one main "
                     "bar across the middle, and this page cannot stack them, "
                     "so they are written here with parentheses for each floor "
                     "and `÷` for the main bar. They mean exactly the same "
                     "thing. In a) the top floor is `1/a` and the bottom floor "
                     "is `1/b`; in b) the top floor is `x/y` and the bottom "
                     "floor is the lone letter `a`. Open the book to Example "
                     "85.3 and read the stacked version beside this one — the "
                     "book writes the reciprocal on **both** floors, and so "
                     "does every line below."},
            {"label": "The move you are about to make, once",
             "text": "Multiply the top floor **and** the bottom floor by the "
                     "reciprocal of the bottom fraction. The bottom floor then "
                     "holds a fraction times its own reciprocal, the letters "
                     "cancel, and it finishes as **1**. Anything over 1 is "
                     "itself, so the top floor is the answer. In part a) that "
                     "cancelling is `(1/b) · (b/1)`, which is `b/b`, which is "
                     "1. Watch the same thing happen in all three parts."},
            {"label": "a) multiply above and below by the reciprocal of 1/b",
             "text": "The bottom fraction is `1/b`, so its reciprocal is `b/1`. "
                     "Multiply both floors by `b/1`. On top, `1/a` times `b/1` "
                     "puts the b over the a. Underneath, `1/b` times `b/1` is "
                     "`b/b`, which cancels to 1 — so the whole bottom floor "
                     "disappears and `b/a` is left.",
             "math": "(1/a) ÷ (1/b) = [(1/a) · (b/1)] ÷ [(1/b) · (b/1)] "
                     "= (b/a) ÷ 1 = b/a"},
            {"label": "b) give the lone letter a floor first",
             "text": "The bottom here is a bare `a` with no fraction bar of its "
                     "own. Write it as `a/1`. Nothing has changed — anything "
                     "over 1 is itself — but now there is a fraction on both "
                     "floors, which is what the method needs."},
            {"label": "b) now multiply above and below by the reciprocal of a/1",
             "text": "Turn `a/1` over and it becomes `1/a`. Multiply both "
                     "floors by it. On top, `x/y` times `1/a` puts the a "
                     "underneath beside the y. Underneath, `a/1` times `1/a` is "
                     "`a/a`, which cancels to 1 again.",
             "math": "(x/y) ÷ (a/1) = [(x/y) · (1/a)] ÷ [(a/1) · (1/a)] "
                     "= [x/(ay)] ÷ 1 = x/(ay)"},
            {"label": "c) the general shape",
             "text": "Both floors are already fractions, so there is nothing to "
                     "set up. The reciprocal of `c/d` is `d/c`. Multiply both "
                     "floors by it. On top, `a/b` times `d/c` is `ad/bc` — tops "
                     "together, bottoms together. Underneath, `c/d` times `d/c` "
                     "is `cd/dc`, and that cancels to 1.",
             "math": "(a/b) ÷ (c/d) = [(a/b) · (d/c)] ÷ [(c/d) · (d/c)] "
                     "= (ad/bc) ÷ 1 = ad/bc"},
            {"label": "Why Saxon stops writing the ÷ 1 step",
             "text": "Look back at the three lines. The bottom floor came out "
                     "as 1 every time, so the last thing left is a division by 1 — "
                     "and Saxon says why in as many words: "
                     "*every time we multiply above and below by the reciprocal "
                     "of the denominator, the denominator fraction simplifies "
                     "to 1* — so he skips writing that step and goes straight "
                     "to the answer. Write it out in full until you believe "
                     "him, then stop writing it — the same way he does, and in "
                     "the same order."},
            {"label": "One picture worth keeping for c)",
             "text": "Reading `(a/b) ÷ (c/d)` down the stacked page you meet a, "
                     "b, c, d in that order. The **outer** pair, a and d, "
                     "multiply to make the top of `ad/bc`. The **inner** pair, "
                     "b and c, make the bottom. That picture is not in the "
                     "book — it is only a way of remembering the shape — so "
                     "check it against the full line above the first few times "
                     "you use it."},
        ],
        "answer": "b/a for part a · x/(ay) for part b · ad/bc for part c",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Both halves of this lesson are written in abbreviations that "
                 "hide how ordinary they are. Here is what each one is short "
                 "for.",
        "rows": [
            {"symbol": "8 ft 3 in",
             "plain": "eight whole feet PLUS three inches — two columns, not "
                      "one number",
             "example": "8 ft 3 in"},
            {"symbol": "ft · in",
             "plain": "feet and inches — and one foot is twelve inches",
             "example": "12 in = 1 ft"},
            {"symbol": "hr · min · s",
             "plain": "hours, minutes and seconds — sixty of the small one "
                      "makes one of the next",
             "example": "60 s = 1 min,  60 min = 1 hr"},
            {"symbol": "carry",
             "plain": "a column went over its limit, so one full group moves "
                      "into the column on the left",
             "example": "70 s  →  1 min carried, 10 s left"},
            {"symbol": "borrow",
             "plain": "a column is too small to subtract from, so one unit is "
                      "broken out of the column on the left",
             "example": "1 ft borrowed  →  12 more inches"},
            {"symbol": "60 hr",
             "plain": "a measure with the other columns left unwritten — they "
                      "are zeros, and you write them in",
             "example": "60 hr  =  60 hr 0 min 0 s"},
            {"symbol": "the main fraction bar",
             "plain": "divide. In the book the MAIN bar is drawn a little "
                      "thicker than the others; here it is the parentheses that "
                      "tell you",
             "example": "(x/y) ÷ a"},
            {"symbol": "reciprocal",
             "plain": "the fraction turned upside down",
             "example": "c/d  →  d/c"},
            {"symbol": "invert and multiply",
             "plain": "flip the bottom fraction over, then multiply instead of "
                      "dividing",
             "example": "(a/b) ÷ (c/d) = (a/b) · (d/c)"},
            {"symbol": "complex fraction",
             "plain": "a fraction with a fraction in its top, its bottom, or "
                      "both",
             "example": "(1/a) ÷ (1/b)"},
        ],
        "after": "`ft`, `in`, `hr`, `min` and `s` are only abbreviations, and "
                 "the middle bar of a complex fraction is only a division sign. "
                 "Neither half of Lesson 85 has a new rule in it — which is why "
                 "the book's own first page says **No New Rules or "
                 "Definitions**.",
    }),

    (B.KIND_ERRORS, {
        "title": "Seven ways this goes wrong — five in the measures, two in the fractions",
        "items": [
            {"name": "Converting, but not far enough — leaving the small column over its limit.",
             "wrong": "50 in = 3 ft 14 in  →  3 ft 14 in + 8 ft 3 in = 11 ft 17 in",
             "right": "50 in = 4 ft 2 in  →  4 ft 2 in + 8 ft 3 in = 12 ft 5 in",
             "note": "`3 ft 14 in` really **is** 50 inches, so nothing feels "
                     "wrong on the way past — and that is why Saxon prints the "
                     "whole list on purpose: three near-misses and the finished "
                     "one, stacked together. 1 ft 38 in, 2 ft 26 in and "
                     "3 ft 14 in are all 50 inches and all unfinished; "
                     "`4 ft 2 in` is the one with nothing left to move. Keep "
                     "pulling feet out until the inches are **under 12**."},
            {"name": "Adding the columns and stopping there.",
             "wrong": "2 hr 30 min 20 s + 3 hr 40 min 50 s = 5 hr 70 min 70 s",
             "right": "2 hr 30 min 20 s + 3 hr 40 min 50 s = 6 hr 11 min 10 s",
             "note": "`5 hr 70 min 70 s` is a true amount of time and a wrong "
                     "answer, which is a horrible combination. A column over "
                     "its limit means the job is half done. The raw sum is a "
                     "**working line**, never the last line."},
            {"name": "Carrying ten, because that is what every column you have ever added does.",
             "wrong": "70 s  →  carry 1, leave 60  →  5 hr 71 min 60 s",
             "right": "70 - 60 = 10  →  5 hr 71 min 10 s",
             "note": "The thing you are carrying is one whole **minute**, and a "
                     "minute is 60 seconds — so 60 leaves and 10 stays. The tell "
                     "is that the seconds column still reads 60 afterwards, "
                     "which is still not under its limit. If a carry does not "
                     "fix the column, it was the wrong size of carry."},
            {"name": "Borrowing ten inches instead of twelve.",
             "wrong": "10 ft 3 in  →  9 ft 13 in  →  13 - 9 = 4  →  3 ft 4 in",
             "right": "3 + 12 = 15  →  15 - 9 = 6  →  3 ft 6 in",
             "note": "One foot is **12** inches, not 10, so a borrowed foot puts "
                     "12 into the inches column. This one is nasty because the "
                     "answer comes out exactly 2 inches short and still looks "
                     "perfectly reasonable. Say the rate out loud as you "
                     "borrow: *one foot, twelve inches.*"},
            {"name": "Turning a column around to avoid borrowing.",
             "wrong": "10 ft 3 in - 6 ft 9 in = 4 ft 6 in",
             "right": "10 ft 3 in = 9 ft 15 in  →  9 ft 15 in - 6 ft 9 in = 3 ft 6 in",
             "note": "3 take away 9 is not 6. Doing `9 - 3` instead — because "
                     "that is the subtraction that *works* — is the oldest error "
                     "in long subtraction and it walks straight into this lesson "
                     "unchanged. When the top number is smaller, you **borrow**. "
                     "You do not swap."},
            {"name": "Flipping the top fraction instead of the bottom one.",
             "wrong": "(a/b) ÷ (c/d) = (b/a) · (c/d) = bc/ad",
             "right": "(a/b) ÷ (c/d) = (a/b) · (d/c) = ad/bc",
             "note": "**The bottom one flips.** Always the one you are dividing "
                     "**by**. This slips through because the wrong answer is not "
                     "nonsense-looking — `bc/ad` is the right answer upside "
                     "down, so it has all the correct letters in it."},
            {"name": "Multiplying by the lone letter instead of dividing by it.",
             "wrong": "(x/y) ÷ a = (x/y) · a = ax/y",
             "right": "(x/y) ÷ (a/1) = (x/y) · (1/a) = x/(ay)",
             "note": "Write the lone `a` as `a/1` **before** you do anything "
                     "else. Once it is a fraction, flipping it is obvious: "
                     "`a/1` becomes `1/a`, and the a lands **underneath**. The "
                     "wrong version puts it on top, which is the opposite of "
                     "dividing by it."},
        ],
    }),

    (B.KIND_REVEAL, {
        "prompt": "The first two of Practice Set 85 — try them on paper before "
                  "you look: 100 in + 10 ft 10 in, and 20 ft 5 in − 10 ft 11 in.",
        "answer": "**The first one comes to 19 ft 2 in.** Sort the pile first: "
                  "twelve goes into 100 eight times with 4 left over, so "
                  "`100 in` is `8 ft 4 in` — and 4 is under 12, so that "
                  "conversion is finished. Now stack and add each column: 4 and "
                  "10 make 14 inches, 8 and 10 make 18 feet, so the raw sum is "
                  "`18 ft 14 in`. But 14 is over 12, so carry one foot and "
                  "leave 2 inches behind. That gives `19 ft 2 in`.\n\n"
                  "**The second one comes to 9 ft 6 in.** You cannot take 11 "
                  "from 5, so borrow a foot: `20 ft 5 in` becomes "
                  "`19 ft 17 in`. Then the inches column is 17 take away 11, "
                  "which is 6, and the feet column is 19 take away 10, which is "
                  "9. Check it by adding back: `9 ft 6 in` plus `10 ft 11 in` "
                  "is `19 ft 17 in`, and that is `20 ft 5 in` again.\n\n"
                  "If you got `18 ft 14 in` on the first one, you did all the "
                  "arithmetic right and stopped one move early. That is an easy "
                  "way to miss this lesson, and it is worth noticing rather "
                  "than rubbing out.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A mixed measure is a **number written in columns** — feet and "
            "inches, or hours and minutes and seconds. Add and subtract one "
            "column at a time, exactly like ordinary long addition.",
            "Each column fills up at its **own** number: seconds and minutes at "
            "**60**, inches at **12**. Ordinary digits fill up at 10, and that "
            "is the only difference between this and ordinary column "
            "arithmetic.",
            "**Convert before you line anything up.** `50 in` has to become "
            "`4 ft 2 in` first — and you are not finished converting until the "
            "small column is under its limit. `3 ft 14 in` is true and "
            "unfinished.",
            "**Carry** left when a column goes over. **Borrow** right when a "
            "column is too small to subtract from — one foot borrowed is 12 "
            "inches, one hour borrowed is 60 minutes.",
            "A column that is not written is a **zero**. `60 hr` is "
            "`60 hr 0 min 0 s`, and sometimes you have to borrow across two "
            "columns to fill them.",
            "Check a subtraction by **adding your answer back on**. You should "
            "land exactly on the number you started with.",
            "A **complex fraction** is a fraction with fractions inside it. The "
            "middle bar still means divide, so **invert and multiply** — that "
            "is Lesson 23, with letters.",
            "Saxon's written form is three steps: multiply **above and below** "
            "by the reciprocal of the bottom fraction, **cancel**, and simplify "
            "to one numerator and one denominator. The bottom floor cancels to "
            "**1** every time, which is why he stops writing it — and why the "
            "short version is the same thing.",
            "If the top or bottom is a lone letter, write it over **1** first, "
            "so there is a fraction on both floors.",
            "`(a/b) ÷ (c/d) = ad/bc` — the **outer** pair multiply to make the "
            "top, the **inner** pair make the bottom.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 85 first. If it didn't quite land, this is here to fix "
    "that. Two separate things happen in this lesson and neither one is new. "
    "First: adding and subtracting times and lengths by treating the units as "
    "columns — an hours column, a minutes column, a seconds column — and "
    "carrying between them. Second: simplifying a fraction that has fractions "
    "inside it, which is Lesson 23's invert-and-multiply with letters in it."
)

PARENT_CONTENT = """## The big idea

Two topics share this page and they are unrelated, so teach them as two
conversations, not one.

**85A — mixed measures.** Saxon states the whole trick in one sentence: *think of
the different measures as place values.* `2 hr 30 min 20 s` is not one number; it
is three columns, exactly like the hundreds, tens and ones in 342. You add each
column on its own and then fix any column that went over. She already does this.
The only thing that changes is the number a column fills up at — 60 for seconds
and minutes, 12 for inches, instead of 10.

The genuinely hard bit is not the carrying. It is the **conversion before the
carrying**, and Saxon builds Example 85.1a around it. To add `50 in + 8 ft 3 in`
she has to turn 50 inches into feet and inches first, and there are four ways to
do it that are all arithmetically true:

> 1 ft 38 in · 2 ft 26 in · 3 ft 14 in · 4 ft 2 in

All four equal 50 inches. Only `4 ft 2 in` is *properly converted*, because it is
the only one whose inches place is under 12. Give her the test in that form —
**is the small column under its limit?** — because it is the same test that tells
her when a carry is finished, and it is the one habit that covers the whole of
85A.

**85B — complex fractions.** A fraction whose top or bottom is itself a fraction.
The middle bar still means divide, so the answer is Lesson 23's *invert and
multiply* with letters instead of numbers. The book says so in as many words:
"the simplification process is identical."

**Write it the book's way at least once.** Saxon does not print the short
version. He prints three steps — *1) multiply above and below by the reciprocal
of the denominator fraction, 2) cancel common factors, 3) simplify to one
numerator and one denominator* — and every worked line on his page shows the
reciprocal written on **both** floors:

> (a/b) ÷ (c/d) = [(a/b) · (d/c)] ÷ [(c/d) · (d/c)] = (ad/bc) ÷ 1 = ad/bc

The bottom floor is a fraction times its own reciprocal, so it cancels to 1
every time — which is precisely why the shortcut is legitimate, and Saxon says
so at part c) before he starts skipping the step. This matters practically:
every worked line in Example 85.3 is written the long way, and problems 385 and
485 are more complex fractions of the same kind. If she has only ever seen
`(a/b) · (d/c)`, the book's own lines will not look like her method. Her page
now works all three parts in full. The one new habit on top of that is
writing a lone letter over 1 (`a` becomes `a/1`) so there is a fraction on both
floors.

Her page also gives her an *outer pair / inner pair* picture for `ad/bc`. That is
a memory hook, not Saxon's wording, and the page says so — if she quotes it back
to you, that is where it came from.

**About the figures.** Example 85.3 is printed as stacked fractions, and practice
problems 385 and 485 are figures. None of those can be reproduced on her page, so
85.3 is rewritten there using parentheses for each floor and `÷` for the main
bar, and her page says so and tells her to open the book beside it. Have the book
open — Saxon's tell for which bar is the main one is that it is drawn *a little
thicker* than the others (his words, at part b), and that is a real reading skill
she can only get from the printed page. It is a small difference; point at it
once for her rather than assuming she will spot it. In later problems he says
parentheses *might* be used instead.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Write `3 hr 45 min` on paper. Ask: **"How many numbers is that?"** Most
   children say one. Say: *"It's two. It's a hours column and a minutes column,
   the same way 34 is a tens column and a ones column."* Draw the two column
   lines around it. That picture is the lesson.
2. Write `342` beside it and ask: **"Ten ones make one what?"** — you want "one
   ten." Then point at the minutes: **"Sixty minutes make one what?"** Same
   answer shape, different number. Say it plainly: *"Same method. Different
   rate."*
3. Now do `2 hr 30 min 20 s + 3 hr 40 min 50 s` in columns, and ask her to add
   each column **without carrying anything**. She will get `5 hr 70 min 70 s`.
   Ask: **"Is that finished?"** Let her find the answer herself — you want her
   to say the seconds column is over 60.
4. Fix the seconds first, then the minutes, and ask at each one: **"How many
   whole minutes are in 70 seconds, and what's left over?"** One and ten. The
   one goes left, the ten stays. Then the same question again for the minutes
   column, which now reads 71 — point out that the extra 1 came from the carry
   she just did, which is why you always work right to left.
5. For 85A's other half, write `10 ft 3 in - 6 ft 9 in` and ask the only
   question that matters: **"Can you take 9 from 3?"** No. **"So what do we
   borrow, and how much does it turn into?"** One foot, twelve inches. Have her
   say "twelve" out loud — that is the number she will get wrong if she gets
   anything wrong.

For 85B, three minutes is enough on a separate occasion. Write `(1/2) ÷ (1/4)`
with *numbers* and let her do it the Lesson 23 way. Then write the identical
problem with letters — `(1/a) ÷ (1/b)` — and ask: **"What changed?"** Nothing
changed. That is the entire second half of the lesson.

## The classic mix-ups, with the exact wrong answer each one produces

- **Converting, but not far enough.** She turns 50 in into `3 ft 14 in`, adds
  `8 ft 3 in`, and gets **11 ft 17 in** instead of **12 ft 5 in**. Nothing feels
  wrong, because 3 ft 14 in genuinely is 50 inches. Fix: the small column must
  end **under 12**.
- **Stopping at the raw sum.** She writes **5 hr 70 min 70 s** instead of
  **6 hr 11 min 10 s**. Fix: a column over its limit means the job is half done.
  The raw sum is a working line, never the last line.
- **Carrying ten instead of sixty.** From 70 seconds she carries 1 and leaves 60,
  giving **5 hr 71 min 60 s**. The tell is that the seconds column is *still* over
  its limit. Fix: if a carry does not fix the column, it was the wrong size.
- **Borrowing ten inches instead of twelve.** `10 ft 3 in - 6 ft 9 in` comes out
  **3 ft 4 in** instead of **3 ft 6 in** — exactly 2 inches short, and it looks
  entirely plausible. Fix: say "one foot, twelve inches" out loud while
  borrowing.
- **Turning a column around to dodge the borrow.** She does `9 - 3` instead of
  `3 - 9` and writes **4 ft 6 in** instead of **3 ft 6 in**. This is the oldest
  error in long subtraction and it arrives here intact.
- **Flipping the top fraction.** `(a/b) ÷ (c/d)` comes out **bc/ad** instead of
  **ad/bc** — the right answer upside down, with every correct letter in it,
  which is why it survives a glance. Fix: the one you divide **by** is the one
  that flips.
- **Multiplying by the lone letter.** `(x/y) ÷ a` comes out **ax/y** instead of
  **x/(ay)**. Fix: write `a` as `a/1` before doing anything, and the flip becomes
  obvious.

## What to watch her do

Watch her **hands**, in this order.

1. Does she draw the columns — actual vertical lines, or at least the numbers
   stacked in line — before she adds anything? A mixed measure written out
   sideways on one line is where every carry error in this lesson is born.
2. On `50 in`, does she **stop and convert before adding**, or does she start
   adding and convert at the end? Both can reach the right answer on 85.1a, but
   only the first survives 85.2b. Converting first is the habit; converting last
   is a coincidence.
3. When she carries, does her pencil actually **write the small leftover back
   into the column**, or does she hold it in her head? Held-in-head carries are
   where 70 seconds silently becomes 10 seconds and the minute never arrives.
4. On the subtraction, does she **rewrite the whole top line** after borrowing
   (`10 ft 3 in` → `9 ft 15 in`), or does she scribble a little 1 above and try
   to keep track? Rewriting the line is what makes 85.2b's double borrow
   possible at all.
5. On 85.2b specifically, watch whether she borrows **twice**. Borrowing an hour
   into minutes and then a minute into seconds is two separate moves. Watching
   her do only one is the fastest diagnosis available in this lesson.
6. On the complex fractions, does the pencil write `a/1` under the bar before
   anything else? If she goes straight to flipping, she will flip the wrong
   thing sooner or later.
7. The first few times, does she write the reciprocal on **both** floors and
   watch the bottom one cancel to 1 — or does she jump to the short version?
   Both reach the same answer, but only the long one matches the lines printed
   in Example 85.3, and only the long one tells you whether she knows *why* the
   bottom fraction flips.

A right answer on 85.1a is not evidence of anything — the numbers are small
enough to do in her head. The five habits above are what survive 85.2b.

## Extend it

- Give her `4 ft 11 in + 3 ft 7 in` and let a carry happen where she is not
  expecting one. Then `5 lb 12 oz + 2 lb 9 oz` and simply tell her that 16 ounces
  make a pound. She has to apply the method at a rate nobody taught her, which
  is the real test of whether she understood it or memorised sixty.
- Ask her to add three times together instead of two — three lap times, say. A
  column can then go over 120, which means carrying **2**, not 1. That is the
  question that shows whether "carry one" was a rule or an understanding.
- Time something real. Two videos, two chores, two drives — add the durations
  with a stopwatch, then subtract to find the difference. Mixed measures are one
  of the few pre-algebra topics with a genuinely everyday use, and it is worth
  spending it.
- For 85B, give her `((1/2)/(3/4))` in numbers, have her simplify it, and then
  ask her to check on a calculator. Getting `2/3` twice from two different
  methods is very convincing.

## Where this sits

DIVE Lecture 85, "Addition and Subtraction with Mixed Measures; Simplifying
Complex Fractions." Its page 1 lists the reviews: **Lesson 25** (equivalent
measures — 12 in = 1 ft, 60 s = 1 min, 60 min = 1 hr) and **Lesson 23** (dividing
fractions by fractions, invert and multiply). Page 1 also says **"No New Rules or
Definitions,"** which is true of both halves and worth saying to her before she
starts.

If she is lost in 85A, go back to **Lesson 25** and re-do the equivalent measures
on their own, with no adding at all. If she is lost in 85B, go back to
**Lesson 23** and do four complex fractions with numbers instead of letters until
the method is boring; then swap the numbers for letters in front of her.

**Proficient** looks like: adds two mixed measures with a single carry, and
subtracts with a single borrow, correctly and unhurried; simplifies `(a/b) ÷
(c/d)`.
**Mastered** looks like: converts `50 in` to `4 ft 2 in` without prompting,
handles 85.2b's double borrow across two empty columns, and writes a lone letter
over 1 before flipping it — without being told to.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 85 (mixed measures; complex "
            "fractions) — idempotent.")

    LESSON_NUMBER = 85
    TITLE = ("Measures in Columns — Adding and Subtracting Mixed Measures; "
             "Simplifying Complex Fractions")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
