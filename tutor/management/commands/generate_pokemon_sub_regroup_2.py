"""Build the Ch3 L3 "The Empty Shelf" subtracting-across-zeros manga.

Whole cast returns from Lessons 1-2, so every character sheet is reused and a
full run draws only the eight panels.

The empty shelves are the lesson. Panels 2 and 3 have to read as *visibly,
unmistakably bare* — a shelf with a few berries on it teaches nothing — and
panels 4 and 5 have to show the two trades as two separate events in order.

Examples:
    python manage.py generate_pokemon_sub_regroup_2 --dry-run --curriculum 1
    python manage.py generate_pokemon_sub_regroup_2 --curriculum 1              # real art
    python manage.py generate_pokemon_sub_regroup_2 --only 4,5 --curriculum 1   # redraw the two trades
    python manage.py generate_pokemon_sub_regroup_2 --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-sub-regroup-2"
CHARACTERS = gen9("sprigatito", "fuecoco", "quaxly")
CAST = ["sprigatito", "fuecoco", "quaxly"]

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A berry storehouse: five big sealed crates along one wall, and two completely bare wooden shelves beside them.",
        "scene": "Wide establishing shot inside a warm wooden berry storehouse. Along the wall stand FIVE big "
                 "identical sealed crates. Beside them are TWO long wooden shelves, both completely EMPTY and "
                 "bare — not a single berry on either. The grass kitten SPRIGATITO, the red crocodile FUECOCO "
                 "and the blue-headed duckling QUAXLY stand together; QUAXLY holds a small paper order slip. "
                 "Dusty golden light through a high window.",
        "refs": CAST,
        "caption": "Five hundred berries in the storehouse. Nothing loose, nothing bundled.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 52, "y": 13, "text": "Someone's ordered 236!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito peers hopefully along a completely bare wooden shelf.",
        "scene": "SPRIGATITO the grass kitten stands on tiptoe peering along a long wooden shelf that is "
                 "completely, obviously EMPTY — bare boards, not one berry anywhere on it. Hopeful expression "
                 "turning puzzled. FUECOCO watches from behind.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 36, "y": 13, "text": "500 take away 236. I need 6 ones… and this shelf is EMPTY."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito turns to the second shelf — also completely bare — and its ears droop.",
        "scene": "SPRIGATITO turns hopefully to a SECOND long wooden shelf, which is also completely EMPTY and "
                 "bare, and its ears droop in dismay. FUECOCO stands calmly beside it, one claw pointing "
                 "further along the wall toward the row of big sealed crates.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 12, "text": "The tens shelf is empty too!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 72, "y": 20, "text": "Then keep walking."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Fuecoco cracks open one big crate and ten banded bundles spill onto the middle shelf; four sealed crates remain.",
        "scene": "FUECOCO the red crocodile levers the lid off ONE of the big crates. TEN neat bundles of "
                 "berries, each banded with a vine ribbon, spill out and land in a tidy row along the middle "
                 "wooden shelf, which was bare a moment ago. Behind, FOUR crates remain clearly sealed and "
                 "stacked. SPRIGATITO watches wide-eyed at the lower-left. Keep the entire upper third of the "
                 "frame as open, plain wall and empty space.",
        "refs": CAST,
        "caption": "No tens to open — so open a HUNDRED. 1 hundred becomes 10 tens: 4 hundreds, 10 tens, 0 ones.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 40, "y": 13, "text": "One hundred is ten tens. That shelf isn't empty any more!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "Sprigatito unties one of the ten bundles and ten loose berries scatter onto the bottom shelf; nine bundles remain.",
        "scene": "SPRIGATITO pulls the ribbon off ONE of the bundles on the middle shelf, and TEN loose "
                 "berries tumble down onto the bottom wooden shelf, which was bare. On the middle shelf NINE "
                 "bundles clearly remain, with a visible gap where the opened one was. QUAXLY watches from "
                 "the lower-right holding the order slip. A soft glow follows the falling berries. Keep the "
                 "entire upper third of the frame as open, plain wall and empty space.",
        "refs": CAST,
        "caption": "Now open a TEN. 1 ten becomes 10 ones: 4 hundreds, 9 tens, 10 ones.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 34, "y": 13, "text": "Two trades — and now every shelf has something!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "The order leaves on a cart; what stays on the shelves is two crates, six bundles and four loose berries.",
        "scene": "A small wooden cart loaded with berries rolls out through the storehouse door at the "
                 "right. What remains behind is clearly arranged in three groups: TWO sealed crates, SIX "
                 "banded bundles on the middle shelf, and FOUR loose berries on the bottom shelf. SPRIGATITO "
                 "and QUAXLY stand together at the lower-left, pleased. Keep the entire upper third of the "
                 "frame as open, plain wall and empty space.",
        "refs": CAST,
        "caption": "ONES: 10 - 6 = 4    TENS: 9 - 3 = 6    HUNDREDS: 4 - 2 = 2       500 - 236 = 264",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 30, "y": 13, "text": "264 left. Perfect!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco sums up the rule while Sprigatito and Quaxly nod.",
        "scene": "FUECOCO sits warm and wise in the storehouse as if sharing a rule, flame tail raised "
                 "gently. SPRIGATITO and QUAXLY sit side by side nodding, both looking like something has "
                 "clicked. Golden light.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 44, "y": 12, "text": "An empty shelf can't lend you anything. Walk to the first one that isn't empty."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Evening in the tidy storehouse: two crates, six bundles and four loose berries each in their place, the three friends resting.",
        "scene": "Evening in the tidy berry storehouse, warm lantern light. The stock sits neatly in its "
                 "places: TWO crates against the wall, SIX bundles in a row on the middle shelf, FOUR loose "
                 "berries on the bottom shelf. SPRIGATITO, FUECOCO and QUAXLY rest together on the floor, "
                 "content and sleepy after a good day's work. Cozy finale.",
        "refs": CAST,
        "caption": "★ ACROSS ZEROS ★   If the next place is 0, you can't borrow from it. Go to the next place that isn't 0, open THAT, and work your way back down. Hundred → ten → one.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 28, "y": 16, "text": "Keep walking till a shelf isn't empty… To be continued →"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch3 L3 'The Empty Shelf' subtracting-across-zeros manga."

    CHAPTER = 3
    LESSON_NUMBER = 3
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_sub_regroup_2"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
