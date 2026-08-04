"""Saxon Pre-Algebra Lesson 74 — Data Interpretation and Representation with Charts.

Reviews Lessons 51, 65, 68 and 70 — the coordinate plane, bar graphs, and the
y = mx + b graphing the parent already taught her by hand. That is the hook:
Example 74.5 is not new mathematics, it is rise over run wearing a fish costume.

THE DATASET. Saxon prints one fish-catch dataset five different ways and states
its own point out loud: "Did you notice we are using the same data, just with
different chart types?" So the tool here is a SWITCHER, not five pictures.

The lesson's text pins four of the five months directly:
    August    4,000  (74.1 — four fish pictures at 1,000 each)
    June      1,000  (74.2 — estimated halfway between 0 and 2,000)
    September 5,000  (74.3)
    October   6,000  (74.3)
July is never stated in words — it lives only in a figure this file cannot see.
It is RECOVERED, not invented, from the lesson's own pie graph: 74.4 says October
is 33.3% of the catch, and October is 6,000, so the five months total 18,000, so
July = 18,000 - (1,000 + 4,000 + 5,000 + 6,000) = 2,000. Every other number the
lesson states then falls out of the same table, including the 1,250 fish/month of
Example 74.5.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use. Practice problems are reworded rather than transcribed.

    python manage.py seed_saxon_74 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

# One dataset. Five costumes. See the derivation of July in the module docstring.
FISH = [
    {"label": "June", "value": 1000},
    {"label": "July", "value": 2000},
    {"label": "Aug", "value": 4000},
    {"label": "Sept", "value": 5000},
    {"label": "Oct", "value": 6000},
]

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 74 · Pre-Algebra",
        "title": "The same numbers, wearing five different outfits",
        "thesis": "A chart does not *contain* the data — it **represents** it. "
                  "The numbers stay put; only the picture changes. So the real "
                  "question is never \"what does this chart say?\" but **\"is this "
                  "the right chart for this data?\"**",
        "formula": "chart  =  a picture of numbers",
        "roles": [
            {"tone": "start", "name": "the data",
             "text": "The actual measurements. These never change, no matter which "
                     "chart you draw."},
            {"tone": "move", "name": "the representation",
             "text": "The picture you chose. Some choices make the truth obvious. "
                     "Some hide it."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anyone bothers drawing the numbers",
        "paragraphs": [
            "Imagine a fisherman hands you a scrap of paper. On it: June 1,000. "
            "July 2,000. August 4,000. September 5,000. October 6,000. You can read "
            "that. But can you *see* it? Probably not — not in one glance.",
            "Now imagine those same five numbers as five bars, tallest on the right. "
            "Instantly you know something the list was hiding: **the catch is going "
            "up, and it is going up steadily.** Nobody had to tell you. You saw it.",
            "That is the entire job of a chart. Data goes in; a **pattern** comes "
            "out — and a pattern is something you can act on. The fisherman can now "
            "guess what November will bring. Nothing was added to the numbers. They "
            "were just put somewhere your eyes could do the work.",
            "Which is also why the *choice* of chart matters so much. Saxon makes "
            "this the point of the whole lesson: it takes **one** set of data and "
            "draws it five ways, so you can watch some pictures tell the truth "
            "clearly and others tell it badly.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 2, "tone": "start",
        "title": "One dataset. Five costumes.",
        "paragraphs": [
            "Below is the fish-catch data, and a row of buttons. Every button draws "
            "the **same five numbers**. Nothing is added and nothing is taken away.",
            "A **pictograph** counts in pictures — one little block stands for 1,000 "
            "fish, so you count blocks and multiply. A **bar graph** turns each "
            "number into a height. A **line graph** joins the dots. A **pie graph** "
            "turns each number into a slice of one whole. A **scatterplot** drops the "
            "bars and keeps only the dots.",
            "Click through all five and watch what each one makes easy — and what "
            "each one makes hard. That comparison *is* Lesson 74.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"I'm going to give you five numbers, and we're going to draw them "
                "five different ways. The numbers don't change once. Not one of them. "
                "Your job is to notice what each picture is good at — because that's "
                "the actual skill here, not the drawing.\"",
    }),

    (B.KIND_TOOL, {
        "title": "The same fish, five ways",
        "intro": "Tap each button. The five numbers underneath never move — only the "
                 "costume changes. Look for what each chart makes obvious.",
        "widget": "chart",
        # `trend` draws the dashed line through the first and last dot on the
        # scatterplot — the exact line Example 74.5 asks her to find the slope of.
        "config": {
            "data": FISH,
            "kinds": ["pictograph", "bar", "line", "pie", "scatter"],
            "per": 1000,
            "unit": "fish",
            "trend": True,
            "label": "one fish-catch dataset drawn five ways",
        },
        "after": "The data, in words: **June 1,000 · July 2,000 · August 4,000 · "
                 "September 5,000 · October 6,000.** All five months together come "
                 "to **18,000 fish** — which is the number the pie graph is quietly "
                 "dividing up.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "How to read any chart, every time",
        "steps": [
            {"label": "Find the key or the scale FIRST.",
             "detail": "Before you look at a single bar. On a pictograph the key says "
                       "what one picture is worth. On a bar or line graph the numbers "
                       "up the side do the same job. Skip this and every answer after "
                       "it is wrong by a factor you never see."},
            {"label": "Name the two axes out loud.",
             "detail": "A bar graph is a coordinate plane in disguise (Lesson 51). "
                       "Instead of (x, y) you have **(Month, Fish catch)**. Say which "
                       "is which before you read anything off it."},
            {"label": "Read the value — and say whether you *measured* or *estimated* it.",
             "detail": "Some values land exactly on a line. Others sit between two "
                       "lines and you have to judge. Both are allowed. Saying which "
                       "one you did is what keeps you honest."},
            {"label": "Only now, answer the question.",
             "detail": "Most chart questions are one subtraction, one multiplication "
                       "or one comparison. The reading is the hard part; the "
                       "arithmetic almost never is."},
        ],
        "after": "And one extra question, every single time: **was this the right "
                 "chart for this data?** That is the question Lesson 74 is really "
                 "training you to ask.",
    }),

    (B.KIND_WORKED, {
        "number": "74.1 – 74.2",
        "question": "Read August off the pictograph. Then use the bar graph to find "
                    "how many more fish were caught in August than in June.",
        "steps": [
            {"label": "Key first",
             "text": "The pictograph's key says **one fish picture = 1,000 fish**. "
                     "Nothing else can be done until that is read."},
            {"label": "Count, then multiply",
             "text": "August's row has 4 fish pictures. Four pictures, worth 1,000 "
                     "each.",
             "math": "4 × 1,000 = 4,000 fish"},
            {"label": "Now the bar graph — measure August, estimate June",
             "text": "August lands exactly on a line: 4,000. June does not — it sits "
                     "about **halfway between 0 and 2,000**, so 1,000 is a fair "
                     "estimate. Then it is one subtraction.",
             "math": "4,000 - 1,000 = 3,000 fish"},
        ],
        "answer": "4,000 fish · 3,000 more fish",
    }),

    (B.KIND_WORKED, {
        "number": "74.3 – 74.4",
        "question": "From the line graph: how many fewer fish were caught in September "
                    "than in October? From the pie graph: in which month was about "
                    "one third of the whole catch landed?",
        "steps": [
            {"label": "Read both months off the line graph",
             "text": "September is at 5,000 and October is at 6,000. October is the "
                     "bigger one, so October goes first in the subtraction."},
            {"label": "Subtract",
             "text": "September was the **smaller** month, so the answer is how many "
                     "*fewer* fish it landed.",
             "math": "6,000 - 5,000 = 1,000 fish"},
            {"label": "The pie graph asks a different kind of question",
             "text": "A pie slice is not a count — it is a **share of the whole**. "
                     "The whole is all 18,000 fish. One third of 18,000 is 6,000, and "
                     "6,000 is October. Read the other way round: October's slice is "
                     "33.3% of the pie, and 33.3% is basically one third.",
             "math": "6,000 / 18,000 = 1 / 3 = 33.3% → October"},
        ],
        "answer": "1,000 fish · October",
    }),

    (B.KIND_TABLE, {
        "caption": "The five costumes — what each one is good at, and what it hides",
        "headers": ["chart", "good at", "watch out for"],
        "rows": [
            {"cells": ["pictograph", "counting in friendly chunks",
                       "half a picture is half the value, not a whole one"]},
            {"cells": ["bar graph", "comparing amounts side by side",
                       "values between gridlines have to be estimated"]},
            {"cells": ["line graph", "showing change over time",
                       "it implies values BETWEEN the labels — often a lie"],
             "emphasis": True},
            {"cells": ["pie graph", "shares of one whole; percentages add to 100",
                       "it shows shares, not counts"],
             "emphasis": True},
            {"cells": ["scatterplot", "spotting a trend in scattered dots",
                       "the dots only *roughly* follow the trend line"]},
        ],
        "note": "The two shaded rows are the ones that mislead people. A line graph "
                "of monthly catches suggests you could read off \"the catch on "
                "August 17th\" — you cannot; nobody measured that. A pie graph "
                "answers *what share?* and refuses to answer *how many?* until you "
                "multiply by the whole.",
    }),

    (B.KIND_TRANSLATION, {
        "title": "Chart shorthand, decoded",
        "intro": "Charts are covered in little marks that assume you already know "
                 "what they mean. Here is what each one is a shorthand for.",
        "rows": [
            {"symbol": "= 1,000 fish",
             "plain": "the key — what one picture is worth",
             "example": "4 pictures means 4,000 fish"},
            {"symbol": "(Month, Fish catch)",
             "plain": "the axes, named — the same idea as (x, y)",
             "example": "(5, 6000) is October, 6,000 fish"},
            {"symbol": "33.3%",
             "plain": "a share of the whole, not a count",
             "example": "33.3% of 18,000 = 6,000"},
            {"symbol": "Δy",
             "plain": "the CHANGE in the up-and-down value",
             "example": "6,000 - 1,000 = 5,000"},
            {"symbol": "Δy / Δx",
             "plain": "slope — how much y changes per 1 of x",
             "example": "5,000 / 4 = 1,250 per month"},
            {"symbol": "trend",
             "plain": "the direction the dots roughly follow",
             "example": "\"roughly\" is doing real work — dots are never perfect"},
        ],
        "after": "**Δ is a Greek capital D**, and it stands for *difference*. `Δy` is "
                 "not Δ times y — it is one thing meaning \"how much y changed\". "
                 "That is the only new symbol in this lesson.",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 2, "tone": "move",
        "title": "A trend has a slope — and you already know how to find it",
        "paragraphs": [
            "Here is the part worth slowing down for. On the scatterplot the dots do "
            "not sit *exactly* on a line — but they nearly do. That near-line is "
            "called a **trend**.",
            "And a trend has a **steepness**, which is exactly the slope you already "
            "found when you graphed `y = mx + b`. Same rise over run. Same "
            "subtraction. The only difference is what the axes are called: instead of "
            "x and y you have **Month** and **Fish catch**.",
            "So the slope stops being an abstract tilt and becomes a sentence in "
            "English: *the catch grows by about 1,250 fish every month.* That "
            "sentence is what the whole lesson was built to let you say — and it is "
            "the same `m` from `y = mx + b`, just with its units spoken out loud.",
            "One thing to be careful about, because it is where nearly everyone slips: "
            "pick the two points **farthest apart** — Month 1 and Month 5. Two dots "
            "close together can be off-trend by luck, and a short run exaggerates it.",
        ],
    }),

    (B.KIND_STEPPER, {
        "title": "Example 74.5 — estimate the rate of change from the trend",
        "equation": "Month 1 → 1,000 fish        Month 5 → 6,000 fish",
        "steps": [
            {"label": "Look first",
             "text": "The months got renamed. June, July, August, September, October "
                     "became Month 1, 2, 3, 4, 5 — because you cannot subtract "
                     "\"June\" from \"October\", but you can subtract 1 from 5."},
            {"label": "Step 1 · write the two ends as ordered pairs",
             "text": "Farthest apart is best, so take the first and the last. The "
                     "pair is (Month, Fish catch) — the month goes first, exactly "
                     "like x does.",
             "math": "(1, 1,000)   and   (5, 6,000)"},
            {"label": "Step 2 · how much did the FISH change?",
             "text": "That is the rise — the up-and-down change, Δy. Bigger minus "
                     "smaller.",
             "math": "Δy = 6,000 - 1,000 = 5,000"},
            {"label": "Step 3 · how much did the MONTH change?",
             "text": "That is the run, Δx. Careful here: Months 1 to 5 is **4 gaps**, "
                     "not 5. Count the jumps, not the dots.",
             "math": "Δx = 5 - 1 = 4"},
            {"label": "Step 4 · divide, then say it in English",
             "text": "Rise over run. Then read the answer out loud as a sentence: "
                     "*the catch grows by about 1,250 fish per month.*",
             "math": "Δy / Δx = 5,000 / 4 = 1,250"},
        ],
    }),

    (B.KIND_MATH, {
        "display": "Δy / Δx  =  (6,000 - 1,000) / (5 - 1)  =  5,000 / 4  =  1,250",
        "note": "Read it left to right as a sentence: *the change in fish, divided by "
                "the change in months, is 1,250 fish per month.* Slope always has "
                "units — **something per something** — and saying them is how you "
                "check you divided the right way up.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "The line graph of this data is drawable — so why does Saxon say it "
                  "is the wrong chart here?",
        "answer": "Because a line **claims there are values in between**. It says you "
                  "could slide along it and read the catch halfway through August. "
                  "But nobody measured halfway through August — the catch was counted "
                  "**once a month**, so the in-between part of the line is invented. "
                  "The rule to keep: *just because you can draw a chart doesn't mean "
                  "it's the right one for the data.*",
    }),

    (B.KIND_ERRORS, {
        "title": "The five mistakes almost everyone makes",
        "items": [
            {"name": "Counting the pictures and forgetting the key.",
             "wrong": "August = 4",
             "right": "August = 4 × 1,000 = 4,000 fish",
             "note": "The single most common chart error there is. Make reading the "
                     "key the **first** thing you do, before your eye goes anywhere "
                     "near the rows."},
            {"name": "Rounding a half picture away.",
             "wrong": "3½ planes → 300,000 tourists",
             "right": "3½ planes = 3 × 100,000 + 50,000 = 350,000 tourists",
             "note": "Practice problem 1 has exactly this shape: whole planes are "
                     "100,000 tourists each, so **half a plane is 50,000**. A half "
                     "symbol is half the key's value — never a whole one, never zero."},
            {"name": "Reading a pie slice as a count.",
             "wrong": "October's slice says 33.3 → 33 fish",
             "right": "18,000 / 3 = 6,000 fish",
             "note": "A pie graph answers *what share?* To turn a share into a count "
                     "you must multiply by the whole — and the whole here is all "
                     "18,000 fish."},
            {"name": "Counting the dots instead of the gaps in the run.",
             "wrong": "Months 1 to 5, so Δx = 5",
             "right": "Δy / Δx = 5,000 / 4 = 1,250",
             "note": "Five fence posts, four gaps. Using 5 gives 1,000 fish/month — "
                     "wrong, and plausible enough that nobody catches it. Count the "
                     "**jumps between** the points."},
            {"name": "Guessing an estimated value instead of using the scale.",
             "wrong": "June's bar is short, so June = 0",
             "right": "June sits halfway from 0 to 2,000 → 2,000 / 2 = 1,000 fish",
             "note": "Estimating is allowed and expected. Guessing is not. Find the "
                     "two gridlines the bar sits between, and place it between them "
                     "on purpose."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A chart **represents** data. The numbers never change — only the picture.",
            "**Read the key or the scale first.** Every other answer depends on it.",
            "A pie slice is a **share**, not a count. Multiply by the whole to get a "
            "count.",
            "Just because you *can* draw a chart doesn't mean it's the **right** one "
            "for the data.",
            "A trend has a slope, and it is the same rise over run as `y = mx + b`: "
            "`Δy / Δx`. **Count the gaps, not the dots.**",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 74 first. If it didn't quite click, this is here to fix "
    "that — and there's a chart you can flip between five different types. That "
    "flipping IS the lesson: one set of numbers, five pictures, and the skill is "
    "noticing which picture tells the truth best."
)

PARENT_CONTENT = """## The big idea

Saxon does something unusual in this lesson and it is easy to miss: it takes
**one dataset — a fisherman's monthly catch — and draws it five ways.** Pictograph,
bar, line, pie, scatterplot. Same numbers every time.

The point is not "here are five chart types, memorise them." The point is
**choosing**. Some pictures make the truth obvious; some hide it; the line graph
here actively implies something false. So the question she should end the lesson
able to ask is *"is this the right chart for this data?"* — not just *"what does
this chart say?"*

The data, so you have it in front of you:

| month | fish | as a share |
|---|---|---|
| June | 1,000 | 5.6% |
| July | 2,000 | 11.1% |
| August | 4,000 | 22.2% |
| September | 5,000 | 27.8% |
| October | 6,000 | 33.3% |
| **total** | **18,000** | **100%** |

The last example (74.5) is the one worth your time. It looks like a new topic and
it is not: **it is the slope you already taught her**, with Month on the bottom
axis instead of x and Fish catch up the side instead of y. `Δy / Δx = 5,000 / 4 =
1,250 fish per month.` If she can graph `y = mx + b`, she can do this — she just
has to be told they are the same thing, out loud, because the textbook never
quite says it.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Read her the five numbers off a scrap of paper — *"June a thousand, July two
   thousand, August four thousand, September five, October six."* Then ask:
   **"What's happening to the fishing?"** She will hesitate. That hesitation is
   the whole argument for charts, and it is worth letting it sit for a second.
2. Now open the lesson page and press **bar**. Ask the same question again:
   **"What's happening?"** — this time it is instant. Say: *"Nothing changed
   except where you put your eyes. That's what a chart is for."*
3. Press through **pictograph → line → pie → scatter**, and at each one ask
   **"What is this one good at?"** Take any reasonable answer. At the **line**,
   push once: **"Could you use this to tell me the catch on August 17th?"** You
   want her to realise the line is offering an answer nobody measured.
4. At the **pie**, ask: **"Which month is about a third?"** (October.) Then the
   follow-up that matters: **"How many fish is that?"** She has to multiply by
   18,000. That gap — share versus count — is the pie graph's whole trap.
5. Now Example 74.5, and here are the literal words for the part the video
   skipped. Point at the first and last dots: *"Fish went from a thousand to six
   thousand. How much is that?"* (5,000.) *"And how many months did that take?"*
   — **make her count the jumps, not the dots** (4, not 5). Then: *"Five thousand
   fish over four months. So per month?"* (1,250.) Finish with: **"That number
   has a name. It's the slope. It's the m in y = mx + b — the same one you did
   with me. Slope is just how much you get per one step across."**

That last line is the sentence to say. Everything else in the lesson she can get
from the page; that connection she needs from you.

## The classic mix-ups, with what she'll actually write

- **Counting pictures without the key.** She writes **4** for August instead of
  **4,000**. Fix it by making "read the key first" a physical habit — finger on
  the key before her eye goes to the rows.
- **Rounding away a half symbol.** With planes worth 100,000 each, 3½ planes gets
  written as **300,000** instead of **350,000**. Half a symbol is half the key.
- **Reading a pie slice as a count.** She sees 33.3% and writes **33 fish**
  instead of **6,000**. Ask "a third of *what*?" until the "of the whole" is
  automatic.
- **Counting dots instead of gaps.** Months 1 to 5 becomes Δx = **5**, giving
  **1,000 fish per month** instead of 1,250. This is the dangerous one — the
  wrong answer is a round number and looks completely reasonable. Fence posts and
  gaps is the image that fixes it.
- **Subtracting backwards.** September minus October gives **−1,000**, and she
  writes "1,000 more" when the question asked "how many fewer." Have her name the
  bigger month out loud before the pencil moves.

## What to watch her do

Watch her **hands**, in this order:

1. Does her finger go to the **key or the scale first**, before it goes to the
   data? If her eye lands on a bar before it lands on the numbers up the side,
   the habit isn't built yet — and that habit is most of this lesson's grade.
2. On the slope example, does she **tap the gaps between the dots** while
   counting the run — or does she tap the dots? Tapping dots gives 5 and a wrong
   answer that looks right. This is visible from across the table.
3. Does she **say the units** when she reports the slope — "1,250 fish per
   month," not just "1,250"? Naming the units is what proves she divided the
   right way up rather than getting lucky.
4. When she estimates a between-the-lines value, does she **point at the two
   gridlines it sits between** before writing a number? Estimating is fine.
   Guessing is not, and the difference is exactly that gesture.

## Extend it

- **Ask her to predict November.** The trend says +1,250 a month, so about 7,250.
  Then ask the better question: *"How much would you bet on that?"* A trend is
  evidence, not a promise — and 12 is a good age to start noticing the difference.
- **Make her the villain.** Hand her the same five numbers and ask her to draw a
  chart that makes the fishing look like it barely improved. (Start the vertical
  axis high, or squash the scale.) Then one that makes it look explosive. Nothing
  teaches "charts can mislead" like being the one who did it.
- **Go find one in the wild.** A chart in a news article or on a cereal box. Ask
  the two lesson questions: *what's the key or scale?* and *is this the right
  chart for this data?*

## Where this sits

DIVE Lesson 74, "Data Interpretation and Representation with Charts." No new
rules — it reviews **Lessons 51** (the coordinate plane; a bar graph is one in
disguise), **65** (making bar graphs / histograms from data), and **68 and 70**
(graphing linear equations, which is where the slope in Example 74.5 comes from).

If she is lost on the *slope* part rather than the chart-reading, go back to 68
and 70 — that is the y = mx + b graphing you already did together, and it is the
same arithmetic.

**Proficient** looks like: reads a value off any of the five chart types
correctly, key included, and gets 74.5's slope right with prompting.
**Mastered** looks like: says "that's the wrong chart for this data" without being
asked, and reports the slope with its units — "1,250 fish per month."
"""


class Command(SaxonSeedCommand):
    help = "Seed Saxon Pre-Algebra Lesson 74 (charts and data) — idempotent."

    LESSON_NUMBER = 74
    TITLE = "The Same Numbers, Five Different Outfits — Charts and Data"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
