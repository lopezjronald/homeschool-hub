"""Build the Ch4 L1 "Equal Groups and Arrays" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l1_equal_groups --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l1_equal_groups --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l1_equal_groups --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l1_equal_groups --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l1-equal-groups"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "Dawn in a berry orchard; all five friends work along the bushes with woven baskets, picking the first berries of the morning.",
        "scene": "Wide establishing shot of a berry orchard at early morning — low golden sun, soft mist, long "
                 "rows of berry bushes heavy with round red fruit. Along the bottom of the frame the grass "
                 "kitten SPRIGATITO, the red crocodile FUECOCO, the blue-headed duckling QUAXLY, the tiny "
                 "electric mouse PAWMI and the plump piglet LECHONK move along the bushes with woven baskets "
                 "on their arms, picking the first berries of the morning, a small wooden wheelbarrow standing "
                 "beside them. Warm, fresh, hopeful. Keep the whole upper part of the frame as open, empty "
                 "sky.",
        "refs": CAST,
        "caption": "Harvest morning. Pick fast, pile it up — and Fuecoco says it all gets SORTED, not dumped.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 50, "y": 13, "text": "Baskets ready! Nobody dump anything!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito has tipped its basket into one messy heap while Pawmi tries to count the pile one berry at a time.",
        "scene": "The picking is done. SPRIGATITO the grass kitten has cheerfully upended its woven basket, "
                 "spilling all of its round red berries into one messy heap on the orchard grass. PAWMI the "
                 "electric mouse crouches at the heap trying to count the berries one at a time with a shaking "
                 "paw, eyes crossed, small sparks popping off its cheeks in frustration. FUECOCO the red "
                 "crocodile stands calmly to one side. All three staged in the lower two-thirds of the frame; "
                 "plain misty orchard air above them, calm and empty.",
        "refs": ["sprigatito", "fuecoco", "pawmi"],
        "caption": "Counting one at a time is slow — and it is very easy to lose your place.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 12, "text": "One, two, three, four— wait, did I count that one already?"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 70, "y": 19, "text": "Don't count them all. Make EQUAL groups."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_FULL,
        "alt": "Four woven baskets in a neat row, each holding exactly three berries, with nothing left on the ground.",
        "scene": "Exactly FOUR identical small woven baskets sit in a neat, evenly spaced left-to-right row on "
                 "the orchard grass, low in the frame, all four fully visible and nothing overlapping or "
                 "hiding any of them. Each basket holds EXACTLY THREE round red berries and no more — in every "
                 "single basket the three berries sit side by side in one simple visible row of three across, "
                 "all three berries the same size and fully in view above the basket rim, with no berry tucked "
                 "behind or stacked on top of another. Four baskets, three berries each, twelve berries in "
                 "total. The bare ground all around the baskets is completely clear — no berry spilled, "
                 "dropped or left over anywhere on the grass. The baskets are the clear focus. SPRIGATITO the "
                 "grass kitten stands at the lower left of the frame, entirely clear of the baskets, pointing "
                 "proudly along the row with one paw; QUAXLY the blue-headed duckling stands neatly at the "
                 "lower right, also entirely clear of the baskets. Clean, simple, diagram-like staging, bright "
                 "and readable. No writing, numbers or symbols anywhere. Keep the entire upper third of the "
                 "frame as open, empty sky.",
        "refs": ["sprigatito", "quaxly"],
        "caption": "4 baskets, 3 berries in each:  3 + 3 + 3 + 3 = 12.     Four groups OF three  →  4 × 3 = 12",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 13, "text": "Four groups OF three! Not four and three!"},
            {"speaker": "Quaxly", "kind": "speech", "x": 70, "y": 19, "text": "Twelve berries — and I never counted past three."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito sneaks an extra berry into the third basket and Quaxly catches it in the act.",
        "scene": "Exactly FOUR identical small woven baskets sit in a neat, evenly spaced left-to-right row on "
                 "the orchard grass, low in the frame, all four fully visible with nothing overlapping or "
                 "hiding any basket mouth. The FIRST, SECOND and FOURTH baskets each hold EXACTLY THREE round "
                 "red berries, sitting side by side in one visible row of three across. The THIRD basket holds "
                 "EXACTLY FOUR round red berries, one more than the others, clearly crowding its rim so it is "
                 "obviously the odd one out at a glance. All the berries are already resting in the baskets — "
                 "none in mid-air, none falling. SPRIGATITO the grass kitten crouches BEHIND and slightly to "
                 "the LEFT of the third basket with its whole body clear of every basket mouth, one paw "
                 "withdrawing guiltily from the third basket, caught in the act with a mischievous grin. "
                 "QUAXLY the blue-headed duckling stands at the lower right of the row, scandalised, one wing "
                 "thrust out pointing straight at the third basket. FUECOCO the red crocodile stands at the "
                 "far right raising one calm claw, unbothered and kind. Comic, warm, caught-red-handed energy; "
                 "all three characters staged in the lower two-thirds. No writing, numbers or symbols "
                 "anywhere. Keep the entire upper third of the frame as open, empty misty sky with no tree "
                 "canopy, leaves or branches in it.",
        "refs": ["sprigatito", "fuecoco", "quaxly"],
        "caption": "3 + 3 + 4 + 3 = 13 — a true addition, but NOT 4 × 3. Multiplication needs every group the same size.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 30, "y": 12, "text": "Four in that one! They aren't equal groups any more!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 70, "y": 19, "text": "Pop it back, and we can multiply again."},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "The twelve berries laid out on a flat wooden drying tray as four rows across with three berries in every row.",
        "scene": "A flat wooden drying tray with a low raised rim rests on the orchard grass low in the frame, "
                 "and the tray is clearly TALLER than it is wide — an upright portrait-shaped tray, noticeably "
                 "taller top-to-bottom than it is wide left-to-right. On the tray the twelve round red berries "
                 "are arranged in one perfectly tidy upright rectangle that is exactly THREE berries ACROSS "
                 "and FOUR berries DOWN — three columns left to right, four rows top to bottom, twelve berries "
                 "in total. Every berry is the same size, evenly spaced, crisply separated from its neighbours "
                 "so each of the four rows of three is easy to count at a glance; no berry sits outside the "
                 "rectangle and none touch or overlap. PAWMI the electric mouse stands on tiptoe at the lower "
                 "left admiring the tray, tiny happy yellow sparks at its cheeks, its whole body kept low in "
                 "the frame. FUECOCO the red crocodile crouches low at the lower right steadying the edge of "
                 "the tray with one claw, kept low so that even the tip of its yellow head crest stays well "
                 "down in the lower two-thirds of the frame. Clean, bright, diagram-like staging. No writing, "
                 "numbers or symbols anywhere. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "Same 12 berries, lined up in a rectangle:  4 rows of 3  →  4 × 3 = 12.   A rectangle of rows and columns is an ARRAY.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 13, "text": "It's the same twelve! Just tidier!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "The same tray turned a quarter turn, now showing three rows across with four berries in every row.",
        "scene": "The identical wooden drying tray with the identical twelve round red berries, now rotated a "
                 "quarter turn so it lies WIDER than it is tall, low in the frame — the same rectangle of "
                 "fruit now reads as exactly FOUR berries ACROSS and THREE berries DOWN: four columns, three "
                 "rows, still twelve berries in total. Small motion-arc lines curve close around the tray, low "
                 "in the frame, showing it has just been turned; not one berry has been added or moved on the "
                 "tray itself. SPRIGATITO the grass kitten gapes at the lower left, one paw raised; QUAXLY the "
                 "duckling nods primly at the lower right. Keep the entire upper third of the frame as open, "
                 "empty sky.",
        "refs": ["sprigatito", "quaxly"],
        "caption": "Turn the tray:  3 rows of 4  →  3 × 4 = 12.     So 4 × 3 = 12 and 3 × 4 = 12. The tray moved. The berries did not.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 12, "text": "Wait— I didn't pick any more berries!"},
            {"speaker": "Quaxly", "kind": "speech", "x": 70, "y": 19, "text": "Three rows of four. Still twelve."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Lechonk lies flat on its back in the orchard grass delivering the punchline without getting up.",
        "scene": "A single continuous illustration with no bands, strips or horizontal joins anywhere — one "
                 "unbroken sky and one unbroken background painted across the whole frame from top edge to "
                 "bottom edge. LECHONK the plump grey piglet lies flat on its back in the soft orchard grass "
                 "beneath a berry bush, utterly relaxed with eyes blissfully shut, one trotter lazily raised "
                 "as if making a very small point. PAWMI the small orange electric mouse sits on the grass "
                 "beside it, ears up, listening intently. Both are staged low in the frame in warm dappled "
                 "morning light. The bushes around them carry round RED berries, matching the rest of the "
                 "orchard. Funny, sleepy, conclusive mood. No writing, numbers, symbols or speech balloons "
                 "anywhere in the art. Keep the entire upper third of the frame as open, empty sky, painted "
                 "continuously with the rest of the sky so there is no visible edge, seam or change of tone "
                 "where it meets the scene below.",
        "refs": ["lechonk", "pawmi"],
        "caption": "4 + 4 + 4 = 12 as well. Three groups of four lands in exactly the same place.",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 40, "y": 13, "text": "Learn 4 × 3 and you get 3 × 4 free. Half the work."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "All five friends carry loaded drying trays home along the orchard path in golden morning light.",
        "scene": "Golden morning light through the berry orchard. Along the lower part of the frame all five — "
                 "SPRIGATITO, FUECOCO, QUAXLY, PAWMI and LECHONK — walk the dirt path carrying flat wooden "
                 "drying trays neatly loaded with round red berries in tidy rows, PAWMI staggering comically "
                 "under the biggest tray while LECHONK ambles behind carrying nothing at all. Joyful, warm, "
                 "harvest-morning finale. Keep the entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "★ THE TWO WAYS TO SEE IT ★   Equal groups tell the STORY — 4 baskets of 3. The array shows it reads both ways — 4 × 3 = 12 and 3 × 4 = 12. And multiplying only works when every group is the same size.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 30, "y": 13, "text": "Groups of, then rows of. Same twelve."},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 19, "text": "Groups of! Rows of! TWELVE!"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L1 'Equal Groups and Arrays' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 1
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l1_equal_groups"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
