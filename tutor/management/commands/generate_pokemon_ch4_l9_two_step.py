"""Build the Ch4 L9 "Two Steps in One Problem" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l9_two_step --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l9_two_step --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l9_two_step --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l9_two_step --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l9-two-step"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A hilltop berry orchard at golden hour with four baskets in a row under a heavy berry tree and all five friends picking.",
        "scene": "Wide establishing shot of a hilltop berry orchard at warm golden hour on the last picking "
                 "day of the season. Four woven baskets sit in a neat row on the grass in the lower half of "
                 "the frame, each holding six plump red berries; a heavy fruit tree leans over them. The "
                 "blue-headed duckling QUAXLY stands beside the baskets inspecting them; the grass kitten "
                 "SPRIGATITO is up on a low branch, the red crocodile FUECOCO steadies the ladder, the tiny "
                 "electric mouse PAWMI carries a berry twice its size, and the plump piglet LECHONK dozes "
                 "against a basket. Warm, busy, harvest-happy. No writing, signs or markings anywhere. Stage "
                 "everyone in the lower two-thirds and keep the upper third as calm open sky.",
        "refs": CAST,
        "caption": "Last picking day. Four baskets, six berries in each one.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 50, "y": 13, "text": "And nine got eaten at snack break. How many are LEFT?"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi panics, shoving berries back and forth between two little piles with sparks flying, while Fuecoco rests a calm claw on its shoulder.",
        "scene": "PAWMI the tiny electric mouse panics low in the frame, eyes spinning and sparks jumping off "
                 "its cheeks, frantically shoving loose berries back and forth between two little piles on the "
                 "grass and getting nowhere. FUECOCO the chunky red crocodile leans in from the right and "
                 "rests one calm claw on Pawmi's shoulder to slow it down, warm and patient, never cross. "
                 "Comic and kind. No paper, slate, writing or markings of any kind. Characters low in the "
                 "frame, upper third plain orchard sky.",
        "refs": ["pawmi", "fuecoco"],
        "caption": "Two things happened — berries picked, then berries eaten. Which step can you do FIRST?",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 12, "text": "Six take away nine— four take away nine— AAAH!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 68, "y": 19, "text": "Slow down. Draw it first."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco crouches and draws one long bar in the orchard dirt, cutting it into four equal sections while the others watch.",
        "scene": "FUECOCO the red crocodile crouches in the soft orchard dirt in the lower half of the frame "
                 "and draws ONE long straight horizontal bar with a single claw, then adds three short "
                 "vertical cuts so the bar is divided into FOUR equal sections, all exactly the same width. "
                 "Plain scratched lines only — no writing, numbers or labels. SPRIGATITO the grass kitten and "
                 "PAWMI the electric mouse lean in from either side to watch the line appear. Focused, "
                 "teacherly, warm afternoon light. Keep the upper third of the frame plain and empty.",
        "refs": ["fuecoco", "sprigatito", "pawmi"],
        "caption": "One bar, cut into four equal parts — one part for each basket.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 44, "y": 12, "text": "Four baskets, all the same size. Equal groups — so we can multiply."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "The bar in the dirt with four equal sections, each holding six berries in two rows of three, while Sprigatito hides a guilty handful of nibbled berries.",
        "scene": "The long bar drawn in the orchard dirt, divided into FOUR equal sections by plain scratched "
                 "lines. Each section holds six real red berries arranged in two tidy rows of three, so all "
                 "four sections look identical. Off to the right and lower down, SPRIGATITO the grass kitten "
                 "hides a small guilty handful of half-nibbled berries behind its back, ears flat, looking "
                 "away innocently; FUECOCO watches from the lower left. Clean, diagram-like, sunlit dirt, no "
                 "writing or labels anywhere. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "4 groups of 6 … then 9 eaten … then ? left. You can't take 9 away yet — there is no whole pile yet.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 34, "y": 13, "text": "The eating comes SECOND! You can't take from a pile you haven't picked."},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "All the berries sweep out of the four sections and gather into one single heap inside one long undivided bar.",
        "scene": "The same bar drawn in the dirt, but now the dividing marks are fading away and all the "
                 "berries from the four sections sweep together with soft motion trails into ONE single "
                 "generous heap sitting inside one long undivided bar. A gentle glow marks the merge. PAWMI "
                 "the electric mouse bounces at the lower left with happy sparks; QUAXLY the duckling watches "
                 "approvingly at the lower right. No writing, numbers or labels anywhere. Keep the entire "
                 "upper third of the frame as open, empty sky.",
        "refs": ["pawmi", "quaxly"],
        "caption": "STEP 1 — do the step you CAN do:  4 × 6 = 24 berries picked   (6, 12, 18, 24)",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 13, "text": "Six, twelve, eighteen, twenty-four! Four sixes!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "A small cluster of berries rolls away out of the big heap toward Sprigatito's nibbled pile, leaving the rest glowing in the bar.",
        "scene": "The same long bar with the single heap of berries, but now a small cluster of nine berries "
                 "ROLLS AWAY out of the heap with motion trails, off to the right toward SPRIGATITO's little "
                 "pile of nibbled stems; SPRIGATITO looks sheepish at the lower right. The berries still "
                 "inside the bar glow softly, clearly the part that remains. QUAXLY the duckling points at the "
                 "glowing remainder from the lower left, delighted. No writing, numbers or labels anywhere. "
                 "Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["quaxly", "sprigatito"],
        "caption": "STEP 2 — use the number you just made:  24 - 9 = 15 berries left",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 32, "y": 13, "text": "Fifteen berries left. THAT'S the question they asked."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi throws both paws up and shouts an answer too early while Quaxly points back at the bar in the dirt and Fuecoco smiles.",
        "scene": "PAWMI the electric mouse throws both paws in the air in triumph, standing on an upturned "
                 "basket in the lower half of the frame, absolutely certain and far too early. QUAXLY the "
                 "duckling stands beside it and patiently points one wingtip back down at the bar drawn in the "
                 "dirt, where a small cluster of berries has rolled away from the heap. FUECOCO the crocodile "
                 "watches from behind with a warm, amused, entirely un-scolding smile. Comic, gentle, no paper "
                 "or writing of any kind. Keep the upper third plain and empty.",
        "refs": ["pawmi", "quaxly", "fuecoco"],
        "caption": "Careful — 24 is the MIDDLE step, not the answer. The question asked how many are LEFT:  15.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 30, "y": 12, "text": "Twenty-four! I'm done!"},
            {"speaker": "Quaxly", "kind": "speech", "x": 62, "y": 19, "text": "That's the picking, not the leftovers. Read it again."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "All five friends share a sunset supper on the orchard hill with the last berries and stacked baskets, the harvest finished.",
        "scene": "Warm sunset supper on the orchard hill. All five — SPRIGATITO, FUECOCO, QUAXLY, PAWMI and "
                 "LECHONK — sit around a plain checked cloth spread on the grass in the lower two-thirds, "
                 "sharing the last handful of berries; empty baskets are stacked neatly behind them and the "
                 "picking ladder rests against the tree. LECHONK lies flat and content with a berry balanced "
                 "on its snout, PAWMI is berry-stained to the ears. Joyful, golden, end-of-chapter finale, no "
                 "banners, writing or lettering anywhere. Keep the entire upper third of the frame as open, "
                 "empty sky.",
        "refs": CAST,
        "caption": "★ TWO-STEP RULE ★   Draw it first. Do the step you CAN do, then use that number to answer the real question. Multiply then subtract: 4 × 6 = 24, then 24 - 9 = 15. Or multiply then divide: 3 × 8 = 24, then 24 ÷ 4 = 6 in each basket.   ★ END OF CHAPTER 4 ★",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 30, "y": 12, "text": "About 25 picked, about 10 eaten — about 15 left. Believable."},
            {"speaker": "Fuecoco", "kind": "speech", "x": 64, "y": 19, "text": "Do the step you can, then use it."},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L9 'Two Steps in One Problem' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 9
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l9_two_step"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
