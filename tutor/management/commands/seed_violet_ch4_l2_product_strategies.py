"""Seed the Ch4 L2 "The Drying Yard — Strategies for Finding the Product" manga (Pokemon Gen 9).

There is a big rack of berries drying in the sun: 6 rows of 7.

Examples:
    python manage.py seed_violet_ch4_l2_product_strategies --curriculum 1
    python manage.py seed_violet_ch4_l2_product_strategies --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Drying Yard — Strategies for Finding the Product"

STUDENT_CONTENT = """THE DRYING YARD  ——  Strategies for Finding the Product
(a math manga · Chapter 4, Lesson 2: Strategies for Finding the Product)

〈 PAGE 1 〉

PANEL 1 — Wide. Early morning in the orchard's drying yard. A long low rack on trestles holds berries laid out in neat rows. Sprigatito, Fuecoco, Quaxly, Pawmi and Lechonk gather around it.
CAPTION: The big drying rack holds 6 rows of 7 berries.
QUAXLY (checking the rack): Six rows of seven. Nobody count them one at a time.

PANEL 2 — Normal. Pawmi immediately counts them one at a time, sparks flying. Fuecoco lowers a claw to stop it.
PAWMI: One, two, three, four— wait, where was I? Aaah!
FUECOCO: Slow down. You already KNOW a fact that's close.

〈 PAGE 2 — BREAK A ROW OFF 〉

PANEL 3 — Full. Seen from a high angle. A thin wooden slat is laid across the rack, cutting it into a block of five rows and one lonely row.
CAPTION: 6 rows of 7  =  5 rows of 7  +  1 row of 7.     Lay a slat across it — two easy racks instead of one hard one.
SPRIGATITO (paw on the slat): Split it where the easy fact lives — I know my fives!

PANEL 4 — Full. The five-row block glows. Down its columns the berries bundle into seven little stacks of five. Pawmi hops from stack to stack.
CAPTION: 5 × 7 = 35 — five rows of seven. Look down the columns and it is seven fives: 5, 10, 15, 20, 25, 30, 35.     The part we already knew is done — one row is still waiting.
PAWMI (delighted): Seven fives! I can do fives all day!

PANEL 5 — Normal. Sprigatito carries the leftover row back and slides it against the big block. Quaxly watches, pleased.
CAPTION: One more ROW is 7 more berries, not 1 more:  35 + 7 = 42.     So 6 × 7 = 42.
QUAXLY: Forty-two berries — from a fact we already knew.

〈 PAGE 3 — OR JUST DOUBLE IT 〉

PANEL 6 — Full. A smaller tray holding two rows of eight. Its identical twin slides in against it, making four rows of eight.
CAPTION: DOUBLE IT — 4 × 8 is double 2 × 8.     2 × 8 = 16, and 16 + 16 = 32.     So 4 × 8 = 32.
FUECOCO: Twice the rows, twice the berries.
PAWMI: Double it? That's the WHOLE trick?

PANEL 7 — Normal. Lechonk, flat on its side in the shade, does not move but does check the answer.
CAPTION: Check: 5 × 7 = 35 and 7 × 7 = 49. Six sevens has to land between them — and 42 does.
LECHONK: More than 35, less than 49. Forty-two fits just fine.

〈 PAGE 4 〉

PANEL 8 — Full. Sunset over the drying yard. All five friends carry the finished berries down in crates.
CAPTION: ★ THE STRATEGY ★   Never count one at a time. Start from a fact you know: break a row off (6 × 7 = 5 × 7 + 7) or double a smaller fact (4 × 8 = double 2 × 8).
FUECOCO: Every fact you know saves you a whole lot of counting.
PAWMI (arms full of berries): Split it or double it!"""

STUDENT_INTRO = """There is a big rack of berries drying in the sun: 6 rows of 7. Counting them one at a time would take all morning — so the friends do something much smarter. They lay a slat across the rack and cut it into a part they already know (5 rows of 7) and one leftover row. Then they use a second trick: some racks you can just DOUBLE. Watch how a fact you already know turns into a fact you don't."""

PARENT_CONTENT = """## The big idea

This lesson teaches no new facts. It teaches the move that makes the facts learnable: **use a fact you already know to reach one you don't.**

**Worked example — 6 × 7, starting from 5 × 7.**

- Break the 6 rows into **5 rows and 1 row**.
- 5 × 7 = **35** — and if you look down the columns of that block, it is seven fives: 5, 10, 15, 20, 25, 30, 35.
- One more row is **7** more berries: 35 + 7 = **42**.
- So **6 × 7 = 42**.

**Second strategy — doubling.**

- 2 × 8 = **16**.
- 4 rows is twice as many rows as 2 rows, so the answer doubles: 16 + 16 = **32**.
- So **4 × 8 = 32**.

Doubling is not a separate idea — it's the same break-apart with the two pieces equal: **4 × 8 = 2 × 8 + 2 × 8**. If she notices that herself, she has understood the whole lesson.

The split is not unique, and it's worth showing her that. **6 × 7 = 3 × 7 + 3 × 7 = 21 + 21 = 42** works too, which means 6 × 7 is also just **double 3 × 7**. Same rack, cut in a different place, same 42.

## Why the array gets cut in half on the page

The formal name for this is the distributive property, and she should not hear that name for years. What she should see is a rectangle of berries getting a stick laid across it.

An array makes the split honest. Nothing is added and nothing is lost when the slat goes down — the same berries are simply in two groups now, and both groups are still perfectly rectangular. Written as a bare rule, **6 × 7 = 5 × 7 + 7** is something to trust; drawn as a rack that got cut, it is something she watched happen.

This is also an investment. The split rectangle becomes the area model in fourth and fifth grade, where 6 × 27 gets cut into 6 × 20 and 6 × 7. Every hour spent cutting arrays now is an hour not spent later wondering where the pieces of a multiplication algorithm come from.

## The classic mix-ups

- **Adding 1 instead of adding a row.** She gets 5 × 7 = 35 and writes 36. This is the single most common error in the lesson: the extra piece is one *row*, which is seven berries. Point at the row, not at the number.
- **Doubling one time too many.** For 4 × 8 she finds 2 × 8 = 16, then doubles it to 32 — and doubles again to 64, as if the rows doubled twice. Ask her how many rows she has now: 64 berries would be 8 rows of 8, not 4.
- **Doubling something that can't be doubled.** 5 × 7 is not double 2 × 7. Doubling 2 × 7 gives 4 × 7 = 28, which is four rows — a fifth row of 7 is still missing, and 28 + 7 = 35. Doubling only works when the target has exactly twice as many rows.
- **Forgetting the leftover entirely.** She computes 5 × 7 = 35, feels finished, and reports 35. Same family as the Chapter 3 mistake of answering the middle step. Ask her to point at the rack and say what she still hasn't counted.
- **Splitting one factor but multiplying the leftover by the wrong number.** For 6 × 7 broken as 6 × 5 + 6 × 2, she writes 30 + 2 = 32 instead of 30 + 12 = 42. The leftover is 2 *of the sixes*, not a bare 2.

## Questions that help more than hints

- *"Which fact close to this one do you already know for sure?"* — this is the whole lesson in one question.
- *"Show me where you'd cut it."* — make her point before she writes.
- *"If you take one row away, how many berries did you take away?"*
- *"Is your answer bigger than the fact you started from? By about how much should it be?"*
- *"Could you cut it somewhere else and still get the same answer?"* — the best question of the set, because it moves her from a memorized trick to a flexible one.

## Extend it

Give her 8 × 6 and ask for **two different ways**. Breaking apart gives 5 × 6 + 3 × 6 = 30 + 18 = **48**; doubling gives 4 × 6 = 24, doubled = **48**. Two roads, one answer, and she proved it.

Build a doubling ladder out loud: 2 × 9 = **18**, so 4 × 9 = **36**, so 8 × 9 = **72**. Three facts, one known fact and two doublings.

On graph paper, have her outline a 6-by-7 rectangle and physically snip one row off with scissors. Count each piece, then tape it back. The tape is the point — the total never changed.

Then turn the rack sideways: 7 × 6 is the same 42 berries seen the other way. If she splits it as 5 × 6 + 2 × 6 = 30 + 12 = 42, she has just found a third route to the same fact.

## A note on the manga

Panels 3, 4 and 5 are one continuous diagram in three moments — the rack cut, the known part counted, the leftover row slid back — so the split reads as something that *happens* rather than three separate pictures. Lechonk's line in Panel 7 is the sanity check the chapter keeps coming back to: 6 × 7 must sit between 5 × 7 = 35 and 7 × 7 = 49, so 42 is believable and 36 would not have been."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L2 'Strategies for Finding the Product' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 2
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
