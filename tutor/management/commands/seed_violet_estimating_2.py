"""Seed the Ch3 L5 "Estimating Sums and Differences - Part 2" manga (Pokemon Gen 9).

Estimating a DIFFERENCE, plus the genuinely new idea in Part 2: you get to CHOOSE
the rounding place, and the choice changes how useful the estimate is. Worked
example 812 - 389: nearest hundred gives 800 - 400 = 400; nearest ten gives
810 - 390 = 420; exact is 423.

The point isn't that one is "right" — it's that a rougher round is faster and a
finer round is closer, and picking is part of the skill.

Examples:
    python manage.py seed_violet_estimating_2 --curriculum 1
    python manage.py seed_violet_estimating_2 --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "How Close Is Close Enough? — Estimating Differences"

STUDENT_CONTENT = """HOW CLOSE IS CLOSE ENOUGH?  ——  Estimating Differences
(a math manga · Chapter 3, Lesson 5: Estimating Sums and Differences - Part 2)

〈 PAGE 1 〉

PANEL 1 — Wide. The morning after the festival. A tall stack of 812 flyers on a table; a much smaller pile of 389 already handed out.
CAPTION: The morning after the festival. Time to tidy up.
LECHONK: We started with 812 flyers. We handed out 389.

PANEL 2 — Pawmi looks at the leftover stack, whiskers twitching.
PAWMI: So how many are LEFT? Do I have to count them all?
LECHONK: Only if you need the exact number. Do you?

PANEL 3 — Pawmi thinks about it, one paw on its chin.
PAWMI: I just need to know if there's enough for tomorrow…
LECHONK: Then estimate. Round, and subtract.

〈 PAGE 2 — THE QUICK ROUND 〉

PANEL 4 — BIG. Two clean simple stacks: eight big hundred-blocks and four big hundred-blocks.
▷ Nearest HUNDRED:  812 → 800     389 → 400
CAPTION: 800 - 400 = 400. About four hundred left.
PAWMI (satisfied): About 400! That's plenty for tomorrow!

PANEL 5 — Lechonk tilts its head, considering something.
LECHONK: That was fast. But we rounded 389 all the way up to 400 — that's 11 away.
LECHONK: If you want CLOSER, round smaller.

〈 PAGE 3 — THE CLOSER ROUND 〉

PANEL 6 — BIG. The stacks resolve into finer detail — tens instead of hundreds.
▷ Nearest TEN:  812 → 810     389 → 390
CAPTION: 810 - 390 = 420. Closer!
PAWMI (impressed): Four hundred twenty! That took longer, but it's nearer.

PANEL 7 — They count the real stack together. The true number appears.
▷ The exact answer: 812 - 389 = 423
LECHONK: 400 was close. 420 was closer. 423 is the truth.
LECHONK: Round rough when you want fast. Round fine when you want near.

〈 PAGE 4 〉

PANEL 8 — Full. Pawmi and Lechonk sit happily on the tidy stack of leftover flyers in the afternoon sun.
★ CHOOSING YOUR ROUNDING ★
Rounding to hundreds is fastest. Rounding to tens is closer. Neither is "wrong" — pick the one that answers YOUR question. And a rounder estimate still catches a badly wrong answer.
PAWMI (content): Fast, or near. My choice!   To be continued →"""

STUDENT_INTRO = (
    "You can estimate a difference the same way you estimate a sum — round, then "
    "subtract. But here's the new part: YOU choose what to round to. Rounding to "
    "hundreds is fastest; rounding to tens is closer. Neither one is wrong — you pick "
    "the one that answers your question. Watch Pawmi work out how many flyers are "
    "left (812 - 389) two different ways, and see which one it actually needed."
)

PARENT_CONTENT = """## The big idea

Estimating a difference works exactly like estimating a sum: round, then subtract.

- **812 - 389** → nearest **hundred**: **800 - 400 = 400**
- → nearest **ten**: **810 - 390 = 420**
- Exact: **423**

The new idea in Part 2 is that **the rounding place is a choice**, and the choice is a trade: rounding to hundreds is faster and rougher, rounding to tens is slower and nearer. Neither is the "right answer". You pick based on what you're using the estimate *for*.

That's a genuinely different kind of thinking from everything else in this chapter — the first time the question is *"what's good enough?"* rather than *"what's correct?"*. Some children find that unsettling. It helps to make the purpose explicit before rounding: *"What do you need to know? Whether there's roughly enough, or exactly how many?"*

## Why 389 → 400 costs accuracy

Worth naming out loud: 389 is 11 away from 400, so rounding it up throws the estimate off by about that much. When a number sits near the middle between two hundreds, a hundreds-estimate drifts. That's the concrete reason a tens-estimate is nearer — not a rule, a consequence.

## The classic mix-ups

- **Expecting the two rounding errors to cancel.** They cancel when both numbers move the *same* way and add up when they move opposite ways. Here 812 rounds down (−12) and 389 rounds up (+11) — opposite ways — so both pushes shrink the difference and the errors add: 400 undershoots 423 by 23. (In Lesson 4 they happened to move opposite ways too, +4 and −5, and for a *sum* that's the cancelling case — which is why 700 sat right next to 701.)
- **Thinking the closer estimate is the "real" one.** Both are estimates. 420 isn't correct either.
- **Estimating after computing** — same trap as Part 1, and it still can't check anything.

## Try this at home

Give her a purpose first, then ask which rounding fits:

- *"Do we have roughly enough juice boxes for the party?"* → hundreds is plenty.
- *"How much change should I get back?"* → you'd want tens, or the exact figure.

Then a good challenge: hand her a subtraction and ask for an estimate that is **within 50** of the true answer, and let her decide how finely to round to get there. That puts the choice in her hands, which is the whole lesson.

## A note on the manga

Pawmi and Lechonk return from Lesson 4, the morning after their festival. Doing the same subtraction *twice*, at two roundings, is the structure of the lesson — the second pass isn't a correction of the first, it's a different tool, and the manga is careful never to call 400 wrong."""


class Command(MangaSeedCommand):
    help = "Seed the Ch3 L5 'How Close Is Close Enough?' estimating-differences manga (idempotent)."

    CHAPTER = 3
    LESSON_NUMBER = 5
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
