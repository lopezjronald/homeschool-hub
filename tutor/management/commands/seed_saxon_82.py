"""Saxon Pre-Algebra Lesson 82 — Two Step Equations, Inequalities.

Reviews Lessons 26, 39, 41 and 70. Lesson 39 is the hook and the book says so
itself: Step 1 IS the additive property of equality and Step 2 IS the
multiplicative property, both taught in 39, and she has been solving two step
equations since Ex. 39.5c. The book's own first page says "No New Rules or
Definitions." The only thing that changed is that the numbers are now fractions
and decimals — so the whole difficulty of this lesson is arithmetic hiding
inside a method she already owns. Part B adds an inequality symbol and nothing
else; the two steps are untouched.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. In the PDF the equation lines of Ex. 82.1a, 82.1b and 82.2b are
typeset images rather than text, so they are not quotable directly — but the
solution narration prints every intermediate number ("1/4 = 2/8, and 2/8-5/8 =
-3/8", "Multiply both sides by 4/1", "-12/8 reduces to -3/2"), which pins each
starting equation to exactly one possibility. They are reconstructed here from
that arithmetic and every reconstruction is checked by substituting the answer
back in, which the worked examples below do on the page.

    python manage.py seed_saxon_82 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 82 · Pre-Algebra",
        "title": "Two steps, in that order — equations and inequalities",
        "thesis": "Nothing in this lesson is new. Step 1 is the **additive property "
                  "of equality** and Step 2 is the **multiplicative property**, and "
                  "you learned both in Lesson 39. The only thing that changed is "
                  "that the numbers are now fractions and decimals.",
        "formula": "ax + b = c",
        "roles": [
            {"tone": "start", "name": "Step 1 — undo the add",
             "text": "Add the opposite of the loose number to both sides. The loose "
                     "number is the one that is not touching the letter."},
            {"tone": "move", "name": "Step 2 — undo the multiply",
             "text": "Multiply both sides by the reciprocal of the number stuck to "
                     "the letter — or divide both sides by that number. Same move, "
                     "two names."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody bothers doing it in two steps",
        "paragraphs": [
            "Put your socks on, then your shoes. Now take them off. You do not "
            "start with the socks — you cannot. The shoes went on last, so they "
            "come off first.",
            "An equation is built the same way. In `3x - 5`, somebody took an x, "
            "multiplied it by 3, and **then** took 5 away. The subtraction went on "
            "last. So it comes off first.",
            "That is the entire reason this is a *two step* method and not a "
            "one step one, and it is the reason the two steps are in the order they "
            "are in. You are unwrapping, and you unwrap from the outside.",
            "Here is the part the book puts on its own first page, and it is worth "
            "believing: **no new rules and no new definitions.** You have been "
            "doing this since Ex. 39.5c, and Ex. 41.2 was full of them. The book's "
            "only warning about today is this one sentence: *the only difference "
            "here is these will involve more fractions and decimals.*",
            "So if this lesson feels hard, notice **where** it feels hard. It will "
            "not be the two steps. It will be the fraction arithmetic sitting "
            "underneath them — and that is a different problem, with a different "
            "fix.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Step 1 takes the loose number off. Step 2 takes the multiplier off.",
        "paragraphs": [
            "Look at `-6.25k + 1.2 = 8.7` and find the number that is **not** "
            "touching the letter. It is the `+ 1.2`. That one is loose, so it is "
            "the outer layer, so it goes first.",
            "**Step 1** is the additive property of equality: you may add the same "
            "thing to both sides and the equation stays true. Add `-1.2` to both "
            "sides and the `+ 1.2` cancels itself out.",
            "Now only one thing is left attached to the letter: the `-6.25` it is "
            "multiplied by. **Step 2** is the multiplicative property of equality: "
            "you may multiply both sides by the same thing. Divide both sides by "
            "`-6.25`, and the letter is finally alone.",
            "Both properties are from **Lesson 39**. If either sentence above felt "
            "like a rule you have never met, go back to 39 rather than pushing "
            "through this page — everything here rests on those two.",
            "One thing that is not optional: whatever you do, you do it to **both "
            "sides**. An equation is a statement that two things are the same "
            "size. Change one side only and you have just made it a lie.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Socks on, then shoes. To take them off you go backwards — shoes "
                "first. Same here. Look at your equation and find the number that "
                "isn't touching the letter. That one went on last, so it comes off "
                "first, and that's Step 1. Whatever's still stuck to the letter "
                "after that, you undo in Step 2. Two steps, always that order, and "
                "always to both sides.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "The only new thing is that the numbers got ugly",
        "paragraphs": [
            "The method has not changed since Lesson 39. What changed is that `5` "
            "became `5/8` and `12` became `-6.25`, and suddenly a problem you can "
            "do stops feeling like a problem you can do.",
            "Saxon says something genuinely useful about this, and it is worth "
            "reading twice: **show work on these steps, but you do not need to show "
            "work on reducing fractions, adding fractions with different "
            "denominators, etc. Try to use mental math for those steps.**",
            "That is not the book being casual. It is the book protecting the two "
            "steps. If you write out every common-denominator conversion, your page "
            "fills with arithmetic and the two moves that actually solve the "
            "equation disappear into the middle of it. Then you cannot check your "
            "own work, because you cannot find it.",
            "So on your paper there are two kinds of thing. The **two steps** get "
            "written down. The **tidying** — turning `1/4` into `2/8`, reducing "
            "`-12/8` to `-3/2`, turning `1 3/5` into `8/5` — happens in your head "
            "and lands on the page already finished.",
            "When a problem has fractions *and* decimals in it, the book hands the "
            "choice to you: *you decide whether to convert the fractions to decimals "
            "first. Do whatever is easier for you to think about.* In Ex. 82.2b it "
            "turns `1/2` into `0.5`, because everything else in that problem was "
            "already a decimal.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Two steps — and the three moves that surround them",
        "steps": [
            {"label": "Tidy before you touch either side.",
             "detail": "Mixed numbers become improper fractions **first** — `1 3/5` "
                       "becomes `8/5`, `2 1/3` becomes `7/3`. If fractions and "
                       "decimals are both in the problem, pick one and convert. This "
                       "happens before Step 1, because Step 1 assumes the numbers "
                       "are already in a shape you can work with."},
            {"label": "Find the number that is NOT touching the letter.",
             "detail": "That is the loose one, the outer layer, the one that came "
                       "last. Point at it before you write anything."},
            {"label": "Step 1 — add its opposite to both sides.",
             "detail": "The additive property of equality. Write the change **in "
                       "line**, out to the right of the equation, the way the book "
                       "does — it saves a whole page over a term.",
             "math": "-6.25k + 1.2 - 1.2 = 8.7 - 1.2"},
            {"label": "Step 2 — undo the multiply.",
             "detail": "Multiply both sides by the **reciprocal** of the number "
                       "stuck to the letter, or divide both sides by that number. "
                       "Those are the same move; use whichever is easier to think "
                       "about with the numbers you have.",
             "math": "(4/1)(1/4x) = (4/1)(-3/8)"},
            {"label": "Tidy in your head, then put the answer back in.",
             "detail": "Reducing, common denominators, improper fractions — none of "
                       "that gets written out. Then substitute your answer into the "
                       "**original** equation. If both sides come out the same "
                       "number, you are done and you know it."},
        ],
        "after": "Only two of these five are *the* two steps — moves 3 and 4. The "
                 "other three are looking and tidying, and Saxon names the lesson "
                 "after the two that do the solving: **two step equations**.\n\n"
                 "For an inequality nothing on this list changes. The only thing "
                 "that changes is that you copy down `≤` or `>` instead of `=` all "
                 "the way through — and then you draw a number line, because the "
                 "answer is a whole range and a range does not fit on a blank.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 82.1a — the fraction one, one beat at a time",
        "equation": "1/4x + 5/8 = 1/4      (write the answer as an improper fraction)",
        "steps": [
            {"label": "Look first",
             "text": "Two numbers are hanging off the x. The `+ 5/8` is **loose** — "
                     "it is not touching the x. The `1/4` **is** touching it; "
                     "`1/4x` means one quarter *times* x. So the 5/8 comes off "
                     "first. Decide that before you write anything."},
            {"label": "Step 1 · add -5/8 to both sides",
             "text": "The book writes this **in line** — out to the right of the "
                     "equation rather than underneath it — to save space. Do it to "
                     "both sides or it stops being true.",
             "math": "1/4x + 5/8 - 5/8 = 1/4 - 5/8"},
            {"label": "The side trip, in your head",
             "text": "The right side is `1/4 - 5/8` and those denominators do not "
                     "match. Quarters are eighths in disguise: `1/4` is `2/8`. Now "
                     "they match. This is exactly the arithmetic Saxon says **not** "
                     "to write out — it happens in your head and lands on the page "
                     "already finished.",
             "math": "1/4 = 2/8  →  2/8 - 5/8 = -3/8"},
            {"label": "Where you are now",
             "text": "The left side is bare: the `+ 5/8` and the `- 5/8` cancelled. "
                     "One thing is still attached to the x, and it is the `1/4`.",
             "math": "1/4x = -3/8"},
            {"label": "Step 2 · multiply both sides by 4/1",
             "text": "`4/1` is `1/4` flipped over — its **reciprocal**. Multiplying "
                     "a fraction by its own reciprocal always gives 1, which is what "
                     "peels it off the x. Again: both sides.",
             "math": "(4/1)(1/4x) = (4/1)(-3/8)"},
            {"label": "Read the answer",
             "text": "The right side comes out `-12/8`. The question asked for an "
                     "**improper fraction**, so you do not turn it into a mixed "
                     "number — you just reduce it. Twelve and eight both divide by "
                     "four.",
             "math": "x = -12/8 = -3/2"},
            {"label": "Check it, because you can",
             "text": "Put `-3/2` back into the equation you started with. If both "
                     "sides come out the same number, the answer is right and you "
                     "do not have to wonder.",
             "math": "(1/4)(-3/2) + 5/8 = -3/8 + 5/8 = 2/8 = 1/4"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "82.1b",
        "question": "Solve  -2 1/3 x + 1 3/5 = 1/10",
        "steps": [
            {"label": "Tidy first — mixed numbers out",
             "text": "The book's first instruction on this one is to convert the "
                     "mixed numbers **before** you start. A mixed number is a whole "
                     "plus a fraction, so multiply the whole by the bottom and add "
                     "the top.",
             "math": "1 3/5 = 8/5  →  2 1/3 = 2 + 1/3 = 7/3"},
            {"label": "So the equation you are actually solving is",
             "text": "`-7/3x + 8/5 = 1/10`. Nothing has been solved yet — it is the "
                     "same equation wearing a shape you can work with."},
            {"label": "Step 1 · add -8/5 to both sides",
             "text": "`8/5` is the loose number, so it comes off first. In line, to "
                     "the right, both sides.",
             "math": "-7/3x + 8/5 - 8/5 = 1/10 - 8/5"},
            {"label": "The side trip, in your head",
             "text": "Fifths are tenths in disguise: `8/5` is `16/10`. Now the "
                     "denominators match and the subtraction is easy.",
             "math": "8/5 = 16/10  →  1/10 - 16/10 = -15/10"},
            {"label": "Where you are now",
             "text": "The left side is bare: the `+ 8/5` and the `- 8/5` cancelled. "
                     "One thing is still attached to the x, and it is the `-7/3`.",
             "math": "-7/3x = -15/10"},
            {"label": "Get rid of the minus signs, then reduce",
             "text": "Both sides are negative, so multiply both sides by `-1` "
                     "mentally and both minus signs vanish at once. Then reduce "
                     "`15/10` to `3/2` — both divide by 5. That is the order the book "
                     "does it in, and it does both of them in its head. Neither one "
                     "is one of the two steps — this is housekeeping, and it makes "
                     "Step 2 much less error-prone.",
             "math": "7/3x = 15/10 = 3/2"},
            {"label": "Step 2 · multiply both sides by 3/7",
             "text": "`3/7` is `7/3` flipped over. Multiply both sides by it.",
             "math": "(3/7)(7/3x) = (3/7)(3/2)"},
            {"label": "Read the answer",
             "text": "Multiply the tops, multiply the bottoms: 3 times 3 is 9, 7 "
                     "times 2 is 14. Nothing divides into both 9 and 14, so it will "
                     "not reduce. Notice that `9/14` is a **proper** fraction — the "
                     "top is lighter than the bottom — and that is fine. Only 82.1a "
                     "was told to answer with an improper fraction; this one was not, "
                     "and `9/14` could not be written as one anyway.",
             "math": "(3/7)(3/2) = 9/14  →  x = 9/14"},
            {"label": "Check it",
             "text": "Back into the original. `-7/3` times `9/14` is `-63/42`, which "
                     "is `-3/2`. Then add the `8/5` you took off, in tenths.",
             "math": "(-7/3)(9/14) + 8/5 = -3/2 + 8/5 = -15/10 + 16/10 = 1/10  →  "
                     "x = 9/14 is right"},
        ],
        "answer": "x = 9/14",
    }),

    (B.KIND_TABLE, {
        "caption": "Every tidy-up in this lesson — and none of it is work you write down",
        "headers": ["the tidy-up", "how it goes in your head", "where it turns up"],
        "rows": [
            {"cells": ["1 3/5  →  improper", "5 × 1 + 3 = 8, so 8/5",
                       "Ex. 82.1b, before Step 1"], "emphasis": True},
            {"cells": ["2 1/3  →  improper", "3 × 2 + 1 = 7, so 7/3",
                       "Ex. 82.1b, before Step 1"], "emphasis": True},
            {"cells": ["1/4 − 5/8", "1/4 is 2/8, and 2/8 − 5/8 = −3/8",
                       "Ex. 82.1a, Step 1"]},
            {"cells": ["1/10 − 8/5", "8/5 is 16/10, and 1/10 − 16/10 = −15/10",
                       "Ex. 82.1b, Step 1"]},
            {"cells": ["−12/8", "both divide by 4, so −3/2", "Ex. 82.1a, Step 2"]},
            {"cells": ["−15/10", "×(−1) first to clear the minus signs, then both "
                       "divide by 5, so 3/2", "Ex. 82.1b, after Step 1"]},
            {"cells": ["1/2, with decimals all around it", "1/2 is 0.5",
                       "Ex. 82.2b, Step 1"]},
        ],
        "note": "Saxon's instruction, in the book's own words: *show work on these "
                "steps, but you do not need to show work on reducing fractions, "
                "adding fractions with different denominators, etc.* The two shaded "
                "rows happen **before** Step 1 even starts.",
    }),

    (B.KIND_WORKED, {
        "number": "82.2a",
        "question": "(C) Solve  -6.25k + 1.2 = 8.7",
        "steps": [
            {"label": "Look first",
             "text": "Same shape as 82.1a, different numbers. The `+ 1.2` is loose. "
                     "The `-6.25` is stuck to the k. So: 1.2 first, then -6.25. "
                     "The `(C)` means a calculator is allowed here — allowed, not "
                     "required."},
            {"label": "Step 1 · add -1.2 to both sides",
             "text": "In line, to the right, both sides. Notice you **subtract** the "
                     "1.2 from the right side — adding its opposite is what makes it "
                     "disappear from the left.",
             "math": "-6.25k + 1.2 - 1.2 = 8.7 - 1.2  →  8.7 - 1.2 = 7.5  →  "
                     "-6.25k = 7.5"},
            {"label": "Step 2 · divide both sides by -6.25",
             "text": "Here dividing is easier to think about than multiplying by the "
                     "reciprocal, so divide. Divide by the **whole** number that is "
                     "stuck to the k, minus sign included. A positive divided by a "
                     "negative comes out negative.",
             "math": "-6.25k ÷ (-6.25) = 7.5 ÷ (-6.25)  →  7.5 ÷ (-6.25) = -1.2  →  "
                     "k = -1.2"},
            {"label": "Check it",
             "text": "Put `-1.2` back into the equation you started with. Negative "
                     "times negative is positive, so `-6.25` times `-1.2` is `7.5`, "
                     "and 7.5 plus 1.2 is 8.7. That is the right side, so it is "
                     "right.",
             "math": "(-6.25)(-1.2) + 1.2 = 7.5 + 1.2 = 8.7  →  k = -1.2 is right"},
        ],
        "answer": "k = -1.2",
    }),

    (B.KIND_WORKED, {
        "number": "82.2b",
        "question": "(C) Solve  1/2 n - 50 = 6.2",
        "steps": [
            {"label": "Pick a lane first",
             "text": "This one has a fraction and two decimals in it. The book lets "
                     "you choose which to convert, and here the choice is obvious: "
                     "one fraction against two decimals, so turn the fraction into a "
                     "decimal and everything is in the same language.",
             "math": "1/2 = 0.5"},
            {"label": "Step 1 · add 50 to both sides",
             "text": "The loose number is `- 50`, so its opposite is `+ 50`. "
                     "Adding 50 to both sides is what makes it vanish from the left.",
             "math": "0.5n - 50 + 50 = 6.2 + 50  →  6.2 + 50 = 56.2  →  0.5n = 56.2"},
            {"label": "Step 2 · multiply both sides by 2",
             "text": "The reciprocal of 0.5 is 2, so multiply both sides by 2 — which "
                     "is the same thing as dividing both sides by 0.5, exactly as the "
                     "book says. Multiplying by 2 is easier to do in your head, so do "
                     "that one.",
             "math": "(2)(0.5n) = (2)(56.2)  →  (2)(56.2) = 112.4  →  n = 112.4"},
            {"label": "Check it",
             "text": "Half of 112.4 is 56.2, and 56.2 take away 50 is 6.2. That is "
                     "the right side of the original equation, so the answer holds.",
             "math": "(0.5)(112.4) - 50 = 56.2 - 50 = 6.2  →  n = 112.4 is right"},
        ],
        "answer": "n = 112.4",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Most of what makes this page look hard is naming, not "
                 "mathematics. Here is what each piece of the book's shorthand is "
                 "short for.",
        "rows": [
            {"symbol": "additive property of equality",
             "plain": "you may add the same thing to both sides and it stays true — "
                      "this is Step 1, and it is from Lesson 39",
             "example": "add -5/8 to both sides"},
            {"symbol": "multiplicative property of equality",
             "plain": "you may multiply both sides by the same thing and it stays "
                      "true — this is Step 2, also from Lesson 39",
             "example": "multiply both sides by 4/1"},
            {"symbol": "1/4x",
             "plain": "one quarter TIMES x. The fraction is glued to the x by "
                      "multiplication and nothing else — which is why Step 2 undoes "
                      "it with a multiply",
             "example": "1/4x means (1/4)(x)"},
            {"symbol": "4/1",
             "plain": "the reciprocal of 1/4 — the same fraction turned upside down. "
                      "A fraction times its own reciprocal is always 1",
             "example": "(4/1)(1/4) = 1"},
            {"symbol": "improper fraction",
             "plain": "top heavier than the bottom, like -12/8. The other way round "
                      "— top lighter, like 9/14 — is a PROPER fraction, and no "
                      "instruction can turn it into an improper one. When a question "
                      "asks for an improper fraction, reduce but do NOT turn it into "
                      "a mixed number",
             "example": "-12/8 = -3/2, not -1 1/2"},
            {"symbol": "in line",
             "plain": "the book's space-saver: write the change out to the right of "
                      "the equation instead of underneath it",
             "example": "1/4x + 5/8 - 5/8 = 1/4 - 5/8"},
            {"symbol": "inequation",
             "plain": "what you technically start with in Part B — an equation with "
                      "an inequality sign. The book's own joke is that nobody calls "
                      "them that",
             "example": "3x - 5 ≤ 1"},
            {"symbol": "(C)",
             "plain": "a calculator is allowed on this problem. Allowed, not "
                      "required",
             "example": "Ex. 82.2 is marked (C)"},
        ],
        "after": "Notice that the two grand-sounding properties are the two ordinary "
                 "moves you already make. **Additive** = add the same thing to both "
                 "sides. **Multiplicative** = multiply both sides by the same thing. "
                 "The long names are labels, not extra rules.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "move",
        "title": "An inequality is the same job with a different kind of answer",
        "paragraphs": [
            "The sign at the fair says **you must be at least 48 inches to ride**. "
            "That is not one height. Forty-eight works, and so does 49, and 52, and "
            "48.5. It is a whole range of heights, described in one short line.",
            "That is what an inequality answers. An equation asks *which number*; an "
            "inequality asks *which numbers*.",
            "You solve it exactly the same way. Same Step 1, same Step 2. The book "
            "is blunt about it: *the ONLY difference is the inequality symbol, the "
            "additive and multiplicative properties work the same.* You copy `≤` or "
            "`>` down the page in the place where `=` used to go, and everything "
            "else is unchanged.",
            "What changes is the **answer**. `x ≤ 2` is not a number you can write "
            "in a blank — it is 2, and 1, and 0, and −7, and 1.999, forever in one "
            "direction. A range like that needs a picture, and the picture is a "
            "**number line**. That is Lesson 26B, and if the dots and the shading do "
            "not feel familiar, that is the lesson to go back to.",
            "Two things to get right on the drawing. A **solid** dot means the "
            "number itself is included — that is `≤` and `≥`, the ones with the "
            "little line underneath. A **hollow** dot means it is not — that is `<` "
            "and `>`. Then shade the side the answer points to.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Four symbols, and what each one does to the dot",
        "headers": ["symbol", "say it out loud", "the dot", "shade which way"],
        "rows": [
            {"cells": ["≤", "less than or equal to",
                       "solid — the number itself counts", "to the left"],
             "emphasis": True},
            {"cells": ["<", "less than",
                       "hollow — the number itself does not count", "to the left"]},
            {"cells": ["≥", "greater than or equal to",
                       "solid — the number itself counts", "to the right"],
             "emphasis": True},
            {"cells": [">", "greater than",
                       "hollow — the number itself does not count", "to the right"]},
        ],
        "note": "The two shaded rows are the ones with a line under the symbol, and "
                "the line is the reminder: **a line under the symbol means a filled "
                "dot on the line.** Say that to yourself once and you never have to "
                "decide again.",
    }),

    (B.KIND_WORKED, {
        "number": "82.3",
        "question": "Solve, then graph each solution on a number line.   "
                    "a) 3x - 5 ≤ 1      b) 2x + 5 > 9",
        "steps": [
            {"label": "a)  3x − 5 ≤ 1",
             "text": "The `- 5` is loose, so **Step 1** adds 5 to both sides and "
                     "leaves `3x ≤ 6`. The 3 is stuck to the x, so **Step 2** "
                     "divides both sides by 3. The `≤` just rides along, copied down "
                     "at every line exactly where an `=` would have gone.",
             "math": "3x - 5 + 5 ≤ 1 + 5  →  3x ≤ 6  →  3x ÷ 3 ≤ 6 ÷ 3  →  x ≤ 2"},
            {"label": "Graph a)",
             "text": "Mark 2 on the number line and make the dot **solid**, because "
                     "`≤` includes 2 itself. Then shade everything to the **left** — "
                     "1, 0, −1, −2 and on forever. Every one of those is less than "
                     "2, so every one of them is an answer."},
            {"label": "b)  2x + 5 > 9",
             "text": "The `+ 5` is loose, so **Step 1** adds −5 to both sides and "
                     "leaves `2x > 4`. **Step 2** divides both sides by 2. Copy the "
                     "`>` straight down — it does not move.",
             "math": "2x + 5 - 5 > 9 - 5  →  2x > 4  →  2x ÷ 2 > 4 ÷ 2  →  x > 2"},
            {"label": "Graph b)",
             "text": "Mark 2 again, but this time the dot is **hollow**: `>` means "
                     "strictly greater, so 2 itself is not an answer. Shade "
                     "everything to the **right**. Same number, different dot, "
                     "opposite shading — which is exactly why the dot is worth being "
                     "careful about."},
        ],
        "answer": "x ≤ 2 · x > 2",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Practice problem 382 asks which of four choices, A to D, is the "
                  "solution to 4x + 4 ≥ 20. The four choices are pictures in the "
                  "book and they did not copy across to this page, so read them in "
                  "your own book. What should you work out before you even look at "
                  "them?",
        "answer": "Solve it first, then go hunting for the picture — never the other "
                  "way round. **Step 1**: the `+ 4` is loose, so add −4 to both "
                  "sides. `4x + 4 - 4 ≥ 20 - 4`, which leaves `4x ≥ 16`. **Step 2**: "
                  "the 4 is stuck to the x, so divide both sides by 4. "
                  "`4x ÷ 4 ≥ 16 ÷ 4`, which leaves **`x ≥ 4`**.\n\n"
                  "Now go and read A to D. The book does not say here what the four "
                  "choices are pictures **of**, so check. If they are number lines — "
                  "which is what Part B has been drawing all lesson — the one you "
                  "want has a **solid dot on 4**, because the symbol has a line under "
                  "it and so 4 itself is included, and it is shaded **to the right**, "
                  "because the answers are 4 and everything bigger. If they turn out "
                  "to be something else, `x ≥ 4` is still the thing you are matching "
                  "them against.\n\n"
                  "Two seconds of checking: put 4 back in. Four fours is 16, plus 4 "
                  "is 20, and 20 ≥ 20 is true — so 4 really does belong. Now try 5: "
                  "twenty plus four is 24, and 24 ≥ 20 is true as well. Try 3: twelve "
                  "plus four is 16, and 16 ≥ 20 is false. The dot goes on 4 and the "
                  "shading goes right.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Multiplying only part of the equation.",
             "wrong": "1/4x + 5/8 = 1/4  →  x + 5/8 = 1  →  x = 3/8",
             "right": "1/4x + 5/8 - 5/8 = 1/4 - 5/8  →  1/4x = -3/8  →  "
                      "x = -12/8 = -3/2",
             "note": "This one multiplies by 4 to clear the `1/4` but only touches "
                     "two of the three numbers — the `5/8` never gets multiplied. "
                     "The answer comes out **3/8** instead of **-3/2**, and it is not "
                     "even negative, which is the tell. If you multiply, every term "
                     "on **both** sides gets multiplied. Shoes before socks — taking "
                     "the loose number off first is the road that keeps this from "
                     "happening, which is why Saxon puts it first."},
            {"name": "Moving the loose number by adding it instead of subtracting it.",
             "wrong": "-6.25k + 1.2 = 8.7  →  -6.25k = 8.7 + 1.2 = 9.9  →  k = -1.584",
             "right": "-6.25k + 1.2 = 8.7  →  -6.25k = 8.7 - 1.2 = 7.5  →  k = -1.2",
             "note": "Step 1 says add the **opposite** to both sides. The opposite "
                     "of `+ 1.2` is `- 1.2`, so the right side goes **down**. Adding "
                     "gives **-1.584** instead of **-1.2**. Catch it by writing the "
                     "line out in full — `+ 1.2 - 1.2` on the left forces `- 1.2` on "
                     "the right."},
            {"name": "Dropping the minus sign off the number you divide by.",
             "wrong": "-6.25k = 7.5  →  k = 7.5 ÷ 6.25 = 1.2",
             "right": "-6.25k = 7.5  →  k = 7.5 ÷ (-6.25) = -1.2",
             "note": "The thing stuck to the k is `-6.25`, minus sign and all, so "
                     "that whole thing is what you divide by. Divide by 6.25 and you "
                     "get **1.2** instead of **-1.2** — right digits, wrong answer. "
                     "A positive divided by a negative is negative; put the brackets "
                     "in and the sign stops going missing."},
            {"name": "Multiplying by the coefficient instead of by its reciprocal.",
             "wrong": "7/3x = 3/2  →  x = (7/3)(3/2) = 7/2",
             "right": "7/3x = 3/2  →  x = (3/7)(3/2) = 9/14",
             "note": "To peel `7/3` off the x you multiply by `3/7`, not by `7/3` — "
                     "the flipped one is the one that makes 1. This gives **7/2** "
                     "instead of **9/14**, and the two are nowhere near each other. "
                     "Say it out loud before you write it: *flip it, then multiply.*"},
            {"name": "Converting the mixed number wrong.",
             "wrong": "2 1/3 = 5/3  →  x = (3/5)(3/2) = 9/10",
             "right": "2 1/3 = 2 + 1/3 = 7/3  →  x = (3/7)(3/2) = 9/14",
             "note": "That adds the 2 and the 3 instead of multiplying them. It is "
                     "**bottom times whole, plus top** — 3 times 2 is 6, plus 1 is 7, "
                     "so `7/3`. One slip here quietly poisons everything after it: "
                     "the rest of the solution runs correctly and lands on **9/10** "
                     "instead of **9/14**."},
            {"name": "Flipping the inequality symbol when nothing told you to.",
             "wrong": "2x > 4  →  2x ÷ 2 ≤ 4 ÷ 2  →  x ≤ 2",
             "right": "2x > 4  →  2x ÷ 2 > 4 ÷ 2  →  x > 2",
             "note": "The symbol is copied straight down, line after line, exactly "
                     "where the `=` would have gone. Flip it and you get **x ≤ 2** — "
                     "the whole opposite half of the number line. Worth knowing: the "
                     "DIVE page for Ex. 82.3b has this very typo printed in it, "
                     "writing `2x÷2≤4÷2` and then correctly answering `x > 2` on the "
                     "next line. If your book and your answer disagree there, the "
                     "answer line is the one to trust."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**No new rules and no new definitions.** Step 1 is the additive "
            "property of equality and Step 2 is the multiplicative property, both "
            "from **Lesson 39**.",
            "Shoes before socks. The number **not touching the letter** comes off "
            "first — that is Step 1. Whatever is still stuck to the letter comes off "
            "second — that is Step 2.",
            "Everything you do, you do to **both sides**.",
            "**The only new thing is fractions and decimals.** Show work on the two "
            "steps; do the reducing, the common denominators and the mixed numbers "
            "**in your head**.",
            "Turn mixed numbers into improper fractions **before** Step 1 — `1 3/5` "
            "is `8/5`, `2 1/3` is `7/3` (bottom times whole, plus top).",
            "Step 2 is *multiply by the reciprocal* or *divide by the number* — the "
            "same move twice. Pick whichever is easier with the numbers in front of "
            "you.",
            "An inequality is solved **identically**. Copy `≤` or `>` down the page "
            "where `=` would go, and do not flip it.",
            "An inequality's answer is a **range**, so it needs a number line. A "
            "line under the symbol (`≤`, `≥`) means a **solid** dot; no line (`<`, "
            "`>`) means a **hollow** one.",
            "Always put your answer back into the original equation. It takes ten "
            "seconds and it turns 'I think so' into 'I know so'.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 82 first. If it didn't land, this is here to fix it — and "
    "the good news is on the book's own first page: there are no new rules and no "
    "new definitions in this lesson. You have been solving two step equations "
    "since Lesson 39. The only thing that changed today is that the numbers are "
    "fractions and decimals. At the end, one of them turns into an inequality — "
    "which you solve in exactly the same two steps."
)

PARENT_CONTENT = """## The big idea

Lesson 82 is **Lesson 39 with uglier numbers**, and the book says so on page one:
*"No New Rules or Definitions."* Step 1 is the additive property of equality, Step
2 is the multiplicative property, and she has been doing both since Ex. 39.5c —
Ex. 41.2 was full of two step equations. The book's only warning about today is
one sentence: *"the only difference here is these will involve more fractions and
decimals."*

Say that to her before she opens the page. It relocates the difficulty, and
relocating the difficulty is most of the help she needs. **If she gets stuck
today, it will almost certainly not be the method — it will be the fraction
arithmetic underneath it.** Those are two different problems with two different
fixes, and telling them apart is the single most useful thing you can do at the
table.

The order of the two steps has a reason, and the reason is worth a sentence of
your time: socks on, then shoes; shoes off, then socks. In `3x - 5`, the x was
multiplied by 3 **and then** 5 was taken away. The subtraction went on last, so it
comes off first.

Part B adds inequalities. It is the same two steps with `≤` or `>` copied down the
page where `=` used to be. What is genuinely different is the *answer*: not one
number but a range, which is why it gets drawn on a number line. That drawing is
**Lesson 26B** — if the solid-versus-hollow dots are shaky, revisit 26B rather
than re-explaining 82.

**One thing worth flagging about her book.** In Ex. 82.3b the DIVE page prints
`2x÷2≤4÷2` — the inequality symbol is flipped in the printed step, and then the
very next line correctly answers `x > 2`. It is a typo in the guide, not a rule.
If she notices it, tell her she is right and that the answer line is the one to
trust. (A symbol *does* flip when you multiply or divide **an inequality** by a
negative. No inequality in Lesson 82 needs that. Ex. 82.2a does divide by −6.25,
but that is an equation — there is no symbol there to flip — so it is not today's
fight.)

**About the page images.** In the PDF the equation lines for Ex. 82.1a, 82.1b and
82.2b are typeset pictures rather than text. Every intermediate number is printed
in the solution narration, though, so the starting equations are pinned exactly —
and each worked example on her page substitutes the answer back into the original
to prove it. Have her book open beside her anyway so she is reading the real
typesetting.

The same is true of **practice problem 382**: its four answer choices, A) to D),
are pictures that did not extract, and the book's wording here is *"which of the
following is the solution"* rather than its usual *"which is the graph of"*. Her
page says so plainly and tells her to read the choices in her own book. Given
Part B, number lines are the obvious guess — but the block deliberately does not
promise it, and it does not need to: the work is to derive `x ≥ 4` first and then
go matching.

One thing the source **does** say explicitly, and her page follows: the
"write answer as an improper fraction" instruction belongs to Ex. 82.1a only (and
to practice problem 182). Ex. 82.1b's answer, `9/14`, is a proper fraction and
could not be written as an improper one, so no such instruction is attached to it.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. **"Socks on, then shoes. Now take them off — which comes off first?"** Wait for
   "shoes." Then write `3x - 5 = 1` and ask: **"Which thing happened to the x
   last?"** You want "the take-away-5." That is the whole lesson, and she just said
   it herself before any symbol got explained.
2. Point at the equation and ask the question she will ask herself for the rest of
   the year: **"Which number is NOT touching the letter?"** Have her put a finger
   on it. That is the Step 1 number, always.
3. **"So what do we add to both sides to make it disappear?"** You want "add 5" —
   the *opposite*. Then say the important half out loud: *"and whatever we do to
   one side, we do to the other, or it stops being true."*
4. Now `3x ≤ 6` or `3x = 6`. **"What's still stuck to the x?"** — the 3. **"So what
   undoes a times-3?"** She may say "divide by 3" or "multiply by one-third." Both
   are right and they are the same move; tell her so, because Saxon uses both
   phrasings and she will otherwise think there are two rules.
5. Now switch to a fraction one — `1/4x + 5/8 = 1/4` — and ask **only** the two
   questions again: which number isn't touching the x, and what's still stuck to
   it. Do not let the fractions change the questions. When she gets to `1/4 - 5/8`,
   say: **"That part you do in your head. It's not the work; it's the tidying."**
   That is Saxon's own instruction and she should hear it as permission.

If she stalls, take the *same* problem and swap the fractions for whole numbers.
If she can do `4x + 5 = 1` in ten seconds and not `1/4x + 5/8 = 1/4`, the method
is fine and the fractions are the job — go do fractions.

## The classic mix-ups, with the exact wrong answer each one produces

- **Multiplying only part of the equation.** On `1/4x + 5/8 = 1/4` she multiplies
  by 4 to clear the quarter but only touches two of the three numbers, getting
  `x + 5/8 = 1` and answering **3/8** instead of **−3/2**. The tell: her answer
  isn't even negative. The defect is the partial multiply, not the order — done
  correctly, multiplying through by 4 first also gives −3/2 (see *Extend it*).
  Fix: every term, both sides — and Saxon's order is the one that makes that
  easy to get right.
- **Adding instead of subtracting in Step 1.** On `-6.25k + 1.2 = 8.7` she writes
  `-6.25k = 8.7 + 1.2 = 9.9` and answers **−1.584** instead of **−1.2**. Fix: make
  her write the full line — `+ 1.2 - 1.2` on the left forces `- 1.2` on the right.
- **The dropped minus on the divisor.** From `-6.25k = 7.5` she divides by `6.25`
  and answers **1.2** instead of **−1.2**. Right digits, wrong answer, and easy to
  miss when you are checking quickly. Fix: brackets — `7.5 ÷ (-6.25)`.
- **Multiplying by the coefficient instead of the reciprocal.** From `7/3x = 3/2`
  she multiplies by `7/3` and gets **7/2** instead of **9/14**. Fix, out loud
  before the pencil moves: *flip it, then multiply.*
- **The mixed-number conversion.** `2 1/3` becomes `5/3` (she added 2 and 3 instead
  of multiplying), and the entire rest of the solution runs correctly to **9/10**
  instead of **9/14**. This is the nastiest one because nothing downstream looks
  wrong. Fix: bottom × whole, **plus** top.
- **Flipping the inequality for no reason.** From `2x > 4` she writes `x ≤ 2`
  instead of `x > 2` — the opposite half of the number line. Fix: the symbol gets
  copied straight down, line after line, wherever an `=` would have gone.
- **Solid versus hollow dot.** `x ≥ 4` drawn with a hollow dot silently excludes 4.
  If 382's four choices turn out to be number lines, that picks the wrong letter
  even though her algebra was perfect. Fix: a line *under* the symbol means a
  *filled* dot.

## What to watch her do

Watch her **hands**, in this order.

1. **Does a finger land on the loose number before the pencil moves?** That is the
   whole method made visible. If she starts writing immediately, she is
   pattern-matching the last problem she saw, and it will hold up until the signs
   change.
2. **Does she write the change on both sides?** Watch for the pencil crossing the
   equals sign. The commonest silent failure at this level is a change made on the
   left and merely *intended* on the right.
3. **Where does the fraction arithmetic happen?** Saxon wants the two steps written
   and the reducing done mentally. If her page is a wall of eighths and tenths, she
   has buried her own work and cannot check it. If she is instead *guessing* the
   mental steps, that is the opposite problem and the fractions need practice on
   their own. Watch which one it is.
4. **Does she convert mixed numbers before Step 1 or partway through?** It must be
   before. Converting mid-solve is where `2 1/3` quietly becomes `5/3`.
5. **Does she put the answer back into the original?** Ten seconds. This lesson's
   answers are unfriendly enough (`-3/2`, `9/14`, `-1.2`) that she cannot eyeball
   them, and substitution is the only self-check she has.
6. **On an inequality, does the pencil pause at the dot?** A hesitation there means
   she is thinking about whether the number is included, which is exactly right. No
   hesitation usually means she drew whichever dot she drew last time.

A right answer on `3x - 5 ≤ 1` proves very little — the numbers are friendly enough
to fall out by accident. The six habits above are what survive `-2 1/3 x + 1 3/5 =
1/10`.

## Extend it

- Give her `1/4x + 5/8 = 1/4` again but ask her to do Step 2 **first** on purpose,
  correctly — multiply *everything* by 4/1, then subtract. She gets `-3/2` again.
  The point is not that order does not matter; it is that Saxon's order keeps the
  arithmetic clean, which she will only believe after seeing the messy way work.
- Ask what happens to `x ≤ 2` if you multiply both sides by −1. Let her test it
  with an actual number (is −2 ≤ −2? is −1 ≤ −2?) and discover the symbol has to
  turn around. She is not expected to know this yet — meeting it as a puzzle now
  makes the rule feel inevitable when Saxon formalises it later.
- Hand her a two step equation with the letter on the **right** — `8.7 = -6.25k +
  1.2` — and let her notice nothing at all changes. Equations do not have a front.
- Ask her to write her own two step equation whose answer is `9/14`. Building one
  backwards is a much stronger test of understanding than solving three more.

## Where this sits

DIVE Lesson 82, *Two Step Equations, Inequalities*. The lesson page lists its
reviews as **Lessons 26, 39, 41 and 70**. **Lesson 39 is the one to revisit if she
is lost on the method** — it is where the additive and multiplicative properties of
equality were taught, and 82 is those two properties used back to back. **Lesson
26B is the one to revisit if she is lost on the drawing**, since that is where
inequalities first went onto a number line. Lesson 41 is where she last met a run
of two step equations, so it is the place to find extra practice at friendlier
numbers.

**Proficient** looks like: solves a two step equation with decimals or simple
fractions, both steps shown, given time — and solves an inequality the same way.

**Mastered** looks like: converts mixed numbers before starting without being
reminded, keeps the negative signs through Step 2 on `-2 1/3 x + 1 3/5 = 1/10`,
substitutes the answer back in unprompted, and draws the right dot on the number
line without having to think about it.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 82 (two step equations, inequalities) — idempotent."

    LESSON_NUMBER = 82
    TITLE = "Two Steps, In That Order — Two Step Equations and Inequalities"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
