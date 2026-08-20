"""Seed the Ch4 L7 "The Berry Wagon — Word Problems with Bar Models" manga (Pokemon Gen 9).

The orchard wagon leaves at sunrise, and six baskets have to be filled with five berries each.

Examples:
    python manage.py seed_violet_ch4_l7_bar_model_word_problems --curriculum 1
    python manage.py seed_violet_ch4_l7_bar_model_word_problems --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Berry Wagon — Word Problems with Bar Models"

STUDENT_CONTENT = """THE BERRY WAGON  ——  Word Problems with Bar Models
(a math manga · Chapter 4, Lesson 7: Word Problems, Part 1)

〈 PAGE 1 〉

PANEL 1 — Wide. Dawn in the berry orchard. A wooden wagon waits on the path; six empty baskets sit in a neat row. All five friends are ready to pick.
CAPTION: Harvest morning. Six baskets to fill — and exactly five berries fit in each one.
QUAXLY: Six baskets. Five berries in each. How many berries is that?

PANEL 2 — Normal. Pawmi is already counting loose berries one at a time, sparks flying, losing track. Fuecoco lowers a calm claw.
CAPTION: Counting a pile one berry at a time works — right up until it doesn't.
PAWMI: One, two, three— wait, did I count that one already?!
FUECOCO: Don't count the pile. Draw the bar — then label one unit.

〈 PAGE 2 — KNOW THE UNIT, FIND THE WHOLE 〉

PANEL 3 — BIG. Fuecoco draws a single rectangle in the orchard dirt and sets exactly five berries inside it. Sprigatito leans in to look.
CAPTION: One unit stands for one basket. 1 unit = 5 berries. Say what one unit is worth before you compute anything.
FUECOCO: One unit is one basket. Five berries live inside it.

PANEL 4 — BIG. That same rectangle, repeated six times in a row, makes one long bar. Every unit holds five berries. Quaxly points along it; Sprigatito bats at the far end; Fuecoco finishes the last section.
CAPTION: 6 units of 5  →  6 × 5 = 30 berries.  (5, 10, 15, 20, 25, 30.)  Unit known, whole unknown — so multiply.
QUAXLY: Thirty berries! Six equal units, five in every one.
SPRIGATITO: Same unit, six times over!

〈 PAGE 3 — KNOW THE WHOLE, FIND THE UNIT 〉

PANEL 5 — Normal. Sprigatito pounces at a butterfly, clips the row of full baskets, and all thirty berries roll into one enormous heap. Quaxly panics; Lechonk does not.
CAPTION: All 30 berries — back in one pile.
SPRIGATITO: Oops. Oops oops oops.
LECHONK: One giant hill of berries.

PANEL 6 — BIG. The same long bar of six equal sections, but now it is the pile that is known. Berries flow from the heap and settle evenly, five into every section.
CAPTION: Whole known, unit unknown — so divide.  30 ÷ 6 = 5 berries in each basket.
FUECOCO: Now we know the whole and we hunt for the unit.
PAWMI: Five each! Again!

PANEL 7 — Normal. Lechonk, flat on its back, checks the answer by running it back the other way while Pawmi and Quaxly lean in.
CAPTION: Check it backwards: 6 × 5 = 30. ✓
LECHONK: Five, ten, fifteen, twenty, twenty-five, thirty. Checks out.

〈 PAGE 4 〉

PANEL 8 — Full. Sunrise on the orchard road. Six full baskets are loaded on the wagon and all five friends wave it off.
CAPTION: ★ THE UNIT RULE ★   Draw the bar, cut it into EQUAL units, label one unit first.   Know the unit → multiply: 6 × 5 = 30.   Know the whole → divide: 30 ÷ 6 = 5.
FUECOCO: Find the unit. Everything else follows.
PAWMI: Draw it, label it, THEN count!"""

STUDENT_INTRO = """The orchard wagon leaves at sunrise, and six baskets have to be filled with five berries each. You could count berries one at a time until your brain melts — or you could draw a bar, cut it into equal UNITS, and say what one unit is worth. Once the unit is known, multiplying is easy: six units of five is thirty. Then a certain grass kitten knocks all thirty berries into one pile, and the same drawing has to run backwards: thirty berries shared into six baskets is five each. Same bar, same story, two different unknowns."""

PARENT_CONTENT = """## The big idea

Chapter 4 finally puts multiplication and division inside stories, and the tool for reading those stories is the bar model from Chapter 2 — a bar cut into equal **units**.

**Six baskets. Five berries in each basket. How many berries altogether?**

- Draw one long bar and cut it into **6 equal units** — one unit per basket.
- Label **one unit = 5 berries**. This is the step to insist on; everything else is bookkeeping.
- The unit is known and the whole is not, so multiply: **6 × 5 = 30 berries** (5, 10, 15, 20, 25, 30).

Then the story reverses. All thirty berries end up in one pile and have to go back into the six baskets.

**30 berries shared equally into 6 baskets. How many in each?**

- Draw the **same** bar: the whole is **30**, still cut into **6 equal units**.
- This time the whole is known and the unit is not, so divide: **30 ÷ 6 = 5 berries per basket**.
- Check by running it backwards: **6 × 5 = 30** ✓.

The two problems are the same picture with the question mark in a different place. That is the entire lesson, and it is worth saying to her in exactly those words.

## Why the bar, and why the unit gets labelled first

A word problem asks a child to do two very different things at once — understand a situation, and choose an operation. The bar splits that in half. Drawing comes first and involves no arithmetic at all; the choice of × or ÷ comes second and, once the bar is drawn, is usually just *looking* rather than deciding.

Labelling one unit before computing is what makes the drawing worth anything. An unlabelled bar is a decoration. A bar where she can point at one section and say "that's one basket, and it holds five berries" is a machine: multiply along it to get the whole, divide the whole by the number of units to get back to one unit.

This is also the honest reason equal groups get a *bar* rather than six little circles. Six circles of five dots work fine at these numbers and collapse completely once the numbers get big. The bar scales, and it is the same drawing she will use for fractions and ratio later. We are paying now for something she gets back for years.

## The classic mix-ups

- **Swapping the unit and the number of units.** She draws 5 units of 6 instead of 6 units of 5. Both give 30 here, which is exactly why it slides past unnoticed — and why it will bite in Part 2 when the numbers differ. Ask her what ONE section stands for; the answer must be "one basket", not "six".
- **Answering with the wrong noun.** For the division she says "six" — the number of baskets — when the question asked how many *berries* in each. Requiring a unit label on the answer ("5 berries") fixes most of this.
- **Unequal sections.** The bar gets cut into six wildly different-sized chunks. If they aren't equal, the drawing is telling a lie about the story. Redraw rather than discuss.
- **Adding instead of multiplying.** 6 + 5 = 11. Almost always a sign she never drew anything and grabbed the two available numbers.
- **Counting the pile one berry at a time.** Not wrong, just defeated — and it is the habit this whole chapter exists to replace. Pawmi does it in Panel 2 so she can watch it fail.
- **Hearing "shared into 6 baskets" as "take away 6."** Taking 6 away once gives 24, which answers nothing. Sharing means dealing the pile out into six equal parts until the pile is gone, and the bar makes that visible in a way the words don't.

## Questions that help more than hints

- *"What does ONE section of your bar stand for?"* — the single most useful question in this lesson.
- *"How many equal sections are there?"*
- *"Do we know the unit, or do we know the whole?"* — this is the question that picks the operation. Let her answer it, don't answer it for her.
- *"Are your sections the same size?"*
- *"Does your answer count berries, or baskets?"*
- *"Can you go back the other way to check?"* — 30 ÷ 6 = 5 gets checked with 6 × 5 = 30.

## Extend it

Ask a **third** question off the same picture: *"30 berries, and 5 fit in each basket — how many baskets?"* That's **30 ÷ 5 = 6**, and it is genuinely harder, because now the unit is known and the *number of units* is the mystery. Same thirty berries, same bar, third unknown.

Then change the unit and rerun both directions: five berries per basket becomes four, so **6 × 4 = 24**, and sharing back gives **24 ÷ 6 = 4**.

Best of all, hand her a drawn bar with nothing written on it — six equal units, a few berries sketched in one of them — and ask her to invent the story that goes with it. Making the word problem requires knowing what the unit means, which is a stiffer test than solving one.

Real objects beat paper for a day or two: egg cartons, coins, LEGO bricks, socks out of the dryer. Fill equal groups, then dump them out and share them back, and say the two sentences out loud every time.

## A note on the manga

The whole cast returns from Chapter 3, in a new orchard setting. Panels 3 and 4 deliberately spend two full-width panels on one drawing — the single labelled unit, then the same unit six times — because the pause between them is where the idea lives. Panel 5 wrecks the baskets on purpose: the division isn't a second exercise tacked on, it's the same thirty berries needing to go home again."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L7 'Word Problems with Bar Models' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 7
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
