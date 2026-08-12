"""Seed the Ch4 L9 "The Last Picking Day — Two Steps in One Problem" manga (Pokemon Gen 9).

Some problems can't be finished in one move — you have to build a middle number first, then use it.

Examples:
    python manage.py seed_violet_ch4_l9_two_step --curriculum 1
    python manage.py seed_violet_ch4_l9_two_step --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Last Picking Day — Two Steps in One Problem"

STUDENT_CONTENT = """THE LAST PICKING DAY  ——  Two Steps in One Problem
(a math manga · Chapter 4, Lesson 9: 2-Step Word Problems)

〈 PAGE 1 〉

PANEL 1 — Wide. A hilltop berry orchard at golden hour on the last picking day of the season. Four baskets sit in a row under a heavy berry tree. All five friends are there, sleeves rolled up.
CAPTION: Last picking day. Four baskets, six berries in each one.
QUAXLY (checking the baskets): And nine got eaten at snack break. How many are LEFT?

PANEL 2 — Pawmi panics, shoving loose berries back and forth between two little piles and getting nowhere, sparks flying off its cheeks. Fuecoco rests one calm claw on its shoulder.
CAPTION: Two things happened — berries picked, then berries eaten. Which step can you do FIRST?
PAWMI: Six take away nine— four take away nine— AAAH!
FUECOCO: Slow down. Draw it first.

PANEL 3 — Fuecoco crouches and draws one long bar in the soft orchard dirt, then cuts it into four equal sections with a claw.
CAPTION: One bar, cut into four equal parts — one part for each basket.
FUECOCO: Four baskets, all the same size. Equal groups — so we can multiply.

〈 PAGE 2 — THE STEP YOU CAN DO 〉

PANEL 4 — BIG. The bar in the dirt: four equal sections, each one holding six real berries in two rows of three. Off to the side, Sprigatito holds a guilty handful of nibbled berries behind its back.
CAPTION: 4 groups of 6 … then 9 eaten … then ? left. You can't take 9 away yet — there is no whole pile yet.
SPRIGATITO: The eating comes SECOND! You can't take from a pile you haven't picked.

PANEL 5 — BIG. All the berries sweep out of the four sections and gather into ONE single heap inside one long undivided bar. The dividing marks fade away.
CAPTION: STEP 1 — do the step you CAN do:  4 × 6 = 24 berries picked   (6, 12, 18, 24)
PAWMI (bouncing): Six, twelve, eighteen, twenty-four! Four sixes!

〈 PAGE 3 — THEN USE WHAT YOU FOUND 〉

PANEL 6 — BIG. A small cluster of nine berries rolls away out of the big heap toward Sprigatito's guilty pile. The berries still in the bar glow softly.
CAPTION: STEP 2 — use the number you just made:  24 - 9 = 15 berries left
QUAXLY: Fifteen berries left. THAT'S the question they asked.

PANEL 7 — Pawmi throws both paws up and shouts the middle number. Quaxly, patient, points a wingtip back down at the bar in the dirt. Fuecoco smiles, not scolding.
CAPTION: Careful — 24 is the MIDDLE step, not the answer. The question asked how many are LEFT: 15.
PAWMI: Twenty-four! I'm done!
QUAXLY: That's the picking, not the leftovers. Read it again.

〈 PAGE 4 〉

PANEL 8 — Full. Sunset supper on the orchard hill: all five friends around a cloth with the last berries, baskets stacked, harvest finished.
CAPTION: ★ TWO-STEP RULE ★ Draw it first. Do the step you CAN do, then use that number to answer the real question. Multiply then subtract: 4 × 6 = 24, then 24 - 9 = 15. Or multiply then divide: 3 × 8 = 24, then 24 ÷ 4 = 6 in each basket. ★ END OF CHAPTER 4 ★
LECHONK: About 25 picked, about 10 eaten — about 15 left. Believable.
FUECOCO: Do the step you can, then use it."""

STUDENT_INTRO = """Some problems can't be finished in one move — you have to build a middle number first, then use it. On the last picking day of the season, four baskets get filled with six berries each, and then nine berries get eaten at snack break. You can't take nine away until you know how many were picked, so there's a step you CAN do and a step you have to wait for. Watch the friends draw it first, do the step they can (4 x 6 = 24), then use that number to answer the question that was actually asked (24 - 9 = 15). This is the last big idea of Chapter 4 — everything you've learned about equal groups comes together here."""

PARENT_CONTENT = """## The big idea

This is the last concept lesson of Chapter 4, and it is where multiplication earns its keep: a problem that cannot be finished in one move.

**Four baskets are picked with six berries in each. Then nine berries are eaten. How many berries are left?**

- **Step 1 — the step you CAN do:** 4 x 6 = **24** berries picked. Skip-count it if the fact isn't automatic yet: 6, 12, 18, 24.
- **Step 2 — use the number you just made:** 24 - 9 = **15** berries left.
- **Check by running it backwards:** 15 + 9 = 24, and 24 ÷ 4 = 6. Both come out clean.
- **Sanity check:** about 25 picked, about 10 eaten, so about 15 left. 15 is believable.

Not every two-step problem ends in a subtraction. The other common shape is multiply-then-divide: **three rows of eight berries (3 x 8 = 24) shared equally into four baskets (24 ÷ 4 = 6 in each basket).** The structure is identical — find the total first, then act on the total — and it is worth showing her both this week so she doesn't decide that "two-step" secretly means "times then take away".

The whole lesson lives in one sentence: **do the step you can do now, then use that result.**

## Why we draw the bar before deciding anything

The arithmetic here is easy. A child who can do 4 x 6 and 24 - 9 separately can still be completely stuck on this problem, because the difficulty isn't calculation — it's *deciding what to do first*. Drawing removes the deciding from her head and puts it on the paper.

One long bar cut into four equal sections shows the multiplication (equal groups, same size, so multiply). Sweeping those sections into one bar shows why Step 1 has to happen first: the nine eaten berries come off the *whole pile*, and until the bar is whole there is nothing to take them from. That "there is no whole pile yet" moment is the entire lesson, and it is visible in the drawing in a way it never is in the sentence.

This also protects the equal-groups idea she built all chapter. A child who takes 9 from one basket rather than from the total has stopped seeing four equal groups; the drawn bar makes that mistake look wrong instead of merely being wrong.

## The classic mix-ups

- **Answering the middle step.** She works out 24, feels the satisfaction of a finished calculation, and writes it down. This is the single most common third-grade error in two-step problems, and it is not a math error — it's a memory error. The fix is mechanical: after any answer, reread the question aloud and check that the answer matches what it asked.
- **Grabbing the numbers in the order they appear.** The sentence says six, then nine, so she tries 6 - 9 (or 4 - 9) and stalls. Ask what those two numbers even mean together — berries in one basket minus berries eaten by everybody isn't a thing.
- **Doing the second operation on one group instead of the total.** Nine eaten becomes "nine off each basket". Point back at the drawing: the snack came out of the pile, not out of every basket.
- **Losing the unit.** She answers "15 baskets" or answers a berry question with a basket number. Have her say the unit out loud with every answer, including the middle one: "24 berries picked", "15 berries left".
- **Multiplying groups that aren't equal.** If the problem says one basket had four berries and the rest had six, multiplication doesn't apply to all of them. Worth testing her once with an unequal set to see if she notices.

## Questions that help more than hints

- *"What is the question actually asking for?"* — in words, before any numbers get touched.
- *"Is there anything you can work out right now, even if it isn't the answer?"* — this is THE two-step question, and it's the one to keep in your pocket.
- *"What does that number you just found mean?"* — naming 24 as "the berries picked" is what stops her handing it in as the answer.
- *"Now that you know that, what can you do next?"*
- *"Does that make sense?"* — estimate at the end, every single time. Fifteen left out of twenty-four picked feels right; five hundred would not.

## Extend it

Give her the same three numbers — 4, 6, 9 — and ask a different question: *"If the nine eaten berries were shared equally between three friends, how many did each one eat?"* (9 ÷ 3 = 3 each.) She has to redraw rather than reuse, which is the real test.

Then have her **write her own** two-step problem for you to solve, and make one rule: you have to need the middle number. Inventing a problem requires her to know where the hidden step lives, and that's a stronger check on understanding than solving five more of yours.

For a stretch, try a three-step: four baskets of six, nine eaten, then the rest shared equally between five friends. 4 x 6 = 24, 24 - 9 = 15, 15 ÷ 5 = 3 each. The rule doesn't change — do the step you can, then use it.

## A note on the manga

Panels 4 through 6 are deliberately one continuous diagram in three moments: the bar cut into four equal sections, the sections merging into one pile, then a handful rolling away. If she can narrate those three pictures in order, she has the lesson.

Panel 7 exists only to stage the middle-step trap on purpose — Pawmi shouts "twenty-four!" and Quaxly sends it back to the question. Fuecoco never scolds, and neither should we; answering the middle step is what a child does when she's *concentrating*, not when she's careless. It closes with Lechonk's estimate and the end of Chapter 4."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L9 'Two Steps in One Problem' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 9
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
