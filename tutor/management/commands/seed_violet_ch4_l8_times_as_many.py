"""Seed the Ch4 L8 "The Matching Bench — Times as Many" manga (Pokemon Gen 9).

Some word problems compare two amounts instead of adding them up.

Examples:
    python manage.py seed_violet_ch4_l8_times_as_many --curriculum 1
    python manage.py seed_violet_ch4_l8_times_as_many --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Matching Bench — Times as Many"

STUDENT_CONTENT = """THE MATCHING BENCH  ——  Times as Many
(a math manga · Chapter 4, Lesson 8: Word Problems — Part 2)

〈 PAGE 1 〉

PANEL 1 — Wide. The orchard packing yard on a bright morning. A long low sorting bench with a chalk line ruled down it. Fuecoco sets down one small basket of four berries; Quaxly wheels up a barrow of three matching baskets. Sprigatito, Pawmi and Lechonk gather round.
CAPTION: Fuecoco picked 4 berries this morning. Quaxly picked 3 TIMES as many.
QUAXLY: Three times as many as yours, Fuecoco! So how many is that?

PANEL 2 — Pawmi blurts out an answer at once, sparks flying. Fuecoco tips its head, kind as ever.
▷ Careful — "3 times as many" is NOT "3 more."   4 + 3 = 7 answers a different question.
PAWMI: Easy! Four and three more — that's seven!
FUECOCO: Different question. Times means COPIES, not more.

PANEL 3 — Fuecoco slides its one small basket to the left end of the bench, right against the chalk mark.
CAPTION: Fuecoco's whole pick is ONE unit: 4 berries. That's the short bar.
FUECOCO: One basket. That's ONE unit — my whole morning's pick.

〈 PAGE 2 — TWO BARS, ONE STARTING LINE 〉

PANEL 4 — BIG. Fuecoco's single basket of four on the upper line. Directly underneath, starting at exactly the same left edge, Quaxly's three identical baskets of four in a straight row.
▷ Same left edge.  Same size units.  Quaxly's bar is 3 copies of Fuecoco's bar.
CAPTION: Lining the left ends up is the whole trick — now the comparison is something you can SEE.
SPRIGATITO: Line the left ends up! Now you can SEE how much longer Quaxly's is.

PANEL 5 — BIG. The long bottom row counted out: three groups of four berries, glowing one group at a time.
▷ 4 + 4 + 4 = 4 × 3 = 12
CAPTION: Three copies of 4. Quaxly picked 12 berries.
QUAXLY: Twelve! Three groups of four, all the same size.

〈 PAGE 3 — RUN THE PICTURE BACKWARDS 〉

PANEL 6 — BIG. Now only the long bar is known: twelve berries tipped into one long line, cut by two chalk marks into three equal groups. The short bar above it is an empty basket, one group long, still waiting.
▷ Quaxly has 12, and that's 3 copies of Fuecoco's pick.   12 ÷ 3 = 4
CAPTION: Same two bars. Knowing the LONG one, you share it into 3 equal parts to find the short one.
FUECOCO: Same two bars. Share the long one into 3 equal parts.

PANEL 7 — Lechonk, flat on its side in the grass, squints at the two rows and checks.
LECHONK: Three of Fuecoco's piles, easy. Seven wouldn't even make two! Nap time.

〈 PAGE 4 〉

PANEL 8 — Full. Sunset over the orchard. All five friends load the two hauls onto the cart, the long row and the short row side by side.
★ TIMES AS MANY ★
Draw two bars from the SAME left edge — a short one for one unit, a long one for the copies. Know one unit? Multiply. Know the long bar? Divide.
FUECOCO: Two bars, one starting line.
PAWMI (upside down in a basket): Times means copies!"""

STUDENT_INTRO = """Some word problems compare two amounts instead of adding them up. When someone has "3 times as many," they don't have 3 MORE — they have 3 whole copies of what the other one has. The trick is to draw TWO bars, one under the other, both starting at the very same left edge, so you can see the short one fitting into the long one exactly three times. Watch Fuecoco pick 4 berries and Quaxly pick 3 times as many at the orchard's long sorting bench. Then watch the friends run the very same picture backwards to find out how many Fuecoco had."""

PARENT_CONTENT = """## The big idea

This lesson is about COMPARISON — "times as many" — and it is the first place in the chapter where multiplication and division are two readings of a single picture rather than two separate skills.

**Fuecoco has 4 berries. Quaxly has 3 times as many. How many does Quaxly have?**

- Fuecoco's amount is **one unit**: 4 berries.
- "3 times as many" means Quaxly's amount is **3 copies of that unit**: 4 + 4 + 4, which is **4 × 3 = 12**.

Written **3 × 4** it still comes to 12, so don't spend any energy policing the order of the two numbers. What matters is that she can say which number is the size of one unit and which is the number of copies.

**Now the reverse. Quaxly has 12 berries, and that is 3 times as many as Fuecoco. How many does Fuecoco have?**

- The long bar is 12 and it is made of **3 equal units**, so one unit is **12 ÷ 3 = 4**.

Same story, same drawing, opposite operation. Which one she needs depends on one question only: *do we know the size of one unit, or do we know the whole long bar?*

## Why two aligned bars

The representation here is not one bar cut into parts — it is **two separate bars, one drawn directly beneath the other, both starting at the same left edge**. That alignment IS the concept. A short one-unit bar on top; a long bar underneath made of three units the same width. Flush left ends let the eye lay the short bar against the long one and see it fit exactly three times.

If the bars start at different places, or the three sections are drawn different widths, the picture stops meaning anything — it becomes decoration. It is worth being fussy about this and nothing else: same left edge, equal-width units.

Drawn this way, the picture does the deciding for her. If she knows the short bar, finding the long one is a multiplication. If she knows the long bar, finding the short one is a division. She does not have to remember a rule about the words "times as many" — she reads it off the paper.

## The classic mix-ups

- **"3 times as many" read as "3 more."** By far the most common: she writes 4 + 3 = 7. This is a language error, not an arithmetic one, and it is why Pawmi says it out loud in Panel 2 — so it gets named rather than quietly repeated.
- **Multiplying when the total was given.** Handed "Quaxly has 12, that's 3 times as many as Fuecoco," she does 12 × 3 = 36. The number got bigger when the answer had to be smaller. Ask: *"Is Fuecoco's pile the big one or the little one?"*
- **Comparing backwards.** She decides Fuecoco has 3 times as many as Quaxly. Reading the sentence with a finger on each bar fixes this faster than any explanation.
- **Answering about the wrong character.** She works out 4, correctly, but the question asked about Quaxly. Have her say the answer as a full sentence — *"Quaxly picked 12 berries"* — and the mismatch becomes obvious.
- **Ragged bars.** Units drawn wildly different sizes, or the second bar started somewhere in the middle. Then the picture confirms whatever she already believed.

## Questions that help more than hints

- *"Who has less? Draw that one first."* — the small amount is always the unit.
- *"How many copies of that little bar make the long bar?"*
- *"Do we know how big one unit is, or do we know the whole long one?"* — this single question chooses × or ÷.
- *"Where do your two bars start?"* — asked as curiosity, not correction.
- *"Does the long bar look about three times as long as the short one?"* — Lechonk's check, and a genuinely good one.

## Extend it

Ask a third question about the very same pair: **"How many MORE berries did Quaxly pick than Fuecoco?"** That's 12 - 4 = **8**, and it forces her to notice that "how many more" and "how many times as many" are different questions about one picture.

Then change the multiplier and run both directions: 4 berries with **5 times as many** gives 4 × 5 = **20**, and "20 is 5 times as many as ?" gives 20 ÷ 5 = **4**.

Finally, have her invent one at the kitchen table with real objects — spoons, blocks, socks — and pose it to you, including the picture. Building a comparison problem requires knowing which pile is the unit, which is the strongest evidence that the idea has landed.

## A note on the manga

Panel 4 spends an entire full-width frame doing nothing but lining the two bars up, before any arithmetic happens at all — that panel is the lesson. Panel 6 keeps the identical drawing and simply changes which bar is known, so the division does not arrive as a new topic. Fuecoco never corrects Pawmi's "seven" with a scold; it just points out that seven answers a different question."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L8 'Times as Many' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 8
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
