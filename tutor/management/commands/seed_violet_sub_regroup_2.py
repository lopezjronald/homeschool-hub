"""Seed the Ch3 L3 "Subtraction with Regrouping - Part 2" manga (Pokemon Gen 9).

The hard case: subtracting from a number with zeros, where the place you want to
borrow from is empty and you have to go further along. Worked example
500 - 236 = 264 (no tens to open, so open a hundred first, then a ten).

The whole lesson hangs on one image — you can't borrow from an empty shelf, so
you go to the next full one and work back.

Examples:
    python manage.py seed_violet_sub_regroup_2 --curriculum 1
    python manage.py seed_violet_sub_regroup_2 --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Empty Shelf — Subtracting Across Zeros"

STUDENT_CONTENT = """THE EMPTY SHELF  ——  Subtracting Across Zeros
(a math manga · Chapter 3, Lesson 3: Subtraction with Regrouping - Part 2)

〈 PAGE 1 〉

PANEL 1 — Wide. The berry storehouse. Five big sealed crates stand along one wall. The two shelves beside them — the TENS shelf and the ONES shelf — are completely bare.
CAPTION: Five hundred berries in the storehouse. Nothing loose, nothing bundled.
QUAXLY (reading an order slip): Someone's ordered two hundred thirty-six!

PANEL 2 — Sprigatito looks at the bare ones shelf, then the bare tens shelf. Fuecoco watches.
SPRIGATITO: 500 take away 236. Ones first — I need 6…
SPRIGATITO (staring at nothing): …and the ones shelf is EMPTY.

PANEL 3 — Sprigatito turns hopefully to the tens shelf. It is also completely bare. Ears droop.
SPRIGATITO (dismayed): So I'll open a ten — but the TENS shelf is empty too!
FUECOCO (calm): Then keep walking. Go to the first shelf that ISN'T empty.

〈 PAGE 2 — OPEN A HUNDRED FIRST 〉

PANEL 4 — BIG. Fuecoco cracks the seal on ONE of the five big crates. Ten banded bundles spill out onto the tens shelf. Four sealed crates remain.
▷ No tens to open — so open a HUNDRED.
CAPTION: 1 hundred becomes 10 tens. Now: 4 hundreds, 10 tens, 0 ones.
FUECOCO: One hundred is ten tens. The tens shelf isn't empty any more.

PANEL 5 — BIG. Now Sprigatito unties ONE of those ten bundles; ten loose berries scatter onto the ones shelf. Nine bundles remain.
▷ Now open a TEN.
CAPTION: 1 ten becomes 10 ones. Now: 4 hundreds, 9 tens, 10 ones.
SPRIGATITO (relieved): Two trades — and now every shelf has something!

〈 PAGE 3 — NOW SUBTRACT 〉

PANEL 6 — BIG. The order goes out the door; what stays is 2 crates, 6 bundles, 4 loose berries.
▷ ONES: 10 - 6 = 4    TENS: 9 - 3 = 6    HUNDREDS: 4 - 2 = 2
CAPTION: Now it's easy.   500 - 236 = 264
QUAXLY (checking the slip): Two hundred sixty-four left. Perfect!

〈 PAGE 4 〉

PANEL 7 — Fuecoco sums it up; Sprigatito and Quaxly nod.
FUECOCO: An empty shelf can't lend you anything.
FUECOCO: Walk to the first shelf that has something — then trade back down, one step at a time.

PANEL 8 — Full. Evening in the tidy storehouse: two crates, six bundles, four loose berries all neatly in their places; the three friends resting.
★ ACROSS ZEROS ★
If the next place is 0, you can't borrow from it. Go to the next place that isn't 0, open THAT, and work your way back down. Hundred → ten → one.
SPRIGATITO (sleepy): Keep walking till a shelf isn't empty…   To be continued →"""

STUDENT_INTRO = (
    "Sometimes the place you want to borrow from is EMPTY. You can't open a ten if "
    "there are no tens! So you keep walking to the first place that isn't zero, open "
    "that one, and trade your way back down. Watch Sprigatito try to take 236 berries "
    "out of a storehouse holding 500 — with an empty ones shelf AND an empty tens "
    "shelf — and see how two trades fix it. Then try your own."
)

PARENT_CONTENT = """## The big idea

This is the same trade as Lesson 2, but the shelf she wants to borrow from is **empty**. You cannot open a ten when there are zero tens — so you go to the first place that *does* have something, open that, and work back down one step at a time.

- **500 - 236** → ones: need 6, have 0. Tens? Also 0.
- Open a **hundred** → 4 hundreds, **10 tens**, 0 ones.
- Now open a **ten** → 4 hundreds, **9 tens**, **10 ones**.
- Subtract: **10 - 6 = 4**, **9 - 3 = 6**, **4 - 2 = 2** → **264**.

Two trades, in order. The stumbling block is almost never the arithmetic — it's believing you're allowed to go two doors down.

## Why this one is genuinely harder

Everything else in Chapter 3 is a single local move. This is the first problem where a child has to *hold a plan across two steps* — go get a hundred, break it, come back, break again. Expect it to take longer than the lessons on either side of it, and expect fluency to lag understanding by a while. That's normal here.

## The classic mix-ups

1. **Borrowing from the zero anyway** — crossing out the 0 and writing 9 with no idea where the 9 came from. It gives the right answer often enough to survive, and then collapses on 5,004 - 236. If she can't say *where the 9 came from*, she's pattern-matching.
2. **Only trading once** — turning 500 into 4 hundreds, 10 tens, 0 ones and then subtracting 0 - 6 anyway.
3. **Losing a hundred** — forgetting the hundreds column dropped from 5 to 4.

## Help her hands-on

Base-ten blocks make this one concrete in a way nothing else does:

1. Build **500** with five hundred-flats. Nothing else on the table.
2. Ask for 6 ones. Let her discover there's nothing to take.
3. Trade **one flat for ten ten-sticks**. Say: *"Now the tens aren't empty."*
4. Trade **one stick for ten ones**. Now subtract.

Two physical trades, in that order. Doing it with her hands two or three times beats any amount of explaining.

## Extend it

Once 500 - 236 is comfortable, try **1,000 - 458** (three trades) and a number with a zero in the middle like **604 - 137**. Ask her to say the plan out loud *before* touching the pencil: *"I need a ten. There aren't any. So first I need a hundred."*

## A note on the manga

The storehouse and its shelves are doing real work: an empty shelf is a picture of a zero, and *walking to the next full shelf* is exactly the algorithm. The two trades get their own big panels, in order, because the order is the thing that gets lost."""


class Command(MangaSeedCommand):
    help = "Seed the Ch3 L3 'The Empty Shelf' subtracting-across-zeros manga (idempotent)."

    CHAPTER = 3
    LESSON_NUMBER = 3
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
