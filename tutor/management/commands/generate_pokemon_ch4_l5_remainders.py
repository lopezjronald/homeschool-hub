"""Build the Ch4 L5 "Division with Remainders" manga art.

The Paldea cast returns from Chapter 3, so every character sheet is reused and a
full run draws only the eight panels.

Examples:
    python manage.py generate_pokemon_ch4_l5_remainders --dry-run --curriculum 1
    python manage.py generate_pokemon_ch4_l5_remainders --curriculum 1              # real art
    python manage.py generate_pokemon_ch4_l5_remainders --only 4,5 --curriculum 1   # redraw a beat
    python manage.py generate_pokemon_ch4_l5_remainders --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-ch4-l5-remainders"
CAST = ["fuecoco", "lechonk", "pawmi", "quaxly", "sprigatito"]
CHARACTERS = gen9(*CAST)

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "An open-air berry packing shed at dusk, with berries heaped on a counter, a stack of empty baskets and a small tin cup, as the friends gather to pack.",
        "scene": "Wide establishing shot of an open-air berry packing shed at the edge of a sunny Paldea "
                 "orchard in warm late-afternoon light. A long low wooden packing counter runs across the "
                 "LOWER half of the frame, heaped with small round yellow berries; a neat stack of empty round "
                 "baskets sits at one end and a small tin cup sits beside them. Behind the counter stands the "
                 "tidy blue-headed duckling QUAXLY; in front of it the grass kitten SPRIGATITO leans eagerly "
                 "over the berries and the plump piglet LECHONK dozes against a crate. Plain unmarked wood and "
                 "plain unmarked baskets, no signs or banners anywhere. Keep all characters and objects staged "
                 "in the lower two-thirds, with calm open evening sky above the shed roofline.",
        "refs": ["sprigatito", "quaxly", "lechonk"],
        "caption": "13 berries came in on the last cart. Every basket holds exactly 4.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 30, "y": 12, "text": "Last cart of the day! Every basket holds exactly four berries."},
            {"speaker": "Sprigatito", "kind": "speech", "x": 70, "y": 19, "text": "Then let's pack them fast!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito drops berries into baskets four at a time while Pawmi wrings its paws in panic and Fuecoco stays calm.",
        "scene": "Close on the lower half of the packing counter. The grass kitten SPRIGATITO drops small "
                 "round yellow berries into a round basket with a quick paw, another already-filled basket "
                 "beside it holding four berries. The tiny electric mouse PAWMI wrings its paws with tiny "
                 "sparks flying, ears flat, thoroughly alarmed. The chunky red crocodile FUECOCO sits calmly "
                 "behind them, entirely unbothered. Warm, comic, busy. Plain unmarked baskets and bare wood, "
                 "no signs or labels. Stage everyone low in the frame and keep the upper third as plain open "
                 "air.",
        "refs": ["sprigatito", "pawmi", "fuecoco"],
        "caption": "Packing means making groups that are all the SAME size — exactly 4 in every basket.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 12, "text": "It won't come out even! Berries are going to be LEFT OVER!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 72, "y": 19, "text": "Good. Left over is allowed."},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_FULL,
        "alt": "Three baskets in a row, each holding four berries, with a single lonely berry sitting apart on the bare counter.",
        "scene": "Clean diagram-like view along the open-air shed's wooden counter, seen from slightly above "
                 "with the open sky visible beyond it. THREE small round baskets sit in a neat evenly spaced "
                 "row, and each basket holds EXACTLY FOUR round yellow berries, clearly visible and countable. "
                 "To the right of the row, a SINGLE lone berry sits by itself on the bare empty counter with a "
                 "clear gap of empty wood between it and the last basket, gently spotlit. The red crocodile "
                 "FUECOCO crouches at the lower-left pointing a claw toward the lone berry; the blue-headed "
                 "duckling QUAXLY stands at the lower-right. Simple and uncluttered, plain unmarked baskets, "
                 "no signs or labels. Keep the entire upper third of the frame as open, empty sky.",
        "refs": ["fuecoco", "quaxly"],
        "caption": "4 + 4 + 4 = 12, and 1 berry is still on the counter.     13 ÷ 4 = 3 R 1  —  three full baskets, remainder one.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 32, "y": 12, "text": "Three full baskets… and one berry with nowhere to go."},
            {"speaker": "Quaxly", "kind": "speech", "x": 70, "y": 19, "text": "Three baskets AND one left over — both parts are the answer!"},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco taps the lonely berry with a claw while Pawmi proudly scoops it into a little tin cup.",
        "scene": "Close, warm moment low in the frame: the red crocodile FUECOCO gently taps one lone round "
                 "yellow berry on the counter with a single claw, patient and kind. Beside it the little "
                 "electric mouse PAWMI scoops that berry into a small dented tin cup held in both paws, "
                 "beaming with pride, tail up. Soft golden light, plain unmarked tin cup with no writing on "
                 "it. Keep the pair in the lower two-thirds and leave the upper third as plain, empty "
                 "background wall.",
        "refs": ["fuecoco", "pawmi"],
        "caption": "The leftover has a name: the REMAINDER. We write it with an R —  13 ÷ 4 = 3 R 1.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 32, "y": 12, "text": "The leftover has a name. It's the REMAINDER."},
            {"speaker": "Pawmi", "kind": "speech", "x": 70, "y": 19, "text": "I'll keep it in my leftover cup!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "On the next cartload Pawmi has stopped after only two baskets and its tin cup is heaped and overflowing with five leftover berries.",
        "scene": "A fresh cartload of berries has arrived behind the counter. On the counter sit only TWO "
                 "round baskets, each holding exactly four round yellow berries, and beside them the small tin "
                 "cup is heaped and overflowing with FIVE loose berries piled well above its rim, one about to "
                 "roll off. The tiny electric mouse PAWMI stands beside the cup looking enormously pleased "
                 "with itself, paws spread. The blue-headed duckling QUAXLY leans in from the right with one "
                 "narrowed, doubtful eye. Comic, suspicious mood. Plain unmarked cart, baskets and cup, no "
                 "signs or labels. Stage the counter and characters low; keep the upper third plain and empty.",
        "refs": ["pawmi", "quaxly"],
        "caption": "Another cart, another 13 berries. Pawmi's try: 2 baskets = 8 berries, so 13 − 8 = 5 berries in the cup. Is 2 R 5 right?",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 12, "text": "I stopped at two baskets! Look how full my leftover cup is!"},
            {"speaker": "Quaxly", "kind": "speech", "x": 70, "y": 19, "text": "Hmm. That cup looks… suspicious."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "Five leftover berries are tipped above an empty basket with four hollows; four settle in and the fifth hovers with nowhere to go.",
        "scene": "Clear diagram-like moment staged in the lower two-thirds of the open-air shed counter, open "
                 "sky beyond. An EMPTY round basket sits on the counter with FOUR berry-sized hollows moulded "
                 "into it, clearly visible. FIVE round yellow berries float in a line just above it, tipped "
                 "out of the tin cup: FOUR of them are settling down into the four hollows with a soft glow, "
                 "while the FIFTH hovers above the now-full basket with nowhere left to go, plainly separate. "
                 "The red crocodile FUECOCO steadies the tipped tin cup at the lower-left; the grass kitten "
                 "SPRIGATITO points up at the one stranded berry from the lower-right, eyes wide. Simple and "
                 "uncluttered, plain unmarked basket and cup, no signs or labels. Keep the entire upper third "
                 "of the frame as open, empty sky.",
        "refs": ["fuecoco", "sprigatito"],
        "caption": "Check the leftover against the basket: 5 is NOT smaller than 4 — so one more whole basket can still be filled. 2 R 5 isn't finished.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 30, "y": 12, "text": "Hold the leftovers against an empty basket. Do they still fill one?"},
            {"speaker": "Sprigatito", "kind": "speech", "x": 70, "y": 20, "text": "They do! So we're not done!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Three full baskets on the counter and exactly one berry rattling in the tin cup, while Lechonk delivers the verdict from a reclining sprawl.",
        "scene": "On the counter now sit THREE round baskets in a row, each holding exactly four round yellow "
                 "berries, and beside them the small tin cup holds ONE single berry, comically lonely at the "
                 "bottom. The plump grey-brown piglet LECHONK sprawls half-reclining against a crate at the "
                 "lower-left, one trotter lazily raised as if delivering a verdict. The tiny electric mouse "
                 "PAWMI peers into the cup at the lower-right, delighted, a small spark popping. Funny, "
                 "conclusive, warm. Plain unmarked baskets, crate and cup, no signs or labels. Keep the upper "
                 "third plain and empty.",
        "refs": ["lechonk", "pawmi"],
        "caption": "Fixed: 3 baskets is 12 berries, and 13 − 12 = 1. Remainder 1 — and 1 IS smaller than 4. ✓",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 30, "y": 12, "text": "If the leftover fills a basket, it isn't a leftover. It's a basket."},
            {"speaker": "Pawmi", "kind": "speech", "x": 70, "y": 19, "text": "One berry left. A REAL leftover!"},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset over the orchard as a cart loaded with berry baskets rolls away, all five friends travelling with it, Pawmi riding on top with its tin cup.",
        "scene": "Warm golden sunset over the Paldea berry orchard, rows of trees glowing. A little wooden "
                 "cart loaded with round baskets of yellow berries rolls along a dirt track across the LOWER "
                 "half of the frame. The tiny electric mouse PAWMI rides on top of the load hugging its small "
                 "tin cup with one berry in it; the grass kitten SPRIGATITO trots alongside, the red crocodile "
                 "FUECOCO pushes from behind, the blue-headed duckling QUAXLY marches proudly in front and the "
                 "plump piglet LECHONK naps on the tailboard. Joyful end-of-day finale. Plain unmarked cart "
                 "and baskets, no banners, signs or lettering. Keep the entire upper third of the frame as "
                 "open, empty sky.",
        "refs": CAST,
        "caption": "★ THE REMAINDER RULE ★   Fill every whole group you can. What's still left is the remainder — and it must always be SMALLER than the group size. If it isn't, make one more group.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 28, "y": 14, "text": "Fill every basket you can — then check what's left!"},
            {"speaker": "Pawmi", "kind": "speech", "x": 68, "y": 20, "text": "Smaller than the basket! Every time!"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch4 L5 'Division with Remainders' manga art."

    CHAPTER = 4
    LESSON_NUMBER = 5
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_ch4_l5_remainders"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
