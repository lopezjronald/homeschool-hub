"""Operation Lexicon: Emily Dickinson — the guide's content, for Kaylin.

Blackbird & Company, by Kimberly Bredberg and Sara Evans. An ABCeDarian: 23
weeks, A through W, four words a week, every example drawn from Dickinson's own
poems and letters.

Each week is three days, the way the book lays it out:

    Day 1   two words — copy the word and its definition, copy Dickinson's
            lines, then craft a sentence of your own
    Day 2   two more words, the same three steps
    Day 3   choose the week's most interesting word and say why, then write a
            micro-story using as many of the week's words as you can

THE COPYING IS THE POINT. "Copy the word and the definition" and "copy the
lines from the poem" are handwriting exercises — the guide lists handwriting
practice and "contemplative attention to detail" among the skills it teaches,
and typing them would swap the skill for keyboard hunting. See WRITTEN_BY_HAND
in seed_lexicon_kaylin.

Text is transcribed from the printed guide by reading the pages, not from its
OCR layer: the OCR dropped whole headwords (week 2's "bisect" among them) and
garbled definitions she is meant to copy exactly.

``example_kind`` is "poem" for verse and "sentence" for prose, because the book
changes its instruction to match ("Copy the lines from the poem here" against
"Copy the sentence here").
"""

CURRICULUM_NAME = "Operation Lexicon: Emily Dickinson"

# The guide's own epigraph, and how it explains itself.
EPIGRAPH = ("By words the mind is winged.", "Aristophanes")

WHY_IT_EXISTS = """Finding just the right word can be a mighty struggle for
students and seasoned writers alike. Each week we will explore a cluster of
words and, teasing out their connotations, discover lost meanings and functions.
Our approach helps students to utilize higher order thinking skills by asking
them to slow down and mindfully consider each word's function in a well crafted,
complex example sentence. Over the course of this exploration, students will
unearth the rich potential in an ABCeDarian of words, enriching their lexicon
each week with four remarkable additions."""

# What the guide asks the student to do, in its own order.
HOW_A_DAY_RUNS = [
    "Read the word and its definition. If you need help saying it, look it up "
    "in a dictionary and read the phonetic notation, or use a dictionary that "
    "says it aloud — and if you are still unsure, just ask.",
    "Copy the word and its definition, thinking carefully about it as you "
    "write. Think about how it sounds and what it means.",
    "Read the example slowly, contemplating how this word is just the right "
    "word in this particular sentence.",
    "Copy the example, thinking carefully about it as you write.",
    "Craft an original sentence of your own using the word in an appropriate "
    "way.",
]

# Day 3's metaphor prompts, for when nothing comes.
STORY_STARTERS = [
    "COURAGE is a lion…",
    "JOY is a flame…",
    "IDEAS are water…",
    "PEACE is a cumulus cloud…",
    "KINDNESS is a garden blooming…",
    "SELFISHNESS is a stone…",
]

WEEKS = [
    {
        "number": 1,
        "letter": "A",
        "words": [
            {
                "day": 1,
                "word": "agate",
                "definition": "an ornamental stone consisting of a hard variety "
                              "of chalcedony, typically banded in appearance",
                "example": "To joint this Agate were a work—\nOutstanding Masonry—",
                "example_kind": "poem",
                "citation": "Thomas H. Johnson, The Complete Poems of Emily "
                            "Dickinson, 1134 pg. 509",
            },
            {
                "day": 1,
                "word": "alabaster",
                "definition": "a fine-grained, translucent form of gypsum, "
                              "typically white, often carved into ornaments",
                "example": "Safe in their Alabaster Chambers—",
                "example_kind": "poem",
                "citation": "Joyce Carol Oates, The Essential Emily Dickinson, "
                            "216 pg. 8",
            },
            {
                "day": 2,
                "word": "aliment",
                "definition": "food or nourishment",
                "example": "Let us hope they will yet be willing to share our "
                           "humble world and feed upon such aliment as we "
                           "consent to do!",
                "example_kind": "sentence",
                "citation": "Ellen Louise Hart and Martha Nell Smith, Open Me "
                            "Carefully, 2 pg. 9",
            },
            {
                "day": 2,
                "word": "ample",
                "definition": "enough or more than enough; plentiful",
                "example": "But if they only stay\nAmpler to fly away\nRiches are sad.",
                "example_kind": "poem",
                "citation": "Johnson, 1199 pg. 530",
            },
        ],
    },
    {
        "number": 2,
        "letter": "B",
        "words": [
            {
                "day": 1,
                "word": "babble",
                "definition": "talk rapidly and continuously in a foolish, "
                              "excited, or incomprehensible way",
                "example": "Babbles the Bee in a stolid Ear",
                "example_kind": "poem",
                "citation": "Oates, 216 pg. 9",
            },
            {
                "day": 1,
                "word": "bisect",
                "definition": "divide into two parts",
                "example": "Did but a snake bisect the brake\nMy life had forfeit been.",
                "example_kind": "poem",
                "citation": "Hart, 36 pg. 81",
            },
            {
                "day": 2,
                "word": "bestir",
                "definition": "make a physical or mental effort; exert or rouse "
                              "oneself",
                "example": "Once more, my now bewildered Dove\nBestirs her puzzled wings",
                "example_kind": "poem",
                "citation": "Johnson, 48 pg. 27",
            },
            {
                "day": 2,
                "word": "bough",
                "definition": "a main branch of a tree",
                "example": "Sitting a Bough like a Brigadier\nConfident and "
                           "straight—\nMuch is the mien of him in March\nAs a "
                           "magistrate—",
                "example_kind": "poem",
                "citation": "Johnson, 1177 pg. 523",
            },
        ],
    },
    {
        "number": 3,
        "letter": "C",
        "words": [
            {
                "day": 1,
                "word": "cajole",
                "definition": "persuade someone to do something by sustained "
                              "coaxing or flattery",
                "example": "It rises—passes—on our South\nInscribes a simple "
                           "Noon—\nCajoles a Moment with the Spires\nAnd "
                           "infinite is gone—",
                "example_kind": "poem",
                "citation": "Johnson, 1023 pg. 470",
            },
            {
                "day": 1,
                "word": "clandestine",
                "definition": "kept secret or done secretively, especially "
                              "because illicit",
                "example": "'Miss Mills,' that is, Miss Julia, never dreamed of "
                           "the depths of my clandestiny…",
                "example_kind": "sentence",
                "citation": "Hart, 16 pg. 45",
            },
            {
                "day": 2,
                "word": "consternation",
                "definition": "feelings of anxiety or dismay, typically at "
                              "something unexpected",
                "example": "I laughed a crumbling Laugh\nThat I could fear a "
                           "Door\nWho Consternation compassed\nAnd never "
                           "winced before.",
                "example_kind": "poem",
                "citation": "Oates, 609 pg. 47",
            },
            {
                "day": 2,
                "word": "cunning",
                "definition": "having or showing skill in achieving one's ends "
                              "by deceit or evasion",
                "example": "…so whitened by the snow you would think 'twas a "
                           "cunning artist had carved it from alabaster—.",
                "example_kind": "sentence",
                "citation": "Hart, 7 pg. 26",
            },
        ],
    },
    {
        "number": 4,
        "letter": "D",
        "words": [
            {
                "day": 1,
                "word": "damask",
                "definition": "having the velvety pink or light red color of a "
                              "damask rose",
                "example": "As of briar and leaf displayed\nFor my little damask maid",
                "example_kind": "poem",
                "citation": "Hart, 27 pg. 7",
            },
            {
                "day": 1,
                "word": "diadem",
                "definition": "a jeweled crown or headband worn as a symbol of "
                              "sovereignty",
                "example": "Unto supremest name—\nCalled to my Full—The "
                           "Crescent dropped—\nWith one small Diadem.",
                "example_kind": "poem",
                "citation": "Oates, 508 pg. 34",
            },
            {
                "day": 2,
                "word": "disown",
                "definition": "refuse to acknowledge or maintain any connection "
                              "with",
                "example": "— there is a darker spirit will not disown its child.",
                "example_kind": "poem",
                "citation": "Hart, 22 pg. 67",
            },
            {
                "day": 2,
                "word": "docile",
                "definition": "ready to accept control or instruction; submissive",
                "example": "Whether my bark went down at sea—\nWhether she met "
                           "with gales—\nWhether to isles enchanted\nShe bent "
                           "her docile sails—",
                "example_kind": "poem",
                "citation": "Johnson, 52 pg. 28",
            },
        ],
    },
    {
        "number": 5,
        "letter": "E",
        "words": [
            {
                "day": 1,
                "word": "edifice",
                "definition": "a building, especially a large, imposing one",
                "example": "Edifice of Ocean\nThy tumultuous Rooms\nSuit me at "
                           "a venture\nBetter than the Tombs",
                "example_kind": "poem",
                "citation": "Johnson, 1217 pg. 536",
            },
            {
                "day": 1,
                "word": "enamored",
                "definition": "have a liking or admiration for",
                "example": "While the Lovers sighed; and twined oak leaves, and "
                           "the anti enamored ate sugar, and crackers, in the "
                           "house, I went to see what I could find.",
                "example_kind": "sentence",
                "citation": "Hart, 7 pg. 25",
            },
            {
                "day": 2,
                "word": "ethereal",
                "definition": "heavenly or spiritual",
                "example": "He stuns you by degrees—\nPrepares your brittle "
                           "Nature\nFor the Ethereal Blow",
                "example_kind": "poem",
                "citation": "Oates, 315 pg. 16",
            },
            {
                "day": 2,
                "word": "exhilaration",
                "definition": "a feeling of excitement, happiness, or elation",
                "example": "Exhilaration is the Breeze\nThat lifts us from the "
                           "Ground\nAnd leaves us in another place\nWhose "
                           "statement is not found—",
                "example_kind": "poem",
                "citation": "Johnson, 1118 pg. 503",
            },
        ],
    },
    {
        "number": 6,
        "letter": "F",
        "words": [
            {
                "day": 1,
                "word": "fictitious",
                "definition": "not real or true, being imaginary or having been "
                              "fabricated",
                "example": "Vinnie is sewing away like a fictitious seamstress, "
                           "and I half expect some knight will arrive at the "
                           "door,…",
                "example_kind": "sentence",
                "citation": "Hart, 3 pg. 11",
            },
            {
                "day": 1,
                "word": "finite",
                "definition": "having limits or bounds",
                "example": "All Forests—Stintless Stars—\nAs much of Noon as I "
                           "could take\nBetween my finite eyes—",
                "example_kind": "poem",
                "citation": "Oates, 327 pg. 17",
            },
            {
                "day": 2,
                "word": "firmament",
                "definition": "the heavens or the sky, especially when regarded "
                              "as a tangible thing",
                "example": "To fetch her Grace—and Hue—\nAnd Fairness—and "
                           "Renown—\nThe Firmament's—To Pluck Her—\nAnd fetch "
                           "Her Thee—be mine—",
                "example_kind": "poem",
                "citation": "Johnson, 671 pg. 333",
            },
            {
                "day": 2,
                "word": "fortnight",
                "definition": "a period of two weeks",
                "example": "Susie—will you give my love to Mrs Bartlett, and "
                           "tell her the fortnight is out next Wednesday, and I "
                           "thought she m't like to know!",
                "example_kind": "sentence",
                "citation": "Hart, 14 pg. 43",
            },
        ],
    },
    {
        "number": 7,
        "letter": "G",
        "words": [
            {
                "day": 1,
                "word": "garner",
                "definition": "a storehouse; a granary",
                "example": "… for bleak, and waste, and barren, are most of the "
                           "fields found here, and I want you to fill the garner.",
                "example_kind": "sentence",
                "citation": "Hart, 16 pg. 46",
            },
            {
                "day": 1,
                "word": "grace",
                "definition": "simple elegance or refinement of movement",
                "example": "Like Time's insidious wrinkle\nOn a beloved Face\nWe "
                           "clutch the Grace the tighter\nThough we resent the "
                           "crease",
                "example_kind": "poem",
                "citation": "Johnson, 1236 pg. 543",
            },
            {
                "day": 2,
                "word": "grapple",
                "definition": "engage in a close fight or struggle without "
                              "weapons; wrestle",
                "example": "As by the dead we love to sit,\nBecome so wondrous "
                           "dear—\nAs for the lost we grapple\nTho' all the rest "
                           "are here—",
                "example_kind": "poem",
                "citation": "Johnson, 88 pg. 44",
            },
            {
                "day": 2,
                "word": "grisly",
                "definition": "causing horror or disgust",
                "example": "When everything that ticked—has stopped—\nAnd Space "
                           "stares all around—\nOr Grisly frosts—first Autumn "
                           "morns,\nRepeal the Beating Ground—",
                "example_kind": "poem",
                "citation": "Oates, 510 pg. 36",
            },
        ],
    },
    {
        "number": 8,
        "letter": "H",
        "words": [
            {
                "day": 1,
                # Printed with a capital H in the guide, where every other
                # headword is lower case. Kept as printed — she copies it.
                "word": "Habiliment",
                "definition": "clothing",
                "example": "Of impudent Habiliment\nAttired to defy,"
                           "\nImpertinence subordinate\nAt times to Majesty",
                "example_kind": "poem",
                "citation": "Johnson, 1279 pg. 559",
            },
            {
                "day": 1,
                "word": "hairbreadth",
                "definition": "a very small amount or margin",
                "example": "We like a Hairbreadth 'scape\nIt tingles in the "
                           "Mind\nFar after Act or Accident\nLike paragraphs of "
                           "Wind",
                "example_kind": "poem",
                "citation": "Johnson, 1175 pg. 522",
            },
            {
                "day": 2,
                "word": "hark",
                "definition": "listen",
                "example": "The man—to die—tomorrow—\nHarks for the Meadow "
                           "Bird—\nBecause its Music stirs the Axe\nThat clamors "
                           "for his head—",
                "example_kind": "poem",
                "citation": "Oates, 294 pg. 14",
            },
            {
                "day": 2,
                "word": "henceforth",
                "definition": "from this time on or from that time on",
                "example": "…they know that the man of noon, is mightier than "
                           "the morning and their life is henceforth to him.",
                "example_kind": "sentence",
                "citation": "Hart, 9 pg. 31",
            },
        ],
    },
    {
        "number": 9,
        "letter": "I",
        "words": [
            {
                "day": 1,
                "word": "incoherent",
                "definition": "expressed in an incomprehensible or confusing "
                              "way; unclear",
                "example": "Perhaps you can't read it, Darling, it is incoherent "
                           "and blind; but the recollection that prompts it, is "
                           "very distinct and clear, and reads easily.",
                "example_kind": "sentence",
                "citation": "Hart, 13 pg. 41",
            },
            {
                "day": 1,
                "word": "inebriate",
                "definition": "a drunkard",
                "example": "Inebriate of Air—am I—\nAnd Debachee of "
                           "Dew—\nReeling—thro endless summer days—\nFrom inns "
                           "of Molten Blue—",
                "example_kind": "poem",
                "citation": "Oates, 214 pg. 80",
            },
            {
                "day": 2,
                "word": "intercede",
                "definition": "intervene on behalf of another",
                "example": "And the preacher whose name is Love—shall intercede "
                           "there for us!",
                "example_kind": "sentence",
                "citation": "Hart, 5 pg. 15",
            },
            {
                "day": 2,
                "word": "intrude",
                "definition": "put oneself deliberately into a place or "
                              "situation where one is unwelcome or uninvited",
                "example": "Thank the wintry wind my dear one—that spares such "
                           "daring intrusion!",
                "example_kind": "sentence",
                "citation": "Hart, 1 pg. 7",
            },
        ],
    },
    {
        "number": 10,
        "letter": "J",
        "words": [
            {
                "day": 1,
                "word": "joggle",
                "definition": "move or cause to move with repeated small bobs "
                              "or jerks",
                "example": "Is it true, dear Sue?\nAre there two?\nI shouldn't "
                           "like to come\nFor fear of joggling Him!",
                "example_kind": "poem",
                "citation": "Johnson, 218 pg. 101",
            },
            {
                "day": 1,
                "word": "jostle",
                "definition": "push, elbow, or bump against someone roughly, "
                              "typically in a crowd",
                "example": "My thoughts are far from idle, concerning e'en the "
                           "trifles of the world at home, but all is jostle, "
                           "here—…",
                "example_kind": "sentence",
                "citation": "Hart, 21 pg. 57",
            },
            {
                "day": 2,
                "word": "jubilee",
                "definition": "a special anniversary of an event, especially one "
                              "celebrating twenty-five or fifty years of a reign "
                              "or activity",
                "example": "As if unto a Jubilee\n'Twere suddenly confirmed—",
                "example_kind": "poem",
                "citation": "Oates, 593 pg. 44",
            },
            {
                "day": 2,
                "word": "just",
                "definition": "based on or behaving according to what is morally "
                              "right and fair",
                "example": "Judgment is justest\nWhen the Judged,\nHis action "
                           "laid away,\nDivested is of every Disk\nBut his "
                           "sincerity",
                "example_kind": "poem",
                "citation": "Johnson, 1671 pg. 683",
            },
        ],
    },
    {
        "number": 11,
        # The ABCeDarian stops lining up exactly with the weeks here — this one
        # runs K into L.
        "letter": "K–L",
        "words": [
            {
                "day": 1,
                "word": "kindle",
                "definition": "arouse or inspire an emotion or feeling",
                "example": "I have heard it said 'persecution kindles'—think it "
                           "kindled me!",
                "example_kind": "sentence",
                "citation": "Hart, 19 pg. 51",
            },
            {
                "day": 1,
                "word": "kinsman",
                "definition": "a man who is one of a person's blood relations",
                "example": "And so, as Kinsmen, met a Night—\nWe talked between "
                           "the Rooms—\nUntil the Moss had reached our "
                           "lips—\nAnd covered up—our names—",
                "example_kind": "poem",
                "citation": "Oates, 451 pg. 30",
            },
            {
                "day": 2,
                "word": "knock",
                "definition": "strike a surface noisily to attract attention, "
                              "especially when waiting to be let in through a "
                              "door",
                "example": "But Rapture's Expense\nMust not be incurred\nWith a "
                           "tomorrow knocking\nAnd the Rent unpaid",
                "example_kind": "poem",
                "citation": "Johnson, 1679 pg. 686",
            },
            {
                "day": 2,
                "word": "languor",
                "definition": "the state or feeling, often pleasant, of "
                              "tiredness or inertia",
                "example": "There is a Languor of the Life\nMore imminent than "
                           "Pain—",
                "example_kind": "poem",
                "citation": "Oates, 396 pg. 23",
            },
        ],
    },
    {
        "number": 12,
        "letter": "L–M",
        "words": [
            {
                "day": 1,
                "word": "larceny",
                "definition": "theft of personal property",
                "example": "Night is the Morning's Canvas—\nLarceny—Legacy—"
                           "\nDeath, but our rapt attention\nTo Immortality—",
                "example_kind": "poem",
                "citation": "Hart, 31 pg. 77",
            },
            {
                "day": 1,
                "word": "lexicon",
                "definition": "the vocabulary of a person, language, or branch "
                              "of knowledge",
                "example": "Rapt Neighborhoods of Men—\nJust finding out—what "
                           "puzzled us—\nWithout the lexicon!",
                "example_kind": "poem",
                "citation": "Johnson, 246 pg. 112",
            },
            {
                "day": 2,
                "word": "longing",
                "definition": "a yearning desire",
                "example": "Longing is like the Seed\nThat wrestles in the Ground",
                "example_kind": "poem",
                "citation": "Johnson, 1255 pg. 549",
            },
            {
                "day": 2,
                "word": "maelstrom",
                "definition": "a situation or state of confused movement or "
                              "violent turmoil",
                "example": "A Crescent in the Sea—\nWith Midnight to the North "
                           "of Her—\nAnd Midnight to the South of Her—\nAnd "
                           "Maelstrom—in the Sky—",
                "example_kind": "poem",
                "citation": "Oates, 721 pg. 54",
            },
        ],
    },
    {
        "number": 13,
        "letter": "M–N",
        "words": [
            {
                "day": 1,
                "word": "merriment",
                "definition": "gaiety and fun",
                "example": "And Hands—so slight—\nThey would elate a Sprite\nWith "
                           "Merriment—",
                "example_kind": "poem",
                "citation": "Johnson, 283 pg. 130",
            },
            {
                "day": 1,
                "word": "mortify",
                "definition": "cause (someone) to feel embarrassed, ashamed, or "
                              "humiliated",
                "example": "—to come to Washington in his Dressing gown and "
                           "mortify me and Vinnie.",
                "example_kind": "sentence",
                "citation": "Hart, 21 pg. 57",
            },
            {
                "day": 2,
                "word": "musing",
                "definition": "a period of reflection or thought",
                "example": "It is such an evening Susie, as you and I would walk "
                           "and have such pleasant musings, if you were only "
                           "here—…",
                "example_kind": "sentence",
                "citation": "Hart, 2 pg. 8",
            },
            {
                "day": 2,
                "word": "native",
                "definition": "associated with the place or circumstances of a "
                              "person's birth",
                "example": "There's Grief of Want—and Grief of Cold—\nA sort they "
                           "call \"Despair—\nThere's Banishment from native "
                           "Eyes—\nIn sight of Native Air—",
                "example_kind": "poem",
                "citation": "Oates, 561 pg. 41",
            },
        ],
    },
    {
        "number": 14,
        "letter": "N–O",
        "words": [
            {
                "day": 1,
                "word": "nosegay",
                "definition": "a small bunch of flowers, typically one that is "
                              "sweet-scented",
                "example": "My nosegays are for Captives—\nDim—long expectant eyes,",
                "example_kind": "poem",
                "citation": "Johnson, 95 pg. 47",
            },
            {
                "day": 1,
                "word": "notability",
                "definition": "the fact or quality of being notable",
                "example": "The Clover's simple Fame\nRemembered of the Cow—\nIs "
                           "better than enameled Realms\nOf notability.",
                "example_kind": "poem",
                "citation": "Johnson, 1232 pg. 542",
            },
            {
                "day": 2,
                "word": "null",
                "definition": "cancel out",
                "example": "Nature's imposing negative\nNulls opportunity—",
                "example_kind": "poem",
                "citation": "Johnson, 1673 pg. 684",
            },
            {
                "day": 2,
                "word": "omen",
                "definition": "an event regarded as a portent of good or evil",
                "example": "I tried to think a lonelier Thing\nThan any I had "
                           "seen—\nSome Polar Expiation—An Omen in the Bone\nOf "
                           "Death's tremendous nearness—",
                "example_kind": "poem",
                "citation": "Oates, 532 pg. 38",
            },
        ],
    },
    {
        "number": 15,
        "letter": "O–P",
        "words": [
            {
                "day": 1,
                "word": "omnipresence",
                "definition": "the state of being widespread or constantly "
                              "encountered",
                "example": "One thing is true, Darling, the world will be none "
                           "the wiser, from Emilie's omnipresence, and two big "
                           "hearts will beat stouter, as tidings from me come in.",
                "example_kind": "sentence",
                "citation": "Hart, 16 pg. 45",
            },
            {
                "day": 1,
                "word": "ossify",
                "definition": "turn into bone or bony tissue",
                "example": "but I guess I'm made with nothing but a hard heart "
                           "of stone, for it dont break any, and dear Susie, if "
                           "mine is stony, your's is stone, upon stone, for you "
                           "never yield any, where I seem quite beflown. Are we "
                           "going to ossify always, say, Susie—how will it be?",
                "example_kind": "sentence",
                "citation": "Hart, 6 pg. 21",
            },
            {
                "day": 2,
                "word": "ostensibly",
                "definition": "apparently or purportedly, but perhaps not actually",
                "example": "To hang our head—ostensibly—\nAnd subsequent, to "
                           "find\nThat such was not the posture\nOf our immortal "
                           "mind—",
                "example_kind": "poem",
                "citation": "Johnson, 105 pg. 51",
            },
            {
                "day": 2,
                "word": "pensive",
                "definition": "engaged in, involving, or reflecting deep or "
                              "serious thought",
                "example": "The wave with eye so pensive, looketh to see the moon…",
                "example_kind": "poem",
                "citation": "Oates, 1 pg. 2",
            },
        ],
    },
    {
        "number": 16,
        "letter": "P–Q",
        "words": [
            {
                "day": 1,
                # Printed exactly like this in the guide. Standard spelling is
                # "perennial" — see "note", which the page shows her, because
                # she is copying this out by hand and should not learn it wrong.
                "word": "perrenial",
                "definition": "lasting or existing for a long or apparently "
                              "infinite time",
                "note": "The guide prints the headword as “perrenial”. The "
                        "standard spelling is “perennial” — Dickinson's own "
                        "letter reads “perrennial”, which the guide marks [sic] "
                        "in the example.",
                "example": "I have not asked you if you were cheerful and "
                           "well—and I cant think why, except that there's "
                           "something perrennial [sic] in those we dearly love, "
                           "immortal life and vigor…",
                "example_kind": "sentence",
                "citation": "Hart, 5 pg. 17",
            },
            {
                "day": 1,
                "word": "pinion",
                "definition": "a bird's wing as used in flight",
                "example": "It did not surprise me—\nSo I said—or thought—\nShe "
                           "will stir her pinions\nAnd the nest forgot",
                "example_kind": "poem",
                "citation": "Johnson, 39 pg. 23",
            },
            {
                "day": 2,
                "word": "propriety",
                "definition": "the details or rules of behavior conventionally "
                              "considered to be correct",
                "example": "I am trying to teach it a few of the proprieties of "
                           "life, now you are gone away, and the poor thing does "
                           "indeed seem quite obedient, and goes slowly eno'…",
                "example_kind": "sentence",
                "citation": "Hart, 14 pg. 42",
            },
            {
                "day": 2,
                "word": "quaint",
                "definition": "attractively unusual or old-fashioned",
                "example": "Some have resigned the Loom—\nSome—in the busy "
                           "tomb\nFind quaint employ.",
                "example_kind": "poem",
                "citation": "Hart, 35 pg. 81",
            },
        ],
    },
    {
        "number": 17,
        "letter": "Q–R",
        "words": [
            {
                "day": 1,
                "word": "quarry",
                "definition": "a place, typically a large, deep pit, from which "
                              "stone or other materials are or have been extracted",
                "example": "Generic as a Quarry\nAnd hearty—as a Rose—\nInvited "
                           "with Asperity\nBut welcome when he goes",
                "example_kind": "poem",
                "citation": "Johnson, 1316 pg. 571",
            },
            {
                "day": 1,
                "word": "quench",
                "definition": "satisfy one's thirst by drinking.",
                "example": "Blazing in Gold—and\nQuenching—in Purple!",
                "example_kind": "poem",
                "citation": "Hart, 68 pg. 104",
            },
            {
                "day": 2,
                "word": "quiver",
                "definition": "tremble or shake with a slight rapid motion",
                "example": "It quivers from the Forge\nWithout a color, but the "
                           "light\nOf unanointed Blaze.",
                "example_kind": "poem",
                "citation": "Oates, 365 pg. 21",
            },
            {
                "day": 2,
                "word": "rapt",
                "definition": "completely fascinated by what one is seeing or "
                              "hearing",
                "example": "Night is the Morning's Canvas—\nLarceny—Legacy—"
                           "\nDeath, but our rapt attention\nTo Immortality—",
                "example_kind": "poem",
                "citation": "Hart, 31 pg. 77",
            },
        ],
    },
    {
        "number": 18,
        "letter": "R–S",
        "words": [
            {
                "day": 1,
                "word": "redemption",
                "definition": "the action of saving or being saved from sin, "
                              "error, or evil",
                "example": "It's such a common—Glory—\nA Fisherman's—Degree—"
                           "\nRedemption—Brittle Lady—\nBe so—ashamed of Thee—",
                "example_kind": "poem",
                "citation": "Johnson, 401 pg. 191",
            },
            {
                "day": 1,
                "word": "replenish",
                "definition": "restore a stock or supply to a former level or "
                              "condition",
                "example": "To lose one's faith—surpass\nThe loss of an "
                           "Estate—\nBecause Estates can be\nReplenished—faith "
                           "cannot—",
                "example_kind": "poem",
                "citation": "Johnson, 377 pg. 180",
            },
            {
                "day": 2,
                "word": "retrospect",
                "definition": "a survey or review of a past course of events or "
                              "period of time",
                "example": "Just such a retrospect\nHath the perfected\nLife—",
                "example_kind": "poem",
                "citation": "Hart, 145 pg. 171",
            },
            {
                "day": 2,
                "word": "scant",
                "definition": "barely sufficient or adequate",
                "example": "Spending Scarlet, like a Woman\nYellow she "
                           "affords\nOnly scantly and selectly\nLike a Lover's "
                           "Words",
                "example_kind": "poem",
                "citation": "Johnson, 1045 pg. 477",
            },
        ],
    },
    {
        "number": 19,
        "letter": "S–T",
        "words": [
            {
                "day": 1,
                "word": "score",
                "definition": "a group or set of twenty",
                "example": "I wish the week had been more, a whole score of days "
                           "and joys for you, yet again, had it lasted longer, "
                           "then had you not come so soon and I had been "
                           "lonelier, it is right as it is!",
                "example_kind": "sentence",
                "citation": "Hart, 7 pg. 25",
            },
            {
                "day": 1,
                "word": "sophistry",
                "definition": "a fallacious argument",
                "example": "These are the days when skies resume\nThe old—old "
                           "sophistries of June—\nA blue and gold mistake.",
                "example_kind": "poem",
                "citation": "Oates, 130 pg. 4",
            },
            {
                "day": 2,
                "word": "sprightly",
                "definition": "lively; full of energy",
                "example": "Frank Pierce thinks I mean berage vail, and makes a "
                           "sprightly plan to import the 'article,' but dear "
                           "Susie knows what I mean.",
                "example_kind": "sentence",
                "citation": "Hart, 16 pg. 45",
            },
            {
                "day": 2,
                "word": "terrestrial",
                "definition": "of, on, or relating to the earth",
                "example": "You know how I must write you, down, down, in the "
                           "terrestrial—no sunset here, no stars; not even a bit "
                           "of twilight which I may poetize—and send you!",
                "example_kind": "sentence",
                "citation": "Hart, 5 pg. 15",
            },
        ],
    },
    {
        "number": 20,
        "letter": "T–U",
        "words": [
            {
                "day": 1,
                "word": "toy",
                "definition": "move or handle an object absentmindedly or "
                              "nervously",
                "example": "Toyed coolly with the final inch\nOf your delirious "
                           "Hem—",
                "example_kind": "poem",
                "citation": "Oates, 414 pg. 25",
            },
            {
                "day": 1,
                "word": "transfigure",
                "definition": "transform into something more beautiful or "
                              "elevated",
                "example": "Till the broken creatures—\nWe adored—for "
                           "whole—\nStains—all washed—\nTransfigured—mended—"
                           "\nMeet us—with a smile—",
                "example_kind": "poem",
                "citation": "Johnson, 428 pg. 205",
            },
            {
                "day": 2,
                "word": "trifle",
                "definition": "a thing of little value or importance,",
                "example": "There's Austin—he's a trifle—and trifling as it is "
                           "that he is coming Monday, it makes my heart (ink "
                           "blot covers 'beat') faster—Vinnie's a trifle too—Oh "
                           "how I love such trifles.",
                "example_kind": "sentence",
                "citation": "Hart, 18 pg. 49",
            },
            {
                "day": 2,
                "word": "unbare",
                "definition": "strip, uncover, bare",
                "example": "She dealt her pretty words like Blades—\nHow "
                           "glittering they shone—\nAnd every One unbared a "
                           "Nerve\nOr wantoned with a Bone—",
                "example_kind": "poem",
                "citation": "Oates, 479 pg. 32",
            },
        ],
    },
    {
        "number": 21,
        "letter": "U–V",
        "words": [
            {
                "day": 1,
                "word": "unconcern",
                "definition": "a lack of worry or interest",
                "example": "So preconcerted with itself—\nSo distant—to "
                           "alarms—\nAn Unconcern so sovereign\nTo Universe, or "
                           "me—",
                "example_kind": "poem",
                "citation": "Johnson, 290 pg. 135",
            },
            {
                "day": 1,
                "word": "undistinguished",
                "definition": "lacking distinction; unexceptional",
                "example": "Yesterday, undistinguished!\nEminent Today\nFor our "
                           "mutual honor,\nImmortality!",
                "example_kind": "poem",
                "citation": "Hart, 43 pg. 87",
            },
            {
                "day": 2,
                "word": "unobtrusive",
                "definition": "not conspicuous or attracting attention",
                "example": "Biography to All who passed\nOf Unobtrusive "
                           "Pain\nExcept for the italic Face\nEndured, "
                           "unhelped—unknown",
                "example_kind": "poem",
                "citation": "Johnson, 955 pg. 447",
            },
            {
                "day": 2,
                "word": "vacant",
                "definition": "having no fixtures, furniture, or inhabitants; "
                              "empty",
                "example": "—only dont be so happy as to let Mattie and me grow "
                           "dimmer and dimmer and finally fade away, and merrier "
                           "maids than we smile in our vacant places!",
                "example_kind": "sentence",
                "citation": "Hart, 2 pg. 10",
            },
        ],
    },
    {
        "number": 22,
        "letter": "V–W",
        "words": [
            {
                "day": 1,
                "word": "vast",
                "definition": "of very great extent or quantity; immense",
                "example": "Than Monotony\nKnew a particle, of\nSpace's\nVast "
                           "society—",
                "example_kind": "poem",
                "citation": "Hart, 96 pg. 127",
            },
            {
                "day": 1,
                "word": "verge",
                "definition": "an edge or border",
                "example": "Themselves the Verge of Seas to be—\nEternity—is "
                           "Those—",
                "example_kind": "poem",
                "citation": "Johnson, 695 pg. 342",
            },
            {
                "day": 2,
                "word": "vulgar",
                "definition": "lacking sophistication or good taste; unrefined",
                "example": "She never deemed—she hurt—\nThat—is not Steel's "
                           "Affair\nA vulgar grimace in the Flesh—\nHow ill the "
                           "Creatures bear—",
                "example_kind": "poem",
                "citation": "Oates, 479 pg. 33",
            },
            {
                "day": 2,
                "word": "wax",
                "definition": "become larger or stronger",
                "example": "Till, morning touching mountain,\nAnd Jacob waxing "
                           "strong,",
                "example_kind": "poem",
                "citation": "Hart, 39 pg. 83",
            },
        ],
    },
    {
        "number": 23,
        "letter": "W–Z",
        "words": [
            {
                "day": 1,
                "word": "whippoorwill",
                "definition": "a North and Central American nightjar with a "
                              "distinctive call",
                "example": "A feather from the Whippoorwill\nThat "
                           "everlasting—sings!\nWhose galleries—are "
                           "Sunrise—\nWhose Opera—the Springs—",
                "example_kind": "poem",
                "citation": "Johnson, 161 pg. 76",
            },
            {
                "day": 1,
                "word": "wick",
                "definition": "a strip of porous material up which liquid fuel "
                              "is drawn by capillary action to the flame in a "
                              "candle, lamp, or lighter",
                "example": "The Wicks they stimulate—\nIf vital Light",
                "example_kind": "poem",
                "citation": "Oates, 883 pg. 58",
            },
            {
                "day": 2,
                "word": "wondrous",
                "definition": "inspiring a feeling of wonder or delight; "
                              "marvelous",
                "example": "I can't believe you are coming—but when I think of "
                           "it, and tell myself it's so, a wondrous joy comes "
                           "over me, and my old fashioned life capers as in a "
                           "dream.",
                "example_kind": "sentence",
                "citation": "Hart, 20 pg. 54",
            },
            {
                "day": 2,
                "word": "zigzag",
                "definition": "a line or course having abrupt alternate right "
                              "and left turns",
                "example": "Leave my Needle in the furrow—\nWhere I put it "
                           "down—\nI can make the zigzag stitches\nStraight—when "
                           "I am strong—",
                "example_kind": "poem",
                "citation": "Johnson, 617 pg. 304",
            },
        ],
    },
]


def all_words():
    """Every word in the guide, in the order she meets them."""
    return [w for week in WEEKS for w in week["words"]]


def words_for_day(week, day):
    return [w for w in week["words"] if w["day"] == day]


def week_by_number(number):
    return next((w for w in WEEKS if w["number"] == number), None)
