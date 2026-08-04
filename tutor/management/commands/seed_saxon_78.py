"""Saxon Pre-Algebra Lesson 78 — Simplifying More Complex Operations with
Exponents; Evaluating Scientific Formulas.

Reviews Lessons 8, 30, 36, 39, 50, 53, 57 and 62. Two topics on one page, joined
by a single habit: name what you have before you touch anything.

The hinge of 78A is that "simplify" is not a matter of taste — Saxon gives it a
three-line definition, and rule 3 (no VARIABLES in the denominator, numbers are
fine) is the one that surprises people, because it is why every finished answer
here still carries negative exponents.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Practice problems are reworded rather than transcribed wherever the
mathematics allows.

    python manage.py seed_saxon_78 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 78 · Pre-Algebra",
        "title": "Nothing inside the bracket gets to hide",
        "thesis": "A power sitting **outside** a bracket lands on **everything** "
                  "inside it — the number in front, every letter, and whatever is "
                  "underneath. And *simplified* is not a feeling. Saxon wrote down "
                  "exactly what it means.",
        "formula": "( 3xy⁻² / t⁴ )⁻³",
        "roles": [
            {"tone": "start", "name": "the power outside",
             "text": "It reaches every single item in the bracket. No exceptions, "
                     "not even the plain number in front."},
            {"tone": "move", "name": "multiply, don't add",
             "text": "A power of a power multiplies the exponents. −2 × 12 is −24."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone bothers with either half of this",
        "paragraphs": [
            "Hand the same messy expression to two people and ask them to tidy it. "
            "You can easily get two answers that look nothing alike and are both "
            "correct. That is unbearable for whoever has to mark it. So Saxon does "
            "not leave *simplify* up to taste — it writes down exactly what a "
            "finished answer looks like, and finished means **that**, every time.",
            "The second half of the page is the reason any of this exists at all. A "
            "scientific formula is a sentence somebody discovered about the world: "
            "how far you get, how heavy a lump of gold is, how long a drive takes. "
            "It ties a few facts together, and it lets you work out the one you "
            "*don't* have from the ones you do.",
            "So the whole lesson is one question asked twice: **what have I got, and "
            "what is the blank?** Answer that first and both halves turn into "
            "routine.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "\"Simplified\" is a place, not a feeling",
        "paragraphs": [
            "When a problem says *simplify*, it sounds like it is asking you to make "
            "the thing look nicer. It isn't. It is asking you to get it into one "
            "particular shape — and Saxon tells you which shape, in three lines.",
            "That matters more than it sounds. Almost everyone who loses marks on "
            "this section does the algebra correctly and then **stops one step "
            "early**. Learn the three checks and run them at the end of every "
            "problem, and you stop guessing whether you are done.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"See this little −3 hanging outside the bracket? Everything inside "
                "the bracket has to answer to it. Nothing gets to hide — not the 3 "
                "out front, not the letter with nothing written on it. Point at each "
                "thing in there and tell me its exponent. If you can't see one, "
                "it's a 1.\"",
    }),

    (B.KIND_STEPS, {
        "tag": "Saxon's definition", "title": "What \"simplify\" is allowed to mean",
        "steps": [
            {"label": "No parentheses.",
             "detail": "Every bracket has been used up and spent. If you can still "
                       "see one, you are not finished — no matter how tidy the rest "
                       "looks."},
            {"label": "Any NUMBER raised to a power gets worked out.",
             "detail": "`3³` is not an answer; **27** is. This applies to numbers "
                       "only. `x³` stays as `x³`, because there is nothing to work "
                       "out until somebody tells you what x is."},
            {"label": "No variables in the denominator — only numbers.",
             "detail": "A **letter** underneath comes upstairs, and its exponent "
                       "flips sign on the way. A plain **number** underneath, like "
                       "27, is perfectly welcome to stay where it is."},
        ],
        "after": "Rule 3 is the one that surprises people, so say it out loud: for "
                 "this lesson `x⁻³` sitting upstairs **is** simplified, and `1/x³` "
                 "**is not**. That is the whole reason the finished answers below "
                 "are full of minus signs.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "The power outside touches everything inside",
        "paragraphs": [
            "Picture the bracket as a bag. In `(3xy⁻²/t⁴)⁻³` the −3 is stamped on "
            "the **outside** of the bag, and the stamp reaches every single thing "
            "inside it. Nothing in the bag sits that out — not the 3, not the x, not "
            "the `t⁴` underneath.",
            "For each item in the bag you **multiply** its exponent by the outside "
            "power. Everything already has an exponent even when you cannot see one: "
            "a bare `3` is `3¹`, a bare `x` is `x¹`. Write those 1s in with a pencil "
            "until you stop needing to.",
            "Two special guests turn up. `2⁰` is 1 — anything except zero, raised to "
            "the zero power, is 1 — so it is a multiplier of 1 and it quietly leaves. "
            "And `√x` is `x` carrying an exponent of one half, which is why `(√x)²` "
            "collapses straight back to `x`: one half times two is one, and we never "
            "write an exponent of 1.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "78.1",
        "question": "Use the power rule to simplify   (2⁰x⁻²y⁴/z)¹²   and   "
                    "(3xy⁻²/t⁴)⁻³",
        "steps": [
            {"label": "a) deal with the zero power first",
             "text": "Anything except zero, raised to the 0 power, equals 1 — so "
                     "`2⁰` is 1. Multiplying by 1 changes nothing, so it just walks "
                     "off the page. It does **not** turn the expression into zero."},
            {"label": "a) now send the 12 to every exponent",
             "text": "x has −2, so −2 × 12 = −24. y has 4, so 4 × 12 = 48. The z "
                     "underneath has an invisible 1, so 1 × 12 = 12 — and then rule 3 "
                     "sends it upstairs as −12, because a letter is not allowed to "
                     "stay in the denominator.",
             "math": "(2⁰x⁻²y⁴/z)¹² = (x⁻²y⁴/z)¹² = x⁻²⁴y⁴⁸/z¹² = x⁻²⁴y⁴⁸z⁻¹²"},
            {"label": "b) find the invisible 1s before you start",
             "text": "In `(3xy⁻²/t⁴)⁻³` the 3 is really `3¹` and the x is really "
                     "`x¹`. The 3 is inside the bracket, so the −3 lands on it too. "
                     "This is the step that gets skipped."},
            {"label": "b) multiply, then tidy up under the definition",
             "text": "1 × (−3) = −3 for both the 3 and the x. y has −2, and "
                     "−2 × (−3) = +6. t has 4, and 4 × (−3) = −12. Then `t⁻¹²` "
                     "underneath comes upstairs as `t¹²`, and `3⁻³` upstairs goes "
                     "downstairs as `3³` — which is a **number** raised to a power, "
                     "so rule 2 says work it out.",
             "math": "(3xy⁻²/t⁴)⁻³ = 3⁻³x⁻³y⁶/t⁻¹² = t¹²x⁻³y⁶/3³ = t¹²x⁻³y⁶/27"},
        ],
        "answer": "x⁻²⁴y⁴⁸z⁻¹²   ·   t¹²x⁻³y⁶/27",
    }),

    (B.KIND_WORKED, {
        "number": "78.2",
        "question": "Use the power rule to simplify   (3√x)²   and   (3x^(1/3))²",
        "steps": [
            {"label": "a) turn the root into an exponent",
             "text": "From Lesson 30, the square-root sign is shorthand for the "
                     "one-half power: `√x` is `x^(1/2)`. Rewriting it that way is the "
                     "whole trick — once it is an exponent, the ordinary rule works."},
            {"label": "a) multiply both exponents by the outside 2",
             "text": "The 3 has an invisible 1, and 1 × 2 = 2, so the 3 becomes `3²` "
                     "— a number raised to a power, so rule 2 says work it out: 9. "
                     "The x has 1/2, and (1/2) × 2 = 1, and an exponent of 1 is never "
                     "written. So x comes back plain.",
             "math": "(3√x)² = (3x^(1/2))² = 3²x¹ = 9x"},
            {"label": "b) same move, different fraction",
             "text": "This time the variable carries a one-third power. Nothing else "
                     "changes: the outside 2 still multiplies every exponent inside. "
                     "**One honest note:** your book prints part b as a picture, and "
                     "that picture did not come through when this page was made. It is "
                     "written here as `(3x^(1/3))²` to match part a. Check your book — "
                     "if there is no 3 in front, your answer is `x^(2/3)` with no 9. "
                     "The method is identical either way; only the 9 changes."},
            {"label": "b) a fraction in the exponent is a finished answer",
             "text": "2 × (1/3) = 2/3. It does not tidy into a whole number, and it "
                     "is not supposed to — leave it as 2/3. The 3 out front still "
                     "becomes 9.",
             "math": "(3x^(1/3))² = 3²x^(2/3) = 9x^(2/3)"},
        ],
        "answer": "9x   ·   9x^(2/3)",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand on this page, decoded",
        "intro": "None of these are new rules. They are compressed ways of writing "
                 "things you already know, and the compression is what makes the "
                 "page look harder than it is.",
        "rows": [
            {"symbol": "3x", "plain": "3¹x¹ — everything has an exponent, "
                                      "you just can't see the 1s",
             "example": "(3x)⁻³ → 3⁻³x⁻³"},
            {"symbol": "2⁰", "plain": "anything except 0, to the zero power, is 1",
             "example": "it multiplies by 1, so it disappears"},
            {"symbol": "x⁻²", "plain": "a note about which floor, not a negative "
                                       "number",
             "example": "x⁻² with x = 2 is 1/4"},
            {"symbol": "1/t⁻¹²", "plain": "a negative exponent downstairs comes "
                                          "upstairs positive",
             "example": "1/t⁻¹² → t¹²"},
            {"symbol": "√x", "plain": "shorthand for the ½ power (Lesson 30)",
             "example": "(√x)² → x"},
            {"symbol": "x^(1/3)", "plain": "the ⅓ power — the cube root, written as "
                                           "an exponent",
             "example": "(x^(1/3))² → x^(2/3)"},
        ],
        "after": "The one to say out loud: **a negative exponent is not a negative "
                 "number.** `x⁻³` is not below zero. Put x = 2 in and you get 1/8 — "
                 "small, but very much positive.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "A formula is a sentence with one blank in it",
        "paragraphs": [
            "`d = rt` says: how far you went equals how fast you were going, times "
            "how long you went for. Three facts, one sentence. Whoever wrote it down "
            "was not being clever — they were writing down something true about "
            "driving.",
            "A problem hands you all but one of the facts and asks for the missing "
            "one. So step zero, every single time: **write down what you have, and "
            "circle what you want.** Most of the difficulty in these problems is "
            "people starting to calculate before they have done that.",
            "Then you get a choice. Either **rearrange first** — get the letter you "
            "want alone, then put the numbers in — or **substitute first** and sort "
            "out the algebra afterwards. Saxon does one of each in this lesson on "
            "purpose. Neither is more correct. One is usually less work.",
        ],
    }),

    (B.KIND_STEPPER, {
        "title": "Example 78.3 — how long does 400 miles at 60 mph take?",
        "equation": "d = r t          d = 400 miles,   r = 60 mph,   t = ?",
        "steps": [
            {"label": "Look first",
             "text": "Three letters, and you have been handed two of them. `d` is "
                     "distance, `r` is rate — which is just the word for speed — and "
                     "`t` is time. **The blank is t.** Say that out loud before you "
                     "write anything."},
            {"label": "Step 1 · get t on its own",
             "text": "In `d = rt`, the t is tied to r by multiplication. You undo "
                     "multiplication by dividing — and whatever you do to one side "
                     "you must do to the other, or it stops being a true sentence.",
             "math": "d / r = r t / r  →  d / r = t"},
            {"label": "Step 2 · turn it round",
             "text": "`d/r = t` and `t = d/r` say exactly the same thing. Saxon "
                     "writes the unknown on the left because it reads better and it "
                     "is easier to spot. **That is the only reason.** It is not a "
                     "step in the maths. You have done this flip before: it is the "
                     "same move you made in Lesson 50 building the Celsius formula.",
             "math": "t = d / r"},
            {"label": "Step 3 · now the numbers go in",
             "text": "Now, and not before. Miles on the top, miles-per-hour "
                     "underneath — the miles cancel and hours are what is left, "
                     "which is exactly the unit the question asked for.",
             "math": "t = 400 / 60 = 40 / 6"},
            {"label": "Step 4 · round to what was asked",
             "text": "Divide it out and you get 6.666… hours. The question says one "
                     "decimal place, so the second 6 rounds the first one up to 7. "
                     "Sanity check: 60 miles an hour for 6 hours is 360 miles, so a "
                     "bit over 6 hours is exactly right for 400.",
             "math": "t ≈ 6.7 hours"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "78.4",
        "question": "Gold has a density of 19.3 g/mL. Using M₁/V₁ = M₂/V₂, find the "
                    "mass M₂ of 50 mL of gold.",
        "steps": [
            {"label": "What density actually is",
             "text": "Density compares how much **stuff** there is (mass) to how much "
                     "**room** it takes up (volume). Ice floats on water not because "
                     "ice is light — a great slab of it still floats — but because "
                     "its mass compared with its volume is smaller than water's. "
                     "Weight alone is not what decides it."},
            {"label": "Write the given density as a fraction, with the invisible 1",
             "text": "\"19.3 g/mL\" means 19.3 grams for every **1** millilitre. "
                     "Write that 1 down. It is the number everyone forgets, and "
                     "forgetting it turns a multiplication into a division.",
             "math": "M₁ / V₁ = 19.3 / 1"},
            {"label": "Substitute, then cross-multiply",
             "text": "Here the numbers go in **first** and the rearranging comes "
                     "second — the opposite order from 78.3. Cross-multiplying a "
                     "proportion is Lesson 53: top-left times bottom-right equals "
                     "bottom-left times top-right.",
             "math": "19.3 / 1 = M₂ / 50  →  M₂ × 1 = 19.3 × 50"},
            {"label": "Finish, and check the units",
             "text": "The millilitres cancel and grams are left, which is what a mass "
                     "should be measured in. Worth a glance: 50 mL of gold weighing "
                     "just under a kilogram sounds about right for a metal that "
                     "heavy.",
             "math": "M₂ = 19.3 × 50 = 965 g"},
            {"label": "Saxon's footnote — the same formula asked backwards",
             "text": "Suppose you were handed the mass and asked for the **volume** "
                     "instead. You would still cross-multiply, and it would still give "
                     "you `M₁V₂ = M₂V₁`. The only difference is what you do next: "
                     "divide both sides by `M₁` to get `V₂` on its own. Same formula, "
                     "same cross-multiply, one extra division. Keep that in your "
                     "pocket — the problem at the bottom of this page is exactly it."},
        ],
        "answer": "965 g",
    }),

    (B.KIND_TABLE, {
        "caption": "Same job, two orders — and both are correct",
        "headers": ["", "Rearrange first (78.3)", "Substitute first (78.4)"],
        "rows": [
            {"cells": ["Step 1", "divide both sides by r",
                       "put 19.3, 1 and 50 into the formula"]},
            {"cells": ["Step 2", "t = d/r", "cross-multiply: M₂ × 1 = 19.3 × 50"]},
            {"cells": ["Step 3", "put 400 and 60 in", "read the answer off: 965 g"]},
            {"cells": ["Easier when…", "the letter comes free in one clean move",
                       "the numbers land in a proportion you can cross-multiply"],
             "emphasis": True},
        ],
        "note": "Saxon shows both on purpose. If you always rearrange first you will "
                "meet a formula where it is horrible; if you always substitute first "
                "you will meet one where the letters won't come apart afterwards. "
                "**Look at the formula and pick.**",
    }),

    (B.KIND_MATH, {
        "display": "(a xᵐ yⁿ / zᵖ)ᵏ  =  aᵏ xᵐᵏ yⁿᵏ z⁻ᵖᵏ",
        "note": "The whole of 78A on one line. The `k` outside reaches the number `a`, "
                "every letter, and the one underneath — and the one underneath comes "
                "upstairs with its sign flipped, because rule 3 says nothing carrying "
                "a letter may stay in the denominator. The only thing left to do "
                "after that is rule 2: work out `aᵏ`, because it is a number.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Your turn. Aluminium has a density of 2.7 g/mL. What volume does "
                  "45 g of aluminium take up? Round to 1 decimal place.",
        "answer": "**16.7 mL.** Set it up the same way as 78.4, remembering the "
                  "invisible 1: `2.7/1 = 45/V₂`. Cross-multiply and you get "
                  "`2.7 × V₂ = 45`, so `V₂ = 45 ÷ 2.7 = 16.666…`, which rounds to "
                  "**16.7 mL**.\n\nNotice this one asks for the *bottom* of the "
                  "fraction rather than the top, so after cross-multiplying you have "
                  "to divide — that is Saxon's footnote from 78.4.\n\nSanity check: "
                  "aluminium is about 2.7 times as dense as water. 45 g of *water* "
                  "would fill 45 mL, so the same mass of aluminium has to fit in "
                  "roughly a third of that room — somewhere near 17 mL. That is what "
                  "we got. If you had come out with 121.5 mL, which is 45 × 2.7, you "
                  "multiplied where you needed to divide.\n\nThen do problem 5 in your "
                  "practice set on your own. It is this exact shape with copper.",
    }),

    (B.KIND_ERRORS, {
        "title": "The seven mistakes almost everyone makes",
        "items": [
            {"name": "Letting 2⁰ wipe out the expression.",
             "wrong": "(2⁰x⁻²y⁴/z)¹² → the 2⁰ is 0, so the whole answer is 0",
             "right": "(2⁰x⁻²y⁴/z)¹² → (x⁻²y⁴/z)¹² because 2⁰ is 1",
             "note": "Anything except zero, raised to the zero power, is **1**. It is "
                     "a multiplier of 1, so it disappears quietly — it does not take "
                     "the rest of the problem with it."},
            {"name": "Powering the letters and forgetting the number in front.",
             "wrong": "(3xy⁻²/t⁴)⁻³ = 3x⁻³y⁶/t⁻¹² → 3t¹²x⁻³y⁶",
             "right": "(3xy⁻²/t⁴)⁻³ = 3⁻³x⁻³y⁶/t⁻¹² → t¹²x⁻³y⁶/27",
             "note": "The 3 is **inside** the bracket, so the outside power lands on "
                     "it exactly like everything else. Its invisible exponent is 1, "
                     "and 1 × (−3) = −3. Getting 3 on top instead of 27 underneath is "
                     "off by a factor of 81."},
            {"name": "Adding the exponents instead of multiplying them.",
             "wrong": "(x⁻²)¹² = x¹⁰",
             "right": "(x⁻²)¹² = x⁻²⁴",
             "note": "A power **of** a power multiplies. You add exponents when you "
                     "multiply two separate powers together — a different job that "
                     "looks similar on the page. −2 × 12 = −24."},
            {"name": "Reading a negative exponent as a negative number.",
             "wrong": "x⁻³ with x = 2 → −8",
             "right": "x⁻³ with x = 2 → 1/8",
             "note": "The minus is about **which floor** the term wants to live on, "
                     "not about being below zero. `x⁻³` is a small positive number "
                     "whenever x is positive."},
            {"name": "Stopping before rule 2 is done.",
             "wrong": "t¹²x⁻³y⁶/3³",
             "right": "t¹²x⁻³y⁶/27",
             "note": "Correct algebra, unfinished answer — and Saxon marks it wrong. "
                     "If it is a **number** raised to a power, work it out: "
                     "3 × 3 × 3 = 27. Letters keep their powers; numbers do not."},
            {"name": "Undoing a multiplication by multiplying again.",
             "wrong": "400 = 60t  →  t = 400 × 60 = 24,000 hours",
             "right": "400 = 60t  →  t = 400 / 60 = 40 / 6  →  t ≈ 6.7 hours",
             "note": "Whatever is tied to t by multiplication comes off by "
                     "**division**. Say it out loud: *sixty times what is four "
                     "hundred?* Nobody would answer twenty-four thousand — but the "
                     "symbols hide it, which is why the sentence version is worth "
                     "saying. Note what is **not** the mistake here: putting the "
                     "numbers in first is perfectly allowed, and 78.4 does exactly "
                     "that."},
            {"name": "Forgetting the invisible 1 under the density.",
             "wrong": "M₂ = 19.3 / 50 = 0.386 g",
             "right": "M₂ = 19.3 × 50 = 965 g",
             "note": "19.3 g/mL is 19.3 grams per **1** millilitre. Write the 1 and "
                     "cross-multiplying gives `M₂ × 1` on one side. Then ask the "
                     "sanity question: should 50 mL of gold weigh more or less than "
                     "1 mL? More — so the answer has to be bigger than 19.3, and "
                     "0.386 is obviously not."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A power outside a bracket lands on **everything** inside — the number "
            "in front, every letter, and whatever is underneath.",
            "Power of a power: **multiply** the exponents. `(x⁻²)¹² = x⁻²⁴`.",
            "Everything has an exponent. If you cannot see one, it is a **1**. "
            "`2⁰` is 1 and leaves; `√x` is the ½ power.",
            "**Simplified has a definition:** no parentheses, numbers raised to "
            "powers actually worked out, no variables in the denominator. Run all "
            "three at the end of every problem.",
            "A negative exponent is a note about which floor, not a negative number.",
            "For a formula: write what you have, circle the blank, then either "
            "isolate it first or substitute first. Both are allowed — pick the one "
            "that is less work.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 78 first. If it didn't quite click, this is here to fix "
    "that — there's a stepper you can click through one beat at a time, and a "
    "problem to try yourself at the bottom. Two things live on this page: what "
    "\"simplify\" actually means when there are exponents everywhere, and how to "
    "get a real number out of a science formula."
)

PARENT_CONTENT = """## The big idea

Two topics share this lesson, and the join between them is one habit: **say what
you have got before you touch anything.**

**78A — exponents.** A power sitting outside a bracket lands on *everything*
inside: the number in front, every letter, and whatever is underneath. For each
one you **multiply** its exponent by the outside power. Anything with no visible
exponent is carrying a 1.

`(3xy⁻²/t⁴)⁻³` → `3⁻³x⁻³y⁶/t⁻¹²` → **`t¹²x⁻³y⁶/27`**

Then Saxon's definition of *simplified*. This is a numbered rule, not a matter of
taste, and she should be able to recite it:

1. **No parentheses.**
2. **Any number raised to a power gets worked out** — `3³` becomes `27`. Numbers
   only; `x³` stays as `x³`.
3. **No variables in the denominator** — only numbers.

Rule 3 is the counter-intuitive one, and it is worth stating plainly: it is why
every finished answer here still carries minus signs in the exponents. `x⁻³`
upstairs **is** simplified. `1/x³` **is not**. Meanwhile a plain number like 27
downstairs is fine, because 27 is not a variable.

**78B — scientific formulas.** `d = rt`, or density `M₁/V₁ = M₂/V₂`. You are
handed all but one of the facts and asked for the missing one. Two orders are
allowed, and the lesson deliberately shows one of each: **rearrange first**
(78.3 — divide by r, get `t = d/r`, then put the numbers in) or **substitute
first** (78.4 — put the numbers in, then cross-multiply).

## Two things to check against the printed book

**Example 78.2b.** The DIVE guide prints both parts of 78.2 as images, and the
text that survives pins only the outside power (2) and the resulting exponent
(2/3) — *"2(1/3)=2/3"*. It does **not** pin the coefficient. Part a is safe
(`3²x¹ = 9x` forces `(3√x)²`), so this page writes b as `(3x^(1/3))²` to match,
giving `9x^(2/3)`. If your book shows no 3 in front of part b, the answer is
`x^(2/3)` and the 9 is ours, not Saxon's. Her page says so too, in her own words
— she is told to check, not told to trust us.

**The problem at the bottom of her page** is aluminium, not the copper in her
practice set. That is deliberate: practice problem 5 is the same shape, and
working it here would have handed her the answer. She should do the aluminium one
on the page and then problem 5 on her own paper.

## Teach it out loud in five minutes

Say these in this order, and ask the question at each step. Paper and pencil, not
the screen — the screen is for afterwards.

1. Write `(3x)²` and put your finger on the bracket. **"How many things are
   inside this bag?"** — you want *"two: a 3 and an x."* Then: *"That little 2
   outside applies to both of them. Nothing hides."* Write `3²x²`, then ask
   **"which one can I actually work out?"** — the number. `9x²`.
2. Write `(x⁻²)¹²`. **"Do I add these or multiply them?"** She will probably say
   add. Don't correct it yet — write `x⁻²` out as *x squared, upside down*, then
   ask her to imagine twelve of those multiplied together. She will get to −24
   herself, and then the rule is hers instead of yours.
3. Write `2⁰` on its own. **"What's that worth?"** Most children say 0 or 2. It
   is **1**. Then: *"So in a big problem it multiplies by one and walks away. It
   doesn't wreck anything."*
4. Now the three rules. Read them out, then hand her `t¹²x⁻³y⁶/3³` and ask
   **"is this finished?"** — the answer is no, rule 2, the `3³` has to become 27.
   That single question is most of the marks in this section.
5. Switch topics. Say **"forty miles an hour for three hours — how far?"** She
   will say 120 without thinking. *"You just used d = rt. That's the whole
   formula."* Then flip it: *"Four hundred miles at sixty. How long?"* and ask
   **"which letter is the blank?"** Do not let her calculate until she has said
   "t" out loud.

## The classic mix-ups, with the exact wrong answer each one produces

- **`2⁰` treated as 0**, so the whole expression collapses to **0**. It is 1, and
  it disappears by multiplying, not by destroying.
- **The number in front left un-powered:** `(3xy⁻²/t⁴)⁻³` written as
  `3x⁻³y⁶/t⁻¹²`, landing on **`3t¹²x⁻³y⁶`** instead of **`t¹²x⁻³y⁶/27`**. That is
  off by a factor of 81. The 3 is inside the bracket; it pays like everyone else.
- **Exponents added instead of multiplied:** `(x⁻²)¹²` written as **`x¹⁰`**
  instead of `x⁻²⁴`. Adding is for multiplying two separate powers — a different
  job that looks the same on the page.
- **A negative exponent read as a negative number:** `x⁻³` with x = 2 answered as
  **−8** instead of **1/8**. Ask her which floor it lives on, not what sign it is.
- **Stopping at `3³`:** answer left as **`t¹²x⁻³y⁶/3³`**. Right algebra, wrong
  form, no marks. Rule 2.
- **Undoing a multiplication by multiplying again:** `400 = 60t` turned into
  **`t = 400 × 60 = 24,000 hours`**. Multiplication comes off by division. Be
  careful how you name this one to her: substituting the numbers in first is
  *not* the error — Saxon does it on purpose in 78.4. The error is the operation.
- **The invisible 1 in the density dropped:** `M₂ = 19.3 ÷ 50 = **0.386 g**`
  instead of `19.3 × 50 = **965 g**`. 19.3 g/mL means 19.3 grams per *one*
  millilitre — the 1 has to be written down before cross-multiplying.

## What to watch her do

Watch her **hands**, not her answer.

On 78A: does her pencil physically touch every item inside the bracket before she
writes the next line? The children who get these right point at each term in turn
— 3, x, y, t — and the ones who don't sweep their eyes over the letters and miss
the number in front. If she isn't pointing, make her point.

Then watch whether she **writes the invisible 1s in**. `3¹x¹`, and the `1` under
`19.3`. Writing them is the fix for four of the seven mistakes above, and it costs
two seconds. Children resist because it looks babyish; the answer to that is that
it is what people who are fast at this actually do.

On 78B: watch whether she writes down what she was given and circles the unknown
*before* she starts calculating. If the first mark on her paper is a number being
divided, she has skipped the step that makes the rest work.

And at the end of every 78A problem, does she go back and check the three rules
without being asked? That habit is the whole lesson.

## Extend it

Give her `(2x³/y)⁰` and let her stare at it. The answer is **1** — the entire bag
is raised to the zero power, and anything *except zero* raised to the zero power
is 1. (Worth saying the caveat out loud, because the page is scrupulous about it
everywhere else: the bracket itself has to be nonzero, which here means x ≠ 0.)
It is a fair question and it is a lovely moment.

Then hand her the density formula backwards: *"a gold ring displaces 0.5 mL of
water. What does it weigh?"* Same formula, but she has to notice which slot the
0.5 goes in. The answer is `19.3 × 0.5 =` **9.65 g** — a shade under the mass of
two US nickels, which are 5 g each. Real problems arrive in the wrong order like
that.

If she wants the science half to mean something: look up the density of water
(1 g/mL) and of ice (about 0.92), and let her explain, out loud, why ice floats.
Saxon's example is doing real work there — it is not decoration.

## Where this sits

**DIVE Lecture 78.** Reviews Lessons 8, 30, 36, 39, 50, 53, 57 and 62. If she is
lost on the **exponent** half, Lesson 57 is the one to revisit — 78A is explicitly
built on 57B's definition of "simplify". If she is lost on the **formula** half,
go back to 39 (isolating a variable) and 53 (cross-multiplying a proportion),
which are the two mechanical skills the second half assumes.

**Proficient** looks like: simplifies a bracket correctly with the three rules
written in front of her, and evaluates `d = rt` for any of the three letters.
**Mastered** looks like: writes the invisible 1s without being told, checks the
three rules unprompted, and can say *why* `t⁻¹²` underneath becomes `t¹²` on top.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 78 (complex exponent operations; "
            "evaluating scientific formulas) — idempotent.")

    LESSON_NUMBER = 78
    TITLE = ("Nothing Inside the Bracket Gets to Hide — Complex Exponents and "
             "Scientific Formulas")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
