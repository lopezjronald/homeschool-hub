"""Build the Ch4 L4 "Multiplying and Dividing with 0 and 1" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l4_zero_and_one --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l4_zero_and_one --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l4_zero_and_one --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l4_zero_and_one --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l4-zero-and-one"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A golden-hour berry market stall at closing time; the five friends pack down baskets and one last crate of berries under a wide open sky.",
        "scene": "Wide establishing shot of a small open-air berry market at the end of a golden afternoon, "
                 "camera at counter height with NO awning or roof overhead — the awning is out of frame above, "
                 "so nothing hangs down into the picture. A plain wooden stall counter fills the LOWER half of "
                 "the frame, with stacked woven baskets and one low crate of dark purple berries still on it; "
                 "rows of berry bushes stretch behind at mid-height only. The grass kitten SPRIGATITO, the "
                 "chunky red crocodile FUECOCO, the tidy blue duckling QUAXLY, the tiny orange mouse PAWMI and "
                 "the plump piglet LECHONK are packing up together along the counter, cheerful and pleasantly "
                 "tired, every one of them staged in the lower two-thirds with no ear tip, head or tail rising "
                 "above the halfway line. Warm sunset light, dust motes in the air. No signs, lettering, "
                 "numbers or written words anywhere in the image. No awning, no posts, no beams, no bunting "
                 "and no tree canopy anywhere in the upper part of the picture. Keep the entire upper third of "
                 "the frame as open, empty golden sky.",
        "refs": CAST,
        "caption": "Closing time at the orchard market — and almost every basket is empty.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 32, "y": 13, "text": "Last stall of the day, everyone. Pack it down!"},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 18, "text": "Wait — my basket still has berries in it!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi holds up a single small basket of berries with both paws while Fuecoco leans in calmly beside a row of tiny empty cups.",
        "scene": "PAWMI the tiny orange-tan electric mouse stands on the stall counter holding up ONE small "
                 "woven basket with both paws, a neat little heap of dark berries inside it, cheeks sparking "
                 "with worry, eyes wide. FUECOCO the chunky red crocodile leans in from the lower right, calm "
                 "and encouraging, one claw resting on the counter beside a row of tiny empty clay cups. Warm "
                 "evening light, cozy stall interior, plain unmarked wood, no lettering or numbers anywhere. "
                 "Both characters staged low in the frame with the upper third left plain and empty.",
        "refs": ["pawmi", "fuecoco"],
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 13, "text": "It's just ONE basket. One isn't even a real times problem… is it?"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 66, "y": 18, "text": "One group is still a group. Watch what one does."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_FULL,
        "alt": "One basket holding seven berries sits beside a row of seven tiny cups that each hold exactly one berry; Fuecoco gestures at the basket while Pawmi peers into the cups.",
        "scene": "A scrubbed wooden stall counter with TWO arrangements side by side, both staged in the lower "
                 "two-thirds. On the LEFT, ONE single round woven basket, wider than it is tall, holding "
                 "exactly SEVEN plump dark-purple berries and no more — arrange the seven so each berry is "
                 "separately countable: four berries sitting in a row across the front of the basket and three "
                 "berries resting on top of them, every berry fully round and clearly separated from its "
                 "neighbours by a visible gap. On the RIGHT, one single straight horizontal row of exactly "
                 "SEVEN identical tiny clay cups, 7 ACROSS and 1 DOWN — seven cups in one line, evenly spaced, "
                 "all the same size, none stacked, none behind another, no second row — and each cup holds "
                 "exactly ONE berry resting in its mouth and nothing more, so the row reads as seven berries "
                 "total. FUECOCO the chunky red crocodile sits at the lower left gesturing calmly toward the "
                 "single basket; PAWMI the tiny orange mouse stands at the lower right on tiptoe, peering "
                 "delightedly along the row of little cups. Warm golden light. No lettering, numbers, signs or "
                 "written words anywhere in the image. Keep the entire upper third of the frame as open, empty "
                 "sky.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "One group of 7 → 1 × 7 = 7.   Seven groups of 1 → 7 × 1 = 7.   Same berries, different picture.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 30, "y": 12, "text": "One group of seven, or seven groups of one — both make seven."},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 17, "text": "They look SO different but it's the same pile!"},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito peers under the last of a row of five upturned baskets in comic dismay while Lechonk lies flopped and unbothered nearby, chewing.",
        "scene": "SPRIGATITO the cream and pale-green grass kitten with a leaf ruff has flipped a row of "
                 "exactly FIVE woven baskets upside down along the stall counter — count them as five and no "
                 "other number: FOUR baskets sit dome-up on the counter in one straight left-to-right line, "
                 "evenly spaced with a clear gap between each, and the FIFTH basket at the right end of that "
                 "same line is tipped up in Sprigatito's paw so its plainly empty inside is visible, giving "
                 "five baskets in total, 5 ACROSS and 1 DOWN, none stacked and none hidden behind another. "
                 "Sprigatito peers underneath the lifted one with a comic look of dismay; every one of the "
                 "five is obviously, completely empty. LECHONK the plump grey-brown piglet lies flopped on its "
                 "side on the grass beside the counter, utterly unbothered, lazily chewing a single dark "
                 "berry. Funny, warm, evening light, plain unmarked wood, no lettering or numbers anywhere. "
                 "Stage BOTH characters entirely in the lower two-thirds — Sprigatito crouches low over the "
                 "counter so that even her ear tips stay below the halfway line of the frame. Keep the entire "
                 "upper third of the frame as open, empty sky.",
        "refs": ["sprigatito", "lechonk"],
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 33, "y": 13, "text": "I flipped every basket. Empty, empty, empty, empty, empty!"},
            {"speaker": "Lechonk", "kind": "speech", "x": 69, "y": 18, "text": "Five whole baskets of nothing. We are rich in air."},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "Five plainly empty baskets in a row on one side of the counter, and a completely bare stretch of counter with no baskets at all on the other; Sprigatito and Quaxly stand at each end.",
        "scene": "The same wooden stall counter, staged low, with a clear left half and right half. On the "
                 "LEFT half, exactly FIVE identical woven baskets in ONE single straight horizontal row, 5 "
                 "ACROSS and 1 DOWN — five baskets side by side in a single line, evenly spaced with a visible "
                 "gap of bare counter between each one, all the same size, none stacked, none tucked behind "
                 "another, and no second row of baskets anywhere. Each of the five is tipped slightly toward "
                 "the viewer so you can plainly see that every one is completely EMPTY inside — bare woven "
                 "bottom, not one berry. On the RIGHT half, a wide stretch of bare, clean, polished counter "
                 "with absolutely nothing on it at all — no baskets, no berries, no crates, just empty wood. "
                 "SPRIGATITO the grass kitten stands at the lower left with one paw resting on the end basket, "
                 "whiskers twitching; QUAXLY the tidy blue-headed duckling stands at the lower right beside "
                 "the bare counter, one wing raised, poised and precise. Warm evening light. No lettering, "
                 "numbers, signs or written words anywhere in the image. Keep the entire upper third of the "
                 "frame as open, empty sky.",
        "refs": ["sprigatito", "quaxly"],
        "caption": "Five groups of 0 → 5 × 0 = 0.   No groups at all → 0 × 7 = 0.   Nothing, however you stack it.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 12, "text": "Five baskets of nothing is… still nothing!"},
            {"speaker": "Quaxly", "kind": "speech", "x": 68, "y": 17, "text": "And no baskets at all? Nothing again. Zero wins twice."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_WIDE,
        "alt": "Quaxly tips six berries into one wide basket on one side; on the other, the same six berries sit in six tiny cups with one berry each, as Fuecoco looks on.",
        "scene": "The stall counter fills the lower half of the frame, split into a left half and a right "
                 "half. On the LEFT, QUAXLY the tidy blue duckling has just finished tipping a small plain "
                 "wooden crate — the crate is now held mouth-down and is completely EMPTY, with no berries "
                 "inside it and no berries at all in mid-air — and all the berries have already landed in ONE "
                 "single wide round woven basket, wider than it is tall, which now holds exactly SIX dark "
                 "berries and no more: arrange the six in the basket as 3 ACROSS in a front row and 3 ACROSS "
                 "in a back row, each berry fully round and clearly separated from its neighbours so all six "
                 "can be counted at a glance. On the RIGHT, exactly SIX tiny identical clay cups stand in ONE "
                 "single straight horizontal row, 6 ACROSS and 1 DOWN, evenly spaced, none stacked or hidden, "
                 "and each cup holds exactly ONE berry — six cups, six berries. FUECOCO the chunky red "
                 "crocodile sits at the lower right, calm and pleased, one claw indicating the row of little "
                 "cups. Warm evening light, plain unmarked wood, no lettering, numbers or written words "
                 "anywhere in the image. Stage everything in the lower two-thirds and keep the entire upper "
                 "third of the frame calm, plain and empty.",
        "refs": ["quaxly", "fuecoco"],
        "caption": "All 6 into 1 basket → 6 ÷ 1 = 6.   6 berries into 6 cups → 6 ÷ 6 = 1 each.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 30, "y": 13, "text": "Lechonk ate one! Six left — and this basket gets every single one."},
            {"speaker": "Fuecoco", "kind": "speech", "x": 70, "y": 18, "text": "Six berries, six cups: exactly one each."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_FULL,
        "alt": "On one side an upturned empty crate above six empty cups; on the other an endless receding line of empty baskets while a crate of six berries sits untouched. Pawmi is frantic, Fuecoco is calm.",
        "scene": "A split scene along the stall counter, staged low. On the LEFT: an upturned, completely "
                 "EMPTY wooden crate resting mouth-down beside ONE single straight horizontal row of exactly "
                 "SIX tiny clay cups, 6 ACROSS and 1 DOWN — six cups in one line, evenly spaced with a clear "
                 "gap between each, all the same size, none stacked, none behind another, no second row and no "
                 "stray extra cup anywhere — and every single one of the six cups is visibly empty inside, "
                 "because there was nothing to share out. On the RIGHT: a long line of EMPTY woven baskets "
                 "marching away from the counter into the distance, one after another after another, receding "
                 "endlessly toward the horizon and every one of them empty; meanwhile a small wooden crate "
                 "holding exactly SIX dark berries, arranged 3 ACROSS and 2 DOWN so all six are separately "
                 "countable, still sits untouched and full at the near edge of the counter. PAWMI the tiny "
                 "orange mouse stands frantic in the lower middle, paws thrown up, sparks flying from its "
                 "cheeks as it stares down the endless line of empty baskets; FUECOCO the chunky red crocodile "
                 "sits calmly in the lower left corner, steady and kind. No lettering, numbers, signs or "
                 "written words anywhere in the image. Keep the entire upper third of the frame as open, empty "
                 "sky.",
        "refs": ["pawmi", "fuecoco"],
        "caption": "0 ÷ 6 = 0 — nothing shared out is nothing each.   But 6 ÷ 0? Empty baskets never hold 6 berries — there is NO answer.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 30, "y": 12, "text": "A hundred empty baskets and the six berries are STILL sitting there!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 68, "y": 18, "text": "Groups of nothing never add up. That's why 6 ÷ 0 has no answer."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset over the orchard market: lanterns lit, the stall packed down, and all five friends sitting on the grass sharing one small basket of berries.",
        "scene": "Warm sunset over the orchard market at Sunset Row: the stall is packed down, small plain "
                 "paper lanterns are being lit along the awning posts, and rows of berry bushes glow gold "
                 "behind. All five — SPRIGATITO, FUECOCO, QUAXLY, PAWMI and LECHONK — sit together on the "
                 "grass in front of the stall sharing one small woven basket of dark berries between them; "
                 "LECHONK is flopped happily on its side, PAWMI dozes leaning against big friendly FUECOCO, "
                 "SPRIGATITO curls beside QUAXLY. Tender, cheerful, contented finale. No signs, lettering, "
                 "numbers or written words anywhere in the image — the lanterns and awning are plain and "
                 "blank. Keep the entire upper third of the frame as open, empty sunset sky.",
        "refs": CAST,
        "caption": "★ THE 0 AND 1 RULES ★   × 1 keeps a number the same. × 0 makes it 0. ÷ 1 keeps it the same. A number ÷ itself is 1. 0 ÷ a number is 0. But you can never divide BY 0 — no pile of empty baskets ever fills up, so there is no answer.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 28, "y": 13, "text": "One keeps it the same. Zero empties it. And nobody divides by zero!"},
            {"speaker": "Lechonk", "kind": "speech", "x": 70, "y": 18, "text": "Six berries, five friends… let's not do THAT one tonight."},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L4 'Multiplying and Dividing with 0 and 1' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 4
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l4_zero_and_one"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
