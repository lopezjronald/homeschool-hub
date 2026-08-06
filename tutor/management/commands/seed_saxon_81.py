"""Saxon Pre-Algebra Lesson 81 — Logic: Converse, Inverse and Contrapositive;
What is Calculus?

Reviews Lessons 5, 28, 35, 44, 55, 62, 66, 68, 70 and 73. Two lessons in one
page, and they are not related: the first half is the Lesson 81 Rules chart —
four rows, and the whole logic lesson is those four rows — and the second half is
a one-paragraph definition of calculus with a worked slope attached to it. The
logic gets the bulk of the page, because it is the bulk of the lesson and two of
the three Lesson 81 practice problems (181 converse, 281 inverse). The third,
381, belongs to the calculus half — so budget time for it.

The hook for the calculus half is Lesson 68/77 slope. The book says it out loud
in its own text — "with calculus, you really are not learning much of anything
new" — so this page leads with that rather than treating Δ as new notation.

NOTE ON WORLDVIEW. Section 81A opens with an explicitly Christian argument: the
Greek *logos* (Lesson 28), "fine sounding arguments" from Colossians 2:4, a
rebuttal of naturalism, and the sentence "as Christians, we should use logic to
discover ideas that match reality." The calculus half closes with a faith-and-
reason paragraph citing Hebrews 11:2. That is the family's chosen curriculum and
it is the lesson's own stated reason for teaching logic at all, so it is carried
here as the book has it — in the purpose block and in Idea 3 — neither amplified
nor stripped out.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Practice problems are reworded rather than transcribed.

The source has exactly one figure: the page-4 graph of f(x)=x² with the line
through (2,4) and (3,9). It is DRAWN here, not described — a KIND_TOOL grid with
`curve: "x^2"`, the worked points `locked` so a stray tap cannot move them, and
`readonly` so the Clear button (which wipes the curve layer) is never rendered.
Example 81.3 needs no figure at all: the book states both points in words.

    python manage.py seed_saxon_81 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 81 · Pre-Algebra",
        "title": "Flipping an if-then statement three ways",
        "thesis": "Every *if-then* sentence has two halves. You can **swap** them, "
                  "you can put a **not** in them, or you can do both — and each of "
                  "those three flips has a name. That is the whole first half of this "
                  "lesson. The second half tells you what calculus is, in two "
                  "sentences.",
        "formula": "If p, then q",
        "roles": [
            {"tone": "start", "name": "p — the hypothesis",
             "text": "The IF half. Whatever comes after the word if, said in words. "
                     "Same word as in science class: the thing you are supposing."},
            {"tone": "move", "name": "q — the conclusion",
             "text": "The THEN half. Whatever comes after the word then. It is what "
                     "follows if the supposing holds."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody bothers naming the flips",
        "paragraphs": [
            "Your phone has a rule inside it. If the battery drops below 20%, then "
            "the low-battery warning pops up. That is an if-then sentence, and you "
            "meet dozens of them a day without noticing.",
            "Now turn it around. *If the warning popped up, then the battery is below "
            "20%.* Say both out loud, one after the other. They are close. They are "
            "not the same sentence.",
            "That is the problem this lesson solves. People flip if-then sentences "
            "constantly — in arguments, in science, in the news — and hand the flipped "
            "one back as though nothing happened. Once each flip has a **name**, you "
            "can say exactly which one somebody just handed you.",
            "Your book starts somewhere you might not expect. Back in Lesson 28 you "
            "learned that the word *rational* comes from the Greek word *logos*, which "
            "can also mean *word*, as in the Word of God. Logic, it says, is basically "
            "the study of reason — and logic is foundational to all of mathematics.",
            "Then it makes a distinction worth reading twice. **Inside** mathematics, a "
            "logical statement is normally also true. **Outside** mathematics, you can "
            "build a statement that is perfectly logical and still not true. Your book "
            "calls those what Scripture calls them: \"fine sounding arguments,\" or "
            "\"persuasive words\" (Colossians 2:4).",
            "Its example is naturalism — the claim that matter and energy are the only "
            "realities, and there is no God. Its reply is a question. What about the "
            "laws of logic themselves? The four rules on this page, Euclid's axioms and "
            "postulates from Lesson 44 — those are real, and they are made of neither "
            "matter nor energy. So, your book says, as Christians we should use logic "
            "to discover ideas that match reality, while rejecting ideas like "
            "naturalism that don't match reality.",
            "Then it gets to work, and the work is small. Four rows in a table.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Every if-then is two halves, and each half has a name",
        "paragraphs": [
            "Take the sentence *If it is raining, then the ground is wet.* Put your "
            "finger on the word **if**, then on the word **then**. Those two words are "
            "hinges. Everything between them is one half; everything after *then* is "
            "the other.",
            "The **if** half is called the **hypothesis**. That is the same word you "
            "use in science — an educated guess, the thing you are supposing for the "
            "moment.",
            "The **then** half is called the **conclusion**. It is what follows, "
            "supposing the guess holds.",
            "Writing those halves out over and over gets long, so logic uses letters. "
            "**p** is short for whatever the if half says. **q** is short for whatever "
            "the then half says. Every conditional statement in this lesson is written "
            "`If p, then q`.",
            "Be careful about one thing here. p and q are **not numbers**. They do not "
            "stand for 3 or −8. They stand for whole sentences: p might be *the weather "
            "is calm*, all four words of it. A letter standing in for a sentence is new, "
            "and it is the only genuinely new idea on this page.",
            "So the first move on every single problem — and this is your book's own "
            "first move in both of its worked examples — is to *observe the conditional "
            "statement* and write down what p is and what q is, in words. Do it on "
            "scratch paper. Do not shorten them.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"If it's raining, then the ground is wet. Point at the if half. Now "
                "point at the then half. Good — now say the whole thing back to me with "
                "those two halves swapped around. ... That's called the converse. Now "
                "say the original one again, but wedge the word 'not' into both halves. "
                "... That's the inverse. You just did the whole lesson. The only thing "
                "left is learning the names.\"",
    }),

    (B.KIND_TABLE, {
        "caption": "The Lesson 81 Rules — the entire logic lesson is these four rows",
        "headers": ["Name", "Form", "Said out loud, using the book's boating example"],
        "rows": [
            {"cells": ["Conditional statement", "If p, then q",
                       "If the weather is calm, then we go boating."],
             "emphasis": True},
            {"cells": ["Converse", "If q, then p",
                       "If we go boating, then the weather is calm."]},
            {"cells": ["Inverse", "If ~p, then ~q",
                       "If the weather is not calm, then we do not go boating."]},
            {"cells": ["Contrapositive", "If ~q, then ~p",
                       "If we do not go boating, then the weather is not calm."]},
        ],
        "note": "The **~** symbol means **not**. The shaded top row is the statement "
                "you are handed; the three rows under it are built out of it. Here "
                "`p` = *the weather is calm* and `q` = *we go boating*.\n\n"
                "Your book adds a caution about this particular example. All three "
                "flips are logical, it says, but only the converse and the inverse are "
                "**both logical and true** here — the contrapositive is logically "
                "equivalent and may still not be true, because something other than "
                "rough weather could keep you off the water. Just because they are "
                "logically the same statement doesn't mean they are equally true.\n\n"
                "Then it tells you what Lesson 81 actually asks of you, and this takes "
                "the pressure off: **build the logically equivalent statement — do not "
                "worry about whether it is also true in real life.**",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "There are only two moves, and only two choices",
        "paragraphs": [
            "Read down the Form column of that table again. Only two things ever "
            "happen.",
            "**Swap.** Trade the halves. What sat behind *if* moves behind *then*, and "
            "the other one comes forward.",
            "**Negate.** Wedge a *not* into a half. The shorthand for that is a squiggle: "
            "`~p` is read out loud as \"not p.\"",
            "Now the three flips are easy to tell apart. The **converse** swaps and does "
            "not negate. The **inverse** negates and does not swap. The "
            "**contrapositive** does both.",
            "The contrapositive is the one people worry about, and there is nothing to "
            "worry about: do the two moves in whichever order you like. Swap first then "
            "negate both, or negate both then swap — either way you land on the same "
            "sentence, `If ~q, then ~p`.",
            "Here is the sentence from your book worth holding onto. Working with these "
            "statements is manageable if you remember that a half only ever has **two "
            "choices**: *this*, or *~this*. There is no third option and there is "
            "nothing in between.",
            "One warning about the squiggle. It is a symbol, but on paper you write the "
            "*not* into the sentence like a person talks. `~q` for *we go boating* comes "
            "out as **we do not go boating** — the word changes shape to fit the "
            "sentence. It is still ~q.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Two moves, four rows — which flip does what",
        "headers": ["", "Swap the halves?", "Put a ~ on both halves?", "What you write"],
        "rows": [
            {"cells": ["Conditional (what you are given)", "no", "no", "If p, then q"],
             "emphasis": True},
            {"cells": ["Converse", "yes", "no", "If q, then p"]},
            {"cells": ["Inverse", "no", "yes", "If ~p, then ~q"]},
            {"cells": ["Contrapositive", "yes", "yes", "If ~q, then ~p"],
             "emphasis": True},
        ],
        "note": "**Both halves get the ~, or neither does.** Negating only the if half "
                "is a common wrong answer, and on practice problem 2 one of the four "
                "printed choices is exactly that half-finished inverse, sitting there "
                "looking correct. Do not count on the trap always being there, though — "
                "problem 1's four choices are built a different way, and hunting for a "
                "half-negated one there will only cost you time. The habit that works on "
                "every question is your own: **count your nots before you circle "
                "anything.** An inverse has two.\n\n"
                "The two shaded rows are the ends of the table: the statement you start "
                "from, and the one flip that does both moves.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, the same way every time",
        "steps": [
            {"label": "Underline the two halves before you write anything.",
             "detail": "One pencil line under the **if** half, one under the **then** "
                       "half. The if half is the **hypothesis**. The then half is the "
                       "**conclusion**. Two marks, four seconds."},
            {"label": "Write out p and q, in words, on scratch paper.",
             "detail": "This is your book's own first instruction in both worked "
                       "examples: *observe the conditional statement, and identify p "
                       "and q*. Copy the halves whole. Shortening them is where the "
                       "words go missing later."},
            {"label": "Read the question again and name which flip it wants.",
             "detail": "Converse, inverse, or contrapositive. A perfectly built "
                       "contrapositive handed in for a question that asked for the "
                       "inverse is still a wrong answer, and it is a common one."},
            {"label": "Build it from the table, then read it back as English.",
             "detail": "Swap, negate, or both — then say the finished sentence out "
                       "loud. If it does not sound like something a person would "
                       "actually say, you dropped a word somewhere.",
             "math": "If p, then q  →  If ~q, then ~p"},
        ],
        "after": "And the instruction your book gives in plain words, which is worth "
                 "reading before you start: for Lesson 81 problems, **you are only "
                 "creating logically equivalent statements.** Whether the result is "
                 "also true in real life is not what is being asked.",
    }),

    (B.KIND_WORKED, {
        "number": "81.1",
        "question": "Write the converse, inverse, and contrapositive for the following "
                    "conditional statement.   If a tornado is coming, then you get in "
                    "the shelter.",
        "steps": [
            {"label": "First, find p and q",
             "text": "Your book's opening move, word for word: *observe the conditional "
                     "statement, and identify p and q*. The if half is **p = a tornado "
                     "is coming**. The then half is **q = you get in the shelter**. "
                     "Write both on scratch paper before you flip anything."},
            {"label": "Converse — swap only",
             "text": "The rule is `If q, then p`. So the shelter half goes in front and "
                     "the tornado half goes behind. Nothing gets a *not*. → **If you "
                     "get in the shelter, then a tornado is coming.**"},
            {"label": "Inverse — negate only",
             "text": "The rule is `If ~p, then ~q`. Same order as the original, but a "
                     "*not* goes into **both** halves. → **If a tornado is not coming, "
                     "then you do not get in the shelter.** Notice the *not* changes "
                     "shape to fit: *is not coming* in one half, *do not get* in the "
                     "other. Both are still just ~."},
            {"label": "Contrapositive — both moves",
             "text": "The rule is `If ~q, then ~p`. Swap the halves **and** put a *not* "
                     "in both. → **If you do not get in the shelter, then a tornado is "
                     "not coming.**"},
            {"label": "Read all three back out loud",
             "text": "Three sentences, and every one of them is a sentence a person "
                     "could say. That is the check. A flip that comes out sounding "
                     "broken is a flip with a word missing from it."},
        ],
        "answer": "Converse: If you get in the shelter, then a tornado is coming. · "
                  "Inverse: If a tornado is not coming, then you do not get in the "
                  "shelter. · Contrapositive: If you do not get in the shelter, then a "
                  "tornado is not coming.",
    }),

    (B.KIND_WORKED, {
        "number": "81.2",
        "question": "Write the converse, inverse, and contrapositive for the following "
                    "conditional statement.   If the length is 8 and the width is 5, "
                    "then the area is 8 × 5 = 40.",
        "steps": [
            {"label": "Find p and q — and keep each one whole",
             "text": "**p = the length is 8 and the width is 5.** **q = the area is "
                     "8 × 5 = 40.** Look hard at p: it has an *and* sitting inside it. "
                     "That does not make it two statements. It is one hypothesis with "
                     "two conditions in it, and it travels as one lump."},
            {"label": "The arithmetic is already done for you",
             "text": "Length times width is the area of a rectangle, and 8 × 5 is 40. "
                     "The question is not asking you to work that out — it worked it "
                     "out in the sentence. Knowing the area is 40 is only what lets you "
                     "say q shortly, as *the area is 40*, the way your book does in the "
                     "flips below."},
            {"label": "Converse — swap only",
             "text": "`If q, then p`. → **If the area is 40, then the length is 8 and "
                     "the width is 5.**"},
            {"label": "Inverse — negate only",
             "text": "`If ~p, then ~q`. Same order, *not* in both halves — and inside "
                     "p, both of its conditions get one. → **If the length is not 8 and "
                     "the width is not 5, then the area is not 40.**"},
            {"label": "Contrapositive — both moves",
             "text": "`If ~q, then ~p`. → **If the area is not 40, then the length is "
                     "not 8 and the width is not 5.**"},
        ],
        "answer": "Converse: If the area is 40, then the length is 8 and the width is "
                  "5. · Inverse: If the length is not 8 and the width is not 5, then "
                  "the area is not 40. · Contrapositive: If the area is not 40, then "
                  "the length is not 8 and the width is not 5.",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Saxon writes this lesson in six pieces of shorthand and seven words "
                 "worth naming, and none of them mean anything complicated. Here is "
                 "each one said out loud.",
        "rows": [
            {"symbol": "if–then", "plain": "a conditional statement — the kind of "
                                           "sentence this lesson flips",
             "example": "If p, then q"},
            {"symbol": "p", "plain": "the if half, written out in words",
             "example": "p = a tornado is coming"},
            {"symbol": "q", "plain": "the then half, written out in words",
             "example": "q = you get in the shelter"},
            {"symbol": "~", "plain": "not — the only other thing a half can be",
             "example": "~p = a tornado is not coming"},
            {"symbol": "hypothesis", "plain": "the if half. Same word as in science: an "
                                              "educated guess",
             "example": "p"},
            {"symbol": "conclusion", "plain": "the then half. What follows if the guess "
                                              "holds",
             "example": "q"},
            {"symbol": "converse", "plain": "swap the halves; no nots",
             "example": "If q, then p"},
            {"symbol": "inverse", "plain": "keep the order; a not in BOTH halves",
             "example": "If ~p, then ~q"},
            {"symbol": "contrapositive", "plain": "swap AND put a not in both halves",
             "example": "If ~q, then ~p"},
            {"symbol": "logically equivalent",
             "plain": "built from the same statement by these rules — which is not a "
                      "promise that it is true",
             "example": "all three flips"},
            {"symbol": "Δ", "plain": "the change in — subtract to find it",
             "example": "Δx = 3 − 2 = 1"},
            {"symbol": "Δy / Δx", "plain": "the rate of change: how far up over how far "
                                           "across. This is slope",
             "example": "5 / 1 = 5"},
            {"symbol": "calculus", "plain": "the mathematical study of rates of change. "
                                            "The study of motion",
             "example": "Δy / Δx"},
        ],
        "after": "Two of those are the words to say out loud until they stick: "
                 "**hypothesis** is the *if*, **conclusion** is the *then*. Everything "
                 "else in the first half of this lesson is built out of those two.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Trading the converse and the inverse.",
             "wrong": "converse of “If p, then q”  →  If ~p, then ~q",
             "right": "converse of “If p, then q”  →  If q, then p",
             "note": "Keep the two verbs apart. **Converse swaps. Inverse negates.** If "
                     "it helps: *con-verse* has the same start as *convert* — you are "
                     "turning it around. The inverse leaves everything where it is and "
                     "only adds nots."},
            {"name": "Putting the ~ on only the if half.",
             "wrong": "inverse  →  If the base is not 10 and the height is not 5, then "
                      "its area equals 25   (Choice B)",
             "right": "inverse  →  If the base is not 10 and the height is not 5, then "
                      "its area doesn’t equal 25   (Choice C)",
             "note": "Straight out of practice problem 2. The choices are written so "
                     "that this half-finished inverse is sitting there looking correct. "
                     "**Both halves, or neither.** Count your nots before you circle "
                     "anything: an inverse has two."},
            {"name": "Handing back the contrapositive when the question said inverse.",
             "wrong": "inverse  →  If the area does not equal 25, then the base is not "
                      "10 and the height is not 5   (Choice D)",
             "right": "inverse  →  If the base is not 10 and the height is not 5, then "
                      "the area doesn’t equal 25   (Choice C)",
             "note": "That wrong answer is a perfectly built contrapositive. It is still "
                     "wrong, because it answers a question nobody asked. Read the "
                     "question a second time **after** you have built your sentence."},
            {"name": "Picking an answer that is not a flip at all.",
             "wrong": "converse  →  If there is a red sky at night, it is the sailor’s "
                      "delight.   (Choice D)",
             "right": "converse  →  If the sailors take warning, then there is a red "
                      "sky in the morning.   (Choice A)",
             "note": "Practice problem 1. That wrong choice is a real saying and it "
                     "sounds like it belongs on the page — but it is not built out of "
                     "this statement's p and q at all. Every correct answer in this "
                     "lesson uses **the same two halves you started with**, moved or "
                     "negated. Nothing new is allowed in.\n\n"
                     "Your book adds a note on this problem, and it is worth reading: "
                     "the red-sky saying is based on Christ's words in Matthew 16:2–3."},
            {"name": "Calling the then half the hypothesis.",
             "wrong": "hypothesis = you get in the shelter",
             "right": "hypothesis = a tornado is coming, conclusion = you get in the "
                      "shelter",
             "note": "**Hypothesis is the if. Conclusion is the then.** They come in "
                     "that order in the sentence and in that order in the definitions. "
                     "If you have them backwards, every flip you build afterwards comes "
                     "out backwards too."},
            {"name": "Subtracting the rate of change backwards.",
             "wrong": "Δy = 1 - 4 = -3  →  Δy / Δx = -3 / 1 = -3",
             "right": "Δy = 4 - 1 = 3  →  Δx = 2 - 1 = 1  →  Δy / Δx = 3 / 1 = 3",
             "note": "From the calculus half. Second point minus first point, both "
                     "times — top and bottom. Mix the order between the two and you get "
                     "the right size with the wrong sign, which is impossible here: "
                     "`f(x) = x²` is **climbing** between x = 1 and x = 2, and a "
                     "function that is going up cannot have a negative rate of change "
                     "over that stretch.\n\n"
                     "Say *climbing here*, not *always climbing*. On the graph further "
                     "down this page you can see `x²` coming back **down** to the left "
                     "of 0. You meet that side of the curve later in this same "
                     "practice set."},
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "What is calculus?",
        "paragraphs": [
            "Halfway down the page your book changes the subject completely. Section "
            "81B is one question: what *is* calculus?",
            "The definition is two short sentences, and they are worth memorising as "
            "they stand. **Calculus is the mathematical study of rates of change. The "
            "study of motion.**",
            "A rate is a how-fast. Miles per hour is a rate. Dollars per week is a rate. "
            "You met rates in Lesson 35, and your book told you then that this was where "
            "they led.",
            "You already know functions from Lesson 62: an x goes in, a y comes out. "
            "Calculus asks the next question. If I nudge the input a little, how much "
            "does the output move?",
            "And here is the part your book says out loud, so you should hear it before "
            "you do any of it: the amount y moved, divided by the amount x moved, is "
            "**rise over run**. That is slope. Lesson 68's slope, Lesson 70's slope, the "
            "slope-from-two-points you did most recently in Lesson 77. In your book's "
            "own words — with calculus, you really are not learning much of anything "
            "new.",
            "There is one piece of shorthand, and you have met it too. Instead of "
            "writing *the change in x*, write **Δx**. The triangle Δ is short for *the "
            "change in* — nothing more than that. Lesson 70 used Δx and Δy to find new "
            "coordinates on a line.",
            "Your book closes the section with something about what learning calculus "
            "asks of you. Calculus is reasonable — rational — but it works best using "
            "unreasonably small values called *infinitesimals* and unreasonably large "
            "ones like *infinity* (Lesson 5). So, it says, a healthy mix of faith and "
            "reason is at the heart of calculus: not a blind faith, but a reasonable "
            "faith, the kind Hebrews 11:2 describes as an \"evidence of things not "
            "seen.\"",
            "The infinity and the infinitesimals are not today. Today has exactly one "
            "job, and your book states it plainly: **connect the idea of calculus with "
            "slope.**",
        ],
    }),

    (B.KIND_STEPPER, {
        "title": "The book's own walk — how fast is y = x² changing near x = 2?",
        "equation": "y = x²        Δx = 1        the points (2, 4) and (3, 9)",
        "steps": [
            {"label": "What is actually being asked",
             "text": "Not *what is y when x is 2* — you could already do that in Lesson "
                     "62. The question is different: **around x = 2, if x moves a "
                     "little, how much does y move?** That is a rate, and rates are what "
                     "calculus is."},
            {"label": "Step 1 · start at x = 2",
             "text": "Put 2 into the function. Two squared means two times two.",
             "math": "y = 2 × 2 = 4"},
            {"label": "Step 2 · pick a small change in x",
             "text": "Call that change **Δx**. Your book picks Δx = 1 and says exactly "
                     "why in one sentence: it did not *have* to be 1, it chose 1 because "
                     "it is an easy number to work with. So the new x is the old x plus "
                     "the change.",
             "math": "x + Δx = 2 + 1 = 3"},
            {"label": "Step 3 · run the same function at the new x",
             "text": "Same function, new input. Three squared means three times three.",
             "math": "y = 3 × 3 = 9"},
            {"label": "Step 4 · how far did x actually move?",
             "text": "Second x minus first x. This one you already know — it is the 1 "
                     "you picked.",
             "math": "Δx = 3 - 2 = 1"},
            {"label": "Step 5 · how far did y move?",
             "text": "Second y minus first y. Stare at this number for a second. You "
                     "nudged x by **one**, and y jumped by **five**.",
             "math": "Δy = 9 - 4 = 5"},
            {"label": "Step 6 · put one over the other",
             "text": "The change in y, over the change in x. Near x = 2, y is changing "
                     "about **five times faster** than x is.",
             "math": "Δy / Δx = 5 / 1 = 5"},
            {"label": "Step 7 · notice what you just did",
             "text": "That 5 is the slope of the line through (2, 4) and (3, 9). You "
                     "have been finding slopes exactly like that since Lesson 68. "
                     "Nothing on this page was new except the word for it."},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "81.3",
        "question": "For the function f(x) = x², f(1) = 1 and f(2) = 4. What is the rate "
                    "of change between f(1) and f(2)? In other words, find the slope, "
                    "Δy / Δx, for a line drawn between the points located at f(1) and "
                    "f(2).",
        "steps": [
            {"label": "Turn what you were given into two points",
             "text": "This is the step people skip, and it is the whole translation. "
                     "`f(1) = 1` means *when x is 1, y is 1* — so that is the point "
                     "(1, 1). And `f(2) = 4` is the point (2, 4). Now it is a "
                     "two-points problem, which is Lesson 77.",
             "math": "f(1) = 1  →  (1, 1)     f(2) = 4  →  (2, 4)"},
            {"label": "Δy — how far up",
             "text": "Second y minus first y. Keep that order.",
             "math": "Δy = 4 - 1 = 3"},
            {"label": "Δx — how far across",
             "text": "Second x minus first x. Same order, every time.",
             "math": "Δx = 2 - 1 = 1"},
            {"label": "Divide, and say what the number means",
             "text": "Rise over run. Between x = 1 and x = 2, y is climbing three times "
                     "as fast as x. Your book points out that this is the same process "
                     "you followed in Ex. 77.2 — nothing about the method changed "
                     "because the word *calculus* appeared.",
             "math": "m = Δy / Δx = 3 / 1 = 3"},
        ],
        "answer": "Δy / Δx = 3",
    }),

    (B.KIND_TABLE, {
        "caption": "Same function, two stretches, two different answers",
        "headers": ["between", "the two points", "Δy", "Δx", "Δy / Δx"],
        "rows": [
            {"cells": ["x = 1 and x = 2", "(1, 1) and (2, 4)", "4 − 1 = 3", "2 − 1 = 1",
                       "3"], "emphasis": True},
            {"cells": ["x = 2 and x = 3", "(2, 4) and (3, 9)", "9 − 4 = 5", "3 − 2 = 1",
                       "5"], "emphasis": True},
        ],
        "note": "Same function both times — `f(x) = x²` — and a different answer both "
                "times. **That is the point of the whole second half.** A straight line "
                "has one slope everywhere; a curve does not. Between 1 and 2 it climbs "
                "at 3; between 2 and 3 it climbs at 5, so the second stretch is "
                "steeper.\n\n"
                "Your book prints a graph of `f(x) = x²` here to show the same thing. "
                "That graph is drawn for you just below, so you can read the two "
                "stretches off the picture as well as out of the table.",
    }),

    (B.KIND_TOOL, {
        "title": "The graph on page 4, drawn",
        "intro": "The green curve is `f(x) = x²` — your book's page-4 graph. The three "
                 "hollow dots are the points you have already worked out: (1, 1), "
                 "(2, 4) and (3, 9). They are the given figure, so you cannot knock "
                 "one off by tapping it.\n\nHold a ruler — or the straight edge of a "
                 "pencil — from the first dot to the second. Then move it to run from "
                 "the second dot to the third.",
        "widget": "grid",
        # The GIVEN figure, drawn for her to READ. `locked` keeps the three worked
        # points out of everything that edits; `readonly` removes the control bar,
        # which matters here because Undo/Clear both wipe the curve layer and would
        # erase the parabola she was told to look at. `curve` draws the parent x².
        # Both spans are 12, so the squares stay square and the steepening she is
        # asked to see is a true picture of it rather than a stretched one.
        "config": {"view": {"xmin": -4, "xmax": 8, "ymin": -2, "ymax": 10},
                   "points": [[1, 1], [2, 4], [3, 9]],
                   "locked": True,
                   "curve": "x^2",
                   "readonly": True,
                   "label": "f(x) = x² with the worked points (1, 1), (2, 4) and (3, 9)"},
        "after": "The second line is steeper than the first. That is the **3** and the "
                 "**5** as a picture instead of as arithmetic — and it is why one "
                 "function can have two different rates of change. Your book says it in "
                 "words: as x increases, f(x) increases greater and greater.\n\n"
                 "One more thing while the curve is in front of you. To the **left** of "
                 "0 the curve comes back *down*. `x²` is not climbing everywhere. It is "
                 "climbing on the stretch you measured.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "This one is practice problem 3 on your set — work it there "
                  "first and use this to check yourself. For f(x) = x², f(3) = 9 and "
                  "f(4) = 16. What is the rate of change between them?",
        "answer": "**7.** The two points are (3, 9) and (4, 16), so take the change in y "
                  "over the change in x: **Δy = 16 - 9 = 7 → Δx = 4 - 3 = 1 → "
                  "Δy / Δx = 7 / 1 = 7.**\n\n"
                  "Now put the three answers next to each other — **3, then 5, then 7.** "
                  "Every stretch is steeper than the one before it, and the rate is "
                  "going up by 2 each time. So `x²` is not only growing; the *speed* it "
                  "grows at is growing. Measuring that speed at one exact point, instead "
                  "of across a whole stretch, is what the rest of calculus is for.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "Every if-then has two halves. The **if** half is the **hypothesis** — "
            "call it `p`. The **then** half is the **conclusion** — call it `q`.",
            "**Converse:** swap the halves. `If q, then p`.",
            "**Inverse:** keep the order, put a *not* in **both** halves. "
            "`If ~p, then ~q`.",
            "**Contrapositive:** do both moves, in either order. `If ~q, then ~p`.",
            "`~` means **not**, and a half only ever has two choices — *this* or "
            "*~this*. There is no third option.",
            "First move on every problem: write out `p` and `q` **in words** before you "
            "flip anything. That is your book's own first instruction in both examples.",
            "Lesson 81 asks you to **build the form**. Your book says directly that "
            "whether the result is true in real life is not the question here.",
            "**Calculus is the mathematical study of rates of change. The study of "
            "motion.**",
            "A rate of change between two points is `Δy / Δx` — which is slope, which "
            "you have been finding since Lesson 68. `Δ` is short for *the change in*.",
            "On a curve the answer depends on where you look. For `f(x) = x²` the rate "
            "is **3** between x = 1 and 2, and **5** between x = 2 and 3.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 81 first. If it didn't quite land, this is here to fix that. "
    "Two things happen in this lesson and they aren't related. First: an if-then "
    "sentence has two halves, and there are three ways to flip them — each one has a "
    "name, and that's most of the page. Second: a two-sentence answer to 'what is "
    "calculus?', which turns out to be slope wearing a new word."
)

PARENT_CONTENT = """## The big idea

Two unrelated lessons share one page, and the split is uneven on purpose — the
logic is roughly 80% of the reading and **two of the three** Lesson 81 practice
problems (1 asks for a converse, 2 for an inverse). The third belongs to the
calculus half: *for f(x) = x², f(3) = 9 and f(4) = 16, what is the rate of
change?* Budget time for it — it is a slope calculation, and its answer is **7**.

**The logic half is four rows and two moves.** Every conditional statement is
`If p, then q`, where p is the **hypothesis** (the if half) and q is the
**conclusion** (the then half). From there:

| flip | swap the halves? | negate both halves? | result |
|---|---|---|---|
| converse | yes | no | `If q, then p` |
| inverse | no | yes | `If ~p, then ~q` |
| contrapositive | yes | yes | `If ~q, then ~p` |

`~` means *not*. That table is the entire lesson. The only genuinely new idea
underneath it is that **a letter can stand for a whole sentence** — p is not a
number here, it is four words like *the weather is calm*. Children who have only
ever seen letters standing for numbers stumble on that, not on the flipping.

**The calculus half is a definition plus a slope.** Saxon's definition, verbatim
and worth memorising: *calculus is the mathematical study of rates of change. The
study of motion.* Then it does one example: for `y = x²`, moving from x = 2 to
x = 3 gives Δy = 5 and Δx = 1, so the rate of change is 5. And it says the useful
thing out loud — that is just the slope of the line through (2, 4) and (3, 9), so
"with calculus, you really are not learning much of anything new." Lead with that
sentence. It is the reassurance the section is built around.

**About the opening.** Section 81A begins with an explicitly Christian argument:
the Greek *logos* from Lesson 28, "fine sounding arguments" (Colossians 2:4), a
rebuttal of naturalism on the grounds that the laws of logic are real but made of
neither matter nor energy, and the line "as Christians, we should use logic to
discover ideas that match reality." The calculus section closes with a
faith-and-reason paragraph citing Hebrews 11:2. Her page carries all of it, in the
book's own framing, in the "Why this exists" section and in Idea 3.

## Teach it out loud in five minutes

Say these in order, and ask the question at each step. A single sentence on paper
does all the work — do not start with p and q.

1. Write **"If it's raining, then the ground is wet."** Ask: **"Put your finger on
   the *if* part. Now the *then* part."** Do not name anything yet. You want two
   fingers on two halves before any vocabulary exists.
2. **"Now say it back to me with those two halves swapped."** Wait for it. She will
   produce *"If the ground is wet, then it's raining."* Then name it: *"That's the
   **converse**."* The name lands better after the thing than before it.
3. **"Say the original again, but wedge the word 'not' into both halves."** You want
   *"If it's not raining, then the ground is not wet."* Name it: **inverse**. Then
   ask the question that catches a half-finished inverse: **"How many nots did you
   put in?"** The answer must be two.
4. **"Now do both — swap them AND put the nots in."** *"If the ground is not wet,
   then it's not raining."* Name it: **contrapositive**. Then tell her the relief:
   it does not matter which move she does first, she lands in the same place.
5. Only now introduce the letters. **"Instead of writing that whole sentence out
   three more times, call the if part p and the then part q."** Point at the rules
   chart. Ask: **"Which row is the one we just did last?"** She should find
   `If ~q, then ~p` unaided. If she can do that, she has the lesson.

For the calculus half, thirty seconds is enough: **"Calculus is about rates of
change — how fast something is changing. Here's the whole trick: you find it the
same way you find slope. How much did y move, over how much did x move."** Then do
Example 81.3 with her and let the ordinariness of it be the point.

## The classic mix-ups

Each produces a specific wrong answer. Four of them are literally the printed
distractors on her practice page — the first four below.

- **Converse and inverse traded.** She is asked for the converse and writes
  **`If ~p, then ~q`**. On practice problem 1 that is **Choice C**. If you drill
  only one of these six, drill this one — Saxon ranks nothing, so that is a
  judgement call and not the book's, but a traded pair changes every answer she
  builds afterwards. Fix: converse *converts* — it turns the sentence around. The
  inverse moves nothing.
- **Only the if half negated.** Practice problem 2 asks for the inverse of "if the
  base is 10 and the height is 5, then the area equals 25", and she picks
  **Choice B** — *"...then its area equals 25"*, with the conclusion left
  un-negated. Choice B exists to catch exactly this. Fix: have her **count the
  nots**. An inverse has two.
- **Contrapositive handed in for the inverse.** Same problem, **Choice D**. The
  sentence she wrote is perfectly correct — for a question nobody asked. Fix: read
  the question a second time *after* building the answer, not before.
- **An answer that isn't a flip at all.** Practice problem 1's **Choice D** ("red
  sky at night, sailor's delight") is a real saying that sounds like it belongs. It
  uses words that never appeared in p or q. Fix: every legal answer reuses the same
  two halves, moved or negated. Nothing new gets in.
- **Hypothesis and conclusion swapped.** She labels *you get in the shelter* the
  hypothesis. Everything built after that comes out mirror-imaged. Fix: hypothesis
  is the **if**, and it comes first in the sentence and first in the definitions.
- **Backwards subtraction on the rate.** On Example 81.3 she computes
  **Δy = 1 − 4 = −3** and reports a rate of **−3** instead of **3**. Fix: second
  point minus first point, on *both* top and bottom. And a sanity check she can run
  herself — `x²` is climbing there, so a negative rate is impossible.

## What to watch her do

Watch her **hands**, not her answers. She can get two of these right by feel.

1. **Does the pencil mark the two halves before she writes anything?** Two
   underlines, or a slash between them. A child who starts writing the flip
   immediately is flipping in her head, and in-the-head flipping is exactly where
   converse and inverse get traded.
2. **Does she write p and q out in words on scratch paper?** This is Saxon's own
   first instruction in both worked examples and it is the step children skip
   because it feels like busywork. It is not — it is what makes the *and* inside
   "the length is 8 and the width is 5" travel as one lump instead of coming apart.
3. **On an inverse, watch for two nots appearing.** Physically count them with her
   the first three times. One not instead of two is the slip here, and it is
   invisible unless you are watching the pencil.
4. **Does she read the finished sentence out loud?** You want to hear it. A flip
   with a dropped word does not sound like English, and her own ear catches it
   faster than any rule will.
5. **On the calculus problems, does she write the two points down first?** `f(1) = 1`
   has to become the point `(1, 1)` on paper before she subtracts anything. Watch
   for that line appearing. If she goes straight to subtracting from the f-notation,
   she will eventually subtract the wrong pair.

## Extend it

- **Run the whole lesson on a sentence about her.** "If Kaylin finishes her math,
  then she gets screen time." Ask for all three flips. The inverse and the
  contrapositive will start an argument, which is the point — she will be arguing
  about logic.
- **Find one in the wild.** Ask her to catch someone flipping an if-then during the
  week: an advertisement, a sibling, you. Naming the flip out loud is a genuinely
  useful skill and it is section 81A's whole motivation.
- **Take the calculus one step further.** Her page gives the rate for `x²` between
  1 and 2 (it is 3) and between 2 and 3 (it is 5); practice problem 3 has her do 3
  to 4, which is 7. Once those three are on paper, ask: **"what's happening to the
  answers?"** They go 3, 5, 7. Then have her do 4 to 5 and predict it first — it is
  9. Then the real question: **"what would happen if Δx were a half instead of 1?
  Or a hundredth?"** That is the door into actual calculus, and she does not need to
  walk through it today to enjoy seeing where it is.
- **A hard, good question:** "is the rate of change of a straight line ever
  different depending on where you look?" No — that is what makes it straight, and
  it connects back to Lesson 68, where slope started.

## Two footnotes — for you, not for her

**First, the logic.** Saxon's paragraph on the boating example says all three flips
are logical, but that only the converse and the inverse are also *true* here, while
the contrapositive
"is logically equivalent, but may not be true." It then closes the question off:
*"For problems from Lesson 81, we will only focus on creating logically equivalent
statements, and not on whether they are also true in real life."* Her page carries
both sentences, in that order, and every Lesson 81 problem asks only for the form —
so no answer she is graded on turns on it.

Worth you knowing what she meets later, in geometry: in formal logic the
**contrapositive** is the flip that always preserves truth — if "if p then q" is
true, then "if ~q then ~p" is true as well, without exception — while the converse
and the inverse are the two that can turn false. The later course therefore draws
the line in the opposite place from the paragraph she reads today. If she asks, the
honest answer is small: *"Today we're only building the forms. Which flip is
guaranteed true is a geometry question, and you'll get it."* It is not worth making
into a fight, and it changes nothing in this lesson.

**Second, a citation.** The calculus paragraph quotes **Hebrews 11:2** for
*"evidence of things not seen."* That phrase is Hebrews 11:**1**; verse 2 reads
*"For by it the elders obtained a good report."* Her page carries the reference
exactly as the book prints it, because that is what she will see in her own DIVE
lesson. If she looks it up and the words do not match, the answer is that the book
cited it one verse off — not that she read it wrong.

## The one figure

- **The graph on page 4** — `f(x) = x²` with the line through (2, 4) and (3, 9).
  Her page **draws it**: the curve itself, with (1, 1), (2, 4) and (3, 9) marked as
  read-only dots she cannot knock off, sitting under the table of the two rates.
  She is asked to lay a ruler across the first pair of dots and then the second, so
  the 3 and the 5 arrive as a picture and not only as arithmetic. Have her DIVE page
  open alongside so she can match the two.
- **Nothing else.** Both logic examples and Example 81.3 are pure text in the
  source, so every number and every sentence on her page is the book's own.

## Where this sits

Pairs with **DIVE Lecture 81**. Reviews Lessons **5, 28, 35, 44, 55, 62, 66, 68,
70 and 73**. If the calculus half is where she is lost, the lessons to revisit are
**68** and **70** (slope, and Δx / Δy) and **77** (slope from two given points) —
because the calculus is nothing but those. If it is the *letters standing for
sentences* that is bothering her in the logic half, that is not a review problem;
that is new, and it is worth five extra minutes on step 5 above.

**Proficient** looks like: given a conditional statement, she produces the correct
converse, inverse and contrapositive with the rules chart in front of her, and
computes `Δy / Δx` between two given function values.
**Mastered** looks like: she does the flips without the chart, catches the
half-negated inverse in a multiple-choice list without prompting, and can say what
a rate of change *means* — "y is moving five times faster than x here" — not just
compute it.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 81 (converse/inverse/contrapositive; "
            "what is calculus) — idempotent.")

    LESSON_NUMBER = 81
    TITLE = ("Flipping an If-Then Statement — Converse, Inverse and Contrapositive; "
             "What is Calculus?")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
