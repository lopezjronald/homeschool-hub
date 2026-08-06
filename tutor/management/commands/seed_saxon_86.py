"""Saxon Pre-Algebra Lesson 86 — Trigonometry Basics.

Reviews Lessons 53, 54 and 78. Lesson 54 is the hook: she already knows the
hypotenuse (the side across from the right angle, and the longest one) from the
Pythagorean Theorem. Lesson 53 supplies the engine — similar triangles are
proportional — which is the whole reason a *ratio* can belong to an angle instead
of to a triangle. Lesson 78 is the mechanics: rearranging a formula to isolate the
unknown, which is all Ex. 86.2 actually asks.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Parts of the guide arrive as images rather than text, and they are
not all the same kind of thing:

* Page 1's three 30-60-90 triangles are a genuine diagram, and so is practice
  problem 386's clinometer sketch. Neither can be reproduced here. The three
  triangles are rebuilt below as a table of real side lengths (1-1.732-2,
  2-3.464-4, 5-8.66-10 — the same shape at three scales, so the ratios come out
  identical exactly as the book claims).
* Ex. 86.2 and practice problem 286 are different. What is missing there is the
  typeset EQUATIONS, not a picture of a triangle: the source prints a bare "a)"
  and "b)" with a gap, and the printed solution is pure algebra that mentions no
  figure at all. Ex. 86.2's two equations are reconstructed from the guide's own
  solution lines — `x(sin 37°) = 10(1)` and `h(1) = 50(tan 42°)` — and written
  out in full, and her page says plainly that this is what happened.

    python manage.py seed_saxon_86 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 86 · Pre-Algebra",
        "title": "Trigonometry basics — three ratios, one angle",
        "thesis": "For such a big word, trigonometry is really just about the "
                  "**ratios of the three sides of a right triangle**, named from "
                  "the angle you are standing at. Three ratios. That is the lesson.",
        "formula": "sin θ = opp / hyp    ·    cos θ = adj / hyp    ·    tan θ = opp / adj",
        "roles": [
            {"tone": "start", "name": "hypotenuse — the side that never moves",
             "text": "The side across from the right angle. It is also the longest "
                     "side. It is the hypotenuse no matter which corner you stand "
                     "in, so it is the one you find first."},
            {"tone": "move", "name": "opposite and adjacent — the two that do move",
             "text": "Opposite means across the triangle from you. Adjacent means "
                     "the one you are touching. Move to the other angle and those "
                     "two labels trade places."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone bothers: measuring a thing you cannot reach",
        "paragraphs": [
            "There is a tree in your yard and you want to know how tall it is. You "
            "cannot climb it with a tape measure. You cannot lean a ruler against "
            "the sky.",
            "But you *can* walk 50 metres away from it and measure two things: how "
            "far you walked, and the angle you have to tilt your head to look at the "
            "top. Those two numbers are enough. The tree's height falls out of them.",
            "That is what this lesson buys you. **One angle plus one side gives you "
            "every other side of a right triangle.** An architect uses it to work out "
            "a roof. An oceanographer uses it on the pattern of the tides. Kaylin "
            "uses it on a tree in Example 86.3.",
            "And the reason it works is something you already learned. In **Lesson "
            "53** you found that similar triangles are proportional to each other. "
            "Two triangles with the same three angles have the same ratios between "
            "their sides, whatever size they are. So the ratio does not really belong "
            "to the triangle at all — **it belongs to the angle**. That is why a "
            "calculator can have a `sin` button: one angle in, one number out, no "
            "triangle required.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Three sides, and only one of them has a fixed name",
        "paragraphs": [
            "A right triangle has one square corner — the 90° one — and two other "
            "angles that are smaller.",
            "**Hypotenuse** is the one name that is nailed down. From **Lesson 54**: "
            "in a right triangle it is the side opposite the right angle, and it is "
            "also the longest side. Two ways to find it, and they always agree. Find "
            "the little square, look straight across from it, and that side is the "
            "hypotenuse — for the rest of the problem, no matter what else happens.",
            "The other two sides are called **legs**, and their names are not fixed. "
            "One of them is *opposite*, one of them is *adjacent* — but which is "
            "which depends on where you are standing.",
            "That is why the book keeps writing **θ** (the Greek letter theta). θ is "
            "not a number you have to find. It is a name for **the angle you are "
            "standing at**, and it is what makes \"opposite\" mean anything at all.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Pick a corner of the triangle — not the square one, one of the "
                "other two — and stand in it. Now, one side is across the room from "
                "you: that's the opposite. One side you're touching: that's the "
                "adjacent. And the long one across from the square corner is the "
                "hypotenuse, and it doesn't care where you stand. Now walk over to "
                "the other corner and tell me what changed.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "Opposite and adjacent are addresses, not names",
        "paragraphs": [
            "Here is the part a picture in a book cannot show you, because a picture "
            "only ever shows one version.",
            "Take one right triangle and stand at the smaller acute angle. The short "
            "leg is across the triangle from you, so it is the **opposite**. The long "
            "leg is under your feet, so it is the **adjacent**.",
            "Now walk to the *other* acute angle without changing the triangle at "
            "all. The short leg is now the one you are touching — it just became the "
            "**adjacent**. The long leg is now across from you — it just became the "
            "**opposite**. Nothing about the triangle moved. Only you did.",
            "The hypotenuse did not budge, because it is defined from the right "
            "angle and you never stood there.",
            "There is a tidy check on this: the two acute angles of a right triangle "
            "always add to 90°, so if one is 30° the other is 60°. Standing at 60° "
            "instead of 30° is the swap. The tool further down this page lets you "
            "press a button and watch the two words trade places.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "Same angle, any size, same ratio",
        "paragraphs": [
            "Page 1 of your lesson shows three right triangles of three different "
            "sizes. All three have the same three angles: **30°, 60° and 90°**. By "
            "Lesson 53 that makes them **similar**, and similar triangles are "
            "proportional.",
            "So look at what `sin 30°` is actually asking for. It says: *find the "
            "ratio between the side opposite the 30° angle and the hypotenuse.* Do "
            "that for the small triangle, then the medium one, then the big one.",
            "You get the same number every time. Not close — the same. That is what "
            "the table below shows, with real side lengths standing in for the "
            "book's three pictures.",
            "This is the whole reason trigonometry exists as a subject rather than a "
            "pile of triangles. **The ratio is a property of the angle.** Ask a "
            "different question about a 30° angle and you always get 0.5, so somebody "
            "was able to write all those answers down once, and now they live in your "
            "calculator.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Three 30-60-90 triangles, three different sizes — rebuilt with "
                   "real numbers, because the book's three pictures cannot be "
                   "reprinted here",
        "headers": ["triangle", "opposite the 30°", "adjacent", "hypotenuse",
                    "opp ÷ hyp"],
        "rows": [
            {"cells": ["small", "1", "1.732", "2", "1 ÷ 2 = 0.5"]},
            {"cells": ["medium", "2", "3.464", "4", "2 ÷ 4 = 0.5"]},
            {"cells": ["large", "5", "8.66", "10", "5 ÷ 10 = 0.5"], "emphasis": True},
            {"cells": ["your calculator", "—", "—", "—", "sin 30° = 0.5"],
             "emphasis": True},
        ],
        "note": "Every row is a different-sized triangle and every row gives the same "
                "0.5. The other two ratios behave the same way: **adj ÷ hyp** comes "
                "out 0.866 in all three (1.732 ÷ 2, 3.464 ÷ 4, 8.66 ÷ 10) and "
                "**opp ÷ adj** comes out 0.577 in all three (1 ÷ 1.732, 2 ÷ 3.464, "
                "5 ÷ 8.66). Those are exactly the numbers your lesson tells you to "
                "expect for cos 30° and tan 30°. Check all three on the calculator — "
                "the book asks you to, and it is worth doing once so you believe it.",
    }),

    (B.KIND_MATH, {
        "display": "sin 30° :   1/2 = 2/4 = 5/10 = 0.5",
        "note": "Three different triangles, three different pairs of numbers, one "
                "answer. `sin 30°` is shorthand for **\"the ratio of the side "
                "opposite the 30° angle to the hypotenuse\"** — twelve words, and it "
                "is the same 0.5 for every right triangle in the world that has a 30° "
                "angle in it.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Five moves, the same way every time",
        "steps": [
            {"label": "Find the right angle and mark the hypotenuse.",
             "detail": "The little square marks the 90° corner. The side straight "
                       "across from it is the hypotenuse. Write **hyp** on it. Do "
                       "this before anything else — it is the one label that will "
                       "not change on you, so it costs nothing to commit to."},
            {"label": "Stand at the angle the problem gives you, and label the "
                      "other two sides from there.",
             "detail": "The leg across the triangle from that angle is **opp**. The "
                       "leg you are touching is **adj**. Write those on the picture "
                       "too. If the problem later mentions a different angle, you "
                       "re-label — that is normal, not a mistake."},
            {"label": "Cross out the side nobody mentioned.",
             "detail": "A problem gives you one side and asks for one side. That is "
                       "two sides, and the third is dead weight. The **two sides "
                       "left standing choose the function for you**: opp and hyp → "
                       "sine, adj and hyp → cosine, opp and adj → tangent."},
            {"label": "Write the ratio, then rearrange it — Lesson 78 and Lesson 39.",
             "detail": "Give the lone trig value the invisible **1** underneath it so "
                       "both sides are fractions, cross-multiply, then divide to get "
                       "the unknown on its own. No new algebra. This is the same move "
                       "you made on scientific formulas."},
            {"label": "Only now reach for the calculator — and check it is in DEGREES.",
             "detail": "Type `sin`, then `30`. If you get **0.5** you are in degree "
                       "mode and you are fine. If you get about **-0.988** you are in "
                       "radian mode and every answer today will be wrong. Keep **3 or "
                       "4 decimal places** of the trig value, do the arithmetic, and "
                       "round only at the very end."},
        ],
        "after": "One promise from the book that will save you an argument with the "
                 "answer key: on trig problems your rounded answer may come out "
                 "**slightly** different from theirs, and that is okay. It is a "
                 "rounding difference, not an error. Rounding sin 37° to 0.6 gives "
                 "16.7 where 0.6018 gives 16.6 — so keep the extra decimals and your "
                 "answers will match theirs far more often.",
    }),

    (B.KIND_WORKED, {
        "number": "86.1",
        "question": "(C) Find a) cos 37°   b) sin 192°   c) tan 58°. Round answers to "
                    "3 decimal places.",
        "steps": [
            {"label": "Read what this one is really for",
             "text": "There is no triangle here and nothing to rearrange. This "
                     "problem exists so you can find the three buttons and prove your "
                     "calculator is in **degree** mode. Record 4 or 5 decimal places "
                     "first, then round to 3 — and the results may come out positive "
                     "or negative."},
            {"label": "a) cosine of 37 degrees",
             "text": "Press `cos`, then `37` (or `37` then `cos` — calculators "
                     "differ). Write down what you see, then round. **One "
                     "difference to expect:** your DIVE guide prints 0.79863 on "
                     "this line and your calculator will show 0.79864. Neither of "
                     "you is wrong. cos 37° is 0.7986355…, so 0.79864 is the "
                     "correctly rounded fifth place and the guide cut the digits "
                     "instead of rounding them. Both give **0.799**, which is what "
                     "the question actually asked for.",
             "math": "cos 37° = 0.79864 = 0.799"},
            {"label": "b) sine of 192 degrees",
             "text": "This one comes out **negative**, and that is not a mistake. 192° "
                     "is more than a half turn, and past a half turn the sine goes "
                     "below zero. You do not need to know why yet — you need to know "
                     "not to drop the minus sign.",
             "math": "sin 192° = -0.20791 = -0.208"},
            {"label": "c) tangent of 58 degrees",
             "text": "Bigger than 1, which is also fine. Tangent is opp ÷ adj, and "
                     "past 45° the opposite side is the longer of the two legs — so "
                     "the fraction is top-heavy.",
             "math": "tan 58° = 1.60033 = 1.600"},
        ],
        "answer": "0.799 · -0.208 · 1.600",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 86.2a — rearrange and solve for the unknown",
        "equation": "sin 37° = 10 / x        ·        round to 1 d.p.",
        "steps": [
            {"label": "Look first",
             "text": "In your book this equation is printed as a picture rather than "
                     "as text, so it is typed out along the top of this box instead. "
                     "It comes straight from the book's own next line, "
                     "`x(sin 37°) = 10(1)` — glance at your page and check the two "
                     "agree before you start. Notice what kind of problem it is "
                     "**not**: there "
                     "is nothing to discover about triangles. `sin 37°` is just a "
                     "number you have not looked up yet, and `x` is on the bottom of "
                     "a fraction. This is Lesson 78 wearing a costume."},
            {"label": "Step 1 · give the left side its invisible 1",
             "text": "`sin 37°` is a value sitting on its own, and any value sitting "
                     "on its own is secretly over 1. Writing that 1 in turns the line "
                     "into two fractions, and two fractions is a shape you already "
                     "know how to attack.",
             "math": "sin 37° / 1 = 10 / x"},
            {"label": "Step 2 · cross-multiply",
             "text": "Top-left times bottom-right, top-right times bottom-left. The "
                     "unknown comes up out of the basement, which was the entire "
                     "point of doing it.",
             "math": "x(sin 37°) = 10(1)"},
            {"label": "Step 3 · divide both sides by sin 37°",
             "text": "`sin 37°` is stuck against the x, so undo it by dividing — the "
                     "same thing you would do if it were a 4 or a 7. Treat it as one "
                     "single number, because that is exactly what it is.",
             "math": "x = 10 / sin 37°"},
            {"label": "Step 4 · now look the number up",
             "text": "Not before now. Keep 4 decimal places — the book asks for 3 or "
                     "4, and this is the step where throwing digits away costs you "
                     "the answer.",
             "math": "sin 37° = 0.6018"},
            {"label": "Step 5 · do the division",
             "text": "Straight arithmetic. Your DIVE guide prints **16.616** on this "
                     "line and you will get **16.6168** — the guide kept more decimal "
                     "places of sin 37° than the 0.6018 it shows you. Both round to "
                     "the same place, which is the whole reason the book tells you "
                     "not to worry about the last digit.",
             "math": "10 / 0.6018 = 16.6168"},
            {"label": "Step 6 · round to 1 decimal place",
             "text": "The question asked for 1 d.p. Round at the end, once, and not "
                     "before.",
             "math": "x = 16.6"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "86.2b",
        "question": "Rearrange and solve for the unknown:  h / 50 = tan 42°. Round to "
                    "1 d.p.",
        "steps": [
            {"label": "Same shape, unknown on top this time",
             "text": "The h is already upstairs, which makes this one shorter. The "
                     "invisible 1 goes under `tan 42°` again.",
             "math": "h / 50 = tan 42° / 1"},
            {"label": "Cross-multiply",
             "text": "h times 1 on one side, 50 times the trig value on the other.",
             "math": "h(1) = 50(tan 42°)"},
            {"label": "Look the number up — degrees, 4 decimal places",
             "text": "One button press, and you are holding an ordinary number.",
             "math": "tan 42° = 0.9004"},
            {"label": "Multiply, then round to 1 d.p.",
             "text": "Nothing clever left. Multiply and round once at the end.",
             "math": "50 * 0.9004 = 45.02  →  h = 45.0"},
        ],
        "answer": "h = 45.0",
    }),

    (B.KIND_WORKED, {
        "number": "86.3",
        "question": "An observer standing 50 m from a tree uses a clinometer to "
                    "measure an angle of 42° between herself and the top of the tree. "
                    "Use the tangent function to find the height, h, of the tree. "
                    "Round to 1 d.p.",
        "steps": [
            {"label": "Draw it before you do anything else",
             "text": "The book prints a picture; draw your own and you will never "
                     "need theirs. A flat line 50 m long from her feet to the base of "
                     "the tree. The tree standing straight up at the far end, height "
                     "**h**. Her line of sight from her eye to the treetop, closing "
                     "the shape. The angle **42°** is at *her* corner, between the "
                     "ground and her line of sight."},
            {"label": "Why we are allowed to call it a right triangle",
             "text": "Nobody said the word *perpendicular* and nobody drew a little "
                     "square. Here is the book's reasoning, and it is worth following "
                     "because it is the kind of move you will keep meeting: **because "
                     "the problem tells you to use the tangent function, you may take "
                     "the tree as standing straight up from the ground** — which "
                     "trees mostly do — and that makes the shape a right triangle. "
                     "The instruction is what buys you the right angle. (The tangent "
                     "button itself is not fussy: it answered for 58° up in Ex. 86.1, "
                     "and sin 192° is not a corner of any right triangle. It is *this "
                     "picture* that needs a right angle, because without one the "
                     "words opposite and adjacent have nothing to mean.) The right "
                     "angle is at the **base of the tree**, so the hypotenuse is her "
                     "line of sight."},
            {"label": "Stand at 42° and name the two legs",
             "text": "She is standing at the 42° corner. The tree is across the "
                     "triangle from her, so **h is the opposite**. The 50 m of ground "
                     "is under her feet, so **50 is the adjacent**. Opposite and "
                     "adjacent together — that is tangent, exactly as the question "
                     "said."},
            {"label": "Write the ratio and notice where you have seen it",
             "text": "θ = 42°, opp = h, adj = 50. Put those into tan θ = opp / adj "
                     "and you get **the equation from Ex. 86.2b, character for "
                     "character**. That is the point of this example: the tree "
                     "problem and the algebra problem were the same problem all "
                     "along.",
             "math": "tan 42° = h / 50"},
            {"label": "So the answer is already solved",
             "text": "Reuse the work. The height of the tree is a little over 45 "
                     "metres — and sanity-checks fine: she is 50 m back and looking "
                     "up steeply, so a tree slightly shorter than her walk is exactly "
                     "what you would expect.",
             "math": "50 * 0.9004 = 45.02  →  h = 45.0 m"},
        ],
        "answer": "h = 45.0 m",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Saxon compresses this lesson into about nine characters. Here is "
                 "what each of them is short for — including the abbreviations the "
                 "book warns you it is about to start using.",
        "rows": [
            {"symbol": "θ", "plain": "theta — a name for the angle you are standing "
                                     "at, not a number to solve for",
             "example": "θ = 42°"},
            {"symbol": "sin θ", "plain": "sine of that angle — short for \"the side "
                                         "opposite ÷ the hypotenuse\"",
             "example": "sin 30° = 0.5"},
            {"symbol": "cos θ", "plain": "cosine — short for \"the side adjacent ÷ "
                                         "the hypotenuse\"",
             "example": "cos 30° = 0.866"},
            {"symbol": "tan θ", "plain": "tangent — short for \"the side opposite ÷ "
                                         "the side adjacent\"",
             "example": "tan 30° = 0.577"},
            {"symbol": "hyp / opp / adj", "plain": "hypotenuse / opposite / adjacent — "
                                                   "the book starts abbreviating them "
                                                   "on page 1",
             "example": "tan θ = opp / adj"},
            {"symbol": "trig", "plain": "trigonometry. Also what everyone calls the "
                                        "three functions: \"the trig functions\"",
             "example": "a trig problem"},
            {"symbol": "(C)", "plain": "calculator allowed on this problem — it is a "
                                       "permission, not an instruction",
             "example": "186. (C) Find sin 320°"},
            {"symbol": "1 d.p.", "plain": "round your final answer to 1 decimal place "
                                          "(d.p. = decimal places)",
             "example": "45.02  →  45.0"},
        ],
        "after": "`sin 37°` is **not** \"sin times 37.\" There is no multiplying "
                 "anywhere in it. It is one instruction — *look up the ratio that "
                 "goes with a 37° angle* — and once you have looked it up you are "
                 "holding a perfectly ordinary number like 0.6018, which you can "
                 "divide by, multiply by, and move around exactly like any other.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "The calculator is in radians.",
             "wrong": "sin 30 = -0.98803",
             "right": "sin 30° = 0.5",
             "note": "This is the big one, because it poisons **every** answer and it "
                     "does not look like an error — it just gives numbers. Degrees "
                     "and radians are two different units for measuring an angle, the "
                     "way inches and centimetres are two units for length. Test it "
                     "before every trig assignment: `sin 30` must give **0.5**. If it "
                     "gives about **-0.988**, find the DEG/RAD button and switch."},
            {"name": "Writing the ratio upside down.",
             "wrong": "tan 42° = 50 / h  →  h = 50 / 0.9004 = 55.5",
             "right": "tan 42° = h / 50  →  h = 50 * 0.9004 = 45.0",
             "note": "**Opposite goes on top** in both sine and tangent. Flipping it "
                     "in Ex. 86.3 turns a 45.0 m tree into a **55.5 m** one — an "
                     "answer that is wrong but not absurd, which is what makes this "
                     "mistake expensive. Say the ratio out loud before you write it: "
                     "\"tangent is opposite over adjacent.\""},
            {"name": "Grabbing sine when the problem handed you the adjacent side.",
             "wrong": "h = 50 * sin 42° = 50 * 0.6691 = 33.5",
             "right": "h = 50 * tan 42° = 50 * 0.9004 = 45.0",
             "note": "Sine needs the **hypotenuse**, and nobody in Ex. 86.3 ever told "
                     "you how long her line of sight was. Using it anyway gives "
                     "**33.5 m**. Cross out the side the problem never mentions "
                     "first, and the two that survive pick the function for you."},
            {"name": "Multiplying when the unknown was on the bottom.",
             "wrong": "x = 10 * 0.6018 = 6.0",
             "right": "x = 10 / 0.6018 = 16.6",
             "note": "In Ex. 86.2a the x is in the **denominator**, so after "
                     "cross-multiplying it ends up multiplied by sin 37° and you undo "
                     "that by **dividing**. Multiplying instead gives **6.0**, and "
                     "there is a free check available: sin and cos are always less "
                     "than 1, so dividing by one makes a number bigger and "
                     "multiplying makes it smaller. Ask which way your answer should "
                     "have moved."},
            {"name": "Rounding the trig value before you use it.",
             "wrong": "x = 10 / 0.6 = 16.7",
             "right": "x = 10 / 0.6018 = 16.6",
             "note": "The book calls this one out by name. Rounding sin 37° to 0.6 "
                     "hands you **16.7** instead of 16.6 — close enough to look "
                     "right, wrong enough to be marked wrong. **Round once, at the "
                     "very end.** Keep 3 or 4 decimals of every trig value until then."},
            {"name": "Keeping the old labels after moving to the other angle.",
             "wrong": "at the 60° corner, the short leg is still the opposite  →  "
                      "sin 60° = 0.5",
             "right": "at the 60° corner, the long leg is the opposite  →  "
                      "sin 60° = 0.866",
             "note": "Opposite and adjacent are **relative to θ**. Change which angle "
                     "you are calling θ and you must re-label the two legs before you "
                     "write another ratio. The hypotenuse is the only one that stays "
                     "put. Play with the button in the tool below until this feels "
                     "obvious rather than fiddly."},
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Which of the three to reach for",
        "headers": ["the two sides your problem involves", "the ratio", "written out"],
        "rows": [
            {"cells": ["opposite and hypotenuse", "sine", "sin θ = opp / hyp"],
             "emphasis": True},
            {"cells": ["adjacent and hypotenuse", "cosine", "cos θ = adj / hyp"],
             "emphasis": True},
            {"cells": ["opposite and adjacent", "tangent", "tan θ = opp / adj"],
             "emphasis": True},
            {"cells": ["the third side — the one nobody mentioned",
                       "cross it out first", "it decides nothing"]},
        ],
        "note": "In Ex. 86.3 you were given the **adjacent** (50 m) and asked for the "
                "**opposite** (h). Nobody said a word about the hypotenuse, so cross "
                "it out — and the two that are left say tangent, which is exactly "
                "what the question told you to use. Your dad may remember this as "
                "**SOH-CAH-TOA**, one letter per side in the order they appear above. "
                "Saxon does not use that phrase, so it is a spare tyre, not the rule.",
    }),

    (B.KIND_TOOL, {
        "title": "Stand at the other angle",
        "intro": "A right triangle with the square corner at the bottom right. The "
                 "orange ring shows **where you are standing** — that corner is θ. "
                 "The three sides are labelled from there, and under the picture is a "
                 "row of three numbers, always in this order: **the sine first, then "
                 "the cosine, then the tangent** of the angle you are standing at. "
                 "Drag the slider to change the angle. Press **Smaller**, then "
                 "**Bigger** again, to change the size of the whole triangle — and "
                 "keep your eyes on the three numbers while you do, because they do "
                 "not move, and that is Lesson 53's promise happening in front of "
                 "you. **Bigger** and **Smaller** change the size; the triangle "
                 "always fits the frame, so a steep one just gets narrower rather "
                 "than taller. Then press **Stand at the other angle**, which is "
                 "the button this whole page is about.",
        "widget": "triangle",
        # {"angle": 30} on purpose: 30° is the angle Saxon works on page 2, so the
        # readout opens showing 0.5 / 0.866 / 0.577 — the three numbers the book
        # tells her to expect. Its complement is 60°, so the swap button lands on
        # the OTHER angle of the same 30-60-90 family the lesson is built around.
        "config": {"angle": 30},
        "after": "Set the slider to **30°** and answer these two before you open the "
                 "drop-down. **One:** which side keeps its name no matter which "
                 "corner you stand in, and why? **Two:** when you press *Stand at the "
                 "other angle*, which of the three numbers change — and does the "
                 "triangle itself change at all?",
    }),

    (B.KIND_REVEAL, {
        "prompt": "At 30°, what happens when you stand at the other angle?",
        "answer": "**Sine and cosine trade places, and the tangent turns upside "
                  "down.** The hypotenuse never moves — it is defined from the right "
                  "angle, and you never stood in that corner, so no button can change "
                  "it. The two legs are what swap jobs. At the 30° corner the short "
                  "leg is opposite and the long leg is adjacent, so the tangent is "
                  "short over long → 0.5 / 0.866 = 0.577 → now stand at the 60° "
                  "corner and those same two legs have swapped, so it is long over "
                  "short → 0.866 / 0.5 = 1.732 → and the sine you were reading at 30° "
                  "(0.5) is now sitting in the cosine slot at 60°. The triangle on "
                  "the screen did not move once. **Only you did** — and that is the "
                  "sentence to remember out of this whole lesson.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "Trigonometry is the study of **right triangles**, and it is really just "
            "the **ratios of the three sides** named from one angle.",
            "**sin θ = opp / hyp   ·   cos θ = adj / hyp   ·   tan θ = opp / adj.** "
            "Three ratios. Learn them in that order.",
            "The **hypotenuse** is the side opposite the right angle and the longest "
            "side (Lesson 54). Its name never changes.",
            "**Opposite and adjacent depend on where θ is.** Move to the other acute "
            "angle and the two legs trade names.",
            "Same angles, different sizes, **same ratios** (Lesson 53). The ratio "
            "belongs to the angle, which is why the calculator can hold all the "
            "answers.",
            "Check **degree mode** before every trig assignment: `sin 30` must give "
            "0.5, not -0.988.",
            "Keep **3 or 4 decimal places** of a trig value while you work, and round "
            "only the final answer. Rounding early is what makes your answer disagree "
            "with the key.",
            "Rearranging one of these is **Lesson 78**, not new mathematics: give the "
            "lone value its invisible 1, cross-multiply, divide.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 86 first. If it didn't quite land, this is here to fix that "
    "— and there's a triangle further down you can actually stand inside. Two things "
    "to hold on to: trigonometry is only three ratios, and \"opposite\" and "
    "\"adjacent\" depend entirely on which corner you're standing in."
)

PARENT_CONTENT = """## The big idea

Trigonometry sounds enormous and is not. Saxon says it plainly on page 1: *"For
such a big word like 'trigonometry,' it is really just about the ratios of the
three sides, defined relative to one of the angles as sine, cosine, and
tangent."* Three ratios, one angle. That is the entire lesson.

The two things that actually have to land:

1. **The hypotenuse is fixed; the other two names are not.** Hypotenuse is a
   Lesson 54 definition she already owns — the side opposite the right angle, and
   the longest side. *Opposite* and *adjacent*, by contrast, are addresses relative
   to **θ**. Stand at the other acute angle of the very same triangle and the two
   legs trade names. A printed diagram shows one of the two worlds and lets a child
   assume it is the only one; the interactive triangle on her page has a **Stand at
   the other angle** button so she can watch the labels swap. That button is the one
   thing on the page a book cannot do, so make her press it.
2. **The ratio belongs to the angle, not to the triangle.** This is Lesson 53 doing
   the work. The book's three 30-60-90 triangles are three sizes with the same three
   angles, so they are similar, so their ratios are equal — 0.5 every time for
   sin 30°. That is *why* a calculator can have a sin button at all. Without this,
   the sin button looks like magic, and children do not trust magic.

**About the figures, and what is actually missing.** Parts of her DIVE guide reach
this page as images rather than text, and they are two different problems.

- **Real diagrams.** Page 1's three 30-60-90 triangles, and practice problem 386's
  clinometer sketch, are pictures and cannot be reprinted here. The three triangles
  are rebuilt on her page as a table of real side lengths (1-1.732-2, 2-3.464-4,
  5-8.66-10 — the same shape at three scales), which carries the point they were
  drawn to make.
- **Missing equations, not missing pictures.** For Ex. 86.2 and practice problem
  286 the guide prints "a)" and "b)" with the *typeset equation* as an image; the
  printed solution that follows is pure algebra and refers to no diagram at all. So
  Ex. 86.2's two equations have been reconstructed from the guide's own solution
  lines — `x(sin 37°) = 10(1)` and `h(1) = 50(tan 42°)` — and written out in full.
  Her page tells her this in the stepper and asks her to check the equation against
  her book before she starts. Please do check it with her once.

Have the book open beside her for 286 and 386 either way, so she works those from
the printed originals.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Draw a right triangle. Mark the square corner. Ask: **"Which side is across from
   the square corner?"** Trace it. **"That's the hypotenuse — you already know it
   from the Pythagorean Theorem. It's also the longest side."** Two definitions,
   they always agree, and this is the only label that will hold still.
2. Put your finger in one of the *other* two corners. **"I'm standing here. Which
   side is across the room from me?"** — that's the opposite. **"Which one am I
   touching?"** — adjacent. Let her answer both; do not supply the words first.
3. Now move your finger to the third corner and ask the question that is the whole
   lesson: **"I haven't changed the triangle at all. What just changed?"** You want
   her to say the two legs swapped names. If she does not get there, ask both
   questions from step 2 again from the new corner and let her hear herself give
   different answers.
4. Write the three ratios down and read them aloud as sentences, not letters:
   *"sine is opposite over hypotenuse."* Then ask: **"If I'm standing somewhere
   else, does sin θ change?"** Yes — because opposite changed. That is the payoff of
   step 3 arriving on schedule.
5. Get the calculator out and do the book's own test. **"Press sin, then 30. What
   did you get?"** You want 0.5. If she gets about −0.988, that is radian mode; find
   the DEG/RAD button together. Then ask the closing question: **"Why should the
   calculator even be able to answer that, when I never told it how big my triangle
   is?"** Because the ratio belongs to the angle. That is Lesson 53 and it is the
   idea worth the five minutes.

If she is lost, go back to step 3. Everything else in the lesson is arithmetic.

## The classic mix-ups, with the exact wrong answer each one produces

- **Radian mode.** `sin 30` returns **−0.98803** instead of **0.5**, and then every
  answer on the page is wrong while looking perfectly reasonable. Check it before
  every trig assignment. Two units for angles, like inches and centimetres.
- **The ratio written upside down.** On Ex. 86.3 she writes `tan 42° = 50/h` instead
  of `h/50`, which gives `50 / 0.9004` = **55.5 m** instead of **45.0 m**. Wrong but
  not absurd, which is what makes it costly. Fix: say the ratio out loud —
  "tangent is opposite over adjacent" — before writing anything.
- **Sine instead of tangent.** She reaches for sine on Ex. 86.3 and gets
  `50 × 0.6691` = **33.5 m**. Sine needs the hypotenuse and nobody ever told her how
  long the line of sight was. Fix: cross out the side the problem never mentions;
  the two survivors choose the function.
- **Multiplying when the unknown was in the denominator.** On Ex. 86.2a she writes
  `x = 10 × 0.6018` = **6.0** instead of `10 ÷ 0.6018` = **16.6**. Free check: sine
  and cosine are always less than 1, so dividing by one makes a number *bigger*.
  Ask her which way the answer should have moved.
- **Rounding the trig value too early.** The book flags this itself: rounding
  sin 37° to 0.6 gives **16.7** where 0.6018 gives **16.6**. Keep 3 or 4 decimals
  until the last line.
- **Keeping the old labels after switching angles.** She moves to the 60° corner and
  still calls the short leg the opposite, giving `sin 60° = 0.5` instead of
  **0.866**. This is mix-up 3 from the teaching script, and it is the one the
  interactive triangle fixes fastest.

## What to watch her do

Watch her **hands**, in this order:

1. **Does she label the picture before she writes any algebra?** You want to see
   *hyp*, *opp*, *adj* written on the three sides in pencil. A child who labels
   cannot write the ratio upside down; a child who does it in her head does, about a
   third of the time.
2. **Does she find the right angle first?** The correct hand movement is: point at
   the little square, then trace straight across to the hypotenuse. If her hand goes
   to the longest-*looking* side instead, she is eyeballing, and that fails the
   moment a diagram is not drawn to scale.
3. **When the angle changes, does her hand go back and re-label?** This is the tell
   for whether idea 2 landed. She should physically erase or re-write *opp* and
   *adj*. If she carries on with the old labels, stop her there.
4. **Does the calculator come out last?** The correct order is: label, choose the
   ratio, rearrange, *then* press buttons. A calculator that comes out first is a
   child guessing which button might help.
5. **Does she round only once, at the end?** Watch for a rounded trig value written
   down mid-page. That single habit accounts for most of the "my answer is close but
   the key says something else" frustration in this chapter.

Getting 45.0 is not what to watch for. She can get 45.0 by copying the shape of
Ex. 86.2b. The five habits above are what survive a problem where the angle is at
the *other* corner.

## Extend it

- **Do practice problem 386 with her out loud**, because it is Ex. 86.3 with the
  numbers changed and it is the cleanest check that she can repeat the process
  rather than the answer. Observer 100 m from a tree, angle 36°, find h. Same
  labelling: h is opposite, 100 m is adjacent, so tangent. `tan 36° = h/100`, then
  `h = 100 × 0.7265 = 72.65`, which rounds to **72.7 m**. If she gets 72.7 without
  help, idea 1 and the recipe have both landed.
- **Ask her to predict before pressing.** With the tool at 30°, ask what
  `sin 60°` will be *before* she presses the swap button. If she says 0.866 because
  that was the cosine a moment ago, she has got hold of something students usually
  meet a year later — that sine and cosine are the same ratio seen from the two ends
  of a right triangle.
- **Send her outside with a protractor and a tape measure** and have her find the
  height of something — the house, a tree, a light pole. Measure the distance,
  measure the angle, use tangent. Add her own eye height at the end, which nobody
  ever remembers and which is a genuinely good discussion. This is the lesson's own
  clinometer example done for real, and it is the reason the topic exists.
- **A puzzle worth leaving open:** ask what tan 90° would be. Adjacent goes to zero,
  and you cannot divide by zero. She is not expected to resolve it; meeting it as a
  puzzle is worth more than being told.

## Where this sits

DIVE Lecture 86, *Trigonometry Basics*. Reviews **Lessons 53, 54 and 78** — page 1
lists them.

- **Lesson 54** is the one to revisit if she is lost on vocabulary: it is where
  hypotenuse was defined and where right triangles first mattered.
- **Lesson 53** is the one to revisit if she does not believe the ratios can be
  equal for three different triangles. That is similar figures, and it is the load
  bearing idea here.
- **Lesson 78** (and Lesson 39 behind it) is the one to revisit if the *algebra* of
  Ex. 86.2 is what is stopping her, rather than the trigonometry. Worth separating
  those two out loud — "is it the triangle you don't like, or the rearranging?" —
  because they need different help.

**Proficient** looks like: labels the triangle correctly, picks the right ratio,
and solves 86.3-style problems with the angle in the familiar corner.
**Mastered** looks like: re-labels without being told when θ moves, keeps full
decimals until the end, and can say *why* the calculator knows sin 30° without
being shown a triangle.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 86 (trigonometry basics) — idempotent."

    LESSON_NUMBER = 86
    TITLE = "Trigonometry Basics — Three Ratios, Named From Where You Stand"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
