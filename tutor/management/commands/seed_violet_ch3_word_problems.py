"""Seed the Ch3 L6 "Word Problems" manga (Pokemon Gen 9).

The chapter's payoff: a two-step word problem solved with a bar model, using the
regrouping from L1-L3 and the estimate from L4-L5 as a check. Worked example —
450 stickers, 175 sold in the morning, 138 in the afternoon, how many left?
175 + 138 = 313 (regroup), then 450 - 313 = 137 (regroup), estimate ~450-300=150.

Bar models are Chapter 2's tool (L8-L11). This lesson deliberately reuses them
rather than introducing anything new: the difficulty here is *deciding what to
do*, and that's plenty on its own.

Examples:
    python manage.py seed_violet_ch3_word_problems --curriculum 1
    python manage.py seed_violet_ch3_word_problems --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Sticker Stand — Two-Step Word Problems"

STUDENT_CONTENT = """THE STICKER STAND  ——  Two-Step Word Problems
(a math manga · Chapter 3, Lesson 6: Word Problems)

〈 PAGE 1 〉

PANEL 1 — Wide. A cheerful sticker stand at the Paldea market. Sprigatito, Fuecoco, Quaxly, Pawmi and Lechonk all crowd around it.
CAPTION: The sticker stand opened this morning with 450 stickers.
QUAXLY (behind the counter): We sold 175 before lunch, and 138 after!

PANEL 2 — Pawmi immediately starts scribbling, sparks flying. Fuecoco gently stops it.
PAWMI: 450 minus 175 minus— wait— minus 138— aaah!
FUECOCO: Slow down. DRAW it first. What do we know?

PANEL 3 — Fuecoco sketches a long bar in the dust with a claw.
FUECOCO: One long bar — that's ALL 450 stickers.
FUECOCO: Now cut it into the parts we know.

〈 PAGE 2 — STEP 1: PUT THE PARTS TOGETHER 〉

PANEL 4 — BIG. The bar in the dust: one long bar split into three sections — 175, 138, and a mystery section with a question mark.
▷ 450 total  =  175 sold  +  138 sold  +  ? left
CAPTION: Two parts we know. One part we don't. That's TWO steps.
SPRIGATITO: We can't take away the leftover — we don't know it yet!

PANEL 5 — BIG. The two sold sections slide together into one combined block.
▷ STEP 1:  175 + 138 = 313   (5 + 8 = 13, carry a ten — then 7 + 3 + 1 = 11, carry a hundred!)
CAPTION: First, add what we SOLD. That's one number now.
PAWMI (proud): Two carries! Bundle ten, carry one — twice! I remember!

〈 PAGE 3 — STEP 2: TAKE IT AWAY 〉

PANEL 6 — BIG. The combined 313 block lifts away from the long 450 bar, leaving the mystery section behind.
▷ STEP 2:  450 - 313 = 137   (regroup: 0 - 3 won't go — open a ten!)
CAPTION: Now take the sold stickers off the whole. What's left is the answer.
QUAXLY: One hundred thirty-seven stickers left!

PANEL 7 — Lechonk, unbothered as ever, checks the work with a quick estimate.
LECHONK: About 450 take away about 300… that's about 150.
LECHONK: 137 is right around there. Believable.

〈 PAGE 4 〉

PANEL 8 — Full. All five friends at the stand at sunset, sharing out the last stickers.
★ TWO-STEP RULE ★
Draw the bar first. Find the part you CAN work out, do that step, then use it to get the answer. Then estimate to check it's believable.
FUECOCO: Draw it, then decide. Never decide first.
PAWMI (covered in stickers): Draw, step, step, check!   ★ END OF CHAPTER 3 ★"""

STUDENT_INTRO = (
    "Some word problems can't be answered in one move — you have to work out a "
    "middle number first. The trick is to DRAW it before you decide anything: one "
    "long bar for the whole, cut into the parts. Then you can see which step you're "
    "able to do first. Watch the friends work out how many stickers are left after "
    "a day of selling (450, 175, 138) — and use everything from this chapter to "
    "do it."
)

PARENT_CONTENT = """## The big idea

This lesson is the chapter's payoff. It uses the regrouping from L1-L3 and the estimate from L4-L5, and adds one genuinely new demand: **deciding what to do first**.

**450 stickers. 175 sold in the morning, 138 in the afternoon. How many left?**

- **Step 1 (combine the parts we know):** 175 + 138 = **313** — regroups **twice**: 5 + 8 = 13 carries a ten, then 7 + 3 + 1 = 11 carries a hundred. That second carry is the one that gets dropped.
- **Step 2 (take that from the whole):** 450 - 313 = **137** — one ordinary regroup: 0 - 3 won't go, so open a ten. (Not the across-zeros case from Lesson 3 — the tens digit here is 5, so there *is* something to borrow.)
- **Check:** 450 is already a round number, so leave it and round 313 to 300: about 450 - 300 ≈ 150. 137 is right around there. ✓ (Rounding 450 up to 500 as well would give 200 — still enough to catch a wildly wrong answer, but a looser check. Worth saying out loud that you *chose* not to round it; that judgement is exactly what Lesson 5 was about.)

## Why bar models, again

Bar models are Chapter 2's tool (L8-L11), and reusing them here is the point: nothing about the *drawing* should be new, so all her attention can go on the decision. One long bar is the whole; the cuts are the parts; the question mark marks what's unknown. Once it's drawn, the two steps are usually visible rather than deduced.

## The one thing to insist on

**Draw before deciding.** The universal failure mode with two-step problems is grabbing the numbers in the order they appeared in the sentence — 450 - 175 - 138 attempted as one move, or 450 - 175 and then stopping, answer 275, feeling finished. Neither is a calculation error; both are decision errors made before the child understood the shape of the problem.

A drawn bar makes "we don't know that part yet" *visible*. That's what stops it.

## Questions that help more than hints

- *"What are we trying to find?"* — say it in words before touching numbers.
- *"What do we know for certain?"*
- *"Is there anything we can work out right now, even if it isn't the answer?"* — this is the two-step question.
- *"Does that answer make sense?"* — estimate at the end, every time.

## The classic mix-ups

- **Answering the middle step.** She computes 313 and writes it down as the answer. Ask her to reread the actual question aloud — this one is very common and completely fixable.
- **Subtracting in the order the words appear** without checking whether that's the shape.
- **Dropping the regrouping** under the extra load of the story. Two-step problems make familiar arithmetic wobble; that's expected, not a regression.

## Extend it

Give her the same three numbers and ask a *different* question — *"how many more sold in the morning than the afternoon?"* — so she has to redraw rather than reuse. Then have her **write her own** two-step problem for you to solve. Writing one requires knowing where the hidden middle step lives, which is a stronger test than solving one.

## A note on the manga

Everyone returns — the berry-stand trio from L1-L3 and the festival pair from L4-L5 — because this lesson gathers up the whole chapter. Panel 4 gives the drawn bar a full panel *before* any arithmetic happens, and Lechonk's estimate at the end closes the loop back to Lessons 4 and 5."""


class Command(MangaSeedCommand):
    help = "Seed the Ch3 L6 'The Sticker Stand' two-step word problems manga (idempotent)."

    CHAPTER = 3
    LESSON_NUMBER = 6
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
