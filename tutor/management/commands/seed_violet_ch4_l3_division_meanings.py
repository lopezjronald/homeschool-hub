"""Seed the Ch4 L3 "The Berry Picnic — Two Ways to Divide" manga (Pokemon Gen 9).

Division asks two different questions, and they sound almost the same until you draw them.

Examples:
    python manage.py seed_violet_ch4_l3_division_meanings --curriculum 1
    python manage.py seed_violet_ch4_l3_division_meanings --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Berry Picnic — Two Ways to Divide"

STUDENT_CONTENT = """THE BERRY PICNIC  ——  Two Ways to Divide
(a math manga · Chapter 4, Lesson 3: Looking Back at Division)

〈 PAGE 1 〉

PANEL 1 — Wide. A picnic blanket at the edge of the berry orchard. A shallow wooden tray holding twelve berries sits in the middle; all five friends are flopped around it after a morning of picking.
CAPTION: Twelve berries. One tray. Nobody can agree on how to split them.
QUAXLY: Picking is finished. Now — how do we divide them?

PANEL 2 — Sprigatito and Quaxly both grab Pawmi at once, each pulling it a different way. Pawmi's sparks fly everywhere.
QUAXLY: Share them onto 3 plates — how many on EACH?
SPRIGATITO: No! Baskets of 3 — how many BASKETS?

PANEL 3 — Fuecoco calmly sets out three empty plates and starts dealing berries around, one at a time, like cards.
CAPTION: Dealing one at a time keeps every plate equal. Equal groups — that is the rule division never breaks.
FUECOCO: Nobody argue — we'll draw BOTH. One for you, one for you, one for you...

〈 PAGE 2 — MEANING ONE: SHARING 〉

PANEL 4 — BIG. Three plates on the blanket, four berries on each. The tray is empty. Fuecoco is letting go of the very last berry.
CAPTION: SHARING — 12 berries shared equally onto 3 plates: how many on EACH?   12 ÷ 3 = 4.   Four berries each. We knew the number of GROUPS; we were hunting the SIZE of each.
QUAXLY: Four each. Perfectly fair.

〈 PAGE 3 — MEANING TWO: GROUPING 〉

PANEL 5 — BIG. The same 12 berries again, this time scooped into little baskets — three berries in every basket, four baskets in a row.
CAPTION: GROUPING — the same 12 berries put into baskets of 3: how many BASKETS?   12 ÷ 3 = 4.   Four baskets. This time we knew the SIZE of each group; we were hunting the number of GROUPS.
SPRIGATITO: Four baskets! Same berries — but now the four counts BASKETS.

PANEL 6 — Fuecoco holds up a plate in one claw and a basket in the other. Pawmi's eyes go enormous.
CAPTION: Both pictures are 12 ÷ 3 = 4. Sharing answers how many in EACH group. Grouping answers how many GROUPS.
FUECOCO: Same berries. Same equation. Two different questions.
PAWMI: One says EACH, one says GROUPS!

〈 PAGE 4 — THE FAMILY 〉

PANEL 7 — BIG. All twelve berries laid out neatly on the tray in a tidy rectangle: three rows of four.
CAPTION: 3 rows of 4 = 12, so 3 × 4 = 12 — and that hands you 12 ÷ 3 = 4 AND 12 ÷ 4 = 3. One picture, one fact family.
QUAXLY: Learn one fact and you get four!

〈 PAGE 5 〉

PANEL 8 — Full. Sunset over the orchard. Lechonk, without standing up, nudges the tray a quarter turn — the three rows of four become four rows of three — and everybody leans in to eat.
CAPTION: ★ DIVISION RULE ★   Ask WHICH question first: how many in each group, or how many groups? And turning the tray shows 4 × 3 = 12 too — every division fact has a multiplication fact holding its hand.
LECHONK: Turn the tray — four rows of three. Still twelve. I didn't even get up.
PAWMI: Four each! Four baskets! Four everything!

★ END OF LESSON 3 ★"""

STUDENT_INTRO = """Division asks two different questions, and they sound almost the same until you draw them. If you SHARE 12 berries equally onto 3 plates, you are asking "how many on EACH?" If you put those same 12 berries into baskets of 3, you are asking "how many BASKETS?" Both are 12 divided by 3, and both answers are 4 — but they count different things. Come to the picnic at the edge of the orchard and watch the friends argue about it, then discover that one tray of berries hides a whole family of facts: 3 x 4 = 12, so 12 / 3 = 4 and 12 / 4 = 3."""

PARENT_CONTENT = """## The big idea

Division means two different things, and Dimensions Math deliberately makes a lesson out of it because the notation hides the difference. **12 ÷ 3 = 4** is the same sentence either way, but the 4 is not the same 4.

**Sharing (partitive): 12 berries shared equally onto 3 plates — how many on EACH?** You know the number of GROUPS (3) and you are hunting for the SIZE of each group. Deal them out one at a time and every plate ends with **4 berries**. **12 ÷ 3 = 4.** (Three plates, three friends, three boxes — same structure; the manga uses plates so that nobody has to wonder why the other two friends are being left out.)

**Grouping (quotative): 12 berries put into baskets of 3 — how many BASKETS?** Now you know the SIZE of each group (3) and you are hunting for the NUMBER of groups. Scoop out threes until the tray is empty and you have made **4 baskets**. **12 ÷ 3 = 4.**

Same numbers, same equation, same answer — but the first 4 counts berries and the second 4 counts baskets. That is the whole lesson.

Then the other half: **division and multiplication are one fact, not two.** Lay the 12 berries out as **3 rows of 4**. That picture says **3 × 4 = 12** and **4 × 3 = 12** and **12 ÷ 3 = 4** and **12 ÷ 4 = 3** all at once. Four facts, one arrangement. If she can recall 3 × 4 = 12, she never has to "work out" 12 ÷ 4 — she already knows it.

## Why plates and baskets, and then an array

The two meanings need two *different* pictures or they collapse into each other. Plates being dealt round-robin is unmistakably sharing; baskets being filled to a fixed size is unmistakably grouping. Doing them back to back with the identical twelve berries is what makes the point land: nothing changed except the question.

The array (the tidy rectangle) then arrives as the reconciler. It is the one picture that holds both meanings at the same time — read it by rows and you get one division fact, read it by columns and you get the other — which is exactly why arrays are the backbone of this chapter and of the multiplication facts she will memorize next.

## The classic mix-ups

**Answering with the wrong unit.** She says "4" for the basket question meaning 4 berries, or "4" for the sharing question meaning 4 baskets. Because the number is right, this slips past easily. Insist on a labeled answer — *4 berries each*, *4 baskets* — every single time.

**Assuming the second number is always the number of groups.** Most children meet sharing first and quietly decide that in 12 ÷ 3, the 3 must be the plates. Then a grouping problem gets solved as a sharing problem, arrives at the right answer anyway, and the misunderstanding survives to bite her when the numbers stop being friendly.

**Writing the numbers in the order the story said them.** "Three plates share twelve berries" becomes 3 ÷ 12. Division is not commutative, and this is the moment to say so out loud: 12 ÷ 3 and 3 ÷ 12 are not the same, unlike 3 × 4 and 4 × 3, which are. The concrete version she can see: you cannot hand 3 berries out to 12 friends and give everyone a whole berry.

**Sharing unequally.** She deals out four, then three, then five, and calls it done. Division always means EQUAL groups; if the last plate has extra, the sharing is not finished. (Leftovers get a proper name — remainders — later; for now the answer to "is that fair?" is no.)

**Treating 12 ÷ 3 and 12 ÷ 4 as unrelated problems** to be worked from scratch, rather than as two readings of the same rectangle.

## Questions that help more than hints

*"Are we sharing into a known number of groups, or making groups of a fixed size?"* — this single question is the lesson. Ask it before any arithmetic.

*"What does your 4 count — berries or baskets?"*

*"Can you draw it? Plates or baskets?"* — the drawing decides the meaning faster than any explanation you could give.

*"If I tell you 3 × 4 = 12, which two division facts do you get for free?"*

*"Would 3 ÷ 12 make sense here? Why not?"* — a good one for building the instinct that the whole goes first.

## Extend it

Give her the same twelve berries (or blocks, or pennies) and ask both questions with different numbers: share onto 2 plates → 6 each; make groups of 6 → 2 groups; share onto 4 plates → 3 each; make groups of 4 → 3 groups. Say the answers with their units out loud each time.

Then hand her a number — 20 — and have HER write you one sharing story and one grouping story for **20 ÷ 5 = 4**. Writing them is a much stronger test than solving them, because she has to decide which quantity is the group size before she can start.

Finally, a fact-family drill that takes thirty seconds: lay out an array of counters, and have her call out all four facts before you sweep it away. Do it with 2 × 6, 3 × 5, 4 × 5. She will start noticing that the square arrays (like 4 × 4) only give two facts, which is a genuinely delightful thing for a nine-year-old to discover on her own.

## A note on the manga

Panels 4 and 5 are the same twelve berries photographed twice, so to speak — the visual repetition is doing the teaching, and it is worth pausing between them and asking her what actually changed. Panel 7 gives the array its own full panel because it is the bridge to everything in the rest of the chapter, and Lechonk's quarter-turn in panel 8 is the commutative property arriving as a punchline rather than a rule."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L3 'Two Ways to Divide' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 3
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
