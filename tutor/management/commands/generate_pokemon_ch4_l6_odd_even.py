"""Build the Ch4 L6 "Odd and Even Numbers" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l6_odd_even --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l6_odd_even --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l6_odd_even --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l6_odd_even --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l6-odd-even"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A sunny orchard pond at harvest time: a wooden dock stacked with crates of red berries, a row of tiny two-seat leaf boats on the water, and all five friends gathered.",
        "scene": "Wide establishing shot of a bright orchard pond on a sunny harvest morning. A low wooden "
                 "dock runs along the bottom of the frame, stacked with crates of round red berries. Bobbing "
                 "at the dock is a neat row of tiny leaf boats, each one clearly built with exactly TWO little "
                 "seats side by side. The blue-headed duckling QUAXLY stands poised at the dock rail; the "
                 "grass kitten SPRIGATITO, the red crocodile FUECOCO, the tiny electric mouse PAWMI and the "
                 "plump piglet LECHONK are gathered along the dock. Cheerful, busy, colourful. No writing, "
                 "signs or symbols anywhere. Stage everything in the lower two-thirds and keep the upper third "
                 "calm open sky.",
        "refs": CAST,
        "caption": "Harvest morning at the orchard pond. Every leaf boat carries exactly TWO berries — two seats, no more, no less.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 50, "y": 13, "text": "Two seats. Two berries. That is the whole rule!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito tips a basket and eight berries roll into a line along the dock while Pawmi looks worried.",
        "scene": "SPRIGATITO the grass kitten tips a woven basket on its side so that EIGHT round red berries "
                 "roll out and settle into a tidy line along the wooden dock. PAWMI the tiny electric mouse "
                 "stands beside the line, paws pressed to its cheeks, tail up, small sparks of worry popping "
                 "around it. Warm, comic, low camera close to the dock boards. No writing or symbols anywhere. "
                 "Calm empty sky across the top third.",
        "refs": ["sprigatito", "pawmi"],
        "caption": "Eight berries, and every boat holds two. Will everybody find a buddy?",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 34, "y": 13, "text": "Eight berries picked! Does everybody get a buddy?"},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 19, "text": "What if one is left ALL ALONE?!"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_FULL,
        "alt": "Four leaf boats sail away from the dock, each carrying exactly two berries side by side, leaving the dock completely empty.",
        "scene": "FOUR little leaf boats sail out across the calm pond in a row, and every single boat carries "
                 "exactly TWO round red berries sitting side by side in its two seats — all four boats "
                 "equally, obviously full. Behind them the wooden dock is completely EMPTY, swept clean, not "
                 "one berry left on it. QUAXLY stands proudly at the lower-left end of the empty dock; "
                 "SPRIGATITO watches from the lower-right, delighted. Clean and diagram-like so the four "
                 "matching pairs read instantly. No writing, numbers or symbols anywhere. Keep the entire "
                 "upper third of the frame as open, empty sky.",
        "refs": ["sprigatito", "quaxly"],
        "caption": "Every berry found a buddy. 8 ÷ 2 = 4 with 0 left over — so 8 is EVEN.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 40, "y": 13, "text": "Four boats, all full. Nobody left on the dock — that's EVEN!"},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Three leaf boats sail away with two berries each while one lonely berry sits by itself at the end of the dock.",
        "scene": "THREE leaf boats sail out across the pond, each carrying exactly TWO round red berries side "
                 "by side. Back on the wooden dock, ONE single small red berry sits all by itself right at the "
                 "end of the boards, with nothing beside it, waiting — the empty space around it left wide and "
                 "obvious. PAWMI the electric mouse stands at the lower-left pointing at the lonely berry, "
                 "eyes huge; FUECOCO the red crocodile watches gently from the lower-right. Same clean "
                 "diagram-like staging as the previous crossing so the missing partner is unmistakable. No "
                 "writing, numbers or symbols anywhere. Keep the entire upper third of the frame as open, "
                 "empty sky.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "Seven won't pair up all the way. 7 ÷ 2 = 3 with 1 left over — so 7 is ODD.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 40, "y": 13, "text": "Three boats… and one berry with nobody. That's ODD!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco settles kindly beside the single leftover berry on the dock while Sprigatito leans in.",
        "scene": "FUECOCO the chunky red crocodile settles down on the dock boards beside the ONE leftover red "
                 "berry, curling a claw around it gently and warmly, reassuring rather than scolding. "
                 "SPRIGATITO the grass kitten leans in close from the side, ears forward, listening. Tender, "
                 "funny, low to the dock. No writing or symbols anywhere. Plain calm sky filling the top "
                 "third.",
        "refs": ["fuecoco", "sprigatito"],
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 38, "y": 12, "text": "Odd isn't wrong. It just means one is left over after every pair."},
            {"speaker": "Sprigatito", "kind": "speech", "x": 66, "y": 19, "text": "One more than a pair!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "On the far shore, two baskets hold four berries each at equal heights; beside them two more baskets hold three and four, clearly uneven.",
        "scene": "On the grassy far shore, TWO identical open baskets stand side by side, each holding FOUR "
                 "round red berries, the two heaps exactly level with each other — perfectly fair. A little "
                 "apart from them stand TWO more identical baskets: the left one holds THREE berries and the "
                 "right one holds FOUR, so one heap sits visibly lower than the other — clearly uneven. "
                 "Simple, clean, chart-like, both pairs of baskets low in the frame and easy to compare. "
                 "FUECOCO stands at the lower-left beside the level pair; QUAXLY at the lower-right beside the "
                 "uneven pair. No writing, numbers, labels or symbols anywhere. Keep the entire upper third of "
                 "the frame as open, empty sky.",
        "refs": ["fuecoco", "quaxly"],
        "caption": "EVEN splits into TWO EQUAL groups:  8 = 4 + 4.   Odd can't:  7 = 3 + 4, and 3 is not 4.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 40, "y": 12, "text": "Even splits into two FAIR halves. Odd leaves them uneven."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "A long line of loaded leaf boats crosses the pond while Quaxly flings out a wing in discovery and Lechonk dozes on a berry crate.",
        "scene": "A long line of leaf boats stretches away across the pond, each one loaded with its pair of "
                 "berries. QUAXLY the tidy duckling stands at the dock edge with one wing flung out "
                 "dramatically, beak open, struck by a sudden discovery. LECHONK the plump piglet lies "
                 "sprawled and half-asleep on a stacked berry crate nearby, utterly unbothered, one trotter "
                 "lazily raised. Comic contrast between them, both staged low in the frame. No writing, "
                 "numbers or symbols anywhere. Open sky across the top third.",
        "refs": ["quaxly", "lechonk"],
        "caption": "Count the evens: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20 — the last digit is always 0, 2, 4, 6 or 8. So 34 is even (34 ÷ 2 = 17, nothing left) and 25 is odd (25 ÷ 2 = 12, with 1 left).",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 32, "y": 12, "text": "I see it! Every even number ends in 0, 2, 4, 6 or 8!"},
            {"speaker": "Lechonk", "kind": "speech", "x": 64, "y": 19, "text": "So don't pair 34 berries — peek at the last one!"},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset over the orchard pond with every boat home and all five friends sitting together on the dock, the last little berry safe in Fuecoco's claw.",
        "scene": "Warm golden sunset over the orchard pond. All the leaf boats are moored home along the dock "
                 "and the berry crates are neatly stacked. SPRIGATITO, FUECOCO, QUAXLY, PAWMI and LECHONK sit "
                 "together in a contented row along the edge of the dock with their feet over the water, "
                 "LECHONK already dozing; FUECOCO cradles the one small leftover red berry safely in a claw. "
                 "Tender, cheerful, restful finale, everyone staged along the lower part of the frame. No "
                 "writing, numbers or symbols anywhere. Keep the entire upper third of the frame as open, "
                 "empty sky.",
        "refs": CAST,
        "caption": "★ THE BUDDY RULE ★   Pair them two-by-two. Nobody left over = EVEN. One left with no buddy = ODD. Even splits into two equal groups; odd always has one over — and the last digit will tell you.   To be continued →",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 40, "y": 14, "text": "Buddy up! Nobody left — even. One left over — odd."},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L6 'Odd and Even Numbers' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 6
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l6_odd_even"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
