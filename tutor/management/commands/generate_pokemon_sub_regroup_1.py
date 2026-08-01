"""Build the Ch3 L2 "Quaxly Unties a Bundle" subtraction-with-regrouping manga.

Reuses the Sprigatito and Fuecoco character sheets already committed under
``static/manga/pokemon-regrouping/`` (see _manga_art.SHEET_DIRS) so the cast is
literally the same cast as Lesson 1 — which is the point, since this lesson is
the visible reverse of that one. Only Quaxly is new, so a full run draws one
sheet rather than three.

Examples:
    python manage.py generate_pokemon_sub_regroup_1 --dry-run --curriculum 1
    python manage.py generate_pokemon_sub_regroup_1 --curriculum 1              # real art
    python manage.py generate_pokemon_sub_regroup_1 --only 4,5 --curriculum 1   # redraw the untying
    python manage.py generate_pokemon_sub_regroup_1 --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-sub-regroup-1"
# Sprigatito and Fuecoco are listed but already committed under Lesson 1's dir,
# so they are reused as reference sheets rather than redrawn. Only Quaxly is new.
CHARACTERS = gen9("sprigatito", "fuecoco", "quaxly")
CAST = ["sprigatito", "fuecoco", "quaxly"]

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A berry market stall in the morning; Sprigatito and Fuecoco behind the counter, Quaxly the blue duckling arriving with a basket.",
        "scene": "Wide establishing shot of a cheerful open-air berry market stall in sunny Paldea. The "
                 "cream-green grass kitten SPRIGATITO and the chunky red crocodile FUECOCO stand behind a "
                 "wooden counter stacked with baskets of round red berries. The small blue-headed white "
                 "duckling QUAXLY waddles up to the counter carrying an empty basket. Bright morning light, "
                 "market bunting, welcoming.",
        "refs": CAST,
        "caption": "Market day! The berry stand is open.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 52, "y": 14, "text": "I'd like 128 berries, please!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito looks over the whole stock: three big baskets, four banded bundles, two loose berries.",
        "scene": "SPRIGATITO the grass kitten stands on the counter surveying the whole stock laid out in "
                 "three neat groups: THREE big woven baskets of berries, FOUR small bundles of berries each "
                 "banded with a vine ribbon, and just TWO loose berries sitting by themselves. Sprigatito "
                 "counts thoughtfully, one paw raised.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 36, "y": 13, "text": "We have 342. So that's 342 take away 128 — start with the ONES!"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito stares at only two loose berries, ears drooping; Fuecoco nods toward the bundles.",
        "scene": "Close on SPRIGATITO looking down at just TWO lonely loose berries on the counter, ears "
                 "drooping, dismayed. The friendly red crocodile FUECOCO beside it nods encouragingly toward "
                 "the row of banded bundles nearby. QUAXLY waits politely at the counter edge.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 32, "y": 12, "text": "Only 2 loose berries… but Quaxly needs 8!"},
            {"speaker": "Fuecoco", "kind": "speech", "x": 72, "y": 20, "text": "Then go next door."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Fuecoco lifts one banded bundle of ten berries over the loose-berry tray, its ribbon half untied.",
        "scene": "FUECOCO the red crocodile lifts ONE bundle of berries (clearly banded with a vine ribbon) "
                 "off the stack and holds it above a small wooden tray holding only two loose berries. The "
                 "ribbon is half untied and trailing, the bundle about to come apart. SPRIGATITO watches "
                 "closely at the lower-left. Keep the entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "2 ones isn't enough to take 8 from. Open ONE ten and pour it into the ones.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 38, "y": 13, "text": "One ten is just ten ones wearing a ribbon. Untie it!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "The ribbon is off and ten berries tumble into the tray with the two already there; the bundle stack is one shorter.",
        "scene": "The loosed ribbon flutters aside as TEN berries tumble down into the small wooden tray, "
                 "joining the two already there so the tray is now generously full. Behind, the row of banded "
                 "bundles is visibly ONE shorter than before, with a small gap where the opened bundle used "
                 "to sit. QUAXLY watches, delighted, at the lower-right. A soft glow follows the falling "
                 "berries. Keep the entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "1 ten becomes 10 ones. 2 + 10 = 12 ones, and the tens drop from 4 to 3.  12 - 8 = 4",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 34, "y": 13, "text": "Twelve! Now there's plenty!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "Quaxly's basket is full; what stays on the counter is two big baskets, one bundle and four loose berries.",
        "scene": "QUAXLY the duckling holds a comfortably full basket of berries at the lower-right, beaming. "
                 "What remains on the counter is clearly arranged: TWO big baskets, ONE banded bundle, and "
                 "FOUR loose berries. SPRIGATITO stands proudly beside the remaining stock at the lower-left. "
                 "Keep the entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "Now the rest.   TENS: 3 - 2 = 1     HUNDREDS: 3 - 1 = 2     342 - 128 = 214",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 13, "text": "214 berries left!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco explains the two-way trade; Sprigatito and Quaxly listen side by side.",
        "scene": "FUECOCO sits tall behind the counter as if sharing a rule, flame tail raised gently. "
                 "SPRIGATITO and QUAXLY sit side by side listening, both nodding with dawning understanding. "
                 "Warm mentor moment.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 44, "y": 12, "text": "Adding, you bundle ten and carry it UP. Subtracting, you untie a ten and pour it DOWN."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "The three friends share berries across the market counter at midday, the stall cheerful and busy.",
        "scene": "Midday at the busy market stall. SPRIGATITO, FUECOCO and QUAXLY share berries together "
                 "across the wooden counter, all three happy and companionable, baskets and bundles neatly "
                 "arranged around them. Warm, cheerful, contented finale.",
        "refs": CAST,
        "caption": "★ REGROUPING RULE (SUBTRACTION) ★   If a place is too small to take from, open ONE of the next-bigger place. Ten comes down into that column — then subtract.",
        "bubbles": [
            {"speaker": "Quaxly", "kind": "speech", "x": 28, "y": 16, "text": "Untie a ten, pour it down… Quaxly can regroup! To be continued →"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch3 L2 'Quaxly Unties a Bundle' subtraction-with-regrouping manga."

    CHAPTER = 3
    LESSON_NUMBER = 2
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_sub_regroup_1"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
