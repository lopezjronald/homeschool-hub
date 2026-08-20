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
                 "orchard in warm late-afternoon light. A long low wooden packing counter, wider than it is "
                 "tall, runs across the LOWER half of the frame. Lying on the counter are EXACTLY THIRTEEN "
                 "small round yellow berries, all the same size, spread out in a single loose layer with a "
                 "clear gap of bare wood between each one so that every single berry is separate and countable "
                 "— no heap, no mound, no berries touching, overlapping or hidden behind one another. There "
                 "must be exactly thirteen berries in the whole picture and no berries anywhere else. A neat "
                 "stack of empty round baskets sits at the left end of the counter and one small plain tin cup "
                 "sits beside the stack. Behind the counter stands the tidy blue-headed duckling QUAXLY; in "
                 "front of it the grass kitten SPRIGATITO leans eagerly over the berries and the plump piglet "
                 "LECHONK dozes against a crate at the right end. Plain unmarked wood and plain unmarked "
                 "baskets, no signs, banners, letters or numbers anywhere. Stage every character and object in "
                 "the lower two-thirds of the frame. Keep the entire upper third of the frame as open, empty "
                 "sky.",
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
        "scene": "Close on the lower half of the wooden packing counter inside the open-air shed. At the left "
                 "the grass kitten SPRIGATITO drops small round yellow berries into a round basket with a "
                 "quick paw: that basket holds THREE berries so far with TWO more berries falling through the "
                 "air toward it. Immediately to its right an identical round basket is already finished and "
                 "holds EXACTLY FOUR round yellow berries, evenly spaced in a shallow ring so all four are "
                 "clearly separate and countable. The tiny electric mouse PAWMI stands at the right wringing "
                 "its paws with tiny sparks flying, ears flat, thoroughly alarmed. The chunky red crocodile "
                 "FUECOCO sits calmly between the two of them, entirely unbothered. Seat FUECOCO low behind "
                 "the counter so that the very top of its yellow head-crest sits BELOW the halfway line of the "
                 "frame; no character's head, ears, tail or crest may reach into the upper third of the "
                 "picture. Keep the background behind the upper part of the frame a plain, softly lit, "
                 "unbroken wall of pale open air with no beams, window frames, shelves or dark woodwork "
                 "crossing it. Warm, comic, busy mood. Plain unmarked baskets and bare wood, no signs, labels, "
                 "letters or numbers. Keep the entire upper third of the frame as calm, plain, empty open "
                 "background.",
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
        "scene": "Close, warm, softly lit moment staged low in the frame against a plain interior wall. "
                 "EXACTLY ONE round yellow berry sits alone on the bare wooden counter — it is the only berry "
                 "anywhere in the picture. At the left the chunky red crocodile FUECOCO gently touches that "
                 "single berry with one claw, patient and kind. At the right the little electric mouse PAWMI "
                 "holds a small dented tin cup in both paws, tilted slightly toward the berry, beaming with "
                 "pride, tail up, plainly about to scoop it. The tin cup is completely EMPTY — no berry inside "
                 "it, no berry at its rim, and no berry in Pawmi's paws. Soft golden light, plain unmarked tin "
                 "cup with no writing on it. Pose both characters crouched low over the counter so that the "
                 "top of FUECOCO's yellow head-crest and the tips of PAWMI's ears both stay BELOW the halfway "
                 "line of the frame, and nothing reaches into the upper third. Keep the entire upper third of "
                 "the frame as plain, calm, empty background wall.",
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
        "scene": "A fresh cartload of berries has arrived behind the counter in the background. On the wooden "
                 "packing counter, which is wider than it is tall, sit EXACTLY TWO round baskets side by side "
                 "toward the left — two baskets only, no third basket anywhere. Each of the two baskets holds "
                 "EXACTLY FOUR round yellow berries: four in the left basket and four in the right basket, "
                 "evenly spaced in a shallow ring so that all four in each are separate, unhidden and "
                 "countable. To the right of the two baskets, standing alone on the bare counter with a clear "
                 "gap of wood between it and the baskets, is the small tin cup, heaped and overflowing with "
                 "EXACTLY FIVE loose round yellow berries — two sitting down inside the cup and three piled in "
                 "a wobbly stack above its rim, the topmost one tipping as if about to roll off. All five "
                 "leftover berries must be separately visible and countable, and there must be no other loose "
                 "berries anywhere on the counter. The tiny electric mouse PAWMI stands beside the cup looking "
                 "enormously pleased with itself, paws spread. The blue-headed duckling QUAXLY leans in from "
                 "the right with one narrowed, doubtful eye. Comic, suspicious mood. Load the background cart "
                 "with the same small round yellow berries, not mixed fruit. Plain unmarked cart, baskets and "
                 "cup, no signs, labels, letters or numbers. Stage the counter and all characters low in the "
                 "frame. Keep the entire upper third of the frame as open, empty sky.",
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
        "scene": "Clear diagram-like moment staged in the lower two-thirds of the open-air shed counter, with "
                 "open sky beyond. In the centre of the wooden counter sits ONE round basket, wider than it is "
                 "tall, seen from slightly above, its floor moulded with EXACTLY FOUR round berry-sized "
                 "hollows — four hollows, no more and no fewer — arranged TWO ACROSS and TWO DOWN (2 columns, "
                 "2 rows). The basket is EMPTY: no berry is resting in it yet. EXACTLY FIVE round yellow "
                 "berries have just been tipped out of the small dented tin cup, which the chunky red "
                 "crocodile FUECOCO steadies on its side at the lower-left. FOUR of those five berries hang in "
                 "the air just above the basket, one directly over each of the four hollows, each with a soft "
                 "glow beneath it showing it is settling in. The FIFTH berry hovers well off to the RIGHT of "
                 "the basket at roughly the same height as the other four, separated from them by a wide gap "
                 "of plain empty air, with bare counter and no hollow beneath it — plainly stranded with "
                 "nowhere to go. There must be exactly five berries in the whole picture: four above the four "
                 "hollows and one alone to the right. The grass kitten SPRIGATITO points up at the single "
                 "stranded berry from the lower-right, eyes wide. Simple and uncluttered, plain unmarked "
                 "basket and cup, no signs, labels, letters or numbers. Keep the entire upper third of the "
                 "frame as open, empty sky.",
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
        "scene": "On the wooden counter, which is wider than it is tall, sit EXACTLY THREE round baskets in a "
                 "single straight left-to-right row, evenly spaced along the counter — three baskets only, "
                 "with no fourth basket anywhere in the picture and no second row or front row. Each of the "
                 "three baskets holds EXACTLY FOUR round yellow berries, evenly spaced in a shallow ring so "
                 "that all four in each basket are separate, unhidden and countable. To the right of the row, "
                 "with a clear gap of bare counter between it and the last basket, stands the small tin cup "
                 "holding EXACTLY ONE single round yellow berry resting comically alone at the bottom. The "
                 "plump grey-brown piglet LECHONK sprawls half-reclining against a crate at the lower-left, "
                 "one trotter lazily raised as if delivering a verdict. The tiny electric mouse PAWMI peers "
                 "down into the cup at the lower-right, delighted, a small spark popping; keep PAWMI entirely "
                 "clear of the baskets so that none of the three baskets or their berries are blocked from "
                 "view. Funny, conclusive, warm mood. Plain unmarked baskets, crate and cup, no signs, labels, "
                 "letters or numbers. Stage the counter and both characters low in the frame. Keep the entire "
                 "upper third of the frame as open, empty sky.",
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
