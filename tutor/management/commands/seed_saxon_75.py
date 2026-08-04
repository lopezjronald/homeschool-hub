"""Saxon Pre-Algebra Lesson 75 — The Binary Numeral System; Pixels.

Reviews Lessons 1 and 3 — continuous vs discrete, and place value. Both of those
are the whole lesson in disguise: base 2 IS place value with a different multiplier,
and a pixel IS a continuous picture chopped into discrete squares.

Two topics, so two IDEA blocks and two WORKED blocks: 75A is the binary numeral
system (Example 75.1's three conversions) and 75B is pixels and megapixels
(Example 75.2).

The source shows two photographs (a bear, zoomed until it pixelates) and a
screenshot of an old display-settings dialog. Neither is reproduced here — the
pixel section is rewritten so it stands on its own words and on the numbers the
text actually states (1600 x 1200), rather than describing pictures the reader
cannot see.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_75 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 75 · Pre-Algebra",
        "title": "Counting with switches",
        "thesis": "A computer has no fingers. It only has switches, and a switch "
                  "is either **on** or **off**. Binary is what counting looks like "
                  "when those two things are all you have.",
        "formula": "1011  =  8 + 2 + 1  =  11",
        "roles": [
            {"tone": "start", "name": "1 means ON",
             "text": "That place counts. Add what it is worth."},
            {"tone": "move", "name": "0 means OFF",
             "text": "That place adds nothing. Skip it and move on."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone counts this way",
        "paragraphs": [
            "You have ten fingers, so you count in tens. When you run out of "
            "fingers you start a new column and write 10. That is the only reason "
            "our number system works in tens — a habit about **hands**, going back "
            "to at least 3000 B.C.",
            "A computer has no fingers. Everything inside it is a tiny switch that "
            "electricity either flows through or doesn't. Two states. So a computer "
            "runs out after **two** instead of after ten, and has to start a new "
            "column much sooner.",
            "That is all binary is. Same counting you already do, with a smaller "
            "hand. Nothing about the mathematics is new — the only thing that "
            "changes is how soon you have to carry.",
            "And you are surrounded by it. Every photo on your phone, every colour "
            "on this screen, is stored as long strings of on and off. Today you "
            "learn to read them.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 2, "tone": "start",
        "title": "A base is how far you can count before you carry",
        "paragraphs": [
            "In base 10, each column is **ten times** the column to its right: "
            "1, 10, 100, 1000. And there are ten digits to fill them — 0 through 9.",
            "In base 2, each column is **two times** the column to its right: "
            "1, 2, 4, 8, 16. And there are only two digits — 0 and 1. That is the "
            "pattern: *the number of digits always equals the base.*",
            "So the chart is the same chart you have used since second grade. "
            "Swap every 10 for a 2 and you are done. You can stretch it further "
            "left whenever you need more room.",
            "Reading a binary number is then one question asked over and over: "
            "**is this place on or off?** If it is on, add what the place is worth. "
            "If it is off, add nothing.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Hold up ten fingers. That's why we count in tens — when you run "
                "out, you start a new column. Now hold up one finger. That's a "
                "computer: on or off, that's all it's got. It still counts exactly "
                "the same way, it just runs out way sooner. Every column is worth "
                "double the one to its right: one, two, four, eight, sixteen. "
                "Reading it is one question, over and over: is this one on?\"",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, every time",
        "steps": [
            {"label": "Draw the places first, before you look at the number.",
             "detail": "Start at the **right** with 1 and double as you go left. "
                       "Draw as many as the binary number has digits.",
             "math": "16     8     4     2     1"},
            {"label": "Drop the digits in, right-hand end first.",
             "detail": "Line up the **last** digit of the binary number under the "
                       "1. Then work leftwards. Lining up from the left is the "
                       "single most common way to get this wrong."},
            {"label": "Cross out every place with a 0 over it.",
             "detail": "Off means it contributes nothing. Saxon says to ignore it "
                       "because you are multiplying by zero — crossing it out is "
                       "the same thing, and you can see it."},
            {"label": "Add up the places still standing.",
             "detail": "That total is your base 10 answer. Nothing else to do."},
        ],
        "after": "Saxon adds a promise worth knowing: **every** Practice Set problem "
                 "in this lesson uses one of the twenty numbers in the table below. "
                 "If you get stuck, you are allowed to look it up. Do the recipe "
                 "first, then check yourself against the table.",
    }),

    (B.KIND_WORKED, {
        "number": "75.1",
        "question": "Convert 1011, 1001 and 10011 to base 10",
        "steps": [
            {"label": "Set up the chart",
             "text": "Four places for the first two — **8, 4, 2, 1**. The third one "
                     "has five digits, so it needs the 16 place as well."},
            {"label": "a)  1011",
             "text": "The 8, the 2 and the 1 are on. The 4 is off.",
             "math": "1(8) + 0(4) + 1(2) + 1(1) = 8 + 2 + 1 = 11"},
            {"label": "b)  1001",
             "text": "The 8 and the 1 are on. The 4 and the 2 are off.",
             "math": "1(8) + 0(4) + 0(2) + 1(1) = 8 + 1 = 9"},
            {"label": "c)  10011",
             "text": "Five digits, so include the 16 place. The 16, the 2 and the 1 "
                     "are on; the 8 and the 4 are off.",
             "math": "1(16) + 0(8) + 0(4) + 1(2) + 1(1) = 16 + 2 + 1 = 19"},
        ],
        "answer": "11   ·   9   ·   19",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 75.1c — 10011, one beat at a time",
        "equation": "10011  =  ?",
        "steps": [
            {"label": "Look first",
             "text": "Count the digits before you do anything else. **Five.** So you "
                     "need five places, and the biggest one is 16."},
            {"label": "Step 1 · draw the places",
             "text": "Right to left, doubling: 1, 2, 4, 8, 16. Written out the "
                     "normal way round, biggest first, that is:",
             "math": "places:   16     8     4     2     1"},
            {"label": "Step 2 · drop the digits in and write a term for each",
             "text": "1, 0, 0, 1, 1 — lined up under those places. Write **every** "
                     "term, including the zeros. The zeros are the part people "
                     "forget, and forgetting one shifts the whole answer.",
             "math": "1(16) + 0(8) + 0(4) + 1(2) + 1(1)"},
            {"label": "Step 3 · throw away the off places",
             "text": "Anything multiplied by 0 is 0, so the 8 and the 4 vanish. "
                     "What is left is what the number is made of.",
             "math": "16 + 0 + 0 + 2 + 1 = 16 + 2 + 1"},
            {"label": "Step 4 · add",
             "text": "Sixteen and two and one. That is the whole answer.",
             "math": "16 + 2 + 1 = 19"},
        ],
    }),

    (B.KIND_TOOL, {
        "title": "Flip the switches yourself",
        "intro": "This is the chart from the recipe, with the places wired up as "
                 "buttons. Tap one to turn it on or off and watch the sum rebuild "
                 "itself underneath, exactly the way the worked example writes it.",
        "widget": "binary",
        # bits=5 because Example 75.1c needs the 16 place. value=11 so it opens on
        # 01011 — Example 75.1a, already solved, so the first thing she sees is a
        # line she has just read rather than a blank chart.
        "config": {"bits": 5, "value": 11},
        "after": "Two things to try. **\"All off\", then \"Count up\" twenty times** — "
                 "watch where the carries happen and compare it to the table below. "
                 "Then turn on **only** the 16 and see how a single switch is worth "
                 "more than the four to its right put together.",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand in this lesson, decoded",
        "intro": "Lesson 75 writes a few things in a compressed way. None of it is "
                 "new mathematics — it is the recipe, written short.",
        "rows": [
            {"symbol": "base 2", "plain": "only two digits exist: 0 and 1",
             "example": "1011"},
            {"symbol": "2⁰", "plain": "the ones place, the far right", "example": "1"},
            {"symbol": "2³", "plain": "2 × 2 × 2 — the eights place", "example": "8"},
            {"symbol": "1(8)", "plain": "the eights switch is ON, so count 8",
             "example": "8"},
            {"symbol": "0(4)", "plain": "the fours switch is OFF, so count nothing",
             "example": "0"},
            {"symbol": "matrix", "plain": "a rectangle of rows and columns",
             "example": "1600 columns × 1200 rows"},
            {"symbol": "MP", "plain": "megapixel — one million pixels",
             "example": "1.92 MP"},
        ],
        "after": "`1(8)` looks like something is being multiplied, and it is — but "
                 "the 1 and the 0 are only ever acting as **yes** and **no**. That "
                 "is why the whole method is just adding.",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Reading a binary number as an ordinary number.",
             "wrong": "1011 → one thousand and eleven",
             "right": "1011 → 8 + 2 + 1 = 11",
             "note": "The digits are **switch positions**, not a base 10 number. "
                     "There is no thousands place in a chart that goes "
                     "8, 4, 2, 1."},
            {"name": "Counting the places from the left.",
             "wrong": "binary 10 = ten",
             "right": "binary 10 → 2",
             "note": "The ones place is always the digit on the far **right**, the "
                     "same as it is in base 10. Line the number up from its "
                     "right-hand end and this mistake disappears."},
            {"name": "Skipping a zero and shortening the number.",
             "wrong": "10011 → 8 + 2 + 1 = 11",
             "right": "10011 → 16 + 2 + 1 = 19",
             "note": "Dropping one 0 in the middle moves every digit to its left "
                     "down a place, and each place is worth **double** the next. "
                     "Write the 0 terms out; do not hold them in your head."},
            {"name": "Multiplying the pixels and calling that the megapixels.",
             "wrong": "5568 × 3712 = 20,668,416 MP",
             "right": "5568 × 3712 ÷ 1,000,000 = 20.668416 → 20.7 MP",
             "note": "The multiplication gives **pixels**. Megapixels means "
                     "millions of pixels, so there is always a divide-by-a-million "
                     "afterwards — or, the same thing, move the decimal six places "
                     "left."},
            {"name": "Thinking a megapixel is a thousand pixels.",
             "wrong": "1 MP = 1,000 pixels",
             "right": "1 MP → 1,000,000 pixels",
             "note": "Mega means million. (A real megapixel is actually "
                     "2^20 = 1,048,576 pixels, because computers count in twos — "
                     "but everyone rounds it to a million, and so will you.)"},
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Every binary number from 1 to 20 — the lesson's own Rules table",
        "headers": ["binary (base 2)", "which places are on", "adds up to", "base 10"],
        "rows": [
            {"cells": ["1", "2⁰", "1", "1"]},
            {"cells": ["10", "2¹", "2", "2"]},
            {"cells": ["11", "2¹+2⁰", "2+1", "3"]},
            {"cells": ["100", "2²", "4", "4"]},
            {"cells": ["101", "2²+2⁰", "4+1", "5"]},
            {"cells": ["110", "2²+2¹", "4+2", "6"]},
            {"cells": ["111", "2²+2¹+2⁰", "4+2+1", "7"]},
            {"cells": ["1000", "2³", "8", "8"]},
            {"cells": ["1001", "2³+2⁰", "8+1", "9"], "emphasis": True},
            {"cells": ["1010", "2³+2¹", "8+2", "10"]},
            {"cells": ["1011", "2³+2¹+2⁰", "8+2+1", "11"], "emphasis": True},
            {"cells": ["1100", "2³+2²", "8+4", "12"]},
            {"cells": ["1101", "2³+2²+2⁰", "8+4+1", "13"]},
            {"cells": ["1110", "2³+2²+2¹", "8+4+2", "14"]},
            {"cells": ["1111", "2³+2²+2¹+2⁰", "8+4+2+1", "15"]},
            {"cells": ["10000", "2⁴", "16", "16"]},
            {"cells": ["10001", "2⁴+2⁰", "16+1", "17"]},
            {"cells": ["10010", "2⁴+2¹", "16+2", "18"]},
            {"cells": ["10011", "2⁴+2¹+2⁰", "16+2+1", "19"], "emphasis": True},
            {"cells": ["10100", "2⁴+2²", "16+4", "20"]},
        ],
        "note": "The three shaded rows are the three parts of Example 75.1. Read "
                "**down** the first column and watch what happens at 1, 3, 7 and 15: "
                "the next number is where a brand new place has to open up, because "
                "every switch you had is already on.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 2, "tone": "move",
        "title": "A photograph is a grid of little squares",
        "paragraphs": [
            "Back in Lesson 1 you met **continuous** and **discrete**. Real life is "
            "continuous — light shades smoothly from one colour into the next, with "
            "no gaps. A screen cannot do that. A screen is made of tiny squares, "
            "each showing exactly one colour.",
            "One of those squares is a **pixel** — short for *picture element*. On a "
            "camera's sensor, pixels *receive* colour; on a screen, they *display* "
            "it. Zoom far enough into any digital photo and the smooth picture "
            "falls apart into the squares it was always made of.",
            "The squares are laid out as a **matrix**: a rectangle of rows and "
            "columns. \"1600 × 1200\" means 1,200 rows with 1,600 pixels in each. "
            "Multiply the two and you get the total number of pixels.",
            "Smaller pixels packed closer together make a picture look smoother and "
            "more real; bigger pixels make it look grainy. That is what *resolution* "
            "means. And because the totals get enormous, we count them in millions — "
            "one **megapixel** is 1,000,000 pixels.",
        ],
    }),

    (B.KIND_WORKED, {
        "number": "75.2",
        "question": "A camera sensor is 5568 pixels wide and 3712 pixels high. "
                    "How many megapixels is that, to 1 decimal place?",
        "steps": [
            {"label": "Picture the matrix",
             "text": "The sensor is a rectangle of square pixels — 5568 across in "
                     "every row, and 3712 rows of them. Total pixels is width "
                     "**times** height, exactly like the area of a rectangle."},
            {"label": "Multiply",
             "math": "5568 × 3712 = 20,668,416"},
            {"label": "Turn pixels into megapixels",
             "text": "Mega means million, so divide by 1,000,000 — or just move the "
                     "decimal point six places to the left, which is the same job "
                     "with less writing.",
             "math": "20,668,416 ÷ 1,000,000 = 20.668416"},
            {"label": "Round to 1 decimal place",
             "text": "The question asked for one decimal place. The digit after the "
                     "6 is another 6, so round up.",
             "math": "20.668416 → 20.7"},
        ],
        "answer": "20.7 MP",
    }),

    (B.KIND_MATH, {
        "display": "1600 × 1200  =  1,920,000 pixels  →  1.92 MP",
        "note": "An older monitor set to **1600 × 1200**: 1,200 rows of 1,600 pixels "
                "each. That is nearly two million little squares, and the graphics "
                "card has to decide what colour every one of them is, many times a "
                "second. It is why turning the resolution *down* makes a slow "
                "computer feel faster — you are giving it less to think about.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Without looking at the table: what is 10100 in base 10?",
        "answer": "**20.** Five digits, so the places are 16, 8, 4, 2, 1. Reading "
                  "left to right: the 16 is on, the 8 is off, the 4 is on, the 2 is "
                  "off, the 1 is off. So `1(16) + 0(8) + 1(4) + 0(2) + 0(1)` = "
                  "16 + 4 = **20**. It is the last row of the table — go and check.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**1 is ON, 0 is OFF.** Reading binary is one question asked over and "
            "over: is this place on?",
            "The places double as you go **left**: 1, 2, 4, 8, 16, and onwards for "
            "as long as you need.",
            "Line the number up from its **right-hand end**, write a term for every "
            "place including the zeros, cross out the zeros, add what is left.",
            "A **pixel** is one square of a picture. A **matrix** is the rows and "
            "columns they sit in. Multiply width by height for total pixels.",
            "**One megapixel is 1,000,000 pixels.** Total pixels ÷ 1,000,000 = MP.",
            "Stuck? Every Practice Set problem in this lesson is one of the twenty "
            "numbers in the table. Look it up — that is allowed here.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 75 first. If it didn't quite click, this is here to fix "
    "that — and there are switches to flip. The whole lesson is one idea: a "
    "computer counts with on-and-off switches instead of ten fingers, so it has "
    "to start a new column after two instead of after ten."
)

PARENT_CONTENT = """## The big idea

Base 10 is a habit about **hands**. Ten fingers, ten digits, and each column is
ten times the one to its right. A computer has no fingers — only switches that are
on or off — so it gets two digits, and each column is **twice** the one to its
right: 1, 2, 4, 8, 16.

Reading a binary number is therefore one question repeated: *is this place on?*
If yes, add what the place is worth. If no, add nothing.

    1011  →  1(8) + 0(4) + 1(2) + 1(1)  =  8 + 2 + 1  =  11

The second half of the lesson is easier and mostly vocabulary. A **pixel** is one
coloured square of a picture; a **matrix** is the rows-and-columns grid they sit
in; a **megapixel** is 1,000,000 pixels. Total pixels = width × height, and
megapixels = that total ÷ 1,000,000.

One thing worth telling her out loud, because it takes the fear out of the whole
lesson: Saxon states that **every** Practice Set problem here is one of the twenty
numbers in the Rules table. She is allowed to look it up. Ask her to do the recipe
first and use the table to check — not the other way round.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. **"Why do we count in tens?"** — let her flounder for a second, then hold up ten
   fingers. *"That's the only reason. When you run out, you start a new column."*
2. Hold up **one** finger. *"This is a computer. On or off. That's everything it
   has."* Then ask: **"So when does it have to start a new column?"** — you want
   "after one." That is the entire lesson and she just said it herself.
3. Write the places right to left, saying **"double it"** each time: 1, 2, 4, 8,
   16. Make *her* say the doubles. Do not write them left to right — the order you
   build them in is the order she will build them in.
4. Write `1011` underneath, **starting from the right-hand end.** Now point at each
   digit and ask only: **"On or off?"** Circle the on ones. Add the circled places
   out loud: eight, two, one — eleven.
5. Do `10011` the same way and let her hit the trap herself: five digits, so five
   places, so the 16 has to exist. Then: **"What would happen if you'd forgotten
   that middle zero?"** Let her work out that everything shifts and the answer
   collapses to 11.

Then let her open the widget on the page and press **Count up** twenty times. Say
nothing while she does it — the carries are visible and she will see the pattern
before you can explain it.

For the pixel half, ask one question: **"Why does a photo go blocky when you zoom
in?"** Then: 1600 × 1200 is 1,920,000 squares — *"and something has to decide the
colour of every single one, sixty times a second."*

## The classic mix-ups, with what she'll actually write

- **Reading `1011` as one thousand and eleven.** The most common one by far. Fix:
  make her name the places out loud before she reads a single digit.
- **Counting places from the left** — writing `binary 10 = ten` instead of 2. The
  ones place is on the far **right**, same as always. Have her line the number up
  from its right-hand end, every time, even when it looks unnecessary.
- **Skipping a middle zero.** She reads `10011` as if it were `1011` and writes
  **11 instead of 19**. Cause: holding the zeros in her head rather than writing
  the `0(8) + 0(4)` terms down. Insist on writing every term.
- **Calling `5568 × 3712 = 20,668,416` the megapixel answer.** That is 20,668,416
  **pixels**; she has to divide by a million to get **20.7 MP**. She will forget
  this step under time pressure roughly half the time at first.
- **Thinking mega means thousand** — writing `1 MP = 1,000 pixels`. Mega means
  million.

## What to watch her do

Watch her **hands**, in this order:

1. Does she write the place values down *before* she looks at the binary number?
   If she starts by reading the digits, she is about to guess.
2. Does her pencil start at the **right-hand end** of the number? Watch where it
   lands first. Left-to-right lining up is the single mistake that produces most
   wrong answers, and you can see it happening from across the table.
3. Does she write the **zero terms** — the `0(8) + 0(4)` — or does she skip them
   and go straight to adding? Skipping is fine once she is fluent, and a reliable
   source of errors before that.
4. On a pixel problem: after multiplying, does her pencil stop, or does it keep
   going to the divide? Stopping at the big number is the classic incomplete
   answer.

**Proficient** looks like: converts any of the twenty numbers correctly, with the
chart written out, given time. **Mastered** looks like: does it without drawing
the chart, and can say *why* — "each place is double the one before it."

## Extend it

- **Count on your fingers in binary.** Each finger is a place: 1, 2, 4, 8, 16. One
  hand gets you all the way to 31, which genuinely surprises most people. This is
  the single best five minutes you can spend on this lesson.
- **Go the other way.** Give her 13 and ask for the binary. The method is greedy
  and she can discover it: what is the biggest place that fits? Take it, then ask
  again with what's left. (8 fits, 5 left; 4 fits, 1 left; 2 doesn't; 1 fits →
  1101.) The table on the page checks her.
- **Measure her own phone.** Look up its camera resolution — something like
  4032 × 3024 — and have her work out the megapixels (12,192,768 pixels, so
  **12.2 MP**). Then compare it to what the phone advertises.
- **Ask why 20.7 MP and not 20.668416 MP.** Rounding to a sensible number of
  figures because the extra digits are noise is a real skill, and this is a
  painless place to notice it.

## Where this sits

DIVE Lesson 75, *The Binary Numeral System; Pixels*. Reviews **Lesson 1**
(continuous vs discrete — which is exactly why a pixel exists) and **Lesson 3**
(place value — which is exactly what a "base" is). If she is lost on the binary
half, Lesson 3 is the one to revisit; if the pixel half feels arbitrary, it is
Lesson 1.
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 75 (binary; pixels) — idempotent."

    LESSON_NUMBER = 75
    TITLE = "Counting with Switches — The Binary Numeral System and Pixels"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
