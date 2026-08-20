"""Saxon Pre-Algebra Lesson 96 — Probability: Compound Events.

Reviews Lesson 45, and that is the only lesson its first page lists. It is also
the hook: 45 is where she priced a SINGLE event — one flip of a coin, one roll
of a die, one spin of a spinner — and 96 is those same events strung together in
a row. The book's own first page says **No New Rules**, and then gives two
definitions. The whole lesson is one verb: multiply.

Lesson 45 sits outside this course's seeded lessons, the way Lesson 65 did in
Lesson 87 — but unlike 65 it does not have to be guessed at, because this source
describes its contents itself ("you found probabilities for several simple
events, like the probability of flipping a coin one time, rolling a die one
time, spinning a number spinner one time"). So the hook is hung on the book's own
sentence rather than on an assumption.

Judgement calls, all of them flagged where she reads them:

* The book gives no reason WHY multiplying is the right verb. It argues only
  that two-in-a-row ought to be *less* probable than one — which rules addition
  out without ruling multiplication in. So the four ways two flips can land
  (HH, HT, TH, TT) are listed here as a table, with a line saying plainly that
  the book does not draw it. It costs one table and it turns the rule into
  something she can see. It also makes Example 96.1b legible: *tails first,
  heads second* is one row out of four, not "either order".
* The book's definition of independent events is worded backwards-sounding —
  events are independent "if the conditions are not identical for each event."
  It is kept as it stands and explained (a real hand never sets a coin up the
  same way twice, which is exactly why one flip cannot push the next around),
  rather than quietly replaced with a tidier definition she would not recognise
  in her book.
* The tool is the ratio bar showing four equally likely endings, with the slider
  running out to 25 — which is the book's own page-2 experiment, "flip a coin
  two times in a row, and do that experiment 100 times." The slider is the ratio
  bar's SCALE, so what it sets is each ending's count; the number of experiments
  is the TOTAL row, four times that, which is why the far right reads HH 25
  against a total of 100. The block says exactly that, because calling the slider
  itself the run count contradicts what she can read on the screen. The reveal's
  second half is that same sentence's *probably, not definitely*.
* The reveal's first half — that HT and TH together are 2/4, so "one of each in
  either order" is twice as likely as HH — is arithmetic the book does not do.
  It is marked on her page as an extension, and it is the same multiplying
  counted honestly.
* The Scripture close is kept, in the book's own frame, the way Lesson 81 kept
  its logic-and-naturalism pages — and in its own block AFTER the ten-rolls
  arithmetic, which is the book's own order: the 1/60,466,176 comes first, and
  the casting-lots passage follows it, running from the foot of page 2 onto
  page 3. Setup and payoff stay together.
* The opening coin experiment is this page's, not the book's — the book only
  says "It's more difficult to do this than to get heads on one flip, right?" So
  the four-attempts figure is written as an average with its spread admitted, an
  attempt is defined (a tails ends it), and the SAY block answers its own
  question rather than leaving her a binary she cannot settle from the page. A
  page whose third idea is *probably, not definitely* cannot open by promising
  her a result that one run of the experiment does not owe her.

No figure is missing from this lesson. The teaching is prose and two worked
examples with nothing drawn; the practice set's pictures (1088's cylinder,
1379's graph, 1553's similar triangles) belong to review problems from other
lessons, so nothing on this page depends on seeing anything.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_96 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 96 · Pre-Algebra",
        "title": "Two in a row is harder, so the number gets smaller",
        "thesis": "When two things have to happen one after the other, you "
                  "**multiply** their probabilities. You never add them — adding "
                  "makes a lucky run look easier the longer you make it, which is "
                  "backwards, and you can prove it is backwards with a coin.",
        "formula": "1/2 × 1/2 = 1/4",
        "roles": [
            {"tone": "start", "name": "one event — the Lesson 45 part",
             "text": "A single flip, a single roll, a single spin. Count the ways "
                     "to win, put that over all the ways it could land. Every "
                     "problem today is built out of these."},
            {"tone": "move", "name": "the next event — it does not remember",
             "text": "Independent means the second flip does not care what the "
                     "first one did. Same coin, same two faces, same 1/2. Nothing "
                     "is ever due."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody multiplies instead of adding",
        "paragraphs": [
            "Get a coin out of a drawer before you read any further. This one is "
            "worth doing with your hands.",
            "Flip it once and try for heads. You will manage it about half the "
            "time, and when you miss you just flip again. Now try for heads "
            "**twice in a row** — not two heads eventually, two heads back to "
            "back, on flip one and flip two. A tails ends the attempt, and you "
            "start counting again from zero. So count **attempts**, not flips, and "
            "run the whole thing several times over. It averages out at about four "
            "attempts — and *averages out* is the honest way to say it, because you "
            "might do it on the first go, and you might still be flipping after a "
            "dozen.",
            "That is the entire lesson and you found it yourself. A run of luck "
            "gets **harder** the longer you ask it to be. So whatever arithmetic "
            "joins events together, it has to make the number *smaller* each time "
            "another event is added.",
            "Which is where the obvious guess falls over. Heads is 1/2, so two "
            "heads must be 1/2 + 1/2 — and that comes to 1. A probability of 1 "
            "means **certain**. Adding claims that flipping a coin twice "
            "guarantees two heads, and you have just spent a minute disproving "
            "that with a coin in your hand.",
            "In **Lesson 45** you worked out the probability of one event: one "
            "flip, one roll of a die, one spin of a number spinner. Lesson 96 is "
            "those same events lined up in a row. The only new thing is which "
            "operation goes between them.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "Multiply, and watch the number shrink",
        "paragraphs": [
            "Here is the rule, and it is the only rule in the lesson. **Work out "
            "the probability of each event on its own, then multiply them "
            "together.**",
            "One flip landing heads is 1/2. Two flips landing heads is 1/2 × 1/2, "
            "which is 1/4. Read those as percentages and they are believable at "
            "once: a **50%** chance of heads on one flip, a **25%** chance of "
            "heads twice running. Fifty percent for the easy thing, twenty-five "
            "for the harder thing.",
            "Multiplying always makes it smaller here, because every probability "
            "here is a fraction of one. Taking half of something leaves you with "
            "less than you started with, and a third flip takes half again.",
            "So you know the shape of the right answer before you start. Add an "
            "event, get a smaller number. If your answer came out **bigger**, you "
            "added somewhere, and you can catch that without checking a single "
            "digit of your arithmetic.",
            "The top of your book's first page says **No New Rules** — and then it "
            "gives you two definitions. That is a fair description. Multiplying "
            "fractions is work you have been doing for years. What is new today is "
            "a *decision*: noticing that a question is asking for two things to "
            "happen in a row, and reaching for × instead of +.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Grab a coin. You flip, I'll count. First job, easy one: get "
                "heads. Good. Now the real one — heads twice in a row, and a tails "
                "anywhere ends the attempt and starts you again from zero. Keep "
                "going until you do it, and tell me how many attempts that took. "
                "Now, from your hand and not from the page: was that harder than one "
                "flip? Right — and here is the size of it, which is the whole "
                "lesson. One head takes about two attempts. Two in a row takes "
                "about four. Twice the waiting, because the half turned into a "
                "quarter.\"",
    }),

    (B.KIND_MATH, {
        "display": "1/2 × 1/2 = 1/4",
        "note": "Half of all flips land heads. Then half of **those** get a second "
                "head. A quarter of the pairs survive both, which is the same as "
                "saying you should **expect** about four attempts before you see it "
                "once. *Expect* is carrying real weight in that sentence: it is what "
                "the flipping averages out to if you keep going, and a single run "
                "proves nothing either way — which is the third idea further down "
                "this page, arriving early. And notice that 1/4 is smaller than "
                "either fraction that went into it. That is the signature of events "
                "strung in a row, and it is the fastest check you own.",
    }),

    (B.KIND_TABLE, {
        "caption": "Every way two flips can land — the picture your book does not "
                   "draw",
        "headers": ["flip 1", "flip 2", "the pair", "heads twice?"],
        "rows": [
            {"cells": ["heads", "heads", "H H", "yes"], "emphasis": True},
            {"cells": ["heads", "tails", "H T", "no"]},
            {"cells": ["tails", "heads", "T H", "no"]},
            {"cells": ["tails", "tails", "T T", "no"]},
        ],
        "note": "Four endings, and the coin has no reason to prefer any of them, "
                "so each one is worth 1/4 — the same 1/4 that 1/2 × 1/2 gives you. "
                "That is where the multiplying comes from: each flip **splits** "
                "every ending into two, so two flips make 4 endings and three "
                "flips make 8. Your book does not print this table. It argues only "
                "that two-in-a-row must be less likely than one, and then tells "
                "you to multiply; the table is here so the rule is something you "
                "can see instead of something you were handed. Read the two middle "
                "rows slowly — **H T and T H are different results**, and Example "
                "96.1b is about exactly one of them.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "Independent means the coin has no memory",
        "paragraphs": [
            "Your book puts two definitions on page 1, and they are the only "
            "new vocabulary in the lesson.",
            "**Compound events** happen consecutively — \"in a row,\" as the book "
            "puts it. Two flips in a row, three rolls in a row. You answer them as "
            "one group, while still working out each event's probability "
            "separately.",
            "**Independent events** are ones where the probability of the next "
            "event does not depend on what happened in the first. The coin does "
            "not know it just landed heads. It has no memory, no momentum, and no "
            "sense that anything is owed.",
            "Read the book's wording of that one twice, because it sounds "
            "backwards at first: events are independent, it says, if the "
            "**conditions are not identical** for each event. A real coin flipped "
            "by a real hand is never set up the same way twice — different height, "
            "different spin, different bounce — and that is precisely why one flip "
            "cannot push the next one around.",
            "Then it makes that concrete with a robot, and the robot is the best "
            "thing on the page. Imagine building a machine to flip a coin: the "
            "coin starts in the same spot every time, the same button releases it, "
            "the same force turns it, the room's air never changes, and it lands in "
            "sand so it cannot bounce or spin. Build that and you have taken the "
            "independence away. The next flip now **depends** on the conditions "
            "being the same as the last one, and those are dependent events.",
            "Which leaves a standing instruction worth writing at the top of your "
            "practice set: for every compound-events problem in this course, "
            "**assume the events are independent**. You are not being asked to "
            "judge it. You are being told.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, and only one of them is new",
        "steps": [
            {"label": "Chop the sentence into single events.",
             "detail": "*Two times in a row* is two events. *Three times in a row* "
                       "is three. Every \"and then\" is a cut. Write them left to "
                       "right in the order the question gives them, with a gap "
                       "between each — the order is part of the question."},
            {"label": "Price each event on its own. This is Lesson 45.",
             "detail": "Count the outcomes that win, and put that over how many "
                       "outcomes there are altogether. Heads is 1 face out of 2. A "
                       "3 on a die is 1 face out of 6.",
             "math": "wins / all the ways it could land"},
            {"label": "Simplify anything that will simplify, before you multiply.",
             "detail": "*Greater than 3* on a die is three faces out of six, and "
                       "three sixths is one half. Doing that now keeps the numbers "
                       "small enough to hold in your head.",
             "math": "3/6 = 1/2"},
            {"label": "Multiply straight across.",
             "detail": "Tops times tops, bottoms times bottoms, and nothing else. "
                       "This is the one move that is new today and it is one line "
                       "long.",
             "math": "1/6 × 1/2 = 1/12"},
        ],
        "after": "Then check the **shape** of the answer before you check the "
                 "digits: it has to be smaller than every fraction that went into "
                 "it. If it is not, you added. That check takes a second and it "
                 "catches the one mistake this lesson is really about.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 96.1 — one coin, flipped again, and again",
        "equation": "a) tails, tails   ·   b) tails, then heads   ·   c) heads, "
                    "heads, heads",
        "steps": [
            {"label": "Look first",
             "text": "Three questions about the same coin, and every single event "
                     "in all three is worth the same **1/2**. A coin has two faces "
                     "and they are the only two things that can happen, so heads "
                     "is 1 out of 2 and tails is 1 out of 2. No part of this "
                     "example needs a different fraction. What changes from a) to "
                     "c) is only **how many** of them get multiplied."},
            {"label": "a) tails twice in a row",
             "text": "Two events, each one worth 1/2. Multiply them and you are "
                     "done — this is the whole method, on its simplest possible "
                     "question.",
             "math": "1/2 × 1/2 = 1/4"},
            {"label": "b) tails first, then heads",
             "text": "Read this one slowly, because it looks like it ought to be "
                     "different and it is not. Tails is 1/2. Heads is also 1/2. "
                     "The coin does not charge extra for changing its mind. Your "
                     "book says it in one line: landing on either heads or tails "
                     "has a probability of 1/2, therefore the result is the same "
                     "as a).",
             "math": "1/2 × 1/2 = 1/4"},
            {"label": "Where b)'s quarter lives in the table above",
             "text": "Go back to the four pairs. **T H** is one row out of the "
                     "four, which is the same 1/4 arriving by a different road. "
                     "And notice what it is *not*: it is not \"one of each, in any "
                     "order\" — that would be two rows. The question named an "
                     "order, so only one row counts."},
            {"label": "c) heads three times in a row",
             "text": "Three events now, so three halves get multiplied. Your book "
                     "does it in two bites: the first two flips give 1/4, and then "
                     "the third flip halves that again.",
             "math": "1/2 × 1/2 × 1/2 = 1/4 × 1/2 = 1/8"},
            {"label": "Read the three answers as a run",
             "text": "1/4, 1/4, 1/8. Adding a flip did not *add* anything — it "
                     "**halved** what was already there. A fourth flip would give "
                     "1/16 and a fifth 1/32. Every event you tack on the end makes "
                     "the whole run rarer, and it never works the other way.",
             "math": "1/4   →   1/8   →   1/16   →   1/32"},
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "One die, six faces — which faces answer which question",
        "headers": ["the question", "the faces that win", "how many", "as a fraction"],
        "rows": [
            {"cells": ["lands on 3", "3", "1 of 6", "1/6"], "emphasis": True},
            {"cells": ["greater than 3", "4, 5, 6", "3 of 6", "3/6 = 1/2"],
             "emphasis": True},
            {"cells": ["3 or greater", "3, 4, 5, 6", "4 of 6", "4/6 = 2/3"]},
            {"cells": ["an even number", "2, 4, 6", "3 of 6", "3/6 = 1/2"]},
        ],
        "note": "A **die** is one 6-sided number cube; **dice** is two or more of "
                "them. Your book stops to say so, and points back to Lesson 45, "
                "because most of the difficulty in a probability question is "
                "vocabulary rather than arithmetic. Rows two and three are the "
                "pair to be careful with: **greater than 3 does not include the "
                "3**. Three faces beat a 3; four faces are 3 or better. Example "
                "96.2b needs row two, and reading it as row three changes the "
                "final answer.",
    }),

    (B.KIND_WORKED, {
        "number": "96.2",
        "question": "What is the probability of rolling a die a) twice, and having "
                    "it land on 3 both times? b) twice, and having it land on 3 "
                    "the first time, and a number greater than 3 the second time?",
        "steps": [
            {"label": "What a die is, before anything else",
             "text": "A die is a 6-sided number cube — the singular of *dice* — and "
                     "your book points back to Lesson 45 for it. Six faces, none "
                     "of them favoured, so any one named face is **1 out of 6**."},
            {"label": "a) a 3, and then a 3 again",
             "text": "Two events. The first is 1 chance in 6. The second is also 1 "
                     "chance in 6, because the die has no memory of the roll "
                     "before it. Multiply straight across: the tops make 1 and the "
                     "bottoms make 36.",
             "math": "1/6 × 1/6 = 1/36"},
            {"label": "b) the first roll — the same 1/6",
             "text": "Nothing new here. Landing on a 3 is one face out of six, "
                     "exactly as it was in part a)."},
            {"label": "b) the second roll — count the faces that beat a 3",
             "text": "*Greater than 3* means 4, 5 or 6. That is three faces out of "
                     "six, and 3/6 simplifies to **1/2** — so this event turns out "
                     "to be as likely as a coin landing heads. Simplify it now, "
                     "while the numbers are still small."},
            {"label": "b) multiply the two events together",
             "text": "One sixth for the 3, one half for the *greater than 3*. Same "
                     "move as every other problem on this page.",
             "math": "1/6 × 3/6 = 1/6 × 1/2 = 1/12"},
            {"label": "Look at the two answers side by side",
             "text": "1/36 and 1/12. The second one is **bigger**, and it should "
                     "be: *greater than 3* can be satisfied three different ways "
                     "and *a 3* only one. More ways to win means a bigger "
                     "probability. That is worth asking yourself at the end of "
                     "every compound-events problem, because it catches a "
                     "miscounted face without any arithmetic."},
        ],
        "answer": "1/36 · 1/12",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "start",
        "title": "Probably. Not definitely — and rarer the longer the run.",
        "paragraphs": [
            "There is a word your book keeps insisting on, and it is the whole "
            "difference between mathematics and fortune telling. All of this is "
            "**probability**, not certainty.",
            "Flip a coin 100 times and it will *probably* land heads about 50 "
            "times — not definitely 50. Flip it twice in a row, and run that "
            "experiment 100 separate times, and *probably* about 25 of those "
            "attempts will be heads both times. The 1/4 tells you what to expect "
            "across a lot of tries. It promises nothing whatsoever about the next "
            "two flips.",
            "The other half of this idea is what happens as a run gets longer. "
            "Every extra event multiplies by another fraction smaller than one, so "
            "the probability of a predictable run **decreases as the number of "
            "events increases**. Your book picks a deliberately absurd example to "
            "show it off: a die landing on 2, ten times in a row. That number is "
            "in the box below.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "1/6 × 1/6 × 1/6 × 1/6 × 1/6 × 1/6 × 1/6 × 1/6 × 1/6 × 1/6 = "
                   "1/60,466,176",
        "note": "Ten rolls, every one of them landing on 2. Your book states the "
                "answer — **1/60,466,176** — without working it out, so here it is "
                "worked out: ten sixths, multiplied. Each extra roll makes the "
                "bottom of the fraction six times bigger, which is how something "
                "that starts at a perfectly ordinary 1-in-6 reaches sixty million "
                "to one in ten steps. Sixty million is roughly the number of people "
                "in Italy. That is the size of the crowd you would need for one of "
                "them, probably, to manage it.",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "move",
        "title": "Where your book finishes: casting lots",
        "paragraphs": [
            "Your book ends the lesson somewhere you might not expect it to, and it "
            "waits until the arithmetic is done before it goes there. The dice "
            "first. Then this.",
            "Rolling dice is old — thousands of years old — and people have used it "
            "not only to play games but to choose between one person and another, "
            "one group and another. Scripture calls that **casting lots**.",
            "It points at **Proverbs 16:33**, where the lot is cast into the lap but "
            "its every decision is from the Lord, and at **Psalm 22:18**, a prophecy "
            "fulfilled in the New Testament when lots were cast for Jesus' clothing. "
            "Its conclusion is that God is ruler over all creation, including the "
            "outcome of every single dice roll ever made or yet to be made.",
            "That is a good thing to hold next to a fraction, and it is worth reading "
            "slowly rather than stepping over on the way to the practice set. The 1/6 "
            "describes what you should expect. Your book is saying it is not the last "
            "word on what happens.",
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The wording, decoded",
        "intro": "There is almost no notation in this lesson. Most of the "
                 "difficulty is in the English — these are the phrases that decide "
                 "what you multiply.",
        "rows": [
            {"symbol": "in a row",
             "plain": "consecutively — one event, then the next, in that order. "
                      "This is the phrase that tells you to multiply",
             "example": "heads twice in a row"},
            {"symbol": "compound events",
             "plain": "two or more events happening consecutively, treated as one "
                      "group but priced one at a time",
             "example": "flip, then flip again"},
            {"symbol": "independent events",
             "plain": "the next event does not depend on what the last one did. "
                      "Assume this on every compound-events problem in this "
                      "course",
             "example": "the coin has no memory"},
            {"symbol": "dependent events",
             "plain": "the opposite — the next event's chances are changed by the "
                      "last one. The robot's coin. Not asked for here",
             "example": "same spot, same force"},
            {"symbol": "die / dice",
             "plain": "a die is ONE 6-sided number cube; dice is two or more of "
                      "them",
             "example": "roll a die twice"},
            {"symbol": "greater than 3",
             "plain": "4, 5 or 6 — three faces. It does NOT include the 3 itself",
             "example": "3/6 = 1/2"},
            {"symbol": "1/6",
             "plain": "one winning face over six possible faces — a Lesson 45 "
                      "fraction, and where every problem starts",
             "example": "landing on a 3"},
            {"symbol": "×",
             "plain": "the entire lesson. Multiply the events together; never add "
                      "them",
             "example": "1/6 × 1/6 = 1/36"},
            {"symbol": "probably",
             "plain": "what to expect over many tries — never a promise about the "
                      "next one",
             "example": "about 25 out of 100"},
        ],
        "after": "The phrase to hunt for is **in a row**. Once you have found it, "
                 "the rest of the sentence is only a list of single events, and "
                 "you already knew how to price each of those in Lesson 45.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Adding the probabilities instead of multiplying.",
             "wrong": "1/2 + 1/2 = 1",
             "right": "1/2 × 1/2 = 1/4",
             "note": "**A probability of 1 means certain.** Adding claims that "
                     "flipping a coin twice guarantees two heads, which you can "
                     "disprove in ten seconds with a real coin — and your book "
                     "opens the lesson with exactly that argument. Stringing "
                     "events together always makes the number smaller; addition "
                     "always makes it bigger. They pull in opposite directions, so "
                     "addition cannot be the right tool."},
            {"name": "Multiplying the tops but adding the bottoms.",
             "wrong": "1/6 × 1/6 = 1/12",
             "right": "1/6 × 1/6 = 1/36",
             "note": "**1/12 instead of 1/36** — three times too likely. "
                     "Multiplying fractions is tops times tops and bottoms times "
                     "bottoms, and 6 times 6 is 36, not 12. This one is arithmetic "
                     "rather than probability, and it hides well: 1/12 is smaller "
                     "than 1/6, so it sails straight past the did-it-get-smaller "
                     "check."},
            {"name": "Letting \"greater than 3\" include the 3.",
             "wrong": "4/6 = 2/3   →   1/6 × 2/3 = 1/9",
             "right": "greater than 3 is 4, 5 and 6   →   3/6 = 1/2   →   "
                      "1/6 × 1/2 = 1/12",
             "note": "**1/9 instead of 1/12** on Example 96.2b. *Greater than* "
                     "means strictly bigger — a 3 is not greater than itself. "
                     "Count the winning faces out loud, on your fingers, before "
                     "you write any fraction down. There are three of them."},
            {"name": "Stopping one event short.",
             "wrong": "heads three times in a row   →   1/2 × 1/2 = 1/4",
             "right": "three flips means three halves   →   1/2 × 1/2 × 1/2 = 1/8",
             "note": "**1/4 instead of 1/8** on Example 96.1c. Three times in a "
                     "row is three events, so three fractions get multiplied. "
                     "Write one fraction per event with a gap between them before "
                     "you multiply anything — a missing event is much harder to "
                     "overlook when there is a visible hole where it should be."},
            {"name": "Thinking the coin is due.",
             "wrong": "four heads already, so tails is more likely now",
             "right": "the coin has no memory   →   the fifth flip is still 1/2",
             "note": "The most expensive mistake in the whole topic, and it is not "
                     "arithmetic at all — grown adults lose real money to it. "
                     "**Independent means the next event does not depend on the "
                     "last one.** A coin that has just landed heads four times is "
                     "still a coin: two faces, 1/2 each. What is genuinely rare is "
                     "the whole run of five — and you can only say that **before** "
                     "you start flipping. Once the four heads have happened they "
                     "are not a probability any more. They are a fact."},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "One hundred pairs of flips",
        "intro": "Four bars, one for each way two flips can land — the table from "
                 "further up the page, wired up. They are all the same length "
                 "because no ending is fancier than any other. The slider sets "
                 "**how many times each ending happens** — that is the number at "
                 "the end of each bar's own row. The **TOTAL** row underneath adds "
                 "the four of them up, and *that* is how many times you ran the "
                 "experiment. Drag to the far right and every ending reads 25 while "
                 "the total reads 100: flipping a coin twice, a hundred separate "
                 "times over. Keep your eye on the TOTAL row the whole way.",
        "widget": "ratiobar",
        # Four parts of ratio 1 — the four ways two flips can land, equally
        # likely, so the bars come out identical and HH is VISIBLY a quarter of
        # the total rather than a quarter she was told about. HH is the "move"
        # tone so the one she is chasing is the one that stands out.
        #
        # target 25 against maxScale 25: sliding to the far right reads HH = 25
        # with the total at 100, which is the book's own page-2 sentence — "flip
        # a coin two times in a row, and do that experiment 100 times, then
        # probably, not definitely, 25 of the attempts will be heads two times in
        # a row" — arrived at by hand instead of by being told.
        "config": {
            "parts": [{"name": "HH", "ratio": 1, "tone": "move"},
                      {"name": "HT", "ratio": 1, "tone": "quiet"},
                      {"name": "TH", "ratio": 1, "tone": "quiet"},
                      {"name": "TT", "ratio": 1, "tone": "quiet"}],
            "target": {"name": "HH", "actual": 25},
            "maxScale": 25, "scale": 1,
        },
        "after": "Start at the far left, where every row reads 1 and the total "
                 "reads 4. That is the fraction itself: **HH is one of the four**, "
                 "and its bar is a quarter as long as the total. Now drag all the "
                 "way right. HH reads 25 and the total reads 100 — the exact "
                 "experiment your book describes on its second page. Then answer "
                 "the drop-down below out loud before you open it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Two questions before you open this. One: why does the widget "
                  "give H T and T H separate rows instead of one row called \"one "
                  "of each\"? Two: slide it until HH reads 25 out of 100 — does "
                  "that mean a hundred pairs of flips will give you exactly 25 "
                  "double-heads?",
        "answer": "**They are two different results, and no.** Take them in "
                  "order.   →   H T means heads first and tails second. T H means "
                  "tails first and heads second. Those are as different from each "
                  "other as 96.1b's *tails first, heads second* is from *heads "
                  "first, tails second*, and each is worth 1/4 on its own. Lump "
                  "them together and you have two rows out of four, so \"one head "
                  "and one tail, in either order\" is twice as likely as heads "
                  "twice — and the widget shows you why, because it takes up two "
                  "bars instead of one. Your book never does this particular sum; "
                  "it is the same multiplying, counted honestly.   →   And no. The "
                  "25 is what to **expect**, not what you are owed. Your book is "
                  "careful with that word: run the experiment a hundred times and "
                  "*probably*, not definitely, about 25 of them will be "
                  "heads-heads. You might get 19. You might get 31. The fraction "
                  "describes the long run, and the long run is the only thing it "
                  "describes.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Compound events happen in a row** — consecutively. Two flips, three "
            "rolls. You answer them as one group.",
            "**Multiply the probabilities. Never add them.** Adding makes a long "
            "run look easier, and a run gets harder the longer it is.",
            "The answer has to come out **smaller** than every fraction that went "
            "into it. If it did not, you added somewhere.",
            "**Independent** means the next event does not depend on the last one. "
            "The coin has no memory, and nothing is ever *due*.",
            "In this course, **assume every compound-events problem is "
            "independent**. Your book says so outright, so you never have to "
            "judge it.",
            "Price each single event the Lesson 45 way — winning outcomes over all "
            "the outcomes — and only then multiply. 1/2 for a coin, 1/6 for one "
            "named face of a die.",
            "**Order is part of the question.** *Tails then heads* is one result "
            "out of four, not two — and it is the same 1/4 as tails twice.",
            "*Greater than 3* on a die is **4, 5 and 6**: three faces, 3/6, which "
            "is 1/2. It never includes the 3 itself.",
            "It is **probability, not certainty**. A hundred pairs of flips gives "
            "you *about* 25 double-heads, not exactly 25.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 96 first. If it didn't quite land, this is here to fix "
    "that — and get a coin out of a drawer before you start, because the first "
    "thing on this page asks you to flip one. The whole lesson is a single "
    "decision: when two things have to happen *in a row*, you multiply their "
    "chances instead of adding them, and the answer gets smaller every time you "
    "add another event."
)

PARENT_CONTENT = """## The big idea

One rule, one page: **the probability of compound events is the probability of
each independent event multiplied together.** `1/2 × 1/2 = 1/4`. That is the
lesson, and her book's page-one heading is honest about it — **No New Rules**,
followed by two definitions.

So the teaching is not about the arithmetic. She can already multiply fractions.
It is about two things that sit underneath it:

1. **Why multiplying and not adding.** Her book's argument is a good one and
   worth repeating in your own words: heads is a 50% shot, so if you *added* you
   would get `1/2 + 1/2 = 1` — a certainty — and that would mean flipping a coin
   twice guarantees two heads. Obviously false, and disprovable with a coin in
   about a minute. Stringing events together must make a run **less** likely, not
   more; addition moves the number the wrong way.
   What her book does *not* do is say where the multiplying comes from. So her
   page adds one table the book does not print: the four ways two flips can land
   — `HH`, `HT`, `TH`, `TT` — each worth a quarter, which is the same `1/4` the
   multiplying gives. It is flagged on her page as an addition. It costs nothing
   and it turns a rule she was handed into one she can see.
2. **Independent.** Her book's definition reads oddly at first — events are
   independent "if the conditions are not identical for each event" — and it is
   worth unpacking rather than skating over. A real hand never sets a coin up the
   same way twice, and *that* is why one flip cannot influence the next. Then
   comes the robot, which is the best paragraph in the lesson: build a machine
   that releases the coin from the same spot with the same force into sand so it
   cannot bounce, and you have made the events **dependent**. Her book then gives
   a standing instruction — for every compound-events problem in this course,
   assume the events are independent — so she is never asked to make the call
   herself.

The third thing, and it is the one that outlives the chapter: **probability is
not a promise.** Flip a coin twice, a hundred times over, and *probably* — not
definitely — about 25 of those attempts are heads twice. Her book italicises this
distinction and so does her page.

The lesson closes with Scripture, and her page keeps it in the book's own frame
and in the book's own place — at the end, *after* the ten-rolls arithmetic rather
than in front of it: dice-rolling is thousands of years old, Scripture calls it
*casting lots* (Proverbs 16:33, and Psalm 22:18 fulfilled at the crucifixion),
and the book's conclusion is that God rules over creation down to the outcome of
every roll. Worth reading together rather than skipping past on the way to the
practice set.

## Teach it out loud in five minutes

Do this with an actual coin. It is the rare lesson where the experiment is faster
than the explanation.

1. Hand her a coin. **"Get heads."** She will, quickly. **"How hard was that?"**
   You want *about half the time*.
2. **"Now get heads twice in a row. A tails ends the attempt and we start again
   from zero. I'm counting attempts."** Let it take as long as it takes — four
   attempts on average, and sometimes far more, which is itself the lesson. Then
   the question that matters — and here is the answer to accept, because she
   cannot get it off the page: **"Was that harder than one flip?"** Yes, plainly.
   So give her the *size* of it, because the size is the lesson: one head takes
   about two attempts, two in a row takes about four. **Twice the waiting, because
   the probability halved.** And if her run took eleven attempts, say so out
   loud — four is what to expect across many goes, not a promise about tonight.
3. Now the arithmetic, and let her walk into the wrong answer first. **"Heads is
   one-half. So two heads in a row is one-half plus one-half — what's that?"**
   She will say 1. **"What does a probability of 1 mean?"** Certain. **"Did that
   coin just behave like it was certain?"** That is the whole argument for
   multiplying, and she made it herself.
4. **"So we multiply instead."** `1/2 × 1/2 = 1/4`. Then convert it out loud: 50%
   for one flip, 25% for two. **"Does 25% look like how many attempts that took
   you?"** Roughly one in four. If her count was nowhere near four, do not paper
   over it — that gap is the third idea on her page arriving early, and it teaches
   more than a tidy match would.
5. Last, the die. **"A 3 on a die is one face out of six. So a 3 twice in a row?"**
   You want `1/6 × 1/6 = 1/36`. Then the part that actually gets missed:
   **"And a number greater than 3 — which faces are those?"** Wait for *4, 5, 6*.
   If she says *3, 4, 5, 6*, do not correct her — ask **"is 3 greater than 3?"**
   and let her fix it herself.

If she gets lost, go back to step 2. Everything on the page follows from the coin
refusing to cooperate.

## The classic mix-ups, with the exact wrong answer each one produces

- **Adding instead of multiplying.** `1/2 + 1/2` = **1** instead of **1/4**. The
  giveaway is that 1 means certainty. Fix: the answer must always come out
  *smaller* than the fractions that went into it.
- **Multiplying the tops but adding the bottoms.** `1/6 × 1/6` written as
  **1/12** instead of **1/36** — three times too likely. This one is fraction
  arithmetic, not probability, and it survives the "did it get smaller?" check,
  so it needs its own look.
- **"Greater than 3" counted as four faces.** She uses `4/6 = 2/3` and gets
  **1/9** instead of **1/12** on 96.2b. *Greater than* excludes the number
  itself. Fix: make her name the winning faces out loud before writing anything.
- **Stopping one event short.** On 96.1c she multiplies two halves and answers
  **1/4** instead of **1/8**. Fix: one fraction written down per event, with gaps,
  *before* any multiplying — a missing event leaves a visible hole.
- **The gambler's fallacy — "it's due."** After four heads she says tails is now
  more likely. It is still `1/2`. This is not in her book by name, but it is
  exactly what *independent* means, and it is the mistake from this lesson that
  people carry into adulthood. The distinction to give her: a run of five is rare
  **before you start**; four heads that have already happened are not a
  probability any more, they are a fact.

## What to watch her do

Watch her **pencil**, in this order:

1. **Does she write one fraction per event before she multiplies?** You want to
   see `1/2   1/2   1/2` sitting on the page with gaps, and only then a `×`
   between them. A child who goes straight to the answer is the child who
   silently drops the third flip on 96.1c.
2. **Does she write a `+` anywhere?** This is the whole lesson and it is visible
   from across the table. Stop her at the plus sign, not at the answer.
3. **On the "greater than 3" part, does she list the faces?** Watch for `4, 5, 6`
   appearing in the margin. A child who converts straight to a fraction without
   listing is guessing at the count, and will include the 3 about half the time.
4. **Does she simplify `3/6` to `1/2` before multiplying, or after?** Before is
   the habit her book models and it keeps the numbers small. After works too, but
   `3/36` needs simplifying at the end and that is one more place to slip.
5. **When she finishes, does she glance back at the fractions she started with?**
   The check is "is my answer smaller than all of them?" — one second, and it
   catches the mistake this lesson is really about. If it is not a habit yet, ask
   her the question out loud each time until it is.

Getting `1/4` is not what to watch for. Practice problems 196, 296 and 396 are
all one multiplication each and she can get them right by pattern-matching. The
habits above are what survive a question where the two events have *different*
probabilities — and in this whole lesson, worked examples and practice set
together, that is **Example 96.2b** and nothing else. It is the one genuinely
hard question here.

## Extend it

- **Run the experiment for real.** Twenty pairs of flips, tally how many pairs
  came out heads-heads. Expected: five. She will almost certainly not get five,
  and that gap *is* the "probably, not definitely" lesson. Worth more than
  another practice problem.
- **Ask her the two-dice question.** What is the probability of rolling two dice
  and getting a 3 on both? Same `1/36` as 96.2a — and then ask why rolling two
  dice at once and rolling one die twice give the same answer. (Because neither
  die knows about the other; independence is not about time.)
- **The widget's other question.** Her page has a ratio bar showing all four
  outcomes. Ask her what "one head and one tail, in either order" is worth. It is
  two bars out of four, so `1/2` — twice as likely as heads-heads. Her book does
  not do this sum; it is the natural next step and her page flags it as an
  extension rather than pretending otherwise.
- **The sixty-million question.** Her book says a die landing on 2 ten times
  running is `1/60,466,176` and does not work it out. Have her do it: ten sixes
  multiplied. Then ask what *eleven* times in a row would be, and let her see
  that she only has to multiply by 6 once more.
- **Where it is not a game.** Two independent systems on an aircraft, each with a
  1-in-1,000 chance of failing, both failing at once: one in a million. That is
  why redundancy is designed the way it is, and it is this lesson exactly.

## Where this sits

DIVE Lesson 96, *Probability: Compound Events*. Reviews **Lesson 45** — the only
lesson its first page lists.

**Lesson 45 is the one to revisit if she is stuck**, and her book describes it in
its own opening paragraph: that is where she found the probability of a *simple*
event — one flip of a coin, one roll of a die, one spin of a number spinner.
Lesson 96 adds nothing to that skill; it only strings the results together. If
she cannot say why a 3 on a die is `1/6`, no amount of work on the multiplying
will help, and Lesson 45 is where to go. That lesson sits outside this course's
seeded pages, so her book is the place to look for it.

**Proficient** looks like: prices each event correctly and multiplies rather than
adds, on questions where every event has the same probability (196, 296, 396,
96.1 and 96.2a).
**Mastered** looks like: handles 96.2b, where the two events have different
probabilities and one of them needs counting first; simplifies before
multiplying; and can say what *independent* means without reciting it — including
why a coin that has just landed heads four times is still a fifty-fifty coin.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 96 (probability: compound events) "
            "— idempotent.")

    LESSON_NUMBER = 96
    TITLE = "Multiply, and Watch It Shrink — Probability: Compound Events"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
