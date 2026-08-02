"""Build the Ch3 L4 "Pawmi's Good Guess" estimating-sums manga.

New cast (Pawmi and Lechonk), so a full run draws two character sheets into this
lesson's dir; L5 reuses them via SHEET_DIRS and draws none.

Examples:
    python manage.py generate_pokemon_estimating_1 --dry-run --curriculum 1
    python manage.py generate_pokemon_estimating_1 --curriculum 1              # real art
    python manage.py generate_pokemon_estimating_1 --only 6,7 --curriculum 1   # redraw the catch
    python manage.py generate_pokemon_estimating_1 --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-estimating-1"
CHARACTERS = gen9("pawmi", "lechonk")
CAST = ["pawmi", "lechonk"]

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A busy festival prize table with two enormous jars of candy; a small electric mouse and a plump piglet gaze up at them.",
        "scene": "Wide establishing shot of a bustling outdoor festival in sunny Paldea — stalls, bunting, "
                 "paper lanterns strung overhead. On a prize table stand TWO enormous glass jars packed with "
                 "colourful round candies. The tiny orange-tan electric mouse PAWMI and the plump grey-brown "
                 "piglet LECHONK gaze up at the jars, tiny beside them. Festive, warm, crowded.",
        "refs": CAST,
        "caption": "FESTIVAL DAY! Guess the candy, win the candy.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 50, "y": 13, "text": "One jar has 296… the other has 405!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi scribbles frantically on a little slate, sparks flying, while Lechonk chews calmly.",
        "scene": "The little electric mouse PAWMI scribbles frantically on a small chalk slate, tiny sparks "
                 "crackling from its cheek-pouches, tail whipping, eyes crossed with effort. Beside it "
                 "LECHONK the piglet chews something placidly, completely unbothered. Comic contrast.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 13, "text": "296 plus 405… carry the… um…"},
            {"speaker": "Lechonk", "kind": "speech", "x": 74, "y": 20, "text": "Just get CLOSE."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Lechonk points a trotter at the first jar, calm and matter-of-fact.",
        "scene": "LECHONK the piglet lifts one trotter to point at the nearer candy jar, calm and "
                 "matter-of-fact, as if stating something obvious. PAWMI looks up from its slate, ears "
                 "perked, listening.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 44, "y": 12, "text": "296 is nearly 300 — round UP. 405 is just past 400 — round DOWN."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "The two crowded jars shimmer into two clean simple jars, one filled with three big scoops, the other with four.",
        "scene": "A magical shimmer transforms the scene: the two crowded candy jars become TWO clean, simple, "
                 "tidy jars — the left holding THREE big neat scoop-loads of candy stacked clearly, the right "
                 "holding FOUR. Everything is simplified and easy to count at a glance, glowing softly. PAWMI "
                 "stares in wonder at the lower-left, LECHONK sits placidly at the lower-right. Keep the "
                 "entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "Round each number to the nearest hundred.   296 → 300     405 → 400",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 13, "text": "Ohhh — those are easy numbers!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "Pawmi zaps happily as the two simple jars slide together into one big jar.",
        "scene": "The two simple jars slide together into ONE big jar of candy. PAWMI the electric mouse "
                 "leaps with delight, small friendly sparks of yellow electricity arcing around it in "
                 "celebration. LECHONK looks on, mildly pleased, at the lower-right. Bright and joyful. Keep "
                 "the entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "300 + 400 = 700.   About seven hundred candies altogether.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 13, "text": "About 700! I didn't even need my slate!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "A festival worker holds up a result card; Pawmi's ears shoot up in alarm, sensing something wrong.",
        "scene": "A cheerful festival stall worker holds up a large blank result card above the prize table. "
                 "PAWMI the electric mouse reacts with sudden alarm at the lower-left — ears bolt upright, "
                 "fur bristling, sparks snapping — clearly certain something is wrong. LECHONK raises an "
                 "eyebrow at the lower-right. Keep the entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "The sign says 1,101 — but the estimate says about 700. That's way too big!",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 13, "text": "That can't be right! We know it's about 700!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "The worker rechecks and flips the card over; Pawmi and Lechonk cheer.",
        "scene": "The festival worker turns the result card over with a sheepish grin, correcting it. PAWMI "
                 "cheers with both paws in the air, thrilled to have been right; LECHONK gives a small "
                 "satisfied nod. Warm, funny, vindicated.",
        "refs": CAST,
        "caption": "The real answer: 296 + 405 = 701",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 44, "y": 12, "text": "701 is right next to 700. THAT one's believable."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Pawmi and Lechonk share an enormous prize jar of candy under glowing festival lanterns.",
        "scene": "Evening at the festival, paper lanterns glowing warmly overhead. PAWMI the electric mouse "
                 "and LECHONK the piglet sit together sharing an ENORMOUS prize jar of colourful candy, both "
                 "delighted and a little sleepy. Cozy, celebratory finale.",
        "refs": CAST,
        "caption": "★ ESTIMATING RULE ★   Round each number to the nearest hundred, then add. The estimate isn't meant to be exact — its job is to tell you whether your exact answer is BELIEVABLE.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 28, "y": 16, "text": "Round first, check after! To be continued →"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch3 L4 'Pawmi's Good Guess' estimating-sums manga."

    CHAPTER = 3
    LESSON_NUMBER = 4
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_estimating_1"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
