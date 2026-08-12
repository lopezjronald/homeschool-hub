"""Build the Ch4 L7 "Word Problems with Bar Models" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l7_bar_model_word_problems --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l7_bar_model_word_problems --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l7_bar_model_word_problems --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l7_bar_model_word_problems --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l7-bar-model-word-problems"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "Dawn in a berry orchard: a wooden wagon on the path, six empty baskets in a neat row, and all five friends ready to pick.",
        "scene": "Wide establishing shot of a berry orchard at dawn, low golden light. A small wooden "
                 "hand-wagon waits on a dirt path in the lower half of the frame, and SIX empty round wicker "
                 "baskets sit in a neat row on the ground beside it. Berry bushes heavy with round red berries "
                 "line the lower background. The blue-headed duckling QUAXLY stands tall beside the wagon; the "
                 "grass kitten SPRIGATITO crouches by the baskets, the red crocodile FUECOCO stands calmly "
                 "behind them, the tiny electric mouse PAWMI bounces on its toes and the plump piglet LECHONK "
                 "dozes against a basket. No writing, numbers or symbols anywhere in the picture. Stage every "
                 "character and object in the lower two-thirds; keep the upper third open pale morning sky.",
        "refs": CAST,
        "caption": "Harvest morning. Six baskets to fill — and exactly five berries fit in each one.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 50, "y": 13, "text": "Six baskets. Five berries in each. How many berries is that?"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi frantically counts loose berries one at a time while Fuecoco calmly lowers a claw to stop it.",
        "scene": "PAWMI the tiny electric mouse sits low in the frame frantically counting a scattered spill "
                 "of loose round berries one at a time, tiny sparks jumping from its cheeks, eyes crossed with "
                 "confusion, berries rolling away behind it. FUECOCO the red crocodile leans in from the right "
                 "and gently lowers one claw onto the ground beside the berries, calm and kind, clearly saying "
                 "slow down. Comic and warm. No writing, numbers or symbols anywhere. Keep both characters and "
                 "the berries in the lower two-thirds; the upper third is plain soft-lit orchard air with "
                 "nothing in it.",
        "refs": ["pawmi", "fuecoco"],
        "caption": "Counting a pile one berry at a time works — right up until it doesn't.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 12, "text": "One, two, three— wait, did I count that one already?!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 70, "y": 19, "text": "Don't count the pile. Draw the bar — then label one unit."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_FULL,
        "alt": "Fuecoco draws a single rectangle in the orchard dirt and places exactly five berries inside it while Sprigatito leans in.",
        "scene": "FUECOCO the red crocodile crouches at the lower right and, with one claw, has drawn a single "
                 "clean rectangle in the smooth dirt of the orchard floor. Sitting neatly inside that one "
                 "rectangle are EXACTLY FIVE round red berries, evenly spaced in a tidy row. Nothing else is "
                 "drawn in the dirt — no writing, no numbers, no letters, no symbols anywhere in the picture. "
                 "SPRIGATITO the grass kitten leans in at the lower left, nose close to the drawing, "
                 "fascinated. Simple, clean, diagram-like, warm morning light. Keep the entire upper third of "
                 "the frame as open, empty sky.",
        "refs": ["fuecoco", "sprigatito"],
        "caption": "One unit stands for one basket. 1 unit = 5 berries. Say what one unit is worth before you compute anything.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 42, "y": 13, "text": "One unit is one basket. Five berries live inside it."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "The same rectangle repeated six times in a row makes one long bar, each of the six equal sections holding five berries.",
        "scene": "The drawing in the dirt has grown: that same rectangle is now repeated SIX times in a "
                 "straight horizontal row, edge to edge, forming ONE long bar of six identical equal sections. "
                 "Every single section holds exactly FIVE round red berries arranged the same tidy way, so the "
                 "repetition is obvious at a glance. A simple plain curved line is scratched in the dirt "
                 "beneath the whole bar, spanning it end to end. There is no writing, no numbers, no letters "
                 "and no symbols anywhere in the dirt or the picture. QUAXLY the blue-headed duckling stands "
                 "proudly at the lower right pointing a wing along the bar; FUECOCO the red crocodile crouches "
                 "at the lower centre smoothing the last section with a claw; SPRIGATITO bats happily at the "
                 "far end at the lower left. Clean, orderly, diagram-like. Keep the entire upper third of the "
                 "frame as open, empty sky.",
        "refs": ["quaxly", "sprigatito", "fuecoco"],
        "caption": "6 units of 5  →  6 × 5 = 30 berries.  (5, 10, 15, 20, 25, 30.)  Unit known, whole unknown — so multiply.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 34, "y": 13, "text": "Thirty berries! Six equal units, five in every one."},
            {"speaker": "Sprigatito", "kind": "speech", "x": 68, "y": 19, "text": "Same unit, six times over!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito pounces at a butterfly, knocks over the row of full baskets, and all the berries roll into one big heap.",
        "scene": "Chaos, comic and affectionate. SPRIGATITO the grass kitten is mid-pounce after a fluttering "
                 "butterfly and has clipped the row of full wicker baskets, which tumble sideways in the lower "
                 "left; a great wave of round red berries pours out of them and gathers into ONE single big "
                 "heap in the lower centre of the frame. QUAXLY the duckling throws its wings up in dismay at "
                 "the lower right; LECHONK the piglet lies unbothered beside the heap. Berries everywhere on "
                 "the ground, none in the air above the midline. No writing, numbers or symbols anywhere. Keep "
                 "the upper third clear open sky.",
        "refs": ["sprigatito", "quaxly", "lechonk"],
        "caption": "All 30 berries — back in one pile.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 13, "text": "Oops. Oops oops oops."},
            {"speaker": "Lechonk", "kind": "speech", "x": 66, "y": 19, "text": "One giant hill of berries."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "The same long bar of six equal sections, with berries flowing from the shrinking heap until every section holds five.",
        "scene": "The same long dirt-drawn bar of SIX identical equal sections stretches across the lower "
                 "middle of the frame. From a nearly emptied heap of round red berries at the left, a last few "
                 "berries stream in a gentle arc into the bar, and every one of the six sections now holds "
                 "exactly FIVE round red berries, laid out the same tidy way in each section. A soft glow "
                 "traces the flow. There is no writing, no numbers, no letters and no symbols anywhere in the "
                 "dirt or the picture. FUECOCO the red crocodile guides the flow with one claw at the lower "
                 "left; PAWMI the electric mouse bounces with delight at the lower right, sparks flying. Clean "
                 "and diagram-like. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "Whole known, unit unknown — so divide.  30 ÷ 6 = 5 berries in each basket.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 36, "y": 13, "text": "Now we know the whole and we hunt for the unit."},
            {"speaker": "Pawmi", "kind": "speech", "x": 70, "y": 19, "text": "Five each! Again!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Lechonk lies on its back checking the answer while Pawmi and Quaxly lean in and watch.",
        "scene": "LECHONK the plump piglet lies flat on its back in the orchard grass at the lower centre, "
                 "utterly relaxed, tapping the air with one trotter as if ticking off numbers in its head. "
                 "PAWMI the electric mouse and QUAXLY the duckling lean over it from the lower left and lower "
                 "right, waiting expectantly. Warm, funny, conclusive. No writing, numbers or symbols "
                 "anywhere. Keep all three low in the frame and the upper third empty sky.",
        "refs": ["lechonk", "pawmi", "quaxly"],
        "caption": "Check it backwards: 6 × 5 = 30. ✓",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 44, "y": 12, "text": "Five, ten, fifteen, twenty, twenty-five, thirty. Checks out."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunrise on the orchard road: six full baskets loaded on the wagon and all five friends waving it off.",
        "scene": "Warm sunrise over the orchard road. The little wooden wagon, now loaded with SIX full wicker "
                 "baskets heaped with round red berries, rolls away down the path in the lower right. All five "
                 "friends — SPRIGATITO, FUECOCO, QUAXLY, PAWMI and LECHONK — stand together in the lower left "
                 "waving it off, PAWMI comically berry-stained, LECHONK already sitting down. Joyful, golden, "
                 "end-of-lesson finale. No writing, numbers or symbols anywhere in the picture. Keep the "
                 "entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "★ THE UNIT RULE ★   Draw the bar, cut it into EQUAL units, label one unit first.   Know the unit → multiply: 6 × 5 = 30.   Know the whole → divide: 30 ÷ 6 = 5.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 30, "y": 13, "text": "Find the unit. Everything else follows."},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 19, "text": "Draw it, label it, THEN count!"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L7 'Word Problems with Bar Models' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 7
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l7_bar_model_word_problems"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
