"""Seed the Ch4 L4 "The Last Six Berries — Multiplying and Dividing with 0 and 1" manga (Pokemon Gen 9).

Some numbers have secret powers.

Examples:
    python manage.py seed_violet_ch4_l4_zero_and_one --curriculum 1
    python manage.py seed_violet_ch4_l4_zero_and_one --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Last Six Berries — Multiplying and Dividing with 0 and 1"

STUDENT_CONTENT = """THE LAST SIX BERRIES  ——  Multiplying and Dividing with 0 and 1
(a math manga · Chapter 4, Lesson 4: Multiplying and Dividing with 0 and 1)

〈 PAGE 1 〉

PANEL 1 — Wide. Closing time at the Sunset Row orchard market. The whole crew packs down the berry stall under a golden sky; stacked baskets, one low crate of berries left.
CAPTION: Closing time at the orchard market — and almost every basket is empty.
QUAXLY: Last stall of the day, everyone. Pack it down!
PAWMI: Wait — my basket still has berries in it!

PANEL 2 — Pawmi holds up ONE basket of berries with both paws, cheeks sparking with worry. Fuecoco leans in, calm, beside a row of tiny empty cups.
PAWMI: It's just ONE basket. One isn't even a real times problem… is it?
FUECOCO: One group is still a group. Watch what one does.

〈 PAGE 2 — THE ONES 〉

PANEL 3 — BIG. On the counter: on the left, ONE basket holding seven berries. On the right, SEVEN tiny cups, each holding exactly ONE berry.
CAPTION: One group of 7 → 1 × 7 = 7.   Seven groups of 1 → 7 × 1 = 7.   Same berries, different picture.
FUECOCO: One group of seven, or seven groups of one — both make seven.
PAWMI: They look SO different but it's the same pile!

PANEL 4 — Sprigatito has flipped a row of FIVE baskets upside down and peers under the last one in comic dismay. Lechonk lies flopped nearby, unbothered, chewing.
SPRIGATITO: I flipped every basket. Empty, empty, empty, empty, empty!
LECHONK: Five whole baskets of nothing. We are rich in air.

〈 PAGE 3 — THE ZEROS 〉

PANEL 5 — BIG. Left: FIVE baskets in a row, every one plainly empty. Right: a bare stretch of counter with no baskets on it at all.
CAPTION: Five groups of 0 → 5 × 0 = 0.   No groups at all → 0 × 7 = 0.   Nothing, however you stack it.
SPRIGATITO: Five baskets of nothing is… still nothing!
QUAXLY: And no baskets at all? Nothing again. Zero wins twice.

〈 PAGE 4 — SHARING THE LAST SIX 〉

PANEL 6 — Wide. Quaxly tips the last SIX berries into ONE wide basket; beside it, the same six berries laid out in SIX tiny cups, one berry per cup. Fuecoco looks on, pleased.
CAPTION: All 6 into 1 basket → 6 ÷ 1 = 6.   6 berries into 6 cups → 6 ÷ 6 = 1 each.
QUAXLY: Lechonk ate one! Six left — and this basket gets every single one.
FUECOCO: Six berries, six cups: exactly one each.

〈 PAGE 5 — THE QUESTION WITH NO ANSWER 〉

PANEL 7 — BIG. Left: an upturned EMPTY crate above six tiny cups, every cup empty. Right: a line of empty baskets marching off into the distance forever, while a crate of six berries sits untouched. Pawmi frantic; Fuecoco calm.
CAPTION: 0 ÷ 6 = 0 — nothing shared out is nothing each.   But 6 ÷ 0? Empty baskets never hold 6 berries — there is NO answer.
PAWMI: A hundred empty baskets and the six berries are STILL sitting there!
FUECOCO: Groups of nothing never add up. That's why 6 ÷ 0 has no answer.

〈 PAGE 6 〉

PANEL 8 — Full. Sunset over Sunset Row: lanterns lit, stall packed down, all five sitting on the grass sharing the last small basket.
★ THE 0 AND 1 RULES ★
× 1 keeps a number the same. × 0 makes it 0. ÷ 1 keeps it the same. A number ÷ itself is 1. 0 ÷ a number is 0. But you can never divide BY 0 — no pile of empty baskets ever fills up, so there is no answer.
PAWMI: One keeps it the same. Zero empties it. And nobody divides by zero!
LECHONK: Six berries, five friends… let's not do THAT one tonight.   To be continued →"""

STUDENT_INTRO = """Some numbers have secret powers. Multiplying or dividing by 1 leaves a number exactly as it was, and multiplying by 0 wipes it out completely — and you can SEE why, if you look at real baskets of berries instead of just trying to remember rules. In this lesson the Paldea crew closes down the orchard market with one full basket, five empty ones, and a few last berries to share out. You'll find out why 7 x 1 and 1 x 7 both make 7, why 6 berries in 6 cups is 1 each, and why nothing shared among six friends is nothing each. And you'll meet the one question in all of math that has no answer at all: what happens when you try to divide by zero."""

PARENT_CONTENT = """## The big idea

This lesson looks like a list of exceptions to memorize. It isn't. Every one of these rules falls straight out of reading "equal groups" carefully, and Violet should *derive* them from a picture rather than store them as trivia.

Work it with real objects — berries, beans, buttons — in baskets or cups. Here is the exact sequence the manga walks:

- **1 × 7 = 7** — ONE group with seven in it. There is nothing to combine, so it is just seven.
- **7 × 1 = 7** — SEVEN groups with one in each. Seven ones is seven. Same total, completely different picture.
- **5 × 0 = 0** — five baskets, each holding nothing. Five nothings is nothing.
- **0 × 7 = 0** — no baskets at all. There is nothing to count.
- **6 ÷ 1 = 6** — six berries into one basket: that basket gets all six.
- **6 ÷ 6 = 1** — six berries shared among six cups: one berry each.
- **0 ÷ 6 = 0** — an empty crate shared among six cups: every cup gets nothing.
- **6 ÷ 0** — has no answer at all.

That last one deserves an honest explanation, not a shrug. Division asks *"how many groups of this size do I need to use up all six?"* If each group holds zero, you can line up ten empty baskets, or a hundred, or a million, and the six berries are still sitting in the crate. No number of empty baskets ever holds six berries — so there is no answer to give. Not infinity, not zero: there simply isn't one, which is why we say a number cannot be divided by zero.

(For completeness: **0 ÷ 0** is undefined too, for a related reason — every answer would "work." That is also why "a number divided by itself is 1" is stated for every number *except* zero. Neither point needs to come up in third grade; the flat rule "you can never divide BY zero" covers it.)

## Why baskets and cups do the work

These rules are exactly where children stop reasoning and start guessing, because 0 and 1 give no interesting arithmetic to hang on to. There is nothing to count on fingers, so the answer feels arbitrary — and an arbitrary answer is one a child will happily invent.

A drawn group fixes that. "Five empty baskets" is a picture with an obvious answer; **5 × 0** is not. The moment she can flip a basket over and see nothing in it, the rule stops being a fact she was told and becomes something she checked.

The picture also keeps the two *directions* apart. **1 × 7** and **7 × 1** give the same product but are different stories, and Singapore method wants her to hold both: number of groups first, size of group second. That distinction is exactly what she will need later in this chapter, when the groups stop coming out even.

## The classic mix-ups

**"Times zero leaves it alone."** She has spent two years learning that adding 0 changes nothing, and she carries the habit across — so she writes **6 × 0 = 6**, which is wrong. The fix is a picture, not a correction: hand her six empty cups and ask how many berries are on the table. Zero is the "does nothing" number for *adding*; 1 is the "does nothing" number for *multiplying*.

**Mixing up 0 ÷ 6 and 6 ÷ 0.** On the page these look nearly identical, so they get the same answer. Make her say each one out loud as a story: "zero berries shared among six friends" (everyone gets nothing — fine, that's 0) versus "six berries put into groups of zero" (that never finishes — no answer). Reading it aloud separates them instantly.

**"6 ÷ 6 = 0."** She hears "they cancel out" or "they disappear" and lands on zero. Six berries and six cups on the table ends this in about four seconds.

**"6 ÷ 1 = 1."** Pure pattern-matching on the 1 in the problem. Ask her to actually pour six berries into one basket and then count what's in it.

**Answering 6 ÷ 0 with 0 or 6.** Third graders hate leaving a blank, so they produce *something*. It's worth saying plainly: "This one is special — mathematicians agree there is no answer, and the right thing to write is that it can't be done." Being allowed to say "no answer" is a genuinely new move for her.

## Questions that help more than hints

*"Say it as a story — how many groups, and how many in each group?"* This single question sorts out almost every error in this lesson.

*"Draw it. What does a group of zero look like?"* An empty basket is drawable; a zero is not.

*"If you keep putting out empty baskets, when will the crate finally be empty?"* Let her chase this for a few seconds. The frustration IS the lesson.

*"Which number here is the number of groups, and which is the size of a group?"* Use it whenever she reverses 0 ÷ 6 and 6 ÷ 0.

*"Would that answer still make sense if I handed you the real berries?"* The all-purpose sanity check — Lechonk's job in the manga.

## Extend it

Give her a mixed stack of ten cards — **8 × 1**, **8 × 0**, **8 ÷ 1**, **8 ÷ 8**, **0 ÷ 8**, **8 ÷ 0**, and a few ordinary facts like **4 × 3** — and have her sort them into "same number," "zero," and "no answer" piles *before* writing any answers. Sorting first forces the reasoning; the arithmetic then takes seconds.

Then flip the roles: you give the answer and she writes a berry story that produces it. "Make me a story where the answer is 0 each." "Now make me one that can't be answered at all." Inventing the impossible one is the real proof she understands it.

## A note on the manga

The orchard market is closing, which is why almost everything on the counter is empty — the setting does the teaching. The numbers stay tiny on purpose (seven, five, six) so that not one ounce of attention goes to computing. Pawmi's basket starts with seven berries and Lechonk quietly eats one, which is why only six are left to share — if Violet notices the change, that is good reading, not an error. Lechonk's last line is a wink at what comes next: six berries shared among five friends does not come out even, and remainders are on the way."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L4 'Multiplying and Dividing with 0 and 1' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 4
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
