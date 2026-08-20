"""Glean option 6 for "A Mouse Called Wolf" — the hands-on one.

WHY THIS EXISTS. The Blackbird guide offers five final projects and every one of
them ends in "write a paragraph". Violet read the book, liked it, and did not
want to do any of them — so this is a sixth option covering the same ground with
her hands instead of her pen. It is not a replacement: the guide's five stay
exactly as printed, so the record still shows the guide followed. She picks.

WHAT IT COVERS. Between them these eleven steps do the work of four of the
guide's five options, which is more coverage than choosing one of them:

    guide option 1 (composer compare)  -> listen and draw, three times, then pick
    guide option 3 (grand piano)       -> match the parts to their jobs, then draw one
    guide option 4 (your name)         -> ask out loud, then draw a name shield
    guide option 5 (musical terms)     -> match all fourteen, in two rounds

NOT ONE WORD OF WRITING. Six drawings, four tapping games and a tap-a-face
self-check. The only "writing" anywhere is optional labelling inside her own
drawings, in her own hand, because a nine-year-old labelling her own picture is
not the same task as being asked for a paragraph.

THE MUSIC IS NAMED, NOT LINKED. Any recording of these will do and links rot, so
the pieces are named precisely enough for a grown-up to find in one search.
"""

from .models import Question

# Famous enough that one search finds a good recording, and short enough that a
# nine-year-old is still drawing when it ends.
LISTENING = [
    ("Mozart", "Eine kleine Nachtmusik", "the first part — quick and bouncy",
     "Wolfgang Amadeus Mozart is who Wolf is named after."),
    ("Beethoven", "Für Elise", "the famous piano one",
     "Beethoven went deaf and kept writing music anyway."),
    ("Schubert", "The Trout (Die Forelle)", "the one that skips along like a fish",
     "Schubert wrote over six hundred songs, and died at only 31."),
]

# The guide's fourteen terms, in kid words. Split into two rounds because
# fourteen pairs on one screen is a wall, not a game.
TERMS_ROUND_1 = [
    ("melody", "the tune you are still humming after the music stops"),
    ("rhythm", "the beat your foot taps along to"),
    ("composer", "the person who makes the music up"),
    ("solo", "music played or sung by just one person, on their own"),
    ("ballad", "a slow song that tells a story"),
    ("carol", "a song people sing together at Christmas"),
    ("scales", "the notes climbing up or down in order, like a ladder"),
]
TERMS_ROUND_2 = [
    ("bass", "the deep, low, rumbly sounds"),
    ("key", "one of the black or white bars you press on a piano"),
    ("discordant", "sounds that clash and make you wince"),
    ("measure", "one small box of beats that music is cut into"),
    ("opus", "the number a composer's piece is labelled with"),
    ("reprise", "when a tune you already heard comes back again"),
    ("sonata", "a long piece, usually for one instrument on its own"),
]

# Inside a grand piano — the guide's "label the parts", as a tapping game. Every
# one of these is a thing she can see or hear if a grown-up opens a piano lid.
PIANO_PARTS = [
    ("the keys", "you press these to choose which note"),
    ("the strings", "these are what actually make the sound"),
    ("the hammers", "little felt mallets that fly up and hit the strings"),
    ("the pedals", "you press these with your feet to hold or hush the sound"),
    ("the lid", "the big top that props open to let the sound out"),
    ("the soundboard", "the big wooden sheet inside that makes the sound loud"),
]


def _matching(pairs, word_order):
    """The tapping game's payload: words on one side, numbered meanings on the other."""
    return {
        "response_type": Question.TYPE_MATCHING,
        "passage": {
            "words": list(word_order),
            "definitions": [{"n": i + 1, "text": meaning, "word": word}
                            for i, (word, meaning) in enumerate(pairs)],
        },
    }


def _drawing(height=420):
    return {"response_type": Question.TYPE_DRAWING, "passage": {"height": height}}


def _choice(options, figure=""):
    """A pick-one with NO right answer — nothing here gets marked wrong."""
    return {
        "response_type": Question.TYPE_CHOICE,
        "passage": {
            "options": [{"key": k, "text": t, "image": ""} for k, t in options],
            "correct": [], "multi": False,
            "figure": figure, "figure_caption": "",
        },
    }


INTRO = (
    "## 🎵 Wolf's Big Concert\n\n"
    "Wolf sang for Mrs Honeybee, and now he is putting on a concert of his own — "
    "and you are running it. There is **nothing to write** in this project. You "
    "listen, you tap, and you draw.\n\n"
    "Do it over a few days if you like. Every drawing is saved as you go."
)

RUBRIC = (
    "## Teacher notes — Glean, hands-on option (20 points)\n"
    "The same 20 points as the guide's five written options, earned the same "
    "way: a finished project, done with care, that connects to the story.\n\n"
    "**Grade the pictures, not the spelling.** Nine of the eleven answers are "
    "drawings or tapping games; there is no prose here to mark and none should "
    "be asked for. If she has labelled inside a drawing in her own hand, that is "
    "a bonus, not a requirement.\n\n"
    "**What each part is really assessing**\n"
    "- The three listening drawings and the pick (steps 1–4) are the guide's "
    "option 1, *composer compare*. Look for three drawings that are actually "
    "DIFFERENT from each other — that difference IS the comparison she would "
    "otherwise have written.\n"
    "- The two word rounds (steps 5–6) are the guide's option 5, *musical "
    "terms*, and mark themselves.\n"
    "- The piano parts and the piano drawing (steps 7–8) are the guide's "
    "option 3, *grand piano*.\n"
    "- The name shield (step 9) is the guide's option 4, *your name*. The "
    "interview happens out loud, at the kitchen table — that is the point of it.\n"
    "- The poster (step 10) is hers, and is where the book comes back.\n\n"
    "**If she works on paper.** Any of the drawings can be done properly on "
    "paper instead. Photograph it, upload it to this section, and tick it "
    "complete — the photo prints in her report the same as a drawing does."
)


def questions():
    """The eleven steps, in the order she meets them."""
    steps = []

    for composer, piece, describe, fact in LISTENING:
        steps.append((
            "application",
            "**Listen and draw — %s.** Ask a grown-up to play **%s** by %s (%s). "
            "While it plays, draw whatever the music puts in your head. There is "
            "no right picture." % (composer, piece, composer, describe),
            "%s Draw while it is still playing — do not wait until the end." % fact,
            _drawing(),
        ))

    steps.append((
        "application",
        "**Wolf's turn.** Wolf is going to sing at his concert. Whose music "
        "should he sing? Tap the one you liked best.",
        "There is no wrong answer here. Pick the one whose music you would "
        "want to hear again.",
        _choice([("a", "Mozart"), ("b", "Beethoven"), ("c", "Schubert")]),
    ))

    steps.append((
        "vocabulary",
        "**Music words, round 1.** Tap a word, then tap what it means.",
        "Say each word out loud first — some of them sound like what they mean.",
        _matching(TERMS_ROUND_1,
                  # Scrambled: straight down the list would be free marks.
                  ["composer", "scales", "melody", "carol", "solo", "rhythm",
                   "ballad"]),
    ))
    steps.append((
        "vocabulary",
        "**Music words, round 2.** Same game, seven more words.",
        "These are the trickier ones. If you are stuck, guess and see — you can "
        "change it.",
        _matching(TERMS_ROUND_2,
                  ["measure", "sonata", "bass", "reprise", "discordant", "opus",
                   "key"]),
    ))

    steps.append((
        "application",
        "**Inside the piano.** Mrs Honeybee's piano is a grand piano. Match each "
        "part to the job it does.",
        "If there is a piano near you, ask to look inside the lid while somebody "
        "presses a key. You can watch the hammer jump.",
        _matching(PIANO_PARTS,
                  ["the hammers", "the lid", "the keys", "the soundboard",
                   "the pedals", "the strings"]),
    ))
    steps.append((
        "application",
        "**Draw a grand piano.** Draw the whole thing, lid propped open, with the "
        "strings inside. Add the parts you just matched — you can write their "
        "names on your drawing if you want to.",
        "A grand piano is a big curved wing shape lying on three legs. Start with "
        "the wing, then the keys along the straight edge.",
        _drawing(480),
    ))

    steps.append((
        "application",
        "**Your name shield.** Ask your mum and dad, out loud: where did my name "
        "come from? Was I named after someone? What does it mean? Then draw a "
        "shield and fill it with PICTURES of what they told you — no sentences.",
        "Wolf was named after Wolfgang Amadeus Mozart. Split your shield into "
        "three or four parts and draw one thing in each.",
        _drawing(480),
    ))

    steps.append((
        "application",
        "**The concert poster.** Draw the poster for Wolf's concert. Who is "
        "singing, where is it, and who is coming? Make it the sort of poster that "
        "would make somebody stop and look.",
        "Think about who was in the book — Wolf, his mother, his brothers and "
        "sisters, Mrs Honeybee. Big shapes and bright colours read from across a "
        "room; tiny details do not.",
        _drawing(560),
    ))

    steps.append((
        "reflection",
        "**How did it go?** Tap a face for each part. Nothing to write.",
        "Be honest — the useful answer is the true one, not the nice one.",
        {
            "response_type": Question.TYPE_SELF_EVAL,
            "passage": {
                "items": [
                    "I listened to all three composers",
                    "My three music drawings are different from each other",
                    "I know what the parts of a piano do",
                    "I can explain what at least five music words mean",
                    "I asked about my name and drew what I found out",
                    "I am proud of my concert poster",
                ],
                "scale": ["Not yet", "Nearly", "Yes!"],
                "notes": False,
            },
        },
    ))
    return steps
