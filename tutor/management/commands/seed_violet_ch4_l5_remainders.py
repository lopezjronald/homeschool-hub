"""Seed the Ch4 L5 "The Leftover Cup — Division with Remainders" manga (Pokemon Gen 9).

Sometimes a number just will not share out evenly, and that is completely okay.

Examples:
    python manage.py seed_violet_ch4_l5_remainders --curriculum 1
    python manage.py seed_violet_ch4_l5_remainders --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Leftover Cup — Division with Remainders"

STUDENT_CONTENT = """THE LEFTOVER CUP  ——  Division with Remainders
(a math manga · Chapter 4, Lesson 5: Division with Remainders)

〈 PAGE 1 — THE LAST CART 〉

PANEL 1 — Wide. The orchard packing shed at the end of the day. Berries heaped on a long counter, a stack of empty round baskets, and one small tin cup.
CAPTION: 13 berries came in on the last cart. Every basket holds exactly 4.
QUAXLY: Last cart of the day! Every basket holds exactly four berries.
SPRIGATITO: Then let's pack them fast!

PANEL 2 — Normal. Sprigatito drops berries into baskets four at a time while Pawmi wrings its paws.
CAPTION: Packing means making groups that are all the SAME size — exactly 4 in every basket.
PAWMI: It won't come out even! Berries are going to be LEFT OVER!
FUECOCO: Good. Left over is allowed.

〈 PAGE 2 — WHAT'S LEFT HAS A NAME 〉

PANEL 3 — Full. Three baskets in a row, four berries in each, and one lonely berry sitting by itself on the bare counter.
CAPTION: 4 + 4 + 4 = 12, and 1 berry is still on the counter.     13 ÷ 4 = 3 R 1  —  three full baskets, remainder one.
FUECOCO: Three full baskets… and one berry with nowhere to go.
QUAXLY: Three baskets AND one left over — both parts are the answer!

PANEL 4 — Normal. Fuecoco taps the lonely berry with a claw. Pawmi scoops it into the little tin cup, delighted.
CAPTION: The leftover has a name: the REMAINDER. We write it with an R —  13 ÷ 4 = 3 R 1.
FUECOCO: The leftover has a name. It's the REMAINDER.
PAWMI: I'll keep it in my leftover cup!

〈 PAGE 3 — PAWMI'S SUSPICIOUS CUP 〉

PANEL 5 — Normal. The next cart brings 13 more berries and Pawmi packs them alone. It has stopped after only two baskets, and its tin cup is heaped and overflowing.
CAPTION: Another cart, another 13 berries. Pawmi's try: 2 baskets = 8 berries, so 13 − 8 = 5 berries in the cup. Is 2 R 5 right?
PAWMI: I stopped at two baskets! Look how full my leftover cup is!
QUAXLY: Hmm. That cup looks… suspicious.

PANEL 6 — Full. The five leftover berries are tipped out above an empty basket with four berry-sized hollows. Four drop in. One is still hovering.
CAPTION: Check the leftover against the basket: 5 is NOT smaller than 4 — so one more whole basket can still be filled. 2 R 5 isn't finished.
FUECOCO: Hold the leftovers against an empty basket. Do they still fill one?
SPRIGATITO: They do! So we're not done!

〈 PAGE 4 — THE RULE 〉

PANEL 7 — Normal. Three full baskets now, and exactly one berry rattling in the tin cup. Lechonk, half-reclining, delivers the verdict.
CAPTION: Fixed: 3 baskets is 12 berries, and 13 − 12 = 1. Remainder 1 — and 1 IS smaller than 4. ✓
LECHONK: If the leftover fills a basket, it isn't a leftover. It's a basket.
PAWMI: One berry left. A REAL leftover!

PANEL 8 — Full. Sunset over the orchard. The cart rolls away loaded with baskets; Pawmi rides on top holding its cup with one berry in it.
CAPTION: ★ THE REMAINDER RULE ★   Fill every whole group you can. What's still left is the remainder — and it must always be SMALLER than the group size. If it isn't, make one more group.
SPRIGATITO: Fill every basket you can — then check what's left!
PAWMI: Smaller than the basket! Every time!   To be continued →"""

STUDENT_INTRO = """Sometimes a number just will not share out evenly, and that is completely okay. When you have filled every group you can, whatever is still sitting there is called the remainder. In this story the friends pack 13 berries into baskets that hold 4 each — and one stubborn berry refuses to fit. You will learn how to write an answer with an R in it, and the one rule that catches almost every mistake: the leftover must always be smaller than the group."""

PARENT_CONTENT = """## The big idea

Up to now every division in this chapter has come out clean. This lesson breaks that on purpose: some numbers simply refuse to share out evenly, and the piece that's left over has a name — the **remainder**.

The worked example: 13 berries, packed into baskets that hold 4 each.

Fill baskets one at a time — **4 + 4 + 4 = 12** — and 1 berry is still sitting on the counter. So **13 ÷ 4 = 3 R 1**: three full baskets, remainder one.

Notice that the answer has **two parts**, and both matter. The 3 counts baskets. The 1 counts berries. Kids who can say what each number counts almost never mangle the answer later.

And here is the rule the whole lesson turns on: **the remainder must always be smaller than the divisor** — here, smaller than the basket size. If what's left is as big as the group size, or bigger, you can still make another whole group, which means you stopped too early.

The manga stages exactly that error on the next cartload of 13. Pawmi stops after only two baskets: **2 × 4 = 8**, and **13 − 8 = 5**, so it claims **2 R 5**. Then the friends tip the five leftover berries over an empty basket — four drop in, one is left hovering. Five was never a legal remainder. Fixed: **3 R 1**, and 1 is smaller than 4. ✓

## Why we check the leftover against the group

Third graders learn "remainder" as a rule they're told, and rules they're told get misremembered. So the story makes the rule something you can *see*: a physical pile of leftovers held up against a physical empty basket.

That check is self-correcting. She doesn't have to remember whether 5 is allowed after dividing by 4 — she just tries to fill one more basket. If it fills, she wasn't finished. If it doesn't, she is. The comparison replaces the memory.

It also plants the seed for long division later, where the "is the remainder smaller than the divisor?" check is the thing that tells you whether your digit was too small.

## The classic mix-ups

**A remainder that's too big.** The number one error, and the reason for the rule: she stops sharing before she has to and reports something like 13 ÷ 4 = 2 R 5. Fix: hold the leftovers against one more empty group.

**Gluing the two numbers together.** 3 R 1 gets read, written, or remembered as "31." The R is not decoration — it separates two different kinds of things (groups and leftovers).

**Checking the remainder against the wrong number.** She compares the leftover to 13 (the whole) or to 3 (the number of groups) instead of to 4 (the basket size). Ask her every time: *"Smaller than WHAT?"*

**Thinking a remainder means she got it wrong.** Some kids will break a berry in half or quietly drop the extra to force it even. Reassure her early: a leftover is a legitimate answer, not a failure.

**Losing the units in a word problem.** "3 R 1" is fine on paper, but the answer to the question is "3 full baskets and 1 berry left." Make her say the sentence.

## Questions that help more than hints

*"How many whole baskets can you fill?"* — starts her on the groups instead of the arithmetic.

*"Is what's left smaller than one basket?"* — the entire lesson in one question. Ask it every single time.

*"Can you make one more whole group with what's left?"* — the same check, phrased so she can just try it.

*"What does the 3 count? What does the 1 count?"* — catches the "31" mistake before it happens.

*"How many MORE berries would you need to fill another basket?"* — 3 more, because 4 − 1 = 3; a lovely second question that quietly previews sharing a whole.

*"Multiply back: how many berries are in the baskets? Where did the rest go?"* — **3 × 4 = 12**, plus 1 makes 13. That's her own answer key.

## Extend it

**Try the whole family.** Divide 12, 13, 14, 15, 16 by 4 and line the answers up: 3 R 0, 3 R 1, 3 R 2, 3 R 3, then 4 R 0. Ask her what she notices — the remainders climb 0, 1, 2, 3 and then reset. She has just discovered that dividing by 4 can only ever leave 0, 1, 2 or 3.

**Change the basket.** Same 13 berries into baskets of 5: **13 ÷ 5 = 2 R 3**. Into baskets of 3: **13 ÷ 3 = 4 R 1**. Bigger baskets, fewer of them.

**Catch the fake.** Hand her wrong answers and let her be the inspector: is 17 ÷ 5 = 2 R 7 legal? (No — 7 is bigger than 5, so it's really **3 R 2**.) Kids love being the one who catches the mistake.

**Real leftovers.** Egg cartons, card hands, socks pairing up, seats in a van for a crowd of cousins. Then ask the grown-up version: 13 cousins need vans, and each van seats 4 — is the answer 3 vans? (No. **13 ÷ 4 = 3 R 1**, and that 1 leftover cousin still needs a seat, so it takes 4 vans. Remainders sometimes push the answer *up*, and that's a genuinely fun thing for her to argue about.)

## A note on the manga

The berry orchard's packing shed gives the leftovers somewhere to physically live — Pawmi's little tin cup. When the cup gets suspiciously full in panel 5, the picture itself is telling her something's wrong before any arithmetic does. If she remembers one image from this lesson, let it be five berries being tipped over a basket that only takes four."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L5 'Division with Remainders' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 5
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
