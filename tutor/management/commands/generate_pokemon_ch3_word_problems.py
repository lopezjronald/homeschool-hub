"""Build the Ch3 L6 "The Sticker Stand" two-step word problems manga.

All five characters return from Lessons 1-5, so every sheet is reused and a full
run draws only the eight panels.

Panels 4-6 are a bar model told as three beats: the bar drawn and cut, the two
known parts merging, the merged block lifting away. They have to read as one
continuous diagram changing — the same bar, three moments — or the two-step
structure the lesson is about doesn't come across.

Examples:
    python manage.py generate_pokemon_ch3_word_problems --dry-run --curriculum 1
    python manage.py generate_pokemon_ch3_word_problems --curriculum 1              # real art
    python manage.py generate_pokemon_ch3_word_problems --only 4,5,6 --curriculum 1 # redraw the bar model
    python manage.py generate_pokemon_ch3_word_problems --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch3-word-problems"
CHARACTERS = gen9("sprigatito", "fuecoco", "quaxly", "pawmi", "lechonk")
CAST = ["sprigatito", "fuecoco", "quaxly", "pawmi", "lechonk"]

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A cheerful sticker stand at the market with all five friends crowded around it.",
        "scene": "Wide establishing shot of a bright, cheerful sticker stall at a sunny Paldea market — "
                 "sheets of colourful stickers pinned up behind a wooden counter, bunting overhead. The "
                 "blue-headed duckling QUAXLY stands behind the counter; the grass kitten SPRIGATITO, the "
                 "red crocodile FUECOCO, the tiny electric mouse PAWMI and the plump piglet LECHONK crowd "
                 "around the front. Busy, happy, colourful.",
        "refs": CAST,
        "caption": "The sticker stand opened this morning with 450 stickers.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 52, "y": 13, "text": "We sold 175 before lunch, and 138 after!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi scribbles frantically with sparks flying; Fuecoco gently lowers a claw to slow it down.",
        "scene": "PAWMI the electric mouse scribbles frantically on its little chalk slate, sparks flying, "
                 "eyes spinning with panic. FUECOCO the red crocodile gently lowers one claw onto the slate "
                 "to slow it down, calm and kind. Comic, warm.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 13, "text": "450 minus 175 minus— wait— aaah!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 74, "y": 20, "text": "Draw it FIRST."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco draws one long straight bar in the dust with a claw while the others watch.",
        "scene": "FUECOCO the red crocodile crouches and draws ONE long straight horizontal bar in the dusty "
                 "ground with a single claw, like a simple diagram. SPRIGATITO and PAWMI lean in to watch the "
                 "line appear. Focused, teacherly, warm.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 44, "y": 12, "text": "One long bar — that's ALL 450 stickers. Now cut it into the parts we know."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "The long bar in the dust, now divided into three sections — two solid, one left blank.",
        "scene": "The long horizontal bar drawn in the dust is now divided by two vertical marks into THREE "
                 "clear sections: the left two sections are firmly filled in and solid, the rightmost "
                 "section is left conspicuously BLANK and empty. SPRIGATITO points at the empty section at "
                 "the lower-left; FUECOCO watches at the lower-right. Simple, clean, diagram-like. Keep the "
                 "entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "450 total  =  175 sold  +  138 sold  +  ? left.     Two parts we know, one we don't — that's TWO steps.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 34, "y": 13, "text": "We can't take the leftover away — we don't know it yet!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "The two filled sections of the bar slide together into a single combined block.",
        "scene": "The two filled-in sections of the dust bar slide together and merge into ONE single "
                 "combined solid block, the dividing mark between them vanishing, while the blank section "
                 "stays separate at the right. A soft glow marks the merge. PAWMI cheers at the lower-left "
                 "with small sparks; QUAXLY watches at the lower-right. Keep the entire upper third of the "
                 "frame as open, empty sky.",
        "refs": CAST,
        "caption": "STEP 1 — add what we SOLD:  175 + 138 = 313   (5 + 8 = 13 — bundle ten, carry one!)",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 13, "text": "Thirteen ones — bundle ten, carry one! I remember!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "The combined block lifts up and away from the long bar, leaving only the previously blank section behind.",
        "scene": "The single combined solid block LIFTS UP and away from the long dust bar, floating clear of "
                 "it, leaving behind only the section that was blank — which now sits alone and highlighted "
                 "with a soft glow. QUAXLY points at the remaining piece at the lower-right, delighted; "
                 "SPRIGATITO beams at the lower-left. Keep the entire upper third of the frame as open, "
                 "empty sky.",
        "refs": CAST,
        "caption": "STEP 2 — take the sold ones off the whole:  450 - 313 = 137   (0 - 3 won't go — open a ten!)",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 32, "y": 13, "text": "137 stickers left!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Lechonk checks the answer with a lazy estimate while the others look on.",
        "scene": "LECHONK the piglet, utterly unbothered and half-reclining, raises one trotter as if doing a "
                 "quick sum in its head. PAWMI and SPRIGATITO look over at it expectantly. Relaxed, funny, "
                 "conclusive.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 44, "y": 12, "text": "About 450 take about 300 — about 150. So 137? Believable."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "All five friends at the sticker stand at sunset, sharing out the last of the stickers.",
        "scene": "Warm sunset over the market. All five — SPRIGATITO, FUECOCO, QUAXLY, PAWMI and LECHONK — "
                 "gather at the sticker stand sharing out the last colourful stickers, several stuck "
                 "comically to PAWMI's fur. Joyful, warm, end-of-chapter finale.",
        "refs": CAST,
        "caption": "★ TWO-STEP RULE ★   Draw the bar first. Find the part you CAN work out, do that step, then use it to get the answer — and estimate to check it's believable.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 28, "y": 16, "text": "Draw, step, step, check!  ★ END OF CHAPTER 3 ★"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch3 L6 'The Sticker Stand' two-step word problems manga."

    CHAPTER = 3
    LESSON_NUMBER = 6
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch3_word_problems"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
