"""Build the Ch4 L2 "Strategies for Finding the Product" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l2_product_strategies --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l2_product_strategies --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l2_product_strategies --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l2_product_strategies --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l2-product-strategies"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "Early morning in the orchard drying yard: all five friends stand around a long rack of berries laid out in neat rows.",
        "scene": "Wide establishing shot of a sunny orchard drying yard just after dawn. A long low wooden "
                 "drying rack rests on trestles in the lower half of the frame, holding small red berries laid "
                 "out in six neat straight rows of seven, evenly spaced. The tidy blue-headed duckling QUAXLY "
                 "stands at one end of the rack inspecting it; the grass kitten SPRIGATITO perches on a crate "
                 "beside it; the red crocodile FUECOCO, the tiny electric mouse PAWMI and the plump piglet "
                 "LECHONK gather along the front of the rack. Berry trees and stacked crates behind. Warm "
                 "golden morning light, cheerful, calm. Keep the entire upper third of the frame as open, "
                 "empty sky.",
        "refs": CAST,
        "caption": "The big drying rack holds 6 rows of 7 berries.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 50, "y": 13, "text": "Six rows of seven. Nobody count them one at a time."},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi counts berries one by one in a panic while Fuecoco gently lowers a claw to stop it.",
        "scene": "PAWMI the tiny electric mouse leans over the edge of the drying rack and pokes at the "
                 "berries one at a time with a paw, eyes spinning, tiny sparks popping off its cheeks in "
                 "panic. FUECOCO the calm red crocodile lowers one broad claw gently in front of PAWMI's paw "
                 "to stop it, patient and kind, not cross. Both staged low in the frame. Comic, warm, "
                 "close-in. Keep the upper part of the frame open and plain.",
        "refs": ["pawmi", "fuecoco"],
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 12, "text": "One, two, three, four— wait, where was I? Aaah!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 68, "y": 19, "text": "Slow down. You already KNOW a fact that's close."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_FULL,
        "alt": "The berry rack seen from a high angle with a wooden slat laid across it, splitting it into a block of five rows and one separate row.",
        "scene": "The long drying rack seen from a high angle, tilted forward so the whole surface of the rack "
                 "reads flat and clear like a diagram while the open orchard beyond it is still visible. The "
                 "rack fills the lower two-thirds of the frame. A thin pale wooden slat has been laid straight "
                 "across it, cutting the berries into a big solid block of five rows of seven berries on the "
                 "far side of the slat and one single separate row of seven berries on the near side. The gap "
                 "the slat makes is clear and obvious. The grass kitten SPRIGATITO stands at the lower-left "
                 "edge of the rack with one paw resting on the end of the slat; the red crocodile FUECOCO "
                 "watches from the lower-right. Clean, simple, bright daylight. Keep the entire upper third of "
                 "the frame as open, empty sky.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "6 rows of 7  =  5 rows of 7  +  1 row of 7.     Lay a slat across it — two easy racks instead of one hard one.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 40, "y": 13, "text": "Split it where the easy fact lives — I know my fives!"},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "The five-row block of berries glows warmly, its berries softly bundled down the columns into seven little stacks of five, while the leftover row sits dim.",
        "scene": "The same drying rack from the same high tilted-forward angle, rack in the lower two-thirds, "
                 "open orchard sky above. The big block of five rows of seven berries GLOWS warm and golden, "
                 "and inside that glowing block the berries are softly bundled DOWN THE COLUMNS — seven slim "
                 "columns, five berries in each, every column faintly outlined like a little stack. The single "
                 "leftover row beyond the slat sits dim and plain, clearly still waiting. The tiny electric "
                 "mouse PAWMI hops merrily from column to column along the near edge of the block, sparks of "
                 "delight trailing behind; the duckling QUAXLY watches from the lower-right corner. Bright, "
                 "clean, diagram-like. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["pawmi", "quaxly"],
        "caption": "5 × 7 = 35 — five rows of seven. Look down the columns and it is seven fives: 5, 10, 15, 20, 25, 30, 35.     The part we already knew is done — one row is still waiting.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 38, "y": 13, "text": "Seven fives! I can do fives all day!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito slides the leftover row of berries back against the big block, closing the gap in the rack.",
        "scene": "SPRIGATITO the grass kitten carries the single leftover row of seven berries on a small slat "
                 "and slides it back up against the big block of berries, closing the gap so the rack is whole "
                 "again. The duckling QUAXLY stands beside the rack looking pleased and precise. Staged low in "
                 "the frame, warm daylight, satisfying and tidy. Keep the upper part of the frame open and "
                 "plain.",
        "refs": ["sprigatito", "quaxly"],
        "caption": "One more ROW is 7 more berries, not 1 more:  35 + 7 = 42.     So 6 × 7 = 42.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 44, "y": 12, "text": "Forty-two berries — from a fact we already knew."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "A small tray of two rows of eight berries with an identical twin tray sliding against it to make four rows of eight.",
        "scene": "A smaller square drying tray seen from a high angle, tilted forward so its surface reads "
                 "flat and clear, sitting in the lower two-thirds of the frame with the open orchard beyond. "
                 "The tray holds two neat rows of eight berries. An IDENTICAL second tray, matching berry for "
                 "berry, slides in from the near side and locks against it, so the two trays together now show "
                 "four rows of eight berries. A soft mirrored glow links the two matching trays to show they "
                 "are the same. The red crocodile FUECOCO nudges the second tray into place at the "
                 "lower-right; the tiny electric mouse PAWMI bounces at the lower-left, sparking with "
                 "surprise. Clean, bright, diagram-like. Keep the entire upper third of the frame as open, "
                 "empty sky.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "DOUBLE IT — 4 × 8 is double 2 × 8.     2 × 8 = 16, and 16 + 16 = 32.     So 4 × 8 = 32.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 30, "y": 13, "text": "Twice the rows, twice the berries."},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 19, "text": "Double it? That's the WHOLE trick?"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Lechonk lies flat in the shade raising one trotter lazily while Sprigatito leans in to hear the verdict.",
        "scene": "The plump piglet LECHONK lies flat on its side in the cool shade under the drying rack, "
                 "utterly unbothered, raising a single trotter as if delivering a verdict without moving "
                 "anything else. The grass kitten SPRIGATITO leans down toward it, ears forward, waiting for "
                 "the answer. Dappled shade, funny, relaxed, conclusive. Staged low in the frame with plain "
                 "open space above.",
        "refs": ["lechonk", "sprigatito"],
        "caption": "Check: 5 × 7 = 35 and 7 × 7 = 49. Six sevens has to land between them — and 42 does.",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 42, "y": 12, "text": "More than 35, less than 49. Forty-two fits just fine."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "All five friends carry crates of finished berries down through the orchard at sunset.",
        "scene": "Warm sunset over the orchard drying yard. All five friends — SPRIGATITO, FUECOCO, QUAXLY, "
                 "PAWMI and LECHONK — carry crates of finished berries down a path between the berry trees, "
                 "the empty racks behind them catching the last light. PAWMI's crate is overfull with berries "
                 "spilling over its arms; LECHONK is riding on top of a crate rather than carrying one. "
                 "Joyful, golden, end-of-lesson finale, everyone staged in the lower two-thirds. Keep the "
                 "entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "★ THE STRATEGY ★   Never count one at a time. Start from a fact you know: break a row off (6 × 7 = 5 × 7 + 7) or double a smaller fact (4 × 8 = double 2 × 8).",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 28, "y": 13, "text": "Every fact you know saves you a whole lot of counting."},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 19, "text": "Split it or double it!"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L2 'Strategies for Finding the Product' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 2
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l2_product_strategies"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
