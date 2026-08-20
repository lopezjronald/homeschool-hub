"""Saxon Pre-Algebra Lesson 93 — Interest Rate, Savings and Debt.

Reviews Lessons 5, 35, 81, 89 and 90. **Lesson 90 is the hook**, and specifically
90B: that lesson introduced equations carrying more than one letter and had her
push the letters around. Lesson 93 hands her another one — F = P(1 + rt) — but
pointed the other way: three of the four letters arrive with numbers attached, so
the job is substitute-and-evaluate, which is the step 90B said it was leaving out
(90's own text: "Problems from this lesson will probably seem easier than Lesson
78B, because they don't involve the evaluate step"). Lesson 89 (limits) is kept
warm by Practice Set 93 — problem 789 is a limit on a discontinuous function —
not because interest needs it; Lesson 81 (logic; What is Calculus?) has no
problem of its own in this set. Problems 492 and 690, a derivative and a rate of
change, are Lessons 92 and 90. Lessons 5 and 35 sit outside this course's seeded
lessons and this guide has not read them, so nothing here claims what is in them.

Two halves, as the book has them, sitting under the page's Rules box (which prints
F = P(1 + rt) first) and the Definitions box directly beneath it — that order is the
DIVE template and the child's page states it. 93A is the savings-and-debt section
and contains no arithmetic at all; it is reported as the book states it, with its
four passages and its own two conclusions, because Practice Set problem 193 examines
it. 93B is
the simple interest formula, worked through Examples 93.1 and 93.2.

Judgement calls, all three disclosed on the child's page as well:

* The book's line on Ex. 93.2 — "three times more than what he paid for it" — is
  about the TOTAL: $15,000 is three times the $5,000 price. Her page keeps the
  book's sentence and then separates the two numbers explicitly ($5,000 of
  controller, $10,000 of interest), because "answered with the interest instead of
  the total" is one of the five errors and the split has to be said out loud once.
* `F = P(1 + rt) = P + Prt` is a distributive restatement the book never writes.
  It is on the page as one MATH block because it is the only thing that explains
  the 1, and the 1 is where the total-versus-interest confusion lives.
* The chart tool runs the book's own Ex. 93.1 numbers at t = 0, 1, 2, 3, 4 and 5
  rather than only at 5 — six dots, the first being the $1,000 before any interest.
  Nothing is invented — same P, same r, same formula — and the intro says so. It
  exists to make "simple" visible: equal steps, straight line, because the rate is
  always taken on P.

The teaching pages of Lesson 93 are entirely text — no diagram, chart or
screenshot — so unlike Lessons 86 and 87 nothing had to be left out or rebuilt.
(Several PRACTICE problems reference printed graphs, but those are review of
earlier lessons and are worked from her book.)

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_93 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

# Example 93.1's own numbers — P = 1000, r = 0.08 — run at t = 0 through 5 instead
# of only at t = 5. Same formula, same figures: 1000(1 + 0.08(1)) = 1080, and so on
# up to the book's own 1400. The point of drawing it is that the steps are equal.
SAVINGS = [
    {"label": "start", "value": 1000},
    {"label": "1 yr", "value": 1080},
    {"label": "2 yr", "value": 1160},
    {"label": "3 yr", "value": 1240},
    {"label": "4 yr", "value": 1320},
    {"label": "5 yr", "value": 1400},
]

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 93 · Pre-Algebra",
        "title": "Interest is rent on money",
        "thesis": "Money that is not yours costs money. This one formula prices "
                  "it — **how much you started with, what fraction gets added each "
                  "year, and how long it sits there** — and it does not care "
                  "whether the money is growing for you or piling up against you.",
        "formula": "F = P(1 + rt)",
        "roles": [
            {"tone": "start", "name": "P — the only real money in the formula",
             "text": "The principal: what you put in, or what you borrowed. "
                     "Everything else in the line is a rule about what happens to "
                     "it. Find P first, every time."},
            {"tone": "move", "name": "rt — how much rent, for how long",
             "text": "Rate times time, multiplied together before anything else. On "
                     "its own, rt is the *fraction of P that gets added*. When rt "
                     "comes out 0.4 you are adding four tenths of your money; when "
                     "it comes out 2 you are adding twice your money."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why money costs money",
        "paragraphs": [
            "Say you earn $50 in a week and you owe somebody $30. The arithmetic is "
            "not hard: 50 - 30 = 20, and $20 is what you actually have. Your book "
            "opens its second half, 93B, with that exact sum, because it is the "
            "simplest money problem there is.",
            "Change it a little. You pay the $30 back at $10 a week for three weeks. "
            "Still easy, but it is not one subtraction any more — it has a shape, "
            "and it lasts a while.",
            "Change it once more. You never had the $30. You **borrowed** it, and "
            "the person who lent it wants more than $30 back. That extra is called "
            "**interest**, and it is where money arithmetic stops being obvious.",
            "Why should anyone get extra just for waiting? Because while their $30 "
            "is in your pocket it is not in theirs — they cannot spend it, lend it "
            "or save it. The extra is what they charge for going without. Interest "
            "is **rent**. You are renting somebody's money, and rent is charged by "
            "the year.",
            "That runs in both directions, which is the part worth holding on to. "
            "Put money in a savings account and you are the one lending — the bank "
            "pays *you* rent. Put a purchase on a credit card and you are the one "
            "borrowing, and you pay. Same formula. Opposite end of it.",
            "In **Lesson 90** you met equations carrying more than one letter and "
            "learned to push the letters around without ever knowing what they were "
            "worth. This lesson hands you one of those — four letters — and then "
            "tells you three of them. Filling them in is the whole job.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "Your book says something first, before it does any arithmetic",
        "paragraphs": [
            "Lesson 93 has its Rules box at the top of the page, but the lesson "
            "itself does not start with arithmetic. It starts with four passages "
            "about money, and there is nothing to calculate in that whole section. "
            "Read it anyway — practice problem 193 asks you about it directly.",
            "Here is what the book cites, in its own order. **Exodus 22:25-27** — "
            "lend money to a poor person, and expect to be paid back, but do not "
            "charge them interest for it. **Psalm 37:21** — wicked people borrow and "
            "do not pay it back. **Proverbs 22:7** — a borrower is like a slave to "
            "the one he owes money to. **Luke 16:13** — you cannot serve both God "
            "and money.",
            "From those the book draws two conclusions: do not steal, which is the "
            "8th Commandment, and do not serve money over God — **either as a debtor "
            "or as a wealthy person**. Notice that the second one points at both "
            "ends. Owing too much and having a great deal are both listed as ways to "
            "get this wrong.",
            "Then it says what it is actually for. Ideally you want more money "
            "coming in than going out, and the reason given is not comfort: it is so "
            "you can care for your own family **and** for other people "
            "(Philippians 2:4). Missionary work costs money. Being able to work, "
            "earn, and have enough left over to share is described as a blessing, "
            "not an achievement.",
            "None of those four passages is about arithmetic. Every one of them is "
            "about what money does to a person — three of the four about owing, and "
            "**Luke 16:13** about wanting. **Proverbs 22:7** is the sentence "
            "the rest of the lesson is really about — and Example 93.2 is about to "
            "put a number on it.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "Two definitions, and both of them face both ways",
        "paragraphs": [
            "The book prints the formula in its Rules box and then, immediately "
            "underneath, gives you two words — and each one is carefully worded to "
            "cover saving *and* owing at the same time. "
            "That is not an accident — read them slowly.",
            "**Interest rate:** a rate which is *charged or paid* for the use of "
            "money or other goods. Charged or paid. Somebody is always doing each. "
            "It is usually given for a year at a time — 10% per year, for example — "
            "and that yearly habit is why **t is measured in years** in every "
            "problem you will meet here.",
            "**Principal:** the same thing as a present sum — the initial amount "
            "*invested or owed*. Invested or owed. Again both directions, and again "
            "one letter covers both: it is **P** either way.",
            "So Example 93.1 puts $1,000 into a savings account and Example 93.2 "
            "puts $5,000 onto a credit card, and the two problems are worked with "
            "the identical line of algebra. Nothing in the formula knows which one "
            "you are doing. The only difference is which way the money is pointing "
            "and, therefore, whether the answer is good news.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Before you write a single number down, tell me two things about "
                "this problem. Whose money is it — yours sitting in a bank, or "
                "somebody else's sitting in your pocket? And how long is it going to "
                "sit there? Good. Now the percent — say it to me as a decimal, and "
                "write that down before you write anything else.\"",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "start",
        "title": "Four letters, and the problem hands you three of them",
        "paragraphs": [
            "The formula is `F = P(1 + rt)`, and it finds the **future worth** of a "
            "sum you have now.",
            "**F** is the future sum — what the money grows to, or what you end up "
            "owing. It is what nearly every problem asks for. **P** is the present "
            "sum, also called the principal. **r** is the interest rate. **t** is "
            "the time, in years.",
            "The book puts it in a way worth copying: you are solving for F, *which "
            "means the problem must give you values for P, r and t*. The letter you "
            "want tells you which letters to go hunting for in the sentence. Go and "
            "find those three before you write anything else, and the rest is "
            "arithmetic.",
            "Now the thing that is easy to miss. The Rules line says **r is the "
            "interest rate in decimal form**. Not 8 — **0.08**. This is the single "
            "most common way to get a wrong answer in this lesson, and it does not "
            "look like an error while you are making it. Write the decimal down the "
            "moment you read the percent.",
            "And the **1** inside the parentheses. It is there because F is the "
            "*total* at the end, and the total includes the money you already had. "
            "Read the formula in English: **keep all of what you started with — "
            "that is the 1 — and add rt of it on top.** Take the 1 away and you "
            "would be calculating only the extra.",
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "This lesson is four letters and one percent sign. Here is what "
                 "each mark is short for — including the two the book states in its "
                 "Rules box and then never repeats.",
        "rows": [
            {"symbol": "F", "plain": "the future sum — what the money grows to, or "
                                     "what you end up owing. Usually the answer",
             "example": "F = $1,400"},
            {"symbol": "P", "plain": "the present sum, also called the PRINCIPAL — "
                                     "what you deposited or what you borrowed",
             "example": "P = $1,000"},
            {"symbol": "r", "plain": "the interest rate, in DECIMAL form, never as a "
                                     "percent",
             "example": "8%  →  r = 0.08"},
            {"symbol": "t", "plain": "the time — in YEARS in every problem in this "
                                     "course, because rates are quoted per year",
             "example": "t = 5"},
            {"symbol": "rt", "plain": "rate times time. One multiplication, and it "
                                      "happens first. It is the fraction of P that "
                                      "gets added",
             "example": "0.08 × 5 = 0.4"},
            {"symbol": "1 + rt", "plain": "all of your own money (the 1) plus the "
                                          "extra. Multiply P by this and you have "
                                          "the total",
             "example": "1 + 0.4 = 1.4"},
            {"symbol": "%", "plain": "per hundred. To get r, move the decimal point "
                                     "TWO places to the left",
             "example": "20%  →  0.20"},
            {"symbol": "simple interest", "plain": "interest worked out on the "
                                                   "starting sum only, so the same "
                                                   "amount is added every year",
             "example": "$80 a year on $1,000 at 8%"},
            {"symbol": "(C)", "plain": "calculator allowed on this problem. Both "
                                       "worked examples are marked with it",
             "example": "293. (C) Estimate the future sum..."},
        ],
        "after": "The two that get mixed up are **r** and the percent it came from. "
                 "`8%` and `0.08` are the same size of thing written two ways, and "
                 "only one of them may go into the formula. A useful habit: write "
                 "`r = 0.08` on its own line as soon as you read the word *percent*, "
                 "before you have decided anything else about the problem.",
    }),

    (B.KIND_MATH, {
        "display": "F = P(1 + rt)   =   P  +  Prt",
        "note": "The book writes the short version and never multiplies it out. The "
                "long version is here because it shows you **where the money is**: "
                "the `P` on its own is your own money coming back, and `Prt` is the "
                "interest by itself. For Example 93.1 that reads "
                "1000 + 1000(0.08)(5) = 1000 + 400, and there is the **$400** of "
                "interest standing on its own, next to the $1,000 that was always "
                "yours. You never have to write this line. You do have to know which "
                "half of your answer is which.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Five moves, and four of them happen before "
                                      "the formula does",
        "steps": [
            {"label": "Say which letter the question is asking for.",
             "detail": "*Future sum*, *what will it be worth*, *how much would he "
                       "owe* — all three mean **F**. Naming it first is what tells "
                       "you the other three letters have to be somewhere in the "
                       "sentence."},
            {"label": "Write P, r and t down the side of the page.",
             "detail": "Three short lines before the formula appears at all. The "
                       "words that point at them are fairly consistent: *present "
                       "value* or a price tag for P, a percent for r, and *for how "
                       "many years* or *over a ... year period* for t.",
             "math": "P = 1000   ·   r = 8%   ·   t = 5"},
            {"label": "Turn the percent into a decimal. Now, not later.",
             "detail": "Two places to the left, every time. This is the step that "
                       "decides whether the whole problem is right, and it takes "
                       "about a second, which is exactly why it gets skipped.",
             "math": "8% → 0.08      20% → 0.20      6% → 0.06"},
            {"label": "Check the time really is in years.",
             "detail": "Your book uses years in every problem, and the rates are "
                       "quoted per year, so the two match without you doing "
                       "anything. If a question ever hands you months, the rate is "
                       "still per year — convert the months before you use them."},
            {"label": "Substitute, then work from the inside out.",
             "detail": "`rt` first, because it is inside the parentheses and it is a "
                       "multiplication. Then add the 1. Then multiply the whole "
                       "bracket by P. Round only if the question told you to.",
             "math": "rt  →  1 + rt  →  P(1 + rt)"},
        ],
        "after": "Then check the **size** of your answer before you check the "
                 "arithmetic. F is never smaller than P — you cannot pay rent on "
                 "money and end up with less than you started, and nobody borrows "
                 "money and owes less afterwards. So an answer smaller than P means "
                 "something has gone wrong somewhere, and an answer many times "
                 "bigger than P usually means the percent went in as a whole "
                 "number. It is a good check and a rough one. A percent that went in "
                 "only a little wrong produces an answer that sails straight through "
                 "it, which is why the decimal gets written down first rather than "
                 "checked for afterwards.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 93.1 — $1,000 in a savings account at 8% for five years",
        "equation": "F = P(1 + rt)      ·      estimate the future sum",
        "steps": [
            {"label": "Look first",
             "text": "The question wants the **future sum**, which is F. Follow the "
                     "book's own reasoning here, because it is a habit and not just "
                     "a step: *we are solving for F, which means the problem must "
                     "give values for P, r and t*. So they are in the sentence "
                     "somewhere. Go and get them."},
            {"label": "Step 1 · pull the three numbers out of the sentence",
             "text": "*Present value* is P. The *8% interest rate* is r, and it goes "
                     "in as a decimal. *For 5 years* is t. Three facts, three "
                     "letters, and the sentence contains nothing else you need.",
             "math": "P = 1000   ·   r = 8% = 0.08   ·   t = 5"},
            {"label": "Step 2 · write the formula, then substitute into it",
             "text": "Formula first, in letters, before any numbers touch it. Then "
                     "each letter is replaced by its number in place. Doing it in "
                     "that order is what stops a number landing in the wrong slot.",
             "math": "F = 1000(1 + 0.08(5))"},
            {"label": "Step 3 · rt first",
             "text": "Inside the parentheses, and it is a multiplication, so it goes "
                     "before the addition. Look at what 0.4 is telling you: over the "
                     "five years you will add **four tenths of your money**.",
             "math": "0.08 × 5 = 0.4   →   F = 1000(1 + 0.4)"},
            {"label": "Step 4 · add the 1",
             "text": "1.4 is the whole story in one number: all of what you put in, "
                     "plus another four tenths of it. Anything you multiply by 1.4 "
                     "comes out 40% bigger.",
             "math": "F = 1000(1.4)"},
            {"label": "Step 5 · multiply by P",
             "text": "One multiplication and the problem is finished.",
             "math": "1000 × 1.4 = 1400   →   F = $1,400"},
            {"label": "Step 6 · read your own answer back",
             "text": "Of that $1,400, **$1,000 was always yours** and **$400 is the "
                     "interest** the bank paid you for leaving it alone. Say both "
                     "numbers out loud. The question asked for the total, so $1,400 "
                     "is the answer — but knowing which part is which is what keeps "
                     "you from answering $400 to a question like this one.",
             "math": "1000 + 400 = 1400"},
            {"label": "One honest note about the word *estimate*",
             "text": "The question says *estimate*, and then the arithmetic comes out "
                     "exact. That is not a contradiction. Your book says plainly "
                     "that this is a very basic interest formula and that there are "
                     "more complex ones it will not cover. The estimate is the "
                     "**formula**, not your sum. Real accounts do a slightly "
                     "richer thing, so treat $1,400 as a good, honest approximation "
                     "of what five years does — which is exactly what the book "
                     "claims for it."},
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Which words in the question point at which letter — both of the "
                   "lesson's examples, side by side",
        "headers": ["the words in the problem", "letter", "Example 93.1",
                    "Example 93.2"],
        "rows": [
            {"cells": ["\"present value of\" · the price of the thing bought", "P",
                       "$1,000", "$5,000"], "emphasis": True},
            {"cells": ["\"at an 8% interest rate\" · \"at an interest rate of 20%\"",
                       "r", "8% = 0.08", "20% = 0.20"], "emphasis": True},
            {"cells": ["\"for 5 years\" · \"over a 10 year period\"", "t", "5", "10"]},
            {"cells": ["rate times time — you work this one out", "rt", "0.4", "2"]},
            {"cells": ["\"the future sum\" · \"how much would he owe\"", "F",
                       "$1,400", "$15,000"]},
        ],
        "note": "Read the **rt** row and you can see the whole difference between a "
                "savings account and a credit card without doing any arithmetic. In "
                "93.1 rt is **0.4**, so four tenths of the money is added. In 93.2 "
                "rt is **2**, so *twice* the money is added on top of itself. A "
                "higher rate for longer years, and the same formula turns from a "
                "pleasant surprise into a bad one.",
    }),

    (B.KIND_WORKED, {
        "number": "93.2",
        "question": "(C) To help him pay for a $5,000 gold-plated video game "
                    "controller, Goofball charged it to his credit card at an "
                    "interest rate of 20%. How much would Goofball owe if he paid "
                    "off the charge over a 10 year period? Assume simple interest "
                    "and round to the nearest dollar.",
        "steps": [
            {"label": "Find the three numbers, exactly as before",
             "text": "The price of the controller is the amount he borrowed, so it "
                     "is **P**. The card's 20% is **r**, as a decimal. The ten years "
                     "is **t**. Nothing about being in debt changes where the "
                     "numbers live in the sentence.",
             "math": "P = 5,000   ·   r = 20% = 0.20   ·   t = 10"},
            {"label": "Same formula. Genuinely the same one.",
             "text": "This is the point of the two definitions at the top of the "
                     "lesson. *Charged or paid*; *invested or owed*. The formula has "
                     "no idea which side of the deal you are on, so you write the "
                     "identical line you wrote for the savings account.",
             "math": "F = P(1 + rt)"},
            {"label": "Substitute and work from the inside out",
             "text": "rt first: 0.2 times 10. Then the 1. Then multiply by P. Three "
                     "lines, and the middle one is worth staring at — the bracket "
                     "comes out **3**.",
             "math": "F = 5,000(1 + 0.2(10))   →   F = 5,000(1 + 2)   →   "
                     "F = 5,000(3) = $15,000"},
            {"label": "Notice what rt did this time",
             "text": "rt = 2. That does not mean *a bit more*. It means the interest "
                     "alone is **twice the price of the thing he bought**, because a "
                     "high rate ran for a long time. In 93.1 rt was 0.4. Same "
                     "formula, and the answer changed character completely.",
             "math": "0.2 × 10 = 2"},
            {"label": "Split the answer into its two parts",
             "text": "Your book's line is: *look at how much money Goofball owes, "
                     "three times more than what he paid for it.* Three times is the "
                     "**total** — $15,000 against a $5,000 price. Now split it: "
                     "$5,000 of that is the controller, and **$10,000 is interest**, "
                     "which is twice what the controller cost. He paid $10,000 for "
                     "the privilege of not waiting.",
             "math": "$15,000 - $5,000 = $10,000 of interest"},
            {"label": "Why 'round to the nearest dollar' is in the question",
             "text": "It is a standing instruction on money problems, not a warning "
                     "that this one is about to get messy. Nothing here needs "
                     "rounding — this answer comes out exact. So does practice "
                     "problem 393, which is this same problem with different "
                     "numbers. If your answer there arrives in whole dollars with "
                     "nothing left over, that is not a sign you have done something "
                     "wrong. The instruction is on the question because most money "
                     "problems are not this tidy, not because this one isn't."},
            {"label": "The book's own conclusion, which is the reason for 93A",
             "text": "Some people think that because they have a credit card they "
                     "have free money. They do not. When you charge something to a "
                     "card, **you are borrowing other people's money**, and every "
                     "card charges high interest if you do not pay it back quickly. "
                     "Then Proverbs 22:7 from the first half of the lesson stops "
                     "being an abstract sentence, because you have just calculated "
                     "what it costs. Your book puts it more briefly: do not be like "
                     "Goofball."},
        ],
        "answer": "$15,000",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "move",
        "title": "Why it is called *simple* interest",
        "paragraphs": [
            "There is a reason the word *simple* is sitting in front of *interest*, "
            "and it is not that the sums are easy.",
            "The rate is always taken on **P** — the sum you started with — and P "
            "never changes. So the same amount of money gets added every single "
            "year. Eight percent of $1,000 is $80, and it is $80 in year one, $80 in "
            "year five, $80 in year fifty. Five of them is the $400 you already "
            "found.",
            "That is what makes the chart below a **straight line** rather than a "
            "curve. Equal steps, one per year. If you can predict every dot on that "
            "chart before you look at it, you have understood the formula, because "
            "there is nothing else in it.",
            "Your book is careful to add that this is a very basic formula and that "
            "there are more complex ones it is not going to cover. Those are the "
            "ones where last year's interest starts earning interest of its own, so "
            "the steps stop being equal and the line starts to bend. You are not "
            "asked for that here and you should not try to use it. But it is worth "
            "knowing which way it bends: it makes savings grow **faster** than this "
            "and debts grow **faster** than this. Simple interest is the gentle "
            "version of both.",
        ],
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Putting the percent in as a whole number.",
             "wrong": "F = 1000(1 + 8(5)) = 1000(41) = $41,000",
             "right": "F = 1000(1 + 0.08(5)) = 1000(1.4) = $1,400",
             "note": "**$41,000 instead of $1,400.** The Rules box says it in eight "
                     "words — *r is the interest rate, in decimal form* — and this "
                     "is the mistake that ignores it. The tell is that the answer is "
                     "absurd, so it is easy to catch **if you look**. Ask whether "
                     "any bank would turn $1,000 into $41,000 in five years."},
            {"name": "Copying the 0.08 pattern onto a two-digit percent.",
             "wrong": "20% → 0.02   →   F = 5,000(1 + 0.02(10)) = 5,000(1.2) = $6,000",
             "right": "20% → 0.20   →   F = 5,000(1 + 0.2(10)) = 5,000(3) = $15,000",
             "note": "**$6,000 instead of $15,000** — and unlike the one above, this "
                     "answer looks completely reasonable, which is what makes it the "
                     "expensive one. It comes out of a habit that works right up "
                     "until it doesn't: 8% became 0.08 and 6% became 0.06, so the "
                     "rule feels like *write the digits after a zero* — and that "
                     "rule turns 20% into 0.02. The real rule is **two places to the "
                     "left**, which puts 20% at **0.20**, twenty hundredths. Check "
                     "any rule you are carrying against something you already know: "
                     "50% must come out 0.5, because half of a hundred dollars is "
                     "fifty dollars. If your rule gives 0.05 for 50%, the rule is "
                     "wrong."},
            {"name": "Adding before multiplying inside the parentheses.",
             "wrong": "1 + 0.08 = 1.08   →   1.08 × 5 = 5.4   →   1000(5.4) = $5,400",
             "right": "0.08 × 5 = 0.4   →   1 + 0.4 = 1.4   →   1000(1.4) = $1,400",
             "note": "**$5,400 instead of $1,400.** `1 + rt` means *one plus (r times "
                     "t)*, not *(one plus r) times t*. There is no visible bracket "
                     "around rt because multiplication does not need one — it goes "
                     "first anyway. Write the rt product on its own line before you "
                     "touch the 1 and this cannot happen to you."},
            {"name": "Answering with the interest instead of the total.",
             "wrong": "1000 × 0.08 × 5 = $400",
             "right": "F = 1000(1 + 0.08(5)) = $1,400",
             "note": "**$400 instead of $1,400** — the interest is right, the "
                     "question was different. This is the 1 doing its job: F is what "
                     "you *end up with*, and that includes the money you already "
                     "had. The same slip on Goofball answers **$10,000** for a "
                     "question whose answer is **$15,000**. Both numbers are worth "
                     "knowing. Answer the one you were asked for."},
            {"name": "Leaving the time in months.",
             "wrong": "6 months at 8% on $1,000   →   t = 6   →   1000(1 + 0.48) = "
                      "$1,480",
             "right": "6 months at 8% on $1,000   →   t = 0.5   →   1000(1 + 0.04) = "
                      "$1,040",
             "note": "This one is not in your book — every problem it gives you is "
                     "already in years — and it is here because the Rules box goes "
                     "out of its way to warn you that time *can* have other units. "
                     "An interest rate is quoted **per year**, so t has to be "
                     "counted in years to match it. Six months is half a year, so t "
                     "is 0.5, and using 6 makes the money sit there twelve times too "
                     "long."},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "Five years, one straight line",
        "intro": "This is Example 93.1's own money — $1,000 at 8% — with the same "
                 "formula run at t = 0, 1, 2, 3, 4 and 5 instead of only at 5. Six "
                 "dots: the first is the $1,000 before any interest has been added, "
                 "and the other five are the years. Nothing new has been put in — "
                 "1000(1 + 0.08(1)) is 1080, 1000(1 + 0.08(2)) is 1160, and the last "
                 "dot is the book's own $1,400. Use the buttons to switch between "
                 "the line and the bars.",
        "widget": "chart",
        # kinds is ["line", "bar"] and nothing else. The line is the one that carries
        # the lesson's point — equal steps make a straight line — and the bar chart is
        # there as the second reading of the same numbers, the way Lesson 74 taught
        # her to expect. A pie or a pictograph would be the wrong shape for money over
        # time and would just be decoration.
        "config": {
            "data": SAVINGS,
            "kinds": ["line", "bar"],
            "label": "$1,000 at 8% simple interest, year by year",
        },
        "after": "Two things to do with it. **One:** look at the gap between one dot "
                 "and the next, then check the next gap along. They are the same, "
                 "and that is why the dots make a straight line instead of a curve. "
                 "**Two:** read the last dot — it is $1,400, which is the answer you "
                 "worked out by hand. The drop-down below asks you *how much* the "
                 "gap is and why it never changes. Say your answer out loud before "
                 "you open it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "How much does the balance go up in each of the five years — and "
                  "why is it exactly the same every year?",
        "answer": "**$80 a year, five years running, which is the $400.**   →   "
                  "0.08 × 1000 = 80   →   80 × 5 = 400   →   1000 + 400 = 1400   "
                  "→   The reason it never changes is that the rate is always taken "
                  "on **P**, the money you started with, and P is a fixed number "
                  "that nothing in this lesson ever updates. Year four does not earn "
                  "interest on the $240 that has piled up by then; it earns interest "
                  "on the original $1,000, same as year one did. That is precisely "
                  "what the word *simple* is doing in *simple interest* — and it is "
                  "why `rt` can be one small multiplication instead of five separate "
                  "ones.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "Interest is **rent on money**. Somebody is always paying it and "
            "somebody is always collecting it.",
            "**F = P(1 + rt).** F is the future sum, P is the present sum (the "
            "principal), r is the rate, t is the time.",
            "**r goes in as a decimal.** 8% is 0.08, 20% is 0.20. Two places left, "
            "and write it down the moment you read the percent.",
            "**t is in years**, because interest rates are quoted per year.",
            "`rt` is one multiplication and it happens **first** — it is inside the "
            "parentheses. `1 + rt` means one plus (r times t).",
            "The **1** is your own money coming back. F is the total, not the "
            "interest. The interest by itself is F - P.",
            "The formula does not know whether you are saving or borrowing. "
            "Examples 93.1 and 93.2 are the same line of algebra pointed in opposite "
            "directions.",
            "**Simple** interest means the rate is always taken on P, so the same "
            "amount is added every year — equal steps, straight line.",
            "$1,000 at 8% for 5 years is **$1,400** ($400 of it interest). $5,000 at "
            "20% for 10 years is **$15,000** ($10,000 of it interest). Look at the "
            "second one again, and remember which of the two you would rather be.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 93 first. If it didn't quite land, this is here to fix that "
    "— and there's a chart near the bottom you can switch between two shapes. Two "
    "halves today, and the first has no arithmetic in it at all: what your book says "
    "about savings and debt. The second is one formula, F = P(1 + rt), and the most "
    "common way it goes wrong is at the percent sign."
)

PARENT_CONTENT = """## The big idea

Two halves, and only one of them is mathematics.

**93A — savings and debt.** After the Rules and Definitions boxes, the lesson proper
opens with four passages and no arithmetic at all: **Exodus 22:25-27** (lend to a
poor person and expect repayment, but do not charge interest),
**Psalm 37:21** (the wicked borrow and do not repay),
**Proverbs 22:7** (a borrower is like a slave to the lender) and **Luke 16:13** (you
cannot serve both God and money). From those the book draws two conclusions — do not
steal, and do not serve money over God *either as a debtor or as a wealthy person* —
and then makes a positive case: more coming in than going out is what lets a family
care for itself **and** for other people (Philippians 2:4), missionary work
included. Practice problem 193 is a multiple-choice question straight out of this
section, so it does get examined. Her page reports all of it in the book's own
order. Worth reading the four passages out of your own Bible with her rather than
the paraphrase, because Proverbs 22:7 is the one Example 93.2 then puts a price on.

**93B — the simple interest formula.** One rule: **F = P(1 + rt)**, where F is the
future sum, P is the present sum (the *principal*), r is the rate **in decimal
form**, and t is the time **in years**. Two worked examples, both marked (C).

The whole lesson has one dominant difficulty and it is not the algebra. It is
`8% → 0.08`. Three of the five errors in the list below are downstream of a percent
that went in wrong or an order-of-operations slip inside the parentheses; the other
two — answering with the interest instead of the total, and leaving the time in
months — are not, and no amount of care with the percent will catch them. If she
writes `r = 0.08` on its own line before she does anything else, the two that come
from the percent cannot happen to her, and the lesson gets a great deal shorter.

Three things her page says out loud that are worth knowing about in advance:

- **The "three times more" line.** On Ex. 93.2 the book exclaims that Goofball owes
  *three times more than what he paid for it* — that is about the **total**:
  `$15,000` against a `$5,000` price. Her page keeps the book's sentence and then
  splits the answer: `$5,000` of controller, `$10,000` of interest. The split has to
  be said once, because "answered with the interest instead of the total" is a real
  error and the two numbers are both worth knowing.
- **`F = P(1 + rt) = P + Prt`.** The book never multiplies it out. Her page does it
  once, in a single box, because it is the only thing that explains the `1`: the
  lone `P` is her own money coming back and `Prt` is the interest standing on its
  own. She is not asked to write it that way.
- **The word *estimate* in Ex. 93.1.** The question says *estimate the future sum*
  and then the arithmetic is exact. That is not sloppiness — the book states that
  this is a very basic interest formula and that more complex ones exist which it
  will not cover. The *formula* is the estimate, not her sum. Her page says so.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. **"If I lend you $30 and you hand me back exactly $30 a year later, what did I
   get out of it?"** Wait. You want *nothing*. Then: **"So what would make it worth
   my while?"** She will invent interest herself, which is a far better start than
   being handed a definition. Name it: rent on money, charged by the year.
2. Write `F = P(1 + rt)` and cover everything except P. **"Which one of these is
   real money?"** Only P. Everything else is a rule about what happens to it. This
   is the sentence that stops her hunting for four numbers when there are three.
3. **"Say 8% as a decimal."** If she says 0.8 or 0.008, stop and do nothing else
   until it is fixed — nothing further in the lesson will come out right until it
   is. The check that settles it: 50% must come out 0.5, because half of a hundred
   dollars is fifty.
4. Work Ex. 93.1 with her but make her do `rt` out loud **and say what it means**:
   `0.08 × 5 = 0.4`, *four tenths of my money gets added*. A child who can say that
   sentence will never write `(1 + 0.08) × 5`.
5. Now Goofball. Get the `$15,000`, then ask the question that is the point of the
   whole lesson: **"How much of that is the controller, and how much is the credit
   card company?"** `$5,000` and `$10,000`. Then, quietly: *he paid ten thousand
   dollars for the privilege of not waiting.* Leave it there. Do not add a lecture —
   the number is the lecture.

If she is lost, it is almost always step 3. Do not re-explain the formula; do six
percents on a scrap of paper and come back.

## The classic mix-ups, with the exact wrong answer each one produces

- **Percent in as a whole number.** `1000(1 + 8(5))` = `1000(41)` = **$41,000**
  instead of **$1,400**. Absurd on its face, so it is catchable — if she looks. Fix:
  ask whether any bank turns $1,000 into $41,000 in five years.
- **The `0.08` habit carried onto a two-digit percent.** `8% → 0.08` and
  `6% → 0.06` make the rule feel like *write the digits after a zero*, and that rule
  turns `20% → 0.02`, which gives `5,000(1.2)` = **$6,000** instead of **$15,000**.
  This one *looks fine*, which makes it the expensive one. Fix: the rule is two
  places left, so 20% is 0.20 — and 50% must come out 0.5.
- **Adding before multiplying inside the bracket.** `(1 + 0.08) × 5 = 5.4` gives
  **$5,400** instead of **$1,400**. Fix: `rt` gets its own line on the page before
  the 1 is touched.
- **Answering with the interest.** `1000 × 0.08 × 5` = **$400** instead of
  **$1,400**; on Goofball, **$10,000** instead of **$15,000**. The arithmetic is
  right and the question was different. Fix: the `1` is her own money coming back —
  F is the total.
- **Time left in months.** Not in her book (every problem is in years), but the
  Rules box warns that time can carry other units, so her page carries it: 6 months
  is `t = 0.5`, and `t = 6` leaves the money there twelve times too long —
  **$1,480** where the answer is **$1,040**.

## What to watch her do

Watch the **page**, in this order:

1. **Do `P`, `r`, `t` appear down the side before the formula does?** Three short
   lines. A child who substitutes straight out of the sentence puts a number in the
   wrong slot about a quarter of the time, and it is invisible afterwards.
2. **Does `0.08` get written down before anything is multiplied?** This is the most
   diagnostic mark on the page. A percent sign still sitting there when the
   multiplying starts is the error that is about to happen.
3. **Inside the parentheses, which operation goes first?** You want to see the `rt`
   product written on its own — `0.08 × 5 = 0.4` — before the `1` is added. If the
   `1 +` is being carried in her head, that is where `$5,400` comes from.
4. **When she has an answer, does she compare it to P?** F is never smaller than P,
   and an answer *many times* bigger than P is almost always a percent that went in
   as a whole number. That check takes two seconds and it catches the `$41,000`
   every time. It will **not** catch the `0.02` slip — `$6,000` on a `$5,000` debt
   sails straight through it — which is why step 2 above, seeing `0.20` written down
   before anything is multiplied, is the only guard against that one.
5. **Can she point at which part of her answer is interest?** Ask on both examples:
   `$400` of the `$1,400`, `$10,000` of the `$15,000`. If she cannot, the `1` has
   not landed, and everything in 93A stays abstract.

Getting `$1,400` is not what to watch for. The arithmetic here is one multiply and
one add; she can be right while holding a badly wrong idea of what she is doing.

## Extend it

- **Do practice problem 293 with her out loud.** `$5,000` at 6% for 10 years is
  `5000(1 + 0.06(10))` = `5000(1.6)` = **$8,000**. Then 393 is the same problem
  again with the numbers changed: `$10,000` at 21% for 10 years is
  `10000(1 + 0.21(10))` = `10000(3.1)` = **$31,000**. Ask her which of the two she
  would rather be holding and why the answers differ so much.
- **Solve the formula for P instead** — which is Lesson 90B, not new work:
  `P = F / (1 + rt)`. Then a real question: *if I want $10,000 in 10 years at 5%,
  how much do I have to put in now?* `10000 / 1.5 = $6,666.67`. That is the same
  formula earning its keep in the other direction.
- **Find a real rate.** A credit card statement, a savings account, a car loan
  advert. Run it through her formula. Then note what her page says about the more
  complex formulas: the real number will be *worse* than simple interest predicts
  for a debt, and *better* for savings. She does not need compound interest — she
  needs to know simple interest is the gentle version.
- **The 27 trillion.** The book says the United States owed more than 27 trillion
  dollars when it was written in **2021**. Look up what the figure is now, together.
  It is a dated number on purpose and a good five minutes: how big is a trillion,
  and who exactly is owed?
- **The question 93A opens with.** Exodus 22:25-27 says not to charge a poor
  person interest. Ask her how that sits beside a bank paying her 8%. There is a
  genuine conversation there about lending to someone in need versus investing, and
  she is old enough for it.

## Where this sits

DIVE Lesson 93, *Interest Rate, Savings and Debt*. Reviews **Lessons 5, 35, 81, 89
and 90** — the book's own first page lists them.

- **Lesson 90 is the one that matters here**, and specifically 90B, *Solving
  Multivariable Equations*. That lesson introduced equations carrying more than one
  letter; this one hands her another and points it the other way — three of the four
  letters arrive with numbers, so the job is substitute-and-evaluate. If she can
  rearrange `F = P(1 + rt)` for P, she has 90B cold.
- **Lesson 89** (limits) is kept warm by the practice set — problem 789 is a limit
  on a discontinuous function — not because interest needs it. **Lesson 81** (logic;
  *What is Calculus?*) has no problem of its own in this set. Problems 492 and 690,
  a derivative and a rate of change, are Lessons 92 and 90.
- **Lessons 5 and 35** sit outside this course's seeded lessons and this guide has
  not read them, so nothing here describes what is in them. The prerequisite this
  formula leans on hardest is percent-to-decimal; if that is shaky, that is what to
  shore up, whichever lesson it came from.

**Proficient** looks like: pulls P, r and t out of the sentence, converts the
percent without prompting, and gets `$1,400` and `$15,000`.
**Mastered** looks like: can say which part of the answer is interest and which part
was always hers, does `rt` before the `1` every time without thinking about it, and
can explain why the same formula covers a savings account and a credit card.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 93 (interest rate, savings and debt) "
            "— idempotent.")

    LESSON_NUMBER = 93
    TITLE = "Interest Is Rent on Money — Interest Rate, Savings and Debt"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
