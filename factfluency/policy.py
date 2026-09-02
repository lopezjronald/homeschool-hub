"""What "fluent" means for a child of her age (HH-203).

WHY THIS IS A TABLE AND NOT A CONSTANT. The old bar was one number — 3000ms
plus 600 per extra digit — applied to every child. That is the automaticity
figure from the literature (Hasselbring 1988; Isaacs & Carroll 1999), and it is
right for a twelve-year-old: Kaylin clears it on 98% of her correct answers.
It was wrong for a nine-year-old. Violet played sixty-five rounds of one level
at 95% accuracy and never left it, because her recall of 2x4 lands at 4.7s and
a bar that does not know she is nine called that "not knowing it".

The whole stimulus-to-response chain runs slower in a younger child (Kail
1991: a seven-year-old at ~2.2x adult speed, a nine-year-old ~1.8x, a
twelve-year-old ~1.4x), and this clock also pays for reading the prompt and
finding the first key on a touch keypad — none of which the spoken-answer
benchmark included. XtraMath makes the same call: 3s is its "true fluency"
setting for older students and 6s is its default precisely because younger
children "are still building typing skills and fine motor control".

WHERE A BAR STOPS BEING A FLUENCY BAR. Above about 5 seconds a four-step skip
count ("2, 4, 6, 8") fits inside it, so the bar would be measuring accuracy
plus effort, not recall. The Monte Carlo on Violet's own 4-6 second answers
made this concrete: a skip-counter beats Level 1 in 0% of runs at 4000/1000
and in 100% of runs at 5000/1000. Band B is 4000 for that reason and no other.
Below Grade 3 the standards do not expect recall of these facts at all, so
Band A is honestly an accuracy bar.

The two anti-guesser controls — three separate rounds to master a form, and
the level gate — are NOT here. They do not vary by age, and every streak-2
variant simulated let a 60%-accurate guesser through Level 1.
"""

from collections import namedtuple

#: base_ms: a correct one-digit answer inside this many ms is recall.
#: per_digit_ms: added for each digit after the first, because the clock runs
#:   to her last keystroke and a second digit is a second deliberate tap.
#: new_facts_per_round: how many never-seen forms a round may introduce. A
#:   small set is the acquisition-rate finding; an older child who plainly knows
#:   a level should not need fifteen rounds to be shown it.
Policy = namedtuple("Policy", "base_ms per_digit_ms new_facts_per_round")

BANDS = [
    (("PREK", "K", "G01", "G02"), Policy(5000, 1000, 4)),
    (("G03", "G04"), Policy(4000, 1000, 4)),
    (("G05", "G06"), Policy(3500, 800, 6)),
    (("G07", "G08", "G09", "G10", "G11", "G12"), Policy(3000, 600, 8)),
]

#: A blank or unknown grade gets the CCSS grade for this content (3.OA.7 puts
#: "know from memory" at the end of Grade 3) — never the strictest band, so a
#: caller that has lost the grade cannot judge a nine-year-old by a
#: twelve-year-old's clock.
DEFAULT_POLICY = BANDS[1][1]


def policy_for(student):
    """The bar for this child. A pure function of her grade_level."""
    grade = (getattr(student, "grade_level", "") or "").strip().upper()
    for grades, policy in BANDS:
        if grade in grades:
            return policy
    return DEFAULT_POLICY


def threshold_for(answer, policy):
    """The fluency bar for an answer of this many digits under this policy."""
    digits = len(str(abs(int(answer))))
    return policy.base_ms + policy.per_digit_ms * (digits - 1)
