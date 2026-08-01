"""Build the Ch3 L5 "How Close Is Close Enough?" estimating-differences manga.

Pawmi and Lechonk return from Lesson 4, so both character sheets are reused via
SHEET_DIRS and a full run draws only the eight panels.

Panels 4 and 6 are the lesson: the SAME two stacks, rendered coarse then fine.
They should look like two views of one thing, not two different scenes.

Examples:
    python manage.py generate_pokemon_estimating_2 --dry-run --curriculum 1
    python manage.py generate_pokemon_estimating_2 --curriculum 1              # real art
    python manage.py generate_pokemon_estimating_2 --only 4,6 --curriculum 1   # redraw the two roundings
    python manage.py generate_pokemon_estimating_2 --link-only --curriculum 1  # prod, no cost
"""

from tutor.models import MangaPanel

from ._manga_art import GEN9_SHEET_DIRS, MangaArtCommand, gen9

ART_DIR = "manga/pokemon-estimating-2"
CHARACTERS = gen9("pawmi", "lechonk")
CAST = ["pawmi", "lechonk"]

PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "The morning after the festival: a tall stack of leaflets on a table and a much smaller emptied pile beside it.",
        "scene": "Wide establishing shot the morning after a festival — bunting sagging, stalls being packed "
                 "up, soft early light. On a long wooden table sits a TALL neat stack of paper leaflets, and "
                 "beside it a much SMALLER emptied pile. The little orange-tan electric mouse PAWMI and the "
                 "plump grey-brown piglet LECHONK stand at the table. Calm, tidy-up mood.",
        "refs": CAST,
        "caption": "The morning after the festival. Time to tidy up.",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 50, "y": 13, "text": "We started with 812 flyers. We handed out 389."},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi eyes the leftover stack, whiskers twitching, daunted by the idea of counting it.",
        "scene": "Close on PAWMI the electric mouse eyeing the tall leftover stack of leaflets, whiskers "
                 "twitching, small paws raised, visibly daunted at the thought of counting them all one by "
                 "one. LECHONK stands calmly beside it.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 13, "text": "How many are LEFT? Do I have to count them ALL?"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi thinks it over with one paw on its chin; Lechonk waits.",
        "scene": "PAWMI sits back on its haunches with one small paw against its chin, thinking it over, ears "
                 "tilted. LECHONK the piglet waits patiently beside it, unhurried. Quiet, considering moment.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 34, "y": 12, "text": "I just need to know if there's enough for tomorrow…"},
            {"speaker": "Lechonk", "kind": "speech", "x": 74, "y": 20, "text": "Then estimate."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "The leaflet stacks simplify into big chunky blocks — eight on one side, four on the other.",
        "scene": "The leaflet stacks simplify into clean geometry: on the left, EIGHT big chunky identical "
                 "blocks stacked in a neat column; on the right, FOUR of the same big blocks. Everything "
                 "coarse, blocky, instantly countable, glowing softly. PAWMI looks satisfied at the "
                 "lower-left, LECHONK placid at the lower-right. Keep the entire upper third of the frame as "
                 "open, empty sky.",
        "refs": CAST,
        "caption": "Nearest HUNDRED:  812 → 800,  389 → 400.      800 - 400 = 400. About four hundred left.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 13, "text": "About 400! That's plenty for tomorrow!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Lechonk tilts its head, considering, one trotter raised.",
        "scene": "LECHONK the piglet tilts its head thoughtfully, one trotter half-raised as if adding a "
                 "footnote, expression mildly shrewd. PAWMI looks over, curious. Warm, conversational.",
        "refs": CAST,
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 44, "y": 12, "text": "Fast — but we pushed 389 all the way up to 400. Want CLOSER? Round smaller."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "The same two stacks resolve into finer detail — many thin slices instead of a few big blocks.",
        "scene": "The SAME two stacks from before resolve into finer detail: each big chunky block breaks "
                 "into many THIN neat slices, so both columns now read as fine-grained stacks rather than "
                 "coarse blocks — clearly the same two piles, seen more precisely. Crisp and detailed, "
                 "glowing softly. PAWMI leans in impressed at the lower-left, LECHONK at the lower-right. "
                 "Keep the entire upper third of the frame as open, empty sky.",
        "refs": CAST,
        "caption": "Nearest TEN:  812 → 810,  389 → 390.      810 - 390 = 420. Closer!",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 32, "y": 13, "text": "420! That took longer — but it's nearer."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pawmi and Lechonk count the real leftover stack together at the table.",
        "scene": "PAWMI and LECHONK count the real stack of leaflets together at the wooden table, PAWMI "
                 "flicking pages with a small paw, LECHONK watching. Companionable, focused, satisfying.",
        "refs": CAST,
        "caption": "The exact answer: 812 - 389 = 423",
        "bubbles": [
            {"speaker": "Lechonk", "kind": "speech", "x": 44, "y": 12, "text": "400 was close. 420 was closer. Round rough for fast, fine for near."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Pawmi and Lechonk sit happily on the tidy stack of leftover flyers in the afternoon sun.",
        "scene": "Afternoon sun over the packed-up festival ground. PAWMI the electric mouse and LECHONK the "
                 "piglet sit contentedly together on top of the tidy remaining stack of leaflets, relaxed and "
                 "pleased with themselves. Warm, golden, restful finale.",
        "refs": CAST,
        "caption": "★ CHOOSING YOUR ROUNDING ★   Hundreds is fastest. Tens is closest. Neither is wrong — pick the one that answers YOUR question.",
        "bubbles": [
            {"speaker": "Pawmi", "kind": "speech", "x": 28, "y": 16, "text": "Fast, or near. My choice! To be continued →"},
        ],
    },
]


class Command(MangaArtCommand):
    help = "Build the Ch3 L5 'How Close Is Close Enough?' estimating-differences manga."

    CHAPTER = 3
    LESSON_NUMBER = 5
    ART_DIR = ART_DIR
    SHEET_DIRS = GEN9_SHEET_DIRS
    SEED_COMMAND = "seed_violet_estimating_2"
    CHARACTERS = CHARACTERS
    PANELS = PANELS
