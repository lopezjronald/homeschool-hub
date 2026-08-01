"""Seed the Ch3 L4 "Estimating Sums and Differences - Part 1" manga (Pokemon Gen 9).

Rounding to estimate a SUM, and — the part that matters — using the estimate to
check whether an exact answer is reasonable. Worked example 296 + 405: round to
300 + 400 = 700, exact answer 701, so 701 is believable and 1,101 would not be.

Estimating is the only lesson in this chapter that is about *judgement* rather
than procedure, so the manga makes the estimate catch a wrong answer rather than
just produce a rough one. An estimate nobody checks anything against is a chore.

Examples:
    python manage.py seed_violet_estimating_1 --curriculum 1
    python manage.py seed_violet_estimating_1 --for-user lopezjronald
"""

from ._manga_seed import MangaSeedCommand

TITLE = "Pawmi's Good Guess — Estimating Sums"

STUDENT_CONTENT = """PAWMI'S GOOD GUESS  ——  Estimating Sums
(a math manga · Chapter 3, Lesson 4: Estimating Sums and Differences - Part 1)

〈 PAGE 1 〉

PANEL 1 — Wide. A bustling Paldea festival. Two huge jars of candy sit on a prize table. Pawmi the little electric mouse and Lechonk the plump piglet stare up at them.
CAPTION: FESTIVAL DAY! Guess the candy, win the candy.
PAWMI (buzzing with excitement): One jar has 296… the other has 405!

PANEL 2 — Pawmi scribbles frantically on a slate, sparks flying, tail whipping.
PAWMI (panicking): Two hundred ninety-six plus four hundred five… carry the… um…
LECHONK (unbothered, chewing): You don't need the exact answer yet. Just get CLOSE.

PANEL 3 — Lechonk points a trotter at the first jar, calm as anything.
LECHONK: 296 is nearly 300. Round it UP.
LECHONK: 405 is just past 400. Round it DOWN.

〈 PAGE 2 — ROUND, THEN ADD 〉

PANEL 4 — BIG. The two jars shimmer into two clean, simple jars — one labelled-by-shape as three full hundred-scoops, the other four.
▷ 296 → 300     405 → 400
CAPTION: Round each number to the nearest hundred. Now the numbers are easy.
PAWMI (eyes wide): Ohhh — those are easy numbers!

PANEL 5 — BIG. Pawmi adds the two easy numbers in one happy zap.
▷ 300 + 400 = 700
CAPTION: About seven hundred candies altogether.
PAWMI (thrilled): About seven hundred! I didn't even need my slate!

〈 PAGE 3 — THE ESTIMATE DOES A JOB 〉

PANEL 6 — BIG. A festival worker holds up a card reading a wildly wrong total. Pawmi's ears shoot up — something's off.
▷ The sign says: 1,101
CAPTION: But wait — the estimate says about 700. That answer is way too big!
PAWMI (indignant): That can't be right! We know it's about 700!

PANEL 7 — The worker rechecks and flips the card: 701. Pawmi and Lechonk cheer.
▷ The real answer: 296 + 405 = 701
LECHONK: 701 is right next to 700. That one's believable.

〈 PAGE 4 〉

PANEL 8 — Full. Pawmi and Lechonk share an enormous prize jar of candy under festival lanterns.
★ ESTIMATING RULE ★
Round each number to the nearest hundred, then add. The estimate won't be exact — it isn't supposed to be. Its job is to tell you whether your exact answer is BELIEVABLE.
PAWMI (mouth full): Round first, check after!   To be continued →"""

STUDENT_INTRO = (
    "An estimate is a quick, close-enough answer — and its real job is to CHECK your "
    "work. Round each number to the nearest hundred, add the easy numbers, and you "
    "know roughly what the answer should be. Then if your exact answer is nowhere "
    "near it, you know something went wrong. Watch Pawmi guess the candy jars "
    "(296 + 405) and catch a badly wrong total. Then try your own!"
)

PARENT_CONTENT = """## The big idea

Rounding to estimate: replace each number with the nearest easy number, then add.

- **296 + 405** → **300 + 400 = 700**. Exact: **701**.

The rounding itself she can probably already do. What's new — and what this lesson is really for — is **what an estimate is for**. An estimate is a *reasonableness check*: 701 sits right next to 700, so it's believable; 1,101 doesn't, so something went wrong.

## Why this matters more than it looks

A child who estimates only when the instructions say "estimate" has learned a chore. A child who estimates *before* computing has a way to catch her own mistakes — which is the single most valuable habit in arithmetic, and it's the reason this lesson sits here, right after two lessons of error-prone regrouping.

Make the estimate come **first**, then the exact answer, then the comparison. In that order it's a tool. In the other order it's homework.

## How to round to the nearest hundred

1. Look at the **tens** digit.
2. 5 or more → round **up** to the next hundred. Less than 5 → round **down**.
3. **296** → tens is 9 → up to **300**. **405** → tens is 0 → down to **400**.

> Ask: *"Which hundred is it closer to?"* — that question does the whole job, and it survives when the rule is forgotten.

## The classic mix-ups

- **Rounding to the wrong place** — turning 296 into 290 (nearest ten) when the problem wants hundreds.
- **Rounding the answer instead of the numbers** — adding exactly, then rounding 701 to 700. That's not an estimate; it can't check anything, because it's derived from the answer it's meant to check.
- **Expecting the estimate to be right** — being troubled that 700 ≠ 701. Say plainly: it's *supposed* to be a little off.

## Try this at home

Estimating is genuinely useful, so use it where it's genuinely useful: at the shop, add up the basket to the nearest dollar before you reach the till. Ask *"about how much?"* and then check against the receipt. She'll find the habit sticks far better than a worksheet does.

Another good game: give her an addition and a **wrong** answer, and ask only *"could that be right?"* — no computing allowed. That's the skill.

## A note on the manga

Pawmi and Lechonk take over from the berry-stand trio; the festival is a place where "about how many?" is a genuinely sensible question. The estimate is deliberately shown **catching a wrong answer** (1,101) rather than merely producing a rough one, because that's the job it does."""


class Command(MangaSeedCommand):
    help = "Seed the Ch3 L4 'Pawmi's Good Guess' estimating-sums manga (idempotent)."

    CHAPTER = 3
    LESSON_NUMBER = 4
    TITLE = TITLE
    STUDENT_INTRO = STUDENT_INTRO
    STUDENT_CONTENT = STUDENT_CONTENT
    PARENT_CONTENT = PARENT_CONTENT
