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
                 "drying rack rests on trestles across the lower half of the frame, turned so its flat top "
                 "surface is clearly visible and only mildly foreshortened — the rack is wider than it is tall "
                 "and its rows stay parallel and easy to read rather than racing to a vanishing point. On the "
                 "rack sit EXACTLY 42 small red berries in one perfect rectangular grid: 7 ACROSS and 6 DOWN "
                 "(7 columns, 6 rows). Every row contains exactly seven berries and every column exactly six, "
                 "evenly spaced with generous bare wood between them so each berry is easy to see and count. "
                 "There are no other berries anywhere on the rack. The tidy blue-headed duckling QUAXLY stands "
                 "at the left end of the rack inspecting it; the grass kitten SPRIGATITO perches on a wooden "
                 "crate at the far left; the red crocodile FUECOCO, the tiny electric mouse PAWMI and the "
                 "plump piglet LECHONK gather along the right-hand front edge of the rack. All five characters "
                 "are staged in the lower two-thirds, and every ear tip and head crest stays below the middle "
                 "of the frame. Low berry trees and stacked crates behind them. Warm golden morning light, "
                 "cheerful, calm. No writing, numerals, letters or signs anywhere in the picture. Keep the "
                 "entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "The big drying rack holds 6 rows of 7 berries.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 50, "y": 13, "text": "Six rows of seven. Nobody count them one at a time."},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi counts berries one by one in a panic while Fuecoco gently lowers a claw to stop it.",
        "scene": "Outdoors in the sunny orchard drying yard, right beside the long wooden drying rack, warm "
                 "morning light with orchard trees kept low and soft in the background. PAWMI the tiny "
                 "electric mouse leans over the near edge of the wooden drying rack in the LOWER HALF of the "
                 "frame and pokes at the small red berries one at a time with a paw, eyes spinning in dizzy "
                 "spirals, tiny sparks popping off its cheeks in panic. FUECOCO the calm red crocodile "
                 "crouches low beside it on the right and lowers one broad claw gently in front of PAWMI's paw "
                 "to stop it — patient and kind, not cross. Both characters are drawn small and staged "
                 "entirely in the lower two-thirds of the frame: the very top of PAWMI's ears and the very top "
                 "of FUECOCO's yellow head-crest must both sit clearly BELOW the halfway line of the frame, "
                 "with nothing of either character rising into the upper region. Comic, warm, affectionate. No "
                 "writing, numerals, letters or signs anywhere in the picture. Keep the entire upper third of "
                 "the frame as open, empty sky.",
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
        "scene": "The same long wooden drying rack as the previous panel — the same flat slatted rack, the "
                 "same dark red berries — seen from the same high angle tilted forward so the whole surface "
                 "reads flat and clear like a diagram, the rack filling the lower two-thirds of the frame with "
                 "open orchard beyond. A thin pale wooden slat lies straight ACROSS the rack, running "
                 "horizontally from the left edge to the right edge, exactly as in the previous panel. On the "
                 "FAR side of the slat is a block of EXACTLY 35 berries arranged 7 ACROSS and 5 DOWN (7 "
                 "columns, 5 rows): every row holds exactly seven berries and every column exactly five. That "
                 "whole block GLOWS warm and golden, and inside it the berries are softly bundled DOWN THE "
                 "COLUMNS — exactly seven slim vertical bundles, five berries in each, every column faintly "
                 "outlined like its own little stack. On the NEAR side of the slat, lying parallel to it, is "
                 "ONE single separate row of EXACTLY 7 berries, drawn dim and plain and grey, clearly still "
                 "waiting; all seven of those berries are fully visible and none is hidden behind a character, "
                 "a beam or the frame edge. The tiny electric mouse PAWMI hops merrily from column to column "
                 "along the near edge of the glowing block, sparks of delight trailing behind, staged in the "
                 "lower-left. The duckling QUAXLY watches from the lower-right corner, standing clear of the "
                 "berries with its head kept below the middle of the frame. Bright, clean, diagram-like "
                 "daylight. No writing, numerals, letters or signs anywhere in the picture. Keep the entire "
                 "upper third of the frame as open, empty sky.",
        "refs": ["pawmi", "quaxly"],
        "caption": "5 × 7 = 35 — five rows of seven. Look down the columns and it is seven fives: 5, 10, 15, 20, 25, 30, 35.     The part we already knew is done — one row is still waiting.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 38, "y": 13, "text": "Seven fives! I can do fives all day!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito slides the leftover row of berries back against the big block, closing the gap in the rack.",
        "scene": "SPRIGATITO the grass kitten stands at the lower-left and carries a single thin wooden slat "
                 "holding EXACTLY 7 small red berries in one straight line, sliding it back up against the "
                 "near edge of the big block of berries so the gap closes and the rack is whole again. The "
                 "drying rack is one single FLAT wooden surface — not stepped, not tiered, no raised ledges — "
                 "seen slightly from above and turned so its rows read clearly, wider than it is tall, sitting "
                 "in the lower two-thirds of the frame. The block already on the rack is EXACTLY 35 berries "
                 "arranged 7 ACROSS and 5 DOWN (7 columns, 5 rows): every one of the five rows holds exactly "
                 "seven berries, every column holds exactly five, all five rows are the same length and all of "
                 "them begin at the same left edge so the block is a clean rectangle. The 7-berry slat comes "
                 "in flush and parallel with those rows, lining up as a sixth row of the same length. The "
                 "duckling QUAXLY stands at the lower-right beside the rack looking pleased and precise. Both "
                 "SPRIGATITO's ear tips and QUAXLY's head must stay below the middle of the frame. Warm "
                 "daylight, satisfying and tidy. No writing, numerals, letters or signs anywhere in the "
                 "picture. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["sprigatito", "quaxly"],
        "caption": "One more ROW is 7 more berries, not 1 more:  35 + 7 = 42.     So 6 × 7 = 42.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 44, "y": 12, "text": "Forty-two berries — from a fact we already knew."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "A small tray of two rows of eight berries with an identical twin tray sliding against it to make four rows of eight.",
        "scene": "Two small drying trays seen from a high angle, tilted forward so both tray surfaces read "
                 "completely flat and clear like a diagram, sitting in the lower two-thirds of the frame with "
                 "the open orchard low beyond. Each tray is a wide shallow rectangle, WIDER THAN IT IS TALL. "
                 "The FAR tray holds EXACTLY 16 berries arranged 8 ACROSS and 2 DOWN (8 columns, 2 rows) — "
                 "exactly eight berries in each of its two rows. An IDENTICAL second tray, matching it berry "
                 "for berry, has slid in from the near side and locked flush against the far tray's near edge "
                 "along one straight shared seam; that near tray also holds EXACTLY 16 berries arranged 8 "
                 "ACROSS and 2 DOWN. The two trays are the same size and shape, their left edges are perfectly "
                 "aligned and their eight columns line up with each other, and neither tray overlaps or hides "
                 "any part of the other, so the pair together reads as one clean rectangle of 8 ACROSS and 4 "
                 "DOWN — exactly 32 berries in four equal rows of eight, every berry fully visible. A soft "
                 "mirrored glow links the two matching trays to show they are the same. The red crocodile "
                 "FUECOCO nudges the near tray into place from the lower-right; the tiny electric mouse PAWMI "
                 "bounces at the lower-left, sparking with surprise. Both characters are drawn small and low: "
                 "the top of PAWMI's ears and the top of FUECOCO's yellow head-crest must sit clearly BELOW "
                 "the halfway line of the frame. Clean, bright, diagram-like daylight. No writing, numerals, "
                 "letters or signs anywhere in the picture. Keep the entire upper third of the frame as open, "
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
