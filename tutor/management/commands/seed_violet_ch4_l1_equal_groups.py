"""Seed the Ch4 L1 "The Berry Orchard — Equal Groups and Arrays" manga (Pokemon Gen 9).

Harvest morning at the berry orchard, and Sprigatito has already dumped its whole basket into one messy heap.

Examples:
    python manage.py seed_violet_ch4_l1_equal_groups --curriculum 1
    python manage.py seed_violet_ch4_l1_equal_groups --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Berry Orchard — Equal Groups and Arrays"

STUDENT_CONTENT = """THE BERRY ORCHARD  ——  Equal Groups and Arrays
(a math manga · Chapter 4, Lesson 1: Looking Back at Multiplication)

〈 PAGE 1 〉

PANEL 1 — Wide. Dawn in the berry orchard. All five friends work along the bushes with woven baskets, picking the first berries of the morning. Mist, low sun, heavy red fruit.
CAPTION: Harvest morning. Pick fast, pile it up — and Fuecoco says it all gets SORTED, not dumped.
QUAXLY: Baskets ready! Nobody dump anything!

PANEL 2 — The picking is done, and Sprigatito has already tipped its whole basket into one messy heap. Pawmi is trying to count the pile one berry at a time and losing track, sparks flying.
CAPTION: Counting one at a time is slow — and it is very easy to lose your place.
PAWMI: One, two, three, four— wait, did I count that one already?
FUECOCO: Don't count them all. Make EQUAL groups.

〈 PAGE 2 — EQUAL GROUPS 〉

PANEL 3 — BIG. Four woven baskets in a neat row, each holding exactly three berries. Nothing left over on the ground.
▷ 4 baskets, 3 berries in each:  3 + 3 + 3 + 3 = 12
▷ Four groups OF three  →  4 × 3 = 12
CAPTION: When every group is the same size, multiplication is the fast way to add the same number again and again. Say it out loud: four groups of three.
SPRIGATITO: Four groups OF three! Not four and three!
QUAXLY: Twelve berries — and I never counted past three.

PANEL 4 — Sprigatito sneaks one extra berry into the third basket. Quaxly catches it mid-sneak. Fuecoco raises one calm claw.
CAPTION: 3 + 3 + 4 + 3 = 13 — a true addition, but NOT 4 × 3. Multiplication needs every group the same size.
QUAXLY: Four in that one! They aren't equal groups any more!
FUECOCO: Pop it back, and we can multiply again.

〈 PAGE 3 — THE SAME TWELVE, IN ROWS 〉

PANEL 5 — BIG. The twelve berries are tipped onto a flat wooden drying tray and pushed into a tidy rectangle: four rows across, three berries in every row.
▷ Same 12 berries, lined up:  4 rows of 3  →  4 × 3 = 12
CAPTION: A rectangle of rows and columns is called an ARRAY. It is the equal groups, standing still.
PAWMI: It's the same twelve! Just tidier!

PANEL 6 — BIG. Fuecoco turns the whole tray a quarter turn. Not one berry moves on the tray — but now there are three rows across with four berries in every row.
▷ Turn the tray:  3 rows of 4  →  3 × 4 = 12
▷ 4 × 3 = 12    and    3 × 4 = 12
CAPTION: The tray moved. The berries did not. Same total, read two ways.
SPRIGATITO: Wait— I didn't pick any more berries!
QUAXLY: Three rows of four. Still twelve.

〈 PAGE 4 〉

PANEL 7 — Lechonk, flat on its back in the grass under the bushes, delivers the punchline without getting up.
CAPTION: 4 + 4 + 4 = 12 as well. Three groups of four lands in exactly the same place.
LECHONK: Learn 4 × 3 and you get 3 × 4 free. Half the work.

PANEL 8 — Full. Golden morning light. All five friends carry the loaded drying trays back along the orchard path.
★ THE TWO WAYS TO SEE IT ★
Equal groups tell the STORY — 4 baskets of 3. The array shows it reads both ways — 4 × 3 = 12 and 3 × 4 = 12. And multiplying only works when every group is the same size.
FUECOCO: Groups of, then rows of. Same twelve.
PAWMI (staggering under a tray): Groups of! Rows of! TWELVE!"""

STUDENT_INTRO = """Harvest morning at the berry orchard, and Sprigatito has already dumped its whole basket into one messy heap. Counting berries one at a time takes forever — so the friends sort them into equal groups instead, and multiplication does the rest. You'll watch 4 baskets with 3 berries in each become 4 × 3 = 12. Then those same twelve berries line up on a drying tray as 4 rows of 3 — and here's the sneaky part, turn the tray a quarter turn and it reads as 3 rows of 4 instead. The total never changes, because nobody picked a single extra berry."""

PARENT_CONTENT = """## The big idea

Chapter 4 opens by going back to what multiplication actually *means* before any facts get drilled. Two pictures carry the whole lesson: **equal groups** and **the array**.

**Worked example — 4 × 3 = 12.**

**As equal groups:** four baskets with three berries in each. Written as repeated addition that is **3 + 3 + 3 + 3 = 12**, and written as multiplication it is **4 × 3 = 12** — read aloud as *"four groups of three"*.

**As an array:** tip those same twelve berries onto a tray and push them into a rectangle — four rows with three berries in each row, so **4 × 3 = 12** again. Now turn the tray a quarter turn without moving a single berry. The identical rectangle now reads as three rows with four berries in each row: **4 + 4 + 4 = 12**, which is **3 × 4 = 12**. Same twelve berries, two sentences: **4 × 3 = 3 × 4 = 12**. That is the commutative property, and the array is the proof — not a rule to be believed, a picture to be turned.

One note on notation. Dimensions Math reads **4 × 3** as *four groups of three*: the first number is how many groups, the second is how many in each. That order matters for the *story* (four baskets of three berries is a different picture from three baskets of four) but never for the *answer*. Keep the language "groups of" and this stays clear; drop it and children start believing the two are unrelated facts to memorise separately.

## Why these two pictures

**Equal groups** is where multiplication comes from — it is the only picture that carries the units. Four baskets of three berries: the answer, twelve, is berries, not baskets. Third graders who lose track of that end up multiplying numbers with no idea what they've produced.

**The array** is where multiplication becomes efficient. Rows and columns make the commutative property physically obvious, which almost halves the number of facts she has to learn (the only ones without a partner are the squares, like 3 × 3), and it is the same rectangle that will carry area in a later grade and the distributive property in Chapter 5. It is worth building properly now.

They earn their places together: the groups say what the problem *is*, the array says what she is *allowed to do* with it.

## The classic mix-ups

**Unequal groups.** She counts four containers, sees twelve things, and writes 4 × 3 — without checking that each container holds the same amount. In the manga Sprigatito sneaks a fourth berry into one basket: 3 + 3 + 4 + 3 = 13, which is a perfectly good addition and not a multiplication at all. Ask "are they equal?" every single time.

**Counting by ones anyway.** She'll arrive at 12 by touching each berry, which is correct and slow, and it hides whether she understood anything. Ask her to get the answer *without* touching every one.

**Reading the array wrong.** Counting rows as columns, or counting the berries along one edge twice. Have her trace one full row with a finger and say "one row of three" before counting how many rows there are.

**Believing 4 × 3 and 3 × 4 are different totals.** Very common, and the tray-turn fixes it in about ten seconds if she does the turning herself.

**"Times means add."** She sees 4 × 3 and writes 7. Usually a slip rather than a misconception, but say the words "four groups of three" aloud and it disappears.

## Questions that help more than hints

*"How many groups, and how many in each group?"* — the two questions that turn any picture into a multiplication sentence.

*"Are the groups equal? How do you know?"*

*"Twelve what?"* — forces the unit back into the answer.

*"Can you say that as an addition?"* — 3 + 3 + 3 + 3, which links the new operation to the one she already owns.

*"What happens if I turn the tray?"* — then wait. Don't tell her the total is unchanged; let her check and be surprised.

## Extend it

Hand her twelve small objects — beans, coins, LEGO bricks — and ask her to find **every** rectangle she can make. She should get 1 × 12, 2 × 6, 3 × 4, 4 × 3, 6 × 2 and 12 × 1: six arrays, which are really three rectangles each seen two ways. Ask which ones are "the same rectangle wearing a different name."

Then give her a number that *won't* cooperate, like 7, and let her discover that the only rectangles are 1 × 7 and 7 × 1. She has just met prime numbers without anyone using the word.

Around the house: egg cartons, muffin tins, window panes, floor tiles, a six-pack of drinks. Ask "how many rows, how many in each row?" and let her tell you the multiplication sentence before she counts.

## A note on the manga

Panels 3, 5 and 6 are the same twelve berries three times over — first in four baskets, then poured onto a tray as four rows of three, then that identical tray turned a quarter turn into three rows of four. Nothing is added or removed between those panels, and that is deliberate: the whole point of the commutative property is that *nothing happened*. If she can say out loud that no berries were picked between panel 5 and panel 6, she has the idea."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L1 'Equal Groups and Arrays' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 1
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
