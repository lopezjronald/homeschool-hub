"""Build the Ch4 L3 "Two Ways to Divide" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l3_division_meanings --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l3_division_meanings --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l3_division_meanings --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l3_division_meanings --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l3-division-meanings"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A picnic blanket at the edge of the berry orchard with a tray of twelve berries in the middle and all five friends flopped around it.",
        "scene": "Wide establishing shot of a red-checked picnic blanket spread on grass at the edge of a "
                 "sunny berry orchard, a low hedge of berry bushes behind. On the blanket sits a shallow "
                 "wooden tray holding exactly twelve round red berries, loosely heaped but clearly countable. "
                 "QUAXLY the tidy blue-headed duckling stands beside the tray looking organised; SPRIGATITO "
                 "the grass kitten, FUECOCO the red crocodile, PAWMI the tiny electric mouse and LECHONK the "
                 "plump piglet sprawl around the blanket, tired and happy after a morning of picking. Empty "
                 "wicker picking baskets stacked at the side. Warm, bright, inviting. Stage every character "
                 "and the tray low, in the bottom two-thirds of the frame, and keep the upper third calm and "
                 "open bright sky.",
        "refs": CAST,
        "caption": "Twelve berries. One tray. Nobody can agree on how to split them.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 50, "y": 13, "text": "Picking is finished. Now — how do we divide them?"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito and Quaxly each pull Pawmi in a different direction while it panics and throws off sparks.",
        "scene": "Comic tug-of-war on the blanket: SPRIGATITO the grass kitten pulls PAWMI the tiny electric "
                 "mouse to the left while QUAXLY the blue-headed duckling pulls it to the right, both talking "
                 "at once. PAWMI is caught in the middle, eyes spinning, small sparks flying off its cheeks. "
                 "SPRIGATITO holds up a small empty wicker basket in one paw; QUAXLY gestures at three empty "
                 "plates on the blanket. Funny, energetic, warm. Stage all three characters low, in the bottom "
                 "two-thirds of the frame, and keep the upper third calm and open sky.",
        "refs": ["sprigatito", "quaxly", "pawmi"],
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 30, "y": 12, "text": "Share them onto 3 plates — how many on EACH?"},
            {"speaker": "Sprigatito", "kind": "speech", "x": 70, "y": 19, "text": "No! Baskets of 3 — how many BASKETS?"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco calmly sets out three empty plates and deals berries around one at a time like cards.",
        "scene": "FUECOCO the chunky red crocodile crouches calmly on the blanket with THREE empty plates set "
                 "out in a row in front of him. He is dealing round red berries onto them one at a time, like "
                 "dealing cards, one berry hovering just above a plate mid-deal. SPRIGATITO and QUAXLY lean in "
                 "on either side, quiet now. Patient, kind, teacherly. Stage the characters and plates low, in "
                 "the bottom two-thirds of the frame, and keep the upper third calm and open sky.",
        "refs": ["sprigatito", "fuecoco", "quaxly"],
        "caption": "Dealing one at a time keeps every plate equal. Equal groups — that is the rule division never breaks.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 44, "y": 12, "text": "Nobody argue — we'll draw BOTH. One for you, one for you, one for you..."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Three plates on the blanket, four berries on each, with the tray now empty beside them.",
        "scene": "Clean, diagram-like arrangement low in the frame: THREE identical plates in a row on the "
                 "picnic blanket, each holding exactly FOUR round red berries laid out clearly and countably, "
                 "plus the shallow wooden tray sitting conspicuously EMPTY beside them. FUECOCO the red "
                 "crocodile at the lower right has just released the very last berry, claw still open above "
                 "the third plate; QUAXLY the blue-headed duckling at the lower left beams with approval. "
                 "Simple, uncluttered, easy to count. Keep the entire upper third of the frame as open, empty "
                 "sky.",
        "refs": ["fuecoco", "quaxly"],
        "caption": "SHARING — 12 berries shared equally onto 3 plates: how many on EACH?   12 ÷ 3 = 4.   Four berries each. We knew the number of GROUPS; we were hunting the SIZE of each.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 34, "y": 13, "text": "Four each. Perfectly fair."},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "The same twelve berries scooped into four small baskets, three berries in every basket.",
        "scene": "Clean, diagram-like arrangement low in the frame: FOUR identical small wicker baskets in a "
                 "row on the picnic blanket, each holding exactly THREE round red berries, clearly visible and "
                 "countable. The three plates from before sit empty and set aside at the edge of the blanket. "
                 "SPRIGATITO the grass kitten at the lower left points along the row of baskets, delighted; "
                 "PAWMI the tiny electric mouse at the lower right counts them on its paws with a spark of "
                 "excitement. Simple, uncluttered, easy to count. Keep the entire upper third of the frame as "
                 "open, empty sky.",
        "refs": ["sprigatito", "pawmi"],
        "caption": "GROUPING — the same 12 berries put into baskets of 3: how many BASKETS?   12 ÷ 3 = 4.   Four baskets. This time we knew the SIZE of each group; we were hunting the number of GROUPS.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 36, "y": 13, "text": "Four baskets! Same berries — but now the four counts BASKETS."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco holds up a plate of four berries in one claw and a small basket of three berries in the other while Pawmi stares in amazement.",
        "scene": "FUECOCO the red crocodile sits low on the blanket holding up a plate of four round red "
                 "berries in his left claw and a small wicker basket of three round red berries in his right "
                 "claw, presenting them side by side like a comparison. PAWMI the tiny electric mouse stares "
                 "between them with enormous round eyes and an open mouth, thunderstruck, one paw on its head. "
                 "Warm, funny, the penny-drop moment. Stage both characters low, in the bottom two-thirds of "
                 "the frame, and keep the upper third calm and open sky.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "Both pictures are 12 ÷ 3 = 4. Sharing answers how many in EACH group. Grouping answers how many GROUPS.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 30, "y": 12, "text": "Same berries. Same equation. Two different questions."},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 19, "text": "One says EACH, one says GROUPS!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_FULL,
        "alt": "All twelve berries laid out on the tray in a tidy rectangle of three rows of four.",
        "scene": "The shallow wooden tray sits low and centred on the blanket with all twelve round red "
                 "berries arranged in a perfectly tidy rectangle: THREE straight horizontal rows with FOUR "
                 "berries in each row, evenly spaced, crisp and countable, seen from a high three-quarter "
                 "angle. QUAXLY the blue-headed duckling stands at the lower left admiring the neatness; "
                 "FUECOCO the red crocodile rests a claw on the tray edge at the lower right. Clean, orderly, "
                 "diagram-like. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["quaxly", "fuecoco"],
        "caption": "3 rows of 4 = 12, so 3 × 4 = 12 — and that hands you 12 ÷ 3 = 4 AND 12 ÷ 4 = 3. One picture, one fact family.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 36, "y": 13, "text": "Learn one fact and you get four!"},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset over the orchard as Lechonk nudges the tray a quarter turn into four rows of three and all five friends lean in to eat.",
        "scene": "Warm golden sunset over the berry orchard. The shallow wooden tray sits low and centred on "
                 "the picnic blanket, its twelve round red berries now arranged as FOUR straight rows with "
                 "THREE berries in each row, crisp and countable. LECHONK the plump piglet, still lying down, "
                 "has just nudged the tray a quarter-turn with one trotter and looks extremely pleased with "
                 "itself. SPRIGATITO, FUECOCO, QUAXLY and PAWMI lean in around the tray, paws and claws "
                 "reaching for their first berry, grinning; the empty plates and small wicker baskets are "
                 "stacked at the edge of the blanket. Joyful, cosy, end-of-lesson finale. Keep the entire "
                 "upper third of the frame as open, empty sunset sky.",
        "refs": CAST,
        "caption": "★ DIVISION RULE ★   Ask WHICH question first: how many in each group, or how many groups? And turning the tray shows 4 × 3 = 12 too — every division fact has a multiplication fact holding its hand.",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 28, "y": 12, "text": "Turn the tray — four rows of three. Still twelve. I didn't even get up."},
            {"speaker": "Pawmi", "kind": "speech", "x": 66, "y": 19, "text": "Four each! Four baskets! Four everything!"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L3 'Two Ways to Divide' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 3
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l3_division_meanings"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
