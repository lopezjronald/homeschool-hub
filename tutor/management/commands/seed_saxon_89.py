"""Saxon Pre-Algebra Lesson 89 — Infinitesimals and the Limit.

Her first real piece of calculus, and the first of the book's "Big 3" (limits
here, derivatives in Lesson 90, integrals in Lesson 94).

Reviews Lessons 5, 23, 26, 66, 76 and 81. **Lesson 76 is the hook, and the source
names it itself** — it sends her back to Ex. 76.2a, where a hollow dot at (4, 2)
kept x = 4 out of the domain (`-2 ≤ x < 4`). Lesson 89 keeps that exact picture and
turns the question round: stop looking at the 4 that is excluded and look at the
3.9, 3.999, 3.99999999 that are not. **Lesson 81 is the second hook**, twice over:
it is where calculus was first named, and where the book's Hebrews 11:1
"reasonable faith" was first raised — and 89 names it once, for the faith-and-reason
point. Lesson 66 supplies
the word *discontinuous*, Lesson 26 the open circle, Lesson 62 (not on the review
line, but cited in the solution) relation-versus-function. Lessons 5 and 23 are on
the book's review line but this guide has not read them and nothing on these pages
leans on them, so nothing here describes what is in them.

Taught at the source's level and no deeper. A limit here is "the number the output
heads for"; a one-sided limit is "which side you walked in from." Nothing about
two-sided limits failing to exist, nothing about continuity criteria, nothing
about infinite limits — the source's own closing note caps the whole lesson at
*two possible answers, the open circle's output or the closed circle's*, and going
past that would contradict the page she is working from.

FIGURES. Three kinds, handled three different ways:

* **Ex. 89.1's graph is DRAWN** — a KIND_TOOL grid, `locked` and `readonly`, built
  only from what the guide's own solution states about it: break at x = 2, two
  horizontal rays, the bottom one to the left and the top one to the right. Same
  precedent as Lesson 81's page-4 parabola. Her page says plainly that the board
  draws every dot hollow, so the open/closed distinction at x = 2 is missing.
* **Ex. 89.2's graph is DESCRIBED, not drawn.** The solution states the break
  (x = 1), which piece lives on which side, and both endpoint outputs (2 and -4) —
  but says only that the pieces are "not horizontal", never their slopes. Drawing
  it would mean inventing them.
* **The two "YOU ARE HERE" cliff sketches and page 1's photograph of a children's
  baseball team** are not reproduced and nothing depends on them; her page says so
  in one sentence for the cliff sketches, which sit inside the Ex. 89.1 walk-through.

JUDGEMENT CALL — a discrepancy in the source, carried openly rather than silently
fixed. On page 3 the Ex. 89.1 solution says the two rays are "one at y=2, and the
other at y=-5", then answers `f(2+) = 3` two lines later, and its own closing note
says "the only choices for answers were 3 and -5." Two votes for 3 against one for
2, and the stray 2 is the x of the break. So the top ray is taken as y = 3 — the
board draws 3, and both her page and the parent guide say why, so a reviewer
comparing against the PDF does not read it as an error introduced here.

Ex. 89.2's two question lines reach this file as images. They are reconstructed
from the guide's own solution text ("1+ tells us to approach from the right",
"1- tells us to approach from the left") as `lim x→1⁺ f(x)` and `lim x→1⁻ f(x)`,
and her page says that is what happened and asks her to check her book.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_89 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

# Example 89.1's graph, as dots. Two horizontal rays either side of a break at
# x = 2: the bottom one (y = -5) owns everything to the left, the top one (y = 3)
# owns everything to the right, and both have an end sitting at x = 2. Every
# coordinate here comes from the guide's own solution paragraph — see the module
# docstring for the one number that had to be adjudicated.
EX_89_1_POINTS = (
    [[x, -5] for x in range(-6, 3)]      # the bottom ray, running off to the left
    + [[x, 3] for x in range(2, 7)]      # the top ray, running off to the right
)

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 89 · Pre-Algebra",
        "title": "Walk right up to the edge. Read your altitude.",
        "thesis": "A limit is the number a function **heads for** — not the number "
                  "it arrives at. You get infinitely close to an x you are never "
                  "allowed to touch, and you write down where the output was going.",
        "formula": "lim x→c f(x) = L",
        "roles": [
            {"tone": "start", "name": "the arrow → — approaching, never arriving",
             "text": "`x → 2` means x gets so close to 2 that nobody can name the "
                     "gap, and still never equals 2. The refusing-to-arrive is the "
                     "whole idea."},
            {"tone": "move", "name": "the little ⁻ or ⁺ — which side you walked in from",
             "text": "`2⁻` means x is *smaller* than 2, so you came from the left. "
                     "`2⁺` means x is bigger, so you came from the right. It is a "
                     "direction, not a minus sign."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody invented a number you never reach",
        "paragraphs": [
            "Picture yourself at the Grand Canyon, walking towards the rim. You are a "
            "metre from the edge. Then half a metre. Then a hand's width. Then close "
            "enough to feel the air move, and you stop, because stopping is the "
            "sensible thing to do at the edge of a canyon.",
            "You never stepped off. Your feet never touched the very last inch of "
            "rock, and they never will. And yet anybody watching could say exactly "
            "what your altitude was heading for, because they could see the ground "
            "you were walking in on. That number — where your height was **going**, "
            "not where you got to — is a limit.",
            "Your book opens this lesson slightly annoyed on your behalf. Nobody "
            "walks up to a six-year-old holding a bat and tells her she is too young "
            "for baseball. Plenty of adults will tell a pre-algebra student she is "
            "too young for calculus. A six-year-old cannot play in the major leagues, "
            "and you are not about to sit a calculus exam — but there are things "
            "about it you can learn right now, and this is the first of them.",
            "Calculus has three big ideas: **limits**, **derivatives** (Lesson 90) "
            "and **integrals** (Lesson 94). You are starting with the first, and the "
            "book makes you a promise worth holding it to — everything you learn "
            "about calculus now is built out of things you already know.",
            "It is not exaggerating. Today comes out of the **hollow dot** you have "
            "been drawing since Lesson 26 and used again in Lesson 76, and Lesson 81 "
            "already told you what calculus is for. What is new today is mostly "
            "notation. You are being asked to look at an old picture from a "
            "different angle.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "An infinitesimal is how close you can get without arriving",
        "paragraphs": [
            "Go back to **Lesson 76** for a moment — your book asks you to, by name. "
            "In Example 76.2a there was a graph with a hollow dot at (4, 2), and you "
            "wrote the domain as `-2 ≤ x < 4`. The hollow dot meant *4 is not in*.",
            "Now stop looking at what is left out and look at what is left **in**. "
            "3.9 is in. So is 3.999. So is 3.99999999. So is a number with a thousand "
            "nines after the point, and one with a million. Every one of them is "
            "allowed in that domain. Not one of them is 4.",
            "How far is 3.99999999 from 4? A tiny distance — and you can always name "
            "a smaller one, and then a smaller one than that, forever, without ever "
            "running out. A gap like that, smaller than any gap you could name and "
            "still not zero, is called an **infinitesimal**. Your book is honest that "
            "this is hard: these are values so close together that our minds cannot "
            "fully hold how close. We work with them anyway.",
            "That is the faith-and-reason point your book raised in **Lesson 81** and "
            "raises again here — the Hebrews 11:1 kind of reasonable faith. You "
            "cannot picture an infinitesimal. You can still reason with one perfectly "
            "well, and the whole of calculus is built on top of it.",
            "Which makes the definition shorter than you would expect. Your book "
            "gives it in one line: a **limit** is *the application of infinitesimals "
            "to evaluating a function.* You feed the function inputs that are an "
            "infinitesimal away from some x — never that x itself — and you watch "
            "where the outputs go.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Put your finger on the 4 on a ruler. Now give me a number that's "
                "close to 4 but isn't 4. Three point nine? Good — give me a closer "
                "one. Closer than that. Closer again. Now two questions, and think "
                "before you answer: are you ever going to run out of numbers? And are "
                "you ever going to land on 4? Both answers are no, and the second one "
                "is the whole lesson.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "The notation is six marks and one word",
        "paragraphs": [
            "Math is a language — your book says so on this page, the way it said so "
            "back in Lesson 1 — so that strange row of symbols has an ordinary "
            "sentence hiding inside it. The sentence is: **the limit of f(x), as x "
            "approaches c, is L.**",
            "`lim` is short for limit. `x → c` is read *x approaches c*, and "
            "*approaches* is doing real work there, because the definition adds "
            "*gets infinitesimally close to, but not equal to*. `f(x)` is the machine "
            "from Lesson 76. `L` is the one number the outputs head for.",
            "Then comes the second half, which is what makes this lesson possible at "
            "all. You can walk up to c from either side, and you can be asked about "
            "one side at a time. A small **minus** on the c means you came from the "
            "left, where x is *smaller* than c. A small **plus** means you came from "
            "the right, where x is *bigger* than c.",
            "Those two are called the **left-hand limit** and the **right-hand "
            "limit**. Say them with your hands if it helps: left is the side where "
            "the numbers are smaller, right is the side where they are bigger, "
            "exactly the way a number line has always worked.",
            "One warning now, because it saves whole problems later. That little ⁻ "
            "is **not** a minus sign on the answer, and it is not an exponent. It is "
            "a direction. Example 89.1 is about to hand you -5 for the left-hand "
            "limit, and you will be tempted to think the minus caused it. Example "
            "89.2 hands you a positive 2 for the left-hand limit, so the temptation "
            "is a trap that gets sprung one page later.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "lim x→c f(x) = L",
        "note": "Read it as a sentence: **the limit of f of x, as x approaches c, is "
                "L.** Then add the clause the definition is careful about — x gets "
                "infinitesimally close to c, *but not equal to c*. Every other `lim` "
                "expression in this lesson is this same line with a tiny ⁻ or ⁺ stuck "
                "on the c to say which side you walked in from.",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Nothing here is a calculation. Every one of these is a label, and "
                 "the reason this lesson looks difficult is that thirteen of them "
                 "turn up on one page. **Six** are genuinely new marks — `lim`, `→`, "
                 "`c`, `L`, `⁻` and `⁺` — with one new word, *infinitesimal*, beside "
                 "them. Two more rows, `x → c` and `f(2⁺)`, are nothing but those new "
                 "marks put together, which is why they look harder than they are. "
                 "The last four you already own outright: `Δx` from Lesson 81, the "
                 "hollow and filled dots from Lessons 26 and 76, and *discontinuous* "
                 "from Lesson 66. Read down the whole list anyway before you look at "
                 "the examples.",
        "rows": [
            {"symbol": "lim", "plain": "short for LIMIT — the one number the outputs "
                                       "head for",
             "example": "lim x→2⁺ f(x)"},
            {"symbol": "→", "plain": "approaches. Not equals, not becomes, not gives",
             "example": "x → 2"},
            {"symbol": "x → c", "plain": "x gets infinitesimally close to c, but never "
                                         "equal to c",
             "example": "x → 2"},
            {"symbol": "c", "plain": "the x-value you are walking towards. On these "
                                     "pages it is where the break is",
             "example": "c = 2 in Ex. 89.1"},
            {"symbol": "L", "plain": "the limit itself — the altitude you read when "
                                     "you stop",
             "example": "L = 3"},
            {"symbol": "2⁻", "plain": "a hair to the LEFT of 2, where x is smaller "
                                      "than 2",
             "example": "1.9, 1.999, 1.99999999"},
            {"symbol": "2⁺", "plain": "a hair to the RIGHT of 2, where x is bigger "
                                      "than 2",
             "example": "2.1, 2.001, 2.000001"},
            {"symbol": "f(2⁺)", "plain": "the output as you arrive at 2 from the right "
                                         "side",
             "example": "f(2⁺) = 3"},
            {"symbol": "Δx", "plain": "a change in x — the same Δ as Lesson 81. Here "
                                      "it is an infinitesimally small one",
             "example": "2 plus a tiny Δx"},
            {"symbol": "○", "plain": "open circle: that point is NOT on the graph "
                                     "(Lesson 26, Lesson 76)",
             "example": "the end that is left out"},
            {"symbol": "●", "plain": "closed circle: that point IS on the graph",
             "example": "the end that is included"},
            {"symbol": "infinitesimal", "plain": "a gap smaller than any gap you can "
                                                 "name, and still not zero",
             "example": "4 − 3.99999999"},
            {"symbol": "discontinuous", "plain": "a graph with a jump or a break in it "
                                                 "(Lesson 66)",
             "example": "the break at x = 2"},
        ],
        "after": "The two that cause the trouble are `2⁻` and `2⁺`. They are not "
                 "exponents — nothing is being raised to a power — and they are not "
                 "the sign of the answer. They are **directions**, and the only "
                 "question they answer is *which side of the break am I standing on*.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe",
        "title": "Four moves, and not one of them is arithmetic",
        "steps": [
            {"label": "Find the break, and call it c.",
             "detail": "These are **discontinuous** functions — Lesson 66's word for a "
                       "graph with a jump or a break in it. Find the x where the graph "
                       "tears in two. It will be the number already sitting under the "
                       "arrow, so this step is really a check that you are looking at "
                       "the right place on the picture."},
            {"label": "Read the little mark and turn it into a word.",
             "detail": "**⁻ means from the left**, where x is smaller than c. **⁺ "
                       "means from the right**, where x is bigger than c. Say *left* "
                       "or *right* out loud **before** you look at the graph, so you "
                       "are not deciding it and reading it at the same time."},
            {"label": "Ask which piece actually exists on that side.",
             "detail": "This is the whole lesson. Put your hand over the other side of "
                       "the break. Whatever piece of graph is still showing is the one "
                       "you walk on. Do not decide it by top and bottom — in Ex. 89.1 "
                       "the right-hand side is the top piece, and in Ex. 89.2 the "
                       "right-hand side is the bottom one.",
             "math": "c = 2,  from the right  →  only the top ray is over there"},
            {"label": "Walk along that piece to the end and read your altitude.",
             "detail": "Your finger travels along the **graph**, not along the x-axis. "
                       "Where the piece stops, look straight across to the y-axis and "
                       "read the number. That is L. Then write it as an answer to the "
                       "question you were actually asked, mark and all.",
             "math": "lim x→2⁺ f(x) = 3"},
        ],
        "after": "Then use the book's own check, which is the most useful sentence in "
                 "the lesson. On any Lesson 89 problem there are only ever **two** "
                 "possible answers: the output at the open circle, and the output at "
                 "the closed circle. In Ex. 89.1 the only two numbers available in the "
                 "whole universe were 3 and -5. So if you have written a third number, "
                 "you have not made an arithmetic slip — there is no arithmetic here. "
                 "You have read the wrong thing off the picture, and you should go back "
                 "to move 3.",
    }),

    (B.KIND_TOOL, {
        "title": "Example 89.1, drawn",
        "intro": "This is the graph from Example 89.1, rebuilt out of dots from your "
                 "book's own description of it: a discontinuous function with a break "
                 "at **x = 2**, two horizontal rays, the bottom one at y = -5 running "
                 "off to the left and the top one at y = 3 running off to the "
                 "right.\n\nNothing on this board can be moved or knocked off — it is "
                 "a picture to read, like the one in your book. Read it with your "
                 "hand: cover the right half and see what is left, then cover the left "
                 "half and see what is left.",
        "widget": "grid",
        # `locked` puts the figure in the read-only layer so a stray tap cannot move
        # a dot; `readonly` removes the control bar as well, because Undo and Clear
        # would otherwise offer to erase the only picture she has of this example.
        # No `curve` — none of the widget's function families is this shape, and the
        # dots ARE the graph. Both spans are 12 so the squares stay square.
        "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                   "points": EX_89_1_POINTS,
                   "locked": True,
                   "readonly": True,
                   "label": "Example 89.1 — a discontinuous function with a break at "
                            "x = 2, a ray at y = -5 to the left and a ray at y = 3 "
                            "to the right"},
        "after": "Two honest notes about this board.\n\n"
                 "**Every dot here is drawn hollow**, because that is how this board "
                 "draws a picture it has locked — hollow is its way of saying *this was "
                 "already here, you did not plot it*. In your book, one of the two "
                 "ends at x = 2 is hollow and the other is filled in. That difference "
                 "is not decoration — it is what makes this a **function** rather than "
                 "a relation, and there is an idea about it further down the page. It "
                 "does not change either answer.\n\n"
                 "**And one number had to be decided.** Your book's solution paragraph "
                 "calls the top ray `y = 2`, then answers **3** two lines later, and "
                 "its own closing note says the only choices were 3 and -5. So the top "
                 "ray is at **y = 3**, and that stray 2 is the x of the break leaking "
                 "into the sentence. This board draws 3, which is what your answers "
                 "should say.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 89.1 — one break, asked from both sides",
        "equation": "find    a) lim x→2⁺ f(x)        b) lim x→2⁻ f(x)",
        "steps": [
            {"label": "Look first",
             "text": "One graph, one break, two questions — and the only difference "
                     "between a) and b) is a mark the size of a full stop. Everything "
                     "else is identical, so whatever makes your two answers different "
                     "has to come from that mark and nothing else.\n\nYour book draws "
                     "two little sketches beside this example with **YOU ARE HERE** "
                     "written on them. This page cannot copy them, and you do not need "
                     "them — they are pictures of the sentence you are about to read."},
            {"label": "Step 1 · a) read the mark",
             "text": "The `⁺` means *from the right side*, or *from the right hand*, "
                     "or — your book's third way of putting it — *plus an "
                     "infinitesimally small value for Δx*. All three say the same "
                     "thing: x is a hair bigger than 2. You are standing to the right "
                     "of the break.",
             "math": "x → 2⁺   →   x = 2.1, 2.001, 2.000001, ..."},
            {"label": "Step 2 · a) which piece is over there?",
             "text": "Cover everything left of x = 2 on the board above. Only the "
                     "**top** ray is still showing. The bottom ray does not exist on "
                     "that side at all, so it cannot be the answer — no matter how "
                     "much closer to the middle of the picture it happens to sit.",
             "math": "right of x = 2   →   the top ray, and only the top ray"},
            {"label": "Step 3 · a) walk to the edge and stop",
             "text": "Here is your book's picture, and it is a good one. You are "
                     "walking along the top ray towards the Grand Canyon, and the edge "
                     "is at x = 2. Go any further and you fall off, so do not. The "
                     "limit is your **altitude** as you stand at that edge.",
             "math": "f(2⁺) = 3"},
            {"label": "Step 4 · b) read the other mark",
             "text": "The `⁻` means *from the left side*, or *from the left hand*, or "
                     "*minus an infinitesimally small value for Δx*. x is a hair "
                     "smaller than 2. Same graph, other side, and that is the entire "
                     "change.",
             "math": "x → 2⁻   →   x = 1.9, 1.999, 1.999999, ..."},
            {"label": "Step 5 · b) which piece is over there?",
             "text": "Cover everything right of x = 2. Now only the **bottom** ray is "
                     "showing. So this time you are down at the bottom of the canyon, "
                     "walking towards the cliff face. Go any further and you smack "
                     "your nose into the rock, so stop.",
             "math": "left of x = 2   →   the bottom ray, and only the bottom ray"},
            {"label": "Step 6 · b) read your altitude again",
             "text": "Standing at the foot of the cliff, your altitude is -5. Same "
                     "walk, same rule, different piece of graph — because a different "
                     "piece of graph was the only one there.",
             "math": "f(2⁻) = -5"},
            {"label": "Check · were there only ever two numbers available?",
             "text": "Yes — 3 and -5, the two ends at the break. Your book says so in "
                     "a note under the example, and it is the fastest check you own. "
                     "Any answer that is not one of those two came from misreading the "
                     "picture.",
             "math": "lim x→2⁺ f(x) = 3        lim x→2⁻ f(x) = -5"},
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "start",
        "title": "Example 89.2 changes one thing, and it is the thing that does not matter",
        "paragraphs": [
            "Your book is blunt about this one. *The ONLY difference between Ex. 89.1 "
            "and Ex. 89.2 is that in Ex. 89.2, the two function pieces are not "
            "horizontal.* And it says in the very next sentence that this has **no "
            "effect** on how you solve the problem.",
            "That is worth a second of your attention. In 89.1 the two pieces were "
            "flat, so *read your altitude at the end* was easy — the altitude had been "
            "the same the whole walk. In 89.2 the pieces are slanted, so your altitude "
            "has been changing every step. It still does not matter, because you only "
            "ever read it at **one place**: the end, where the piece stops at the "
            "break.",
            "What has genuinely changed is where things sit. The break is at **x = 1**, "
            "not 2. And the two pieces have swapped sides. In 89.1 the piece living to "
            "the right of the break was the top one. In 89.2 the piece living to the "
            "right is the **bottom** one, and the top piece exists only to the left.",
            "So the rule you may have quietly formed while working 89.1 — *from the "
            "right means the top piece* — is wrong, and 89.2 turns up on the next page "
            "partly to break it before you get attached to it. Cover the side you were "
            "not asked about. Whatever is left is what you walk on. That is the only "
            "rule there is, and it does not care which piece is higher.",
            "One thing about the printing. In your book the two questions for this "
            "example are set as pictures, and the pictures did not survive being "
            "copied onto this page. They are `lim x→1⁺ f(x)` and `lim x→1⁻ f(x)`, "
            "rebuilt from the book's own solution, which opens *\"1+ tells us to "
            "approach from the right\"* and *\"1- tells us to approach from the "
            "left.\"* Glance at your book and check the two agree before you start.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "89.2",
        "question": "For the discontinuous function shown — two slanted pieces with a "
                    "break at x = 1 — find a) lim x→1⁺ f(x)   b) lim x→1⁻ f(x)",
        "steps": [
            {"label": "What the picture is, in words",
             "text": "This graph is not redrawn here, because your book only says the "
                     "pieces are *not horizontal* and never says how steep they are — "
                     "so any drawing would be a guess. What the solution does tell you "
                     "is enough to work from, and it is all here: the break is at "
                     "**x = 1**; the **top** piece exists only to the **left** of "
                     "x = 1 and its end there is at 2; the **bottom** piece exists "
                     "only to the **right** of x = 1 and its end there is at -4. If "
                     "your book is open beside you, check those three facts against "
                     "the picture. Everything below follows from them."},
            {"label": "a) from the right — so which piece is over there?",
             "text": "`1⁺` says approach from the right, where x is bigger than 1. The "
                     "top piece exists only to the left of x = 1, so it is simply not "
                     "available. That leaves the bottom piece, and you are walking "
                     "towards the base of a cliff at x = 1, exactly as in 89.1b.",
             "math": "right of x = 1   →   the bottom piece"},
            {"label": "a) read the altitude at the end",
             "text": "Walk along the bottom piece until it stops at x = 1, then look "
                     "straight across. Your altitude there is -4. The slant made no "
                     "difference at all — you only ever read the end.",
             "math": "f(1⁺) = -4"},
            {"label": "b) from the left — so which piece is over there?",
             "text": "`1⁻` says approach from the left, where x is smaller than 1. "
                     "This time only the top piece exists, so you are up on top of the "
                     "cliff walking towards the edge.",
             "math": "left of x = 1   →   the top piece"},
            {"label": "b) read the altitude at the end",
             "text": "The top piece stops at x = 1 with an output of 2. Stand there "
                     "and read it.",
             "math": "f(1⁻) = 2"},
            {"label": "Check · and look at what happened to the signs",
             "text": "Only two numbers were available — 2 and -4, the two ends at the "
                     "break — and both answers are among them, so the reading was "
                     "sound. Now compare with 89.1. There, the **left**-hand limit was "
                     "the negative one. Here, the left-hand limit is the **positive** "
                     "one and the right-hand limit is negative. The marks were never "
                     "about signs.",
             "math": "lim x→1⁺ f(x) = -4        lim x→1⁻ f(x) = 2"},
        ],
        "answer": "-4   ·   2",
    }),

    (B.KIND_REVEAL, {
        "prompt": "In Example 89.1, *approach from the right* put you on the top "
                  "piece. In Example 89.2, *approach from the right* put you on the "
                  "bottom piece. Same words, opposite halves of the picture. So what "
                  "actually decides it?",
        "answer": "**Which piece exists on that side. Nothing else.** *Top* and "
                  "*bottom* were never part of the rule — they are just where the two "
                  "pieces happened to sit in one particular drawing.   →   In 89.1 the "
                  "graph to the right of x = 2 was the top ray, so from the right you "
                  "got 3.   →   In 89.2 the graph to the right of x = 1 was the bottom "
                  "piece, so from the right you got -4.   →   Which is why the "
                  "reliable move is a physical one: put your hand over the half of the "
                  "picture you were not asked about, and read whatever is still "
                  "showing. A rule you form from one drawing turns out to be a rule "
                  "about that drawing.",
    }),

    (B.KIND_TABLE, {
        "caption": "The two examples side by side — the same questions, asked twice",
        "headers": ["", "Example 89.1", "Example 89.2"],
        "rows": [
            {"cells": ["the break is at", "x = 2", "x = 1"]},
            {"cells": ["shape of the two pieces", "two horizontal rays",
                       "two slanted pieces"]},
            {"cells": ["what lives to the LEFT", "the bottom piece, ending at -5",
                       "the top piece, ending at 2"]},
            {"cells": ["what lives to the RIGHT", "the top piece, ending at 3",
                       "the bottom piece, ending at -4"]},
            {"cells": ["lim x→c⁻ f(x)   (from the left)", "-5", "2"],
             "emphasis": True},
            {"cells": ["lim x→c⁺ f(x)   (from the right)", "3", "-4"],
             "emphasis": True},
            {"cells": ["the only answers available anywhere", "3 and -5", "2 and -4"]},
        ],
        "note": "Read the two shaded rows **across**, not down. From the left the "
                "answers were -5 and 2 — one negative, one positive. From the right "
                "they were 3 and -4 — one positive, one negative. If the little mark "
                "decided the sign of the answer, that could not possibly happen. The "
                "mark decides the **side**; the side decides which piece; the piece "
                "decides the number. And notice the two rows above them: the pieces "
                "swapped sides between the two examples, which is the whole reason to "
                "look rather than to remember.",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "move",
        "title": "Why one of those two dots is hollow",
        "paragraphs": [
            "Go back to the break in Ex. 89.1 one last time. Two pieces end there, one "
            "at 3 and one at -5. Both ends are stacked on the same vertical line — "
            "the line at x = 2 — one of them high above the axis, the other well "
            "below it.",
            "That is a problem, and your book stops to fix it. A **function** is "
            "allowed exactly one output for each input — Lesson 62. If both ends at "
            "x = 2 were filled in, then f(2) would be 3 *and* -5 at the same time, and "
            "a picture like that is a **relation**, not a function.",
            "So one of the two ends is drawn as an **open circle** — the same hollow "
            "dot from Lesson 26 and Lesson 76. Hollow means *this point is not "
            "actually on the graph*. The other end is filled in, and that filled one "
            "is the real f(2). Your book puts it in a single line: **one open and one "
            "closed circle make this a function.**",
            "Now the part that surprises people. Being hollow does **not** put a value "
            "out of reach as an answer. Your book's own note says your two choices are "
            "the output at the open circle and the output at the closed circle — so in "
            "Ex. 89.1, one of 3 and -5 is sitting at a hollow dot, and it is still the "
            "correct answer to the question it belongs to.",
            "That is because a one-sided limit never asks what the function **is** at "
            "x = 2. It asks where the outputs were **heading** as you walked in. You "
            "can walk towards a step that is not there and still say, exactly and "
            "without any doubt, where you were going.",
        ],
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Reading the little mark as a minus sign.",
             "wrong": "lim x→1⁻ f(x)   →   \"the minus one\"   →   -4",
             "right": "lim x→1⁻ f(x)   →   from the LEFT   →   the top piece   →   2",
             "note": "**-4 instead of 2.** This one is dangerous because it works by "
                     "accident in Ex. 89.1: the left-hand limit there really is -5, "
                     "the negative one, and a rule that has just worked feels true. "
                     "Ex. 89.2 breaks it on the very next page. The mark is a "
                     "**direction** — ⁻ means x is smaller than c — and that is all it "
                     "has ever meant."},
            {"name": "Deciding by top and bottom instead of by side.",
             "wrong": "from the right, so the top piece   →   lim x→1⁺ f(x) = 2",
             "right": "from the right, so whatever exists right of x = 1   →   the "
                      "bottom piece   →   -4",
             "note": "**2 instead of -4.** In 89.1 the right-hand side happened to be "
                     "the top ray, and one example is all it takes for a rule to form. "
                     "Fix it with your hand rather than your memory: cover the half of "
                     "the picture you were not asked about, and read what is left "
                     "showing."},
            {"name": "Treating the little ⁺ as an exponent.",
             "wrong": "x → 2⁺   →   x → 4   →   read the graph at x = 4",
             "right": "x → 2⁺   →   x = 2.1, 2.001, 2.000001   →   read the end at x = 2",
             "note": "It sits up and to the right like a power, so it gets read like "
                     "one. It is not arithmetic at all. Your book does describe it as "
                     "*plus an infinitesimally small value for Δx* — but that addition "
                     "is a hair, not a number you work with. It nudges you a hair to "
                     "the right of 2 — to 2.1, then 2.001, then closer still. It "
                     "never carries you off to another whole number, and it certainly "
                     "never squares anything."},
            {"name": "Answering with a number that is not one of the two ends.",
             "wrong": "the ends are 3 and -5, so the limit is somewhere between   →   -1",
             "right": "lim x→2⁺ f(x) = 3        lim x→2⁻ f(x) = -5",
             "note": "There is nothing in between. The graph does not exist between the "
                     "two ends, and that gap is exactly what the word "
                     "**discontinuous** means (Lesson 66). Your book's note is the "
                     "shortest check on the page: on a Lesson 89 problem there are "
                     "only ever **two** possible answers, the value at the open circle "
                     "and the value at the closed circle. A third number means the "
                     "picture was misread."},
            {"name": "Thinking a hollow dot cannot be the answer.",
             "wrong": "that end is an open circle, so the limit from that side has no "
                      "answer",
             "right": "the limit from that side = the output at that end, hollow or "
                      "filled",
             "note": "The open circle says the function has no value **at** x = 2 on "
                     "that piece. A one-sided limit is not asking for the value at "
                     "x = 2 — it is asking where the outputs were heading on the way "
                     "in. Your book settles it in its own note: the two candidates are "
                     "the output at the open circle *and* the output at the closed "
                     "circle."},
            {"name": "Letting x actually arrive.",
             "wrong": "f(2) = 3   and   f(2) = -5",
             "right": "lim x→2⁺ f(x) = 3        lim x→2⁻ f(x) = -5",
             "note": "Written the first way it says the function has two outputs for "
                     "one input, which would make it a **relation** and not a function "
                     "at all (Lesson 62). The definition is careful for exactly this "
                     "reason: x gets infinitesimally close to c, *but not equal to* c. "
                     "Keep the `lim` and the arrow in front of your answer and this "
                     "cannot happen to you."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A **limit** is the one number f(x) heads for as x gets infinitesimally "
            "close to c — **and never equal to c**. Approaching, not arriving.",
            "Your book's definition is one line: a limit is **infinitesimals applied "
            "to a function**.",
            "An **infinitesimal** is a gap smaller than any gap you could name, and "
            "still not zero. 3.9, 3.999, 3.99999999 — always closer to 4, never 4.",
            "`lim x→c⁻ f(x)` is the **left-hand** limit: x is *smaller* than c. "
            "`lim x→c⁺ f(x)` is the **right-hand** limit: x is *bigger* than c.",
            "Those marks are **directions — not signs, not exponents.** In 89.1 the "
            "left-hand limit was -5; in 89.2 the left-hand limit was 2.",
            "To answer one: find the break, turn the mark into the word *left* or "
            "*right*, **cover the other side with your hand**, and read where the "
            "piece that is left standing stops.",
            "Never decide by top and bottom. In 89.1 the right-hand side was the top "
            "piece; in 89.2 it was the bottom one.",
            "A slanted piece changes nothing, because you read your altitude at **one "
            "place only** — the end, at the break.",
            "On any Lesson 89 problem there are only **two possible answers**: the "
            "output at the open circle and the output at the closed circle. A third "
            "number means you misread the picture, not the arithmetic.",
            "One open circle and one closed circle at the break is what makes the "
            "graph a **function** instead of a relation (Lesson 62) — and a hollow end "
            "can still be the answer to a limit.",
            "Limits (89), derivatives (90) and integrals (94) are the **Big 3** of "
            "calculus, and all three are built out of things you already know.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 89 first. If it didn't quite land, this is here to fix that "
    "— and Example 89.1's graph is drawn further down the page so you can read it "
    "while you work. This is your first real piece of calculus. The whole idea is "
    "that you can walk right up to the edge of something, never reach it, and still "
    "say exactly where you were heading."
)

PARENT_CONTENT = """## The big idea

This is her first calculus lesson, and the book knows it is being provocative.
Page 1 argues that nobody tells a six-year-old she is too young for baseball, but
adults happily tell a pre-algebra student she is too young for calculus — and then
it teaches limits anyway. Lesson 90 is derivatives and Lesson 94 is integrals. The
book calls the three of them the **Big 3 Ideas** and promises that everything in
them is built from things she already knows. On this page that promise is
literally true, and it is worth pointing at.

The lesson is really two sentences.

1. **An infinitesimal is how close you can get without arriving.** The book sends
   her back to Ex. 76.2a, where a hollow dot at (4, 2) kept x = 4 out of the
   domain, `-2 ≤ x < 4`. Its move is to stop looking at the excluded 4 and look at
   what *is* included — 3.9, 3.999, 3.99999999, and on forever. A gap smaller than
   any gap you can name, and still not zero, is an infinitesimal. The book is
   candid that we cannot picture one, and ties that back to the Hebrews 11:1
   "reasonable faith" it raised in Lesson 81. That is the family's chosen
   curriculum making its own argument, and it is carried here as the book has it.
2. **A limit is that idea applied to a function.** The definition it gives is one
   line: *the application of infinitesimals to evaluating a function.* Feed the
   function inputs an infinitesimal away from c — never c itself — and watch where
   the outputs head.

Then almost all of the actual work is reading notation. `lim x→c f(x) = L` is a
sentence: *the limit of f of x, as x approaches c, is L.* Six marks are new today —
`lim`, `→`, `c`, `L`, ⁻ and ⁺ — with one new word, *infinitesimal*, beside them. The
little ⁻ and ⁺ on the c are the pair that cause the trouble, and they mean **which
side you walked in from** — ⁻ where x is smaller than c, ⁺ where x is bigger.

**The examples are much easier than the notation.** Both are discontinuous graphs
(Lesson 66's word) with a break, and the method is four moves, none of them
arithmetic: find the break, turn the mark into *left* or *right*, cover the other
side of the picture with your hand, and read where the surviving piece ends. The
book's own image is a cliff — walking along the top towards the edge of the Grand
Canyon, or along the bottom towards the rock face — and the limit is your
**altitude** when you stop.

Its closing note is the single most useful sentence in the lesson and appears twice:
on any Lesson 89 problem there are **only two possible answers**, the output at the
open circle and the output at the closed circle. In Ex. 89.1 the only numbers
available were 3 and -5; in Ex. 89.2, 2 and -4. If she writes a third number, she
has misread the picture — there is no arithmetic here to slip on.

**About the figures, and what was done about each.**

- **Ex. 89.1's graph is drawn on her page** as an interactive board, rebuilt from
  nothing but the guide's own solution paragraph: break at x = 2, two horizontal
  rays, the bottom one to the left and the top one to the right. It is locked and
  read-only, so she cannot knock a dot off it.
- **That board draws every dot hollow**, because that is how it marks a picture it
  has locked — hollow there means "this was already here", not "this is an open
  circle". In the book, one of the two ends at x = 2 is hollow and one is filled.
  Her page says so plainly and explains why the difference exists — it does not
  change either answer.
- **One number in the source contradicts itself, and her page says so.** The Ex.
  89.1 solution paragraph calls the top ray `y = 2`, then answers **3** two lines
  later, and its own note says the only choices were 3 and -5. The top ray is taken
  as **y = 3** here. If she asks, that is a genuine slip in the printed guide, not
  a trick — and noticing it is a better moment than anything else on the page.
- **Ex. 89.2's graph is described, not drawn.** The book says only that the pieces
  are "not horizontal", never how steep, so drawing it would mean inventing it. Her
  page lists the three facts the solution does state (break at x = 1; top piece to
  the left ending at 2; bottom piece to the right ending at -4) and asks her to
  check them against her book.
- **Ex. 89.2's two question lines are printed as images** in the guide and are
  reconstructed from its own solution text as `lim x→1⁺ f(x)` and `lim x→1⁻ f(x)`.
  Please check that once with her book open.
- The two little **YOU ARE HERE** cliff sketches and page 1's photograph of a
  children's baseball team are not reproduced. Nothing depends on them.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Hand her a ruler. **"Put your finger on 4. Now give me a number close to 4 that
   isn't 4."** Whatever she says, ask for a closer one. Then closer. Do it four or
   five times until she starts laughing at you. Then the two questions that matter:
   **"Will you ever run out?"** and **"Will you ever land on 4?"** No and no. She
   has just built an infinitesimal herself, which is much better than being handed
   the word.
2. Connect it back before you move on: **"Where have you seen a number that's
   allowed to get close but not be included?"** You want the hollow dot — Lesson 76,
   Ex. 76.2a. If it does not come, open Lesson 76 to that example rather than
   telling her.
3. Now the notation, and read it as English, not symbols. Write `lim x→2⁻ f(x)` and
   ask her to say it in words. Insist on the whole sentence: *the limit of f of x,
   as x approaches 2 from the left.* Then ask the question that catches the classic
   error: **"Does that minus sign make the answer negative?"** Let her commit to an
   answer. She will find out on her own page, at Ex. 89.2, that it does not.
4. Open her page to the drawn board. Cover the left half with your hand and ask
   **"what's left?"** — the top ray. Uncover, cover the right half, ask again — the
   bottom ray. That physical move *is* the method, and doing it with your hand
   before she sees the question is what keeps her from guessing by top-and-bottom.
5. Last, the check, and make it her sentence rather than yours. **"Before you work
   the next one — how many different numbers could the answer possibly be?"** You
   want *two*, and you want her to point at the two ends of the break when she says
   it.

If she is lost, it is almost never the idea — it is the notation. Go back to step 3
and make her read five limit expressions out loud as English sentences without
answering a single one of them.

## The classic mix-ups, with the exact wrong answer each one produces

- **Reading ⁻ as a minus sign on the answer.** On Ex. 89.2b she answers **-4**
  instead of **2**. This is the big one, because in Ex. 89.1 the left-hand limit
  really is the negative number (-5), so the wrong rule gets confirmed on its first
  outing and then fails one page later. Fix: the mark is a *direction* — ⁻ means x
  is smaller than c.
- **Deciding by top and bottom.** She learns "from the right = the top piece" from
  Ex. 89.1 and answers **2** instead of **-4** on Ex. 89.2a. Fix: her hand over the
  half she was not asked about, every single time.
- **Reading the ⁺ as an exponent.** `x → 2⁺` becomes `x → 4` and she reads the
  graph in completely the wrong place. It sits up and to the right like a power, so
  this is a reasonable misreading, not a careless one. Fix: say it out loud as
  "from the right" and it stops looking like arithmetic.
- **Answering with a number between the two ends.** She gives **-1** on Ex. 89.1
  because it feels like the graph must go through the middle somehow. Nothing is
  there; the gap *is* what discontinuous means. Fix: the book's two-answers note.
- **Thinking the hollow end is disqualified.** She decides an open circle cannot be
  an answer and gets stuck with nothing to write. Fix: the limit asks where the
  outputs were heading, not what the function equals at c — and the book's own note
  names the open circle's output as one of the two candidates.
- **Letting x arrive.** She writes `f(2) = 3 and f(2) = -5`, which claims two
  outputs for one input and would make it a relation, not a function (Lesson 62).
  Fix: keep `lim` and the arrow in front of the answer.

## What to watch her do

Watch her **hands**, and watch them in this order:

1. **Does a hand cover half the picture?** This is the most diagnostic thing on the
   page and you can see it from across the room. A child who covers the other side
   cannot pick the wrong piece. A child who stares at the whole graph is choosing by
   eye, and on a two-piece graph that is a coin-flip.
2. **Does her finger travel along the graph, or along the x-axis?** The walk is
   along the curve — that is what makes "read your altitude" mean anything. A finger
   sliding along the bottom of the page is looking for x, not for f(x).
3. **Does she say *left* or *right* before she looks at the picture?** Watch the
   order. Reading the mark and reading the graph at the same time is how the two
   get mixed together; naming the side out loud first keeps them separate.
4. **After she writes an answer, does she check it against the two ends?** You want
   a visible glance back at the break. That is the book's own check and it takes
   about a second.
5. **Does she still write `lim` in her answer, or has it quietly disappeared?** A
   bare number will pass on the practice set, but her page asks her to keep the
   `lim` and the arrow in front of it, and an answer written as `f(2) = 3` has lost
   the idea — the question was never what the function equals at 2. The notation is
   doing real work here.

Getting 3 and -5 is not what to watch for. On a two-piece graph she can be right by
coin-flip. The hand over the picture is the habit that survives problems 189 to 489,
where the graphs are all different and none of them is the one she memorised.

## Extend it

- **Do 189 through 489 with her book open and say almost nothing.** All four are the
  same problem with different pictures. Ask exactly one question per problem —
  *"which side, and what's still showing?"* — and let the answers follow.
- **Ask her to draw one.** Give her the answers first: "draw me a discontinuous
  function where the limit from the left is 6 and the limit from the right is -1."
  Working backwards from answers to a picture is a much stronger test than reading
  a picture, and it forces her to decide where to put the open circle.
- **The honest question, if she asks it.** Some child eventually asks what happens
  when the two one-sided limits are the *same* number. That is the beginning of
  continuity, and of the plain two-sided `lim x→c f(x)` sitting at the top of her own
  Rules box — and this lesson deliberately does not go there. The book does, but only
  in passing: Lesson 90's Rules box prints a plain, unmarked limit
  (`f '(x) = lim Δx→0 ...`) and tells her in as many words that she is only being
  shown the symbols, not asked to use them, and Lesson 91 spends its first half on
  continuity and discreteness. So do not promise her a lesson that answers it.
  "Good question — hold on to that one. It's the plain limit in your Rules box.
  You'll see that symbol again next lesson, and nobody is going to make you use it
  yet" is a better answer than a lecture.
- **This week's practice set is a tour of the term.** Every problem number carries
  its own lesson in its last two digits: 787 is the shrimp table from Lesson 87, 1575
  converts the binary number 111 back to base 10 (Lesson 75), 588 is a syllogism
  (Lesson 88), 1281 an inverse (Lesson 81), and 886 is a clinometer and tangent
  (Lesson 86). If any of those wobble, the seeded lesson page for that number is
  the fastest place to go.

## Where this sits

DIVE Lesson 89, *Infinitesimals and the Limit*. Reviews **Lessons 5, 23, 26, 66, 76
and 81** — page 1 lists them.

- **Lesson 76 is the one to revisit if the idea is lost**, and the book says so
  itself: Ex. 76.2a is the open circle at x = 4 that this whole lesson grows out of.
- **Lesson 81 is the one for context** — it is where calculus was first defined for
  her, and where the faith-and-reason argument this page returns to was first made.
- **Lesson 66** is where *discontinuous* was defined (a graph with a jump or a
  break), and **Lesson 26** is where the open circle was first drawn. Neither is
  among this course's seeded lessons, so nothing here describes their contents
  beyond what Lesson 89's own text says about them.
- **Lesson 62** is not on the review line but the solution cites it, for the
  distinction between a relation and a function — which is the reason one of the two
  circles at the break has to be open.
- **Lessons 5 and 23** are on the review line, sit outside the seeded lessons, and
  this guide has not read them. Nothing on Lesson 89's pages leans on them; if the
  review list matters to you, her book is the place to look.

**Proficient** looks like: reads `lim x→2⁺ f(x)` aloud correctly as a sentence, and
gets the right answer on a graph laid out the same way as Ex. 89.1.
**Mastered** looks like: covers the other half of the picture without being told,
is not thrown when the pieces swap sides or slant, does not let the ⁻ leak into the
sign of the answer, and can say why one of the two circles at the break has to be
open.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 89 (infinitesimals and the limit) "
            "— idempotent.")

    LESSON_NUMBER = 89
    TITLE = "Infinitesimals and the Limit — Walk to the Edge and Read Your Altitude"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
