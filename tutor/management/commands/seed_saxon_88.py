"""Saxon Pre-Algebra Lesson 88 — Logic: The Syllogism; Surface Area.

Reviews Lessons 37, 42, 44, 67 and 81. **Lesson 81 is the hook**, and the source
says so itself twice: the letters p and q are 81's letters (88 only adds r), and
88 repeats 81's uncomfortable fact — an argument can be logical and still false in
reality. Only 81 sits inside this course's seeded lessons. Lessons 37, 42, 44 and
67 do not, and nothing here describes them beyond the two the book itself names in
passing (Euclid at 44, analogies at 37).

Two unrelated halves, so two runs of blocks: 88A is the syllogism (Examples 88.1a
and 88.1b) and 88B is surface area (Examples 88.2, 88.3 and 88.4).

Judgement calls:

* **No KIND_TOOL.** None of the six widgets teaches a syllogism or a surface area,
  and bolting one on would have been decoration; Lesson 85 has no tool either. The
  predict-then-check load is carried by the reveal instead, which asks her to work
  out the book's own remark that 88.1b "would be valid if the conclusion and minor
  premise were switched."
* **The Euler diagrams are written with brackets, not described.** The source draws
  them as circles, but it states every label in text — *Mortal things / All men /
  Aristotle*, *things with hair / all dogs / Rover*, *Things with 8 tentacles /
  cats / Jordan* — so the nesting is rendered as `[ outer [ inner ] ]` out of the
  book's own words rather than invented. Her page says the pictures themselves are
  in her book.
* **The three surface-area figures are not reproduced.** Every number used is
  stated in the printed solutions: `2π(3)(8)` gives the cylinder r = 3 and h = 8 m,
  `4π(2)²` gives the sphere r = 2 ft, and Ex. 88.4's `2•4 = 8` with `2(2•2)` gives a
  square base 2 m on a side standing 5 m tall. Idea 3 says so in one sentence on her
  page and the parent guide repeats it.
* **The book's arrow direction is odd, and is carried anyway.** It writes the major
  premise as "If p, then q" with p the property and q the set — "if hairy then dog" —
  which runs backwards from how the English sentence sounds. The page follows the
  book and tells her to test the *pattern* (p to q, q to r, so p to r) rather than
  argue with the direction.
* **The if/then letters are taught as a check, never as a shortcut.** The book gives
  both forms — `p→q, q→r, ∴ p→r` valid and `p→q, p→r, ∴ q→r` invalid — and the
  tempting summary ("a letter shows up in both premises and then vanishes") is
  *wrong*: in the invalid form p does exactly that. What actually separates them is
  where the shared letter sits — q has to end one premise and begin the other so the
  two hook end to end. The page says that, and says it does not replace the book's
  own test.
* **The errors block practises on an invented syllogism** (*All robins have feathers.
  Pepper has feathers. So Pepper is a robin.*) and says on the page that it is not
  from her book. Practice problem 288 is the same shape with cats and four legs, and
  quoting it here would hand her the answer to one of only two syllogism problems she
  has to work. Lesson 87's errors block does the same thing for the same reason. The
  288 discussion stays in the parent guide.
* The closing worldview paragraph — logic as God's standard for human thinking, true
  because Christ is true — is carried as the book has it, the way Lesson 81's was,
  neither amplified nor stripped. Its exclamation mark is the one thing dropped.

Digitized from the family's purchased DIVE lesson guide ((c) 2021 DIVE, LLC) for
private use.

    python manage.py seed_saxon_88 --curriculum 100
"""

from tutor.models import LessonBlock as B

from ._saxon_seed import SaxonSeedCommand

BLOCKS = [
    (B.KIND_MASTHEAD, {
        "eyebrow": "Saxon · Lesson 88 · Pre-Algebra",
        "title": "Check the middle sentence. Then unroll the sides.",
        "thesis": "A three-sentence argument is **valid** when all three sentences "
                  "do their own job — and the job that goes wrong first is the "
                  "middle sentence's, which has to put a member inside the set the "
                  "first sentence talked about. Validity has nothing to do with "
                  "whether any of it is true. "
                  "Then a second, unrelated half: the side of a solid is a rectangle "
                  "rolled up, so its area is **perimeter times height**.",
        "formula": "LSA = Ph    ·    SA = 4πr²",
        "roles": [
            {"tone": "start", "name": "the major premise — a property, and a set",
             "text": "Sentence one. It says something about a whole group: all dogs "
                     "have hair. The something is p, the property. The group is q, "
                     "the set."},
            {"tone": "move", "name": "the minor premise — the sentence that decides",
             "text": "Sentence two. It has one job: put a member (r) inside that "
                     "group. Rover is a dog does that. Jordan has eight tentacles "
                     "does not — and that is where 88.1b breaks first, with the "
                     "conclusion left doing this sentence's job afterwards."},
        ],
    }),

    (B.KIND_PURPOSE, {
        "title": "Why anybody bothers naming the parts of an argument",
        "paragraphs": [
            "Somebody says: everyone on the team has to be at practice by four, "
            "you are on the team, so you have to be there by four. Nobody argues "
            "with that. Three sentences, and it is airtight.",
            "Now here is one that sounds exactly as good. *Everyone who was late got "
            "benched. Marcus got benched. So Marcus was late.* Read it twice. Same "
            "rhythm, same confidence, same three sentences — and it does not follow. "
            "Marcus might have been benched for a sprained ankle.",
            "The difference between those two is not volume or confidence. It is "
            "**shape**. Twenty-three centuries ago Aristotle worked out what the shape "
            "has to be and gave the three-sentence argument a name: a **syllogism**. "
            "Your book says who he was — one of Plato's students, who died when Euclid "
            "was still a boy — and calls him the Father of Logic.",
            "You already own most of the machinery. In **Lesson 81** you wrote "
            "sentences as *If p, then q*, and you learned the uncomfortable part: a "
            "statement can be perfectly logical and still not be true in reality. "
            "Lesson 88 adds exactly one letter — **r** — and one more sentence. That "
            "is all the new notation there is.",
            "The second half of this lesson has nothing to do with the first, so "
            "treat it as a second short lesson. It asks a question you have not quite "
            "asked before: not *how much fits inside this shape*, which is volume, but "
            "**how much skin is on the outside of it**. How much paint for the silo. "
            "How much paper in the label around a soup can.",
            "And the answer turns out to be easy in a way worth seeing once. Peel the "
            "label off a can and flatten it on the table. It is a **rectangle**. Its "
            "short side is the can's height. Its long side is the distance all the way "
            "around the can. So the area of the side of the can is just those two "
            "multiplied together — and that is the entire first rule on your page.",
        ],
    }),

    (B.KIND_IDEA, {
        "n": 1, "of": 3, "tone": "start",
        "title": "Three sentences, and each one has a job",
        "paragraphs": [
            "Your book's definition is worth having word for word. A **syllogism** is "
            "a type of logical argument where a conclusion is drawn from two "
            "introductory statements, called **propositions**, or **premises**. The "
            "two introductory statements are the **major premise** and the **minor "
            "premise**.",
            "So: three sentences. Major premise, minor premise, conclusion, always in "
            "that order. The whole three-step process is also called an **argument**.",
            "Here is the famous one, the one Aristotle is remembered for. *Mortality "
            "is for all men. That man is Aristotle. Mortality is for Aristotle.* Say "
            "it out loud once. Nothing about it is surprising, which is the point — "
            "the shape is so natural that you have been using it your whole life "
            "without a name for it.",
            "Now the letters, which are Lesson 81's letters with one addition. **p** "
            "is the property: *mortal*. **q** is the set: *man*. **r** is the member: "
            "*Aristotle*. You have used p and q before. Only r is new.",
            "Each sentence has exactly one job. The major premise gives a **property "
            "to a whole set**. The minor premise names a **member of that set**. The "
            "conclusion hands the property down to the member. That is the machine: "
            "the property is true of everything in the set, this thing is in the set, "
            "so the property is true of this thing.",
            "All three sentences can also be written as if/then statements — the "
            "conditional statements from Lesson 81. Your book writes them that way "
            "beside each sentence, and it is worth copying the letters onto your own "
            "paper the first few times, even though you will stop needing to.",
        ],
    }),

    (B.KIND_TABLE, {
        "caption": "Aristotle's own syllogism, laid out the way your book lays it out",
        "headers": ["the part", "the sentence", "the letters, as the book writes them"],
        "rows": [
            {"cells": ["major premise", "Mortality is for all men.",
                       "If p, then q     (p = mortal, q = man)"], "emphasis": True},
            {"cells": ["minor premise", "That man is Aristotle.",
                       "If q, then r     (q = man, r = Aris.)"], "emphasis": True},
            {"cells": ["conclusion", "Mortality is for Aristotle.",
                       "If p, then r     (p = mortal, r = Aris.)"]},
        ],
        "note": "Read the letter column top to bottom. **q ends the first premise and "
                "starts the second**, and then it is gone from the conclusion. The two "
                "premises hook together at q, and what is left when they hook is the "
                "conclusion — that is what the valid form looks like in letters. Use "
                "it carefully, though. It is not enough for some letter to turn up "
                "twice; it has to *finish* one premise and *begin* the other, and you "
                "cannot tell until you have named p, q and r. Check your work with it; "
                "do not use it instead of the real test. The two "
                "shaded rows are the premises; your book also calls them "
                "*propositions*. One warning about the arrows: written this way they "
                "point from the property to the set, which is the opposite of how the "
                "English sentence sounds. Follow your book's order, and test the "
                "**pattern** rather than arguing with the direction.",
    }),

    (B.KIND_SAY, {
        "text": "\"Read me the middle sentence. Just the middle one. Now tell me: does "
                "it say that something is *in* the group the first sentence was about? "
                "Not that it looks like it. Not that it has the same feature. Is it "
                "*in* the group. If it is, draw your circles and watch them nest. If "
                "it isn't, you're finished — it's invalid, and it doesn't matter how "
                "sensible the last sentence sounds.\"",
    }),

    (B.KIND_IDEA, {
        "n": 2, "of": 3, "tone": "move",
        "title": "Valid means the shape is right. It does not mean anything is true.",
        "paragraphs": [
            "Your book gives the test as a three-part checklist. An argument is "
            "**valid** if the major premise identifies a property (p) of the set (q), "
            "the minor premise identifies a member (r) of the set (q), and the "
            "conclusion links the property (p) with the member (r). **All other "
            "syllogisms are invalid.**",
            "Read the middle clause again. The minor premise has to identify a member "
            "**of the set**. Not of the property — of the set. That one word is where "
            "nearly every broken argument breaks, and it is the thing to check first, "
            "because it is the thing easiest to fake.",
            "There is a faster way to run the test than juggling letters, and your "
            "book recommends it: draw it. An **Euler diagram** — named after Leonhard "
            "Euler — is circles inside circles. Property circle on the outside, the "
            "set inside it, the member inside that. If the premises **force** "
            "everything to nest — the member has nowhere else it could go — the "
            "argument is valid.",
            "If the premises leave the member two legal places to stand, inside the "
            "set or outside it, the argument is invalid — and that stays true even "
            "when one of those two drawings happens to nest. Your book "
            "warns you in advance about how that will feel: as you get experience with "
            "invalid syllogisms you will sense a confusion about where to put the "
            "member circle, because it could fit inside the set or outside it. **That "
            "confusion is the answer.** A valid argument never leaves you a choice "
            "about where the member goes.",
            "Now the hard part, and it is the same hard part as Lesson 81. A syllogism "
            "can be perfectly **valid** and still have premises or a conclusion that "
            "are **false in reality**. Validity is a claim about the shape of the "
            "argument — about whether the conclusion follows — and no claim at all "
            "about whether the sentences are true. Example 88.1b is about cats with "
            "eight tentacles, and the tentacles are not what is wrong with it.",
            "Your book closes this half with the reason it thinks any of it holds. "
            "Laws of logic — syllogisms, analogies from Lesson 37, and the rest — are, "
            "it says, God's standard for human thinking. He created us in His image, "
            "which is why we are able to use the laws of logic to gain knowledge at "
            "all; and the laws of logic are true, absolute and eternal because Christ "
            "is true, absolute and eternal.",
        ],
    }),

    (B.KIND_MATH, {
        "display": "[ mortal things  [ all men  [ Aristotle ] ] ]",
        "note": "That is Aristotle's syllogism drawn as an Euler diagram, written out "
                "with brackets because your book draws it with circles. Three rings, "
                "each one wholly inside the last. **Forced to nest means valid** — "
                "and you can see why in the picture rather than having to be told: "
                "Aristotle sits inside *all men*, and every single thing inside *all "
                "men* is also inside *mortal things*, so Aristotle has nowhere else to "
                "be. A picture that merely *can* be drawn nested proves nothing; this "
                "one had no choice. The "
                "circles are in your book; a bracket inside a bracket is the same "
                "claim with less drawing.",
    }),

    (B.KIND_STEPS, {
        "tag": "The recipe", "title": "Four moves, and the third one decides it",
        "steps": [
            {"label": "Underline the group in the first sentence.",
             "detail": "The major premise always talks about a whole group — *all "
                       "men*, *all dogs*, *all cats*. That group is **q**, the set. "
                       "Write it down before anything else; everything in the argument "
                       "gets measured against it."},
            {"label": "Underline what the first sentence says about that group.",
             "detail": "*are mortal*, *have hair*, *have eight tentacles*. That is "
                       "**p**, the property. It belongs to the whole set, which is "
                       "exactly why it will belong to anything you can get inside the "
                       "set."},
            {"label": "Read the second sentence and ask one question: does it put "
                      "something inside the set?",
             "detail": "**This is the move that decides the argument.** *Rover is a "
                       "dog* puts Rover inside *all dogs* — yes. *Jordan has eight "
                       "tentacles* gives Jordan the **property** and never says he is "
                       "a cat — no. A minor premise that repeats the property instead "
                       "of naming the set is the invalid shape, and out loud it sounds "
                       "identical to the valid one.",
             "math": "valid:  the member is IN the set      invalid:  the member "
                     "merely has the property"},
            {"label": "Check that the conclusion joins the property to the member.",
             "detail": "It has to say *the member has the property* — mortality is for "
                       "Aristotle, Rover has hair. If instead it joins the set to the "
                       "member, it has stolen the minor premise's job, and your book "
                       "calls that out by name in Example 88.1b."},
        ],
        "after": "Two things this test never asks, on purpose. It does not ask whether "
                 "the sentences are **true** — an argument about eight-tentacled cats "
                 "can be perfectly valid. And it does not ask whether the ending sounds "
                 "sensible. **Valid is a shape.** The moment you find yourself agreeing "
                 "because the conclusion feels right, you have stopped testing and "
                 "started nodding.",
    }),

    (B.KIND_STEPPER, {
        "title": "Example 88.1a — is this argument valid?",
        "equation": "All dogs have hair.   ·   Rover is a dog.   ·   So, Rover has "
                    "hair.",
        "steps": [
            {"label": "Look first",
             "text": "Three sentences in the order your book always uses: major "
                     "premise, minor premise, conclusion. Before deciding anything, "
                     "notice what you are **not** being asked. Nobody wants to know "
                     "whether Rover has hair. The question is whether these three "
                     "sentences fit together properly, and that is a different "
                     "question."},
            {"label": "Step 1 · name the set",
             "text": "The first sentence talks about a whole group: **all dogs**. That "
                     "is q. Write it in the margin. Every later move measures something "
                     "against that circle.",
             "math": "q = all dogs"},
            {"label": "Step 2 · name the property",
             "text": "What does that first sentence say about the whole group? That "
                     "they **have hair**. That is p. Because it belongs to the entire "
                     "set, it will belong to anything you can show is inside the set.",
             "math": "p = having hair"},
            {"label": "Step 3 · the deciding question",
             "text": "*Rover is a dog.* Does that put something inside the set? Yes — "
                     "it says outright that Rover is one of the dogs. So r is Rover, "
                     "and r is inside q. **This is the step that decides the "
                     "argument**, and here it goes the right way.",
             "math": "r = Rover,  and r is inside q"},
            {"label": "Step 4 · check the conclusion",
             "text": "*Rover has hair* joins the property to the member, which is "
                     "exactly what a conclusion is for. Your book's own words: the "
                     "conclusion links the property (p, having hair) with the member "
                     "(r, Rover), so this is a **valid** argument."},
            {"label": "Draw it, because circles are faster than letters",
             "text": "Your book says so itself: using pictures like the Euler diagram "
                     "is often easier than trying to break the syllogism into p, q and "
                     "r. Three rings, each inside the last. The drawing is in your "
                     "book; written with brackets it looks like the line below. "
                     "Nothing in the premises lets Rover sit anywhere but there, and "
                     "nesting you are forced into is what valid looks like.",
             "math": "[ things with hair  [ all dogs  [ Rover ] ] ]"},
            {"label": "Rewrite it as three if-thens — Lesson 81 again",
             "text": "Every one of the three sentences can be written as a conditional "
                     "statement. Written that way you can watch the two premises hook "
                     "together: the first one ends at **dog** and the second one begins "
                     "at **dog**, so they link end to end, and the conclusion is what is "
                     "left when they do. That hook is what a valid syllogism looks like "
                     "in letters. It is a way of checking, not a way of skipping — you "
                     "still have to name p, q and r first, and 88.1b is about to show "
                     "you letters that repeat without hooking anything.",
             "math": "If hairy then dog.  ·  If dog then Rover.  ·  "
                     "If hairy then Rover."},
        ],
    }),

    (B.KIND_WORKED, {
        "number": "88.1b",
        "question": "Determine if this syllogism is valid or invalid. Major premise: "
                    "All cats have eight tentacles. Minor premise: Jordan has eight "
                    "tentacles. Conclusion: Jordan is a cat.",
        "steps": [
            {"label": "First, the objection everybody makes",
             "text": "It is false. Octopi have eight tentacles, cats do not — your book "
                     "says exactly that. Now put it aside, because **false is a "
                     "different question from invalid**. Lesson 81 told you the same "
                     "thing about if-then statements: just because an argument is "
                     "logical does not mean it is true in reality. A syllogism about "
                     "eight-tentacled cats could be perfectly valid. This one is not, "
                     "and the reason has nothing to do with cats."},
            {"label": "Name the set and the property",
             "text": "The first sentence talks about the group **all cats** and says "
                     "they have **eight tentacles**. Nothing is wrong yet. The major "
                     "premise is doing its job properly — it identifies a property of "
                     "a set, which is all it was ever asked to do.",
             "math": "q = all cats,  and p = having eight tentacles"},
            {"label": "Now the deciding question, and this time the answer is no",
             "text": "*Jordan has eight tentacles.* Read it slowly. It gives Jordan the "
                     "**property**. It does not say, anywhere, that Jordan is a "
                     "**cat**. So the second sentence has not put Jordan inside the "
                     "set — and putting the member inside the set is the only thing a "
                     "minor premise is for."},
            {"label": "Which is why the conclusion has nothing to stand on",
             "text": "*Jordan is a cat* tries to link the set to the member. Here is "
                     "your book's sentence about it: the syllogism concludes by linking "
                     "the set (q) with the member (r) — but that's what the minor "
                     "premise does. The two sentences have swapped jobs. Both jobs end "
                     "up half done, and the argument is **invalid**."},
            {"label": "Draw it and the hole shows",
             "text": "Eight-tentacled things on the outside, cats inside them, and "
                     "Jordan somewhere in the eight-tentacled ring — but nothing in the "
                     "argument tells you whether Jordan is inside the cats ring or "
                     "outside it. That is the confusion your book promised you would "
                     "feel, and the confusion **is** the verdict. Notice what a drawing "
                     "has to do, though: it has to put Jordan *somewhere*. Your book's "
                     "picture puts him outside the cats, and so does the line below — "
                     "but that is only one of the two places the premises allow. Draw "
                     "him inside the cats instead and every sentence still holds. **Two "
                     "different pictures, both of them legal — that is the hole.**",
             "math": "[ things with 8 tentacles   [ cats ]   [ Jordan ] ]"},
            {"label": "Write the three if-thens and hold them next to 88.1a",
             "text": "The valid shape ran p to q, then q to r, therefore p to r — the "
                     "two premises met at q. This one runs p to q, then p to r, "
                     "therefore q to r. Follow q, the set: it ends the major premise, "
                     "and then it turns up again in the conclusion. So q is used twice; "
                     "counting is not the test. What matters is that q never appears in "
                     "**both premises**. Both premises begin at p instead, so they hang "
                     "off the same peg and never hook to each other, and nothing links.",
             "math": "If 8 tentacles then cat.  ·  If 8 tentacles then Jordan.  ·  "
                     "If cat then Jordan."},
            {"label": "The verdict",
             "text": "Two sentences have swapped jobs, so the argument fails. Say the "
                     "reason out loud when you write the answer — not *because it is "
                     "false*, but *because the minor premise never put Jordan in the "
                     "set*. The reason is the part that transfers to the next problem.",
             "math": "the minor premise never puts Jordan inside the set   →   invalid"},
        ],
        "answer": "invalid",
    }),

    (B.KIND_TABLE, {
        "caption": "88.1a beside 88.1b — the same three slots, filled two different "
                   "ways",
        "headers": ["", "88.1a — valid", "88.1b — invalid"],
        "rows": [
            {"cells": ["major premise", "All dogs have hair.",
                       "All cats have eight tentacles."]},
            {"cells": ["minor premise", "Rover is a dog.  (names the SET)",
                       "Jordan has eight tentacles.  (names the PROPERTY)"],
             "emphasis": True},
            {"cells": ["conclusion", "Rover has hair.", "Jordan is a cat."]},
            {"cells": ["as if-thens",
                       "If hairy then dog. If dog then Rover. If hairy then Rover.",
                       "If 8 tentacles then cat. If 8 tentacles then Jordan. "
                       "If cat then Jordan."]},
            {"cells": ["the shape", "p to q,  q to r,  so p to r",
                       "p to q,  p to r,  so q to r"]},
            {"cells": ["the circles", "[ hairy [ dogs [ Rover ] ] ]",
                       "[ 8 tentacles [ cats ]  [ Jordan ] ]   — or Jordan inside "
                       "the cats; both fit"]},
            {"cells": ["verdict", "valid", "invalid"], "emphasis": True},
        ],
        "note": "**Two rows** differ in kind: the shaded minor-premise row near the "
                "top, and the conclusion row under it — and the first is why the "
                "second went wrong. 88.1a's conclusion hands the property to the "
                "member, which is what a conclusion is for; 88.1b's hands over the set "
                "instead, which is the minor premise's job, and it is left doing that "
                "job only because the minor premise did not. In 88.1a the minor "
                "premise names the set, so the two premises meet at q and the "
                "conclusion is "
                "what is left over. In 88.1b it hands Jordan the property instead, so "
                "both premises begin at p and q never appears in both of them — nothing "
                "hooks, and there is no chain at all. That is also why the right-hand "
                "circles come with an *or*: the premises leave Jordan two legal places "
                "to stand. Read both arguments out loud and they "
                "sound equally confident — which is the entire reason this test is "
                "worth doing on paper rather than by ear.",
    }),

    (B.KIND_IDEA, {
        "n": 3, "of": 3, "tone": "start",
        "title": "Surface area is the skin, and the sides unroll into a rectangle",
        "paragraphs": [
            "Second half. Nothing here depends on anything in the first half, so start "
            "fresh.",
            "**Surface area** is the area found on the surface of a solid. Not what "
            "fits inside it — that is volume — but what covers it. Paint, wrapping "
            "paper, sheet metal, the label on a can.",
            "Your book splits it in two, and that split is nearly all the vocabulary "
            "you need. **Lateral surface area (LSA)** is the area around the sides of "
            "a right solid; it does not include the top and the bottom, only the "
            "sides. **Total surface area (TSA)** is the LSA plus the area of the top "
            "and bottom faces. The book adds a caution worth reading twice: TSA as "
            "defined in this course is only for right solids.",
            "The word **right** in *right solid* is doing the same job it does in "
            "*right angle* — the sides stand square to the base instead of leaning. "
            "That is also why the rule insists on the **perpendicular** height: h is "
            "measured straight up from the base, never along a slanted edge.",
            "Now the rule, and where it comes from. Peel the label off a soup can and "
            "lay it flat. It is a rectangle. Its short side is the can's height, h. "
            "Its long side is the distance all the way around the base — the base's "
            "perimeter, P. So the area of the side is P times h. That is the whole "
            "first rule: **LSA = Ph**.",
            "It works for a box exactly as well as for a can, because that argument "
            "never mentioned circles. Unroll the four walls of a shoebox standing on "
            "end and you get one long rectangle whose length is the perimeter of the "
            "bottom. Your book puts it plainly: on some problems you will be given P, "
            "and on others you have to calculate it. **Finding P is where the work "
            "actually is.**",
            "A sphere refuses to play. It has no sides, no top and no bottom, and "
            "nothing to unroll, so it gets a rule of its own — **SA = 4πr²** — and "
            "because there are no sides to separate out, that answer is already the "
            "total surface area.",
            "One honest note about the pictures. All three examples in this half are "
            "drawn in your book and the drawings are not copied here. You do not need "
            "them: every number this page uses is one your book states in its own "
            "printed solution — the cylinder's radius of 3 and height of 8 m, the "
            "sphere's radius of 2 ft, and a rectangular solid whose square base is 2 m "
            "on a side and which stands 5 m tall. Keep the book open beside you and "
            "check each one against its picture as you go.",
        ],
    }),

    (B.KIND_STEPS, {
        "tag": "The second recipe",
        "title": "Four moves for a surface-area problem",
        "steps": [
            {"label": "Decide first: sides only, or sides plus lids?",
             "detail": "**LSA** is the sides only — no top, no bottom. **TSA** is the "
                       "LSA plus the top and bottom faces. The question always says "
                       "which one it wants, and writing that down is the cheapest "
                       "thing you can do for yourself. A sphere is the exception: no "
                       "sides at all, so its one rule gives you the total straight "
                       "away."},
            {"label": "Find P — the perimeter of the BASE.",
             "detail": "Not the outline of the side you happen to be looking at. The "
                       "distance all the way around the **bottom face**. Sometimes the "
                       "problem hands you P outright. Otherwise build it: a square base "
                       "of side s gives 4s, a rectangle gives 2(l + w), and a "
                       "**circle** gives its circumference, 2πr.",
             "math": "square base, side 2 m   →   P = 2 × 4 = 8 m"},
            {"label": "Multiply. That is the LSA, and there is nothing else in it.",
             "detail": "LSA = P × h, with h the **perpendicular** height. Practice "
                       "problem 388 says it to you in so many words: *don't overthink "
                       "this, lateral surface area really is just the base perimeter "
                       "times the height.* If you find yourself reaching for a third "
                       "number, you have added something the rule does not have."},
            {"label": "If the question wanted TSA, add the two base faces — and keep "
                      "the 2.",
             "detail": "TSA = Ph + 2(area of the base). Top **and** bottom, so two of "
                       "them. Then finish the answer in **square** units, because "
                       "every one of these answers is an area, whatever the shape "
                       "was.",
             "math": "TSA = Ph + 2(A base)"},
        ],
        "after": "Use **3.14** for π every time — your book says so at the top of the "
                 "section and again at the top of the practice set. And steal a habit "
                 "from Lesson 78: write the formula down first, then substitute, then "
                 "work. Putting `LSA = Ph` on the page before you touch a number is "
                 "what stops you multiplying the wrong two things.",
    }),

    (B.KIND_WORKED, {
        "number": "88.2",
        "question": "Find the lateral surface area (LSA) of the right cylinder shown — "
                    "a can 8 m tall whose circular base has a radius of 3.",
        "steps": [
            {"label": "Write the rule before you write a number",
             "text": "For right solids the LSA is the perimeter of the base times the "
                     "height perpendicular to it. Nothing about that sentence mentions "
                     "circles, so it applies here unchanged.",
             "math": "LSA = Ph"},
            {"label": "The base is a circle, so P is a circumference",
             "text": "This is the only genuinely new work in the problem. The base of a "
                     "cylinder is a circle, and the distance all the way around a "
                     "circle is its circumference — so you use the circumference "
                     "formula to build P, then carry on as normal.",
             "math": "P = 2πr = 2π(3)"},
            {"label": "Substitute both numbers at once",
             "text": "Radius 3, height 8. Put them into Ph and the whole thing becomes "
                     "a single line of arithmetic with one π left over in it.",
             "math": "LSA = 2πrh = 2π(3)(8)"},
            {"label": "Collect the plain numbers first, and leave π alone",
             "text": "2 times 3 times 8 is 48, so the answer is 48 of something — 48π. "
                     "Doing it in this order keeps the arithmetic small, and it is how "
                     "your book writes it.",
             "math": "2 × 3 × 8 = 48   →   48π"},
            {"label": "Now put 3.14 in for π, and label it as an area",
             "text": "Your book says to use 3.14 for π every time. And the unit is "
                     "**square** metres, not metres — this is a quantity of surface, "
                     "the amount of metal in the side of the can.",
             "math": "48 × 3.14 = 150.72   →   150.72 m²"},
            {"label": "One thing this answer is not",
             "text": "It is not the total surface area. Your book stops to say so: to "
                     "get the TSA you would have to find the area of the top and bottom "
                     "bases — two equal circles — and add them to this. Nobody asked, "
                     "so nobody adds them. Answer the question that was written down."},
        ],
        "answer": "150.72 m²",
    }),

    (B.KIND_WORKED, {
        "number": "88.3",
        "question": "Find the surface area of this sphere — a ball whose radius is "
                    "2 ft.",
        "steps": [
            {"label": "Why this one skips the LSA question entirely",
             "text": "A sphere has no sides. There is no base to find the perimeter of, "
                     "no top, no bottom and nothing to unroll — so `LSA = Ph` has "
                     "nothing to grip. Your book's reasoning is one line: since a "
                     "sphere doesn't have sides, the formula calculates the **total** "
                     "surface area.",
             "math": "SA = 4πr²"},
            {"label": "Square the radius on its own, before anything else",
             "text": "The rule squares r, so do that first and get it out of the way. "
                     "The radius is 2, and 2 squared is 4. Then multiply that 4 by the "
                     "4 already in the formula.",
             "math": "2 × 2 = 4   →   4 × 4 = 16"},
            {"label": "So the answer is 16 of π",
             "text": "Same pattern as the cylinder: gather the plain numbers, leave π "
                     "sitting there, and only bring in 3.14 at the very end.",
             "math": "4π(2)² = 16π"},
            {"label": "Swap in 3.14 and label it in square feet",
             "text": "The radius was given in feet, so the surface is measured in "
                     "square feet. And because a sphere has no sides to leave out, "
                     "there is nothing further to add — this number is already the "
                     "total.",
             "math": "16 × 3.14 = 50.24   →   50.24 ft²"},
        ],
        "answer": "50.24 ft²",
    }),

    (B.KIND_WORKED, {
        "number": "88.4",
        "question": "Find the total surface area of the rectangular solid. Dimensions "
                    "are in meters — a square base 2 m on a side, standing 5 m tall.",
        "steps": [
            {"label": "Build the formula before you build the answer",
             "text": "The question says **total**, so it is the sides plus the two "
                     "bases. Your book writes the formula out first and only then "
                     "reaches for numbers, which is worth copying — the 2 is much "
                     "easier to lose after the arithmetic has started. Your book also "
                     "mentions that this is the same rectangular solid you found the "
                     "volume of back in Example 69.1: same box, different question.",
             "math": "TSA = LSA + 2(A base)   →   TSA = Ph + 2(A base)"},
            {"label": "The base is a square, so P is four equal sides",
             "text": "Each side of the base is 2 m and a square has four of them. That "
                     "is the perimeter of the bottom face, which is the only perimeter "
                     "this rule ever wants.",
             "math": "P = 2 × 4 = 8 m"},
            {"label": "And the area of that same base is side times side",
             "text": "The base is 2 m by 2 m, so its area is 4 square metres. Notice "
                     "you are using the base twice in this problem, for two different "
                     "things — its perimeter goes into the sides, its area goes into "
                     "the lids.",
             "math": "A base = 2 × 2 = 4   →   4 m²"},
            {"label": "Substitute everything, then work it",
             "text": "Perimeter 8, height 5, base area 4, and two bases. The 8 times 5 "
                     "part is the LSA — the four walls — and the 2 times 4 part is the "
                     "top and the bottom.",
             "math": "TSA = 8 × 5 + 2 × 4 = 40 + 8"},
            {"label": "Add, and finish in square metres",
             "text": "Forty square metres of wall, eight square metres of lids. If you "
                     "had stopped at 40 you would have written down a perfectly correct "
                     "LSA for a question that asked for the TSA — which is the single "
                     "most common way to lose this one.",
             "math": "TSA = 40 + 8 = 48   →   48 m²"},
        ],
        "answer": "48 m²",
    }),

    (B.KIND_TRANSLATION, {
        "title": "The shorthand, decoded",
        "intro": "Both halves lean on abbreviations your book introduces once and then "
                 "never explains again. None of them are mathematics — they are labels, "
                 "and here is what each is short for.",
        "rows": [
            {"symbol": "syllogism", "plain": "a three-sentence argument: two premises "
                                             "and a conclusion drawn from them",
             "example": "Aristotle's, on page 1"},
            {"symbol": "premise", "plain": "one of the two introductory statements; "
                                           "your book also calls them propositions",
             "example": "All dogs have hair."},
            {"symbol": "major / minor", "plain": "which premise it is — the major one "
                                                 "names the set, the minor one names "
                                                 "the member",
             "example": "major first, minor second"},
            {"symbol": "argument", "plain": "the whole three-step process taken as one "
                                            "thing",
             "example": "a valid argument"},
            {"symbol": "valid", "plain": "the three sentences fit together properly. It "
                                         "says NOTHING about whether they are true",
             "example": "valid, and still false"},
            {"symbol": "p, q, r", "plain": "the property, the set, the member — letters "
                                           "standing for whole sentences, as in "
                                           "Lesson 81",
             "example": "If p, then q"},
            {"symbol": "Euler diagram", "plain": "circles inside circles, drawn to test "
                                                 "a syllogism (after Leonhard Euler)",
             "example": "forced to nest means valid"},
            {"symbol": "LSA", "plain": "lateral surface area — the sides of a right "
                                       "solid only, no top and no bottom",
             "example": "150.72 m²"},
            {"symbol": "TSA", "plain": "total surface area — the LSA plus the top and "
                                       "bottom faces",
             "example": "48 m²"},
            {"symbol": "P", "plain": "the perimeter of the BASE: the distance all the "
                                     "way around the bottom face",
             "example": "P = 8 m"},
            {"symbol": "h", "plain": "the perpendicular height — straight up from the "
                                     "base, never along a slant",
             "example": "h = 5 m"},
            {"symbol": "right solid", "plain": "a solid whose sides stand square to its "
                                               "base instead of leaning",
             "example": "a soup can"},
            {"symbol": "π", "plain": "3.14 in this course, every single time — your "
                                     "book says so at the top of the section",
             "example": "48π = 150.72"},
            {"symbol": "m²", "plain": "square metres. Every surface-area answer is an "
                                      "area, so it wears the little 2",
             "example": "48 m²"},
        ],
        "after": "Two of these matter more than the rest. **LSA and TSA differ by "
                 "exactly the two lids**, so a question that says *total* and an answer "
                 "that stopped at the sides are only one addition apart — and that "
                 "addition is the whole difference between right and wrong. And "
                 "**valid** is not a compliment. It says the argument is built "
                 "properly. It does not say the world agrees with it.",
    }),

    (B.KIND_ERRORS, {
        "title": "The six mistakes almost everyone makes",
        "items": [
            {"name": "Calling an argument invalid because it isn't true.",
             "wrong": "cats do not have eight tentacles, so the argument is invalid",
             "right": "cats do not have eight tentacles, so the argument is false   →   "
                      "whether it is valid is a separate test",
             "note": "**Two different questions, and this lesson only asks one of "
                     "them.** Your book is blunt: just because an argument is logical "
                     "does not mean it is true in reality. Your book also says 88.1b's "
                     "shape can be repaired by rearranging its three sentences — the "
                     "drop-down further down this page asks you which two move — and "
                     "the repaired version is a **valid** argument that is still "
                     "complete nonsense about tentacles. Test the shape first. Judge "
                     "the truth separately, and afterwards."},
            {"name": "The minor premise names the property instead of the set.",
             "wrong": "Jordan has eight tentacles   →   so Jordan is one of the cats",
             "right": "Jordan has eight tentacles   →   that is the property, not the "
                      "set   →   invalid",
             "note": "**This is the mistake the whole first half exists to catch.** "
                     "Here is one more to practise on, and this one is not in your "
                     "book: *All robins have feathers. Pepper has feathers. So Pepper "
                     "is a robin.* Having feathers does not make you a robin — a goose "
                     "has feathers. A minor premise has to say the member **is in** "
                     "the set, in so many words. Handing the member the same property "
                     "the major premise mentioned leaves both premises hanging off p, "
                     "and they never hook together. Your practice set will ask you "
                     "this again, so get the reason into words now."},
            {"name": "Using the radius as the perimeter of a circular base.",
             "wrong": "LSA = 3 × 8 = 24",
             "right": "LSA = 2 × 3.14 × 3 × 8 = 150.72",
             "note": "**24 instead of 150.72** — out by a factor of more than six. P "
                     "means *all the way around the base*, and for a circle that is the "
                     "circumference, 2πr. The radius is a line from the middle to the "
                     "edge, and nothing wraps around a can in a straight line. Whenever "
                     "the base is a circle, write `P = 2πr` on its own line before h "
                     "gets anywhere near it."},
            {"name": "Not squaring the radius in the sphere rule.",
             "wrong": "SA = 4 × 3.14 × 2 = 25.12",
             "right": "SA = 4 × 3.14 × 4 = 50.24",
             "note": "**25.12 instead of 50.24** — exactly half, because the radius "
                     "here happened to be 2. The rule is 4πr², so the radius is squared "
                     "**first** and only then does everything get multiplied together. "
                     "Square it on its own line: 2 squared is 4, and 4 is the number "
                     "that goes into the formula."},
            {"name": "Adding only one base to a total surface area.",
             "wrong": "TSA = 40 + 4 = 44",
             "right": "TSA = 40 + 2 × 4 = 48",
             "note": "**44 instead of 48.** A right solid has a top *and* a bottom, "
                     "which is precisely why the rule carries a 2: TSA = Ph + 2(area of "
                     "the base). The other half of this trap is stopping at 40 "
                     "altogether — that is the LSA, and it is the correct answer to a "
                     "question nobody asked."},
            {"name": "Finishing an area answer in the wrong units.",
             "wrong": "150.72 m",
             "right": "150.72 m²",
             "note": "Surface area is an **area**, so it is measured in square units "
                     "every single time — square metres, square feet, square "
                     "millimetres. A length unit on an area answer is marked wrong even "
                     "when the number is perfect, and it is the cheapest mark on the "
                     "page to lose. Example 88.2 ends in m², 88.3 in ft², 88.4 in m²."},
        ],
    }),

    (B.KIND_REVEAL, {
        "prompt": "Your book says Example 88.1b would become valid if two of its three "
                  "sentences were switched. Which two, and what does the repaired "
                  "argument say? Decide before you open this.",
        "answer": "**The minor premise and the conclusion trade places.** Leave the "
                  "first sentence alone and swap the other two:   →   Major premise: "
                  "All cats have eight tentacles.   →   Minor premise: Jordan is a "
                  "cat.   →   Conclusion: Jordan has eight tentacles.   →   Now run the "
                  "test on it. The set is still *all cats* and the property is still "
                  "*having eight tentacles*, because the major premise never moved. But "
                  "the minor premise now puts a member **inside** the set instead of "
                  "merely handing him the property, and the conclusion links the "
                  "property to the member. All three jobs are done by the right "
                  "sentence, so the argument is **valid**.   →   And it is still "
                  "nonsense, because cats do not have eight tentacles. That is the "
                  "point your book keeps making and the one thing worth carrying out of "
                  "this half: **valid is about the shape of the argument, not the truth "
                  "of it.**",
    }),

    (B.KIND_RECAP, {
        "title": "Remember this",
        "items": [
            "A **syllogism** is three sentences — a major premise, a minor premise and "
            "a conclusion drawn from them. The whole three-step thing is called an "
            "**argument**, and the premises are also called **propositions**.",
            "The major premise gives a **property (p)** to a whole **set (q)**. The "
            "minor premise puts a **member (r)** inside that set. The conclusion links "
            "the property to the member.",
            "**The minor premise is the one that decides.** If it names the property "
            "instead of naming the set, the argument is invalid — and it will sound "
            "exactly like a valid one.",
            "**Valid is a shape, not a truth.** An argument about cats with eight "
            "tentacles can still be valid. Lesson 81 said the same thing about "
            "if-then statements.",
            "An **Euler diagram** settles it faster than letters do. If the premises "
            "force the circles to nest — the member has nowhere else to go — the "
            "argument is valid; if they leave the member two legal places to stand, "
            "inside the set or outside it, it is invalid.",
            "**LSA = Ph.** The lateral surface area of a right solid is the perimeter "
            "of the **base** times the **perpendicular** height. Sides only — no top, "
            "no bottom.",
            "**TSA = LSA + 2(area of the base)**, for right solids. Two bases, so the "
            "2 is not optional.",
            "Build P out of the base's own shape: a square of side s gives 4s, a "
            "rectangle gives 2(l + w), and a circle gives its circumference, 2πr.",
            "A sphere has no sides, so it gets its own rule and that answer is already "
            "the total: **SA = 4πr²**. Square the radius before you multiply anything.",
            "Use **3.14** for π, and finish every one of these answers in **square** "
            "units.",
        ],
    }),
]

STUDENT_INTRO = (
    "Watch DIVE Lecture 88 first. If it didn't quite land, this is here to fix that. "
    "Two halves today, and they have nothing to do with each other. The first is a "
    "three-sentence argument called a syllogism, where the whole test turns on the "
    "middle sentence. The second is surface area, which is gentler than it sounds: "
    "unroll the sides of a solid and they flatten into one rectangle."
)

PARENT_CONTENT = """## The big idea

Two halves with nothing in common. Teach them as two short lessons — separate
sittings if the day allows it. Nothing in 88B needs 88A.

**88A — the syllogism.** Three sentences: a major premise, a minor premise, and a
conclusion drawn from them. Aristotle's own is the book's example: *Mortality is
for all men. That man is Aristotle. Mortality is for Aristotle.* The test for a
**valid** argument is a three-part checklist — the major premise identifies a
property (p) of a set (q), the minor premise identifies a member (r) **of the
set**, and the conclusion links the property with the member. Everything else is
invalid.

The whole lesson hangs on three words in the middle clause: *of the set*. Example
88.1b breaks there first, and the break spreads: because the minor premise never
puts Jordan in the set, the conclusion is left doing the minor premise's job
instead of linking the property to the member, so two of the three checks fail —
which is why repairing it takes two sentences and not one. "All cats have eight
tentacles. Jordan has eight tentacles. So Jordan is a cat." The minor premise
hands Jordan the **property**; it never says Jordan is a cat. Her practice set asks the same
question again in problem 288 with `Furbag` and four legs, so this is the sentence
to get right today. Say it to her this way: *having four legs doesn't make you a
cat — a table has four legs.*

The second thing that has to land is the one Lesson 81 already taught and that
children resist: **valid and true are different questions.** She will want to say
88.1b is invalid *because cats don't have tentacles*, and she will be right about
the tentacles and wrong about the reason. The book is explicit — "just because an
argument is logical does not mean it is true in reality" — and it proves the point
by telling her the very same nonsense would be **valid** if the minor premise and
the conclusion were switched. That swap is the predict-then-check drop-down on her
page; make her commit to an answer before she opens it.

Her page uses the **Euler diagram** as the working tool, because the book
recommends it: "using pictures like the Euler diagram is often easier than trying
to break the syllogism into p, q and r." The circles are drawn in her book. Her
page writes the same nesting with brackets — `[ things with hair [ all dogs
[ Rover ] ] ]` — so the two agree while she has both open.

Say the rule out loud the first time she draws, because the short version of it is
wrong. What makes an argument valid is that the premises leave the member
**nowhere else to go** — not merely that a nested picture *can* be drawn. Problem
288 can be drawn with Furbag inside the cats, and it is still invalid, because
nothing in it stops you drawing him outside them instead. Two legal pictures are
the signature of an invalid argument; her book only ever claims the other
direction, that a valid argument *will* be nested.

One oddity to have ready. The book's letter forms point *backwards* from how the
English sounds: the major premise "All dogs have hair" is written `If hairy then
dog`. Do not fight it and do not let her fight it. What is being tested is the
**pattern** — p to q, then q to r, therefore p to r — and the diagnostic is *where*
q sits: it ends one premise and starts the other, so the two hook together end to
end and q drops out of the conclusion. In 88.1b both premises begin at p, so q
never appears in both premises and nothing hooks. Be careful how you say this to
her. q does appear twice in 88.1b — in the major premise and again in the
conclusion — and so does every other letter, so **counting appearances is not the
test**. Neither is "a letter in both premises and not in the conclusion": in 88.1b
p does exactly that, and 88.1b is invalid. The letters are a way to check the
answer she already reached by asking whether the minor premise put a member in the
set. They are not a shortcut past that question.

**88B — surface area.** One rule and one exception. `LSA = Ph`: the lateral
surface area of a right solid is the perimeter of the **base** times the
**perpendicular** height — the sides only, no lids. `TSA = LSA + 2(A base)` adds
the top and the bottom back on. The exception is a sphere, which has no sides to
separate out, so `SA = 4πr²` is already the total. Use `3.14` for π throughout.

The intuition is worth five minutes with an actual can. Peel the label, flatten
it, and it is a rectangle whose long side is the distance around the can. That is
`LSA = Ph` in your hands, and it is why the same rule works for a shoebox: unroll
the four walls and they make one long rectangle. What varies between problems is
never the rule, only **how you get P** — hand it to her (problem 388 does), or
`4s` for a square base, or `2(l + w)` for a rectangle, or the circumference `2πr`
for a circle.

**About the figures.** All three surface-area examples are drawn in her guide and
the drawings are not reproduced on her page. Nothing is lost: every number comes
out of the book's own printed solution. `2π(3)(8)` fixes the cylinder at radius 3,
height 8 m; `4π(2)²` fixes the sphere at radius 2 ft; and `2•4 = 8` with `2(2•2)`
fixes Ex. 88.4 as a square base 2 m on a side, 5 m tall. Her page says this in one
sentence and asks her to check each figure in the book as she goes. Please do have
the book open beside her for that half.

## Teach it out loud in five minutes

Say these, in this order, and ask the question at each step.

1. Give her the good argument first and let it feel obvious: **"Everyone on the
   team has to be at practice by four. You're on the team. So?"** She finishes it
   without effort. Then: **"You just did a syllogism. It has a name because the
   next one is going to fool you."**
2. Now the bad one, said with exactly the same confidence: **"Everyone who was
   late got benched. Marcus got benched. So Marcus was late."** Ask: **"Does that
   follow?"** Wait. If she says yes, do not correct her — ask **"can you think of
   another reason to get benched?"** and let her find the ankle herself.
3. Point at the middle sentence of each. **"In the first one, the middle sentence
   put you *in* the group. In the second one, it only said Marcus had the same
   thing that happens to the group. That's the whole lesson."** Say it once more
   with the book's words: the minor premise must identify a **member of the set**.
4. Draw the circles for Rover — hair on the outside, dogs inside, Rover inside
   that — then ask her to draw them for Jordan. **"Where does Jordan's circle
   go?"** She will hesitate. Say: **"That hesitation is your answer. Your book
   promised you'd feel it."**
5. For the second half, hand her a soup can and a pair of scissors. **"Take the
   label off and flatten it. What shape is it?"** A rectangle. **"How long is the
   long side?"** Wrap a strip of paper around the can and lay it next to the
   label. Then: **"So how would you find the area of the side of this can?"** She
   will say the two multiplied. Write `LSA = Ph` under her answer and tell her she
   just derived the rule.

If the first half is lost, go back to step 3 and do nothing else. If the second
half is lost, it is almost always P — she has taken the perimeter of the wrong
face, or used a radius where a circumference was wanted.

## The classic mix-ups, with the exact wrong answer each one produces

- **Judging validity by truth.** She says 88.1b is invalid *because cats don't
  have tentacles*. Right verdict, wrong reason, and it will not transfer. Fix:
  make her say the reason out loud — *the minor premise never puts Jordan in the
  set* — and show her that the swapped version is valid and still absurd.
- **A minor premise that names the property.** `Jordan has eight tentacles` →
  treated as though it said `Jordan is a cat`. This is the error, and problem 288
  repeats it. Fix: three words, *is in the set*, checked out loud every time.
- **Radius used as the perimeter.** On Ex. 88.2 she writes `3 × 8` = **24**
  instead of `2 × 3.14 × 3 × 8` = **150.72**. Fix: whenever the base is a circle,
  `P = 2πr` gets its own line before h is allowed near it.
- **Radius not squared.** On Ex. 88.3 she writes `4 × 3.14 × 2` = **25.12**
  instead of `4 × 3.14 × 4` = **50.24** — exactly half, because r was 2. Fix:
  square the radius on its own line, then multiply.
- **One lid instead of two.** On Ex. 88.4 she writes `40 + 4` = **44** instead of
  `40 + 2 × 4` = **48**. Or she stops at **40**, which is a correct LSA for a
  question that asked for the TSA. Fix: read the question's own word — *total* —
  before the arithmetic starts, and circle it.
- **Linear units on an area.** `150.72 m` instead of `150.72 m²`. The number is
  perfect and the mark is gone. Fix: every answer in this half wears a little 2.

## What to watch her do

Watch her **hands**, in this order:

1. **On a syllogism, does her pencil go to the middle sentence first?** That is
   the whole diagnostic for the first half and you can see it from across the
   table. A pencil that starts at the conclusion is a child deciding whether she
   agrees with the ending, which is not what she was asked.
2. **Does she draw circles at all?** The book recommends the Euler diagram over
   the letters, and children who draw are markedly faster and steadier than
   children who juggle p, q and r in their heads. If she never draws, ask her to
   draw one — the one she hesitates over is an invalid syllogism, not a mistake.
   Check that she wrote *invalid* for it; the hesitation is the verdict, exactly
   as her book promised.
3. **Does the formula appear on the page before the numbers?** You want to see
   `LSA = Ph` or `TSA = Ph + 2(A base)` written out first, blank, and then filled.
   That habit is Lesson 78's, and it is what keeps the 2 alive in a TSA.
4. **On a circular base, does `2πr` get its own line?** Watch for a 3 sliding
   straight into the multiplication where a circumference belonged. This is a
   single-line habit that removes the most expensive mistake in the half.
5. **Does her final answer carry a square unit?** Look at the last thing she
   writes, not the working. `m²`, `ft²`, `mm²`. If the little 2 is missing more
   than once, stop the page and do five answers that are nothing but units.

Getting the right verdict on 88.1a and 88.1b is not what to watch for — there are
only two verdicts and she can hit one by coin flip. The reason she gives is the
thing that survives to the next argument.

## Extend it

- **Do practice problem 388 out loud with her.** The base perimeter is handed to
  her as `105.432` and the height is `40 mm`, so `105.432 × 40` = **4,217.28**.
  The problem itself says *don't overthink this*. If she reaches for π, or for a
  base area, or for anything at all beyond those two numbers, the rule has not
  landed yet and that is worth knowing before the practice set eats an hour.
- **Problem 488 is Ex. 88.3 with one number changed** — a sphere labelled `4 m`.
  Read as the radius, the way Ex. 88.3 reads its `2 ft`, that gives
  `4 × 3.14 × 16` = **200.96 m²**. Have her check the label on her own figure
  before she computes; that check is the habit, not the number.
- **Then ask the question those two spheres set up — but keep the units
  together.** Ex. 88.3's sphere is measured in **feet** and 488's in **metres**,
  so `50.24 ft²` and `200.96 m²` are not two measurements of the same kind of
  thing and must not be laid side by side as though one were the other doubled.
  Run the comparison inside one unit instead: ask her what a **4 ft** sphere
  would come to. `4 × 3.14 × 16` = **200.96 ft²**, which is four times
  `50.24 ft²`. Doubling the radius multiplied the surface by **four**, not by
  two. Ask her why, and let her find the squared r. This is genuinely surprising
  and the arithmetic is one line she has already done twice.
- **Collect a bad syllogism from real life.** They are everywhere: *everyone who
  cheats gets a zero; Ava got a zero; so Ava cheated.* Ask her to name which
  sentence has the wrong job. One a week for a month does more than any worksheet.
- **The one worth leaving open.** Ask her for an argument that is invalid but
  whose conclusion happens to be true — problem 288 is one, since Furbag may well
  be a cat. Noticing that a true ending can come out of a broken argument is the
  entire reason validity gets tested separately from truth.

## Where this sits

DIVE Lesson 88, *Logic: The Syllogism; Surface Area*. Reviews **Lessons 37, 42,
44, 67 and 81**.

**Lesson 81 is the one to revisit**, and it is the only one of the five inside this
course's seeded lessons. That is where `If p, then q` came from, where p and q
first stood for whole sentences rather than numbers, and where she first met the
fact that a logical statement need not be a true one. Lesson 88 adds one letter and
one sentence to all of that. **Lessons 37, 42, 44 and 67 sit outside this course's
seeded lessons and this guide has not read them** — so nothing here describes what
is in them. The book itself names two in passing: Euclid at Lesson 44 and analogies
at Lesson 37. Nothing on Lesson 88's pages depends on any of the four. Example 88.4
also points back to Example 69.1, the same rectangular solid whose volume she once
found; Lesson 69 is likewise outside this course, and 88.4 states everything it
needs.

Two threads worth naming. Her practice set carries **587**, the shrimp chart from
Lesson 87 — `$150` of budget, large shrimp, so estimate the band, then
`150 ÷ 10.45` = 14.35, round **down** to **14 lb** — which is Lesson 87's whole
method run again. And **1181** asks for the rate of change between `f(8) = 64` and
`f(9) = 81`, which is **17**: that is Lesson 81's calculus half, and it is the
thread that Lesson 89 picks up.

**Proficient** looks like: names the three parts of a syllogism, gets 88.1a and
88.1b right, and computes an LSA when the perimeter is handed to her.
**Mastered** looks like: says *why* a false-but-valid argument is not a
contradiction, builds P herself for a circular base, and never returns a TSA that
forgot a lid or an answer without square units.
"""


class Command(SaxonSeedCommand):
    help = ("Seed Saxon Pre-Algebra Lesson 88 (the syllogism; surface area) "
            "— idempotent.")

    LESSON_NUMBER = 88
    TITLE = "Check the Middle Sentence — The Syllogism, and Surface Area"
    STUDENT_INTRO = STUDENT_INTRO
    PARENT_CONTENT = PARENT_CONTENT
    BLOCKS = BLOCKS
