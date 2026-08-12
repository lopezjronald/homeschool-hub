"""Seed the Ch4 L6 "The Two-Seat Ferry — Odd and Even Numbers" manga (Pokemon Gen 9).

Every leaf boat on the orchard pond carries exactly TWO berries — two seats, two berries.

Examples:
    python manage.py seed_violet_ch4_l6_odd_even --curriculum 1
    python manage.py seed_violet_ch4_l6_odd_even --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "The Two-Seat Ferry — Odd and Even Numbers"

STUDENT_CONTENT = """THE TWO-SEAT FERRY  ——  Odd and Even Numbers
(a math manga · Chapter 4, Lesson 6: Odd and Even Numbers)
(The art never shows words or numbers — all the math lives in the CAPTIONS.)

〈 PAGE 1 〉

PANEL 1 — Wide. Harvest morning at the orchard pond. A little wooden dock, crates of round red berries, and a row of tiny leaf boats bobbing in the water — each boat built with exactly two seats. All five friends are there.
CAPTION: Harvest morning at the orchard pond. Every leaf boat carries exactly TWO berries — two seats, no more, no less.
QUAXLY: Two seats. Two berries. That is the whole rule!

PANEL 2 — Sprigatito tips a basket and eight berries roll into a line along the dock. Pawmi already looks worried.
CAPTION: Eight berries, and every boat holds two. Will everybody find a buddy?
SPRIGATITO: Eight berries picked! Does everybody get a buddy?
PAWMI: What if one is left ALL ALONE?!

PANEL 3 — BIG. The eight berries buddy up two-by-two: four leaf boats sail off, each carrying two berries side by side. The dock behind them is completely empty — count the boats, count the pairs.
CAPTION: Every berry found a buddy. 8 ÷ 2 = 4 with 0 left over — so 8 is EVEN.
QUAXLY: Four boats, all full. Nobody left on the dock — that's EVEN!

〈 PAGE 2 — ONE LEFT OVER 〉

PANEL 4 — BIG. The next basket holds seven berries. Three boats sail away with two berries each — and one small berry sits alone at the end of the dock, waiting for a partner who never comes.
CAPTION: Seven won't pair up all the way. 7 ÷ 2 = 3 with 1 left over — so 7 is ODD.
PAWMI: Three boats… and one berry with nobody. That's ODD!

PANEL 5 — Fuecoco settles beside the lonely berry, calm and kind, and curls a claw around it. Sprigatito leans in to listen.
FUECOCO: Odd isn't wrong. It just means one is left over after every pair.
SPRIGATITO: One more than a pair!

〈 PAGE 3 — TWO EQUAL GROUPS, AND A SHORTCUT 〉

PANEL 6 — BIG. On the far shore, two baskets share eight berries fairly: four and four, the heaps exactly level. Beside them, two more baskets try the same with seven: three in one, four in the other — one heap sits visibly lower.
CAPTION: EVEN splits into TWO EQUAL groups:  8 = 4 + 4.   Odd can't:  7 = 3 + 4, and 3 is not 4.
FUECOCO: Even splits into two FAIR halves. Odd leaves them uneven.

PANEL 7 — A long line of loaded boats crosses the pond. Quaxly stands tall, wing flung out, struck by a discovery. Lechonk is half-asleep on a berry crate.
CAPTION: Count the evens: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20 — the last digit is always 0, 2, 4, 6 or 8. So 34 is even (34 ÷ 2 = 17, nothing left) and 25 is odd (25 ÷ 2 = 12, with 1 left).
QUAXLY: I see it! Every even number ends in 0, 2, 4, 6 or 8!
LECHONK: So don't pair 34 berries — peek at the last one!

〈 PAGE 4 〉

PANEL 8 — Full. Sunset over the pond. Every boat is home, the crates are stacked, and the five friends sit together on the dock — the last little berry tucked safely in Fuecoco's claw.
CAPTION: ★ THE BUDDY RULE ★   Pair them two-by-two. Nobody left over = EVEN. One left with no buddy = ODD. Even splits into two equal groups; odd always has one over — and the last digit will tell you.   To be continued →
SPRIGATITO: Buddy up! Nobody left — even. One left over — odd."""

STUDENT_INTRO = """Every leaf boat on the orchard pond carries exactly TWO berries — two seats, two berries. So when the friends buddy up their harvest, one question decides everything: does everybody get a buddy? If the berries pair up perfectly with nobody left on the dock, the number is EVEN. If one lonely berry is left over with no buddy, the number is ODD. Ride along with Sprigatito, Fuecoco, Quaxly, Pawmi and Lechonk as 8 berries sail away in 4 full boats — and 7 berries leave somebody waiting. At the very end, Quaxly spots a sneaky shortcut hiding in the last digit."""

PARENT_CONTENT = """## The big idea

A number is **even** if it can be paired up completely — two by two, with nothing left over. It is **odd** if pairing leaves exactly one behind. That is the whole definition, and it is worth insisting on before any shortcut appears.

**8 berries, two to a boat:** 4 full boats and nothing on the dock. In division language from Lesson 5, **8 ÷ 2 = 4 remainder 0** — even.

**7 berries, two to a boat:** 3 full boats and 1 berry with no buddy. **7 ÷ 2 = 3 remainder 1** — odd.

The same idea said the other way round: **even means it splits into two equal groups**. 8 splits as **4 + 4** (equal, so even). 7 splits as **3 + 4** — it *did* split into two groups, but they are not equal, so 7 is odd.

Dividing by 2 can only ever leave a remainder of 0 or 1. That is why every whole number is either even or odd, with nothing in between — a nice thing to notice out loud.

The digit shortcut arrives at the very end of the lesson, as a **discovery, not a definition**: counting the evens gives 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, and the last digit is always 0, 2, 4, 6 or 8. It works on numbers too big to pair by hand: 34 ends in 4, so it is even (**34 ÷ 2 = 17**, nothing left over); 25 ends in 5, so it is odd (**25 ÷ 2 = 12 remainder 1**).

## Why pairing, and why the shortcut comes last

Pairing is the meaning; the last digit is only a symptom. A child taught the digit rule first can label numbers correctly for a year and still not know what she is labelling — and it shows up later, when she meets "can these 26 chairs be arranged in two equal rows?" or halving, or parity in a proof-shaped problem, and has no picture to reason from.

Two-seat boats are used instead of loose counters on purpose: the pairing is *built into the object*. A boat is either full or it is embarrassingly half-empty, and a half-empty boat is exactly what "remainder 1" looks like. She cannot fudge it.

This lesson also sits directly on Lesson 5. Odd and even is not a new topic so much as the **÷ 2 case of remainders**: remainder 0 means even, remainder 1 means odd. Saying that sentence connects two lessons for free.

## The classic mix-ups

**Reading the wrong digit.** She checks the first digit and calls 43 even because it starts with 4, or scans for any even digit anywhere in the number. Only the **ones** digit decides it — because every ten pairs up perfectly on its own, so the tens and hundreds can never leave anyone over.

**"It split into two groups, so it's even."** 7 into a pile of 3 and a pile of 4 is two groups, and she may accept it. The groups must be **equal**. Ask her to hand out the berries one-for-me-one-for-you rather than dumping them into two piles.

**Confusing "even" with "equal" in general.** 9 makes three equal groups of 3, and a child will offer that as proof that 9 is even. Even is specifically about **two** groups — or about pairs, which is the same thing.

**Thinking 0 is odd, or "neither."** 0 is even: 0 ÷ 2 = 0 with nothing left over, and 0 = 0 + 0. It also has to be, for the count-by-2s pattern to keep working past 20.

**Hearing "odd" as "wrong" or "weird."** Third graders take the word personally, and some decide odd numbers are broken or cannot be divided at all. Fuecoco's line in Panel 5 is doing real work: odd just means one over a pair.

**Miscounting rather than mis-reasoning.** With 13 or 17 objects she may lose track mid-pairing and get the wrong answer with perfectly good logic. Have her physically move each pair away as she makes it, the way the boats sail off.

## Questions that help more than hints

- *"Can everybody get a buddy?"* — the whole lesson in five words.
- *"If just the two of us shared these, would we get the same amount?"*
- *"How many are left over when you put them in twos?"* — connects straight back to Lesson 5.
- *"You said 26 is even. Which digit did you look at? Why that one?"* — after the shortcut appears, make her justify it.
- *"Is 0 even or odd? How could we check?"*
- *"Is there any number that's neither?"* — a lovely one to leave hanging.

## Extend it

Pair up the real world: shoes, socks, egg cartons, hands at the dinner table. Ask whether the number of people at dinner tonight is odd or even before anyone sits down.

Take a walk and read house numbers — one side of the street odd, the other even. Ask her to predict the next number she will see on each side.

Then run a small investigation with counters, letting her find the rules herself rather than being told: **even + even** (4 + 6 = 10, even), **odd + odd** (3 + 5 = 8, even — the two lonely ones buddy up with each other!), **even + odd** (4 + 5 = 9, odd). The odd + odd result surprises everyone, and pairing explains it perfectly.

If she wants a challenge: is 100 even? Is 101? Is 1,000,000? She should be able to answer instantly and then say *why* the last digit is enough.

## A note on the manga

Same five friends, new corner of the orchard — the pond crossing, so the chapter does not feel like nine identical berry-counting days. The two-seat boat is the pairing model made physical, and Panel 4 deliberately leaves one small berry alone on the dock for a full beat before anyone says the word "odd." Quaxly gets the digit discovery in Panel 7 only after the pairing has been shown twice, and Lechonk closes it with the reason anyone would want a shortcut at all: nobody wants to pair up thirty-four berries by hand."""


class Command(MangaSeedCommand):
    help = "Seed the Ch4 L6 'Odd and Even Numbers' manga (idempotent)."

    CHAPTER = 4
    LESSON_NUMBER = 6
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
