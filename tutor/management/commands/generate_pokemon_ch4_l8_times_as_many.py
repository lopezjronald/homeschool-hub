"""Build the Ch4 L8 "Times as Many" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l8_times_as_many --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l8_times_as_many --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l8_times_as_many --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l8_times_as_many --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l8-times-as-many"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "The orchard packing yard: a long low sorting bench where Fuecoco sets down one small basket of four berries while Quaxly wheels up a barrow of three matching baskets.",
        "scene": "Wide establishing shot of a sunny orchard packing yard, rows of berry trees behind and open "
                 "pale sky above. A long low wooden sorting bench runs across the LOWER half of the frame with "
                 "a faint chalk line ruled along it. FUECOCO the red crocodile sets down ONE small woven "
                 "basket holding exactly FOUR big round red berries at the left end of the bench. QUAXLY the "
                 "blue-headed duckling wheels up a little barrow carrying THREE identical woven baskets, each "
                 "holding FOUR of the same big round red berries. SPRIGATITO, PAWMI and LECHONK crowd at the "
                 "front of the bench, curious. Bright, warm, busy harvest morning. Keep the upper third of the "
                 "frame calm and empty.",
        "refs": CAST,
        "caption": "Fuecoco picked 4 berries this morning. Quaxly picked 3 TIMES as many.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 48, "y": 13, "text": "Three times as many as yours, Fuecoco! So how many is that?"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi blurts out an answer with sparks flying while Fuecoco tips its head kindly.",
        "scene": "PAWMI the tiny electric mouse bounces on the low bench in the bottom half of the frame, one "
                 "paw thrown up in triumph, small sparks popping from its cheeks, utterly certain of itself. "
                 "FUECOCO the red crocodile sits beside it and tips its head gently, patient and amused, not "
                 "scolding. A plain sunlit shed wall fills the calm, empty upper third.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "Careful — \"3 times as many\" is NOT \"3 more.\"  4 + 3 = 7 answers a different question.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 13, "text": "Easy! Four and three more — that's seven!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 68, "y": 19, "text": "Different question. Times means COPIES, not more."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco slides its single basket of four berries flush against the chalk mark at the left end of the bench.",
        "scene": "Close, low view along the wooden sorting bench. FUECOCO the red crocodile slides its ONE "
                 "small woven basket — FOUR big round red berries inside, easy to count — so that it sits "
                 "flush against the chalk mark at the left end of the bench, pressing it neatly into place "
                 "with one claw. SPRIGATITO the grass kitten crouches at the bench edge watching the basket "
                 "line up. The bench and characters sit in the lower two-thirds; plain open sky above, calm "
                 "and empty.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "Fuecoco's whole pick is ONE unit: 4 berries. That's the short bar.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 46, "y": 12, "text": "One basket. That's ONE unit — my whole morning's pick."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Two rows on the bench: one basket of four berries on the upper line, and directly beneath it three identical baskets of four starting from the same left edge.",
        "scene": "Very wide, clean, diagram-like view of the sorting bench outdoors. TWO chalk lines are ruled "
                 "horizontally across the lower half, one just above the other, and both begin at the same "
                 "vertical chalk mark at the left. On the upper line sits ONE small woven basket holding FOUR "
                 "big round red berries. On the lower line, starting at exactly that same left mark and "
                 "running to the right, sit THREE identical woven baskets in a straight unbroken row, each the "
                 "same size and each holding FOUR of the same berries, evenly spaced with no gaps. SPRIGATITO "
                 "the grass kitten stands at the lower left pointing along the left-hand chalk mark where both "
                 "rows begin; QUAXLY the blue-headed duckling watches from the lower right. Simple, tidy, "
                 "obviously deliberate. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["sprigatito", "quaxly"],
        "caption": "Same left edge, same size units. Quaxly's bar is 3 copies of Fuecoco's bar — now the comparison is something you can SEE.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 38, "y": 13, "text": "Line the left ends up! Now you can SEE how much longer Quaxly's is."},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "The long lower row counted out as three separate glowing baskets of four berries each, with the single short basket still above.",
        "scene": "The same two-row bench layout, very wide. On the lower row each of the THREE baskets is lit "
                 "by its own soft warm glow, one after another from left to right, the FOUR round red berries "
                 "in each one clearly countable. The single basket of FOUR still sits on the upper row "
                 "directly above the leftmost one, both rows still starting at the same left chalk mark. "
                 "QUAXLY the blue-headed duckling stands at the lower right with a wing raised, poised and "
                 "pleased; PAWMI the tiny electric mouse peers over the bench edge at the lower left, counting "
                 "with one paw, sparks popping. Warm afternoon light. Keep the entire upper third of the frame "
                 "as open, empty sky.",
        "refs": ["quaxly", "pawmi"],
        "caption": "4 + 4 + 4 = 4 × 3 = 12.   Three copies of 4 — Quaxly picked 12 berries.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 44, "y": 12, "text": "Twelve! Three groups of four, all the same size."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "The long row tipped into one line of twelve berries cut by two chalk marks into three equal groups, with an empty basket one group long waiting above.",
        "scene": "The same wide bench, but now the lower row's berries are tipped out into ONE long straight "
                 "line of TWELVE round red berries, and TWO chalk cut-marks divide that line into three equal "
                 "groups of four. On the upper row, starting at the same left chalk mark and running exactly "
                 "as far as the FIRST group below it, sits a small woven basket that is completely EMPTY, "
                 "waiting to be filled. FUECOCO the red crocodile stands at the lower right drawing one of the "
                 "chalk cut-marks with a claw; SPRIGATITO the grass kitten watches from the lower left. Clean "
                 "and diagram-like. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["fuecoco", "sprigatito"],
        "caption": "Now run it backwards. Quaxly's 12 is 3 copies of Fuecoco's pick, so share the 12 into 3 equal parts: 12 ÷ 3 = 4.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 42, "y": 13, "text": "Same two bars. Share the long one into 3 equal parts."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Lechonk lies in the grass squinting sideways at the short row and the long row to check the answer looks right.",
        "scene": "LECHONK the plump piglet lies flat on its side in the orchard grass in the lower half of the "
                 "frame, one eye squinted, lazily sizing up the two rows of berries on the bench beside it — "
                 "one short, one much longer. PAWMI the tiny electric mouse sits nearby with ears up, waiting "
                 "for the verdict. Lazy, funny, conclusive. Soft empty sky across the top third.",
        "refs": ["lechonk", "pawmi"],
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 42, "y": 12, "text": "Three of Fuecoco's piles, easy. Seven wouldn't even make two! Nap time."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "All five friends load the short row and the long row of baskets onto a cart at sunset in the orchard.",
        "scene": "Warm golden sunset over the orchard. All five — SPRIGATITO, FUECOCO, QUAXLY, PAWMI and "
                 "LECHONK — load baskets of red berries onto a little wooden cart in the lower two-thirds of "
                 "the frame: one small basket lifted up on one side, a long row of three matching baskets on "
                 "the other. PAWMI is upside down inside an empty basket with only its tail sticking out. "
                 "Joyful, warm, end-of-lesson finale. Keep the entire upper third of the frame as open, empty "
                 "sky.",
        "refs": CAST,
        "caption": "★ TIMES AS MANY ★   Draw two bars from the SAME left edge — a short one for one unit, a long one for the copies. Know one unit? Multiply. Know the long bar? Divide.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 30, "y": 12, "text": "Two bars, one starting line."},
            {"speaker": "Pawmi", "kind": "speech", "x": 66, "y": 18, "text": "Times means copies!"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L8 'Times as Many' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 8
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l8_times_as_many"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
