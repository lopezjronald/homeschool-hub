"""Saxon Pre-Algebra Lesson 99 — Sigma Means Sum.

Reviews Lessons 8, 62, 94 and 98. Lesson 98 is the hook, and the source names it
out loud: sums "are a lot like the series we covered in Lesson 98, except that
they don't necessarily always follow an arithmetic or geometric pattern." Lesson
62 sits underneath the Rule's own sentence that "the element is like a function"
— one input, never two outputs, which is why substituting 1, 2, 3, 4 hands you
exactly four numbers to add. Lesson 94 is where the lesson is pointed: the source
closes by saying integrals "are about summing the area under a function," and
Lesson 94 is where she counted those squares by hand.

Lesson 8 is listed as review on the book's first page but sits outside this
course's seeded lessons and this guide has not read it, so nothing here describes
what is in it. Nothing on Lesson 99's pages leans on it.

THREE JUDGEMENT CALLS.

* The notation cannot be stacked. The book prints the least value under the sigma
  and the greatest value above it; this template has no way to stack them, so
  every summation here is written on one line as `Σ  x = 1 to 4  of  3x`. Her page
  says so plainly in Idea 1 and again in the translation table, so the shape of
  the thing in her book is not a surprise.
* Example 99.2's element is `2ˣ + 1`, not `2x + 1`. The exponent is lost in the
  text extraction, but the book's own three solution lines settle it —
  `2⁰+1=1+1=2`, `2¹+1=2+1=3`, `2²+1=4+1=5`. Read as `2x + 1` those terms would be
  1, 3, 5 and the sum would be 9, not the printed 10. That misreading is error
  pattern 3 on her page, checkable at the first term. Those three lines are shown
  as `f(0) = 2⁰ + 1  →  1 + 1 = 2` rather than as the book's single unbroken
  `f(0) = 2⁰+1=1+1=2`: the arithmetic sweep in tutor/tests.py flattens superscript
  digits, so a bare `2⁰ + 1` inside an equals-chain reads as 21 and the guard
  fires on a correct line. Same numbers, one arrow instead of one equals.
* The tool offers only the bar chart. The chart widget's `line` readout is written
  for Lesson 74's fish data and says Saxon calls a line the wrong choice there —
  true of fish, meaningless here — so the switcher is not offered. Bars are the
  right picture anyway: a sum is countable separate pieces, which is exactly where
  Lesson 94's squares are going.

Page 1's "summation notation anatomy" is a labelled image and is not reproduced.
It is not needed: the Rule names all three parts in words — the element, the least
value, the greatest value n — and the anatomy table on her page is built from
those words rather than from the picture. Practice problems 1 and 2 are two more
summations printed the same way; the parent guide sends her to the book for them.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_99 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 99 · Pre-Algebra",
        "title": "Sigma is an instruction, not a number",
        "thesis": "Σ is a **short way of writing a paragraph of directions**: work "
                  "this out for every whole number from here to there, then add up "
                  "everything you got.",
        "formula": "Σ  x = 1 to 4  of  3x   =   3 + 6 + 9 + 12   =   30",
        "roles": [
            {"tone": "start", "name": "the element — what to work out",
             "text": "The expression sitting next to the Σ. Treat it as a function: "
                     "feed it a number, get one number back. It can be 3x, or x², or "
                     "1/t."},
            {"tone": "move", "name": "the two numbers — where to start, where to stop",
             "text": "Underneath the Σ is where the counting begins. Above it is "
                     "where it ends — and you stop *on* that number, not before it."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody invented a symbol for adding",
        "paragraphs": [
            "Say you start saving on a schedule. Week one you put away $3. Week two, "
            "$6. Week three, $9. Week four, $12 — every week you save three dollars "
            "times the week number. At the end of the month, how much is in the tin?",
            "Adding four numbers is not the hard part. Writing down the "
            "**instructions** is. In words it comes out like this: *take the week "
            "number, multiply it by three, write the answer down; do that again for "
            "week two; and again for week three; and again for week four; now add "
            "everything you wrote down.* That is a paragraph, and you would have to "
            "write it out again every time the job changed.",
            "So Leonhard Euler took one letter and made it stand for the whole "
            "paragraph. He picked the capital Greek **sigma**, Σ — the Greek S, for "
            "*sum*. That one character now says: do this for each whole number in "
            "this range, then add the results together.",
            "Which is the whole lesson. Your book's own first page says **No New "
            "Definitions**, and it means it — you have known how to multiply 3 by 4 "
            "and add a column of numbers for years. What is new is a piece of "
            "handwriting that tells you **which steps to repeat**.",
            "In **Lesson 98** you met a *series*: the indicated sum of a sequence. A "
            "Σ is very close to that, with one extra freedom. The numbers coming out "
            "do not have to march in an arithmetic or geometric pattern. Whatever the "
            "element hands you, you add it.",
            "And it is worth learning properly because of where it goes next — this "
            "notation is how calculus gets written down, which is what the end of "
            "this page is about.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Σ on its own does not equal anything. It tells you to do something.",
        "paragraphs": [
            "First thing to get straight, because it is where the fear comes from: Σ "
            "on its own is not a quantity. It is not something you multiply by. It is "
            "closer to a **verb** than to a number.",
            "Three pieces of information get packed around it. **The element** is the "
            "expression written to the right of the Σ — that is the thing you work "
            "out. **The least value** is written underneath, and it says where to "
            "start counting. **The greatest value** is written above, called **n** in "
            "your book, and it says where to stop.",
            "Two warnings about that stopping number. You stop **on** it, not before "
            "it. And you use every whole number in between — your book's phrase is "
            "*consecutive integers*, which means you skip none of them.",
            "One difference between your book and this page. In the book those two "
            "numbers are **stacked**, one tucked under the Σ and one sitting over it. "
            "A web page cannot stack them like that, so this page writes them beside "
            "it instead: `Σ  x = 1 to 4  of  3x`. Same instruction, laid out sideways. "
            "Your book's page 1 shows the stacked version with every part labelled — "
            "look at it once so the shape is familiar, and then the two are "
            "interchangeable to you.",
            "Last thing, and it catches people: **the least value does not have to be "
            "1.** Your book says so directly — it can be any integer, and 0 and 1 are "
            "the two you will see most often. Example 99.1 starts at 1. Example 99.2 "
            "starts at 0.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Don't try to work out what that symbol equals — on its own it "
                "doesn't equal anything. Read it to me as an instruction instead. "
                "Start where? Stop where? And what am I doing to each number in "
                "between? Now say the whole thing as one sentence: 'work out three x "
                "for x equals one, two, three and four, then add them.' If you can "
                "say that sentence, the arithmetic is the easy part.\"",
    }),

    (B.KIND_TABLE, {
        "caption": "One summation, part by part — built from the words in your book's "
                   "Rule, because the labelled picture lives on your book's page",
        "headers": ["the part", "where your book puts it", "what it tells you to do"],
        "rows": [
            {"cells": ["the element", "to the right of the Σ",
                       "the thing to work out — treat it as a function"],
             "emphasis": True},
            {"cells": ["the least value", "underneath the Σ",
                       "where to start. Usually x = 1 or x = 0"], "emphasis": True},
            {"cells": ["the greatest value, n", "above the Σ",
                       "where to stop — and you stop ON it"], "emphasis": True},
            {"cells": ["the letter itself", "in the element, and under the Σ",
                       "the name of the counter. Usually x, but not always"]},
        ],
        "note": "Read them in that order every single time and the notation stops "
                "being frightening: **what am I working out, where do I start, where "
                "do I stop.** And do not expect the element to always look like 3x — "
                "your book says it can be any single-variable relationship and prints "
                "`x²`, `1/t` and `3b⁵ + b` as its own examples. The last two do not "
                "even count in x.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, and the last one is just adding",
        "steps": [
            {"label": "Read the bottom number first.",
             "detail": "That is your **starting** value, and it goes at the left of "
                       "your page. In Example 99.1 it is x = 1. In Example 99.2 it is "
                       "x = 0, and zero is a perfectly ordinary place to begin."},
            {"label": "Read the top number, and count your terms before you write any.",
             "detail": "Greatest minus least, **plus one** — the plus one is there "
                       "because both ends are included. Knowing the count in advance "
                       "is how you catch yourself stopping early, and it costs one "
                       "second.",
             "math": "how many terms = greatest - least + 1"},
            {"label": "Rename the element as a function, then evaluate it one whole "
                      "number at a time.",
             "detail": "3x becomes f(x) = 3x, and then you write f(1), f(2), f(3), "
                       "f(4) on **separate lines**. One line each. Crowding them onto "
                       "one line is how a term goes missing without anyone noticing."},
            {"label": "Add the outputs.",
             "detail": "That is everything the Σ ever asked for, and the answer is a "
                       "single number. Nothing gets added until every term exists — "
                       "evaluate first, combine second."},
        ],
        "after": "Then count what you actually added against your prediction from step "
                 "2. If you said four terms and you are looking at three, you already "
                 "know what went wrong and roughly where. That check is worth more "
                 "than re-doing the arithmetic, because **the arithmetic is almost "
                 "never the problem in this lesson**.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 99.1 — Σ  x = 1 to 4  of  3x",
        "equation": "Σ  x = 1 to 4  of  3x",
        "steps": [
            {"label": "Look first",
             "text": "Nothing here needs discovering. The element is **3x**. The "
                     "bottom number says start at 1, the top number says stop at 4. "
                     "Before writing anything, say how many terms you are about to "
                     "make: 4 - 1 + 1 = **four**.",
             "math": "4 - 1 + 1 = 4 terms"},
            {"label": "Step 1 · rename the element as a function",
             "text": "Your book's own instruction: *treat the element, 3x, like a "
                     "function, f(x) = 3x.* Nothing has changed except the name. It is "
                     "worth doing, because **f(1)** is something you already know how "
                     "to work out, while \"3x at x = 1\" is something you have to stop "
                     "and think about.",
             "math": "f(x) = 3x"},
            {"label": "Step 2 · evaluate at every whole number from 1 to 4",
             "text": "Four substitutions, four answers. Notice that all four are still "
                     "sitting there unadded — that is on purpose. Nothing gets "
                     "combined until every term exists.",
             "math": "3(1) + 3(2) + 3(3) + 3(4) = 3 + 6 + 9 + 12"},
            {"label": "Step 3 · add them up",
             "text": "Your book adds them in pairs rather than left to right, which is "
                     "easier to hold in your head: 3 and 6 make 9, 9 and 12 make 21, "
                     "and 9 and 21 make 30.",
             "math": "3 + 6 + 9 + 12   →   9 + 21 = 30"},
            {"label": "Step 4 · look at what came out",
             "text": "Your book stops here to point something out, so look at the four "
                     "outputs: 3, 6, 9, 12. Each one is 3 more than the one before — "
                     "in its words, *an arithmetic series with a common difference of "
                     "3*, which is Lesson 98's language turning up again. That "
                     "happened because the element was 3x. It will **not** always "
                     "happen, and the very next example proves it.",
             "math": "3, 6, 9, 12   →   common difference 3"},
        ],
    }),

    (B.KIND_MATH, {
        "display": "3(1) + 3(2) + 3(3) + 3(4)  =  3 + 6 + 9 + 12  =  30",
        "note": "That entire line is what the Σ was short for. Read it backwards for a "
                "moment: **30** is the answer, `3 + 6 + 9 + 12` is the sum written "
                "out, `3(1) + 3(2) + 3(3) + 3(4)` is the substituting that produced "
                "it, and `Σ` is all of it compressed into one character. Every step is "
                "arithmetic you have been able to do for years. The only genuinely new "
                "thing in this lesson is the shorthand at the front.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "The element is a function wearing different clothes",
        "paragraphs": [
            "Your book says this twice, so it is worth slowing down for: *the element "
            "is like a function, and can be any single-variable relationship.* The "
            "three it offers are `x²`, `1/t` and `3b⁵ + b`.",
            "Two things follow from that. First, **the letter is not always x.** "
            "`1/t` counts in t; `3b⁵ + b` counts in b. The letter written under the Σ "
            "tells you which one is doing the counting, and it will be the same letter "
            "you see inside the element.",
            "Second, hand the element one of the whole numbers in the range and you "
            "will **never get two answers back**. That is Lesson 62's definition of "
            "a function doing quiet work here — a relation that gave two outputs "
            "for one input would leave you standing there wondering which one to "
            "add.",
            "So the substituting is completely mechanical, and it is supposed to be. "
            "Feed the element the starting number, write down what comes out; feed it "
            "the next number, write down what comes out. The element is allowed to be "
            "as ugly as it likes. The process does not change at all.",
            "Example 99.2's element is **2ˣ + 1**, and read that carefully: it is 2 "
            "raised to the power x, and then you add 1. It is **not** 2 times x, plus "
            "1. That single misreading is the most expensive mistake in the lesson, "
            "and you can catch it at the very first term — 2⁰ is 1, so that term comes "
            "out 2, while 2 times 0 is 0, which would give you 1.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "99.2",
        "question": "Find  Σ  x = 0 to 2  of  2ˣ + 1",
        "steps": [
            {"label": "Read the range before you do anything else",
             "text": "The bottom number is **x = 0**. Zero is where you start and it "
                     "is a real term, not a blank. Greatest minus least plus one gives "
                     "three terms — say \"three\" out loud now, because two is the "
                     "answer people end up with.",
             "math": "2 - 0 + 1 = 3 terms"},
            {"label": "Rename the element as a function",
             "text": "Your book again: *treat the element, 2ˣ + 1, like a function, "
                     "f(x) = 2ˣ + 1, and evaluate f(0), f(1) and f(2).* Exactly the "
                     "same move as Example 99.1, on a much less friendly-looking "
                     "element.",
             "math": "f(x) = 2ˣ + 1"},
            {"label": "f(0) — and this is where 2ˣ proves it is not 2x",
             "text": "Anything except zero, raised to the power zero, is 1 — so 2⁰ is "
                     "**1**, not 0. Then add the 1 that was already sitting in the "
                     "element.",
             "math": "f(0) = 2⁰ + 1   →   1 + 1 = 2"},
            {"label": "f(1)",
             "text": "2 to the first power is just 2.",
             "math": "f(1) = 2¹ + 1   →   2 + 1 = 3"},
            {"label": "f(2)",
             "text": "2 squared is 4.",
             "math": "f(2) = 2² + 1   →   4 + 1 = 5"},
            {"label": "Add the three outputs",
             "text": "Three terms, exactly as predicted. Your book writes its final "
                     "line in precisely this shape — the Σ there is standing in for "
                     "the summation you have just carried out, which is what makes "
                     "putting 10 on the other side of the equals fair. A bare Σ, with "
                     "no element and no range around it, still does not equal "
                     "anything.",
             "math": "Σ = 2 + 3 + 5 = 10"},
            {"label": "Now look at the outputs and notice what is missing",
             "text": "2, 3, 5. From 2 to 3 is a step of one; from 3 to 5 is a step of "
                     "two. There is **no common difference** here at all. So Example "
                     "99.1's tidy pattern was a property of *that element*, not a rule "
                     "about sums — which is your book's own point when it says sums do "
                     "not necessarily follow an arithmetic or geometric pattern. "
                     "Evaluate every term. There is no shortcut waiting for you."},
        ],
        "answer": "10",
    }),

    (B.KIND_TABLE, {
        "caption": "The lesson's two examples, side by side",
        "headers": ["what to compare", "Example 99.1", "Example 99.2"],
        "rows": [
            {"cells": ["the element", "3x", "2ˣ + 1"]},
            {"cells": ["starts at", "x = 1", "x = 0"]},
            {"cells": ["stops at", "4", "2"]},
            {"cells": ["how many terms", "4 - 1 + 1 = 4", "2 - 0 + 1 = 3"],
             "emphasis": True},
            {"cells": ["the outputs", "3, 6, 9, 12", "2, 3, 5"]},
            {"cells": ["a pattern in the outputs?", "yes — up by 3 every time",
                       "no — up 1, then up 2"], "emphasis": True},
            {"cells": ["the sum", "30", "10"], "emphasis": True},
        ],
        "note": "Two examples, one procedure — and the procedure did not care that "
                "one element was 3x and the other 2ˣ + 1. Look hard at the "
                "term-count row: the same **+ 1** turns up in both, and it is the "
                "thing standing between you and a missing term. Then look at the "
                "pattern row, because "
                "a whole lesson's worth of caution lives in it — **a sum does not owe "
                "you a pattern.**",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "Where this is going: adding up the pieces of a curve",
        "paragraphs": [
            "Your book spends its last paragraph on why anybody outside this chapter "
            "cares, and it names two places.",
            "**Computers.** A computer cannot hold something smooth and unbroken. It "
            "needs discrete pieces — separate things it can count. A sum is the tool "
            "for chopping something continuous into pieces and then putting one number "
            "on the whole collection.",
            "**Calculus, and integrals especially.** In your book's own words, "
            "integrals are about **summing the area under a function**. You have "
            "already done one of those by hand: in **Lesson 94** you found the area "
            "under a graph by counting squares. Every square was a piece, and the "
            "counting was the adding.",
            "So a Σ is what that square-counting looks like once it is written down. "
            "Chop the space under a curve into strips, work out the area of one strip, "
            "then add every strip from the left edge to the right edge. A thing to "
            "work out, a place to start, a place to stop — which is exactly the "
            "anatomy at the top of this page.",
            "Nobody is asking you to do calculus today. You are being handed the "
            "notation it gets written in a little early, so that when the strips show "
            "up the symbol in front of them is already an old friend.",
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "This lesson is one symbol and the furniture standing around it. Here "
                 "is every mark, and what each one is short for.",
        "rows": [
            {"symbol": "Σ", "plain": "capital Greek sigma — Euler's letter for SUM. An "
                                     "instruction, not a quantity on its own",
             "example": "Σ  x = 1 to 4  of  3x"},
            {"symbol": "the element", "plain": "the expression next to the Σ — the "
                                               "thing you evaluate, over and over",
             "example": "3x"},
            {"symbol": "x = 1 (below)", "plain": "the least value: where the counting "
                                                 "starts",
             "example": "first term is 3(1)"},
            {"symbol": "n (above)", "plain": "the greatest value: where the counting "
                                             "stops, and it IS included",
             "example": "last term is 3(4)"},
            {"symbol": "Σ x = 1 to 4 of 3x",
             "plain": "how THIS page writes it, because a web page cannot stack the "
                      "two numbers under and over the sigma",
             "example": "your book stacks them"},
            {"symbol": "f(x)", "plain": "the element renamed as a function, so you can "
                                        "say f(1), f(2), f(3) instead of a sentence",
             "example": "f(x) = 3x"},
            {"symbol": "2ˣ", "plain": "2 raised to the power x — NOT 2 times x",
             "example": "2⁰ = 1"},
            {"symbol": "consecutive integers",
             "plain": "every whole number from the least to the greatest, skipping "
                      "none of them",
             "example": "0, 1, 2"},
            {"symbol": "series", "plain": "Lesson 98's word for the indicated sum of a "
                                          "sequence — a Σ is one way of writing one",
             "example": "3 + 6 + 9 + 12"},
            {"symbol": "common difference",
             "plain": "the fixed step from one term to the next, on the occasions when "
                      "there is one",
             "example": "3, 6, 9, 12 → 3"},
        ],
        "after": "The row to hold on to is the first one. **Σ does not equal anything "
                 "by itself.** It is a set of directions with a number waiting at the "
                 "end of them, and every other row in this table is a detail about "
                 "which directions.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Stopping one short of the top number.",
             "wrong": "Σ x = 1 to 4 of 3x   →   3 + 6 + 9 = 18",
             "right": "3 + 6 + 9 + 12 = 30",
             "note": "**18 instead of 30.** The greatest value is where you stop, not "
                     "where you stop *before*. This is the single most common "
                     "summation error there is, and counting your terms first — "
                     "greatest minus least plus one — makes it impossible. Four "
                     "predicted, three added, and you have found it before you wrote "
                     "the answer down."},
            {"name": "Skipping the term where x = 0.",
             "wrong": "Σ x = 0 to 2 of 2ˣ + 1   →   3 + 5 = 8",
             "right": "2 + 3 + 5 = 10",
             "note": "**8 instead of 10.** Zero looks like nothing, so it gets treated "
                     "like nothing — but f(0) is an output like any other, and here it "
                     "is 2. Your book says outright that 0 and 1 are the two most "
                     "common starting values, so this comes up constantly. 2 - 0 + 1 "
                     "is three terms; if you are adding two, one has gone missing."},
            {"name": "Reading 2ˣ as 2x.",
             "wrong": "2(0)+1,  2(1)+1,  2(2)+1   →   1 + 3 + 5 = 9",
             "right": "2⁰+1,  2¹+1,  2²+1   →   2 + 3 + 5 = 10",
             "note": "**9 instead of 10** — one away from right, which is exactly what "
                     "makes it dangerous. An exponent is a small mark and it is easy "
                     "to lose. Check it at the very first term, and carry it all the "
                     "way through: `2ˣ` at x = 0 is 1, so the first term is 1 + 1 = "
                     "**2**. Read as `2x`, x = 0 gives 0, so the first term would be "
                     "0 + 1 = **1**. A first term of 1 means the exponent got "
                     "dropped."},
            {"name": "Substituting only the top number.",
             "wrong": "Σ x = 1 to 4 of 3x   →   3(4) = 12",
             "right": "3(1) + 3(2) + 3(3) + 3(4) = 30",
             "note": "**12 instead of 30.** This is Σ being read as a container for "
                     "one calculation instead of an instruction to repeat one. The top "
                     "number is not *the* input — it is the **last** input. Say the "
                     "instruction out loud before your pencil moves: *for every whole "
                     "number from here to there.*"},
            {"name": "Expecting the outputs to make a pattern, then using it as a "
                     "shortcut.",
             "wrong": "outputs 2, 3, …   →   assume it climbs by 1   →   2 + 3 + 4 = 9",
             "right": "evaluate all three   →   2 + 3 + 5 = 10",
             "note": "**9 instead of 10.** Example 99.1's outputs really did climb by a "
                     "steady 3, and noticing that is a good habit — but it was a "
                     "property of that element, not a promise. Your book is explicit: "
                     "sums do not necessarily follow an arithmetic or geometric "
                     "pattern. Evaluate every term, then spot the pattern afterwards "
                     "if there is one to spot."},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "The four terms of Example 99.1, as four bars",
        "intro": "One bar per term of `Σ x = 1 to 4 of 3x` — each one is an output of "
                 "f(x) = 3x, with its input written underneath. **Four bars, because "
                 "there are four terms**, and the sum is all four of them put "
                 "together: 30. Two things to look at. The tops climb by exactly the "
                 "same amount each time, which is the common difference of 3 your book "
                 "pointed out. And the picture is made of separate countable pieces "
                 "rather than one smooth line — which is the whole reason sums matter "
                 "to computers and to integrals.",
        "widget": "chart",
        # `kinds: ["bar"]` on purpose, so no switcher renders. The widget's `line`
        # readout is written for Lesson 74's fish data — it tells the reader Saxon
        # says a line is the wrong choice here, which is true of monthly fish counts
        # and meaningless for four terms of a summation. Bars are the honest picture
        # anyway: a sum is separate countable pieces, which is where Lesson 94's
        # squares are going. Values are read off each bar's own label because the
        # widget's gridlines land on 2.5s for this data; `after` says so.
        "config": {
            "data": [
                {"label": "x = 1 → 3", "value": 3},
                {"label": "x = 2 → 6", "value": 6},
                {"label": "x = 3 → 9", "value": 9},
                {"label": "x = 4 → 12", "value": 12},
            ],
            "kinds": ["bar"],
            "label": "the four terms of Example 99.1 drawn as bars: 3, 6, 9 and 12",
        },
        "after": "Cover the bars one at a time with your hand and read what total is "
                 "left standing. Then answer this before you open the drop-down: if "
                 "the greatest value were **5** instead of 4, how tall would the fifth "
                 "bar be, and what would the whole sum become?\n\n"
                 "One honest note about the chart itself. The faint gridlines behind "
                 "the bars come in steps of 2.5, which is an awkward scale for these "
                 "numbers — so read the value written under each bar rather than "
                 "trying to read heights off the lines.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "If the top number were 5 instead of 4, how tall is the fifth bar, "
                  "and what is the new sum?",
        "answer": "**The fifth bar is 15, and the sum becomes 45.** The element never "
                  "changed — it is still 3x — so the new term is simply f(5):   →   "
                  "3(5) = 15   →   30 + 15 = 45   →   And notice you did not start "
                  "over. Raising the greatest value **adds terms to the end**; every "
                  "term you already worked out is still good, which is worth knowing "
                  "the first time a problem asks you for a long one. The outputs are "
                  "now 3, 6, 9, 12, 15 — still climbing by 3, because a straight-line "
                  "element like 3x is what produced that pattern in the first place.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Σ is an instruction, not a number.** It says: work the element out for "
            "every whole number in the range, then add all the answers together.",
            "Three parts. The **element** (what to work out) sits to the right. The "
            "**least value** (where to start) sits underneath. The **greatest value "
            "n** (where to stop) sits above. Read them in that order.",
            "**You stop ON the top number.** Count your terms before you make any: "
            "greatest minus least, plus one.",
            "The least value does not have to be 1 — **0 and 1 are the two most "
            "common** — and f(0) is a real term that gets added like any other.",
            "Treat the element as a function, `f(x) = 3x`, and write one substitution "
            "per line. It can be any single-variable relationship: `x²`, `1/t`, "
            "`3b⁵ + b`. The letter is not always x.",
            "Example 99.1:  `3(1) + 3(2) + 3(3) + 3(4) = 3 + 6 + 9 + 12 = 30`.",
            "Example 99.2:  `2ˣ + 1` from 0 to 2 gives `2 + 3 + 5 = 10` — and "
            "remember that **2ˣ is not 2x**.",
            "**A sum does not owe you a pattern.** 99.1's outputs climbed by a steady "
            "3 — what your book calls *an arithmetic series with a common difference "
            "of 3* (Lesson 98). 99.2's did not climb by any steady amount at all. "
            "Evaluate every term either way.",
            "A sum is how something smooth gets broken into countable pieces. That is "
            "why computers use them, and why an integral — the area under a function "
            "you counted squares for in **Lesson 94** — is a sum underneath.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 99 first. If that symbol looked like a lot, this is here to "
    "fix that — Σ is one letter standing in for a whole paragraph of instructions, "
    "and there are four bars near the bottom you can count. Two things to hold on to "
    "today: you stop *on* the top number, not before it, and the thing sitting next "
    "to the sigma is only a function waiting for numbers."
)

PARENT_CONTENT = """## The big idea

One symbol, and her book is honest about it: page one says **No New Definitions**.
Every piece of arithmetic in Lesson 99 is something she has been able to do for
years. What is new is a **notation** — a compressed way of writing down which steps
to repeat.

Say the sentence to her, because it is the whole lesson: **Σ is an instruction, not
a number.** It does not equal anything on its own. It says *work the element out for
every whole number from the bottom value to the top value, then add up what you
got.* Euler chose the capital Greek sigma for *sum*, and her book makes the point
that symbolic notation "saves us from having to explain in writing which steps to
repeat each time."

Three parts, and her book's Rule names all three in words:

- **the element** — the expression to the right of the Σ, which her book says to
  treat "like a function," and which can be "any single-variable relationship" —
  `x²`, `1/t`, `3b⁵ + b` are its own examples;
- **the least value** — written under the Σ, where the counting starts;
- **the greatest value, n** — written above it, where the counting stops.

**The two most common errors are both about the range, not the arithmetic.** She
stops one short of the top number, or she skips the term where x = 0 because zero
looks like nothing. Both are cured by the same habit: count the terms *before*
making any. Greatest minus least, **plus one**. Four terms in Ex. 99.1, three in
Ex. 99.2. If she predicts four and adds three, she catches herself in a second.

That habit does not reach the third error, and the third error is not about the
range at all: misreading `2ˣ` as `2x`, under Ex. 99.2 below. It hands her three
terms — the count she predicted — and a final answer of 9 that looks entirely
reasonable, which is why her page calls it the most expensive mistake in the
lesson. For that one, watch her *first term*, not her term count.

**Ex. 99.1** — `Σ` from x = 1 to 4 of `3x`. Treat it as f(x) = 3x, evaluate at 1, 2,
3, 4: `3(1) + 3(2) + 3(3) + 3(4) = 3 + 6 + 9 + 12`. The book adds in pairs —
`9 + 21 = 30`. Then it stops to observe that the outputs 3, 6, 9, 12 form "an
arithmetic series with a common difference of 3," which is Lesson 98's vocabulary
coming back.

**Ex. 99.2** — `Σ` from x = 0 to 2 of `2ˣ + 1`. Three terms, starting at zero:
`f(0) = 2⁰ + 1 = 1 + 1 = 2`, `f(1) = 2¹ + 1 = 3`, `f(2) = 2² + 1 = 5`, so
`Σ = 2 + 3 + 5 = 10`. Two traps live in this one. The element is **2 to the
power x**, not 2 times x — read as `2x + 1` the terms come out 1, 3, 5 and the sum
is 9, not 10. And the outputs 2, 3, 5 have **no** common difference, which is the
book's own caveat arriving on cue: sums "don't necessarily always follow an
arithmetic or geometric pattern." Ex. 99.1's tidiness was the element's doing, not a
rule.

**A note on the page's layout, so it does not surprise either of you.** Her book
stacks the two numbers above and below the sigma. This template cannot stack them,
so her page writes every summation on one line as `Σ  x = 1 to 4  of  3x` and says
so twice — in Idea 1 and in the translation table. Page one of her book shows the
stacked version with each part labelled; that picture is not reproduced here and is
worth a shared glance so the shape is familiar. **Practice problems 1 and 2 are two
more summations printed the same way**, so work those straight from the book rather
than from anything on her screen.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Write `Σ` on paper and ask: **"What do you think that equals?"** Let her try. Then
   tell her the answer is that it does not equal anything — it is closer to a verb.
   Starting here saves ten minutes of her hunting for a value that is not there.
2. Write the Ex. 99.1 summation the way her book does, stacked. Point at each of the
   three parts and ask **"what do you think this one is for?"** — element, bottom,
   top. She can usually reason out the bottom and top from the phrase *least value*
   and *greatest value*; the element is the one to tell her.
3. Ask the question that prevents the two big errors: **"Before you work anything
   out — how many numbers are you going to end up adding?"** You want *four*, and you
   want to hear the reasoning "one, two, three, four" or "4 minus 1 plus 1." If she
   says three, do not correct her — ask her to count them on her fingers out loud.
4. Now let her do it. `3(1) + 3(2) + 3(3) + 3(4)`. It will feel too easy, and saying
   that out loud is the point: **the hard part was reading the symbol, not the
   maths.** Then have her look at 3, 6, 9, 12 and ask what she notices — you want
   "they go up by 3."
5. Straight into Ex. 99.2 while that is still warm, because it is the counterweight.
   **"This one starts at zero. How many terms?"** — three, and zero is one of them.
   **"And 2ˣ — is that two times x?"** — no. Then, once she has 2, 3, 5, ask the
   question that matters most: **"Do these go up by a steady amount like the last
   ones did?"** They do not. That is her book's warning, arrived at by her rather
   than read to her.

If she is lost, go back to step 1. Everything else in this lesson is substitution
and addition.

## The classic mix-ups, with the exact wrong answer each one produces

- **Stopping one short of the top number.** `Σ` 1 to 4 of `3x` becomes
  `3 + 6 + 9` = **18** instead of **30**. The top value is included. Fix: count the
  terms before making any — greatest minus least plus one.
- **Skipping x = 0.** In Ex. 99.2 she writes `3 + 5` = **8** instead of **10**. Zero
  looks like a non-thing; f(0) is a perfectly real 2. Fix: same count, `2 - 0 + 1`
  is three terms, so two terms means one is missing.
- **Reading `2ˣ` as `2x`.** Terms come out 1, 3, 5 and the sum is **9** instead of
  **10** — one away, which is what makes it slip through. Fix: check the first term,
  carried through to the end. `2ˣ` at x = 0 is 1, so the term is 1 + 1 = **2**. Read
  as `2x`, x = 0 gives 0, so the term would be 0 + 1 = **1**. A first term of 1
  means the exponent got dropped.
- **Substituting only the top number.** `3(4)` = **12** instead of **30**. This is Σ
  read as a container for one calculation rather than an instruction to repeat one.
  Fix: make her say the instruction as a sentence before the pencil moves.
- **Assuming a pattern and shortcutting it.** Having seen 3, 6, 9, 12 climb by 3, she
  assumes 2, 3, … climbs by 1 and writes `2 + 3 + 4` = **9** instead of **10**. Fix:
  evaluate every term; notice the pattern *after*, never instead.
- **Treating Σ as a quantity.** Arithmetic done *to* a bare sigma, with no element
  and no range attached — "Σ × 3", "Σ + 5". If you see that, stop and go back to the
  first teaching step above; nothing downstream will make sense until it is undone.
  Her book's own `Σ = 2 + 3 + 5 = 10` is a different thing and is correct: written
  after the instruction has been carried out, it is shorthand for *the value of this
  summation is 10*.

## What to watch her do

Watch her **paper**, in this order:

1. **Does a term count appear before any terms do?** A small "4" or "3" written at
   the top of the working is the single most diagnostic mark on the page. It is the
   habit that immunises her against the two most common errors in the entire topic.
2. **Is there one substitution per line?** `f(0) =`, `f(1) =`, `f(2) =` stacked down
   the page. Everything crammed onto one line is where a term evaporates, and you can
   see it from across the table.
3. **Does she write the substituted form before the answer?** You want to see
   `3(1) + 3(2) + 3(3) + 3(4)` on the page, not just `3 + 6 + 9 + 12` appearing out
   of nowhere. The substituted line is her proof of which inputs she actually used.
4. **On Ex. 99.2, does her first term come out 2 or 1?** A 1 means she read `2ˣ` as
   `2x`. This is worth glancing at specifically, because the final answer of 9 looks
   entirely reasonable and nothing else on the page flags it.
5. **After she gets a total, does she look back at the outputs?** Her book models
   this — "observe how the results formed an arithmetic series" — and it is a good
   mathematical instinct. Just make sure the looking happens *after* the adding, not
   instead of some of it.

Getting 30 is not what to watch for. She can get 30 by copying the shape of the
worked example. The term count and the one-line-per-substitution habit are what
survive a summation with nine terms in it.

## Extend it

- **Change one number and re-ask.** Same element, `3x`, but stop at 5 instead of 4.
  The point is not the answer (45) — it is that she does **not** start over. Raising
  the top value adds terms to the end; everything already worked out still stands.
  That is on her page as the drop-down under the bar chart, so let her predict first.
- **Change the bottom instead.** `3x` from x = 2 to 4 is `6 + 9 + 12` = 27. Ask her
  which term disappeared and why. Moving the least value is a different kind of
  change from moving the greatest one, and feeling that difference is worth five
  minutes.
- **Have her write one.** Give her a plain instruction in words — *"add up the
  squares of 1, 2 and 3"* — and ask her to write it as a summation. Going the other
  way round is the real test of whether the notation has landed, and it is much
  harder than reading one.
- **Point at problem 8 of her own practice set.** It asks her to estimate the area
  under a linear function from x = 0 to 4 by counting squares — Lesson 94. That *is*
  a sum: every square is a term. Her book's own line for this lesson says integrals
  "are about summing the area under a function," and the two problems are sitting in
  the same practice set. Showing her that connection costs one sentence and is the
  best answer available to "when will I use this."

## Where this sits

DIVE Lesson 99, *Sigma Means Sum*. Reviews **Lessons 8, 62, 94 and 98**.

- **Lesson 98** is the one to revisit if the vocabulary is what is bothering her —
  sequence, series, common difference, common ratio. Lesson 99's text hooks onto it
  by name and then adds one freedom: a sum does not have to follow a pattern.
- **Lesson 62** is the one behind the Rule's phrase "the element is like a function."
  If she is uneasy about why substituting is allowed to be so mechanical, that is
  where one-input-one-output was settled.
- **Lesson 94** is where this is going, not where it came from — counting squares
  under a graph. Worth naming out loud even though nothing in today's teaching
  depends on it.
- **Lesson 8** is listed as review on her book's first page, but it sits outside this
  course's seeded lessons and this guide has not read it, so nothing here describes
  what is in it. Lesson 99's pages do not lean on it; if the review list matters to
  you, her book's Lesson 8 is the place to look.

**Proficient** looks like: reads a summation correctly, evaluates every term, and
adds them — given a straightforward element and the range written out.
**Mastered** looks like: counts the terms before writing any, starts at 0 without
hesitating, does not confuse `2ˣ` with `2x`, and does not assume a pattern she has
not checked.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 99 (sigma means sum) — idempotent."

    LESSON_NUMBER = 99
    TITLE = "Sigma Means Sum — One Symbol for a Paragraph of Instructions"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
