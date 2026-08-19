"""Saxon Pre-Algebra Lesson 98 — Sequences and Series.

Reviews Lessons 5, 68 and 75, and this is the rare lesson where the book says
out loud what each one is for. Lesson 5 is the hook for the definition — that is
where *sequence* was first defined, and 98 keeps that definition unchanged.
Lesson 68 is the hook for the picture: that is where a sequence was used to
recognize a linear pattern and graph it, which is why the tool on her page is
graph paper rather than anything cleverer. Lesson 75 is the hook for why anyone
cares — a computer holds discrete pieces of information, and a sequence is
exactly that shape. The book's own first page says **No New Rules**, and means
it: there is no formula in this lesson at all.

Two halves, so two runs of blocks. 98A is sequences (Examples 98.1 and 98.2 —
common difference and common ratio) and 98B is series (Examples 98.3 and 98.4 —
the sums 25 and 26).

Judgement calls:

* Nothing in this lesson arrives as a figure. Both pages reach this file as text,
  so unlike 86 and 87 there is no picture to reconstruct and nothing missing from
  her page. The only images in the source are in the review half of the practice
  set, which this lesson does not teach.
* Example 98.3's arithmetic is kept exactly as the book prints it, pairs and all:
  `1+3+5+7+9` becomes `4 + 12 + 9`, then `16 + 9 = 25`. That is friendlier than a
  left-to-right running total, and it is what she will see printed beside her, so
  the page follows it rather than tidying it up.
* Examples 98.1a and 98.2a both begin **2, 4** — one arithmetic, one geometric.
  The book does not remark on it. This page does, in the table note, the error
  list and the reveal, because it is the cleanest possible argument for Saxon's
  own instruction to *test some pairs*, and every number in it comes from the two
  printed examples.
* One check is added that the book does not print — five terms of 98.3 add to
  five times the middle term. It is labelled on her page as a check and not a
  rule, and it is flagged as working only on an arithmetic list with an odd
  number of terms.
* The tool graphs 98.1a's terms against their term numbers. Saxon does not draw
  this, but the lesson's own Lesson 68 sentence is about doing exactly that, and
  the widget's family buttons confirm the straight line for the arithmetic list
  and the curve for the geometric one. Her page also warns her, before she meets
  it, that the widget will say `|x|` fits her arithmetic dots too — it does, and
  the honest reason why is worth three sentences.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_98 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 98 · Pre-Algebra",
        "title": "A list with a rule. Then the total of the list.",
        "thesis": "A **sequence** is a list of numbers you could carry on without "
                  "being told how. A **series** is what you get when you decide to "
                  "add that list up. Two words, and the two kinds this lesson "
                  "names are the two most common ones — the rule is either *add "
                  "the same thing* or *multiply by the same thing*.",
        "formula": "arithmetic:  + the common difference     ·     "
                   "geometric:  × the common ratio",
        "roles": [
            {"tone": "start", "name": "the common difference — what you add",
             "text": "Subtract a term from the one after it and the answer comes "
                     "out the same every time. That answer is the common "
                     "difference. It is allowed to be negative, which only means "
                     "the list is heading down."},
            {"tone": "move", "name": "the common ratio — what you multiply by",
             "text": "Divide a term by the one before it and the answer comes out "
                     "the same every time. That answer is the common ratio. "
                     "Between 0 and 1 and the list is shrinking; above 1 and it "
                     "runs away."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why a list of numbers is worth its own word",
        "paragraphs": [
            "Somebody offers you two ways to be paid for walking their dog for a "
            "month. The first way: five dollars on day one, and a dollar more each "
            "day after that. Six, seven, eight. The second way: one cent on day "
            "one, and double it every day. Two cents, four cents, eight cents.",
            "The first way looks obviously better, and for eleven days it is. On "
            "day twelve the doubling one goes past it and never comes back. By day "
            "thirty it pays over five million dollars — on that one day.",
            "Both of those are lists with a rule. But they are not the same kind of "
            "rule, and the difference is the whole first half of this lesson. One "
            "of them **adds** the same amount every step. The other **multiplies** "
            "by the same amount every step. For the first eleven days the "
            "multiplying one looks like a joke — two cents, four cents, eight "
            "cents. By the end of the month it has eaten the other.",
            "Now the second question, and it is a different one: what do you "
            "actually take home? Not any single day's pay — the **total** of all "
            "thirty days. That is $585 the first way and $10,737,418.23 the second. "
            "A list is one thing; the total of the list is another. In this lesson "
            "the list is called a *sequence* and the total is called a *series*, "
            "and 98A is about the first while 98B is about the second.",
            "Your book puts this next to computers, and points back at **Lesson "
            "75**: a computer can only hold discrete pieces of information — "
            "separate, countable, one and then the next, never a smooth smear. A "
            "sequence is exactly that shape, which is why the two subjects keep "
            "running into each other.",
            "One promise before you start. The first page of your lesson says **No "
            "New Rules**, and it is telling the truth. There is no formula in here. "
            "Everything you are about to do is one subtraction, one division, or "
            "some adding — with two new words on top.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "A sequence is a list you could carry on by yourself",
        "paragraphs": [
            "Saxon's definition is one line: **numbers ordered in a way that they "
            "form a definite pattern**. Two words in it are doing all the work.",
            "*Ordered* means the order is part of the thing. 2, 4, 6, 8 and 8, 4, "
            "6, 2 are not the same sequence, and the second one is not a sequence "
            "at all — nobody can say what comes after it.",
            "*Definite* means you can say what comes next and be **sure**, not "
            "guess. That is the test for whether something is a sequence: hand it "
            "to somebody else and they should be able to carry it on without asking "
            "you anything.",
            "Each number in the list is called a **term**. The first number is term "
            "1 — not term 0, and not the thing before the list starts. That sounds "
            "like fussiness until 98B, where miscounting the terms is the mistake "
            "that costs the most marks.",
            "The three dots at the end — `2, 4, 6, 8, 10, ...` — mean *and so on, "
            "by the same rule*. They are a promise that the pattern does not stop "
            "and does not change.",
            "You met this word first in **Lesson 5**, and used it again in **Lesson "
            "68** to spot a linear pattern and graph it. Lesson 98 is not replacing "
            "either of those. It is giving the two most common kinds of sequence "
            "their names.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Read me the list out loud, all of it. Now tell me the next "
                "number — and then tell me how you knew. If you got there by adding "
                "the same thing every time, it is arithmetic. If you got there by "
                "multiplying by the same thing every time, it is geometric. That is "
                "the whole first half of the lesson, and you just did it.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "Two kinds: the adding kind and the multiplying kind",
        "paragraphs": [
            "In an **arithmetic sequence**, each term is separated from the one "
            "before it by a **common difference**. The word *difference* is the "
            "instruction: differences come from subtracting, so you find it by "
            "subtracting.",
            "In a **geometric sequence**, each term is separated from the one "
            "before it by a **common ratio**. The word *ratio* is the instruction "
            "too: ratios come from dividing, so you find it by dividing.",
            "Both of the book's rules are the same sentence with one word changed — "
            "*the same between each term and the one before it*. Which means the "
            "order inside the subtraction is not up to you. **Later first, earlier "
            "second.** In the list 10, 5, 0, the 5 comes after the 10, so it is "
            "5 - 10 = -5. Do it the comfortable way round and you get +5, which "
            "describes a list climbing when yours is falling.",
            "Saxon says *test some pairs* — and says it four times, once in every "
            "part of both examples. That plural is not padding. **One pair is a "
            "guess. Two pairs is a check.** You will see why in a moment: two of "
            "the book's own examples start with exactly the same two numbers and "
            "then go somewhere completely different.",
            "Which test do you reach for first? Look at the list. Creeping up or "
            "down by roughly the same amount → try subtracting. Doubling, halving, "
            "exploding → try dividing. And if the subtractions come out different "
            "from each other, that is not a failed attempt. It is the answer to a "
            "question: it is **not** arithmetic, so divide instead.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "The two families, and the book's own four sequences",
        "headers": ["the sequence", "what separates the terms", "test it by",
                    "the book's own test", "the answer"],
        "rows": [
            {"cells": ["2, 4, 6, 8, 10, ...", "a common difference", "subtracting",
                       "4 - 2 = 2   and   6 - 4 = 2", "difference 2"],
             "emphasis": True},
            {"cells": ["10, 5, 0, -5, -10, -15, ...", "a common difference",
                       "subtracting", "5 - 10 = -5   and   -5 - 0 = -5",
                       "difference -5"]},
            {"cells": ["2, 4, 8, 16, 32, ...", "a common ratio", "dividing",
                       "4 ÷ 2 = 2   and   8 ÷ 4 = 2", "ratio 2"],
             "emphasis": True},
            {"cells": ["4, 2, 1, 1/2, 1/4, 1/8, ...", "a common ratio", "dividing",
                       "2 ÷ 4 = 1/2   and   1/4 ÷ 1/2 = 1/2", "ratio 1/2"]},
        ],
        "note": "Look at the two shaded rows, which are the a) parts of Examples "
                "98.1 and 98.2. **They both start 2, 4.** One of them is adding 2 "
                "and the other is multiplying by 2, and for the first two terms "
                "there is no way on earth to tell them apart. At the third term one "
                "says 6 and the other says 8, and from there they never meet again. "
                "That is the whole reason Saxon tells you to test some *pairs*. The "
                "two unshaded rows do the same trick going downwards: one falls by "
                "subtracting 5 each time, the other falls by halving.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe",
        "title": "Four moves, and the fourth one is only if the third fails",
        "steps": [
            {"label": "Write the list out with room between the numbers.",
             "detail": "You are about to write small workings in those gaps, so "
                       "leave them. Number the terms if the list is long — **the "
                       "first number is term 1.**"},
            {"label": "Subtract one pair: the later term minus the one before it.",
             "detail": "That order, every time. The answer you get is a candidate "
                       "for the common difference, and it is allowed to come out "
                       "negative.",
             "math": "4 - 2 = 2"},
            {"label": "Test a second pair somewhere else in the list.",
             "detail": "Not the same pair again. If the second subtraction gives "
                       "you the **same** number, the sequence is arithmetic and "
                       "that number is the common difference. Write it down and "
                       "stop.",
             "math": "6 - 4 = 2   →   arithmetic, common difference 2"},
            {"label": "If the two subtractions disagree, divide instead.",
             "detail": "Later term ÷ the one before it, and again test two pairs. "
                       "Matching answers mean the sequence is **geometric** and "
                       "that number is the common ratio. A question that already "
                       "tells you which kind it is — as both of today's examples "
                       "do — lets you skip straight to the right test.",
             "math": "8 ÷ 4 = 2   →   geometric, common ratio 2"},
        ],
        "after": "Then look at your answer beside the list and ask whether the two "
                 "agree. A list going **down** cannot have a positive common "
                 "difference, and a list of positive numbers that is **shrinking** "
                 "cannot have a common ratio bigger than 1. If yours does, you "
                 "almost certainly did the subtraction or the division backwards — "
                 "check that before you check anything else.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 98.1 — find the common difference",
        "equation": "a)  2, 4, 6, 8, 10, ...        b)  10, 5, 0, -5, -10, -15, ...",
        "steps": [
            {"label": "Look first",
             "text": "The question has already told you these are **arithmetic**, "
                     "so you are not deciding what kind of list it is. You are "
                     "finding one number. The book gives you the rule in a single "
                     "line: *the common difference is the same between each term "
                     "and the one before it.*"},
            {"label": "a) Step 1 · subtract one pair",
             "text": "Take the second term and subtract the first. Later minus "
                     "earlier, which is the order the rule just gave you.",
             "math": "4 - 2 = 2"},
            {"label": "a) Step 2 · test a second pair",
             "text": "The book's own word here is **test**, and it is a real "
                     "instruction. Pick a different pair and do it again. Same "
                     "answer, so 2 is the common difference — and now you know it "
                     "rather than suspecting it.",
             "math": "6 - 4 = 2   →   the common difference is 2"},
            {"label": "b) Step 3 · the same move on a list that falls",
             "text": "Nothing about the method changes when the numbers go "
                     "downwards. The 5 comes **after** the 10, so the 5 is the one "
                     "that goes first. If you catch yourself writing 10 - 5 "
                     "because it feels tidier, that is the mistake this whole step "
                     "exists to stop.",
             "math": "5 - 10 = -5"},
            {"label": "b) Step 4 · test a second pair, further along",
             "text": "The book skips down the list for its second test, which is a "
                     "good habit — a pattern that holds at both ends of a list is "
                     "much better evidence than two pairs sitting next to each "
                     "other. Here the term is -5 and the one before it is 0.",
             "math": "-5 - 0 = -5   →   the common difference is -5"},
            {"label": "b) Step 5 · read the sign, then walk the list",
             "text": "A **negative** common difference means the list goes down. "
                     "Adding -5 each time and taking 5 away each time are the same "
                     "instruction. Walk it once to be sure: start at 10, take 5 "
                     "away five times, and check you land on the -15 the book's "
                     "list ends at. Six numbers, five subtractions — the same "
                     "counting you are about to need in 98B. Notice that crossing "
                     "zero does nothing special — 5 - 5 is 0 and 0 - 5 is -5, and "
                     "the rule never flinches.",
             "math": "10 → 5 → 0 → -5 → -10 → -15      (six terms, five steps)"},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "98.2",
        "question": "Find the common ratio for the following geometric sequences: "
                    "a) 2, 4, 8, 16, 32, ...   b) 4, 2, 1, 1/2, 1/4, 1/8, ...",
        "steps": [
            {"label": "One word changes, and so does the operation",
             "text": "The book's rule for this one is the *same sentence* as before "
                     "with *difference* swapped for **ratio**: the common ratio is "
                     "the same between each term and the one before it. A ratio is "
                     "a division, so this time you divide — and the order is the "
                     "same as it was, later ÷ earlier."},
            {"label": "a) Divide one pair, then test a second",
             "text": "Two divisions, both giving 2, so the common ratio is 2. Look "
                     "back at Example 98.1a while this is in front of you: that "
                     "list also began 2, 4. Adding 2 and multiplying by 2 do "
                     "exactly the same thing to a 2 — which is why the third term "
                     "is the first place these two lists can be told apart.",
             "math": "4 ÷ 2 = 2   and   8 ÷ 4 = 2   →   the common ratio is 2"},
            {"label": "b) Same move, and the fractions do not change it",
             "text": "The list is falling, so expect a ratio smaller than 1. Start "
                     "with the easy pair: 2 divided by 4 is one half.",
             "math": "2 ÷ 4 = 1/2"},
            {"label": "b) The second test is a fraction divided by a fraction",
             "text": "The book picks the pair 1/4 and 1/2, which is the hardest one "
                     "in the list — so do it slowly. Dividing by a fraction means "
                     "**flip the one you are dividing by, then multiply**. Flip "
                     "1/2 and you get 2/1.",
             "math": "1/4 ÷ 1/2   →   1/4 × 2/1 = 2/4 = 1/2"},
            {"label": "Read both answers back to their lists",
             "text": "Both tests on b) give one half, so the common ratio there is "
                     "1/2. A ratio between 0 and 1 shrinks the list every step, and "
                     "multiplying by 1/2 is the same instruction as halving — which "
                     "is plainly what 4, 2, 1 is doing. Part a) does the opposite: a "
                     "ratio of 2 doubles the list every step, which is plainly what "
                     "2, 4, 8 is doing. Both answers agree with their own lists, so "
                     "you are done.",
             "math": "a) 2   ·   b) 1/2"},
        ],
        "answer": "a) 2   ·   b) 1/2",
    }),

    (B.KIND_MATH, {
        "display": "arithmetic:   term  -  the term before it        "
                   "geometric:   term  ÷  the term before it",
        "note": "That is the entire method of 98A. Two lines, and the second is the "
                "first with the operation swapped. Two things to hold on to about "
                "them. **The order is not negotiable** — later, then earlier — "
                "because subtraction and division both care which number comes "
                "first, and doing them backwards turns -5 into 5 and 1/2 into 2. "
                "And **you run each line twice**, on two different pairs, before "
                "you believe the answer.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "A series is the same list with plus signs in it",
        "paragraphs": [
            "Now 98B, and the definition is six words long: a series is **the "
            "indicated sum of a sequence**.",
            "*Indicated* means shown, written down, pointed at. `1 + 3 + 5 + 7 + 9` "
            "is a series whether or not anybody ever works out that it comes to 25. "
            "The series is the **adding-up written down**; the 25 is what you get "
            "when you do it.",
            "Saxon puts it more usefully than his own definition does, and prints "
            "the same sentence in both examples with only the kind-word changed: "
            "*an arithmetic series is like a sequence with plus signs between the "
            "numbers*, and then *a geometric series is like a sequence with plus "
            "signs between the numbers*. That is all that has happened. A series is "
            "not a new object you have to learn the shape of. It is a sequence and "
            "a decision to total it.",
            "So arithmetic and geometric mean exactly what they meant a minute ago. "
            "An arithmetic series is built by adding the common difference; a "
            "geometric series is built by multiplying by the common ratio. Only the "
            "last step — the totalling — is new.",
            "Here is what makes these questions feel harder than they are: **they "
            "do not hand you the list.** They hand you three things instead — a "
            "number to start at, a rule, and how many terms you want. Building the "
            "list is your job, and it is the first thing you do, before any plus "
            "sign is written down.",
            "And when you build it, count the **numbers you have written**, not the "
            "times you applied the rule. The starting number is already term 1. "
            "Five terms means the rule gets used **four** times.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Sequence is the list. Series is the total. So say the list out "
                "loud first — all of it, one number at a time, and count them on "
                "your fingers as you go. Only then start adding. Nearly every "
                "mistake in this half of the lesson is a list that got built wrong, "
                "or a list that got built one number too long.\"",
    }),

    (B.KIND_WORKED, {
        "number": "98.3",
        "question": "Find the sum of the first 5 terms of an arithmetic series that "
                    "begins with 1 and has a common difference of 2.",
        "steps": [
            {"label": "Notice what you were and were not given",
             "text": "There is no list in that sentence. There is a **start** (1), "
                     "a **rule** (add 2) and a **count** (5 terms). Three "
                     "ingredients, and the list is something you make out of them."},
            {"label": "Build the five terms, counting the numbers not the steps",
             "text": "The 1 is already term one, so you only add 2 four more times. "
                     "Write them in a row and count them: one, two, three, four, "
                     "five. Five numbers, four arrows.",
             "math": "1 → 3 → 5 → 7 → 9      (five terms, four steps)"},
            {"label": "Turn the sequence into a series",
             "text": "Plus signs between the numbers, exactly as the book says. "
                     "Nothing else changes and nothing gets re-ordered.",
             "math": "1 + 3 + 5 + 7 + 9 ="},
            {"label": "Add it the way the book does — friendly pairs first",
             "text": "Saxon does not go left to right. He takes 1 + 3 and 5 + 7, "
                     "which are two easy sums, and leaves the 9 waiting. Follow his "
                     "layout, because it is what is printed beside you and because "
                     "small sums go wrong less often than long ones.",
             "math": "1 + 3 + 5 + 7 + 9   →   4 + 12 + 9"},
            {"label": "Finish it",
             "text": "Two more additions and you are done. The answer to the "
                     "question is a single number, because a sum is a single "
                     "number.",
             "math": "4 + 12 + 9   →   16 + 9 = 25"},
            {"label": "A check, which is not a rule from your book",
             "text": "Your five terms are 1, 3, 5, 7, 9 and the middle one is 5. "
                     "Five terms, middle term 5, and 5 × 5 = 25 — the answer you "
                     "just got. Use it to check yourself, not to skip the adding — "
                     "and only on an **arithmetic** list with an **odd** number of "
                     "terms. Both words matter: odd, so there is a middle to find; "
                     "arithmetic, so the terms above the middle are as far above it "
                     "as the ones below are below, and they pair off. Try it on "
                     "Example 98.4 and it falls over — three terms, middle term 6, "
                     "3 × 6 = 18, but the sum is 26.",
             "math": "5 terms × middle term 5 = 25 ✓"},
        ],
        "answer": "25",
    }),

    (B.KIND_WORKED, {
        "number": "98.4",
        "question": "Find the sum of the first 3 terms of a geometric series that "
                    "begins with 2 and has a common ratio of 3.",
        "steps": [
            {"label": "Same question, different engine",
             "text": "Start (2), rule (**multiply** by 3), count (3 terms). The "
                     "only thing that has changed from 98.3 is that the rule "
                     "multiplies instead of adding — which is exactly the "
                     "difference between the two halves of 98A."},
            {"label": "Build the three terms",
             "text": "The 2 is term one, so the rule gets used twice: 2 × 3 is 6, "
                     "and 6 × 3 is 18. Three numbers, two arrows. Do not add the 3 "
                     "— a ratio is a division, so its opposite is a "
                     "multiplication.",
             "math": "2 → 6 → 18      (three terms, two steps)"},
            {"label": "Turn the sequence into a series",
             "text": "Plus signs between the numbers again. The book uses the same "
                     "sentence here that it used for the arithmetic one, with only "
                     "the word *geometric* swapped in, because it is the same "
                     "move.",
             "math": "2 + 6 + 18 ="},
            {"label": "Add, the book's way",
             "text": "2 + 6 is 8, and the 18 waits. Then one more addition.",
             "math": "2 + 6 + 18   →   8 + 18 = 26"},
            {"label": "Look at how fast that grew",
             "text": "The total you were asked for is 26. Three terms in and the "
                     "last one is already nine times the first. Two more terms "
                     "would put you at 162. That is the thing worth remembering "
                     "about geometric anything, and it is the same thing the "
                     "dog-walking pay did at the top of this page.",
             "math": "2 + 6 + 18 = 26      →      2, 6, 18, 54, 162, ..."},
        ],
        "answer": "26",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "This lesson is four sentences of definition and a lot of notation "
                 "that never gets explained. None of it is difficult; all of it is "
                 "assumed. Here is what each piece is short for.",
        "rows": [
            {"symbol": "...", "plain": "the list keeps going by the same rule — read "
                                       "it out loud as \"and so on\"",
             "example": "2, 4, 6, 8, 10, ..."},
            {"symbol": "term", "plain": "one number in the list. The starting number "
                                        "is TERM 1",
             "example": "in 1, 3, 5 the second term is 3"},
            {"symbol": "sequence", "plain": "numbers ordered so they form a definite "
                                            "pattern — a LIST",
             "example": "1, 3, 5, 7, 9"},
            {"symbol": "series", "plain": "the indicated sum of a sequence — the same "
                                          "list with plus signs in it",
             "example": "1 + 3 + 5 + 7 + 9"},
            {"symbol": "indicated", "plain": "written down and shown, whether or not "
                                             "you ever work it out",
             "example": "1 + 3 + 5 + 7 + 9 = 25"},
            {"symbol": "arithmetic", "plain": "the ADDING kind. Here it is an "
                                              "adjective (say it a-rith-MET-ic), not "
                                              "the word for doing sums",
             "example": "2, 4, 6, 8, 10"},
            {"symbol": "common difference", "plain": "what you ADD to get the next "
                                                     "term. Found by subtracting",
             "example": "-5"},
            {"symbol": "geometric", "plain": "the MULTIPLYING kind. Nothing to do "
                                             "with shapes, in spite of the name",
             "example": "2, 4, 8, 16, 32"},
            {"symbol": "common ratio", "plain": "what you MULTIPLY by to get the next "
                                                "term. Found by dividing",
             "example": "1/2"},
            {"symbol": "1/4 ÷ 1/2", "plain": "dividing by a fraction: flip the one "
                                             "you are dividing BY, then multiply",
             "example": "1/4 × 2/1 = 1/2"},
            {"symbol": "the first 5 terms", "plain": "five numbers, counting the "
                                                     "starting one — so the rule is "
                                                     "used four times",
             "example": "1, 3, 5, 7, 9"},
            {"symbol": "discrete", "plain": "separate countable numbers with gaps "
                                            "between them, not a smooth line "
                                            "(Lesson 75)",
             "example": "five dots, not a curve"},
        ],
        "after": "The one that catches people out loud is **arithmetic**. All your "
                 "life it has meant *doing sums*; here it is an adjective describing "
                 "a kind of list, and the stress even moves when you say it. "
                 "\"Arithmetic series\" does not mean \"a series you do arithmetic "
                 "on.\" It means **the kind that adds the same thing each time**.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Subtracting the pair backwards.",
             "wrong": "10, 5, 0, -5, ...   →   10 - 5 = 5   →   common difference 5",
             "right": "5 - 10 = -5   →   common difference -5",
             "note": "**5 instead of -5**, and the sign is the entire answer here. "
                     "The rule is *each term and the one before it* — later first. "
                     "There is a free check that costs one second: a list going "
                     "**down** cannot have a positive common difference. If your "
                     "answer and your list disagree about which way the numbers are "
                     "heading, you subtracted the comfortable way round."},
            {"name": "Testing one pair and stopping.",
             "wrong": "2, 4, 8, 16, 32   →   4 - 2 = 2   →   \"common difference 2\"",
             "right": "8 - 4 = 4, not 2   →   divide instead   →   4 ÷ 2 = 2, "
                      "8 ÷ 4 = 2   →   common ratio 2",
             "note": "Both of the book's own a) sequences begin **2, 4** — Example "
                     "98.1a is arithmetic and Example 98.2a is geometric, and the "
                     "first pair is identical in both. Nothing you can do to those "
                     "two numbers will tell them apart. That is why Saxon writes "
                     "*test some pairs* in both examples, and why the plural "
                     "matters."},
            {"name": "Counting the terms wrong.",
             "wrong": "begins with 1, difference 2, first 5 terms   →   "
                      "1, 3, 5, 7, 9, 11   →   36",
             "right": "1, 3, 5, 7, 9   →   25",
             "note": "**36 instead of 25.** The number you start at is already term "
                     "1, so five terms means you add the common difference **four** "
                     "times, not five. Count the numbers you have written down, "
                     "never the times you did the adding — and count them out loud, "
                     "touching each one."},
            {"name": "Adding the common ratio instead of multiplying by it.",
             "wrong": "begins with 2, ratio 3   →   2, 5, 8   →   15",
             "right": "begins with 2, ratio 3   →   2, 6, 18   →   26",
             "note": "**15 instead of 26.** This is the two halves of 98A getting "
                     "crossed. The word is the reminder: a **ratio** is a division, "
                     "so building the list with one is a multiplication. A "
                     "**difference** is a subtraction, so building with one is an "
                     "addition. Read which word the question used before you write "
                     "the second term."},
            {"name": "Answering with the list when the question asked for the total.",
             "wrong": "1, 3, 5, 7, 9",
             "right": "1 + 3 + 5 + 7 + 9 = 25",
             "note": "Not wrong mathematics — a wrong question answered correctly, "
                     "which is a strange way to lose a mark. **Sequence is the "
                     "list. Series is the sum.** The word *sum* in the question is "
                     "the instruction, and a sum is always one number."},
            {"name": "Multiplying instead of flipping, on a fraction ÷ a fraction.",
             "wrong": "1/4 ÷ 1/2   →   1/4 × 1/2 = 1/8",
             "right": "1/4 ÷ 1/2   →   1/4 × 2/1 = 2/4 = 1/2",
             "note": "**1/8 instead of 1/2.** Flip the fraction you are dividing "
                     "**by**, and only that one, then multiply. Check it against "
                     "the list rather than against your memory of the rule: the "
                     "ratio has to turn 1/2 into 1/4, and 1/2 × 1/2 does give "
                     "1/4 ✓, while 1/2 × 1/8 gives 1/16 ✗."},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "Graph the two lists and watch them come apart",
        "intro": "This is what **Lesson 68** meant. Along the bottom is *which "
                 "term* — first, second, third — and up the side is *the term "
                 "itself*. Plot Example 98.1a: **(1, 2), (2, 4), (3, 6), (4, 8), "
                 "(5, 10)**. Dots, not a line, because a sequence is discrete: "
                 "there is no term number two-and-a-half. Then press **x** and the "
                 "widget draws the true straight line through your dots.",
        "widget": "grid",
        # The window is stretched taller than it is wide on purpose. Example
        # 98.2a's fourth term is 16, and a 6-high grid would have asked her to
        # plot a point that is not on the paper. Its FIFTH term, 32, is off the
        # top even here — which is the point being made, so `table` holds only the
        # arithmetic five, and the geometric points are named in `after`.
        "config": {"view": {"xmin": -2, "xmax": 10, "ymin": -2, "ymax": 18},
                   "choices": ["x", "x^2", "a^x"],
                   "table": [[1, 2], [2, 4], [3, 6], [4, 8], [5, 10]],
                   "label": "plot a sequence, term number across and term up"},
        "after": "Two things will happen, and both are worth knowing about first. "
                 "**One:** when you press `x` the readout says the V shape `|x|` "
                 "fits your dots as well. It is right — you only plotted points on "
                 "the right-hand side, and over there a V and a straight line lie "
                 "on top of each other. A sequence has no term number zero and no "
                 "term number minus one, so the picture genuinely cannot rule the V "
                 "out. You can, and that is a limit of the graph rather than of "
                 "your answer. **Two:** now press **Clear** and plot Example 98.2a "
                 "instead — **(1, 2), (2, 4), (3, 8), (4, 16)** — then press "
                 "`aˣ (a>1)`. Same first two dots as before. Third one already "
                 "adrift, fourth one nearly off the top, and the fifth term, 32, "
                 "does not fit on this grid at all.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Both of the book's a) sequences begin 2, 4. Where do they part "
                  "company, and how far apart are they by the fifth term?",
        "answer": "**At the third term — and by the fifth they are 22 apart.** "
                  "Arithmetic, adding 2:   →   2, 4, 6, 8, 10   →   Geometric, "
                  "multiplying by 2:   →   2, 4, 8, 16, 32   →   32 - 10 = 22   →   "
                  "They agree on the first two terms and never agree again, because "
                  "adding 2 to a 2 and doubling a 2 both give 4 — the one place "
                  "these two rules cannot be told apart. Everything you do "
                  "afterwards depends on which of them you decided it was, which is "
                  "why the book makes you test **more than one pair** before you "
                  "commit.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A **sequence** is numbers put in an order that makes a definite "
            "pattern. Each number is a **term**, and the `...` promises the rule "
            "carries on.",
            "**Arithmetic**: each term is separated from the one before it by a "
            "**common difference**. Find it by **subtracting**.",
            "**Geometric**: each term is separated from the one before it by a "
            "**common ratio**. Find it by **dividing**.",
            "Both tests run **later, then earlier**. Backwards turns -5 into 5 and "
            "1/2 into 2 — a different list, going the other way.",
            "**Test more than one pair.** 2, 4, 6, 8 and 2, 4, 8, 16 start "
            "identically and are not the same kind of list.",
            "Check the answer against the list: falling list, negative difference; "
            "shrinking list of positive numbers, ratio between 0 and 1. "
            "Disagreement means you did the test backwards.",
            "A **series** is the **indicated sum** of a sequence — the same list "
            "with plus signs between the numbers.",
            "Series questions give you a start, a rule and a count, not a list. "
            "**Build the list first.** The starting number is term 1, so five terms "
            "means four steps.",
            "Sequence is the list; series is the total. Answer the question you "
            "were actually asked.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 98 first. If it didn't quite click, this is here to fix "
    "that — and there is graph paper near the bottom you can plot a sequence on. "
    "Two words today, and they are not the same word. A *sequence* is a list of "
    "numbers with a rule. A *series* is that list added up. Everything else in the "
    "lesson is subtracting, dividing and adding, which you have been doing for "
    "years."
)

PARENT_CONTENT = """## The big idea

Two halves, and they nest inside each other. **98A is a list. 98B is that list
added up.** Saxon's definitions are one line each — *sequence: numbers ordered in
a way that they form a definite pattern*; *series: the indicated sum of a
sequence* — and the page's own heading says **No New Rules**, which is true.
There is no formula anywhere in this lesson.

**98A — two kinds of list.** In an *arithmetic* sequence each term is separated
from the one before it by a **common difference**, found by subtracting. In a
*geometric* sequence each term is separated from the one before it by a **common
ratio**, found by dividing. The two rules are the same sentence with one word
swapped, and each word tells her which operation to use: a *difference* is a
subtraction, a *ratio* is a division.

Two things in that half are worth slowing down for.

**The order inside the test.** The rule says *between each term and the one
before it* — later minus earlier. On Example 98.1b (`10, 5, 0, -5, ...`) she must
write `5 - 10 = -5`, and the comfortable `10 - 5 = 5` gives the right size with
the wrong sign, which describes a list climbing while hers falls. The check is
free and worth teaching as a habit: *does my answer agree with which way the list
is going?*

**Why "test some pairs" is plural.** This is the nicest thing in the lesson and
Saxon does not point it out, so her page does. Example 98.1a is `2, 4, 6, 8, 10`
and Example 98.2a is `2, 4, 8, 16, 32`. **They begin with the same two numbers.**
One adds 2, one multiplies by 2, and on a 2 those are the same act. The third
term is the first place they can possibly be distinguished — so one pair is a
guess, and two pairs is a check. If she takes only one thing out of 98A, this is
the one that generalises.

**98B — series.** *Indicated sum* means the adding-up written down: `1 + 3 + 5 +
7 + 9` is the series, and 25 is what you get. Saxon's own working line is better
than his definition and he repeats it in both examples: *a series is like a
sequence with plus signs between the numbers.*

The difficulty in 98B is not the adding. It is that **the question does not give
her a list** — it gives a start, a rule and a count, and building the list is the
first move. Example 98.3 (begins with 1, difference 2, first 5 terms) is
`1, 3, 5, 7, 9` and then `1+3+5+7+9`. Note that the book adds it in friendly
pairs rather than left to right — `4 + 12 + 9`, then `16 + 9 = 25` — and her page
follows that layout so it matches what is printed beside her. Example 98.4
(begins with 2, ratio 3, first 3 terms) is `2, 6, 18`, then `8 + 18 = 26`.

And the counting: **the starting number is term 1.** Five terms means the rule is
applied four times. A child who counts her additions instead of her numbers gets
`1, 3, 5, 7, 9, 11` and answers 36.

Nothing in this lesson is a figure — both pages are text — so her page is missing
nothing from the book. The pictures in the practice set belong to the review
problems, not to Lesson 98.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Write `2, 4, ...` on a scrap of paper and ask: **"What comes next?"** Whatever
   she says — 6 or 8 — tell her she is right, and then write the other one. Both
   continue a perfectly good pattern. **That is the lesson**, delivered in fifteen
   seconds and by her rather than by you.
2. Now write both lists out: `2, 4, 6, 8, 10` and `2, 4, 8, 16, 32`. Ask:
   **"What is each one doing?"** You want "adding 2" and "doubling." Give her the
   two names then, not before — *arithmetic* for the adding kind, *geometric* for
   the multiplying kind — and the two tests: subtract to find a difference, divide
   to find a ratio.
3. Write `10, 5, 0, -5, -10`. Ask **"What is the common difference?"** and then
   wait for what she writes, not what she says. If `5` appears on the paper, ask
   the checking question rather than correcting her: **"Is this list going up or
   down?"** She will fix her own sign.
4. Switch halves with one sentence: **"Sequence is the list. Series is the
   total."** Then set her Example 98.3 out loud — *begins with 1, common
   difference 2, first five terms* — and make her write the **list** before any
   plus sign appears. Watch for that; it is the whole method.
5. When she has `1, 3, 5, 7, 9`, ask the two counting questions in this order:
   **"How many times did you add 2?"** (four) and **"How many numbers have you
   got?"** (five). Those two different answers are the mistake that costs the most
   in this lesson, and hearing herself say both makes it stick.

If she is lost in 98A, go back to step 1 and use two-number lists until she is
irritated by how ambiguous they are. That irritation is the point.

## The classic mix-ups, with the exact wrong answer each one produces

- **Subtracting backwards.** On 98.1b she writes `10 - 5 = 5` and answers **5**
  instead of **-5**. Fix: the sign has to agree with the direction of the list.
- **One pair and stop.** On `2, 4, 8, 16, 32` the first gap is 2, so she writes
  "common difference 2" — and the next gap is 4. Fix: two pairs, always; Saxon
  says *test some pairs* in both examples.
- **Counting the terms wrong.** On 98.3 she builds `1, 3, 5, 7, 9, 11` and answers
  **36** instead of **25**. Fix: the start is term 1; five terms, four steps.
- **Adding the ratio.** On 98.4 she builds `2, 5, 8` and answers **15** instead of
  **26**. Fix: a *ratio* is a division, so building with it is multiplication.
- **Answering with the list.** She writes `1, 3, 5, 7, 9` for 98.3 and stops. Not
  wrong, just not the question. Fix: *sum* means one number.
- **Fraction ÷ fraction.** On 98.2b she does `1/4 × 1/2 = 1/8` instead of
  `1/4 × 2/1 = 1/2`. Fix: flip only the one you are dividing by. Then check it
  forwards — the ratio has to turn 1/2 into 1/4.

## What to watch her do

Watch her **pencil**, in this order:

1. **Does the subtraction get written down, or done by eye?** Eyeballing the gaps
   works fine on `2, 4, 6, 8` and falls apart on `10, 5, 0, -5`. If nothing
   appears in the gaps between the numbers, she is guessing successfully, which
   lasts exactly until the numbers get unfriendly.
2. **Does she test a second pair without being asked?** This is the single most
   diagnostic thing on the page. One test is a habit that will eventually hand her
   a wrong answer with complete confidence.
3. **On the falling list, which number does she write first?** Watch the *order*
   she writes `5 - 10`, not just the answer. A child who writes the bigger number
   first and then fixes the sign at the end got it right today and will not
   tomorrow.
4. **On a series question, does a list appear before any plus signs?** You want
   to see `1, 3, 5, 7, 9` written out on its own line first. Jumping straight to
   adding means she is holding the list in her head, which is where terms go
   missing.
5. **Does she count her terms by touching them?** Watch for a finger or a pencil
   tip landing on each number. Counting in her head is how `first 5 terms` becomes
   six numbers.

Right answers are cheap in this lesson — the arithmetic is easy enough that she
can be right for the wrong reason all afternoon. The second test and the
written-out list are the two habits that survive a harder sequence.

## Extend it

- **The four problems that are actually this lesson**, with answers so you can
  check without solving: **198** `3, 8, 13, 18, 23, 28` → common difference **5**.
  **298** `1, 4, 16, 64, 256` → common ratio **4**. **398** begins 5, difference 1,
  five terms → `5+6+7+8+9` = **35**. **498** begins 2, ratio 2, three terms →
  `2+4+8` = **14**. Everything else in her practice set is review from other
  lessons.
- **Problem 1487 is Lesson 87's tree table again**, and she has already been
  taught it. *43 trees, 3-4 ft tall*: the `3 - 4'` row, and 43 falls in the
  `21 - 50` band, so `$22.95` each — `43 × 22.95` = **$986.85**. If she reaches
  for the `$26.95` in the left column, that is the "row with three prices" habit
  from Lesson 87 slipping, not a Lesson 98 problem.
- **Run the dog-walking bet for real.** Two columns on paper, thirty rows: $5 and
  a dollar more each day, against a penny doubled each day. She should find the
  crossover at day twelve herself. Then ask which column she would rather have
  been paid from — and make her total them, because the totals ($585 against
  $10,737,418.23) are a far bigger gap than the daily amounts, and *that* is why
  98B is a separate idea from 98A.
- **Ask for a sequence that is neither kind.** `1, 4, 9, 16, 25` — the squares —
  has a definite pattern and is neither arithmetic nor geometric: the differences
  go 3, 5, 7 and the ratios go 4, 2.25, 1.78. The book gives her the two most
  common kinds and does not say they are the only kinds, and noticing that gap
  herself is worth more than another practice problem.
- **Graph it.** Have her use the widget on her page, or plain graph paper: term
  number across, term up. The arithmetic sequence lands in a straight line — that
  is exactly what Lesson 68 was about — and the geometric one bends up and leaves
  the page. It is the fastest way to *see* the difference the whole lesson is
  built on.

## Where this sits

DIVE Lesson 98, *Sequences and Series*. Reviews **Lessons 5, 68 and 75**, and
unusually the book says what each one is for in its own body text.

- **Lesson 5** is where *sequence* was first defined, and 98 keeps that definition
  unchanged. Revisit it if the word itself is what she is stuck on.
- **Lesson 68** is where a sequence was used to recognise a linear pattern and
  graph it. Revisit it if you want the graphing extension above to land — it is
  the same idea, one lesson later, with a name attached.
- **Lesson 75** is the *why*: computers need discrete pieces of information. She
  saw 75 again in **Lesson 87** (bits, bytes, pixels), so that is the more recent
  handle if you need one.

Lessons 5 and 68 sit outside this course's seeded lessons and this guide has not
read them — everything said about them above comes from Lesson 98's own sentences
about them. Her book is the place to look if you want more.

**Proficient** looks like: finds a common difference or a common ratio when told
which kind of sequence it is, and can total a short series once the list is in
front of her.
**Mastered** looks like: tests a second pair without being reminded, gets the sign
right on a falling list, builds the list before adding, and does not confuse the
sequence with the series when the question asks for one of them.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 98 (sequences and series) — idempotent.")

    LESSON_NUMBER = 98
    TITLE = "Sequences and Series — A List With a Rule, and the Total of the List"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
