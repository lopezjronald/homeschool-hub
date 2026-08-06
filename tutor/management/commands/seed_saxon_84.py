"""Saxon Pre-Algebra Lesson 84 — Systems of Equations; More on Roots and Radical Signs.

Reviews Lessons 30, 54, 68 and 78. Two topics share one page, and they share one
sentence: **count first.** A system needs as many equations as it has unknowns;
a root needs as many identical factors as its little number says. Everything on
this page is one of those two counts.

The lesson's sharpest idea is the one Saxon is careful about and most books are
not: `√25` is **5**, one answer, because the radical sign means the *principal*
(positive) square root — but `x² = 25` has **two** answers, +5 and -5, because
solving an equation by taking the square root of both sides is a different job
from simplifying a root that is already written down. This page keeps those two
jobs visibly apart.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Example 84.2 and practice problem 284 are graphs, and Example 84.4's
worked lines are printed as images. The two lines of 84.2 were not visible when
this page was built, so they are not redrawn — but the one thing the book *states*
about that graph, the crossing point, IS drawn: a read-only grid holds a locked dot
at (3, 1). The rest of the graph idea is rebuilt from the numbers Example 84.1
itself supplies, and 84.4 is written out in symbols instead of reprinted. Nothing
is invented: the second system worked below is practice problem 184 out of this
lesson's own set.

    python manage.py seed_saxon_84 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 84 · Pre-Algebra",
        "title": "Two unknowns need two equations — and roots that count past two",
        "thesis": "Two topics, one habit: **count**. Count the unknowns and give "
                  "yourself that many equations. Count the little number on the "
                  "radical sign and look for that many identical factors. The whole "
                  "lesson is those two counts.",
        "formula": "x² = 25  →  x = ±5",
        "roles": [
            {"tone": "start", "name": "counting equations",
             "text": "To solve a system, the number of equations must equal the "
                     "number of unknowns. Two unknowns? You need two equations. "
                     "One equation and two unknowns is not hard — it is impossible."},
            {"tone": "move", "name": "counting factors",
             "text": "A square root asks for 2 identical factors, a cube root for 3, "
                     "a fourth root for 4, an nth root for n. That is the only thing "
                     "the little number ever means."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone would want two equations at once",
        "paragraphs": [
            "Here is a real question. A man and his twin sons stand together. Add the "
            "man's height to one son's height and you get 10 feet. All three of them "
            "stacked up come to 14 feet. How tall is the man?",
            "Try it with one equation and you will feel the problem. `m + s = 10` is "
            "true, and it is useless on its own — m could be 9 and s could be 1, or m "
            "could be 6 and s could be 4, and the equation is happy with every one of "
            "those. One fact about two unknown things never pins either of them down.",
            "The second sentence is what saves you. `m + 2s = 14` is a **different** "
            "fact about the **same** two heights. Only one pair of numbers can make "
            "both sentences true at once, and finding that pair is what solving a "
            "system means.",
            "That is the rule the book states flatly on page one: **to solve any "
            "system of equations, the number of equations must equal the number of "
            "unknowns.** Two unknowns, two equations. Three unknowns, three equations. "
            "If you are one equation short, you have not made a mistake — you have not "
            "been given enough, and the honest answer is to go back and find the "
            "second fact.",
            "The back half of the page is a different subject and it exists for a "
            "smaller reason: you already know how to undo a square, and sooner or "
            "later something is cubed instead. A cube root undoes a cube the same way "
            "a square root undoes a square. Nothing new happens; you just count "
            "higher.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "A system is two facts about the same two things",
        "paragraphs": [
            "The word **system** sounds like machinery. It is not. A system of "
            "equations is just two or more equations that get solved **together**, "
            "because they are talking about the same unknowns. Saxon also calls them "
            "**simultaneous equations**, which is a better name: they are true at the "
            "same time.",
            "Look at the two from the man and his sons and notice what is ordinary "
            "about them. `m + s = 10` and `m + 2s = 14` are plain linear equations — "
            "the same kind you have been solving and graphing since Lesson 68. Not "
            "every system is linear, but every system in Lesson 84 is.",
            "The one thing that is new is the **counting rule**, and it is worth "
            "saying out loud before you touch a pencil: the number of equations must "
            "equal the number of unknowns. Two letters in the problem means you go "
            "hunting for two sentences, and you do not start solving until you have "
            "found both.",
            "Sometimes you will spot the answer before you do any algebra — with "
            "these numbers, you might just see that each son is 4 feet and the man is "
            "6. That is fine, and it is not the point. The point is to learn the "
            "method here, on numbers small enough that you can check it, so the method "
            "still works when the numbers stop being friendly.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Give me one fact: two numbers add up to ten. Now tell me what they "
                "are. You can't — there's a whole list. Nine and one. Six and four. "
                "Seven and three. One fact about two mystery numbers is never enough. "
                "So now I'll give you a second fact about those same two numbers, and "
                "watch what happens: only one pair survives both. That's all a system "
                "is. Two facts, same two mysteries.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "Make both equations say the same thing, then set them equal",
        "paragraphs": [
            "Here is the method the book uses, and it rests on something you already "
            "believe. If `m = -s + 10` and also `m = -2s + 14`, then those two "
            "right-hand sides are both equal to m — so they are equal to **each "
            "other**.",
            "That single move is the whole trick, because the moment you write "
            "`-s + 10 = -2s + 14` the letter m is gone. You are back to a one-unknown "
            "equation, which is a thing you have solved a hundred times.",
            "So the shape of the work is: **rearrange both equations to start with "
            "the same letter, set the two other sides equal, solve for the letter that "
            "is left, then put that number back in to get the first one.**",
            "It does not matter which letter you solve for first. Solve both for `s` "
            "instead and you land on the same pair of heights. Pick whichever one is "
            "already sitting alone, or nearly alone, in both equations — that is the "
            "one that costs you the least rearranging.",
            "And when you have both numbers, **put them back into both original "
            "equations**. Not one. Both. A wrong number will usually survive the "
            "equation you just used and fall apart in the other one, which is exactly "
            "why checking against only one of them catches nothing.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Solving a system, the same way every time",
        "steps": [
            {"label": "Name the unknowns and count them.",
             "detail": "One letter per mystery thing. `m` for the man, `s` for a son. "
                       "Write down what each letter *means* beside it — that one line "
                       "is what stops you answering the wrong question at the end."},
            {"label": "Count your equations. You need as many as you have letters.",
             "detail": "Two unknowns, two sentences. If the problem only gave you one, "
                       "read it again — the second fact is in there, usually in the "
                       "sentence you skimmed."},
            {"label": "Translate each sentence into an equation.",
             "detail": "Exactly the key-word work from Lesson 16. *\"Add the man's "
                       "height to the height of 1 son\"* is `m + s`. *\"The total "
                       "height of the man and 2 sons\"* is `m + 2s`. The word "
                       "**is** becomes the equals sign."},
            {"label": "Rearrange BOTH equations so the same letter stands alone.",
             "detail": "Get `m = something` out of each one. Now both right-hand "
                       "sides are equal to m, so they are equal to each other."},
            {"label": "Set the two other sides equal and solve.",
             "detail": "One letter is left. Solve it the ordinary way — undo the "
                       "additions, then the multiplications."},
            {"label": "Substitute that number back to get the other unknown.",
             "detail": "Into either original equation. If you have time, do it in "
                       "both: they must hand you the same number."},
            {"label": "Check the pair in both original equations.",
             "detail": "Both. A wrong value very often satisfies one of them by "
                       "accident and almost never satisfies both."},
        ],
        "after": "Then answer the question that was actually asked. The book asks for "
                 "**the heights of the man and his sons** — so the answer is two "
                 "numbers with units on them, not a bare `s = 4`.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 84.1 — the man and his twin sons",
        "equation": "man + one son = 10 ft   ·   man + two sons = 14 ft   ·   the sons are the same height",
        "steps": [
            {"label": "First, two questions",
             "text": "Before any algebra: **what am I solving for?** The heights of "
                     "the man and his twin sons. And **what did they give me?** Two "
                     "separate facts. Ask those two questions in that order on every "
                     "word problem — they are the same two from Lesson 16."},
            {"label": "Step 1 · translate the first fact",
             "text": "\"Add the man's height to the height of 1 son, we get 10 feet.\" "
                     "Let `m` be the man's height and `s` be one son's height. Because "
                     "the sons are twins, one `s` covers either of them.",
             "math": "m + s = 10"},
            {"label": "Step 2 · translate the second fact",
             "text": "\"The total height of the man and 2 sons is 14 feet.\" Two sons "
                     "at the same height is `2s`. This is a **different** fact about "
                     "the same two heights, which is what makes it useful.",
             "math": "m + 2s = 14"},
            {"label": "Step 3 · check the count before you solve",
             "text": "Two unknowns, `m` and `s`. Two equations. The counting rule is "
                     "satisfied, so this system can be solved. Do this check every "
                     "time — it takes two seconds and it tells you whether the work "
                     "ahead of you is possible.",
             "math": "2 equations = 2 unknowns"},
            {"label": "Step 4 · get m alone in both",
             "text": "Subtract the `s` term from both sides of each equation. Now both "
                     "equations open with `m =`, which is the setup the next step "
                     "needs.",
             "math": "m = -s + 10   ·   m = -2s + 14"},
            {"label": "Step 5 · set them equal and solve for s",
             "text": "Both right-hand sides equal `m`, so they equal each other — and "
                     "`m` disappears. Add `2s` to both sides, then take 10 off both "
                     "sides. One unknown, ordinary work.",
             "math": "-s + 10 = -2s + 14  →  s + 10 = 14  →  s = 14 - 10 = 4"},
            {"label": "Step 6 · substitute to get m",
             "text": "Put 4 in wherever `s` was. Use the first equation.",
             "math": "m = -4 + 10 = 6"},
            {"label": "Step 7 · do it in the other one too",
             "text": "The second equation must give the same man. It does. Two "
                     "different roads to 6 is a strong signal you did not slip.",
             "math": "m = -2 × 4 + 14 = -8 + 14 = 6"},
            {"label": "Step 8 · check the pair in the first fact",
             "text": "Man 6, one son 4. Does that add to 10 feet? It does.",
             "math": "6 + 4 = 10"},
            {"label": "Step 9 · check the pair in the second fact",
             "text": "Man 6 plus two sons at 4 each. Does that come to 14 feet? It "
                     "does. **Both** originals agree, so the pair is right.",
             "math": "6 + 2 × 4 = 14"},
            {"label": "Step 10 · answer the actual question",
             "text": "The sons are **4 feet** tall and the man is **6 feet** tall. "
                     "Numbers with units, because the question asked about heights — "
                     "not a bare `s = 4` sitting at the bottom of the page."},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "Practice 184",
        "question": "A man has 2 daughters. The daughters are twins; they are the same "
                    "height. If we add the man's height to the height of 1 daughter, "
                    "we get 11 feet. The total height of the man and his 2 daughters "
                    "is 16 feet. What are the heights of the man and his daughters?",
        "steps": [
            {"label": "Name and count",
             "text": "`m` is the man's height, `d` is one daughter's height — one "
                     "letter does for both daughters because they are twins. Two "
                     "unknowns, so you need two equations, and the problem gives you "
                     "two sentences. Good."},
            {"label": "Translate the first sentence",
             "text": "Man plus one daughter is 11 feet.",
             "math": "m + d = 11"},
            {"label": "Translate the second sentence",
             "text": "Man plus two daughters is 16 feet. Two daughters at the same "
                     "height is `2d`.",
             "math": "m + 2d = 16"},
            {"label": "Get m alone in both",
             "text": "Take the daughter term off both sides of each equation.",
             "math": "m = -d + 11   ·   m = -2d + 16"},
            {"label": "Set them equal and solve for d",
             "text": "Both sides equal `m`, so they equal each other. Add `2d` to both "
                     "sides, then subtract 11 from both sides.",
             "math": "-d + 11 = -2d + 16  →  d + 11 = 16  →  d = 16 - 11 = 5"},
            {"label": "Substitute back for m",
             "text": "Put 5 in for `d` in the first equation.",
             "math": "m = -5 + 11 = 6"},
            {"label": "Check the first original",
             "text": "Man 6 plus one daughter 5 should be 11 feet.",
             "math": "6 + 5 = 11"},
            {"label": "Check the second original",
             "text": "Man 6 plus two daughters at 5 each should be 16 feet. Both "
                     "originals agree, so you are done.",
             "math": "6 + 2 × 5 = 16"},
            {"label": "Write the answer",
             "text": "Each daughter is **5 feet** tall and the man is **6 feet** tall. "
                     "Units on both numbers, because the question asked about heights. "
                     "Notice the man came out 6 feet again — same as Example 84.1, "
                     "different numbers everywhere else. That is a coincidence, not a "
                     "pattern, and it is worth naming so you do not start expecting "
                     "it.",
             "math": "d = 5 feet   ·   m = 6 feet"},
        ],
        "answer": "d = 5 feet · m = 6 feet",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "move",
        "title": "The picture version: the answer is where the lines cross",
        "paragraphs": [
            "Example 84.2 gives you the same job as a **graph** instead of as "
            "sentences. Two lines are drawn, and the question is where they meet. "
            "That is not a different question dressed up — it is literally the same "
            "one.",
            "Think about what a line *is*. Every point on it is an (x, y) pair that "
            "makes that line's equation true. So a point sitting on **both** lines is "
            "a pair that makes **both** equations true — which is the definition of "
            "the solution of a system. The crossing point is the answer, and there is "
            "nothing else it could be.",
            "The book's graph for 84.2 has its lines crossing at **(3, 1)**, so the "
            "answer is the ordered pair `(3, 1)` — x first, y second, in parentheses, "
            "with a comma. That is not decoration; an ordered pair is how a two-number "
            "answer is written, and swapping the order gives a different point.",
            "You can watch this happen with the system you just solved. `m = -s + 10` "
            "and `m = -2s + 14` are two straight lines. Draw them with `s` across and "
            "`m` up, and they cross at `s = 4`, `m = 6` — the very pair the algebra "
            "handed you. Same answer, found by looking instead of by solving.",
            "Reading a crossing point off a graph only works when the crossing sits "
            "on a corner of the paper. In Lesson 84 it always will; the book promises "
            "the values are **integers** — whole numbers and their negatives, so `-2` "
            "counts and `2.5` does not. When they are not integers, the algebra is the "
            "only honest way to get them — which is why you learn the algebra first.",
        ],
    }),

    (B.KIND_TOOL, {
        "title": "The crossing point, on a grid",
        "intro": "Straight talk about this one. Example 84.2's two lines are printed "
                 "in your DIVE book and this page cannot reprint them — so keep the "
                 "book open beside you for the lines themselves. What the book *states* "
                 "is where they cross, and that is what is marked below: one hollow "
                 "dot at **(3, 1)**. Nothing here is clickable; it is a picture. Walk "
                 "it with your finger — 3 across first, then 1 up.",
        "widget": "grid",
        # A GIVEN figure, not her work: `points` + `locked` so the dot cannot be
        # nudged or deleted, `readonly` so no controls appear at all. Only the
        # crossing point is drawn, because the crossing point is the only thing
        # the source says about this graph — the two lines are not invented here.
        # Nothing is lost with JS off: (3, 1) is stated in words just above.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "points": [[3, 1]],
                   "locked": True,
                   "readonly": True,
                   "label": "the point (3, 1), where the two lines of Example 84.2 cross"},
        "after": "Now do the swap in your head. **(1, 3)** would be 1 across and 3 up — "
                 "a different dot on the same grid, and a wrong answer. That is why "
                 "the order is part of the answer and not a formatting habit.",
    }),

    (B.KIND_MATH, {
        "display": "√25 = 5   ·   x² = 25  →  x = +5 and x = -5",
        "note": "These two lines are the heart of the second half of this lesson, and "
                "they are **not** contradicting each other. On the left you are "
                "**simplifying** a root that is already written down, and the radical "
                "sign only ever means the positive one. On the right you are "
                "**solving an equation** by taking the square root of both sides, and "
                "then both signs are allowed in. Same number 25, different job, "
                "different number of answers.",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "start",
        "title": "Simplifying a root is not the same job as solving an equation",
        "paragraphs": [
            "Start with the easy half. Asked to simplify `√9`, you think: *what times "
            "what is 9?* Two identical factors. Since 3 × 3 = 9, the answer is 3. It "
            "is called a **square** root because finding the area of a square "
            "multiplies two sides that are the same length.",
            "Now the fair objection, and Saxon calls it a good question: -3 × -3 is "
            "also 9. So why isn't -3 an answer too? Because when you **simplify** a "
            "square root you take only the **principal square root**, and the "
            "principal square root is defined to be the **positive** one. The radical "
            "sign is not asking which numbers square to 9. It is a symbol that hands "
            "back exactly one number, and that number is positive.",
            "But `x² = 9` is a different sentence. It does not contain a radical sign "
            "at all — it is an equation, and you solve it by taking the square root of "
            "**both sides**. Do that and both 3 and -3 make it true, so it has two "
            "solutions and you write `x = ±3`. The `±` is shorthand for *both the "
            "positive one and the negative one*.",
            "There is a moment where you throw the negative one away, and it is not a "
            "rule about square roots — it is a rule about the question. If x is a "
            "**distance**, as in Lesson 54B, then -3 is not an answer anyone wants, "
            "because nothing is negative three feet long. You drop it because of what "
            "x means, not because of the mathematics.",
            "Everything above was about the number 2. Now count higher. `³√8` asks "
            "*what times what times what is 8?* — three identical factors, and since "
            "2 × 2 × 2 = 8, it is 2. Just as a square root goes with the area of a "
            "square, a cube root goes with the **volume** of a cube from Lesson 69: "
            "three sides, all the same length.",
            "So the pattern is one sentence long. **The little number on the radical "
            "sign tells you how many identical factors to look for.** Square root: 2. "
            "Cube root: 3. Fourth root: 4. nth root: n. That is all it has ever "
            "meant.",
            "One last thing about how it is written. `√x` really means `²√x`, and "
            "everybody leaves the 2 off because square roots are far and away the most "
            "common. The radical sign itself was Leonhard Euler's idea in the 1700s, "
            "invented as a shorter way of writing fractional exponents — `√x` is "
            "`x` to the power of 1/2, and `ⁿ√x` is `x` to the power of 1/n. The "
            "symbol is nothing but shorthand.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "The whole root family — the only thing that changes is the count",
        "headers": ["written", "its name", "identical factors to find",
                    "an example from this lesson"],
        "rows": [
            {"cells": ["√x   (the 2 is left off)", "square root", "2", "√9 = 3"],
             "emphasis": True},
            {"cells": ["³√x", "cube root", "3", "³√8 = 2"]},
            {"cells": ["⁴√x", "fourth root", "4", "⁴√16 = 2"]},
            {"cells": ["⁵√x", "fifth root", "5", "⁵√-32 = -2"], "emphasis": True},
            {"cells": ["ⁿ√x", "nth root", "n", "ⁿ√x is x to the power 1/n"]},
        ],
        "note": "The two shaded rows are the ones that catch people. The **top** one "
                "is shaded because the 2 is invisible — `√x` and `²√x` are the same "
                "thing, and the missing 2 is why beginners think square roots are a "
                "separate species instead of the n = 2 case. The **fifth-root** row is "
                "shaded because there is a negative inside the radical sign and it is "
                "perfectly legal: **odd roots accept a negative inside, even roots do "
                "not.** Five factors of -2 multiplied together come to -32, because an "
                "odd number of negatives leaves one minus sign unpaired. Take an even "
                "count of factors instead and the minus signs pair off and cancel, "
                "which is why no real number gives you `⁴√-16`.",
    }),

    (B.KIND_WORKED, {
        "number": "84.3",
        "question": "Simplify the following roots. All answers are integers.   "
                    "a) ⁴√16    b) ³√-27    c) ⁵√-32",
        "steps": [
            {"label": "Read the little number first",
             "text": "Before anything else, look at the little number on each radical "
                     "sign: 4, then 3, then 5. That number is your instruction — it says how "
                     "many identical factors you are hunting for. And notice two of "
                     "these have a **negative** inside. For odd-numbered roots that is "
                     "completely fine. Do not confuse it with the principal square "
                     "root, which is a rule about square roots only."},
            {"label": "a) ⁴√16 — four identical factors",
             "text": "What number, multiplied by itself four times, gives 16? Try 2: "
                     "2 × 2 is 4, times 2 is 8, times 2 is 16. Four 2s. So the fourth "
                     "root of 16 is 2.",
             "math": "2 × 2 × 2 × 2 = 16  →  ⁴√16 = 2"},
            {"label": "b) ³√-27 — three identical factors",
             "text": "The inside is negative and the little number is odd, so the "
                     "answer will be negative. What number three times over gives -27? Try -3: "
                     "-3 × -3 is +9, and +9 × -3 is -27. Three of them, all the same.",
             "math": "-3 × -3 × -3 = -27  →  ³√-27 = -3"},
            {"label": "c) ⁵√-32 — five identical factors",
             "text": "An odd-numbered root again, negative inside again, so expect a "
                     "negative answer. Five -2s: the first pair makes +4, the next -8, "
                     "then +16, then -32. Five factors, and an odd number of minus "
                     "signs leaves the answer negative.",
             "math": "-2 × -2 × -2 × -2 × -2 = -32  →  ⁵√-32 = -2"},
            {"label": "The pattern underneath all three",
             "text": "You never did anything different. You read the little number, you "
                     "looked for that many identical factors, and you wrote one of them down. "
                     "The only extra thought was the sign, and the sign follows one "
                     "rule: an **odd** number of negative factors gives a negative "
                     "result, an **even** number gives a positive one."},
        ],
        "answer": "2 · -3 · -2",
    }),

    (B.KIND_WORKED, {
        "number": "84.4",
        "question": "Solve the following equations.   a) x² = 9    b) x² = 10",
        "steps": [
            {"label": "Notice the word: SOLVE, not simplify",
             "text": "There is no radical sign anywhere in these two questions. They "
                     "are **equations**, and you solve them by taking the square root "
                     "of both sides. That is the situation where the negative answer "
                     "is allowed back in — so both of these will have two answers, "
                     "and the book says so in its own solution."},
            {"label": "a) x² = 9",
             "text": "Take the square root of both sides. 9 is a perfect square, so "
                     "the root simplifies to 3 — and because you solved an equation "
                     "rather than simplified a written-down root, you keep both signs. "
                     "Check them: 3 × 3 = 9, and -3 × -3 = 9. Both work, so both are "
                     "answers.",
             "math": "x² = 9  →  x = ±3"},
            {"label": "b) x² = 10",
             "text": "Same move, take the square root of both sides. But 10 is not a "
                     "perfect square — no whole number times itself gives 10 — so "
                     "there is nothing to simplify and the root stays written as it "
                     "is. Still two answers, still one positive and one negative.",
             "math": "x² = 10  →  x = ±√10"},
            {"label": "Why b) looks unfinished and is not",
             "text": "`±√10` feels like you stopped halfway. You did not. `√10` is a "
                     "perfectly good number — it sits between 3 and 4, since 3 × 3 is "
                     "9 and 4 × 4 is 16 — and leaving it under the radical sign is "
                     "**exact**, where a rounded decimal would not be. Simplify only "
                     "when there is something to simplify."},
        ],
        "answer": "x = ±3 · x = ±√10",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand on the page, decoded",
        "intro": "Lesson 84 puts a lot of meaning into very small marks. Here is what "
                 "each of them is short for.",
        "rows": [
            {"symbol": "a system", "plain": "two or more equations about the same "
                                            "unknowns, solved together — also called "
                                            "simultaneous equations",
             "example": "m + s = 10  and  m + 2s = 14"},
            {"symbol": "√x", "plain": "the PRINCIPAL square root of x — the positive "
                                      "one, and only that one",
             "example": "√9 = 3, never -3"},
            {"symbol": "²√x", "plain": "the same thing written out in full; the 2 is "
                                       "normally left off because square roots are the "
                                       "most common",
             "example": "²√9 means √9"},
            {"symbol": "³√x", "plain": "cube root — three identical factors; the inside "
                                       "may be negative",
             "example": "³√-27 = -3"},
            {"symbol": "ⁿ√x", "plain": "nth root — n identical factors. Negative inside "
                                       "is allowed only when n is odd",
             "example": "⁵√-32 = -2"},
            {"symbol": "±", "plain": "\"both the positive one and the negative one\" — "
                                     "two answers written on one line",
             "example": "x = ±5 means x = 5 and x = -5"},
            {"symbol": "x to the 1/n", "plain": "the fractional-exponent way of writing "
                                                "the nth root; Euler invented the "
                                                "radical sign in the 1700s to save "
                                                "writing this",
             "example": "x to the 1/2 is √x"},
            {"symbol": "(3, 1)", "plain": "an ordered pair — how the answer to a "
                                          "graphed system is written, x first then y",
             "example": "the lines in Ex. 84.2 cross at (3, 1)"},
        ],
        "after": "The one to keep is `±`. It is not a new operation and it is not an "
                 "error bar — it is two answers folded onto one line, and you unfold "
                 "it by writing them out separately whenever you are checking.",
    }),

    (B.KIND_ERRORS, {
        "title": "The seven mistakes almost everyone makes",
        "items": [
            {"name": "Giving a simplified square root two answers.",
             "wrong": "√9 = +3 and -3",
             "right": "√9 = 3",
             "note": "The radical sign means the **principal** square root, which is "
                     "the positive one. Nothing is being solved here — you were handed "
                     "a symbol and asked what number it is, and it is one number. "
                     "**No equation, no ±.**"},
            {"name": "Solving x² = 9 and keeping only the positive answer.",
             "wrong": "x² = 9  →  x = 3",
             "right": "-3 × -3 = 9,  so x² = 9  →  x = ±3",
             "note": "This is the mirror image of the mistake above, and it is the "
                     "more common one. Here there is **no radical sign in the "
                     "question** — you put one there yourself by taking the square "
                     "root of both sides, and that is exactly when both signs count. "
                     "Ask which word the problem used: *simplify* means one answer, "
                     "*solve* means two."},
            {"name": "Refusing a negative under an odd root.",
             "wrong": "³√-27 = no answer",
             "right": "-3 × -3 × -3 = -27  →  ³√-27 = -3",
             "note": "Odd roots take negatives happily. Three negative factors leave "
                     "one minus sign unpaired, so the product is negative — which "
                     "means a negative number really does have a cube root. The "
                     "\"no negatives inside\" instinct comes from square roots and "
                     "does not travel."},
            {"name": "Allowing a negative under an EVEN root.",
             "wrong": "⁴√-16 = -2",
             "right": "-2 × -2 × -2 × -2 = 16  →  ⁴√-16 is not a real number",
             "note": "Four negative factors pair off completely, so the product comes "
                     "out **positive 16**, not -16. Take an even count of identical "
                     "factors and the minus signs always pair off, so the product can "
                     "never be negative. An odd-numbered root takes a negative inside; "
                     "an even-numbered root does not."},
            {"name": "Counting the wrong number of factors.",
             "wrong": "³√8 = 4",
             "right": "2 × 2 × 2 = 8  →  ³√8 = 2",
             "note": "That answer came from halving 8 instead of counting factors — "
                     "one step, when the little number asked for three. The little "
                     "**3** is an instruction: "
                     "find **three** identical factors. Say it out loud — \"what times "
                     "what times what\" — with one *what* per count."},
            {"name": "Trying to solve two unknowns out of one equation.",
             "wrong": "m + s = 10  →  m = 5 and s = 5",
             "right": "m + s = 10 and m + 2s = 14  →  s = 4  →  m = 6",
             "note": "5 and 5 is not wrong arithmetic — it is a guess that happens to "
                     "fit the one equation it was tested against. Feed it to the "
                     "second equation and 5 + 10 gives 15, not 14. **The number of "
                     "equations must equal the number of unknowns**, and until it does "
                     "there is nothing to solve."},
            {"name": "Moving a number across and adding it instead of subtracting.",
             "wrong": "s + 10 = 14  →  s = 24",
             "right": "s + 10 = 14  →  s = 14 - 10 = 4",
             "note": "Old habit, new place to trip on it. Whatever you do, do it to "
                     "**both** sides: taking 10 off the left leaves `s`, and taking 10 "
                     "off the right leaves 4. Fast catch — 24 in an equation whose "
                     "biggest number is 14 cannot be right, and noticing that takes no "
                     "algebra at all."},
        ],
    }),

    (B.KIND_REVEAL, {
        "prompt": "Practice problem 484 says: Solve x² = 49. How many answers does it "
                  "have, and what are they? Work it out before you open this.",
        "answer": "Two answers: **x = +7** and **x = -7**. Check them both: 7 × 7 "
                  "gives you 49, and -7 × -7 also gives you 49, so both really do "
                  "work. The reason you are allowed two is the word **solve** — you "
                  "are taking the square root of both sides of an equation, and that "
                  "is the job where the negative comes along. Now notice the "
                  "difference: if the question had said *simplify √49*, the answer "
                  "would be **7** on its own, because the radical sign means the "
                  "principal square root. Same number, different question, different "
                  "number of answers.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**To solve a system, the number of equations must equal the number of "
            "unknowns.** Two letters means you go looking for two sentences before "
            "you start.",
            "A **system** is two or more equations solved **together**, because they "
            "describe the same unknowns. Saxon also calls them **simultaneous** "
            "equations — they are true at the same time.",
            "The method: **rearrange both equations so the same letter stands alone, "
            "set the two other sides equal, solve, then substitute back.** Check the "
            "pair in **both** originals, never just one.",
            "On a graph, the solution of a system is **where the lines cross**, "
            "written as an **ordered pair** — x first, y second, like `(3, 1)`.",
            "**Simplifying `√9` gives one answer, 3.** The radical sign means the "
            "**principal** square root, which is the positive one.",
            "**Solving `x² = 9` gives two answers, `x = ±3`**, because you took the "
            "square root of both sides of an equation. You drop the negative one only "
            "when the question makes it meaningless — a distance, for instance.",
            "The little number on a radical sign is a **count of identical factors**: "
            "2 for a square root, 3 for a cube root, n for an nth root. `√x` is really "
            "`²√x` with the 2 left off.",
            "**Odd roots may hold a negative inside; even roots may not.** "
            "`⁵√-32 = -2` is fine. `⁴√-16` is not a real number at all.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 84 first. If it didn't quite land, this is here to fix that. "
    "There are two topics on this page and they share one habit: counting. Count the "
    "unknowns and make sure you have that many equations. Count the little number on "
    "the radical sign and look for that many identical factors. There is also one "
    "genuinely tricky idea — why √25 has one answer but x² = 25 has two — and it gets "
    "a section of its own."
)

PARENT_CONTENT = """## The big idea

Two topics share this page, and the honest thing to tell her is that they are not
related — they are two separate small ideas that happen to be scheduled together.
Do not manufacture a connection. Teach them as two sittings if she is tired.

**Systems of equations** is one rule and one method. The rule: *to solve any system
of equations, the number of equations must equal the number of unknowns.* The
method the book uses: get both equations to say `m = something`, set the two
somethings equal to each other, solve the one-unknown equation that is left, then
substitute back.

The whole reason it works is worth saying to her explicitly, because it is not
mysterious and she already believes it: **if two things are both equal to m, they
are equal to each other.** That is the entire move. Everything else on the page is
ordinary Lesson 68 equation-solving.

**Roots** is the other half, and it contains the one genuinely subtle idea in the
lesson:

- `√25 = 5`. One answer. When you **simplify** a root that is already written down,
  you take the **principal square root**, which is defined as the positive one.
- `x² = 25` gives `x = ±5`. Two answers. When you **solve an equation** by taking
  the square root of both sides, both signs are legitimate, since (-5)² and (5)²
  both equal 25.

Most textbooks blur this. Saxon does not, and neither should you. The
distinguishing question is which verb the problem used: **simplify** means one
answer, **solve** means two. She will meet this again in quadratics for years, so
it is worth fifteen extra minutes now.

The rest of the roots material is just counting: the little number on the radical
sign says how many identical factors to hunt for. Two for a square root, three for
a cube root, n for an nth root. The only extra rule is about signs — **a negative
may sit inside an odd root but never inside an even one**, because an odd number of
negative factors leaves one minus sign unpaired.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. **"Two numbers add up to ten. What are they?"** Wait. Let her offer nine and one.
   Say *"could be"* and write it down. Let her offer six and four. Write that down
   too. Then ask: **"How many pairs work?"** — you want her to realise it is endless.
   That feeling is the whole motivation for a system, and it takes twenty seconds.
2. Now add the second fact: **"Same two numbers. This time take the first one and
   add the second one twice, and you get fourteen. Now which pair survives?"** Let
   her hunt. She may well find 6 and 4 by trying. Let her — then say the important
   sentence: *"You just solved a system. Now let me show you the method for when the
   numbers aren't friendly."*
3. Write both equations, `m + s = 10` and `m + 2s = 14`. Ask: **"How many mystery
   letters, and how many sentences?"** Two and two. That is the counting rule, and
   asking it as a question makes it hers.
4. Rearrange both to `m = -s + 10` and `m = -2s + 14`. Then ask the key question:
   **"Both of those are equal to m. So what do you know about them?"** You want
   *"they're equal to each other."* Do not say it for her — this one line is the
   entire lesson, and she can produce it.
5. Set them equal, solve for `s = 4`, substitute back for `m = 6`. Then ask the
   checking question: **"Does that work in the OTHER equation too?"** 6 + 2(4) = 14.
   Insist on both. Checking against only the equation you just used catches nothing.

Then, separately — a different sitting is fine — do the roots half:

6. Write `√9` and ask **"what times what is nine?"** She says three. Now write
   `-3 × -3` on the board and ask: **"Isn't that nine as well? So why isn't -3 an
   answer?"** Let the objection sit. Then tell her the answer: because the radical
   sign means the *principal* square root, and that one is positive by definition.
7. Now write `x² = 9` beside it and ask: **"Is that the same question?"** It is not.
   There is no radical sign in it. She solves it by taking the square root of both
   sides, and there both answers count: `x = ±3`. Put the two lines side by side on
   the paper and leave them there for the rest of the session.
8. Finally write `³√8` and ask **"what times what times what is eight?"** Then
   `⁵√-32`. Let her discover on her own that an odd number of negatives stays
   negative. That discovery is worth more than the rule.

## The classic mix-ups, with the exact wrong answer each one produces

- **Giving a simplified root two answers.** She writes `√9 = ±3` instead of
  **`√9 = 3`**. Fix: no equation in the question means no `±`. The radical sign
  hands back exactly one number and it is positive.
- **Solving `x² = 9` and keeping only the positive.** She writes **`x = 3`** instead
  of **`x = ±3`**. This is the more common half of the pair. Fix: the question had
  no radical sign in it — *she* put one there by taking the root of both sides, and
  that is precisely when both signs count.
- **Refusing a negative under an odd root.** She writes **"no answer"** for `³√-27`
  instead of **-3**. Fix: -3 × -3 × -3 = -27, so it plainly does have one. The "no
  negatives inside" instinct belongs to square roots and does not travel.
- **Allowing a negative under an even root.** She writes **`⁴√-16 = -2`**. Fix: work
  it out forwards — -2 × -2 × -2 × -2 = **+16**, not -16. Four negatives pair off
  completely.
- **Counting the wrong number of factors.** She writes **`³√8 = 4`**, having halved
  8. Fix: the little 3 is an instruction. Make her say "what times what times what"
  with one *what* per count.
- **Solving for two unknowns from one equation.** Given only `m + s = 10` she
  produces **m = 5, s = 5** and calls it done. Fix: test it in the second equation —
  5 + 2(5) = 15, not 14. Two unknowns need two equations; until then there is
  nothing to solve.
- **The sign slip on the last line.** From `s + 10 = 14` she writes **`s = 24`**.
  Fix: do it to both sides. Fast catch — 24 cannot come out of an equation whose
  largest number is 14.

## What to watch her do

Watch her **hands**, in this order:

1. Does she **write down what each letter means** before she writes any equation?
   `m = man's height`. If the letters float unlabelled she will solve correctly and
   then report the daughter's height as the man's — a lost mark on a problem she
   actually understood.
2. Does she **count** before she solves — letters, then equations? You want to see
   her eyes go back to the problem looking for a second sentence, not a pencil
   starting straight into algebra.
3. When she sets the two right-hand sides equal, **does her pencil hesitate?** A
   hesitation there means she is copying the shape of the method without believing
   the reason. Stop and re-ask "both of these equal m, so what do you know?"
4. At the end, does she **substitute into both original equations**, or does she
   check the one she just used? Checking against the equation you solved from is
   free and proves nothing. Watch for the pencil going back up to the *first*
   equation.
5. On the roots half, watch whether her finger or pencil **counts the factors** —
   three taps for a cube root. Mental counting is where `³√8 = 4` comes from.
6. And the one that matters most: when she meets `x² = 49`, does she **stop and look
   at the verb**? A visible pause before writing `±` is the habit this lesson exists
   to build.

## Extend it

- Give her a system with **no solution**: `m + s = 10` and `m + s = 12`. Set them
  equal and everything cancels, leaving `10 = 12`, which is false. Graphed, the two
  lines are parallel and never cross. She is not expected to know this yet, and
  meeting it as a puzzle is far better than being told the rule later.
- Then give her `m + s = 10` and `2m + 2s = 20` — the second is the first one
  doubled, so it is not a new fact at all. Every pair that works for one works for
  the other. This is the counting rule biting from a direction she will not expect:
  two equations written down, but only one piece of information.
- Ask her for `√-9`. There is no real answer, and she can prove it herself: any
  number times itself is positive or zero. That is a genuinely satisfying thing for
  a twelve-year-old to establish on her own, and it sets up imaginary numbers later.
- Ask what `⁶√64` is, then `³√64`, then `√64`. Same 64, three different counts,
  three different answers (2, 4 and 8). Nothing shows what the little number *does*
  better than holding the inside still and changing only that number.

## Where this sits

DIVE Lesson 84. Reviews Lessons 30, 54, 68 and 78. **Lesson 54 is the one to
revisit if she is lost on the second half** — that is where square roots were used
to solve equations, and where the distance case first made her throw a negative
answer away. Lesson 30 is the original square-root definition. Lesson 68 is the
linear-equation work the whole systems half rests on.

**About the figures.** Example 84.2 and practice problem 284 are graphs in her DIVE
book, and Example 84.4's worked lines are printed as images — the lines themselves
were not visible to whoever built this page, so they are not redrawn here. What the
book states about 84.2 is the crossing point, so the page draws exactly that: a
read-only grid with one locked dot at (3, 1), for practising how an ordered pair is
read off a grid. The rest of 84.2 is rebuilt from Example 84.1's own numbers, and
84.4 is written out in symbols. She is told this in plain words on her own page, so
she is not left wondering what she is missing — have the book open beside her for
the two lines, and for problem 284.

**Proficient** looks like: solves a two-equation system correctly with the book's
method, and simplifies square and cube roots of perfect powers.
**Mastered** looks like: gets `√25` and `x² = 25` right in the same sitting without
being reminded which is which, and knows why `⁵√-32` is fine while `⁴√-16` is not.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 84 (systems of equations; more on roots "
            "and radical signs) — idempotent.")

    LESSON_NUMBER = 84
    TITLE = "Systems of Equations; More on Roots and Radical Signs"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
