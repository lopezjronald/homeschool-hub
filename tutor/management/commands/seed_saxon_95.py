"""Saxon Pre-Algebra Lesson 95 — Mean, Median, Mode and Range.

Reviews Lessons 34, 55, 65 and 74. Lesson 74 is the seeded hook and the page uses
it by name: 74's thesis was that a chart *represents* the data rather than
containing it, and four summary numbers are the other half of that same trade —
a representation with no picture in it. Lesson 65 is the hook the book itself
reaches for, because Example 95.1's twenty-five temperatures are the Lesson 65
data set and the shape argument on page 1 is 65's frequency distribution and
histogram. Lessons 34 and 55 are where an average was taught; the book sends her
back to them by name and this page repeats the pointer rather than reteaching it.

Only ONE example exists in this lesson — 95.1 — so there is exactly one worked
run of numbers on the page and nothing invented alongside it. That is why this
lesson, like Lesson 73, carries no KIND_WORKED block: a second example block
would have to be fabricated, and 95.1 is four different questions asked of one
data set in sequence, which is the shape KIND_STEPPER exists for. One example,
in the block that reveals one beat at a time — and because it is the only one,
nothing before it may solve it. The comparison table carries no answer column and
the recipe's math lines are written as rules rather than results, so nothing
between the masthead and the stepper works 95.1 for her. The masthead formula
names the four results up front, which is the pattern's own precedent (seed_87
mastheads its own Example 87.1 answer, 100 × 9.75 = 975.00), and Idea 2 reuses
26.8 and 26 as talking points about how the three middles behave. Neither of them
shows the working, which is what the stepper is for. The standalone mean block
sits AFTER the stepper where it reads as the counting warning it is.
Four further judgement calls, all of them visible to her on the page:

* THE HISTOGRAM. Page 1 prints the Lesson 65 frequency distribution as a figure
  this file cannot see; the OCR recovers only the bin labels (5-9.9 … 45-49.9)
  and a frequency axis running 0-6. The bar heights are RECOVERED, not invented,
  by sorting Example 95.1's own reprinted data into those printed bins:
  1, 2, 3, 4, 5, 4, 3, 2, 1. They total 25, which is the count Ex. 95.1 divides
  by, and they peak at 5, which sits under the printed axis top of 6. Her page
  says it is a rebuild and tells her the book wins if they disagree.
* THE ORDER. The source shows the histogram BEFORE Example 95.1. This page
  computes the four numbers first and looks at the shape afterwards, because
  Ex. 95.1's own closing paragraph is the central-tendency observation — the
  three middles landing at 26.8, 26 and 25 hits harder once she has produced them
  herself.
* THE EVEN-COUNT MEDIAN. The rule is in the page-1 box, but 95.1 has 25 values,
  so the printed lesson never performs the step. The arithmetic of the rule is
  shown on the 13th and 14th of the lesson's OWN list — (26 + 27) ÷ 2 = 26.5 —
  and the math block says plainly that this is the rule, not a book example.
  Practice problem 195 is the even one; its answer stays in the parent guide.
* WHAT COUNTS AS A MEASURE OF CENTRAL TENDENCY. The page follows the book, which
  puts RANGE inside the group: p.1 heads the list "Measures of central tendency
  include:" and lists all four, then repeats it in prose — "Mean, median, mode,
  and range are often referred to as measures of central tendency." The usual
  convention counts only the first three, and an earlier draft of this page
  printed that convention and attributed it to the book, which is the one thing
  a digitization must not do. The genuinely useful observation survives, said as
  itself: range is not pointing at a middle. The parent guide flags the split so
  neither of them is surprised when she meets the shorter list elsewhere.

One oddity of the source worth knowing: the four definitions are printed under
the heading **Rules**, and the Definitions column then says *No New Definitions*.
Nothing is missing — the layout just puts them on the other side.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_95 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

# Example 95.1's data, exactly as the book reprints it — already ordered, which
# the book says out loud. Kept as a list so the stepper's equation line and the
# lesson's prose cannot drift apart from each other.
TEMPS = [7, 11, 12, 15, 16, 18, 21, 22, 23, 24, 25, 25, 26, 27, 29, 31, 32, 33,
         34, 35, 37, 37, 40, 41, 49]
TEMP_LINE = ", ".join(str(t) for t in TEMPS)

# The Lesson 65 frequency distribution, rebuilt. See the module docstring: the
# BINS are printed in the source, the HEIGHTS are recovered by sorting TEMPS into
# them. Labels are the START of each five-degree band — "10-14.9" and its eight
# neighbours will not fit side by side under a 460px chart, and a smudge of
# overlapping text would be worse than a legible convention explained in words.
BANDS = [
    {"label": "5", "value": 1},
    {"label": "10", "value": 2},
    {"label": "15", "value": 3},
    {"label": "20", "value": 4},
    {"label": "25", "value": 5},
    {"label": "30", "value": 4},
    {"label": "35", "value": 3},
    {"label": "40", "value": 2},
    {"label": "45", "value": 1},
]

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 95 · Pre-Algebra",
        "title": "Four numbers that stand in for a whole pile of numbers",
        "thesis": "Twenty-five temperatures is too many to hold in your head. "
                  "**Three of these four numbers tell you where the pile sits. The "
                  "fourth tells you how spread out it is** — and that is the "
                  "question no middle can ever answer.",
        "formula": "mean 26.8   ·   median 26   ·   mode 25 and 37   ·   range 42",
        "roles": [
            {"tone": "start", "name": "the three middles — mean, median, mode",
             "text": "Three different answers to \"what is a typical one?\" When the "
                     "data is piled up around one place they land close together. "
                     "When they do not, that disagreement is itself telling you "
                     "something."},
            {"tone": "move", "name": "the spread — range",
             "text": "Not a middle at all. Range measures how far apart the numbers "
                     "are. Two data sets can share all three middles and still be "
                     "nothing alike."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody squeezes a pile of numbers down to one",
        "paragraphs": [
            "Say your family is choosing between two cities and you want to know "
            "which one has the milder winter. Somebody hands you every daily high "
            "temperature both cities recorded in January. Sixty-two numbers.",
            "You cannot compare thirty-one numbers against thirty-one other "
            "numbers. Nobody can. So you do what everybody does: you work out the "
            "**average** for each city and compare those two numbers instead. That "
            "is the whole idea of this lesson — a pile of data squeezed down into "
            "one number that stands in for it.",
            "Baseball works the same way. Nobody settles an argument about two "
            "players by reading through every at-bat of the season. They compare "
            "**batting averages**, one number each, and suddenly the argument is "
            "possible. Both of those examples are your book's own.",
            "But one number is a kind of lie, because very different piles can "
            "squeeze down to the same average. So the lesson gives you four. Three "
            "of them answer *where is the middle*, in three different ways, and "
            "they usually agree with each other. The fourth answers *how spread "
            "out is it*, and it is the one that catches what the other three miss.",
            "The squeezing part you have already done. Calculating an average is "
            "**Lessons 34 and 55**, and your book sends you back to them by name "
            "rather than teaching it again. What is new today is the other three "
            "words, and the judgement about which one you were actually asked for.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "Four questions you can ask a pile of numbers",
        "paragraphs": [
            "All four definitions sit in one box on page 1 of your lesson. Read "
            "them as four different **questions**, because that is what they are.",
            "**Mean** — *what would everyone get if we shared it out evenly?* Add "
            "every number, divide by how many numbers there are. Mean and average "
            "are the same word; the book says so outright, and researchers use "
            "*mean* when they write about the average of the data they collected.",
            "**Median** — *which one is in the middle of the line?* Put the numbers "
            "in order, smallest to largest, then walk to the centre. Notice there "
            "is no adding in that sentence. With an odd count the median is a "
            "**position** you walk to, not a calculation.",
            "**Mode** — *which one turns up most often?* No arithmetic at all. You "
            "are just looking for a repeat. There can be two of them, and there "
            "can be none.",
            "**Range** — *how far apart are the two ends?* Largest minus smallest. "
            "Your book puts all four under one heading and says it twice: "
            "*measures of central tendency include* mean, median, mode and range. "
            "So when your book asks for the measures of central tendency, it wants "
            "**four** things. Notice all the same that range is the odd one out. "
            "The first three point at a middle. Range does not — it is describing "
            "**spread**, which is a different question entirely. Other books draw "
            "the line there and count only the first three. Yours counts four, so "
            "answer the book in front of you.",
            "One thing about the page itself, so it does not throw you. Those four "
            "definitions are printed under the heading **Rules**, and the "
            "Definitions column beside them says *No New Definitions*. Nothing is "
            "missing. The layout just put them on the other side.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Give me one number that describes this whole list. Any number "
                "you like — just one. Now tell me what you did to get it. Okay: "
                "somebody else would have done something completely different and "
                "they'd be just as right. That's why there are four of these and "
                "not one. The work today isn't the arithmetic, it's knowing which "
                "of the four you were asked for.\"",
    }),

    (B.KIND_TABLE, {
        "caption": "The four, side by side — the question each one answers and "
                   "the work each one costs you",
        "headers": ["name", "the question it answers", "how you get it"],
        "rows": [
            {"cells": ["mean", "what would each one get if we shared evenly?",
                       "add them all, divide by how many"]},
            {"cells": ["median", "which one sits in the middle of the line?",
                       "order them, then step to the centre"]},
            {"cells": ["mode", "which one turns up most often?",
                       "scan for a repeat — no arithmetic"]},
            {"cells": ["range", "how far apart are the two ends?",
                       "largest minus smallest"]},
        ],
        "note": "Your book calls all four of these **measures of central "
                "tendency** — it prints that heading over the list and then says "
                "it again in a sentence, so a question asking for them is asking "
                "for four things. Read the middle column downwards anyway. The "
                "first three rows are three different ways of asking *where is "
                "the middle*, and the fourth is not asking that at all — it is "
                "asking how far apart the ends are. There are no numbers in "
                "this table on purpose. Work the example below first, then come "
                "back and check that the method you used is the one sitting in "
                "the third column.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "Three middles, because each one can be fooled by something different",
        "paragraphs": [
            "If all three point at the middle, one ought to be enough. They are "
            "three because they are three genuinely different ideas of *middle*, "
            "and each has a weakness the other two do not.",
            "The **mean** is the only one that touches every single number. That "
            "is its strength and its weakness at once. It is the fair-share "
            "number — pour all twenty-five temperatures into one pot, share them "
            "out evenly, and everybody gets 26.8. But because every number gets a "
            "vote, one freakish value drags it. The 49 on the end of the "
            "temperature list nudges the mean up slightly. A single 490 would have "
            "hauled it somewhere ridiculous.",
            "The **median** does not care how big the extremes are, only how many "
            "of them there are. Change that 49 to a 490 and the median is still "
            "26, because the 490 is still only *the last one in the line*. That is "
            "why house prices and incomes are almost always reported as medians — "
            "a handful of enormous values would make the mean describe nobody who "
            "actually lives there.",
            "The **mode** is the only one that can point at a value because it is "
            "genuinely common rather than merely central. It is also the only one "
            "that works on things that cannot even be put in order: the most "
            "common eye colour in a room has a mode and does not have a mean.",
            "So when the three land close together, that agreement is information. "
            "It says the data is piled up around one place. When they land far "
            "apart, the disagreement is information too. **Reading the three of "
            "them against each other** is most of what this lesson is for, and it "
            "is exactly what your book does in the last paragraph of Example 95.1.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe",
        "title": "Order the list first. Then answer four questions off it.",
        "steps": [
            {"label": "Write the numbers out in order, smallest to largest.",
             "detail": "Do this even when the question does not ask you to. Median "
                       "is defined by **position**, and an unordered list has no "
                       "middle. Once it is sorted, the smallest and the largest "
                       "are sitting at the two ends where you can see them, and "
                       "any repeats are next to each other."},
            {"label": "Count how many numbers there are. Write the count down.",
             "detail": "You need it **twice** — to divide by for the mean, and to "
                       "work out which position the median is in. Count them in "
                       "fives so you do not lose your place."},
            {"label": "Mean: add them all, then divide by the count.",
             "detail": "The average, from Lessons 34 and 55. Nothing new.",
             "math": "mean = sum ÷ count"},
            {"label": "Median: step to the middle of the ordered line.",
             "detail": "An **odd** count has one number sitting in the middle, at "
                       "position (count + 1) ÷ 2. An **even** count has a gap "
                       "there instead, so you average the two numbers either side "
                       "of it.",
             "math": "odd count   →   position (count + 1) ÷ 2"},
            {"label": "Mode: scan the sorted list for repeats.",
             "detail": "Nothing to calculate. Scan the **whole** list, not just "
                       "until you find the first one — two values can tie, and if "
                       "they do, both are modes and the set is called *bimodal*. "
                       "If nothing repeats at all, say so: there is no mode."},
            {"label": "Range: largest minus smallest.",
             "detail": "The two ends of the line you sorted in step 1. One "
                       "subtraction, and it is the last thing you do.",
             "math": "range = largest - smallest"},
        ],
        "after": "Look at how little arithmetic that was. Only the **mean** makes "
                 "you touch every number. Median is a walk — plus one small "
                 "average if the count came out even — mode is a scan, and "
                 "range is one subtraction between two numbers already sitting at "
                 "the ends. **Sorting the list first does three-quarters of the "
                 "work**, which is why it is step one even when nothing appears "
                 "to ask for it.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 95.1 — all four, for the Lesson 65 temperature data",
        "equation": TEMP_LINE,
        "steps": [
            {"label": "Look first",
             "text": "Twenty-five temperatures, and they arrive **already in "
                     "order** — the book says so: *the ordered data is reprinted "
                     "below*. Step one of the recipe has been done for you, which "
                     "will not happen on the practice set. These are the same "
                     "readings you sorted into bands back in Lesson 65. Nothing "
                     "about the data has changed. Only the question has."},
            {"label": "Step 1 · count them",
             "text": "In fives, so you do not lose your place. There are **25**. "
                     "Write that down — you are about to need it twice, and it is "
                     "the number that decides whether the median is one value or "
                     "the average of two.",
             "math": "count = 25"},
            {"label": "Step 2 · mean — add everything, divide by the count",
             "text": "Add all twenty-five temperatures and you get 670. Then divide "
                     "by how many numbers there are. This is the average from "
                     "Lessons 34 and 55 wearing a new name, and the book does not "
                     "reteach it because there is nothing to reteach.",
             "math": "670 ÷ 25 = 26.8"},
            {"label": "Step 3 · median — walk to the middle",
             "text": "Twenty-five is odd, so exactly one number sits in the middle: "
                     "twelve to its left, twelve to its right. That makes it the "
                     "**13th**. Count along the line and the 13th is 26. Notice "
                     "you did no arithmetic in this step at all — with an odd "
                     "count the median is a position you walk to.",
             "math": "the 13th of 25 numbers   →   26"},
            {"label": "Step 4 · mode — look for repeats",
             "text": "Scan for anything written twice. **25** appears twice. Keep "
                     "going — so does **37**. Nothing appears three times, so it is "
                     "a tie, and a tie is not a tiebreak. Both of them are modes, "
                     "and a data set with two of them has its own word: this one is "
                     "**bimodal**.",
             "math": "25 twice   ·   37 twice   →   bimodal"},
            {"label": "Step 5 · range — the two ends",
             "text": "The list is in order, so the smallest is at the far left and "
                     "the largest at the far right. One subtraction and you are "
                     "done.",
             "math": "49 - 7 = 42"},
            {"label": "Step 6 · now read the four together",
             "text": "This is the part of the example most people skip and the book "
                     "does not. **26.8, 26, and one of the modes at 25 are "
                     "practically the same number.** The three middles agree with "
                     "each other, and that agreement is what the book means by "
                     "this data having good *central tendency*. The range of 42 is "
                     "the one it is less pleased about — it says the book would "
                     "have preferred a smaller one, and the next section is about "
                     "why.",
             "math": "26.8   ·   26   ·   25 and 37   ·   42"},
        ],
    }),

    (B.KIND_MATH, {
        "display": "670 ÷ 25 = 26.8",
        "note": "One line out of that example is worth stopping on, because it is "
                "the line people get wrong. The 670 is every temperature added "
                "together. The **25** is how many numbers there are — not the last "
                "one, not the biggest one, and not 24 because you lost your place "
                "counting. A mean is always a division by the **count**. Count in "
                "fives, write the number down, and then use that same written-down "
                "number again when you go hunting for the median.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "start",
        "title": "The shape underneath, and what a small range buys you",
        "paragraphs": [
            "Go back to **Lesson 65** for a moment. These same twenty-five "
            "temperatures were sorted into bands there — 5 to 9.9 degrees, 10 to "
            "14.9, and so on up to 45 to 49.9 — and then drawn as a **frequency "
            "distribution**: one bar per band, and the height of each bar is how "
            "many readings fell into it.",
            "Drawn that way, something shows up that a list of twenty-five numbers "
            "hides completely. The bars are short at both ends and tallest in the "
            "middle. The data is **centred**. Lesson 65 has a name for that shape — "
            "a **normal distribution** — and page 1 of your lesson prints the "
            "picture.",
            "Two things follow from that shape and your book states both. **One:** "
            "if data really is normally distributed, the mean, the median and the "
            "mode usually come out quite similar. Look at what you just "
            "calculated — 26.8, 26, and a mode at 25. **Two:** the smaller the "
            "range, the more likely the data is following that shape, because a "
            "wide range means values straggling out at the edges where the bars "
            "should be getting short.",
            "So the four numbers are not four separate answers. Between them they "
            "describe one thing: **where the pile sits, and how tightly it is "
            "piled.** In **Lesson 74** you learned that a chart does not contain "
            "the data, it represents it. This is the other half of the same trade — "
            "four numbers that represent the data, with no picture required at all.",
            "One honest note before the chart below. Page 1 prints that histogram "
            "as a picture, and this page cannot copy pictures. The bars you are "
            "about to see are **rebuilt** — the bands are the ones your book "
            "prints, and the heights were worked out by sorting Example 95.1's own "
            "twenty-five temperatures into them. They should match your book "
            "exactly. If they do not, your book wins; show it to your parent.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "The Lesson 65 frequency distribution, rebuilt from Example "
                   "95.1's own twenty-five temperatures",
        "headers": ["band (°F)", "the readings that landed there", "how many"],
        "rows": [
            {"cells": ["5 - 9.9", "7", "1"]},
            {"cells": ["10 - 14.9", "11, 12", "2"]},
            {"cells": ["15 - 19.9", "15, 16, 18", "3"]},
            {"cells": ["20 - 24.9", "21, 22, 23, 24", "4"]},
            {"cells": ["25 - 29.9", "25, 25, 26, 27, 29", "5"], "emphasis": True},
            {"cells": ["30 - 34.9", "31, 32, 33, 34", "4"]},
            {"cells": ["35 - 39.9", "35, 37, 37", "3"]},
            {"cells": ["40 - 44.9", "40, 41", "2"]},
            {"cells": ["45 - 49.9", "49", "1"]},
        ],
        "note": "The right-hand column adds to **25**, which is the check that "
                "nothing got lost or counted twice — do that addition every time "
                "you build one of these. Now read that column on its own: **1, 2, "
                "3, 4, 5, 4, 3, 2, 1.** The shape is sitting there in the numbers "
                "before anybody draws anything. The shaded band is where the middle "
                "lives — the mean (26.8), the median (26) and one of the two modes "
                "(25) all fall inside that single five-degree band, which is what "
                "good central tendency looks like when you can see it.",
    }),

    (B.KIND_TOOL, {
        "title": "The Lesson 65 histogram, rebuilt",
        "intro": "Nine bars, one per five-degree band, and the height of a bar is "
                 "how many of the twenty-five readings landed in that band. It is "
                 "the table you just read, drawn. The number under each bar is the "
                 "**start** of its band, so the bar marked 25 is the 25-to-29.9 "
                 "band — the labels are shortened because nine full band names "
                 "will not fit side by side without turning into a smudge.",
        "widget": "chart",
        # kinds=["bar"] alone, on purpose. Lesson 74's switcher existed because
        # Saxon's point there was that one dataset can wear five costumes. Here
        # the bar chart IS the book's own figure — a histogram — and the widget's
        # other costumes would misrepresent it. A line joining these bars would
        # claim the data flows between bands, which is exactly the reading the
        # widget's own line-chart note warns against. With one kind, no switcher
        # buttons render and the picture is just the picture.
        "config": {
            "data": BANDS,
            "kinds": ["bar"],
            "label": "frequency distribution of twenty-five temperature readings "
                     "in degrees Fahrenheit",
        },
        "after": "Three things to look for, in this order. **One:** the tallest bar "
                 "is the middle one, and the bars get shorter in both directions "
                 "away from it. That is the centring the lesson keeps talking "
                 "about, and it is the reason the mean, the median and a mode all "
                 "came out around 26. **Two:** put your finger on the left-hand "
                 "bar and count rightwards, adding the heights as you go — 1, then "
                 "3, then 6, then 10, then 15. The 13th reading is inside the fifth "
                 "bar, which is precisely where the median landed. **Three:** the "
                 "bars stretch across every band, from 5-9.9 at the left end to "
                 "45-49.9 at the right. That whole width is the **spread**, and "
                 "seeing it in one look is the thing a list of twenty-five numbers "
                 "will not do for you. It will not hand you the range exactly, "
                 "though: the end bars only say which band the extremes fell in, "
                 "not that they were 7 and 49. For the 42 itself you still have to "
                 "go back to the list and take 49 - 7. Then open the drop-down "
                 "below and answer it before you read the answer.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "Your lesson ends with an odd little thought. If those "
                  "twenty-five numbers were not temperatures but the distances "
                  "from the bullseye to where each of a shooter's bullets hit, a "
                  "range of 42 would be bad news. Why does the same number mean "
                  "something different?",
        "answer": "**Because for a shooter, spread is not just a description of "
                  "the data — it is part of what is being judged.** Put the two "
                  "cases side by side, and watch how hard your book presses in "
                  "each one.   →   "
                  "*Temperatures:* the readings run 7° to 49°, a range of 42, and "
                  "the book's verdict is mild — *a smaller range would be "
                  "preferred though*. Preferred, and that is all. Temperatures "
                  "vary; the range is reporting the weather, not an error.   →   "
                  "*Bullet holes:* the same numbers now say one shot landed 7 "
                  "units from the bullseye and another landed 49 units out. Here "
                  "the book does not say smaller. It says a **much** smaller range "
                  "would be preferred, and that jump from *smaller* to *much "
                  "smaller* is the whole answer. And notice the mean did not "
                  "move — 26.8 either way. (It is not good news for the shooter "
                  "either: an average miss of 26.8 units is a long way from the "
                  "bullseye. It is just not the number your book is pointing at "
                  "here.) A shooter is judged on landing close **and** landing "
                  "consistently, and the range is the number that reports the "
                  "second one.   →   "
                  "The mean cannot tell those two stories apart, because **a "
                  "middle says nothing at all about spread**. That is why range "
                  "sits in this lesson alongside the three middles instead of in "
                  "a lesson of its own. Two data sets can share a mean, a median "
                  "*and* a mode and still be nothing like each other — and the "
                  "range is the first number that notices.",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "move",
        "title": "When there is no single middle",
        "paragraphs": [
            "Twenty-five numbers have a middle. Twenty-four do not.",
            "Line up an even number of things and the centre falls in the **gap** "
            "between the two middle ones. No number is sitting there, so the rule "
            "is: take the number on each side of the gap and average them. That "
            "average is the median — and it is allowed to be a value that never "
            "appeared in your data at all.",
            "That is not a special case bolted on to make even lists work. A "
            "median is a value with as much data below it as above it. When the "
            "count is odd, exactly one of your own numbers does that. When the "
            "count is even, the split falls in the gap instead, and *any* value "
            "between the two middle numbers would divide the data evenly — the "
            "definition on its own does not pick one out. So the rule picks the "
            "fairest point in that gap, the one dead halfway between them. That is "
            "why you average the middle pair: not a patch, a tie-break for "
            "something the definition leaves open.",
            "Two things to be careful about. First, **order the list before you go "
            "looking for the middle** — with an even count you are pulling two "
            "numbers out by position, and position means nothing in an unsorted "
            "list. Second, **count the list twice.** Whether you take one number "
            "or average two depends entirely on whether that count came out odd or "
            "even, and miscounting by one flips you onto the wrong rule.",
            "Practice problem 195 is the even one — ten high temperatures from "
            "King Salmon, Alaska. Your book gives you both hints inside the "
            "problem itself: sort them first, and average the middle two. Those "
            "are the two sentences above, printed where you cannot miss them.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "an even count:   … 26 |gap| 27 …   →   (26 + 27) ÷ 2 = 26.5",
        "note": "**This is the arithmetic of the rule, not one of the book's "
                "examples.** Lesson 95's only worked example has 25 numbers in it, "
                "which is odd, so the printed lesson never actually performs this "
                "step — the rule is stated in the box on page 1 and then left for "
                "you to use on the practice set. The two numbers above are the "
                "13th and 14th of this lesson's own temperature list, borrowed "
                "here just to show the move: find the gap, take the number on each "
                "side, add them, halve them. And notice the answer. **26.5 is not "
                "one of the temperatures.** A median often is not, and that is not "
                "a sign you did it wrong.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Hunting for the median before sorting the list.",
             "wrong": "median = whatever sits in the middle of the list as printed",
             "right": "sort smallest → largest first, then step to the middle",
             "note": "**The median is defined by position, and position means "
                     "nothing until the numbers are in order.** Example 95.1 hands "
                     "you the data pre-sorted and says so, which means this trap "
                     "never fires while you are reading the lesson — and then "
                     "fires immediately on the practice set, where the numbers "
                     "arrive shuffled. Sort first, every time. It costs thirty "
                     "seconds and it hands you the range for free."},
            {"name": "Dividing by the wrong number for the mean.",
             "wrong": "670 ÷ 24 ≈ 27.9",
             "right": "670 ÷ 25 = 26.8",
             "note": "**27.9 instead of 26.8**, from losing one number while "
                     "counting twenty-five of them. That wrong line has a ≈ and "
                     "not an = for a reason: 670 ÷ 24 does not come out even, it "
                     "runs on as 27.9166… and has to be rounded. Which is a clue "
                     "in itself — the ÷ 25 version stops dead at 26.8. The mean "
                     "divides by **how many numbers there are** — not by the "
                     "largest, not by the last one, and not by a miscount. Count "
                     "in fives, write the count down where you can see it, and "
                     "reuse that written number for the median instead of counting "
                     "all over again."},
            {"name": "Taking one middle number when the count is even.",
             "wrong": "10 numbers   →   the 5th one",
             "right": "10 numbers   →   (the 5th + the 6th) ÷ 2",
             "note": "There is no fifth-and-a-half number, so an even count needs "
                     "the two either side of the gap, averaged. **Practice problem "
                     "195 is exactly this** and your book warns you inside the "
                     "problem. The tell that you have slipped is that you did no "
                     "arithmetic — an even-count median nearly always needs one "
                     "small addition and one halving."},
            {"name": "Stopping at the first repeat you find.",
             "wrong": "mode = 25",
             "right": "25 twice and 37 twice   →   bimodal, both are modes",
             "note": "**In Example 95.1 there is a tie, and a tie is not a "
                     "tiebreak.** You do not pick the smaller one, or the first "
                     "one, or the one nearest the mean. You report both and call "
                     "the set **bimodal**. So scan the whole list before you "
                     "answer. And if nothing repeats at all, the honest answer is "
                     "that this data set has no mode — not that the mode is zero."},
            {"name": "Writing the range as a pair of ends.",
             "wrong": "range = 7 to 49",
             "right": "range = 49 - 7 = 42",
             "note": "**The range is one number, not two.** In ordinary English a "
                     "range *is* a pair of ends — \"temperatures in the range 7 to "
                     "49\" is a perfectly normal sentence — which is exactly why "
                     "this slip is so easy. In this lesson range means a "
                     "**difference**, largest minus smallest, and it is a single "
                     "number precisely so you can hold it up against another data "
                     "set's single number."},
            {"name": "Treating a big range as proof something went wrong.",
             "wrong": "range 42   →   the data must be bad",
             "right": "range 42   →   the data is spread out; whether that is bad "
                      "depends what it measures",
             "note": "Your book is careful here and it is worth copying. A range of "
                     "42 across a set of temperature readings is just "
                     "**weather** — the book allows itself only *a smaller range "
                     "would be preferred* and moves on. The very same 42, measured "
                     "between a bullseye and a shooter's bullet holes, would be a "
                     "real problem, and there the book asks for a **much** "
                     "smaller range. Range measures spread — and whether spread "
                     "is bad news, good news "
                     "or no news at all is a question about the thing being "
                     "measured, never about the arithmetic."},
        ],
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "This lesson is mostly vocabulary, and four of its words look "
                 "ordinary while meaning something exact. Here is each one, plus "
                 "the abbreviations the practice set uses without stopping to "
                 "explain them.",
        "rows": [
            {"symbol": "mean", "plain": "the average — add every number, divide by "
                                        "how many there are",
             "example": "670 ÷ 25 = 26.8"},
            {"symbol": "median", "plain": "the middle number of an ORDERED list; "
                                          "average the middle two if the count is "
                                          "even",
             "example": "the 13th of 25 = 26"},
            {"symbol": "mode", "plain": "the number that turns up most often — "
                                        "there can be two, and there can be none",
             "example": "25 and 37"},
            {"symbol": "range", "plain": "largest minus smallest: one number, a "
                                         "difference, not a pair of ends",
             "example": "49 - 7 = 42"},
            {"symbol": "measures of central tendency",
             "plain": "your book's collective name for all FOUR — mean, median, "
                      "mode and range. The first three point at the middle; range "
                      "measures spread",
             "example": "26.8 · 26 · 25 and 37 · 42"},
            {"symbol": "bimodal", "plain": "a data set with two modes, because two "
                                           "values tie for most common",
             "example": "Example 95.1"},
            {"symbol": "frequency distribution",
             "plain": "data sorted into bands, counting how many landed in each "
                      "(Lesson 65)",
             "example": "25 - 29.9 °F: 5 readings"},
            {"symbol": "normal distribution",
             "plain": "the piled-in-the-middle, thin-at-both-ends shape defined in "
                      "Lesson 65",
             "example": "1, 2, 3, 4, 5, 4, 3, 2, 1"},
            {"symbol": "°F", "plain": "degrees Fahrenheit — the unit every "
                                      "temperature in this lesson is measured in",
             "example": "49 °F"},
            {"symbol": "(C)", "plain": "calculator allowed on this problem — a "
                                       "permission, not an instruction",
             "example": "195. (C) Find the mean…"},
            {"symbol": "1 d.p.", "plain": "round the final answer to 1 decimal "
                                          "place (d.p. = decimal places)",
             "example": "26.8"},
        ],
        "after": "The one to watch is **mean**. In ordinary English the word has "
                 "nothing to do with arithmetic, and in this lesson *mean* and "
                 "*average* are simply the same thing — your book says so on page "
                 "1 and then uses whichever it feels like from sentence to "
                 "sentence. When a scientist writes \"the mean temperature was "
                 "26.8 °F\", she added up her readings and divided by how many she "
                 "took. Nothing more mysterious than that is going on.",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Mean** = add them all, divide by **how many**. It is the average "
            "from Lessons 34 and 55 under a new name.",
            "**Median** = the middle of the **ordered** list. Odd count: one "
            "middle number. Even count: average the middle two.",
            "**Mode** = the value that turns up most often. There can be **two** "
            "(bimodal), and there can be none at all.",
            "**Range** = largest minus smallest. One number, and it is a "
            "**difference** — never a pair of ends.",
            "**Sort the list first, always.** The median needs it, the range falls "
            "out of it for free, and repeats line up next to each other where you "
            "can see them.",
            "**Count the numbers and write the count down.** You divide by it for "
            "the mean, and it tells you whether the median is one number or the "
            "average of two.",
            "Your book calls all four the **measures of central tendency** — so "
            "if it asks for them, give it four. Three of them answer *where is "
            "the middle*. **Range answers a different question:** how spread out "
            "the numbers are.",
            "When data follows a **normal distribution** — Lesson 65's "
            "piled-in-the-middle shape — the three middles usually come out close "
            "together. In Example 95.1 they were 26.8, 26 and — taking the lower "
            "of the two modes — 25.",
            "A **smaller range** makes a normal distribution more likely. Whether "
            "a small range is *desirable* depends entirely on what you are "
            "measuring: temperature readings spread out, and a shooter's bullets "
            "had better not.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 95 first. If it didn't quite click, this is here to fix "
    "that — and there's a chart near the middle you can read most of the lesson "
    "off. Four words today, and the arithmetic that touches the numbers is one "
    "addition and one division for the mean, one subtraction for the range, and "
    "— only if the list has an even number of things in it — one small halving "
    "for the median. Mean, median and mode are three "
    "different ways of saying *the middle*. Range is not a middle at all — it "
    "measures how spread out the numbers are, which is the one thing a middle can "
    "never tell you."
)

PARENT_CONTENT = """## The big idea

Four definitions, one worked example, and no arithmetic she has not had since
Lesson 34. What is actually being taught here is **which question she was asked**,
because three of the four words mean something close to "the middle" and a child
under time pressure answers whichever one she calculated first.

- **mean** — the average. Add every value, divide by the count. The book sends her
  back to **Lessons 34 and 55** by name rather than reteaching it, and states that
  *mean* and *average* are the same word.
- **median** — the middle value of the **ordered** list. Found by position, not
  by adding everything up. Odd count: one number. Even count: no single middle, so
  average the two either side of the gap.
- **mode** — the value that occurs most often. It can tie (**bimodal**) and it can
  be absent entirely.
- **range** — largest minus smallest. The first three say where the data sits;
  range says how spread out it is, and separating those two jobs out loud is the
  single most useful thing you can do in this lesson.

**One labelling point, because her page follows the book and not the convention.**
Page 1 heads the list *Measures of central tendency include:* and then puts all
four under it — mean, median, mode **and range** — and repeats it in prose a few
lines later. Most textbooks and most of the internet count only the first three,
so if she meets the term anywhere else she will meet the shorter list. Her page
says all four, because that is what her book asks for and a four-item question
answered with three items loses a mark she earned. Say the distinction as a
distinction rather than a correction: all four are on her book's list, and range
is still the one that is not pointing at a middle.

**Example 95.1** is the whole of the taught content and it runs on the twenty-five
temperature readings she organised back in Lesson 65, reprinted in order:
`7, 11, 12, 15, 16, 18, 21, 22, 23, 24, 25, 25, 26, 27, 29, 31, 32, 33, 34, 35,
37, 37, 40, 41, 49`. Mean: they sum to 670, so `670 ÷ 25 = 26.8`. Median: 25 is
odd, so it is the 13th number, `26`. Mode: **both** 25 and 37 appear twice, so the
set is **bimodal** — the book is explicit that a tie is reported as a tie. Range:
`49 - 7 = 42`.

Then the paragraph the book writes and most people skim: 26.8, 26 and one of the
modes at 25 are practically the same number, so this data has good **central
tendency** — and the range of 42 is the part it is less happy about. That
observation is the actual lesson. The four numbers are not four separate answers;
between them they say *where the pile sits and how tightly it is piled*.

**The histogram, and what her page does about it.** Page 1 reproduces the Lesson 65
frequency distribution as a figure, and this page cannot copy figures. The bars on
her page are **rebuilt, not invented**: the bands are the ones the book prints
(`5-9.9` up to `45-49.9`) and the heights come from sorting Example 95.1's own
twenty-five temperatures into them — **1, 2, 3, 4, 5, 4, 3, 2, 1**, which totals 25
and peaks at 5 against the book's printed axis running to 6. Her page says it is a
rebuild and tells her the book wins if the two ever disagree. Worth one glance
together with the book open so the figure is not a mystery.

**A layout oddity, so it does not throw either of you.** The four definitions are
printed under the heading **Rules**, and the Definitions column beside them reads
*No New Definitions*. Nothing is missing from her book.

**One thing her page does that the printed lesson does not.** The even-count median
rule is in the page-1 box, but Example 95.1 has 25 values, so the printed lesson
never performs the step — she is expected to meet it cold on practice problem 195.
Her page therefore shows the arithmetic of the rule on the 13th and 14th of the
lesson's own list, `(26 + 27) ÷ 2 = 26.5`, and says plainly that this is the rule
rather than one of the book's examples.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Open her page to the twenty-five temperatures and cover everything else. Ask:
   **"If you had to describe this whole list to somebody using one number, what
   number would you pick?"** Take whatever she says. Most people reach for the
   average, and that instinct is right — say so. Then the follow-up:
   **"Why not just read them all twenty-five numbers?"** You want *because nobody
   can hold twenty-five numbers in their head.* That is the entire reason this
   lesson exists and she has just supplied it herself.
2. Now the separation that matters. **"Point at the middle number of that list."**
   She counts to the 13th. **"Now work out the average."** She adds and divides.
   Then: **"Those were two completely different jobs. Did you notice?"** One was
   walking, one was arithmetic. Median and mean, done back to back, is the fastest
   way to feel that they are not the same idea.
3. **"They came out 26 and 26.8. Why so close?"** Let her sit with it. The answer is
   the shape — the data is piled up in the middle. Show her the rebuilt histogram
   on her page and ask what shape it is. *Normal distribution* is Lesson 65's word;
   if she remembers it, excellent, and if not the picture does the work anyway.
4. **"Find me a number that shows up twice."** She finds 25. Now wait, and watch
   whether she keeps looking. If she stops, ask: **"Are you sure there's only
   one?"** There is also 37. That one question teaches *bimodal* better than the
   definition does, because she discovers the tie instead of being handed it.
5. Last, the one that separates this lesson from the three ideas before it.
   **"Biggest minus smallest is 42. Is 42 a good number or a bad number?"** You want
   *it depends what you're measuring.* When she gets there, read her the book's own
   closing line — that if these were distances from a bullseye to a shooter's bullet
   holes, a much smaller range would be preferred. That is the moment range stops
   being a fifth thing to memorise.

If she is lost, go back to step 2. Everything else in this lesson is arithmetic she
already owns.

## The classic mix-ups, with the exact wrong answer each one produces

- **Median without sorting.** She takes the middle of the list as printed. Example
  95.1 hides this trap by handing her pre-sorted data and saying so; the practice
  set does not. Fix: sorting is step one whether or not anything asks for it, and it
  hands her the range for free.
- **Dividing by the wrong count.** `670 ÷ 24` ≈ **27.9** instead of **26.8** — one
  number lost while counting twenty-five of them. Note the `≈`: 670 ÷ 24 runs on as
  `27.9166…` and has to be rounded, while `670 ÷ 25` stops dead at `26.8`. If her
  mean arrives as an endless decimal on a Saxon problem, the count is worth
  recounting. Fix: count in fives, write the count down, and reuse that written
  number for the median rather than recounting.
- **One middle number on an even list.** Ten data points and she takes the 5th
  instead of averaging the 5th and 6th. **Practice problem 195 is exactly this**,
  and the book warns her inside the problem. The tell is that she did no arithmetic.
- **Stopping at the first repeat.** She answers `mode = 25` and misses that 37 also
  appears twice. A tie is not a tiebreak — both are modes and the set is
  **bimodal**. Fix: scan the whole list before answering. And if nothing repeats,
  the answer is *no mode*, not *zero*.
- **Range written as a pair.** She writes "7 to 49" instead of **42**. In ordinary
  English a range *is* a pair of ends, which is why this is so easy. Here it is a
  difference — one number, so it can be compared against another data set's one
  number.
- **Answering the wrong one of the four.** She computes all four correctly and then
  labels them wrongly, most often swapping mean and median. Fix: make her write the
  word next to each answer, not just the number.

## What to watch her do

Watch her **pencil**, in this order:

1. **Does she rewrite the list in order before doing anything else?** This is the
   most diagnostic thing on the page and you can see it from across the table. A
   child who starts calculating from an unsorted list will get the mean right and
   the median wrong, which looks like carelessness and is actually a missing step.
2. **Does the count get written down?** Look for a small number circled or boxed at
   the top. If the count only ever lives in her head, she will recount for the
   median, get a different answer the second time, and never know which one was
   right.
3. **On the median, does she check the position from both ends?** Her page works
   out the position first — `(25 + 1) ÷ 2` is the 13th — and then counts along the
   line to it. That is the method to use, and it is also one arithmetic slip away
   from the wrong number with nothing to catch it. The check costs nothing: a
   finger at each end, stepping inwards together, should meet on the number she
   already wrote down.
4. **Does she keep scanning after she finds a repeat?** Watch for the pencil
   stopping at 25. In Example 95.1 stopping there is wrong, and it is wrong in a way
   that feels finished.
5. **Does she label her four answers with words?** `26.8, 26, 25 and 37, 42` written
   in a row is an invitation to hand in the median when the question said mean. This
   is the cheapest habit on the list and it prevents the most common lost mark.

Getting the four numbers is not the thing to watch for — the arithmetic here is easy
enough that she can be right for the wrong reason. The sorting habit and the labels
are what survive contact with a shuffled data set.

## Extend it

- **Do practice problem 195 with her out loud**, because it is the even-count case
  and the lesson never demonstrates it. Ten King Salmon high temperatures:
  `28, 17, 32, 12, 33, 26, 25, 25, 30, 18`. Sorted, that is
  `12, 17, 18, 25, 25, 26, 28, 30, 32, 33`. Mean: they total 246, so
  `246 ÷ 10 = 24.6`. Median: ten is even, so average the 5th and 6th —
  `(25 + 26) ÷ 2 = 25.5`, a value that is not in the data at all, which is worth
  pointing out. Mode: `25`. Range: `33 - 12 = 21`. If she gets 25.5 without being
  reminded which rule applies, the lesson has landed.
- **The same-mean challenge.** Ask her to invent two sets of five numbers that have
  the *same* mean and wildly different ranges. `10, 10, 10, 10, 10` and
  `0, 0, 10, 20, 20` both average 10. This is the reveal on her page turned into
  something she builds herself, and it is the fastest route to *why four numbers
  and not one*.
- **Collect her own data.** Time how long it takes her to walk to the letterbox, ten
  times. All four measures, on numbers she produced. Then ask which of the four she
  would quote if she were bragging, and which one you should ask for if you wanted
  to know whether she is *reliable*. That second question is the range, and framing
  it as reliability is what makes it stick.
- **Where medians beat means in real life.** House prices, incomes, house sizes.
  Ask her why the news says "median house price" and never "mean house price". A few
  enormous values would drag the mean somewhere that describes nobody. She has
  everything she needs from Idea 2 to work this out.

## Where this sits

DIVE Lesson 95, *Mean, Median, Mode and Range*. Reviews **Lessons 34, 55, 65 and
74** — page 1 lists them.

- **Lesson 74** is the one seeded in this course and the natural place to go back
  to if the *shape* argument is what she is losing. 74's whole thesis was that a
  chart represents data rather than containing it; this lesson is the same trade
  done with four numbers instead of a picture.
- **Lesson 65** is the one the book itself reaches for — frequency distributions,
  histograms, and the definition of a normal distribution. Everything on her page
  about that shape comes from what Lesson 95 says about 65, because 65 sits outside
  this course's seeded lessons and this guide has not read it directly. If the
  histogram is what is confusing her, her book's Lesson 65 is the place to look.
- **Lessons 34 and 55** are where an average was taught, and the book names them for
  exactly that reason. Also outside the seeded set. Go there only if the *mean*
  itself is the problem — which it usually is not, since she has been calculating
  averages for sixty lessons.

**Proficient** looks like: sorts the list, finds all four for an odd-count data set,
and reports a tie as a tie.
**Mastered** looks like: handles the even count without being reminded which rule
applies, labels her answers with the words, and can say what range is doing on a
list of middles when it is not pointing at a middle.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 95 (mean, median, mode and range) "
            "— idempotent.")

    LESSON_NUMBER = 95
    TITLE = "Mean, Median, Mode and Range — Three Middles and One Spread"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
