"""Saxon Pre-Algebra Lesson 87 — Word Problems and Data from a Chart;
Bits, Bytes and Binary Numbers.

Reviews Lessons 65, 74 and 75. Lesson 74 is the hook for the first half — she
already learned that a table IS a chart, and 74 then studied every kind of chart
*except* tables. Lesson 87 goes back and does the one that was skipped. Lesson 75
is the hook for the second half: she already flipped binary switches there, and a
byte is nothing more than eight of them side by side. The book's own first page
says **No New Rules**.

Two halves, so two runs of blocks: 87A is reading a price table (Examples 87.1 and
87.2) and 87B is bits, bytes and how much memory an image costs (Examples 87.3 and
87.4).

The source shows a screenshot of an old display-settings dialog next to the 87B
text. It is not reproduced or described here — Examples 87.3 and 87.4 state their
own resolution and bit depth, so both stand on their own numbers. Idea 3 says so in
one sentence on the child's own page rather than leaving her to wonder what she is
missing, and the parent guide repeats it. The tree-price table IS reproduced, as a
table block, because the whole first half of the lesson is the act of finding a cell
in it.

87B follows the book on what "32 bit" means: 2⁸ × 2⁸ × 2⁸ = 2²⁴ of colour plus a
fourth byte of transparency (source p.3). The memory answers are the same either
way, but the name is only explicable with the transparency byte in it.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_87 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 87 · Pre-Algebra",
        "title": "Find the cell first. Then multiply.",
        "thesis": "A price table has already done the hard thinking for you. The "
                  "only question it asks is **which box am I in** — and once you "
                  "have the right box, the arithmetic is one line long.",
        "formula": "100 × 9.75 = 975.00",
        "roles": [
            {"tone": "start", "name": "the row — what kind",
             "text": "What are you buying? Tree size, shrimp size, screen quality. "
                     "The row is the *thing*."},
            {"tone": "move", "name": "the column — how many",
             "text": "How many are you buying? The column is the *amount*, and it "
                     "is the one people forget to look at."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody puts numbers in a table",
        "paragraphs": [
            "Imagine a tree nursery. Somebody phones and asks what a tree costs. The "
            "honest answer is *it depends* — on how big the tree is, and on how many "
            "you want, because buying a hundred of anything is cheaper per item than "
            "buying one.",
            "You could write that out as a paragraph. Nobody would read it. So the "
            "nursery puts it in a **table** instead: sizes down the side, quantities "
            "across the top, and a price sitting in every box where a size meets a "
            "quantity.",
            "Now the table answers the question for you. You do not compute the "
            "price. You **locate** it. That is the whole skill in the first half of "
            "this lesson, and it is a real one — every menu, shipping chart, tax "
            "table and phone plan in your life works this way.",
            "Here is the part that catches people. The arithmetic in these problems "
            "is easy — one multiply, or one divide. The mistake is almost never in "
            "the arithmetic. It is in **which number you picked up**. So the work "
            "moves earlier: you slow down at the table and you go fast at the sum.",
            "In Lesson 74 you learned that a table counts as a chart, and then that "
            "lesson went off and studied bar graphs, line graphs, pie charts — "
            "practically every kind of chart **except** tables. Lesson 87 is going "
            "back for the one that got skipped.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "The answer is already printed. You are looking, not calculating.",
        "paragraphs": [
            "A word problem usually hands you numbers and asks you to make a new one. "
            "A table problem is different. The number you need is **already on the "
            "page**, and somebody typed it there on purpose.",
            "So the first move is not a pencil move. It is a finger move. Find the "
            "**row** — that is *what kind of thing*. Then find the **column** — that "
            "is *how many*. Where they cross is your number.",
            "Only then does the pencil start. And when it does, it usually only has "
            "one job: price per item **times** how many items.",
            "Say the cell out loud before you use it. \"Eight-to-twelve-inch trees, "
            "fifty or more, nine seventy-five each.\" If that sentence matches the "
            "question, you have the right box. If it does not, you found out before "
            "you multiplied instead of after.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"This one isn't a math problem yet. It's a *find it* problem. Put "
                "your finger on the row — that's what you're buying. Now slide it "
                "across to the column — that's how many. Whatever number is under "
                "your finger, that's the only number you're allowed to use. Read it "
                "to me out loud before you write anything down.\"",
    }),

    (B.KIND_TABLE, {
        "caption": "The nursery's price list — this is the lesson's own table, "
                   "reprinted so you can practise on it",
        "headers": ["Size", "0 – 20 trees", "21 – 50 trees", "50+ trees"],
        "rows": [
            {"cells": ['8 - 12 "', "$12.95", "$10.95", "$9.75"], "emphasis": True},
            {"cells": ["1 - 2 '", "$16.95", "$14.45", "$12.75"], "emphasis": True},
            {"cells": ["2 - 3 '", "$18.95", "$16.15", "$14.25"]},
            {"cells": ["3 - 4 '", "$26.95", "$22.95", "$20.25"]},
            {"cells": ["4 - 5 '", "$35.95", "$30.55", "$26.95"]},
            {"cells": ["5 - 6 '", "$49.95", "$42.45", "$37.45"]},
        ],
        "note": "Every number in here is the price of **one tree**, not a total — the "
                "heading over the three price columns says *price per tree*. The two "
                "shaded rows are the ones the worked examples use. And read across "
                "any single row: the same tree gets cheaper the more of them you "
                "buy. That is the whole reason the table has three columns instead "
                "of one.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, and only the last one is arithmetic",
        "steps": [
            {"label": "Read the question twice and underline two things.",
             "detail": "**What kind** (the size, the type, the quality) and **how "
                       "many** (the count, the pounds, the budget). Those two "
                       "underlines are your row and your column."},
            {"label": "Find the row with your finger.",
             "detail": "Down the left-hand edge. Match the *kind of thing*. Do not "
                       "look at any prices yet — you will grab one by accident."},
            {"label": "Slide across to the right column.",
             "detail": "The column headings are **bands**: a range of amounts, not a "
                       "single amount. Ask which band your number falls into. This "
                       "is the step people skip, and skipping it is what produces a "
                       "wrong answer that still looks tidy.",
             "math": "row: 8 - 12 in.      column: 50+ trees      cell: $9.75"},
            {"label": "Now multiply — and only now.",
             "detail": "Price per item × number of items. One line. If your problem "
                       "gives you a budget instead of a count, you divide instead — "
                       "same table, same cell, the sum runs the other way."},
        ],
        "after": "Then look at the answer and ask whether it is **the size of thing "
                 "you expected**. A hundred small trees should cost around a "
                 "thousand dollars. If your answer came out near a hundred, or near "
                 "ten thousand, you are in the wrong box — go back to step 3 before "
                 "you check your multiplying.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 87.1 — 100 trees, 8 to 12 inches tall",
        "equation": "100 trees, 8 - 12 in. tall   ·   how much will it cost?",
        "steps": [
            {"label": "Look first",
             "text": "The question gives you exactly two facts, and each one picks "
                     "one thing. **8 to 12 inches** is a size, so it picks the row. "
                     "**100** is a count, so it picks the column. Nothing else in "
                     "the sentence matters yet."},
            {"label": "Step 1 · find the row",
             "text": "The 8-to-12-inch row is the top one. There are **three** prices "
                     "sitting in it, and only one of them is yours. Notice that "
                     "now — a row with three prices is the table warning you that "
                     "you are not finished.",
             "math": "8 - 12 in. row:    $12.95     $10.95     $9.75"},
            {"label": "Step 2 · find the column",
             "text": "The landscaper needs 100 trees. The three bands are 0-20, "
                     "21-50, and 50+. "
                     "A hundred is more than fifty, so it lands in the **last** "
                     "column — the cheapest one, which is the whole point of buying "
                     "a hundred at once.",
             "math": "100 trees   >   50 trees   →   the 50+ column"},
            {"label": "Step 3 · read the cell where they cross",
             "text": "Top row, last column. That box says $9.75, and $9.75 is the "
                     "price of **one** tree. Say it out loud: *eight-to-twelve-inch "
                     "trees, fifty or more, nine seventy-five each.*",
             "math": "the cell where that row meets that column:    $9.75"},
            {"label": "Step 4 · now do the arithmetic",
             "text": "One hundred trees at $9.75 each. Price per tree times number of "
                     "trees. This is the only calculating in the entire problem.",
             "math": "100 × 9.75 = 975.00"},
            {"label": "Step 5 · does that look like the right size of answer?",
             "text": "A hundred trees at roughly ten dollars each ought to come to "
                     "roughly a thousand dollars. It does. That check takes two "
                     "seconds and it catches a wrong column, which is the mistake "
                     "you are actually likely to make.",
             "math": "100 × 10 = 1000"},
        ],
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "When they give you the money instead of the count",
        "paragraphs": [
            "Example 87.2 turns the problem around. Instead of *here are 100 trees, "
            "what do they cost*, it says *here is $500, how many trees can I get*. "
            "Same table, same cell-finding — but now the arithmetic is a **divide**.",
            "And there is a genuine tangle in it. To pick the column you need to know "
            "how many trees she is buying. But how many she can buy depends on the "
            "price, which is what the column decides. Each one needs the other first.",
            "Saxon's way out is an **estimate**. All three prices in that row are "
            "somewhere around $15, so guess with $15 and see roughly how many trees "
            "$500 buys. The estimate does not have to be right. It only has to be "
            "close enough to tell you **which band** you are in.",
            "Then, once the band has told you the real price, divide properly. And "
            "when the division gives you a decimal, you cannot round the ordinary "
            "way. You cannot buy 0.6 of a tree, and 35 whole trees would cost more "
            "money than she has. So you round **down** — always down, whenever the "
            "question is *how many can I afford*.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "87.2",
        "question": "The landscaper has $500 to spend on trees. What is the maximum "
                    "number of 1-2 ft. trees she can purchase?",
        "steps": [
            {"label": "Find the row — that part is easy",
             "text": "She wants 1-to-2-foot trees, so it is the second row. Three "
                     "prices again: $16.95, $14.45 and $12.75.",
             "math": "1 - 2 ft. row:    $16.95     $14.45     $12.75"},
            {"label": "You cannot pick the column yet",
             "text": "The column depends on how many she buys, and how many she buys "
                     "depends on the price. So estimate your way in. All three prices "
                     "are in the fifteen-dollar neighbourhood — try 15 and see how "
                     "many $500 gets you."},
            {"label": "Estimate, roughly, with a friendly number",
             "text": "Start the guess by dividing: $500 shared out at about $15 a "
                     "tree is about 33 trees. Now nudge it up to a round-ish 34 and "
                     "check it the easy way — 15 times 34 is about $510, which is "
                     "near enough to $500 to trust. That is Saxon's own estimate, "
                     "and it is quick because 15 is a number you can multiply in "
                     "your head. The estimate does not have to land on the exact "
                     "count. It only has to land in the right band.",
             "math": "500 ÷ 15 = 33.3   →   15 × 34 = 510"},
            {"label": "The estimate tells you the band",
             "text": "Thirty-three or thirty-four trees — either guess lands in the "
                     "**21-50** column, not the 0-20 one and not the 50+ one. So the "
                     "real price is $14.45 per tree. The estimate has done its only "
                     "job and you can throw it away now.",
             "math": "21   ≤   34   ≤   50   →   $14.45 each"},
            {"label": "Now divide with the real price",
             "text": "Five hundred dollars, split into pieces of $14.45. To one "
                     "decimal place that is 34.6 — and 34.6 trees is not a thing "
                     "that exists.",
             "math": "500 ÷ 14.45 = 34.6"},
            {"label": "Round DOWN, and prove it",
             "text": "34.6 rounds to 35 the ordinary way, and 35 is wrong: 35 trees "
                     "cost $505.75, which is more than she has. 34 trees cost "
                     "$491.30, which she can afford. When the question is *how many "
                     "can I afford*, the leftover change never buys another one.",
             "math": "34 × 14.45 = 491.30   →   35 × 14.45 = 505.75   →   34 trees"},
        ],
        "answer": "34 trees",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Grabbing the first price in the row.",
             "wrong": "100 × 12.95 = 1,295.00",
             "right": "100 trees is more than 50   →   100 × 9.75 = 975.00",
             "note": "**$1,295.00 instead of $975.00** — over three hundred dollars "
                     "wrong, from a multiplication that was done perfectly. The "
                     "left-hand price is the *small order* price. Buying a hundred "
                     "is not a small order. Whenever a row hands you three numbers, "
                     "that is the table telling you the column still has to be "
                     "chosen."},
            {"name": "Right column, wrong row.",
             "wrong": "the 1 - 2 ft. row by mistake   →   100 × 12.75 = 1,275.00",
             "right": "the 8 - 12 in. row, 50+ column   →   100 × 9.75 = 975.00",
             "note": "**$1,275.00 instead of $975.00.** The rows sit close together "
                     "and the eye slips down one. Keep a finger physically on the "
                     "row label the whole time you are sliding across — the finger "
                     "cannot slip a row the way your eyes can."},
            {"name": "Rounding a budget answer the ordinary way.",
             "wrong": "34.6   →   nearest whole number   →   35 trees",
             "right": "500 ÷ 14.45 = 34.6   →   35 × 14.45 = 505.75   →   34 trees",
             "note": "**35 instead of 34.** Rounding 34.6 up to 35 is correct "
                     "arithmetic and a wrong answer, because 35 trees cost $505.75 "
                     "and she has $500. *How many can I afford* always rounds down. "
                     "Test it the way this line does: multiply the bigger number "
                     "back and see whether it fits in the budget."},
            {"name": "Sliding off the edge of a band.",
             "wrong": "20 trees, 8 - 12 in. row   →   the 21 - 50 column   →   "
                      "20 × 10.95 = 219.00",
             "right": "20 trees, 8 - 12 in. row   →   the 0 - 20 column   →   "
                      "20 × 12.95 = 259.00",
             "note": "**$219.00 instead of $259.00**, both read from the 8-12 inch "
                     "row. The first band is *0 to 20*, so 20 is still inside it — "
                     "the discount starts at 21. This one is not in your book; it is "
                     "here because band edges are where tables bite. Read the band's "
                     "own edges before you decide; 20 and 21 sit in different columns "
                     "and look almost identical on the page."},
            {"name": "Forgetting that bits are not bytes.",
             "wrong": "1500 × 1000 = 1,500,000 bytes = 1.5 MB",
             "right": "16 bit means 2 bytes per pixel   →   2 × 1500 × 1000 = 3,000,000",
             "note": "**1.5 MB instead of 3.0 MB** — exactly half, which is the "
                     "signature of this mistake. \"16 bit\" is the number of "
                     "**bits** each pixel needs, and memory is measured in "
                     "**bytes**. Eight bits make one byte, so 16 bits is 2 bytes, "
                     "and every pixel costs two. Convert to bytes *before* you "
                     "multiply by the pixel count."},
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "A bit is a switch. A byte is eight of them.",
        "paragraphs": [
            "Now the second half of the lesson, and it starts with two definitions "
            "that are the whole thing.",
            "A **bit** is one digit of a binary number — a 1 or a 0. Inside a "
            "computer it is a tiny electrical switch: **on** means 1, **off** means "
            "0. That is all a bit ever is. You already flipped these in Lesson 75.",
            "A **byte** is 8 bits. Not a different kind of thing — just eight "
            "switches standing in a row, read as one number. That single sentence is "
            "the only new fact in 87B, and every question in this half is built on "
            "it.",
            "So how big can a byte get? Turn all eight switches on and add up what "
            "the places are worth: 128 + 64 + 32 + 16 + 8 + 4 + 2 + 1, which is 255. "
            "Then count 0 as a value too — a byte showing all zeros is still saying "
            "something — and one byte can hold **256** different numbers.",
            "That 256 is why colours work the way they do. Each pixel is a mix of "
            "red, green and blue, and one byte per colour gives 256 shades of each. "
            "Multiply the three together and a screen can show 256 × 256 × 256 = "
            "16,777,216 different colours. Nearly seventeen million, out of "
            "twenty-four little switches.",
            "Twenty-four is where the name comes from. Three bytes of colour is "
            "2⁸ × 2⁸ × 2⁸, which is 2²⁴, so a screen set this way is called "
            "**24-bit** colour. Then computers keep one more byte per pixel to say "
            "how see-through that pixel is — transparency. Eight more switches, "
            "thirty-two altogether, 2³², and that is the **32-bit** setting a "
            "computer calls its highest quality. So 32 bit is not thirty-two "
            "switches of colour. It is twenty-four for colour and eight for "
            "transparency.",
            "One honest note: your book prints a photograph of an old computer's "
            "display-settings window beside this part of the lesson. This page does "
            "not copy that picture, and you do not need it — Examples 87.3 and 87.4 "
            "state their own resolution and their own quality setting, so every "
            "number you need is in the questions themselves.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "128 + 64 + 32 + 16 + 8 + 4 + 2 + 1 = 255",
        "note": "Eight switches, all on. That is the **biggest** number one byte can "
                "hold. The **count** of numbers it can hold is one more — **256** — "
                "because all-switches-off is a perfectly good value too. Biggest is "
                "255; how many is 256. Those are two different questions — a byte "
                "holds 256 different numbers, and they run 0 up to 255 — and this "
                "lesson asks you both of them, so answer the one you were asked.",
    }),

    (B.KIND_TABLE, {
        "caption": "One byte, place by place — the lesson's own chart",
        "headers": ["bit (counting from the right)", "power of 2",
                    "what that switch is worth"],
        "rows": [
            {"cells": ["8", "2⁷", "128"], "emphasis": True},
            {"cells": ["7", "2⁶", "64"]},
            {"cells": ["6", "2⁵", "32"]},
            {"cells": ["5", "2⁴", "16"]},
            {"cells": ["4", "2³", "8"]},
            {"cells": ["3", "2²", "4"]},
            {"cells": ["2", "2¹", "2"]},
            {"cells": ["1", "2⁰", "1"], "emphasis": True},
        ],
        "note": "Read it from the **bottom up** and every line is double the one "
                "before it. The two shaded rows are the ends of the byte: the "
                "cheapest switch is worth 1, and the dearest is worth 128 — more "
                "than all seven of the others put together, which is worth checking "
                "for yourself on the buttons below.",
    }),

    (B.KIND_TOOL, {
        "title": "Build a whole byte",
        "intro": "Eight switches, which is exactly one byte — the same chart as the "
                 "table above, wired up. It opens with everything off, which is a "
                 "real value and not a blank screen: all zeros means zero. Tap a "
                 "switch to turn it on and watch the sum rebuild itself underneath.",
        "widget": "binary",
        # bits=8 and nothing else. The lesson's one new fact is "a byte is 8 bits",
        # so the widget's job here is to BE a byte — eight switches, no more and no
        # fewer. No `value`, so it opens all-off: the child turns them on one at a
        # time and arrives at 255 herself, which is the number this half of the
        # lesson is built on.
        "config": {"bits": 8},
        "after": "Three things to try, in this order. **Turn every switch on** and "
                 "read the total — that is the 255 from the box above, and now you "
                 "have built it instead of being told it. Then **turn on only the "
                 "128** and compare it with the other seven all on together. Last, "
                 "press **All off** and then **Count up** a few times and watch how "
                 "far this eight-wide chart could go before it runs out of room. "
                 "The drop-down right below asks you about the middle one — say your "
                 "answer out loud before you open it.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Turn on only the 128 switch and read the total. Now turn that one "
                  "off and turn on all seven of the others. Which is bigger, and by "
                  "how much?",
        "answer": "**The lone 128 wins — by exactly one.** Add the other seven up:   "
                  "→   64 + 32 + 16 + 8 + 4 + 2 + 1 = 127   →   128 - 127 = 1   →   "
                  "That is true at every place in a byte, not only the top one: a "
                  "switch is always worth one more than everything to its right put "
                  "together. It is also why turning that eighth switch on as well "
                  "gives the biggest number a byte holds:   →   128 + 127 = 255",
    }),

    (B.KIND_WORKED, {
        "number": "87.3 and 87.4",
        "question": "How much memory, in megabytes (MB), is required to display a "
                    "1500 × 1000 image at medium quality (16 bit)? And the same "
                    "image at high quality (32 bit)?",
        "steps": [
            {"label": "Turn the quality into bytes per pixel",
             "text": "\"16 bit\" and \"32 bit\" say how many **bits** the computer "
                     "spends on one pixel — its colour, and at 32 bit its "
                     "transparency as well. Memory is counted in **bytes**, and 8 "
                     "bits make a byte. So 16 bits is 2 bytes and 32 bits is 4 "
                     "bytes. That number — 2 or 4 — is the cost of **one** pixel, "
                     "whatever those bits are being spent on."},
            {"label": "Count the pixels",
             "text": "The resolution 1500 × 1000 means 1,000 rows with 1,500 pixels "
                     "in each, exactly like Lesson 75. Every one of those pixels "
                     "costs the same number of bytes, so the total is bytes-per-"
                     "pixel times width times height."},
            {"label": "87.3 — medium quality, 16 bit",
             "text": "Two bytes for every pixel, across the whole picture. Then turn "
                     "bytes into megabytes: mega means million, so divide by "
                     "1,000,000 — or move the decimal point six places left, which "
                     "is the same job with less writing.",
             "math": "2 × 1500 × 1000 = 3,000,000   →   3.0 MB"},
            {"label": "87.4 — high quality, 32 bit",
             "text": "Same picture, same number of pixels — but each one now costs 4 "
                     "bytes instead of 2. Nothing else changed, so the memory "
                     "**doubles**. You could have said the answer before dividing.",
             "math": "4 × 1500 × 1000 = 6,000,000   →   6.0 MB"},
        ],
        "answer": "3.0 MB   ·   6.0 MB",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Both halves of this lesson lean on marks and abbreviations the book "
                 "never stops to explain. None of them are mathematics — they are "
                 "labels, and here is what each one is short for.",
        "rows": [
            {"symbol": "8 - 12 \"", "plain": "the double mark means INCHES — a tree "
                                             "height, so it is a row label",
             "example": "a knee-high seedling"},
            {"symbol": "1 - 2 '", "plain": "the single mark means FEET — also a "
                                           "height, also a row label",
             "example": "a small potted tree"},
            {"symbol": "0 - 20 trees", "plain": "a quantity BAND, printed as a column "
                                                "heading: buy anywhere from none to "
                                                "twenty and this is your price",
             "example": "ordering 14 trees"},
            {"symbol": "50+", "plain": "the plus means fifty or more, with no upper "
                                       "limit — the bulk-discount column",
             "example": "ordering 100 trees"},
            {"symbol": "price per tree", "plain": "the heading over all three price "
                                                  "columns: every number below is "
                                                  "for ONE tree, never a total",
             "example": "9.75 buys one tree"},
            {"symbol": "bit", "plain": "one binary digit — a switch that is on (1) or "
                                       "off (0)",
             "example": "1"},
            {"symbol": "byte", "plain": "8 bits read together as one number",
             "example": "11111111"},
            {"symbol": "2⁷", "plain": "2 × 2 × 2 × 2 × 2 × 2 × 2 — what the leftmost "
                                      "switch in a byte is worth",
             "example": "128"},
            {"symbol": "16 bit", "plain": "how many bits the computer spends on ONE "
                                          "pixel — so 2 bytes per pixel",
             "example": "medium quality"},
            {"symbol": "32 bit", "plain": "24 bits of colour (one byte each for red, "
                                          "green and blue) plus 8 more for "
                                          "transparency — so 4 bytes per pixel",
             "example": "high quality"},
            {"symbol": "MB", "plain": "megabyte — 1,000,000 bytes",
             "example": "3,000,000 bytes is 3.0 MB"},
        ],
        "after": "The two easiest to mix up are `\"` and `'`. Double is inches, single "
                 "is feet — and it is worth knowing cold, because a table that "
                 "measures the small trees in inches and the big ones in feet will "
                 "hand you the wrong row otherwise.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A table problem is a **finding** problem before it is a math problem. "
            "Row = what kind. Column = how many. The cell where they cross is the "
            "only number you are allowed to use.",
            "**The column is the step people skip.** A row with three prices in it "
            "is the table telling you that you are not finished yet.",
            "Every price in that table is **per one tree**. Multiply by how many.",
            "Given a budget instead of a count: **estimate first** to find the band, "
            "then divide with the real price, then round **down**. You cannot afford "
            "the extra one, and you cannot buy part of a tree.",
            "Check the size of your answer before you check your arithmetic. A wrong "
            "column produces a tidy answer that is hundreds of dollars out.",
            "A **bit** is one switch: 1 is on, 0 is off. A **byte** is **8 bits**. "
            "That one sentence is the only new fact in the second half.",
            "One byte: biggest value **255**, number of different values **256** "
            "(because 0 counts). Do not swap those two.",
            "Bits are not bytes. Divide the bit depth by 8 first, then multiply by "
            "the pixel count — 16 bit is 2 bytes per pixel, 32 bit is 4.",
            "\"32-bit\" is **24 bits of colour plus 8 for transparency**, not 32 "
            "bits of colour. The memory sum does not care — 4 bytes either way — "
            "but the name only makes sense once you know that.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 87 first. If it didn't quite click, this is here to fix "
    "that — and there are switches to flip near the bottom. Two halves today. The "
    "first is reading a price table, where the whole trick is finding the right box "
    "*before* you multiply. The second is one sentence long: a bit is a switch, and "
    "a byte is eight of them."
)

PARENT_CONTENT = """## The big idea

Two halves, and they are genuinely separate. Teach them as two short lessons, not
one long one.

**87A — data from a chart.** The book gives a tree nursery's price list: sizes down
the left, quantity bands across the top, a price in every cell. The mathematics is
one multiply or one divide. The *lesson* is everything that happens before that:
**row = what kind of thing, column = how many, and the cell where they cross is the
only number she is allowed to use.**

The column is the step that gets skipped. She will find the 8-12 inch row instantly,
see `$12.95` sitting at the left of it, and multiply. The answer comes out
`$1,295.00` — arithmetically perfect and three hundred dollars wrong, because 100
trees is a bulk order and belongs in the `50+` column at `$9.75`. Say it to her this
way: *a row with three prices in it is the table telling you that you are not
finished yet.*

Example 87.2 turns it around — `$500` of budget, how many 1-2 ft trees? — and hides
a real circularity: she needs the count to pick the column, and the column to get
the price. Saxon's way out is an **estimate**: all three prices in that row are
around `$15`, so `500 ÷ 15` is about 33 — call it 34 and check it the easy way,
`15 × 34 = 510`. The book prints only the `510` and never says where its 34 came
from, so say the division out loud for her; an unexplained number in the middle of
a method is how a child decides the method is magic. About 34 trees lands in the
`21-50` band at `$14.45`. Then divide properly: `500 ÷ 14.45 = 34.6`. And 34.6
**rounds down**, not to the nearest — 35 trees cost `$505.75` and she only has
`$500`.

**87B — bits and bytes.** One new fact: **a bit is one on/off switch, and a byte is
8 bits.** Everything else follows. All eight switches on is
`128 + 64 + 32 + 16 + 8 + 4 + 2 + 1 = 255`, and counting zero as a value too, a byte
holds **256** different numbers. Then Examples 87.3 and 87.4 spend that fact: "16
bit" means 2 bytes per pixel, so a 1500 × 1000 image needs
`2 × 1500 × 1000 = 3,000,000` bytes = **3.0 MB**, and 32-bit doubles it to
**6.0 MB**.

One point of vocabulary the book is careful about, so her page is too: the *colour*
of a pixel is **24** bits — one byte each for red, green and blue,
`2⁸ × 2⁸ × 2⁸ = 2²⁴`, which is why screens say "24-bit colour". The fourth byte is
**transparency**, and 24 + 8 is the "32-bit" highest-quality setting. The memory
arithmetic does not care (32 bits is 4 bytes whatever the bits describe), but if she
asks *why is it called 32-bit*, that is the answer, and "32 bits of colour" is not.

The book puts a photograph of an old display-settings dialog beside this section.
Her page does not reproduce it and says so plainly — Examples 87.3 and 87.4 both
state their own resolution and quality, so nothing on the page depends on being able
to see that picture. If she has the book open beside her, it is worth a glance
together so the screenshot is not a mystery.

The book's page-one heading is worth reading to her: **No New Rules.** The only new
things in the whole lesson are the two definitions, and one of them is a number: 8.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Open her page to the tree table and cover the prices with your hand. Ask:
   **"Why does this table have three price columns instead of one?"** You want
   something like "because it's cheaper if you buy lots." That single answer is the
   entire first half of the lesson and she got there without you.
2. Uncover it. Read the question aloud — *100 trees, 8 to 12 inches* — and ask:
   **"Which two words in that sentence are pointing at the table?"** You want the
   size and the number. Underline them on her page.
3. Put **her** finger on the row, not yours. Then: **"Now, how many is she buying,
   and which column is that?"** Wait through the pause. If she says the first
   column, do not correct her — ask her to read the three column headings out loud
   instead, and she will correct herself.
4. **"Read me the cell."** Insist on the whole sentence: *eight-to-twelve-inch
   trees, fifty or more, nine seventy-five each.* Then and only then: **"Okay — now
   what's the math?"** She will say `100 × 9.75` and it will feel almost too easy.
   Say out loud that this is the point: *the hard part was choosing, not
   multiplying.*
5. For the second half, hold up eight fingers. **"That's a byte. Every finger is a
   switch. How big a number can you make?"** Let her open the widget on her page and
   turn all eight on. When she reads **255**, ask the follow-up that separates the
   two ideas: **"So how many different numbers can it hold?"** — you want 256,
   because zero counts. Then send her to the drop-down under the widget, which asks
   her to *predict* something she has not been told: whether the single 128 switch
   beats the other seven put together. Make her commit to an answer before it opens.

If she is lost on the first half, do not re-explain — hand her the shrimp table from
her own practice set (problem 187) and ask only *"which row, which column?"* three
times with different quantities. The finding is the skill; the arithmetic will look
after itself.

## The classic mix-ups, with the exact wrong answer each one produces

- **First price in the row.** `100 × 12.95` gives **$1,295.00** instead of
  **$975.00**. The left column is the *small order* price. Fix: three prices in a
  row means the column is still unchosen.
- **Eye slips one row down.** Reading the 1-2 ft prices for an 8-12 in question
  gives `100 × 12.75` = **$1,275.00** instead of **$975.00**. Fix: her finger stays
  physically on the row label the whole time it slides right.
- **Rounding a budget answer to the nearest.** `500 ÷ 14.45 = 34.6` becomes **35**
  instead of **34** — and 35 trees cost `$505.75`, which she cannot pay. Fix: make
  her multiply the bigger number back and check it fits. *How many can I afford*
  always rounds down.
- **Falling off the edge of a band.** 20 trees priced from the `21-50` column gives
  `20 × 10.95` = **$219.00** instead of **$259.00**. The first band is *0 to 20*, so
  20 is still in it; the discount starts at 21.
- **Bits counted as bytes.** For 87.3 she writes `1500 × 1000` = **1.5 MB** instead
  of **3.0 MB** — exactly half, which is the tell. "16 bit" is bits *per pixel*;
  memory is bytes. Divide by 8 first: 16 bits is 2 bytes.
- **Biggest versus how many.** She answers **256** when asked the largest value in a
  byte, or **255** when asked how many values it holds. Both questions are asked in
  this lesson. Zero is a value, so the count is one bigger than the biggest.

## What to watch her do

Watch her **hands**, in this order:

1. **Does a finger land on the table before the pencil moves?** If the pencil starts
   first, she is multiplying a price she has not chosen yet. This is the single most
   diagnostic thing on the page — you can see it from across the table.
2. **Does the finger travel sideways?** Watch for it stopping in the first price
   column. The sideways travel *is* the column-choosing step; a finger that never
   moves right has skipped it, whatever her mouth is saying.
3. **On the budget problem, does she write the estimate down, or try to hold it in
   her head?** `500 ÷ 15 ≈ 33`, then `15 × 34 = 510` on paper is the whole method.
   Held in her head, it evaporates and she picks a column by feel.
4. **After she divides, does her pencil stop at 34.6?** Watch for what happens next.
   You want a visible second multiplication — `35 × 14.45` — testing whether the
   bigger number fits. A child who rounds without testing got 34 by luck today.
5. **On 87.3, does she write the "2" before the 1500?** Watch whether bytes-per-
   pixel appears at the *front* of the multiplication or gets bolted on afterwards.
   Bolted on afterwards is how it gets forgotten under time pressure.

Getting the right answer is not the thing to watch for here. The arithmetic in this
lesson is easy enough that she can be right for the wrong reason. The finger habit
is what survives contact with a harder table.

## Extend it

- **Hand her a real one.** A restaurant menu, a shipping chart, a phone plan, a
  parcel-postage table. Ask a question that needs a row and a column both. This is
  the rare Saxon lesson that is used verbatim by adults, and saying so is worth more
  than another practice problem.
- **Make her build the table.** Give her a made-up product with three quantity bands
  and ask her to price it — then ask *why* a business would offer the discount at
  all. That is the reasoning underneath the whole first half.
- **The boundary question.** Ask what 50 trees cost. The book's own bands are `21-50`
  and `50+`, which both claim 50 — a real ambiguity in a real table, and Example 87.1
  only ever says "more than 50". The right answer is *ask the nursery*, and noticing
  that a table can be genuinely unclear is a better lesson than any price.
- **Count to 255 on her fingers.** Eight fingers, eight bits, and one hand plus three
  gets her the whole byte. Genuinely surprises most people.
- **Why 16,777,216 colours?** One byte per colour, three colours,
  `256 × 256 × 256`. Then ask what happens to the file size if you halve the
  resolution — she has everything she needs from 87.3 to work it out.

## Where this sits

DIVE Lesson 87, *Word Problems and Data from a Chart; Bits, Bytes and Binary
Numbers*. Reviews **Lessons 65, 74 and 75**.

**Lesson 74 is the one to revisit if the first half is lost** — that is where a
table was defined as a kind of chart, and 74 then went on to study every other kind
of chart *except* tables. Lesson 87 is going back for the one that was skipped.
**Lesson 75 is the one for the second half**: binary switches and pixels, which is
where 1-means-on and 0-means-off came from. A byte is just eight of those switches
in a row. **Lesson 65** is listed as review on the book's own first page, but it
sits outside this course's seeded lessons and this guide has not read it — so
nothing here describes what is in it. Lesson 87's pages do not lean on it; if the
review list matters to you, her book's Lesson 65 is the place to look.

**Proficient** looks like: picks the correct cell and multiplies, on a table
problem stated in the ordinary direction, given time — and can say what a bit and a
byte are.
**Mastered** looks like: handles the budget direction too, rounds down without being
reminded and *checks* by multiplying the bigger number back, and does not confuse
"biggest value in a byte" with "how many values a byte holds."
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 87 (data from a chart; bits and bytes) "
            "— idempotent.")

    LESSON_NUMBER = 87
    TITLE = ("Find the Cell First — Word Problems from a Chart, and Bits, Bytes "
             "and Binary Numbers")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
