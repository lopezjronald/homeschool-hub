"""Saxon Pre-Algebra Lesson 91 — Calculus and the Trinity; Area and Volume
Conversions.

Reviews Lessons 1, 25, 38 and 90. Two halves that have nothing to do with each
other, so two runs of blocks.

91A is a reading, not a calculation: unity and diversity, continuity and
discreteness, a syllogism, E. T. Bell, and the Euler/Condorcet story. **Lesson 90
is the hook** — she has just finished shrinking Δx towards dx, which is exactly the
"continuous thing cut into discrete pieces" the reading is about; Lesson 1 (and
Lesson 68 behind it) is where the trinity claim was first made.

91B is the arithmetic and it is where the set's other two new problems, 291 and
391, live — everything from 490 on is the usual cumulative review.
**Lesson 25 is the hook**: unit multipliers, unchanged. The only new instruction is
*how many times* — and the exponent on the unit is the count. Lesson 38 is named
too, for the capacity-versus-volume distinction the book is careful about.

Three judgement calls:

* The typeset fraction stacks under each `solution:` are images and did not
  survive the PDF extraction — the source prints `solution:` and then blank space,
  then the printed result. Every setup below is reconstructed from the book's own
  equivalent measures (`1 in = 2.54 cm`, `1 m = 100 cm`) and its own printed
  answers, all of which did survive. Idea 3 says so in one sentence on her page and
  the parent guide repeats it.
* The source prints the answer to Ex. 91.2a as `81.94 cm2`. The number is right
  (2.54³ = 16.387064, × 5 = 81.93532) but the unit is a typo — 5 in³ converts to
  cm³. Reproduced and flagged on her page rather than silently corrected, so she is
  not marked down against her own book without knowing why.
* The syllogism on page 1 affirms the consequent — the conclusion runs the major
  premise backwards, which is its converse. Lesson 81 gave her the name for that
  flip, and practice problem 1381 in this very set asks her for the inverse of a
  conditional, so the machinery is fresh. But that lesson deliberately set the truth
  question aside ("build the logically equivalent statement — do not worry about
  whether it is also true in real life"), and its one caution about truth points the
  other way: in its own boating example the converse and the inverse are the pair it
  calls both logical and true. So she has the vocabulary and not the warning. Her
  page reproduces the three lines faithfully and does not argue with them. The
  observation is raised with her father in the parent guide instead, where it
  belongs.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_91 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 91 · Pre-Algebra",
        "title": "Area is length twice. Volume is length three times.",
        "thesis": "Two halves today, and they are not related. The first is a "
                  "reading about why a subject that cuts continuous things into "
                  "countable pieces looks, to your book, like God's work. The second "
                  "is one counting rule: **the little number on the unit tells you "
                  "how many unit multipliers you owe**.",
        "formula": "5 in² × (2.54 cm / 1 in)² = 32.26 cm²",
        "roles": [
            {"tone": "start", "name": "the unit multiplier — a 1 in disguise",
             "text": "1 in = 2.54 cm, so the fraction 2.54 cm over 1 in is worth "
                     "exactly **1**. Multiplying by 1 cannot change how much you "
                     "have. It only changes what you call it. That is Lesson 25, "
                     "unchanged."},
            {"tone": "move", "name": "the exponent — how many copies",
             "text": "in² means in · in. Two inch-units standing there means two of "
                     "them to cancel, which means two multipliers. in³ means three. "
                     "Count the exponent and you have counted the fractions."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Two halves that have nothing to do with each other",
        "paragraphs": [
            "Saxon does this now and then. Lesson 91 is two lessons in one coat. The "
            "first half is two pages of reading with a single multiple-choice "
            "question at the end of it. The second half is arithmetic, and it is "
            "where the set's only other new problems — 291 and 391 — live. "
            "Everything after those is the usual review from earlier lessons. Do "
            "the two halves as two sittings, not one.",
            "Here is the second half, and you can answer it with a tape measure and "
            "no notation at all. **A rug is one yard long and one yard wide. A yard "
            "is three feet. How many square feet of floor does it cover?**",
            "Almost everybody says three. Go and lay it out. Three feet across, three "
            "feet down — that is three rows with three squares in each. **Nine.** The "
            "3 did not get used once. It got used **twice**, because there were two "
            "directions that needed converting.",
            "Now picture a box a yard long, a yard wide and a yard tall. Same question "
            "in three directions, so the 3 gets used three times: 3 × 3 × 3 is "
            "**twenty-seven** cubic feet in a cubic yard. Not three. Not nine.",
            "That is the whole of the second half, and you already own the machinery. "
            "In **Lesson 25** you learned to convert a length by multiplying it by a "
            "fraction worth 1. Nothing about that changes today. The only new "
            "instruction is *how many times to do it* — and the unit itself tells "
            "you, if you read the small number on its shoulder.",
            "The first half is a reading, and it is about something else entirely: "
            "why a subject that breaks smooth, continuous things into countable "
            "pieces should look, to your book, like the work of a God who is one and "
            "three at the same time.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "One God in three Persons. One curve in a million pieces.",
        "paragraphs": [
            "Back in **Lesson 1**, before any arithmetic happened, your book made a "
            "claim about who God is: **one** God, and **three** Persons. One and many "
            "at the same time, and neither half cancelling the other. The word for "
            "that is **trinity**, and Lesson 68 came back to it.",
            "Both halves of that idea have names in mathematics. **Continuous** means "
            "no gaps — one unbroken thing, like a line you can draw without lifting "
            "the pencil. **Discrete** means separate countable pieces, like eggs in a "
            "box. Nearly every mathematical object you have met so far is clearly one "
            "or clearly the other.",
            "Calculus is where the two meet, and that is why your book has stopped "
            "here to talk about it. Take a curve like `y = x²`. It is completely "
            "continuous — smooth, unbroken, no gaps anywhere. And calculus works by "
            "chopping it into **discrete pieces**, then making those pieces so small "
            "that you cannot draw one, cannot measure one, and have to take it on "
            "trust that they are there at all.",
            "You did this yourself in **Lesson 90**. You made Δx smaller. Then "
            "smaller. And the thing you were heading towards was `dx` — the "
            "infinitesimal difference, a gap too small to be a gap. A continuous "
            "curve, handled by cutting it into pieces that are almost nothing. One "
            "thing and many things, in the same breath.",
            "Your book's claim is that this is not a coincidence. **Being one and "
            "many at once is what God is like**, so it is what the things God made "
            "are like — and mathematics, on this view, is *discovered* rather than "
            "invented. A God-given tool, not a manmade one.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The argument",
        "title": "Three lines, in the order your book puts them",
        "steps": [
            {"label": "Major premise",
             "detail": "**If God made it, then it expresses His attribute of unity "
                       "and diversity.** A premise is something you are asked to "
                       "grant before an argument starts. This one is a claim about "
                       "God: whatever He makes carries His fingerprints, and the "
                       "fingerprint in question is being one and many at once."},
            {"label": "Minor premise",
             "detail": "**Mathematics expresses God's attribute of unity and "
                       "diversity.** This is the line the whole first half of the "
                       "lesson has been spent supporting — the continuous and the "
                       "discrete, living inside calculus together."},
            {"label": "Conclusion",
             "detail": "**Mathematics is made by God.** Which is the claim your book "
                       "set out to make: that mathematics is found rather than "
                       "invented, and that \"man created mathematics\" has it "
                       "backwards."},
        ],
        "after": "A **syllogism** is just this shape — two premises and the "
                 "conclusion they are meant to force. You have been circling this "
                 "kind of sentence for a while: Lesson 81's *if… then* statements are "
                 "the same machinery, and problem 1381 in this very practice set asks "
                 "you for the **inverse** of one of them. So read the three lines "
                 "slowly, more than once. Arguments written this compactly are meant "
                 "to be chewed on.",
    }),

    (B.KIND_SAY, {
        "text": "\"Before we get to the maths half — name me something else that's "
                "one thing and lots of things at the same time. Not a trick question. "
                "A song is one song and a stack of separate notes. A family is one "
                "family and it's you and me and your sister. Find me a third one. "
                "Then tell me which half you'd have to throw away to make it "
                "simple.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "A battle, or a dance?",
        "paragraphs": [
            "E. T. Bell wrote a book called *The Development of Mathematics*, and he "
            "thought the relationship between continuity and discreteness mattered so "
            "much that the whole history of the subject could be read as \"a battle "
            "for supremacy between these two concepts.\"",
            "Your book says: not a battle. More like a **dance**, or a relationship "
            "between good friends. Neither one wins, and neither one is trying to. "
            "Read that phrase twice — it is the sentence the whole first half has "
            "been walking towards.",
            "Where there **has** been a real fight, your book says, is with human "
            "pride — the claim that man created mathematics rather than found it. And "
            "it gives you a piece of evidence you could go and check. Leonhard Euler "
            "wrote two of the first books ever written about calculus, but his most "
            "famous work was not one of them: *Letters to a German Princess*, "
            "written to an 18th-century princess and translated into many "
            "languages. When it was translated into French, a revolutionary named "
            "Condorcet edited it and took great pains to take the Christian parts "
            "out. He did not want it getting about in France that one of the greatest "
            "mathematicians in recorded history was a devout Christian.",
            "Your book's closing thought, and the one worth carrying out of the first "
            "half: a war between science and Scripture, or between reason and faith, "
            "is a war somebody had to go to the trouble of arranging. On your book's "
            "account they come out of the same fountain, and separating the Creator "
            "from His creation is what leads to foolishness — it sends you to "
            "**Romans 1:18-25** for that, and to **Jeremiah 33:3** for the promise "
            "that there are great and unsearchable things still to be found.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "start",
        "title": "The small number on the unit counts your fractions",
        "paragraphs": [
            "Second half, and it starts where **Lesson 25** left off. There you "
            "converted lengths with **unit multipliers**: a fraction whose top and "
            "bottom are the same amount written two ways, so the whole fraction is "
            "worth exactly 1. `2.54 cm / 1 in` is 1. Multiplying by it cannot change "
            "how much you have — it only changes what you call it.",
            "An area conversion is that same move, done twice. Here is why, and it is "
            "not a rule to memorise. **Area is length × length.** So `in²` is not a "
            "new unit at all — it is `in · in`, two inch-units standing side by side. "
            "One multiplier cancels one of them. Two inch-units need **two** "
            "multipliers.",
            "**Volume is length × length × length**, so `in³` is `in · in · in` and "
            "it needs **three**. Same reason, one more time.",
            "Which gives you the only rule in this half, and it is a counting rule: "
            "**the exponent on the unit is the number of unit multipliers you owe.** "
            "cm is one. cm² is two. cm³ is three. Read it before you write anything "
            "down.",
            "One honest note about this page. Your book prints each conversion as a "
            "neatly typeset stack of fractions, and those stacks did not survive "
            "being pulled out of the PDF — under every `solution:` there is blank "
            "space where the working should be, and then the printed answer. So the "
            "setups below are written out in line instead, rebuilt from the book's "
            "own equivalent measures (`1 in = 2.54 cm` and `1 m = 100 cm`) and its "
            "own printed answers, which did survive. Have your book open beside this "
            "and check one against the other before you start.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "in² = in · in        so        (2.54 cm / 1 in)² = 6.4516 cm² / 1 in²",
        "note": "Two lengths multiplied together is what the little 2 **means**. So "
                "there are two `in` to get rid of, and one multiplier only cancels "
                "one of them. When you square the bracket to save writing, the "
                "exponent lands on **everything inside it** — the 2.54 becomes "
                "6.4516 *and* the cm becomes cm². Squaring the number but leaving the "
                "unit alone is the quiet mistake in this lesson, because it gives the "
                "right answer today and the wrong one the moment the units stop "
                "cancelling.",
    }),

    (B.KIND_TABLE, {
        "caption": "One number, three exponents — the book's own 410, converted three "
                   "ways",
        "headers": ["what it is", "the unit, spelled out", "multipliers you owe",
                    "410 of them, into metres"],
        "rows": [
            {"cells": ["a length", "cm", "1", "410 ÷ 100 = 4.1 m"]},
            {"cells": ["an area", "cm² = cm · cm", "2",
                       "410 ÷ 100² = 410 ÷ 10,000 = 0.041 m²"], "emphasis": True},
            {"cells": ["a volume", "cm³ = cm · cm · cm", "3",
                       "410 ÷ 100³ = 410 ÷ 1,000,000 = 0.00041 m³"], "emphasis": True},
        ],
        "note": "Read the last column downwards. Same 410, same two units at each "
                "end, and every answer is a hundred times smaller than the one above "
                "it. Nothing changed except the small raised number on the unit — and "
                "that number is doing all the work, because it is **counting how many "
                "times you divide by 100**. The two shaded rows are Examples 91.1b "
                "and 91.2b straight out of your book: `0.041` is what 91.1b rounds to "
                "`0.04`, and `0.00041` is what 91.2b writes as `4.1 × 10⁻⁴`. The top "
                "row is not in the book — it is there so you can see where the "
                "pattern starts.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Five moves, and the first one is counting",
        "steps": [
            {"label": "Read the exponent on the unit and say the number out loud.",
             "detail": "`cm` is one. `cm²` is two. `cm³` is three. That number is how "
                       "many unit multipliers you are about to write, and knowing it "
                       "*before* you write anything is what stops you writing one and "
                       "stopping."},
            {"label": "Write down what you are given, on the left.",
             "detail": "Your book insists on this order and it is worth keeping. The "
                       "given quantity first, then the multipliers stacked to its "
                       "right. A fraction invented before you know what it has to "
                       "cancel is a fraction that ends up upside down."},
            {"label": "Build one multiplier out of the equivalent measure — Lesson 25.",
             "detail": "The unit you are **leaving** goes on the **bottom**, so it can "
                       "cancel. The unit you are **going to** goes on top. The same "
                       "fact makes both fractions; which way up you write it is "
                       "decided entirely by which direction you are travelling.",
             "math": "inches → centimetres:  (2.54 cm / 1 in)      "
                     "centimetres → inches:  (1 in / 2.54 cm)"},
            {"label": "Use it as many times as step 1 told you.",
             "detail": "Two for an area, three for a volume. Writing the fraction out "
                       "in full that many times is never wrong. Writing it once and "
                       "putting the exponent on the bracket is the same thing with "
                       "less ink — and its one hazard is forgetting that the exponent "
                       "hits the unit too: `(1 m / 100 cm)²` is `1 m² / 10,000 cm²`."},
            {"label": "Cancel first. Calculate last.",
             "detail": "Run your eye along the tops and bottoms and strike out every "
                       "unit that appears in both. Whatever is left standing should "
                       "be exactly the unit the question asked for. If it is not, you "
                       "have the fraction upside down or the wrong number of copies — "
                       "and you have found that out for free, before spending a "
                       "single button press."},
        ],
        "after": "Then round once, at the end, to whatever the question asked for. One "
                 "number is worth knowing cold for this practice set, because "
                 "problems 291 and 391 both work in feet and inches: **12² = 144**. A "
                 "square foot is 144 square inches — not 12. Its volume twin is "
                 "**12³ = 1728** — a cubic foot is 1728 cubic inches — which nothing "
                 "in today's practice set asks for, but which is the same idea one "
                 "exponent up. If those feel surprising, rule a one-foot square into "
                 "one-inch boxes and count them.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 91.1a — use 2 unit multipliers to convert 5 in² to cm²",
        "equation": "5 in²  →  cm²     ·     1 in = 2.54 cm     ·     round to 2 d.p.",
        "steps": [
            {"label": "Look first",
             "text": "The question hands you the count before you start: **two** unit "
                     "multipliers. It did not have to. `in²` already says two, "
                     "because in² *is* in · in — two lengths multiplied, so two "
                     "inch-units standing there waiting to be cancelled."},
            {"label": "Step 1 · write down what is given",
             "text": "The given quantity goes down first and stays on the left. "
                     "Everything else is going to be built to fit it, so it has to be "
                     "on the page first.",
             "math": "5 in²   =   5 in · in"},
            {"label": "Step 2 · fetch the equivalent measure",
             "text": "From Lesson 25: 1 in = 2.54 cm. That one fact, written as a "
                     "fraction, is your multiplier. Inches go on the **bottom**, "
                     "because inches are what you are leaving.",
             "math": "the multiplier:  (2.54 cm / 1 in)      "
                     "inches underneath, so inches cancel"},
            {"label": "Step 3 · use it twice, because there are two inches to kill",
             "text": "One multiplier cancels one `in`. There are two of them. So "
                     "write the fraction down twice — this is the whole difference "
                     "between an area conversion and the length conversions you have "
                     "been doing since Lesson 25.",
             "math": "5 in² × (2.54 cm / 1 in) × (2.54 cm / 1 in)"},
            {"label": "Step 4 · check the cancelling before you touch the calculator",
             "text": "in² on the top, in × in on the bottom. They divide out and "
                     "vanish. The only units left standing are cm × cm, which is cm² "
                     "— an area, which is what you were asked for. This check is free "
                     "and it catches nearly every mistake in this lesson.",
             "math": "in² / in² = 1      →      cm × cm = cm²"},
            {"label": "Step 5 · now the arithmetic",
             "text": "2.54 × 2.54 is 6.4516, and there were 5 of them to start with. "
                     "Keep the digits; the rounding instruction is for the end.",
             "math": "5 × 2.54 × 2.54 = 32.258"},
            {"label": "Step 6 · round to 2 d.p.",
             "text": "Two decimal places was the instruction. Round once, here, and "
                     "not before. Sanity check while you are at it: a centimetre is "
                     "smaller than an inch, so there should be **more** square "
                     "centimetres than square inches — and 32 is more than 5.",
             "math": "32.258   →   32.26 cm²"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "91.1b",
        "question": "Use 2 unit multipliers to convert 410 cm² to m². Round to 2 d.p.",
        "steps": [
            {"label": "Same job, other direction",
             "text": "This time you are leaving the small unit and going to the big "
                     "one, so the count of them is going to come **down**. The "
                     "equivalent measure is 1 m = 100 cm, and centimetres go on the "
                     "bottom because centimetres are what you are leaving.",
             "math": "the multiplier:  (1 m / 100 cm)      "
                     "centimetres underneath, so centimetres cancel"},
            {"label": "Write it once and square it",
             "text": "Your book's own shortcut on this part: instead of writing the "
                     "same fraction out twice, write it once and put a 2 on the "
                     "bracket. It saves time and space, and there is less to copy "
                     "wrong. Just remember the 2 lands on the **unit** as well as the "
                     "number.",
             "math": "410 cm² × (1 m / 100 cm)²   =   410 cm² × (1 m² / 10,000 cm²)"},
            {"label": "Check the cancelling",
             "text": "cm² over cm² divides out and disappears. m² is the last unit "
                     "standing, which is what the question asked for. Correct shape, "
                     "so the arithmetic is safe to do.",
             "math": "cm² / cm² = 1      →      m²"},
            {"label": "Divide",
             "text": "100 squared is **10,000** — four zeros, because two lots of two "
                     "zeros. Not 200, and not 100.",
             "math": "410 ÷ 10,000 = 0.041"},
            {"label": "Round to 2 d.p.",
             "text": "Two decimal places was the instruction, so the 1 in the "
                     "thousandths place goes. Sanity check: a square metre is far "
                     "bigger than a square centimetre, so the count had to fall — and "
                     "410 cm² is about two thirds of a sheet of printer paper, which "
                     "is nowhere near a whole square metre.",
             "math": "0.041   →   0.04 m²"},
        ],
        "answer": "0.04 m²",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "move",
        "title": "Volume, and the thing Lesson 38 was doing instead",
        "paragraphs": [
            "Three multipliers instead of two, for the reason you already have: `cm³` "
            "is three cm standing together and each one needs its own fraction to "
            "cancel it. There is nothing else to learn. Your book makes the point by "
            "choosing **the same numbers and the same units** for Example 91.2 as it "
            "used for 91.1 — only the exponent moved.",
            "But watch what one extra copy does to the size of the answer. Converting "
            "cm to m divides by 100. Converting cm² to m² divides by 100 × 100 = "
            "**10,000**. Converting cm³ to m³ divides by 100 × 100 × 100 = "
            "**1,000,000**. Each step adds two more zeros, and by the third one you "
            "are dividing by a million.",
            "That is why 91.2b comes out as `4.1 × 10⁻⁴`. Once an answer has three "
            "zeros sitting after the decimal point, scientific notation (**Lesson "
            "72**) is simply an easier way to write it and a much harder way to "
            "miscount. There is a slider further down this page holding that exact "
            "number.",
            "Last thing, and it is a vocabulary point your book is careful about. In "
            "**Lesson 38** you converted **capacity** — how much a container *holds*, "
            "measured in things like litres, gallons and cups — and Lesson 38 also "
            "explained how capacity differs from volume. This lesson does **volume**: "
            "how much space something *occupies*, measured in units of length cubed — "
            "cm³, m³, ft³. The unit-multiplier method is identical. The family of "
            "units is not. So read the units in the question before you decide which "
            "one you are in.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "91.2a",
        "question": "Use 3 unit multipliers to convert 5 in³ to cm³. Round to 2 d.p.",
        "steps": [
            {"label": "Notice what did and did not change",
             "text": "Your book says it out loud: these are the same numbers and the "
                     "same units as Example 91.1, but the units are length³ now. So "
                     "only one thing about the method moves — you write each "
                     "multiplier three times instead of twice."},
            {"label": "Three copies of the inch multiplier",
             "text": "in³ is in · in · in. Three inch-units on the top, so three "
                     "fractions with inches on the bottom. Check the cancelling "
                     "first, as always: all three inches go, and cm × cm × cm is left "
                     "standing, which is cm³.",
             "math": "5 in³ × (2.54 cm / 1 in) × (2.54 cm / 1 in) × (2.54 cm / 1 in)"},
            {"label": "Do the arithmetic",
             "text": "2.54 multiplied by itself three times is 16.387064 — that is "
                     "2.54 × 2.54 × 2.54, **not** 2.54 × 3. Then multiply by the 5 "
                     "you started with and round to two decimal places.",
             "math": "5 × 2.54 × 2.54 × 2.54 = 5 × 16.387064 = 81.93532   →   "
                     "81.94 cm³"},
            {"label": "One thing to fix in your book",
             "text": "Your guide prints this answer as `81.94 cm²`. The **number is "
                     "right**; the little 2 should be a 3. You started with cubic "
                     "inches and every step kept three lengths, so you finish with "
                     "cubic centimetres. Write **81.94 cm³**, and do not let the "
                     "printed line talk you out of it. This is the cancelling check "
                     "from step 5 of the recipe, and it works even on the answer key."},
        ],
        "answer": "81.94 cm³",
    }),

    (B.KIND_WORKED, {
        "number": "91.2b",
        "question": "Use 3 unit multipliers to convert 410 cm³ to m³. Use scientific "
                    "notation and round to 1 d.p.",
        "steps": [
            {"label": "Write it once and cube it",
             "text": "Same shortcut as 91.1b, one exponent higher — and the 3 lands "
                     "on the unit as well as on the 100. A hundred multiplied by "
                     "itself three times is **1,000,000**: six zeros, because three "
                     "lots of two.",
             "math": "410 cm³ × (1 m / 100 cm)³   =   410 cm³ × (1 m³ / 1,000,000 cm³)"},
            {"label": "Check the cancelling, then divide",
             "text": "cm³ over cm³ cancels and m³ is left standing, so the shape is "
                     "right. Then it is one division. Count the zeros carefully — "
                     "this is where the answer comes out a hundred times too big if "
                     "you were still thinking in areas.",
             "math": "410 ÷ 1,000,000 = 0.00041"},
            {"label": "Put it into scientific notation",
             "text": "Lesson 72 again. Move the point four places to the right so "
                     "that exactly one digit sits in front of it, and pay for those "
                     "four places with an exponent of **-4**. One decimal place was "
                     "asked for, and 4.1 already has exactly one.",
             "math": "0.00041   =   4.1 × 10⁻⁴ m³"},
        ],
        "answer": "4.1 × 10⁻⁴ m³",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Using the multiplier once on an area conversion.",
             "wrong": "5 in² × (2.54 cm / 1 in) = 12.70",
             "right": "5 in² × (2.54 cm / 1 in)² = 5 × 6.4516 = 32.258  →  32.26 cm²",
             "note": "**12.70 instead of 32.26** — this is the mistake the whole "
                     "lesson exists to prevent, and it is just doing what you have "
                     "always done. The units give it away before the number does: one "
                     "multiplier leaves one `in` uncancelled, so that answer is "
                     "really 12.70 in·cm, which is not a unit anybody uses. Cancel "
                     "first and this one cannot survive."},
            {"name": "Squaring the number but not the unit.",
             "wrong": "(2.54 cm / 1 in)² = 6.4516 cm / 1 in",
             "right": "(2.54 cm / 1 in)² = 6.4516 cm² / 1 in²",
             "note": "The exponent lands on **everything inside the bracket** — the "
                     "number *and* the unit. This one is dangerous precisely because "
                     "the arithmetic still comes out right on 91.1a, so nothing warns "
                     "you. What it costs you is the cancelling check — and the "
                     "cancelling check catches every other error on this list except "
                     "the cubing one, which the units cannot see."},
            {"name": "Dividing by 100 when you should divide by 10,000.",
             "wrong": "410 cm²  →  410 ÷ 100 = 4.1 m²",
             "right": "410 cm²  →  410 ÷ 100 ÷ 100 = 410 ÷ 10,000 = 0.041  →  0.04 m²",
             "note": "**4.1 m² instead of 0.04 m²** — a hundred times too big, and it "
                     "does not look absurd, which is what makes it expensive. Get a "
                     "picture of the two: 410 cm² is about two thirds of a sheet of "
                     "printer paper. 4.1 m² is about the floor of a small bathroom. "
                     "If your answer could be walked on, you converted once instead "
                     "of twice."},
            {"name": "Using two multipliers on a volume conversion.",
             "wrong": "410 cm³  →  410 ÷ 10,000 = 0.041 m³",
             "right": "410 cm³  →  410 ÷ 1,000,000 = 0.00041 = 4.1 × 10⁻⁴ m³",
             "note": "**0.041 instead of 0.00041**, again a hundred times too big — "
                     "and notice that the wrong answer here is the *right* answer to "
                     "the previous example, which is exactly why your book gave both "
                     "problems the same numbers. Count the exponent on the unit and "
                     "count your fractions. They must match: a 3 up there means three "
                     "of them."},
            {"name": "Multiplying by 3 instead of cubing.",
             "wrong": "5 × (2.54 × 3) = 5 × 7.62 = 38.10",
             "right": "5 × 2.54 × 2.54 × 2.54 = 5 × 16.387064 = 81.93532  →  81.94 cm³",
             "note": "**38.10 instead of 81.94.** \"Use it three times\" means three "
                     "copies **multiplied together**, not the number tripled. The "
                     "word *three* is doing two different jobs in your head and only "
                     "one of them is this one. Write the fraction out three times in "
                     "full if the exponent tempts you — it is longer and it is never "
                     "wrong."},
            {"name": "Writing the multiplier upside down.",
             "wrong": "5 in² × (1 in / 2.54 cm)² = 5 ÷ 6.4516 = 0.775  →  0.78",
             "right": "5 in² × (2.54 cm / 1 in)² = 5 × 6.4516 = 32.258  →  32.26 cm²",
             "note": "**0.78 instead of 32.26.** Nothing cancels: with inches on top "
                     "in both places, the in² multiplies instead of dividing out and "
                     "you finish holding in⁴/cm², which is not a unit anybody uses. "
                     "There is a second free check here as well — a centimetre is "
                     "smaller than an inch, so the *count* of them has to go up. "
                     "Yours went down, so it was wrong before you rounded it."},
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Both halves lean on marks and words the book does not stop to "
                 "explain. Almost none of them are mathematics — they are labels, and "
                 "here is what each one is short for.",
        "rows": [
            {"symbol": "in²", "plain": "square inches — short for in · in. The raised "
                                       "2 counts how many lengths are multiplied "
                                       "together",
             "example": "a postage stamp is about 1 in²"},
            {"symbol": "in³", "plain": "cubic inches — in · in · in. Three lengths, so "
                                       "it is a solid, not a flat shape",
             "example": "a one-inch dice is 1 in³"},
            {"symbol": "unit multiplier", "plain": "a fraction whose top and bottom are "
                                                   "the same amount written two ways, "
                                                   "so it is worth exactly 1",
             "example": "2.54 cm / 1 in"},
            {"symbol": "equivalent measure", "plain": "the fact a multiplier is built "
                                                      "out of — two ways of saying the "
                                                      "same amount (Lesson 25)",
             "example": "1 in = 2.54 cm"},
            {"symbol": "(2.54 cm / 1 in)²", "plain": "the whole bracket squared — the "
                                                     "number AND the unit. Identical "
                                                     "to writing the fraction twice",
             "example": "6.4516 cm² / 1 in²"},
            {"symbol": "cancel", "plain": "the same unit appearing on a top and a "
                                          "bottom divides out and disappears",
             "example": "in² ÷ in² = 1"},
            {"symbol": "4.1 × 10⁻⁴", "plain": "scientific notation (Lesson 72) — the "
                                              "minus means the point moves four places "
                                              "LEFT to write it out",
             "example": "0.00041"},
            {"symbol": "2 d.p.", "plain": "round the final answer to 2 decimal places, "
                                          "once, at the end",
             "example": "32.258  →  32.26"},
            {"symbol": "(C)", "plain": "calculator allowed on this problem — a "
                                       "permission, not an instruction",
             "example": "291. (C) convert 11 ft² to in²"},
            {"symbol": "capacity vs volume", "plain": "capacity is how much a container "
                                                      "HOLDS (Lesson 38); volume is "
                                                      "how much space a thing OCCUPIES",
             "example": "litres  ·  cm³"},
            {"symbol": "continuous / discrete", "plain": "continuous = no gaps, one "
                                                         "unbroken thing. discrete = "
                                                         "separate countable pieces",
             "example": "a curve  ·  eggs in a box"},
            {"symbol": "Δx and dx", "plain": "Δx is a gap you can measure; dx is that "
                                             "gap shrunk until it is infinitesimal "
                                             "(Lesson 90)",
             "example": "Δx  →  dx"},
            {"symbol": "syllogism", "plain": "an argument laid out in three lines: two "
                                             "premises, then the conclusion they are "
                                             "meant to force",
             "example": "the three lines on page 1"},
        ],
        "after": "The one to keep your eye on is the **small raised number on a "
                 "unit**. It is not decoration and it is not something you multiply "
                 "by. It is a count of how many lengths got multiplied together — "
                 "which is exactly the count of unit multipliers you owe. `cm` is "
                 "one. `cm²` is two. `cm³` is three. Read it first, every time.",
    }),

    (B.KIND_TOOL, {
        "title": "The point moves. The value does not.",
        "intro": "This is Lesson 72's slider, brought back for the last line of "
                 "Example 91.2b. The number loaded into it is your book's own answer, "
                 "`4.1 × 10⁻⁴`. Drag the slider: the digits move one way, the "
                 "exponent moves the other, and the value along the bottom sits there "
                 "refusing to change — which is the entire reason you are allowed to "
                 "swap one writing for the other.",
        "widget": "scislide",
        # mantissa 4.1 / exponent -4 is Ex. 91.2b's printed answer, not a made-up
        # number — so sliding it is checking the book rather than playing. span 4 is
        # chosen exactly: four moves right of standard form lands on 0.00041 × 10⁰,
        # which is the *other* line the book prints for the same answer. She can put
        # the two halves of `0.00041 = 4.1 × 10⁻⁴` on screen with one drag.
        "config": {"mantissa": 4.1, "exponent": -4, "span": 4},
        "after": "Slide it until the front number reads **0.00041** and stop there. "
                 "The tool will object — **too small**, it says, and offers to put a "
                 "digit back in front. It is right that this is not standard form, "
                 "and you should stay put anyway: that is exactly the state you came "
                 "here to look at. Now look at the exponent. It has climbed all the "
                 "way to 0, so there is no power of ten left doing any work. What you "
                 "are looking at is the plain decimal, and it is character for "
                 "character what `410 ÷ 1,000,000` gave you a few boxes up. Two "
                 "writings, one number. Then answer the question in the drop-down "
                 "below **before** you open it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Example 91.1b turned 410 cm² into 0.041 m². Example 91.2b turned "
                  "410 cm³ into 0.00041 m³. Same 410, same units at both ends. Why is "
                  "the volume answer exactly a hundred times smaller?",
        "answer": "**Because a volume owes one more unit multiplier than an area "
                  "does, and each multiplier divides by another 100.**   →   area: "
                  "410 ÷ 100 ÷ 100 = 410 ÷ 10,000 = 0.041   →   volume: "
                  "410 ÷ 100 ÷ 100 ÷ 100 = 410 ÷ 1,000,000 = 0.00041   →   The second "
                  "line is the first line with one more `÷ 100` on the end, and "
                  "0.041 ÷ 100 = 0.00041. The exponent on the unit went from 2 to 3, "
                  "so the count of hundreds went from two to three, so the answer "
                  "fell by a factor of a hundred. Nothing else about the two problems "
                  "differs at all — which is exactly why your book gave them the same "
                  "numbers.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "The first half is a **reading**, not a calculation. Its claim: "
            "mathematics shows **unity and diversity** — one thing made of many "
            "pieces — because the God who made it is one God in three Persons "
            "(Lesson 1, and Lesson 68 behind it).",
            "Calculus is where that shows up most plainly: a smooth continuous curve "
            "like `y = x²` cut into pieces so small you have to trust they are there. "
            "That was **Lesson 90**, shrinking Δx towards dx.",
            "Continuity and discreteness are not at war. Your book's own phrase for "
            "what they are instead is **a relationship between good friends**.",
            "**Area is length × length**, so an area conversion uses each unit "
            "multiplier **twice**.",
            "**Volume is length × length × length**, so a volume conversion uses each "
            "unit multiplier **three times**.",
            "The exponent on the unit **counts your multipliers**. cm² means two, cm³ "
            "means three. That one sentence is the whole second half.",
            "You may write the multiplier once and put the exponent on the bracket — "
            "but it lands on the **unit** as well as the number: "
            "`(1 m / 100 cm)² = 1 m² / 10,000 cm²`.",
            "The unit you are **leaving** goes on the bottom so it cancels; the unit "
            "you are **going to** goes on top. **Check the cancelling before you "
            "calculate** — the units catch the mistake for free.",
            "Lesson 38 converted **capacity** — what a container holds. This lesson "
            "converts **volume** — the space a thing takes up. Same method, different "
            "family of units.",
            "410 cm² is 0.041 m² — 0.04 once your book rounds it. 410 cm³ is "
            "0.00041 m³. Same number in, and the volume answer is a hundred times "
            "smaller — that extra hundred is the third multiplier.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 91 first. If it didn't quite land, this is here to fix that "
    "— and there's a slider near the bottom holding one of the answers. Two halves "
    "today, and they have nothing to do with each other. The first is a reading: why "
    "calculus, of all things, is where your book sees God's fingerprints. The second "
    "is one counting rule — the little number on the unit tells you how many times "
    "to convert."
)

PARENT_CONTENT = """## The big idea

Two halves, genuinely unrelated. Teach them as two short sittings.

**91A — Calculus and the Trinity.** This is a *reading*, not a calculation, and the
only thing it produces in the practice set is multiple-choice problem 191. The
argument: God is one and three at once — the trinity, from **Lesson 1** and revisited
in Lesson 68 — and *unity and diversity together* is therefore the fingerprint on
everything He made. Mathematics has that fingerprint in two words she now owns:
**continuous** (no gaps, one unbroken thing) and **discrete** (separate countable
pieces). Calculus is where they meet, which is why the book stopped here: a perfectly
continuous curve like `y = x²` gets handled by cutting it into pieces so small you
must take them on trust. She did that herself last lesson, shrinking `Δx` towards
`dx`. **Lesson 90 is the hook — say its name out loud, because it makes the whole
first half concrete instead of abstract.**

The book quotes E. T. Bell — that the history of mathematics can be read as a battle
between these two ideas — and then disagrees with the word *battle*: it is more like a
dance, or a relationship between good friends. That phrase is the answer to problem
191, word for word, so it is worth her hearing it twice.

**91B — area and volume conversions.** One rule, and it is a counting rule. An area
conversion is a **Lesson 25** length conversion done **twice**, because area is
length × length and `in²` is really `in · in` — two identical units to cancel means
two identical unit multipliers. Volume needs **three**. **The exponent on the unit is
the number of multipliers she owes.** That is the entire second half.

The book also offers a shortcut on the (b) parts: rather than writing the same
fraction twice, write it once and square the bracket. Fine — as long as she remembers
the exponent lands on the *unit* too: `(1 m / 100 cm)²` is `1 m² / 10,000 cm²`, not
`1 m² / 100 cm²`.

And one vocabulary point the book is careful about: **Lesson 38** converted
*capacity* (litres, gallons, cups — what a container holds) and explained how that
differs from volume. This lesson does *volume* — space occupied, in units of length
cubed. Same method, different family of units.

**About the missing working.** Under each `solution:` her DIVE guide sets the
conversion as a typeset stack of fractions, and those are images — they did not
survive the extraction, so the source reads `solution:`, blank space, then the printed
result. What *did* survive is everything needed to rebuild them: the equivalent
measures the book names (`1 in = 2.54 cm`, `1 m = 100 cm`), the instruction of how
many multipliers, and every printed answer. Her page writes each setup out in line and
tells her plainly that this is what happened, and asks her to check one against her
book. Please do check one with her — it takes ten seconds and it means she is working
from her own book rather than trusting this page.

**One typo to fix in her book.** Ex. 91.2a converts 5 in³ and the guide prints the
answer as `81.94 cm²`. The number is right — `2.54³ = 16.387064`, times 5 is
`81.93532` — but the unit should be **cm³**. Her page reproduces the printed line and
says so, because a child who has just been taught to check her units and then finds
the answer key contradicting her needs to know which one to believe. Tell her she was
right.

**One thing to have an answer ready for.** The syllogism on page 1 runs: *if God made
it, it expresses unity and diversity; mathematics expresses unity and diversity;
therefore mathematics is made by God.* She has been working on exactly this shape of
sentence very recently — **Lesson 81** is conditionals, converses and inverses, and
problem 1381 in this very practice set asks her for the **inverse** of one. Lesson 81
also gave her the name for the move these three lines make — the conclusion runs the
major premise backwards, which is its **converse** — but that lesson deliberately
stopped at building the forms and told her not to worry about whether a flip is also
true, and its one caution about truth points the other way: in the boating example it
calls the converse and the inverse the two that are *both logical and true*. So she
has the vocabulary and not the warning. If she notices the shape anyway, the noticing
is good work and worth telling her so. It is also worth saying that the claim does
not stand or fall on those three lines — the surrounding pages argue it from what
mathematics is actually *like*, not from the syllogism, and three lines in a textbook
are a summary of a conviction rather than a proof of one. The thing to avoid is her
concluding that the logic she is being taught has to be switched off in the parts of
the book that matter most to you. Her own page reproduces the argument as printed and
does not argue with it; this is your conversation to have, not the page's.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Start with 91A and no book. Ask: **"Name me something that's one thing and lots of
   things at the same time."** A song and its notes. A family. A team. Let her find
   two or three. Then: **"Which half would you have to throw away to make it
   simple?"** Neither — and that is the whole first half of the lesson in her own
   words before she has read a page of it.
2. Now the connection. **"What were you doing last lesson with Δx?"** You want
   *making it smaller and smaller*. Then: **"So what were you doing to a smooth
   curve?"** Cutting it into pieces. **"How many pieces?"** More than you can count,
   each smaller than you can draw. That is continuous and discrete in the same
   sentence, and she got there from Lesson 90 rather than from a definition.
3. Read her the E. T. Bell line and the book's reply, then ask: **"Battle, or
   dance?"** The book's answer is *a relationship between good friends*, and problem
   191 is going to ask her that in those words.
4. Switch halves. Put a tape measure on the floor. **"A rug one yard by one yard —
   how many square feet?"** Nearly every child says three. Mark it out, three by
   three, and count nine. Then: **"Why nine and not three?"** You want *because there
   were two directions*. Do not supply it. Then ask about a cubic yard and let her
   arrive at 27 herself.
5. Now the notation, and only now. Write `in²` and ask: **"What does the little 2
   actually mean?"** *in times in.* **"So how many inches do you have to cancel?"**
   Two. **"So how many multipliers?"** Two. That chain — exponent, units to cancel,
   fractions to write — is the second half of the lesson and she just said all three
   links out loud.

If she is lost on 91B, do not re-explain the rule. Give her `100 in²` to convert to
`ft²` (problem 391) and ask one question only: *"how many inches are you cancelling?"*

## The classic mix-ups, with the exact wrong answer each one produces

- **One multiplier on an area conversion.** `5 in² × 2.54` gives **12.70** instead of
  **32.26**. The unit gives it away before the number does: one multiplier leaves an
  `in` uncancelled, so 12.70 is really in·cm. Fix: cancel before calculating.
- **Squaring the number but not the unit.** She writes `(2.54 cm / 1 in)²` as
  `6.4516 cm / 1 in`. The arithmetic on 91.1a still comes out right, which is why this
  one survives — but it has quietly destroyed the cancelling check, and the cancelling
  check is what catches every other error on this list except the cubing one.
- **Dividing by 100 instead of 10,000.** On 91.1b she gets **4.1 m²** instead of
  **0.04 m²** — a hundred times too big and not absurd-looking. Fix with a picture:
  410 cm² is about two thirds of a sheet of printer paper; 4.1 m² is a small
  bathroom floor. If the answer could be walked on, she converted once.
- **Two multipliers on a volume conversion.** On 91.2b she gets **0.041 m³** instead
  of **0.00041 m³**. Note what the wrong answer *is*: it is the correct answer to the
  previous example. That is not a coincidence — the book gave both problems the same
  numbers on purpose, and it is the cleanest possible demonstration that the exponent
  is the only thing that changed.
- **Multiplying by 3 instead of cubing.** `5 × (2.54 × 3)` = **38.10** instead of
  **81.94**. "Use it three times" means three copies *multiplied*, not the number
  tripled. Fix: have her write the fraction out three times in full; it is longer and
  it is never wrong.
- **The multiplier upside down.** `5 in² × (1 in / 2.54 cm)²` gives **0.78** instead
  of **32.26**, and nothing cancels — the units come out `in⁴/cm²`. Second free check
  available: centimetres are smaller than inches, so the count must go *up*. Hers went
  down.

## What to watch her do

Watch her **pencil**, in this order:

1. **Does she write the given quantity down first?** The book insists on this and it
   is not fussiness — a fraction invented before she knows what it has to cancel is a
   fraction that ends up upside down about half the time.
2. **Does she say a number before she writes a fraction?** You want to hear "two" or
   "three" — the exponent read off the unit — *before* any multiplier appears on the
   page. A child who starts writing fractions and then counts them has the steps
   backwards and will stop at one.
3. **Does she strike out the cancelling units on the page?** Physically crossed out,
   with the survivor circled. This is the single most diagnostic habit in the lesson,
   and you can see it from across the table. Every error above except the cubing one
   is caught by it.
4. **Does the exponent land on the unit as well as the number?** Look at what she
   actually wrote inside the squared bracket. `6.4516 cm² / 1 in²` is right;
   `6.4516 cm / 1 in` is the quiet failure that still gets 32.26 today.
5. **Does she round only at the end?** `0.041` should appear on the page before
   `0.04` does. Rounding at the division and then rounding again is how a 2 d.p.
   answer drifts.

Getting 32.26 is not what to watch for. She can get 32.26 by copying the shape of the
worked example. The cancelling habit is what survives a problem that goes the other
direction.

## Extend it

- **Do problems 291 and 391 out loud with her.** They are the same skill in feet and
  inches, and they need `12² = 144` — a square foot is 144 square inches, not 12,
  which surprises most adults. 291: `11 ft² × (12 in / 1 ft)² = 11 × 144` = **1584
  in²**. 391: `100 in² × (1 ft / 12 in)² = 100 ÷ 144` = **0.69 ft²**. If she gets both
  without help, the rule has landed.
- **Rule a one-foot square into one-inch boxes and count them.** 144. It takes five
  minutes and it makes the number stop being arbitrary. Then ask how many one-inch
  cubes fill a one-foot box — she can reason to 1728 without building it.
- **The unit-cancelling check, applied to the answer key.** Ex. 91.2a is a live
  example: the book's printed unit is wrong and her method catches it. That is worth
  naming out loud as a moment where the method beat the authority, because it is rare
  and it builds the habit.
- **For 91A, go and look up the Euler story.** Leonhard Euler's *Letters to a German
  Princess* and Condorcet's French edition are real history and are findable. A
  fifteen-minute look at what was actually cut is a better use of the first half than
  re-reading it.
- **A question worth leaving open.** Ask her what a *fourth* power of a length would
  be — ft⁴ — and how many multipliers it would need. She can answer the second part
  instantly and nobody can answer the first part with a picture. Meeting that as a
  puzzle is worth more than being told.

## Where this sits

DIVE Lesson 91, *Calculus and the Trinity; Area and Volume Conversions*. Reviews
**Lessons 1, 25, 38 and 90**, and the book's own first page says **No New Rules or
Definitions**.

- **Lesson 90** is the one to revisit if the first half feels abstract. Δx shrinking
  towards dx *is* the continuous-and-discrete idea, and she has already done it.
- **Lesson 25** is the one to revisit if the second half is lost. Unit multipliers and
  equivalent measures are entirely Lesson 25's; today only adds a count.
- **Lesson 38** is worth a glance for the capacity-versus-volume distinction, which
  the book raises here specifically to say *this lesson is not doing that*.
- **Lesson 1** (and **Lesson 68**) is where the trinity claim was first made. Both sit
  outside this course's seeded lessons and this guide has not read them, so nothing
  here describes what else is in them; her book is the place to look if you want the
  original wording.

**Proficient** looks like: converts an area correctly in the familiar direction, uses
two multipliers without being reminded, and can say what a bit of the first half was
about.
**Mastered** looks like: reads the exponent off the unit *first*, uses three for a
volume unprompted, cancels on the page and uses the leftover units as a check — and
can explain why 410 cm³ comes out a hundred times smaller than 410 cm².
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 91 (calculus and the Trinity; area and "
            "volume conversions) — idempotent.")

    LESSON_NUMBER = 91
    TITLE = ("Count the Exponent — Calculus and the Trinity, and Area and Volume "
             "Conversions")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
