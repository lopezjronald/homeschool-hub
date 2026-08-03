"""Saxon Pre-Algebra Lesson 72 — Operations with Scientific Notation.
Reviews Lessons 8, 59, 64.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_72 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 72 · Pre-Algebra",
        "title": "Adding and multiplying enormous numbers without writing the zeros",
        "thesis": "The `× 10ⁿ` is a **note about where the decimal point went**. "
                  "Everything in this lesson comes from that one fact.",
        "formula": "4.42 × 10⁴",
        "roles": [
            {"tone": "move", "name": "the front number",
             "text": "The digits. In standard form, exactly one of them sits before "
                     "the decimal point."},
            {"tone": "start", "name": "the power of ten",
             "text": "How far the point slid, and which way."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody writes numbers this way",
        "paragraphs": [
            "The sun is about 93,000,000 miles away. A virus is about 0.00000012 m "
            "across. Try adding those on paper and you will lose your place counting "
            "zeros — and losing your place by one zero means being wrong by a factor "
            "of ten.",
            "Scientific notation keeps the digits that matter and puts the zeros into "
            "a little number up in the corner. Once it is written that way, the "
            "arithmetic gets **easier**, not harder — especially multiplying.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 2, "tone": "start",
        "title": "The point and the power pay for each other",
        "paragraphs": [
            "Slide the decimal point one place **left** and the number gets ten times "
            "smaller — so the exponent goes **up** by one to pay it back. Slide it "
            "**right** and the exponent goes **down**.",
            "The value never changes. That is the whole trick, and it is worth playing "
            "with until it feels obvious.",
        ],
    }),

    (B.KIND_TOOL, {
        "title": "Slide the point and watch the value refuse to move",
        "intro": "Drag the slider. The digits move one way, the exponent moves the "
                 "other, and the number at the bottom does not budge.",
        "widget": "scislide",
        "config": {"mantissa": 3.2, "exponent": 3, "span": 4},
        "after": "That is why `3.2 × 10³` and `0.32 × 10⁴` are the same number — and "
                 "why you are allowed to swap one for the other whenever it suits you.",
    }),

    (B.KIND_SAY, {
        "text": "\"Watch the bottom number. I'm going to move the decimal point all "
                "over the place and the actual value is going to sit there doing "
                "nothing. Whatever you take off the front, the little number pays back.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 2, "tone": "move",
        "title": "Same shoes to add. Split the job to multiply.",
        "paragraphs": [
            "**Adding or subtracting:** you cannot add 3 apples and 4 oranges, and you "
            "cannot add `10³` and `10⁴`. Slide one of them until **both powers match**, "
            "then add the front numbers and keep the power.",
            "**Multiplying or dividing:** you are allowed to shuffle the four factors "
            "around. Put the front numbers together, put the powers together. Multiply "
            "the fronts and **add** the exponents; divide the fronts and **subtract** "
            "them.",
            "Then, always, look at the answer and ask: *is exactly one digit sitting "
            "in front of the point?* If not, slide it — and pay the exponent.",
        ],
    }),

    (B.KIND_STEPPER, {
        "title": "Example 72.1a — add 3.2 × 10³ and 4.1 × 10⁴",
        "equation": "3.2 × 10³  +  4.1 × 10⁴",
        "steps": [
            {"label": "Look first",
             "text": "The powers are **different** — 3 and 4. You cannot add them yet. "
                     "Pick one and slide it to match the other."},
            {"label": "Step 1 · make the shoes match",
             "text": "Slide 3.2 × 10³ one place left. The front shrinks, the power "
                     "grows.",
             "math": "3.2 × 10³  =  0.32 × 10⁴"},
            {"label": "Step 2 · now they add",
             "text": "Same power, so add the fronts and keep the power.",
             "math": "(0.32 + 4.1) × 10⁴  =  4.42 × 10⁴"},
            {"label": "Step 3 · is it dressed properly?",
             "text": "One digit before the point — a 4. Yes. Done.",
             "math": "4.42 × 10⁴"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "72.1b",
        "question": "6.2 × 10⁵ + 8.9 × 10⁵",
        "steps": [
            {"label": "Powers already match", "text": "Both are 10⁵. Just add the fronts."},
            {"label": "Add", "math": "(6.2 + 8.9) × 10⁵ = 15.1 × 10⁵"},
            {"label": "Dressed properly?", "text": "**No** — 15.1 has two digits in "
                                                   "front. Slide left one, pay the "
                                                   "exponent."},
            {"label": "Renormalise", "math": "15.1 × 10⁵ = 1.51 × 10⁶"},
        ],
        "answer": "1.51 × 10⁶",
    }),

    (B.KIND_WORKED, {
        "number": "72.2b",
        "question": "3.2 × 10⁵ − 6.2 × 10⁴",
        "steps": [
            {"label": "Powers differ", "text": "3.2 is smaller than 6.2, which looks "
                                               "like trouble — but the powers are "
                                               "different, so it isn't."},
            {"label": "Match them", "math": "3.2 × 10⁵ = 32 × 10⁴"},
            {"label": "Subtract", "math": "(32 − 6.2) × 10⁴ = 25.8 × 10⁴"},
            {"label": "Renormalise", "math": "25.8 × 10⁴ = 2.58 × 10⁵"},
        ],
        "answer": "2.58 × 10⁵",
    }),

    (B.KIND_WORKED, {
        "number": "72.3 – 72.4",
        "question": "Multiplying and dividing: split the job",
        "steps": [
            {"label": "(5 × 10⁴)(3 × 10⁻²)",
             "text": "Fronts together, powers together. Multiply the fronts, **add** "
                     "the exponents.",
             "math": "(5)(3) × 10⁴⁺⁽⁻²⁾ = 15 × 10² = 1.5 × 10³"},
            {"label": "(6 × 10⁸)(2 × 10⁷)",
             "math": "12 × 10¹⁵ = 1.2 × 10¹⁶"},
            {"label": "(8 × 10⁴) ÷ (2 × 10⁻²)",
             "text": "Divide the fronts, **subtract** the exponents. Careful: "
                     "4 − (−2) = 6.",
             "math": "4 × 10⁶"},
            {"label": "(6 × 10⁸) ÷ (3 × 10¹¹)",
             "math": "2 × 10⁸⁻¹¹ = 2 × 10⁻³"},
        ],
        "answer": "1.5 × 10³   ·   1.2 × 10¹⁶   ·   4 × 10⁶   ·   2 × 10⁻³",
    }),

    (B.KIND_TABLE, {
        "caption": "Which operation does what to the exponent",
        "headers": ["you are…", "the powers must…", "the exponents…"],
        "rows": [
            {"cells": ["adding", "MATCH first", "stay the same"], "emphasis": True},
            {"cells": ["subtracting", "MATCH first", "stay the same"], "emphasis": True},
            {"cells": ["multiplying", "not matter", "ADD"]},
            {"cells": ["dividing", "not matter", "SUBTRACT"]},
        ],
        "note": "The top two rows are the ones people get wrong. Adding is the fussy "
                "operation here, not multiplying — which is backwards from everything "
                "else in maths, and worth saying out loud.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Why does multiplying ADD the exponents?",
        "answer": "Because `10⁴ × 10²` is `(10 × 10 × 10 × 10) × (10 × 10)` — six tens "
                  "multiplied together, which is `10⁶`. You are just counting how many "
                  "tens there are in total. Dividing cancels them off in pairs, so you "
                  "subtract.",
    }),

    (B.KIND_ERRORS, {
        "title": "The four mistakes almost everyone makes",
        "items": [
            {"name": "Adding the exponents when you are ADDING the numbers.",
             "wrong": "3.2 × 10³ + 4.1 × 10⁴ = 7.3 × 10⁷",
             "right": "0.32 × 10⁴ + 4.1 × 10⁴ = 4.42 × 10⁴",
             "note": "Exponents are added when you **multiply**, never when you add. "
                     "Same shoes first, then add the fronts and leave the power alone."},
            {"name": "Stopping before it is in standard form.",
             "wrong": "15.1 × 10⁵",
             "right": "1.51 × 10⁶",
             "note": "Standard form means **exactly one non-zero digit** before the "
                     "point. Make \"is it dressed properly?\" the last step of every "
                     "single problem."},
            {"name": "Sliding the decimal the wrong way.",
             "wrong": "3.2 × 10³ = 32 × 10⁴",
             "right": "3.2 × 10³ = 32 × 10²   or   0.32 × 10⁴",
             "note": "Check it with the slider above: if the value at the bottom "
                     "changed, you slid the wrong way."},
            {"name": "Sign slips on negative exponents when dividing.",
             "wrong": "(8 × 10⁴) ÷ (2 × 10⁻²) = 4 × 10²",
             "right": "(8 × 10⁴) ÷ (2 × 10⁻²) = 4 × 10⁶",
             "note": "4 − (−2) = 4 + 2 = 6. Subtracting a negative adds. Write the "
                     "subtraction out rather than doing it in your head."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "`× 10ⁿ` says where the decimal point went. Move the point, pay the power.",
            "**Adding or subtracting: match the powers first.** Then add the fronts "
            "and keep the power.",
            "**Multiplying: add the exponents. Dividing: subtract them.** The fronts "
            "are handled separately.",
            "Last step, every time: *is exactly one digit in front of the point?*",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 72 first. If it didn't quite click, this is here to fix "
    "that — and there's a slider to play with. The whole lesson rests on one idea: "
    "the decimal point and the little power of ten pay for each other, so the "
    "value never actually changes."
)

PARENT_CONTENT = """## The big idea

`× 10ⁿ` records **how far the decimal point slid**. Move the point one place left
and the exponent goes up one to compensate; the value is unchanged. Every rule in
the lesson falls out of that.

- **Add / subtract:** make the powers match first, then add the front numbers and
  keep the power. `3.2 × 10³ + 4.1 × 10⁴` → `0.32 × 10⁴ + 4.1 × 10⁴` = **4.42 × 10⁴**
- **Multiply:** multiply the fronts, **add** the exponents. `(5×10⁴)(3×10⁻²)` =
  `15 × 10²` = **1.5 × 10³**
- **Divide:** divide the fronts, **subtract** the exponents. `(8×10⁴)/(2×10⁻²)` =
  **4 × 10⁶** — note `4 − (−2) = 6`.
- **Always finish** by renormalising: `15.1 × 10⁵` = **1.51 × 10⁶**

## Teach it out loud in five minutes

1. Write `3200` and ask her to write it as something-times-a-power-of-ten. Let her
   try a few. `3.2 × 10³`, `32 × 10²`, `0.32 × 10⁴` are all correct — **say so.**
   That surprises most children and it is the key that unlocks the lesson.
2. **"Which one is dressed properly?"** — introduce standard form as a *convention*,
   not a rule from nowhere: one digit in front, so everyone writes it the same way.
3. Now: **"Can I add 3 apples and 4 oranges?"** No. *"Then I can't add 10³ and 10⁴
   either. Make them the same fruit first."*
4. Multiplying: write `10⁴ × 10²` out as tens and count them. She will see the 6.
   Do not give her the rule before she counts.
5. Use the slider on the lesson page for the sliding — it is the one thing that is
   genuinely better on screen than on paper, because the value visibly refuses to
   move.

## The classic mix-ups, with what she'll actually write

- **`3.2 × 10³ + 4.1 × 10⁴ = 7.3 × 10⁷`.** She adds the exponents because that is
  what she just learned to do for multiplication. Name it explicitly: adding is the
  *fussy* operation here, multiplying is the easy one. That is backwards from the
  rest of maths and it is exactly why this trips people.
- **Stopping at `15.1 × 10⁵`.** Right arithmetic, unfinished answer. Saxon marks it
  wrong. Make "is it dressed properly?" a ritual last line.
- **Sliding the wrong way** — `3.2 × 10³` written as `32 × 10⁴`. The slider catches
  this instantly: the value at the bottom changes.
- **`4 − (−2) = 2`.** Sign slip on division. Have her write the subtraction down
  rather than doing it in her head.

## What to watch her do

Whether she **checks the form at the end without being asked.** Everything else in
this lesson is arithmetic she can already do; the renormalise step is the new
habit, and it is the one that decides whether her answers are marked right.

## Extend it

Ask her which is bigger, `4 × 10⁻³` or `9 × 10⁻⁵`, without converting — reading
magnitude straight off the exponent is the real-world payoff of the whole topic.
Then give her the sun's distance and the width of a virus and ask how many viruses
would span it. The answer is absurd, which is the point.

## Where this sits

DIVE Lesson 72. Reviews Lessons 8 (commutative property — why you may shuffle the
factors), 59 and 64 (moving the decimal and what it does to the exponent). If she
is lost on the *sliding* rather than the operations, 59 and 64 are the ones to
revisit.

**Proficient**: gets all four operations right with the rules in front of her.
**Mastered**: renormalises without prompting, and does not have to think about which
operation needs matching powers.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 72 (scientific notation) — idempotent."

    LESSON_NUMBER = 72
    TITLE = "Enormous Numbers Without the Zeros — Scientific Notation"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
