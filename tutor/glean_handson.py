"""Hands-on Glean options for Kaylin's Blackbird books.

WHY THESE EXIST. All six of I Am David's printed final projects end in writing —
an epilogue, an alternate ending, a research essay, an essay about a discussion
question. The Folk Keeper's are better, but four of its six are writing too.
Kaylin draws. She read the books; she did not want to write about them a seventh
time.

So each book gains one more option, alongside the printed ones. Not instead of:
the guide's six stay exactly as they are, so the record still shows the
purchased guide followed, and she picks.

WHAT MAKES THESE GRADE 7 AND NOT GRADE 3. Violet's hands-on Glean asks her to
draw what the music put in her head. These ask for drawings that carry an
argument — the same face twice and what changed between them; a journey drawn as
scenes rather than dots; the thing the book deliberately never describes. Every
one of them requires having read closely, and several cannot be done without
going back to the text. That is the point: the drawing is the comprehension
check.

PROMPTS SEND HER TO THE BOOK RATHER THAN ASSERTING ITS DETAILS. "Draw everything
David carried out of the camp — go back and get the list right" is a better
prompt than a list I supply, and it cannot be wrong.

Any of these can be done properly on paper and photographed in; the teacher note
says so, and for the big ones that is what I would do.
"""

from .models import Question

DRAW = Question.TYPE_DRAWING
WRITE = Question.TYPE_TEXT


def _drawing(prompt, hint, height=520):
    return ("application", prompt, hint,
            {"response_type": DRAW, "passage": {"height": height}})


def _written(prompt, hint):
    """The one place she writes — with the type-it/write-it picker."""
    return ("writing", prompt, hint,
            {"response_type": WRITE, "passage": {"answer_mode": True}})


def _self_eval(items):
    return ("reflection",
            "**How did it go?** Tap a face for each part. Nothing to write.",
            "Be honest — the useful answer is the true one.",
            {"response_type": Question.TYPE_SELF_EVAL,
             "passage": {"items": items,
                         "scale": ["Not yet", "Nearly", "Yes!"],
                         "notes": False}})


# ---------------------------------------------------------------------------
# I Am David — Anne Holm. A boy escapes a prison camp and crosses Europe alone.
# ---------------------------------------------------------------------------

I_AM_DAVID = {
    "title": "What David Saw",
    "intro": (
        "## 🧭 What David Saw\n\n"
        "David walked out of a camp and across a continent, and almost "
        "everything he met he was seeing for the first time. This project is "
        "that — drawn.\n\n"
        "There is **one** thing to write, at the end. Everything else you make. "
        "Work on paper if you'd rather; photograph it and upload it here."
    ),
    "steps": [
        _drawing(
            "**The bundle.** Draw everything David carried out of the camp, laid "
            "out flat like a museum case, each thing labelled. Go back to the "
            "book and get the list right — he did not carry much, and every "
            "single item mattered to him.",
            "Draw them at the size they matter, not the size they are. Label in "
            "your own hand.",
            480),
        _drawing(
            "**First colour.** David had spent his life somewhere grey. Find the "
            "moment in the book where he first really SEES something — colour, "
            "or beauty, or the sea — and draw it the way somebody would see it "
            "who had never seen it before.",
            "This is the hard one, and the best one. How do you draw a colour "
            "somebody has never met? Think about how much of the page it takes up.",
            560),
        _drawing(
            "**The journey.** Map David's route out of the camp and north. "
            "Instead of a dot at each place, draw a small scene of what happened "
            "there — six or seven of them, joined by his path.",
            "Check the countries against the book rather than guessing. Small "
            "scenes, drawn tight — this is a map made of pictures.",
            620),
        _drawing(
            "**The same face, twice.** David on the day he got out, and David on "
            "the last page. Same boy, drawn twice, side by side.",
            "Everything you know about what changed has to live in the second "
            "face. Nothing else on the page is allowed to explain it.",
            520),
        _drawing(
            "**The cover.** Pick the ONE moment you would put on the cover of a "
            "new edition of this book, and draw it. Title and author on the "
            "page, in your own lettering.",
            "A cover has to make somebody pick the book up without spoiling what "
            "happens. Choose carefully.",
            600),
        _written(
            "**Why that moment?** In a short paragraph, say why you chose the "
            "scene you put on the cover — and what you wanted somebody who has "
            "never read the book to feel when they see it.",
            "This is the only writing in the whole project. Say the real reason, "
            "not the tidy one."),
        _self_eval([
            "I went back to the book to get the details right",
            "My two portraits of David really are different",
            "Somebody could follow David's journey from my map",
            "My cover would make a stranger pick the book up",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's six written options, earned the same "
        "way: a finished project, done with care, that connects to the story.\n\n"
        "**Every one of the printed six ends in writing.** This one has a single "
        "paragraph in it and five drawings, and it is not the easier option — "
        "each drawing carries an argument that cannot be made without having "
        "read closely.\n\n"
        "**What to look at**\n"
        "- *The bundle* and *the journey* are comprehension checks wearing "
        "different clothes. Wrong items or wrong countries mean a re-read, not a "
        "lower mark for drawing.\n"
        "- *The same face, twice* is the one that shows whether she understood "
        "the book. If the second David is only older, ask her what else changed.\n"
        "- *First colour* is the hardest and the most worth talking about. There "
        "is no right answer; there are answers she can defend.\n"
        "- The paragraph is the only writing. Judge whether she says a real "
        "reason, not whether it is polished.\n\n"
        "**On paper is fine** — photograph it, upload it to this section, tick "
        "it complete. The photo prints in her report the same as a drawing does."
    ),
}


# ---------------------------------------------------------------------------
# The Folk Keeper — Franny Billingsley. Corinna lives as Corin, keeps the Folk
# in the cellar, and finds out what she actually is.
# ---------------------------------------------------------------------------

FOLK_KEEPER = {
    "title": "The Cellar and the Sea",
    "intro": (
        "## 🌊 The Cellar and the Sea\n\n"
        "This book keeps two things hidden: what Corinna is, and what is down "
        "in the dark eating the food she leaves. You get to decide what both of "
        "them look like.\n\n"
        "There is **one** thing to write, at the end. Everything else you make. "
        "Work on paper if you'd rather; photograph it and upload it here."
    ),
    "steps": [
        _drawing(
            "**The Folk.** The book never lets you see them. Draw what you think "
            "is down there — using only what the story actually tells you: the "
            "sounds, the damage, what they will and will not accept.",
            "Everything you draw has to be defensible from the text. That "
            "constraint is the whole exercise.",
            560),
        _drawing(
            "**Corin and Corinna.** The same person, drawn twice — as the Folk "
            "Keeper everybody sees, and as herself.",
            "Not just different clothes. What does she do with her shoulders, "
            "her hands, her eyes, when she is being Corin?",
            520),
        _drawing(
            "**The Folk Keeper's kit.** Draw the tools of the job, laid out and "
            "labelled — what she takes down to the cellar and what each thing is "
            "for.",
            "Go back to the book for these. Anything you cannot find, leave out.",
            480),
        _drawing(
            "**Marblehaugh Park, from above.** Draw the place as a map — the "
            "house, the cellar, the sea, and the paths between them. Mark where "
            "the important things happen.",
            "A reader who has never been there should be able to follow the "
            "story on your map.",
            600),
        _drawing(
            "**Sealfolk.** Design one. Not a seal and not a person — the thing "
            "the story is actually describing.",
            "The interesting decision is what you keep from each and what you "
            "refuse to.",
            560),
        _written(
            "**The sea.** Corinna writes about the sea more beautifully than "
            "about anything else. In a short paragraph, say what the sea is "
            "doing in this book — what it means, not what happens in it.",
            "This is the only writing in the whole project. There is more than "
            "one right answer; pick one and back it."),
        _self_eval([
            "Everything in my Folk drawing can be defended from the book",
            "Corin and Corinna read as the same person",
            "Somebody could follow the story on my map",
            "My sealfolk is neither a seal nor a person",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's six, earned the same way. Four of the "
        "printed six end in writing; this one has a single paragraph and five "
        "drawings, and it is not the easier option.\n\n"
        "**What to look at**\n"
        "- *The Folk* is the best question in the book made visible. The test is "
        "not whether it is frightening but whether every choice can be pointed "
        "back to a line of the text. Ask her to justify one detail.\n"
        "- *Corin and Corinna* is the comprehension check: if the only difference "
        "is clothing, she has the disguise but not the person.\n"
        "- *The kit* and *the map* both send her back to the book, which is the "
        "point of them.\n"
        "- The paragraph is the only writing. Judge the thinking, not the polish.\n\n"
        "**On paper is fine** — photograph it, upload it to this section, tick "
        "it complete."
    ),
}




# ---------------------------------------------------------------------------
# Violet's three, at nine. Same idea as Kaylin's, pitched younger: the drawings
# still need the book, but they are invitations rather than arguments.
# ---------------------------------------------------------------------------

RICKSHAW_GIRL = {
    "title": "Naima Paints",
    "intro": (
        "## 🎨 Naima Paints\n\n"
        "Naima is the best alpana painter in her village, and by the end of the "
        "book she is painting something much bigger. This project is all "
        "painting and drawing — there is **one** thing to write, right at the "
        "end.\n\n"
        "Do it on paper if you'd rather, then photograph it and upload it here."
    ),
    "steps": [
        _drawing(
            "**An alpana.** Look at the patterns printed at the start of each "
            "chapter in your book — those are alpanas. Draw one of your own in "
            "that style.",
            "Alpanas are built out of the same shape repeated and turned. Start "
            "in the middle and work outwards.",
            520),
        _drawing(
            "**Paint the rickshaw.** Draw a rickshaw panel the way Naima would "
            "paint one — as bright and as full as you can make it.",
            "Rickshaw panels are covered edge to edge. Leave no boring corners.",
            520),
        _drawing(
            "**The day it went wrong.** Find the moment in the book where "
            "Naima's plan goes badly wrong, and draw it.",
            "Faces matter here. What is she feeling in the second it happens?",
            480),
        _drawing(
            "**An alpana for YOUR family.** Design one for something your own "
            "family celebrates. Same style, your celebration.",
            "What colours and shapes belong to your family? There is no wrong "
            "answer to this one.",
            520),
        _written(
            "**Tell her.** If you could say one thing to Naima at the end of the "
            "book, what would it be? A few sentences is plenty.",
            "This is the only writing in the whole project."),
        _self_eval([
            "I looked at the alpanas in my book before I drew mine",
            "My rickshaw panel is bright all the way to the edges",
            "My family's alpana really is about my family",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's six printed options, earned the same "
        "way — and it is not the easier option: the first and third both send "
        "her back to the book.\n\n"
        "**What to look at**\n"
        "- *An alpana* is a looking exercise. Did she study the chapter-heading "
        "patterns, or invent from nothing? Ask her to point at the one she "
        "copied from.\n"
        "- *The day it went wrong* is the comprehension check — the wrong scene "
        "means a re-read, not a lower mark for drawing.\n"
        "- *An alpana for your family* is the one that matters most and the one "
        "with no wrong answer.\n"
        "- The few sentences at the end are the only writing. Judge whether she "
        "means it.\n\n"
        "**On paper is fine** — and for the alpanas, better. Photograph it, "
        "upload it here, tick it complete."
    ),
}


MISS_AGNES = {
    "title": "The Year Everything Changed",
    "intro": (
        "## 🏫 The Year Everything Changed\n\n"
        "Miss Agnes walked into a one-room school in Alaska and changed almost "
        "everything about it. This project is that year, drawn.\n\n"
        "There is **one** thing to write, right at the end. Do it on paper if "
        "you'd rather and photograph it in."
    ),
    "steps": [
        _drawing(
            "**The schoolroom, before and after.** Miss Agnes changed the room "
            "almost straight away. Draw it twice — how it was, and how it "
            "became. Same room, two pictures.",
            "Go back to the book for what she actually did to it. The "
            "difference between your two pictures IS the answer.",
            560),
        _drawing(
            "**Outside.** Draw the village and the country around it, in the "
            "season the story spends most of its time in.",
            "Alaska is the other main character in this book. What is the "
            "weather doing?",
            520),
        _drawing(
            "**Talking without words.** Bokko is deaf, and by the end of the "
            "book she is not shut out any more. Draw the moment that changes.",
            "Hands are hard to draw and worth trying. Look at your own while "
            "you draw.",
            480),
        _drawing(
            "**Your wall.** Miss Agnes covered her walls with pictures of the "
            "whole world. If the wall were yours, what would you put on it? "
            "Draw the wall.",
            "Whatever you would actually want to look at every day. That is the "
            "only rule.",
            560),
        _written(
            "**Why did she come back?** Miss Agnes did not have to return. In a "
            "few sentences, say why you think she did.",
            "This is the only writing in the project. Use what the book showed "
            "you about her."),
        _self_eval([
            "My two schoolrooms really are different",
            "I checked the book for what Miss Agnes changed",
            "You can tell what the weather is doing in my outside picture",
            "My wall is full of things I would actually want to look at",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "Four of the guide's six printed options are research reports or "
        "writing. This one is drawn, and it is not the easier option — the "
        "before-and-after cannot be done without going back to the text.\n\n"
        "**What to look at**\n"
        "- *Before and after* is the comprehension check. If the two rooms are "
        "the same but tidier, she has missed what Miss Agnes actually did.\n"
        "- *Talking without words* is the heart of the book. There is more than "
        "one right moment; ask her why she chose hers.\n"
        "- *Your wall* is hers. No wrong answers, and worth talking about.\n"
        "- The few sentences at the end are the only writing.\n\n"
        "**On paper is fine** — photograph it, upload it here, tick it complete."
    ),
}


HUNDRED_DRESSES = {
    "title": "A Hundred Dresses",
    "intro": (
        "## 👗 A Hundred Dresses\n\n"
        "Wanda said she had a hundred dresses at home. She wasn't lying — but "
        "you have to finish the book to find out why. This project is the "
        "drawing one, done properly.\n\n"
        "There is **one** thing to write, right at the end. Paper is lovely for "
        "this — photograph it and upload it here."
    ),
    "steps": [
        _drawing(
            "**Ten dresses.** Design ten of Wanda's hundred, on one page. All "
            "different, all coloured in.",
            "Wanda drew hers from her head, in a house with almost nothing in "
            "it. Ten is a lot — start small and fill the page.",
            620),
        _drawing(
            "**Room 13.** Draw the classroom, and show where everybody sat — "
            "including the corner Wanda sat in.",
            "The book tells you exactly where she sat and why. Go and find it.",
            520),
        _drawing(
            "**The day they walked in.** Find the moment the girls come into the "
            "classroom and stop short, and draw what they saw.",
            "This is the biggest moment in the book. How much of the page does "
            "it take up?",
            560),
        _drawing(
            "**A picture for Wanda.** Wanda gave two drawings away at the end. "
            "Draw something you would give to her.",
            "It can be anything. Think about what she would like, not what you "
            "like.",
            520),
        _written(
            "**What would you say?** If Wanda were standing in front of you, "
            "what would you say to her? A few sentences.",
            "This is the only writing in the project. Say the true thing."),
        _self_eval([
            "I really drew ten different dresses",
            "I found where Wanda sat before I drew Room 13",
            "My picture of the classroom shows why the girls gasped",
            "I thought about Wanda when I chose her present",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "This is the guide's own option 3 — ten dress designs — done in the app "
        "instead of on the photocopier, with three more pieces around it. Not "
        "the easier option: two of the four send her back to the text.\n\n"
        "**What to look at**\n"
        "- *Ten dresses* is stamina as much as art. Ten genuinely different "
        "ones is the assignment; five and a shrug is not.\n"
        "- *Room 13* and *the day they walked in* are the comprehension checks. "
        "The corner Wanda sat in is stated in the book.\n"
        "- *A picture for Wanda* is the one that shows whether the book landed.\n"
        "- The few sentences are the only writing. This book is about somebody "
        "who said nothing while a friend was teased — if what she writes is "
        "uncomfortable, that is the book working.\n\n"
        "**On paper is fine, and for the dresses it is better** — photograph it, "
        "upload it here, tick it complete."
    ),
}


BOOKS = {
    "i_am_david": I_AM_DAVID,
    "folk_keeper": FOLK_KEEPER,
    "rickshaw_girl": RICKSHAW_GIRL,
    "miss_agnes": MISS_AGNES,
    "hundred_dresses": HUNDRED_DRESSES,
}


def questions(book):
    """The steps for one book, as the seeder's (category, prompt, hint, extra)."""
    import json

    out = []
    for category, prompt, hint, extra in BOOKS[book]["steps"]:
        out.append((category, prompt, hint, {
            "response_type": extra["response_type"],
            "passage": json.dumps(extra["passage"]),
        }))
    return out
