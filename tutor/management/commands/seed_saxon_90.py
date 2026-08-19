"""Saxon Pre-Algebra Lesson 90 — The Derivative and Slope; Solving Multivariable
Equations.

Reviews Lessons 39, 68, 78 and 81. Lesson 81 is the hook for the first half and
the book says so itself: 81B defined calculus as the study of rates of change, and
Ex. 81.3 found the slope of y = x² between x = 1 and x = 2. Lesson 90 runs that
exact example again with Δx a hundred times smaller and gives the answer a new
name. Lesson 68 is where the slope underneath it all started. Lesson 39 is the
hook for the second half — the book names it directly, as the place where general
equations written in letters first appeared — and Lesson 78B is the same
rearranging with the evaluate step removed, which the book also says out loud.

Two halves, so two runs of blocks: 90A is the derivative (Example 90.1) and 90B is
solving an equation for one letter while the other letters stay letters
(Example 90.2).

Judgement calls:

* The source prints two diagrams side by side at x = 2 — the Lesson 81B secant
  (Δy=5, Δx=1, slope=5) and a near-tangent (Δy=0.04, Δx=0.01, slope=4) with a
  zoomed-in inset. The pictures are not reproduced. Both label their own numbers
  in the text, so the page works from those numbers and says in one sentence that
  the drawing is in her book. The left-hand one is already drawn on her Lesson 81
  page as a KIND_TOOL grid, so Idea 3 sends her back to it.
* Those printed labels are ROUNDED. 2.01² is 4.0401, so the honest figures are
  Δy = 0.0401 and a slope of 4.01 — which is why the book's own prose beside the
  picture says the slope drops to "around 4". Her page carries the book's 0.04 and
  4 and then says plainly where the extra digits went, the same treatment Lesson 86
  gave the guide's 0.79863.
* The shrinking-Δx table runs Δx = 1, 0.1, 0.01, 0.001 at x = 1. The first and
  third rows are the book's own (Ex. 81.3 and Ex. 90.1); the middle and last are
  the identical sum at the in-between gaps the book explicitly invites — "if we can
  decrease ∆x from 1 to 0.01, we can decrease from 0.01 to .001, and so on" — and
  the table's note says which rows are which.
* Practice Set 90 opens "For problems marked (C), calculator use is allowed but
  not required", and problem 886 is *find tan 1°* — the very button the
  tangent-line warning says she does not need. So the warning is scoped to the
  teaching and names 886 as the Lesson 86 review problem it is, rather than
  telling her there is no calculator on a page that has one.
* No power rule anywhere. The source never gives her one, so the reveal lets her
  line up 2, 4 and 6.01 and notice, and then says in as many words that noticing is
  the right amount to do with it today.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_90 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 90 · Pre-Algebra",
        "title": "Derivative means slope",
        "thesis": "Your book prints that sentence on a line of its own, and it is "
                  "the whole first half of the lesson. Not a new procedure — a new "
                  "**word** for the slope you have been finding since Lesson 68. "
                  "The rest of that half is about how close together you put the two "
                  "points; the second half is an unrelated, shorter subject.",
        "formula": "Δy / Δx = 0.0201 / 0.01 = 2.01",
        "roles": [
            {"tone": "start", "name": "Δx — the gap, and you pick it",
             "text": "How far apart the two points are, sideways. Lesson 81 picked 1 "
                     "because 1 is easy. Today it gets small, and then smaller."},
            {"tone": "move", "name": "Δy / Δx — the slope of the line through them",
             "text": "Rise over run, unchanged. Shrink the gap and this number stops "
                     "moving. Where it stops is the derivative."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "How fast is something moving in a photograph?",
        "paragraphs": [
            "Your book puts a photograph at the top of this lesson: a surfer in the "
            "middle of an aerial, caught by a high-speed camera. The motion was "
            "continuous — the surfer never stopped moving — but the camera cut it "
            "into separate frozen frames.",
            "Pick one frame and ask a fair question. **How fast was the surfer moving "
            "in that photo?** In the photo nothing is moving at all. It is a still "
            "picture. And yet everybody knows the surfer was moving, and roughly how "
            "fast.",
            "With the mathematics you already have you cannot answer that from one "
            "frame, because every speed you have ever calculated needed **two** "
            "moments: where they were, and where they were a moment later. Divide how "
            "far they moved by how long it took. That is a speed, and it is also a "
            "slope — Lesson 68's rise over run, Lesson 81's Δy / Δx.",
            "But it is an *average* over that stretch, and the longer the stretch the "
            "more it lies. Two frames a whole second apart give you their average "
            "speed across a second, and the entire aerial happened inside that second.",
            "So move the frames closer together. Half a second. A hundredth. And here "
            "is the thing worth the whole lesson: as the gap shrinks the answer does "
            "not fly off anywhere. It **settles**. It heads towards one particular "
            "number, and that number is what the surfer was doing in the single "
            "frozen frame.",
            "That settled number is called the **derivative**, and your book's way of "
            "saying all of the above is three words long: *derivative means slope.* "
            "The second half of the lesson is unrelated and much shorter — it is "
            "about what to do when an answer is allowed to have letters in it.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 4, "tone": "start",
        "title": "One word swapped for another",
        "paragraphs": [
            "Your book offers two ways to describe a derivative, a simple one and a "
            "complicated one, and it tells you which to hold on to. The simple one is "
            "a swap of vocabulary.",
            "Think to yourself: **derivative means slope.** That is the book's own "
            "sentence, printed on a line by itself. Then it adds the condition that "
            "makes a slope a *derivative* — the slope of a line drawn between two "
            "points on a function that are an **infinitesimally small Δx** apart.",
            "So the arithmetic does not change today. You will do exactly what you "
            "did in Ex. 81.3: turn what you were given into two points, subtract to "
            "get Δy, subtract to get Δx, divide. Your book puts it in one line — *the "
            "only difference in solving those problems and what we are about to do is "
            "that now we will study smaller values of ∆x.*",
            "You have been rehearsing this without being told. The book lists the "
            "problems by name: **81.3, 83.6, 84.7, 86.9 and 88.11** — every one of "
            "them a slope on `y = x²`. All of them used Δx = 1 except 83.6, which "
            "used a *bigger* gap, Δx = 2. Today the gap goes the other way, and it "
            "keeps going.",
            "And that is the only reason Lesson 81 could not already call its answer "
            "a derivative. Δx = 1 is not a small gap. It is a whole unit of x, and "
            "the slope you get across it belongs to the stretch, not to the point.",
        ],
    }),

    (B.KIND_SAY, {
        "text": "\"Don't learn anything new for a minute. Just do the slope you "
                "already know — the change in y over the change in x — except do it "
                "between two points that are really close together. One, and "
                "one-point-oh-one. That's it. That's the lesson. When the two points "
                "are that close, the answer gets a new name and we call it the "
                "derivative. Same sum. New word. Now tell me what Δy is.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 4, "tone": "move",
        "title": "Shrink the gap and watch the answer settle",
        "paragraphs": [
            "Here is the experiment this lesson is actually running. It is worth doing "
            "on paper, because the result is the point.",
            "Take `f(x) = x²` and stand at **x = 1**. In Lesson 81 you found the slope "
            "from x = 1 across to x = 2 — a gap of Δx = 1 — and got **3**. Now do the "
            "same sum with a smaller gap. Then a smaller one. Then smaller again.",
            "The answers do not wander. They come down, and then they almost stop "
            "moving: 3, then 2.1, then 2.01, then 2.001. Each drop is smaller than "
            "the one before it, each answer is nearer to **2** than the one before "
            "it, and not one of them ever gets there.",
            "Your book has a word for a number that a run of answers heads towards "
            "without arriving. The slope **approaches a limit**. That limit is the "
            "derivative at x = 1.",
            "Notice how the question had to change shape to have an answer at all. "
            "You are not being asked what the slope **is** at x = 1 — a single point "
            "has no slope, because there is nothing to divide by. You are asked what "
            "the slope **heads towards** as the gap closes. The second question has an "
            "answer even though the first one does not, and swapping one for the "
            "other is the trick the whole of calculus is built on.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "One function, one place, four different-sized gaps — f(x) = x² "
                   "at x = 1",
        "headers": ["Δx", "the two points", "Δy", "Δy / Δx", "where it came from"],
        "rows": [
            {"cells": ["1", "(1, 1) and (2, 4)", "4 − 1 = 3", "3 ÷ 1 = 3",
                       "Ex. 81.3"], "emphasis": True},
            {"cells": ["0.1", "(1, 1) and (1.1, 1.21)", "1.21 − 1 = 0.21",
                       "0.21 ÷ 0.1 = 2.1", "the same sum, in between"]},
            {"cells": ["0.01", "(1, 1) and (1.01, 1.0201)", "1.0201 − 1 = 0.0201",
                       "0.0201 ÷ 0.01 = 2.01", "Ex. 90.1"], "emphasis": True},
            {"cells": ["0.001", "(1, 1) and (1.001, 1.002001)",
                       "1.002001 − 1 = 0.002001", "0.002001 ÷ 0.001 = 2.001",
                       "the same sum, in between"]},
        ],
        "note": "The two shaded rows are your book's. The top one is Ex. 81.3 from "
                "Lesson 81; the third is Ex. 90.1 on this page. The other two are the "
                "identical sum at the in-between gaps, and the book invites you to do "
                "exactly that: *if we can decrease ∆x from 1 to 0.01, we can decrease "
                "from 0.01 to .001, and so on.*\n\n"
                "Now read the fourth column downwards. **3 → 2.1 → 2.01 → 2.001.** "
                "Every row is closer to 2 and no row is 2. That is what *approaches a "
                "limit* means, and it is the one genuinely new idea in the first half "
                "of this lesson.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 90.1 — the same problem as Ex. 81.3, with the gap 100 "
                 "times smaller",
        "equation": "f(x) = x²      f(1) = 1      f(1.01) = 1.0201      find Δy / Δx",
        "steps": [
            {"label": "Look first",
             "text": "Your book's own opening move is to notice what this is **not**. "
                     "*Observe this problem is similar to Ex. 81.3. The only "
                     "difference is now ∆x is 100 times smaller.* No new method is "
                     "coming. You are following the same process you used in Ex. 81.3 "
                     "and, before that, in Ex. 77.2."},
            {"label": "Step 1 · turn the function values into two points",
             "text": "`f(1) = 1` means *when x is 1, y is 1* — so that is the point "
                     "(1, 1). And `f(1.01) = 1.0201` is the point (1.01, 1.0201). "
                     "This is the translation step, and it is the one people skip.",
             "math": "f(1) = 1  →  (1, 1)        f(1.01) = 1.0201  →  (1.01, 1.0201)"},
            {"label": "Step 2 · Δy — how far y moved",
             "text": "Second y minus first y. Keep that order, and keep every digit "
                     "you were given: this subtraction runs all the way out to the "
                     "fourth decimal place.",
             "math": "Δy = 1.0201 - 1 = 0.0201"},
            {"label": "Step 3 · Δx — how far x moved",
             "text": "Second x minus first x, the same order. You can see this one in "
                     "the question before you subtract anything — it is the gap you "
                     "were handed.",
             "math": "Δx = 1.01 - 1 = 0.01"},
            {"label": "Step 4 · divide",
             "text": "Change in y over change in x. Both numbers are small and the "
                     "answer is not, because you are dividing a small number by a "
                     "smaller one. If your answer came out tiny, you divided the "
                     "wrong way round.",
             "math": "Δy / Δx = 0.0201 / 0.01 = 2.01"},
            {"label": "Step 5 · say what the 2.01 is",
             "text": "Your book's sentence: *the slope of a tangent line at x = 1 "
                     "should equal about 2.* Read the hedging honestly. You have not "
                     "been handed a way to prove it is exactly 2. You have been "
                     "handed a number very close to 2, and a reason to believe the "
                     "next one down would be closer still."},
            {"label": "Step 6 · compare it with Ex. 81.3 — that is the actual question",
             "text": "Lesson 81 got **3** for this same function at this same place. "
                     "This lesson gets **2.01**. Your book does not call the 3 wrong; "
                     "it says 2.01 is *more accurate*. The 3 was an honest slope "
                     "across a whole unit of x. The 2.01 is a slope across a "
                     "hundredth, so it belongs to x = 1 itself rather than to the "
                     "stretch lying beside it.",
             "math": "Ex. 81.3, Δx = 1:   3        Ex. 90.1, Δx = 0.01:   2.01"},
        ],
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 4, "tone": "start",
        "title": "The tangent line, and the part you take on trust",
        "paragraphs": [
            "The line you have been drawing deserves a name. A line drawn through two "
            "points on a function that are a tiny Δx apart is a **tangent line** — "
            "your book's definition is *a line that touches a function essentially at "
            "one point*.",
            "Watch the word *essentially*. In the body of the lesson your book is even "
            "more careful and says a tangent line touches the function at **almost** "
            "one point. Almost, because there are really two points sitting there. You "
            "needed two to have a slope at all, and the zoomed-in picture in your book "
            "shows them apart.",
            "Then the book stops and admits something, in its own words: *this is one "
            "of those \"faith things\" about calculus.* If you can shrink Δx from 1 to "
            "0.01, you can shrink it from 0.01 to 0.001, and keep going — down to an "
            "**infinitesimal**, a Δx so small you cannot calculate it or picture it. "
            "Nobody performs that last step. You trust it exists, and you agree to "
            "treat the two points as one point. Lesson 81 ended on the same idea and "
            "called it a reasonable faith rather than a blind one.",
            "One warning about vocabulary, and your book flags it in its own "
            "definitions rather than letting you find out the hard way. **The tangent "
            "here has nothing to do with the tangent in Lesson 86.** There, tangent "
            "was a ratio of two sides of a right triangle and it lived on a calculator "
            "button. Here it is a line touching a curve. Same six letters, two "
            "unrelated jobs.",
            "Your lesson draws all of this at **x = 2** rather than at x = 1, in two "
            "pictures side by side. Those pictures are in your book and are not copied "
            "here — but each one labels its own numbers, so nothing on this page "
            "depends on seeing them. On the **left** is the Lesson 81B line from x = 2 "
            "to x = 3: Δy = 5, Δx = 1, slope = **5**. That picture is already drawn on "
            "your Lesson 81 page, so go and look at it there. On the **right** is the "
            "line from x = 2 to x = 2.01, labelled Δy = 0.04, Δx = 0.01, slope = "
            "**4** — with a zoomed-in view beside it, because at that scale the two "
            "points are one dot.",
            "So at x = 2 the slope falls from 5 to about 4 as the gap closes, exactly "
            "the way it fell from 3 to about 2 at x = 1. Two different places, one "
            "behaviour: shrink Δx and the number settles.",
            "One honest note about those printed labels. Work the right-hand picture "
            "out for yourself and you get Δy = **0.0401** and a slope of **4.01**, "
            "because 2.01 × 2.01 is 4.0401. The diagram is showing you rounded labels "
            "— which is why the sentence beside it says the slope drops to *around* 4. "
            "Example 90.1 keeps its extra digits and answers 2.01 rather than 2, so "
            "keep yours too, and round only when a question asks you to.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "f '(x)  =  lim  [ f(x + Δx) - f(x) ] / Δx     as  Δx → 0",
        "note": "This is the complicated way of describing a derivative, and your book "
                "prints it and then tells you in the same breath not to worry about "
                "it: *you don't need to study and understand this right now, we are "
                "simply presenting this for you to get used to the symbols used in "
                "calculus.* Take it at exactly that.\n\n"
                "You can already read most of it, though. `f(x + Δx) - f(x)` is the "
                "second y minus the first y — that is **Δy**, written out the long "
                "way. Underneath it is **Δx**. So the fraction is Δy / Δx, the slope "
                "you have been computing all lesson, and your book prints that shorter "
                "version too: **f '(x) = lim Δy / Δx as Δx → 0**. The `lim` with "
                "`Δx → 0` under it is an instruction in shorthand — *let the gap shrink "
                "towards nothing, and tell me where the answer settles.* It is the "
                "table above, said in symbols.",
    }),

    (B.KIND_TABLE, {
        "caption": "Your book's own chart — one set of ideas, two vocabularies",
        "headers": ["exploring calculus, where Δx is larger",
                    "actual calculus, where Δx is an infinitesimal"],
        "rows": [
            {"cells": ["slope", "derivative"], "emphasis": True},
            {"cells": ["Δx", "dx"]},
            {"cells": ["Δy", "dy"]},
            {"cells": ["Δy / Δx", "dy / dx,   f '(x)"], "emphasis": True},
        ],
        "note": "The left column is where you have been living since Lesson 68. The "
                "right column is where the rest of calculus happens. The only thing "
                "that changed is that Δx stopped being a number you picked and became "
                "an infinitesimal — and on the page, **the straight Δ becomes a d.**\n\n"
                "Why two sets of symbols for one idea? Because two people arrived at "
                "this at once. Newton wrote **f '(x)**, or just **y'**. Leibniz wrote "
                "**Δy / Δx** and **dy / dx**. Newton usually gets the credit for "
                "discovering calculus, but your book says Leibniz's notation is the "
                "better one to meet first, because it keeps reminding you that the "
                "thing is a *fraction* — a change in the output over a change in the "
                "input.",
    }),

    (B.KIND_TOOL, {
        "title": "Watch the answer settle",
        "intro": "The four gaps from the shrinking-Δx table further up this page, "
                 "drawn. Each bar is the slope that one value of Δx produced for "
                 "`f(x) = x²` at x = 1 — 3, then 2.1, then 2.01, then 2.001. The "
                 "gridlines are whole numbers, so the one marked **2** is the line to "
                 "keep your eye on.",
        "widget": "chart",
        # Bars only, deliberately. The `chart` widget draws a control button per
        # kind and prints a fixed note under each, and the note baked into `line`
        # is Lesson 74's ("for monthly counts that is not really true") — true
        # there, nonsense here. One kind means no buttons and no wrong sentence.
        # The values top out at 3, so niceScale puts gridlines on the whole
        # numbers and 2 becomes a printed line the last three bars stop just above.
        "config": {
            "data": [
                {"label": "Δx = 1", "value": 3},
                {"label": "Δx = 0.1", "value": 2.1},
                {"label": "Δx = 0.01", "value": 2.01},
                {"label": "Δx = 0.001", "value": 2.001},
            ],
            "kinds": ["bar"],
            "label": "the slope of y = x² at x = 1 for four shrinking values of Δx",
        },
        "after": "Two things to notice, and the second one is the lesson. **One:** "
                 "nearly all the movement happened in the very first shrink. From "
                 "Δx = 1 to Δx = 0.1 the bar drops most of a whole unit; after that it "
                 "barely moves at all. **Two:** the last three bars are nearly the "
                 "same height, and every one of them stops just *above* the "
                 "gridline at 2. The numbers under them are still coming down — "
                 "2.1, then 2.01, then 2.001 — but by so little that the drawing "
                 "can barely show it. They are getting closer to 2 and none of "
                 "them lands on it. "
                 "That is *approaching a limit*, drawn.\n\n"
                 "One fair objection, worth saying out loud: four bars cannot **prove** "
                 "the answer settles on 2 rather than on 1.999. They cannot, and your "
                 "book does not claim they do — it says the slope *should equal about "
                 "2*, and it calls that last step down to an infinitesimal one of the "
                 "faith things about calculus.",
    }),

    (B.KIND_REVEAL, {
        "prompt": "This is problem 190, the first on your practice set — work it there "
                  "first, then open this to check yourself. For f(x) = x², f(3) = 9 "
                  "and f(3.01) = 9.0601. What is the rate of change between f(3) and "
                  "f(3.01)?",
        "answer": "**6.01.** The two points are (3, 9) and (3.01, 9.0601), so it is "
                  "Example 90.1 with different numbers:   →   Δy = 9.0601 - 9 = "
                  "0.0601   →   Δx = 3.01 - 3 = 0.01   →   Δy / Δx = 0.0601 / 0.01 = "
                  "**6.01**\n\n"
                  "Your practice set then asks you to compare that with Practice Set "
                  "81.3, which was this same problem with Δx = 1 and came out at "
                  "**7**. Same story as Ex. 90.1: the wide gap gave 7, the narrow gap "
                  "gives 6.01, and the narrow one is the answer that belongs to x = 3 "
                  "itself.\n\n"
                  "Now set the three places beside each other, because something is "
                  "sitting there in plain view.   →   at x = 1 the slope settles near "
                  "**2**   →   at x = 2 your book's picture gives about **4**   →   at "
                  "x = 3 you have just found **6.01**   →   2, 4, 6.\n\n"
                  "That is not a coincidence. It is also not in this lesson: Saxon has "
                  "given you no rule for it and you are not expected to produce one. "
                  "Noticing it is exactly the right amount to do with it today.",
    }),

    (B.KIND_IDEA, {
        "n": 4, "of": 4, "tone": "move",
        "title": "When the answer is allowed to be an expression",
        "paragraphs": [
            "Halfway down the page the lesson changes subject completely, and this "
            "half is much shorter than the first.",
            "Every equation you have solved until now ended in a number. `x = 7`. That "
            "is what an answer looked like. Section 90B says it does not have to.",
            "Some equations have **more than one variable** — that is the whole of "
            "what *multivariable* means — and when you solve one of them for x, the "
            "answer comes out with letters still in it. `x = y + z` is a finished "
            "answer. It is not half-done, and you are not stuck.",
            "You have met equations shaped like this twice already, and your book "
            "points at both. **Lesson 39** is the first: the general equations in its "
            "Rules — the additive and multiplicative properties of equality — are "
            "written in letters precisely because they hold for every number you could "
            "put in. **Lesson 78B** is the second: the scientific formulas where you "
            "rearranged to get the unknown by itself.",
            "And here is the promise the book makes before you start, which is worth "
            "hearing: these will probably feel **easier** than Lesson 78B, because 78B "
            "made you rearrange *and then* evaluate. Today there is nothing to "
            "evaluate. You rearrange, and then you stop.",
            "So the only new thing in 90B is knowing when you are finished. **You are "
            "finished when the letter you were asked for is alone on one side.** Not "
            "when the other letters have gone — they are not going anywhere.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe",
        "title": "Three moves, and the third one is knowing you are done",
        "steps": [
            {"label": "Circle the letter you were asked for.",
             "detail": "The instruction says *solve for x*, or *solve for y*, and that "
                       "is the entire question. Practice problem 290 gives you "
                       "`x + y = z` and asks for **y** — not x, even though x is "
                       "written first. Circle it before your pencil touches anything "
                       "else."},
            {"label": "Ask what is being done to that letter, and undo it on both sides.",
             "detail": "This is Lesson 39 and nothing more. Something **added** to it "
                       "→ subtract that from both sides. Something **multiplied** by "
                       "it → divide both sides by that. Treat every other letter "
                       "exactly as you would treat a 5: it is a number nobody has told "
                       "you yet.",
             "math": "x - y = z      →      add y to both sides"},
            {"label": "Stop when your letter is alone.",
             "detail": "Alone means: on its own side, with nothing added to it and "
                       "nothing multiplied by it. Whatever is sitting on the **other** "
                       "side may be as lettery as it likes. `x = y + z` is done. "
                       "`x = a/y` is done."},
        ],
        "after": "One check, and it costs about five seconds. Put your finished answer "
                 "back into the original equation in your head. `x = y + z` back into "
                 "`x - y = z` gives `(y + z) - y = z`, and the two y's cancel, so it "
                 "holds. If the two sides do not agree, you undid the wrong thing.",
    }),

    (B.KIND_WORKED, {
        "number": "90.2",
        "question": "Solve each equation for x.    a) x - y = z     b) xy = a",
        "steps": [
            {"label": "a) What is happening to the x?",
             "text": "There is a **y being subtracted** from it, and nothing else is "
                     "going on. Subtraction is undone by addition, so add y to both "
                     "sides — the Lesson 39 move, done to a letter instead of a "
                     "number."},
            {"label": "a) Do it, then write what is left",
             "text": "Your book prints both lines, so write both. On the left, `-y` "
                     "and `+y` cancel each other out and the x is alone. On the right "
                     "you have z + y, which your book writes as **y + z** — addition "
                     "does not care about the order, and that is the tidier way "
                     "round. That is the answer. There is nothing further to do to it.",
             "math": "x - y + y = z + y   →   x = y + z"},
            {"label": "b) What is happening to the x now?",
             "text": "It is being **multiplied** by y, because `xy` means x times y. "
                     "Multiplication is undone by division, so divide both sides by "
                     "y — and again your book prints both lines."},
            {"label": "b) Do it, then write what is left",
             "text": "On the left the y's divide out and x stands alone. On the right, "
                     "a divided by y, written as the fraction a/y. Finished — and "
                     "notice you were never told what a or y are, and never needed to "
                     "be.",
             "math": "xy ÷ y = a ÷ y   →   x = a/y"},
        ],
        "answer": "x = y + z for part a   ·   x = a/y for part b",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "This lesson hands you a page of symbols and then tells you not to "
                 "panic about most of them. Here is what each one is short for. The "
                 "four calculus symbols near the bottom — `lim`, `Δx → 0`, `f '(x)` "
                 "and `dy / dx` — you are expected to **recognise**, not to use yet; "
                 "that is your book's own instruction about those, not a shortcut. "
                 # "The last two" had no noun after it, so it read as the four
                 # calculus symbols just listed — telling her she uses f '(x)
                 # and dy/dx today, which is the opposite of the same sentence's
                 # first half. The rows she does use are the bottom two.
                 "The bottom two rows — `multivariable` and `solve for x` — are "
                 "the ones you actually use today.",
        "rows": [
            {"symbol": "Δx", "plain": "the change in x — how far apart your two points "
                                      "are, sideways. YOU choose it",
             "example": "Δx = 0.01"},
            {"symbol": "Δy", "plain": "the change in y — how far the function's output "
                                      "moved between those same two points",
             "example": "Δy = 0.0201"},
            {"symbol": "Δy / Δx", "plain": "the slope of the line through the two "
                                           "points. Rise over run, Lesson 68, "
                                           "unchanged",
             "example": "0.0201 / 0.01 = 2.01"},
            {"symbol": "f(1.01)", "plain": "what the function gives back when 1.01 "
                                           "goes in. It is a y, so it makes a point "
                                           "with the 1.01",
             "example": "(1.01, 1.0201)"},
            {"symbol": "tangent line", "plain": "a line touching a function "
                                                "essentially at one point. NOT the "
                                                "tangent of Lesson 86",
             "example": "the line at x = 1"},
            {"symbol": "infinitesimal", "plain": "a value too small to calculate or "
                                                 "picture, which you agree to trust "
                                                 "exists",
             "example": "Δx smaller than any number"},
            {"symbol": "lim", "plain": "limit — the number a run of answers heads "
                                       "towards without necessarily arriving",
             "example": "3, 2.1, 2.01, 2.001 → 2"},
            {"symbol": "Δx → 0", "plain": "printed underneath lim: let the gap shrink "
                                          "towards nothing",
             "example": "lim as Δx → 0"},
            {"symbol": "f '(x)", "plain": "read \"f prime of x\". Newton's way of "
                                          "writing THE DERIVATIVE OF f(x) — notation, "
                                          "not a new operation",
             "example": "y ' means the same"},
            {"symbol": "dy / dx", "plain": "Leibniz's way of writing the derivative. "
                                           "The d is a Δ that has shrunk to an "
                                           "infinitesimal",
             "example": "same thing as f '(x)"},
            {"symbol": "multivariable", "plain": "an equation with more than one "
                                                 "letter in it",
             "example": "xy = a"},
            {"symbol": "solve for x", "plain": "get x alone on one side. The other "
                                               "letters are allowed to stay letters",
             "example": "x = y + z"},
        ],
        "after": "The one worth separating out is **tangent**, because you met the "
                 "other one four lessons ago. Lesson 86's `tan 42°` is a *ratio of two "
                 "sides of a right triangle*, and it belongs to an angle. Lesson 90's "
                 "tangent *line* is a line touching a curve. They share a name and "
                 "nothing else, and no problem about a tangent *line* uses that "
                 "button. Your practice set does have a `tan` on it — problem 886, "
                 "*find tan 1°* — but that is a review problem from Lesson 86, not "
                 "from today.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Dividing the two small numbers the wrong way round.",
             "wrong": "Δx / Δy = 0.01 / 0.0201 = 0.4975",
             "right": "Δy / Δx = 0.0201 / 0.01 = 2.01",
             "note": "**0.4975 instead of 2.01.** Slope is *rise over run*, so the "
                     "change in **y** goes on top, and it has been that way since "
                     "Lesson 68. The mistake is easier to make here than it was in "
                     "Lesson 81 because both numbers are small and neither one looks "
                     "obviously like the top. Free check: a slope on `y = x²` near "
                     "x = 1 should come out around 2, not around a half. Ask whether "
                     "your answer is the size you expected."},
            {"name": "Subtracting the two points in different orders.",
             "wrong": "Δy = 1.0201 - 1 = 0.0201   →   Δx = 1 - 1.01 = -0.01   →   "
                      "-2.01",
             "right": "Δy = 1.0201 - 1 = 0.0201   →   Δx = 1.01 - 1 = 0.01   →   2.01",
             "note": "**-2.01 instead of 2.01.** Second point minus first point, on "
                     "the top *and* on the bottom. Mixing the order gives the right "
                     "size with the wrong sign — which is impossible here, because "
                     "`f(x) = x²` is climbing between x = 1 and x = 1.01, and "
                     "something climbing cannot have a negative rate of change."},
            {"name": "Rounding 1.0201 before subtracting.",
             "wrong": "Δy = 1.02 - 1 = 0.02   →   0.02 / 0.01 = 2",
             "right": "Δy = 1.0201 - 1 = 0.0201   →   0.0201 / 0.01 = 2.01",
             "note": "**2 instead of 2.01** — and 2 is very nearly where the whole "
                     "lesson is heading, which is exactly what makes this one sneaky. "
                     "The question asked for the rate of change between f(1) and "
                     "f(1.01), and that is 2.01. Δy is one ten-thousandth bigger than "
                     "0.02, and that one ten-thousandth is the entire difference "
                     "between the two answers. The smaller Δx gets, the further right "
                     "the meaningful digits sit — so keep every digit the question "
                     "handed you."},
            {"name": "Reaching for the tangent from Lesson 86.",
             "wrong": "\"tangent line at x = 1\"   →   press tan on the calculator",
             "right": "\"tangent line at x = 1\"   →   a line touching the curve, "
                      "slope about 2",
             "note": "Two unrelated things wearing one name, and your book prints the "
                     "warning in its own definitions. Lesson 86's tangent is "
                     "`opp / adj`, a ratio belonging to an **angle**. Lesson 90's "
                     "tangent line is a **line** touching a curve at essentially one "
                     "point. Nothing in the tangent-line teaching in this lesson needs a "
                     "calculator. Your practice set does carry one real `tan` — "
                     "problem 886, *find tan 1°* — and that is a review problem from "
                     "Lesson 86, not a Lesson 90 one."},
            {"name": "Deciding a multivariable answer is unfinished.",
             "wrong": "x = y + z   →   \"but what does x equal?\"   →   keep going",
             "right": "x = y + z   →   x is alone on one side   →   done",
             "note": "There is nowhere left to go, and a child who keeps going invents "
                     "something — usually cancelling a letter that cannot be "
                     "cancelled. **Alone on one side is the finish line.** Say it out "
                     "loud when you arrive: *x is by itself, so I am done.*"},
            {"name": "Solving for the wrong letter.",
             "wrong": "290. Solve for y:   x + y = z   →   x = z - y",
             "right": "290. Solve for y:   x + y = z   →   y = z - x",
             "note": "**x = z - y instead of y = z - x.** Both lines are correct "
                     "rearrangements of a true equation, and only one of them answers "
                     "the question that was asked. The wanted letter moves around in "
                     "this lesson — Example 90.2 asks for x, practice problems 290 and "
                     "390 both ask for y. Circle it in the instruction first."},
        ],
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "**Derivative means slope.** Your book prints that sentence on a line of "
            "its own, and it is the whole first half.",
            "More precisely: the derivative is the slope of a line drawn between two "
            "points on a function that are an **infinitesimally small Δx** apart.",
            "The arithmetic has not changed since Lesson 81. Turn `f(1) = 1` into the "
            "point (1, 1), subtract to get Δy and Δx — **second minus first, both "
            "times** — and divide.",
            "Shrink Δx and the answer **settles**. On `y = x²` at x = 1: 3, then 2.1, "
            "then 2.01, then 2.001. It **approaches a limit** without arriving.",
            "Ex. 81.3 got 3 and Ex. 90.1 gets **2.01** for the same function at the "
            "same place. Your book calls 2.01 *more accurate* rather than calling the "
            "3 wrong — a smaller gap gives an answer that belongs to the point instead "
            "of to the stretch.",
            "A **tangent line** touches a function essentially — almost — at one "
            "point. Almost, because there are really two, and closing that last gap is "
            "the step the book asks you to take on trust.",
            "**Lesson 90's tangent has nothing to do with `tan` in Lesson 86.** One is "
            "a line touching a curve; the other is a ratio belonging to an angle.",
            "When Δx becomes an infinitesimal the symbols change: **Δx → dx, Δy → dy, "
            "Δy/Δx → dy/dx or f '(x)**, and *slope* becomes *derivative*. Newton wrote "
            "f '(x); Leibniz wrote dy/dx.",
            "**Multivariable** only means more than one letter. Solving for x is "
            "Lesson 39 — undo what was done to x, on both sides — and unlike Lesson "
            "78B there is nothing to evaluate afterwards.",
            "You are finished when **your letter is alone on one side**. `x = y + z` "
            "and `x = a/y` are complete answers. Check which letter was asked for; it "
            "is not always x.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 90 first. If it didn't quite land, this is here to fix that "
    "— and partway down there's a chart where you can watch an answer settle onto "
    "a number. Two halves today, and they aren't related. The first one gives a new "
    "name to something you've been doing since Lesson 68: *derivative means slope*. "
    "The second is shorter — some equations have more than one letter in them, and "
    "an answer with letters left in it is still a finished answer."
)

PARENT_CONTENT = """## The big idea

Two halves, and they have nothing to do with each other. Teach them as two short
lessons.

**90A — the derivative.** The book's own headline is three words, printed on a line
by itself: ***derivative means slope***. Nothing about the arithmetic is new. She
turns `f(1) = 1` into the point (1, 1), subtracts to get Δy and Δx, and divides —
which is Ex. 81.3, which was Ex. 77.2 before that. The single new move is that the
gap between the two points gets **small**, and the book says so plainly: *the only
difference in solving those problems and what we are about to do is that now we
will study smaller values of ∆x.*

What she is meant to come away with is the *behaviour*, not a technique. Do it on
`y = x²` at x = 1 with four gaps and read the answers downwards:

| Δx | Δy | Δy/Δx | |
|---|---|---|---|
| 1 | 3 | **3** | Ex. 81.3 |
| 0.1 | 0.21 | 2.1 | in between |
| 0.01 | 0.0201 | **2.01** | Ex. 90.1 |
| 0.001 | 0.002001 | 2.001 | in between |

3, 2.1, 2.01, 2.001. It does not wander; it **settles**, closer to 2 every time and
never landing on it. That is the book's word — the slope *approaches a limit* — and
that limit is the derivative. The two bold rows are the book's own; the other two
are the identical sum at gaps the book explicitly invites ("*we can decrease from
0.01 to .001, and so on*"), and her page says which is which.

Two smaller things in 90A, both worth naming out loud:

1. **Nothing is proved, and the book admits it.** Shrinking Δx from 1 to 0.01 is
   arithmetic. Going all the way down to an *infinitesimal* is not — and the book
   writes, in its own voice, that *this is one of those "faith things" about
   calculus*: you trust the infinitesimal exists and you agree to treat the two
   points as one point. That is why the answer to Ex. 90.1 is `2.01` and why the
   book's next sentence hedges to *should equal about 2*. Lesson 81 closed on the
   same idea (reasonable faith, not blind faith), so it is not a new posture.
2. **Tangent is a homonym.** Four lessons ago tangent was `opp/adj` on a calculator
   button. Here a *tangent line* is a line touching a curve at essentially one
   point. The book flags the collision itself in its definitions; if she connects
   them she will go looking for a button that has no part in today's teaching.

**90B — multivariable equations.** Genuinely easy, and the book says so: these will
feel easier than Lesson 78B, because 78B made her rearrange *and then* evaluate.
Here there is nothing to evaluate. `x - y = z` → add y to both sides → **x = y + z**.
`xy = a` → divide both sides by y → **x = a/y**. Pure Lesson 39: undo what was done
to the letter, on both sides.

The only thing that trips a child here is not the algebra — it is not believing she
is finished. `x = y + z` looks unfinished, so she keeps going and invents a
cancellation. The sentence that fixes it: **you are done when your letter is alone
on one side; the other letters are not going anywhere.**

**About the figures.** The source prints two diagrams side by side at x = 2 — the
Lesson 81B line from x = 2 to x = 3 (Δy=5, Δx=1, slope=5) and the near-tangent from
x = 2 to x = 2.01 (labelled Δy=0.04, Δx=0.01, slope=4) with a zoomed-in inset. They
are not reproduced on her page; both label their own numbers in the text, so nothing
depends on them, and her page says so in one sentence. The left-hand one is already
drawn for her on her **Lesson 81** page — a fixed graph of `y = x²` she reads rather
than one she can move — so send her back to it.

One thing to have ready, because a careful child will find it: those printed labels
are **rounded**. 2.01² is 4.0401, so the true figures are Δy = 0.0401 and a slope of
4.01 — which is why the book's own prose beside the picture says the slope drops to
*around* 4. Her page carries the book's numbers and then says where the extra digits
went. If she computes 4.01 and thinks she has contradicted the book, she has not.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Show her the surfer photograph at the top of her lesson and ask the whole thing
   in one question: **"How fast is the surfer going in this picture?"** Let the
   silence sit. You want her to notice that a photo has no speed in it and that she
   knows the answer anyway. That gap is what calculus is for.
2. **"How would you work out a speed if I gave you two photos?"** Distance moved
   over time taken. Then say the sentence that connects it: *that is rise over run,
   which is slope, which you have been doing since Lesson 68.*
3. Now the move. **"What if the two photos are closer together? And closer?"** Then
   the book's own claim, as a question: **"Does the answer go crazy, or does it head
   somewhere?"** Do not answer it — that is what the table on her page is for.
4. Work Ex. 90.1 with her, out loud, and stop at the end to ask the comparison the
   question actually wants: **"Lesson 81 said 3 for this exact function at this exact
   place. Now we get 2.01. Which one is right?"** The answer is *both, and 2.01 is
   more accurate*, because a smaller gap gives an answer belonging to the point
   rather than to the stretch beside it. That is the whole lesson in one exchange.
5. For the second half, write `x - y = z` on paper and ask **"what's being done to
   the x?"** — subtracting y. Undo it. Then, when she writes `x = y + z`, ask the
   question that is really the lesson: **"Are you finished?"** If she hesitates, that
   hesitation is the thing to fix, not her algebra.

If she is lost on the first half, go back to step 3 and stay there. Everything else
in 90A is subtraction and division she can already do.

## The classic mix-ups, with the exact wrong answer each one produces

- **Slope upside down.** `0.01 ÷ 0.0201` = **0.4975** instead of **2.01**. Both
  numbers are small, so neither looks obviously like the top. Fix: rise over run —
  the change in *y* goes upstairs, always. Free check: the answer near x = 1 should
  be about 2, not about a half.
- **Subtracting in different orders top and bottom.** `Δx = 1 - 1.01` gives
  **-2.01** instead of **2.01**. Second point minus first point, both times. `x²` is
  climbing there, and a thing that is climbing cannot have a negative rate of change.
- **Rounding 1.0201 to 1.02 first.** Gives **2** instead of **2.01** — and 2 is
  nearly where the lesson is heading, which is what makes it sneaky. The digit she
  threw away is one ten-thousandth, and that one ten-thousandth is the entire
  difference between the two answers. Fix: on these problems, keep every digit the
  question gave her.
- **The wrong tangent.** She sees "tangent line" and reaches for the `tan` button
  she learned in Lesson 86. Nothing in the tangent-line teaching needs a calculator
  — but do not tell her the lesson has no `tan` in it, because her practice set has
  one: problem 886, *find tan 1°*, marked (C). Naming it is the cleanest way to make
  the point — it is a Lesson 86 review problem, not a Lesson 90 one. Fix: say the
  two definitions back to back once — *a ratio belonging to an angle* versus *a
  line touching a curve*.
- **"But what does x equal?"** She writes `x = y + z`, does not believe it, and
  keeps going — usually by cancelling something that cannot cancel. Fix: **alone on
  one side is the finish line.**
- **Solving for the wrong letter.** Practice problem 290 is `x + y = z` and asks for
  **y**; a child who has just done Example 90.2 solves for x out of habit and writes
  `x = z - y` instead of **`y = z - x`**. Both are true rearrangements; only one
  answers the question. Fix: circle the wanted letter before starting.

## What to watch her do

Watch her **pencil**, in this order:

1. **Does she write the two points down before doing anything else?** `f(1) = 1 →
   (1, 1)` should appear on the page. A child who goes straight to subtracting is
   holding the translation in her head, and that is where the "which number is y?"
   confusion comes from.
2. **Does she keep all four decimals of 1.0201?** Watch for a `1.02` appearing
   anywhere. That single rounding is the most common wrong answer in 90A and it is
   visible from across the table.
3. **On the divide, which number goes on top?** You want to see `0.0201` written
   above `0.01`, not beside it in whichever order it came out of her head.
4. **After she gets 2.01, does she look back at Lesson 81's 3?** The question asks
   her to compare, and comparing is the actual content. If she stops at 2.01 and puts
   her pencil down, ask her the comparison out loud.
5. **On 90B, does her pencil stop when the letter is alone?** Watch for extra
   working after `x = y + z`. Stopping confidently is the skill in the second half;
   there is nothing else in it.

Getting 2.01 is not what to watch for — she can get 2.01 by copying the shape of the
example. Watching an answer settle, and being willing to stop when the answer has
letters in it, are the two things that survive into the next lesson.

## Extend it

- **Do the in-between row with her.** The book gives Δx = 1 and Δx = 0.01. Ask her
  for Δx = 0.1 herself: `f(1.1) = 1.21`, so `0.21 ÷ 0.1 = 2.1`. Getting 2.1 to land
  neatly between 3 and 2.01 without being told it would is the moment the word
  *limit* stops being vocabulary.
- **The two practice problems in the second half take one minute together.**
  290: `x + y = z` → subtract x → **y = z - x**. 390: `xy = z` → divide by x →
  **y = z/x**. Both ask for y, which is the point of them.
- **Ask her what happens at x = 2 and x = 3.** Her book's picture gives about 4 at
  x = 2, and practice problem 190 gives 6.01 at x = 3. With the 2 from x = 1 that is
  **2, 4, 6** — and Saxon gives her no rule for it. Let her notice it and leave it
  noticed; a child who spots a pattern a year early should not immediately be handed
  the formula.
- **The honest objection is worth raising yourself.** Four values cannot prove the
  slope settles on 2 rather than on 1.999. They cannot, and the book does not claim
  they do. Saying that out loud is more respectful of her than pretending the
  argument is airtight, and it is exactly what the book means by a faith thing.
- **Newton or Leibniz.** Two people got here at once and wrote it two different
  ways: `f '(x)` and `dy/dx`. The book prefers Leibniz's for beginners because it
  never lets you forget the thing is a fraction. Worth two minutes if she likes the
  history.

## Where this sits

DIVE Lesson 90, *The Derivative and Slope; Solving Multivariable Equations*.
Reviews **Lessons 39, 68, 78 and 81**.

- **Lesson 81 is the one to revisit if the first half is lost.** 81B is where
  calculus was defined as the study of rates of change, and Ex. 81.3 is literally
  this lesson's example with a bigger gap. Her Lesson 81 page also carries the drawn
  graph of `y = x²` that Lesson 90's own book diagrams redraw at x = 2 — her Lesson 90
  page does not reproduce those diagrams.
- **Lesson 68** is where slope itself started, and it is the thing to go back to if
  the problem is `Δy/Δx` rather than the shrinking.
- **Lesson 39** is the one for the second half: the additive and multiplicative
  properties of equality, written in letters. The book names it directly as what a
  multivariable equation looks like.
- **Lesson 78B** is the same rearranging done to scientific formulas, with an
  evaluate step on the end. If she found 78B hard, tell her before she starts that
  this is 78B with the hard part removed — the book says so itself.

**Proficient** looks like: turns `f(1.01) = 1.0201` into a point, computes
`Δy/Δx = 2.01` keeping all the digits, and solves `x - y = z` for x without
hesitating over the letters.
**Mastered** looks like: can say what *approaches a limit* means in her own words,
explains why 2.01 is better than Lesson 81's 3 rather than just different, and stops
cleanly on a multivariable answer without asking what x "really" equals.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 90 (the derivative and slope; solving "
            "multivariable equations) — idempotent.")

    LESSON_NUMBER = 90
    TITLE = ("Derivative Means Slope — The Derivative and Slope, and Solving "
             "Multivariable Equations")
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
