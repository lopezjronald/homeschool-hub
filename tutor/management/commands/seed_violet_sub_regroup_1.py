"""Seed the Ch3 L2 "Subtraction with Regrouping - Part 1" manga (Pokemon Gen 9).

The deliberate mirror of Ch3 L1: L1 bundles ten ones INTO a ten, this one unties
a ten back into ten ones. Same Paldea berry field, same cast plus Quaxly, so the
two moves read as one idea running both directions — the single most useful
thing a child can notice about regrouping.

Worked example 342 - 128 = 214 (one regroup: 2 - 8 won't go, so open a ten ->
12 - 8 = 4).

Examples:
    python manage.py seed_violet_sub_regroup_1 --curriculum 1
    python manage.py seed_violet_sub_regroup_1 --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "Quaxly Unties a Bundle — Subtracting with Regrouping"

STUDENT_CONTENT = """QUAXLY UNTIES A BUNDLE  ——  Subtracting with Regrouping
(a math manga · Chapter 3, Lesson 2: Subtraction with Regrouping - Part 1)

〈 PAGE 1 〉

PANEL 1 — Wide. The Paldea berry stand at morning. Sprigatito and Fuecoco behind a counter stacked with berries; Quaxly the little blue duckling waddles up with a basket.
CAPTION: Market day! The berry stand is open.
QUAXLY (bright): I'd like one hundred twenty-eight berries, please!

PANEL 2 — Sprigatito looks at their whole stock: 3 big hundred-baskets, 4 ten-bundles, 2 loose berries.
SPRIGATITO: We have three hundred forty-two. So we'll have…
SPRIGATITO (thinking): 342 take away 128. Start with the ONES!

PANEL 3 — Sprigatito stares at just 2 loose berries, ears drooping. Quaxly waits politely.
SPRIGATITO (worried): I only have 2 loose berries… and Quaxly needs 8!
FUECOCO: Then don't stay stuck. Go next door.

〈 PAGE 2 — OPEN A TEN 〉

PANEL 4 — BIG. Fuecoco lifts ONE ten-bundle off the stack and holds it over the loose-berry tray, ribbon half untied.
▷ ONES:  2 - 8  won't go — borrow from the TENS
CAPTION: 2 ones isn't enough. Open ONE ten and pour it into the ones.
FUECOCO: One ten is just ten ones wearing a ribbon. Untie it!

PANEL 5 — BIG. The ribbon is off: ten berries tumble into the ones tray, joining the 2 already there. The tens stack is now one shorter.
▷ 1 ten -> 10 ones.   2 + 10 = 12 ones.   Tens: 4 becomes 3.
CAPTION: Now there are 12 ones. 12 - 8 = 4.
QUAXLY (delighted): Twelve! Now there's plenty!

〈 PAGE 3 — FINISH THE TENS AND HUNDREDS 〉

PANEL 6 — BIG. Quaxly's basket fills as bundles and baskets move across the counter; what stays behind is 2 hundreds, 1 ten, 4 ones.
▷ TENS: 3 - 2 = 1     HUNDREDS: 3 - 1 = 2
CAPTION: Take the rest away.   342 - 128 = 214
SPRIGATITO (proud): Two hundred fourteen berries left!

〈 PAGE 4 〉

PANEL 7 — Fuecoco explains; Sprigatito and Quaxly listen, side by side.
FUECOCO: Adding, you BUNDLE ten and carry it up.
FUECOCO: Subtracting, you UNTIE a ten and pour it down. Same trade, other way!

PANEL 8 — Full. The three friends share berries on the counter at midday, the stall cheerful and busy.
★ REGROUPING RULE (SUBTRACTION) ★
If a place is too small to take from, open ONE of the next-bigger place. Ten comes down into that column — then subtract.
QUAXLY (happy, mouth full): Untie a ten, pour it down… Quaxly can regroup!   To be continued →"""

STUDENT_INTRO = (
    "Last time you bundled ten ones into a ten. Now you go the other way. When you "
    "subtract and a place is too small to take from, you OPEN one of the next-bigger "
    "place: untie a ten and pour ten ones into the ones column, then subtract. Watch "
    "Sprigatito try to give Quaxly 8 berries with only 2 loose ones — and see what "
    "happens when Fuecoco unties a bundle (342 - 128). Then try your own!"
)

PARENT_CONTENT = """## The big idea

Subtraction regrouping ("borrowing") is **the same trade as carrying, run backwards**. In addition you bundle ten ones into one ten. Here you *untie* one ten back into ten ones so the column has enough to take from.

- **342 - 128** → ones: **2 - 8** won't go → open one ten → **12 - 8 = 4**, and the tens drop from 4 to **3**.
- tens: **3 - 2 = 1**; hundreds: **3 - 1 = 2** → **214**.

If she met Ch3 L1 first, say the connection out loud — *"bundling and untying are the same trade"*. Children who see them as two unrelated rules are the ones who later can't tell which to use.

## How to subtract with regrouping

1. Line the numbers up by place.
2. Look at the **ones**. Enough to take from? Subtract. Not enough? **Open one ten** — the ones gain 10, the tens lose 1.
3. Move to the **tens**, then the **hundreds**, opening again whenever a place is short.

> Ask: *"Is there enough here to take from? If not, where do I go to get more?"*

## The classic mix-up

The big one is **subtracting the smaller digit from the larger regardless of position**: seeing `2 - 8` and writing **6**. It looks like arithmetic and it is very persistent, because it gives an answer that *feels* fine. The fix isn't "remember to borrow" — it's making `2 - 8` feel genuinely impossible with objects in hand. Two berries cannot become eight berries; you have to go get more.

Watch also for forgetting to **reduce the place she borrowed from** (taking the ten but still writing 4 in the tens).

## Help her hands-on

Use banded bundles of ten (craft sticks, straws, base-ten blocks):

1. Build **342**: 3 hundred-flats, 4 ten-sticks, 2 ones.
2. Ask her to take away 8 ones. Let her get stuck — that stuck moment is the lesson.
3. Let her **physically untie a ten-bundle** and drop the ten ones in. Count: 12.
4. Now take 8. Then the tens, then the hundreds.

Say it every time: *"Not enough — open a ten."*

## Extend it

Ask her to **predict which columns will need regrouping before she starts**, then check. Give her a subtraction with *no* regrouping needed mixed among ones that do, so the decision stays live rather than automatic. Estimating first ("about 340 - 130 ≈ 210") gives the exact answer something to be checked against.

## A note on the manga

Quaxly, the Gen 9 water starter, joins Sprigatito and Fuecoco from Lesson 1 — same Paldea, same berry field, so the untying reads as the visible reverse of the bundling she already watched. The stuck moment (2 loose berries, 8 needed) is given a whole panel on purpose: that pause is where the idea actually lands."""


class Command(MangaSeedCommand):
    help = "Seed the Ch3 L2 'Quaxly Unties a Bundle' subtraction-with-regrouping manga (idempotent)."

    CHAPTER = 3
    LESSON_NUMBER = 2
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
