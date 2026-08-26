"""Hands-on Glean options — the girls MAKE something instead of writing about it.

WHY THESE EXIST. Every final project the printed guides offer ends in writing —
an epilogue, an alternate ending, a research essay. By the time a child reaches
the Glean section she has already written about the book repeatedly. Both girls
are makers. So each book gains ONE more option alongside the printed ones; the
guide's stay exactly as they are, so the record still shows the purchased guide
followed, and she picks.

WHAT CHANGED IN THE SECOND PASS. The first version of this file was five drawing
prompts in a row. Good prompts, but one mode repeated — and the thing that made
Violet's music project work was that it moved between listening, tapping and
drawing. For an artist the equivalent is not different senses but different
MATERIALS: clay, hand-mixed paint, sewing, printing, construction. Every project
below spans at least four, and no more than one step in each is drawing.

THERE IS NO WRITING IN THIS FILE. Not a paragraph, not "a few sentences", not a
caption that is a sentence in disguise. Hand-lettered labels on her own work are
fine — a child labelling her own museum case is not being asked to compose prose.

RULE ONE, AND IT IS THE ONE THAT KEEPS THESE HONEST: never state a number the
book has to supply. "Find three things he was given" is an unverified claim about
how often the book does something, and a child who hunts for three and finds one
concludes she read badly. Open counts cannot be wrong. Where a number does appear
below, it is because a character says it out loud in the text.

Everything is made on a kitchen table, photographed, and uploaded step by step —
Question.TYPE_PHOTO exists for exactly this.
"""

from .models import Question

DRAW = Question.TYPE_DRAWING
MAKE = Question.TYPE_PHOTO


def _photo(prompt, hint):
    """She built a real thing and photographs it. Many photos per step."""
    return ("application", prompt, hint, {"response_type": MAKE, "passage": {}})


def _drawing(prompt, hint, height=560):
    """The one drawing step. At most one per project, deliberately.

    allow_photo because a comic page or a charcoal cellar is often better on
    real paper than on a tablet, and the intro of every project already tells
    her she can photograph each piece. She gets both: the canvas, or a photo of
    what she did on paper.
    """
    return ("application", prompt, hint,
            {"response_type": DRAW,
             "passage": {"height": height, "allow_photo": True}})


def _self_eval(items):
    return ("reflection",
            "**How did it go?** Tap a face for each part. Nothing to write.",
            "Be honest — the useful answer is the true one.",
            {"response_type": Question.TYPE_SELF_EVAL,
             "passage": {"items": items,
                         "scale": ["Not yet", "Nearly", "Yes!"],
                         "notes": False}})


_ON_PAPER = ("Photograph each piece as you finish it and add it to that step. "
             "You can add more than one photo.")


# ---------------------------------------------------------------------------
# I Am David — Anne Holm. Kaylin, 12. A boy escapes a camp and crosses Europe.
# ---------------------------------------------------------------------------

I_AM_DAVID = {
    "title": "The David Museum",
    "intro": (
        "## 🏛️ The David Museum\n\n"
        "You are curating an exhibition about this book. Everything in it you "
        "make — nothing is written anywhere, and only one piece is drawn.\n\n"
        "Work in whatever you have: clay, card, paint, foil, string, things out "
        "of the recycling. " + _ON_PAPER
    ),
    "steps": [
        _photo(
            "**Case one: what he carried out.** Make every single thing David "
            "took with him when he escaped, at the size it really was. Go back "
            "to the first chapter and get the list right — he did not carry "
            "much, and the book tells you how it was wrapped. Lay the case out "
            "and hand-letter a small card for each thing: what it is, and the "
            "chapter it turns up in. Two lines, no more.",
            "Make them at real size, not miniature. A bar of soap you could "
            "actually hold says something a drawing of one does not."),
        _photo(
            "**Case two: what he was given.** A second, smaller case — "
            "everything you can find that came to him along the way, from "
            "somebody who chose to give it. Hunt the whole book. However many "
            "you turn up is the right number.",
            "Group them by who gave them, not by what they are. That grouping "
            "is the argument this case is making."),
        _photo(
            "**The colour wall.** Mix real paint. Start with the colours of the "
            "place he escaped from — go and look at what the book actually says "
            "was there, because there IS colour in the camp and most people "
            "miss it. Then mix every colour that stops him once he is out. "
            "Paint them as patches in the order he meets them and letter what "
            "each one belongs to.",
            "Mix them; do not use a colour straight out of the tube. Getting "
            "the exact green of something you have only read about is the whole "
            "exercise, and the failures are worth keeping."),
        _drawing(
            "**One chapter, six panels.** Pick a chapter and draw it as a comic "
            "— six panels, and **no narration boxes and no captions.** Only what "
            "a reader could actually see. Speech is allowed only if somebody "
            "says it in the book.",
            "The no-narration rule is the whole exercise. Anything you cannot "
            "show, you have to work out how to show.",
            620),
        _photo(
            "**The dust jacket.** Build the wraparound cover for a new edition — "
            "front, spine and back, in one strip, with your own lettering. On "
            "the inside flap, map his route. The book never names the country he "
            "starts in, so leave that end of your map blank, the way Anne Holm "
            "left it.",
            "Measure the spine with a strip of paper rather than a ruler — wrap "
            "it round the book and pinch it. The blank end of the map is not a "
            "mistake; it is the most interesting thing on the jacket."),
        _photo(
            "**Install it.** Set the whole exhibition up together, the way a "
            "museum would, and photograph it from low down and off to one side "
            "with a single lamp — not from above, and not with the big light on.",
            "One light from the side gives everything a shadow and makes the "
            "clay look like objects instead of lumps. Move the lamp about "
            "before you take the picture."),
        _self_eval([
            "I went back to the book for the escape kit instead of guessing",
            "My colours are mixed, not straight from the tube",
            "My six panels work with no narration at all",
            "Somebody could walk round my museum and follow the story",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's printed options, earned the same way: "
        "a finished project, done with care, that could not have been made "
        "without reading the book.\n\n"
        "**This is not the easier option.** Every printed option ends in writing; "
        "this one has none. What it has instead is five different materials and "
        "an escape-kit list that cannot be faked.\n\n"
        "**What to look at**\n"
        "- *Case one* is the comprehension check. The book is specific about what "
        "he carried and how it was wrapped. Wrong contents mean a re-read, not a "
        "lower mark for modelling.\n"
        "- *Case two* has no fixed answer on purpose — the count is hers to turn "
        "up. Ask her who gave what; the grouping is the argument.\n"
        "- *The colour wall* is the best conversation in the project. There is "
        "colour in the camp and most readers miss it; if she caught it, say so.\n"
        "- *Six panels* — if she has smuggled narration back in, that is the note "
        "to give. Everything has to be shown.\n"
        "- *The blank end of the map* is deliberate. If she asks whether she has "
        "missed the country's name, she has understood the book.\n\n"
        "**Materials**: the jacket needs one strip about 24 inches long — two "
        "cereal-box panels taped together, or parcel paper. Everything else is "
        "clay, paint and the recycling."
    ),
}


# ---------------------------------------------------------------------------
# The Folk Keeper — Franny Billingsley. Kaylin, 12.
# ---------------------------------------------------------------------------

FOLK_KEEPER = {
    "title": "The Keeper's Kit",
    "intro": (
        "## 🔦 The Keeper's Kit\n\n"
        "You are making the equipment for a job nobody sane would want. "
        "Everything here you build, sew or mix — one piece only is drawn, and "
        "there is nothing to write.\n\n" + _ON_PAPER
    ),
    "steps": [
        _photo(
            "**The charms.** Corinna protects herself with particular things, in "
            "particular places. Hunt the book for them and make them for real. "
            "If you have turned up fewer than a handful you have not gone back "
            "far enough.",
            "Use the real materials where you can, and a stand-in where you "
            "cannot — a twist of garden dirt does for anything you are not "
            "digging up."),
        _photo(
            "**What goes down to the Folk.** Make what she takes into the cellar "
            "— in clay, on a real plate. Go back to her Record and see what she "
            "actually brings and how often.",
            "Check whether the Record logs it every time or only sometimes. That "
            "changes how much food you make."),
        _photo(
            "**The sealskin.** Sew one, by hand, out of whatever cloth you have. "
            "Go and look up the lines that tell you how it fits and how heavy it "
            "is before you cut anything.",
            "Hand-sewn and slightly wrong is better than neat and invented. The "
            "weight matters more than the shape."),
        _drawing(
            "**The cellar, with nothing in it.** Draw the dark below the house — "
            "and no Folk anywhere in the picture. Not because they are absent, "
            "but because nobody in the book has ever seen them: they cannot bear "
            "light. Draw what a person WOULD see, and let the rest be dark.\n\n"
            "Work the way charcoal works: put the dark down first, then take "
            "light back out of it.",
            "The temptation is to draw a monster. The book refuses to, and it is "
            "more frightening for it. Everything you show has to be something a "
            "person could actually have seen.",
            620),
        _photo(
            "**The sea, in colours.** Corinna writes about the sea more carefully "
            "than about anything else. Go through the book for the places where "
            "she gives it a colour and mix each one as a real patch of paint. "
            "Take as many as you can; do not stop early.",
            "Put them in the order they happen in the book, not prettiest first. "
            "The order is doing something."),
        _photo(
            "**Hair up, hair down.** Two panels, made of fibre — thread, wool, "
            "string, anything. On one, her hair the way it is when she is Corin: "
            "cut with scissors, contained, kept. On the other, her hair the way "
            "it is when she is not: torn rather than cut, and running off the "
            "edge of the paper.",
            "Cut versus torn is the whole point. Do not draw this one — glue "
            "actual fibre down."),
        _self_eval([
            "Every charm I made, I turned up in the book",
            "There are no Folk in my cellar picture",
            "I looked up the lines about the sealskin before I cut",
            "My two hair panels really are cut and torn, not drawn",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's printed options. Four of the printed "
        "six end in writing; this one has none, and is not the easier option.\n\n"
        "**What to look at**\n"
        "- *The charms* are a whole-book re-read wearing a craft apron. Ask her "
        "where each one is in the text.\n"
        "- *The cellar* is the best idea in the book made visible. The test is "
        "not whether it is frightening but whether every mark could be something "
        "a person actually saw. Nobody has ever seen the Folk — they cannot bear "
        "light — and a drawing that shows them has missed the point.\n"
        "- *The sealskin* — hand-sewing is slow and that is fine. Check she went "
        "and looked the description up first.\n"
        "- *Hair up, hair down* is the comprehension check. If both panels look "
        "the same, she has the disguise but not the person.\n\n"
        "**Materials**: an old towel or layered paper beats a bed sheet for the "
        "sealskin. Garden dirt stands in for anything you would rather not go "
        "and dig up."
    ),
}


# ---------------------------------------------------------------------------
# Violet's three, at nine. Same idea, pitched younger: the making still needs
# the book, but the steps are invitations rather than arguments.
# ---------------------------------------------------------------------------

RICKSHAW_GIRL = {
    "title": "Naima's Colours",
    "intro": (
        "## 🎨 Naima's Colours\n\n"
        "Naima is the best alpana painter in her village. In this project you "
        "are going to **make your own paint** out of things from the kitchen, "
        "and then paint the way she does.\n\n"
        "Nothing to write. " + _ON_PAPER
    ),
    "steps": [
        _photo(
            "**The colour chart.** Go through the book and pick out every colour "
            "it says out loud. Paint a patch of each one and letter what it "
            "belongs to. However many the book names is how many you need.",
            "Only colours the book actually says. If you are not sure, go and "
            "look — that is the game."),
        _photo(
            "**Make the paint.** Real paint, out of the kitchen. Turmeric for "
            "yellow, cold tea for brown, beetroot juice for pink-red, a burnt "
            "matchstick or charcoal for black, brick or terracotta dust for "
            "orange. Grind each one, mix it with a little water and a squeeze of "
            "glue, and photograph your row of pots.",
            "Do this on a tray — beetroot stains everything it touches. The "
            "glue is what makes it stick instead of wiping off."),
        _photo(
            "**Paint the rickshaw panel.** Rickshaws are covered in painted "
            "pictures, and Naima's father's is one of them. Paint a panel with "
            "YOUR paints — flat bright colours first, all the way to the edges, "
            "and the black outlines last.",
            "Rickshaw art leaves no boring corners. Outlines go on at the very "
            "end, over the top of the colour, not before it."),
        _photo(
            "**An alpana, big.** Mix rice flour with water into a thin paste, go "
            "outside, and paint an alpana on a paving slab — as wide as your "
            "arms can reach. Start in the middle and work outwards.",
            "Needs a dry day and somewhere outdoors. Alpanas are built from one "
            "shape repeated and turned, so pick your shape before you start."),
        _photo(
            "**Photograph it, then wash it away.** Take your picture of the "
            "alpana first — then wash it off the slab with a bucket of water, "
            "which is what really happens to them.",
            "Take the photo before the water. Once it is gone, the photograph "
            "is the only one there is."),
        _self_eval([
            "Every colour on my chart is one the book says",
            "I made my own paint out of real things",
            "My rickshaw panel is bright all the way to the edges",
            "My alpana was as wide as my arms",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's printed options, earned the same "
        "way, and it is **not the easier option** — grinding a pigment that "
        "actually works is harder than writing a paragraph about one.\n\n"
        "**Why this one is worth the mess.** The material itself is the "
        "comprehension check: she makes Naima's kind of paint out of Naima's "
        "kind of things, paints what Naima paints, and ends on the book's own "
        "ending by washing her work away.\n\n"
        "**What to look at**\n"
        "- *The colour chart* sets no number on purpose. However many the book "
        "names is right. Ask her to point at one in the text.\n"
        "- *Make the paint* is the heart of it. Home-made paint is streaky and "
        "pale; that is what home-made paint is.\n"
        "- *The alpana* needs a dry day and a paving slab — schedule it rather "
        "than springing it.\n\n"
        "**Warn her before the last step that the washing-away is deliberate**, "
        "or losing an hour's work reads as a punishment rather than the point."
    ),
}


MISS_AGNES = {
    "title": "The Room Miss Agnes Made",
    "intro": (
        "## 🏫 The Room Miss Agnes Made\n\n"
        "This whole book is about one room changing. You are going to build that "
        "room twice — once before she arrives, and once after.\n\n"
        "A shoebox or a cereal box is plenty. Nothing to write. " + _ON_PAPER
    ),
    "steps": [
        _photo(
            "**The room, before.** Build the schoolroom the way it is at the "
            "very start of the book, in a box. Walls, floor, whatever furniture "
            "the story gives you.",
            "Go back to the first chapter. What is on the walls at the "
            "beginning matters as much as what is on them later."),
        _photo(
            "**The room, after.** Now build it again — the same room once Miss "
            "Agnes has been there a while. Everything you add has to be "
            "something the book actually puts in the room.",
            "Two boxes side by side is the whole idea. Do not change the walls; "
            "change what is on them."),
        _photo(
            "**Mix the colours.** Do not use paint straight from the tube. Mix "
            "the colours you need for both rooms, and letter what each one is "
            "for.",
            "The two rooms should not be the same colour. Working out how they "
            "differ is the interesting part."),
        _photo(
            "**The timeline.** Miss Agnes makes a long paper timeline, and she "
            "makes it out of PICTURES rather than words. Look it up in the book, "
            "copy her marks, and draw each one as a picture the way she did. "
            "Then put it in your 'after' room.",
            "Copy the marks she actually uses — the book tells you several of "
            "them. Pictures, not words, because that was her whole idea."),
        _photo(
            "**The record.** Miss Agnes brings music. Cut a disc of black card "
            "and draw the music onto it as one unbroken spiral, from the outside "
            "edge into the middle — thick where it is loud, thin where it is "
            "soft, jagged or smooth as it sounds to you. Then stand it in your "
            "'after' room.",
            "One line, never lifted, all the way to the middle. Put a record on "
            "and draw while it plays."),
        _photo(
            "**Two photographs.** Photograph the finished 'after' room twice — "
            "once from down at a child's desk looking up, and once from the "
            "doorway looking in.",
            "Get the camera right down inside the box for the first one. The "
            "room looks like a different place from a desk than from the door."),
        _self_eval([
            "My 'before' room came from the first chapter",
            "Everything I added to the 'after' room is really in the book",
            "I mixed my colours instead of using them straight",
            "My timeline is pictures, like hers",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's printed options.\n\n"
        "**Why this one.** The book's subject is a single room changing, so "
        "building it twice is a comprehension check that leaves a non-reader's "
        "second box empty. It is **not the easier option**: she has to know what "
        "was in the room before anything can go into the box.\n\n"
        "**What to look at**\n"
        "- The *before* room is the one children skim. If it is bare, ask what "
        "the first chapter says was there.\n"
        "- The *timeline* is the best-grounded step: the book describes it and "
        "describes that it was made of pictures. Check she copied the marks "
        "rather than inventing them.\n"
        "- The *record disc* has no right answer. It is a listening exercise "
        "wearing a craft hat.\n\n"
        "**Scope**: two boxes is a long afternoon at nine. Splitting it across "
        "two days is fine and does not cost marks."
    ),
}


HUNDRED_DRESSES = {
    "title": "Room Thirteen",
    "intro": (
        "## 👗 Room Thirteen\n\n"
        "Wanda said she had a hundred dresses, all lined up in her closet. She "
        "was telling the truth — just not the way anybody thought.\n\n"
        "You are going to make them, and put them up the way they went up in the "
        "book. Nothing to write. " + _ON_PAPER
    ),
    "steps": [
        _photo(
            "**The colour chart.** The book gives some of the dresses a colour, "
            "and sometimes a colour for the trimming too. Go through and pick "
            "out every one it names, and mix that exact colour as a patch. "
            "Letter which dress each patch belongs to.",
            "Mix them — do not use the tube colour. Some of them have two "
            "colours, the dress and the trim, so those patches need both."),
        _photo(
            "**A hundred dresses, four ways.** Make them in four batches of "
            "about twenty-five, and change the material every batch: painted, "
            "then stamped or printed, then cut from catalogues or magazines, "
            "then coloured pencil. **No two the same** — that is the rule Miss "
            "Mason gives in the book.\n\nFold long strips concertina-style and "
            "cut several at once, then make each one different.",
            "A hundred sounds impossible and is not — concertina folding does "
            "most of the work. Different material each batch is what stops your "
            "hand getting bored."),
        _photo(
            "**Put them up.** Look up how the drawings were put up in the "
            "classroom — the book is very specific about where they went. Now do "
            "that in your own room, in the same places, and photograph it from "
            "the doorway.",
            "The book lists the places. Put yours where it says, not where it "
            "is easiest."),
        _photo(
            "**The dress she actually wore.** Make it, out of real cloth. Here "
            "is the thing to get right: it was **clean**. It was never pressed "
            "properly and it did not hang right, but it was clean. Crumple it, "
            "wet it, let it dry crumpled — do not stain it or dirty it.",
            "Getting this wrong is easy and it matters. She was poor, not "
            "grubby, and the book is careful about that."),
        _drawing(
            "**The two from the letter.** At the very end, Wanda says who should "
            "have which drawing. Draw those two — and draw them the way she drew "
            "them, because each one is a picture of the girl it is for.\n\n"
            "Draw the face last, and lightly.",
            "You can only do this step if you got to the last chapter. The faces "
            "are the whole point, and Wanda hid hers so quietly that neither "
            "girl noticed at first.",
            620),
        _self_eval([
            "Every colour on my chart is one the book names",
            "I used four different materials for my hundred dresses",
            "I put mine up where the book puts them",
            "My cloth dress is clean, just crumpled",
            "I am proud of at least one of these",
        ]),
    ],
    "rubric": (
        "## Teacher notes — Glean, hands-on option (20 points)\n"
        "The same 20 points as the guide's printed options, and it is **not the "
        "easier option** — a hundred dresses is more work than an essay, and the "
        "last step cannot be done without finishing the book.\n\n"
        "**What to look at**\n"
        "- *The colour chart* has no fixed count. However many the book names is "
        "right.\n"
        "- *A hundred dresses* is ambition on purpose, and the concertina fold "
        "makes it doable at nine. Check the four batches really are four "
        "materials.\n"
        "- *Putting them up* is a comprehension check — the book says exactly "
        "where the drawings went, and it is a lovely list.\n"
        "- *The cloth dress* is the one that carries the book's moral point. "
        "**Clean but unpressed.** If she has made it dirty, that is the "
        "conversation to have, and it is the most important one in the project.\n"
        "- *The two from the letter* cannot be done without finishing the book. "
        "If the faces are not likenesses of Peggy and Maddie, ask her to look "
        "at the last chapter again.\n\n"
        "**Scope**: a hundred is a lot. Twenty-five a day across four days, one "
        "material each day, is the intended shape."
    ),
}


BOOKS = {
    "i_am_david": I_AM_DAVID,
    "folk_keeper": FOLK_KEEPER,
    "rickshaw_girl": RICKSHAW_GIRL,
    "miss_agnes": MISS_AGNES,
    "hundred_dresses": HUNDRED_DRESSES,
}


HANDS_ON_SUFFIX = "(hands-on)"


def hands_on_title(book):
    """The set title for one book's hands-on option."""
    return "Section 5 · Glean: %s %s" % (BOOKS[book]["title"], HANDS_ON_SUFFIX)


def retire_superseded(lesson, new_title):
    """Make sure this lesson ends up with ONE hands-on set, called new_title.

    The seeders upsert on (lesson, title), so renaming a PROJECT — "What David
    Saw" becoming "The David Museum" — created a second set and left the first,
    meaning the child was offered both the retired writing-based project and its
    replacement.

    Renaming rather than deleting keeps work she has already done attached:
    _seed_set then updates that same row in place. But a set with the new title
    may ALREADY exist (a rename that has been seeded once), and two rows sharing
    a title would make the next upsert blow up with MultipleObjectsReturned — so
    the rename only happens when the destination is free.

    A superseded set that carries no work is deleted. One that carries work is
    left alone and reported, because silently binning a child's finished project
    is worse than a duplicate a parent can see.
    """
    from .models import QuestionSet, ResponseSheet

    target = QuestionSet.objects.filter(lesson=lesson, title=new_title).first()
    superseded = list(QuestionSet.objects.filter(
        lesson=lesson, title__endswith=HANDS_ON_SUFFIX).exclude(title=new_title))
    stranded = []
    for old in superseded:
        has_work = ResponseSheet.objects.filter(question_set=old).exists()
        if target is None:
            # The destination is free, so reuse this row and keep its work.
            QuestionSet.objects.filter(pk=old.pk).update(title=new_title)
            target = QuestionSet.objects.get(pk=old.pk)
            continue
        if has_work:
            stranded.append(old.title)
        else:
            old.delete()
    return stranded


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
