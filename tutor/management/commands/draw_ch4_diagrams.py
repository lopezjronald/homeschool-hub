"""Redraw Chapter 4's counting panels as exact diagrams.

The image model cannot count: two passes left 25 of 72 panels contradicting their
own captions (16 berries under "4 x 3 = 12", 48 under "6 rows of 7", 14 under
"13 berries came in"). Those panels carry the maths, so they are drawn from the
numbers instead -- see tutor/mangadiagram.py. Character and story panels keep
their illustrated art.

Each entry below names the panel and the exact quantities its caption asserts,
so the picture and the caption cannot drift apart again.

    python manage.py draw_ch4_diagrams --list     # what would be drawn
    python manage.py draw_ch4_diagrams            # write the JPEGs
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand

from tutor import mangadiagram as dg

# (slug, panel, span, builder, human note tying it to the caption)
PANELS = [
    # ---- L1 Equal Groups and Arrays ----
    ("pokemon-ch4-l1-equal-groups", 4, "normal",
     lambda s: dg.equal_groups([3, 3, 4, 3], span=s),
     "3 + 3 + 4 + 3 = 13 -- one basket is the odd one out"),
    ("pokemon-ch4-l1-equal-groups", 5, "full",
     lambda s: dg.array(3, 4, span=s),
     "4 rows of 3 -> 4 x 3 = 12 (upright: 3 across, 4 down)"),

    # ---- L2 Strategies for Finding the Product ----
    ("pokemon-ch4-l2-product-strategies", 1, "wide",
     lambda s: dg.array(7, 6, span=s),
     "the rack holds 6 rows of 7 = 42"),
    ("pokemon-ch4-l2-product-strategies", 5, "full",
     lambda s: dg.split_array(7, 5, 1, span=s),
     "5 rows of 7 = 35, plus one more row of 7 -> 42"),
    ("pokemon-ch4-l2-product-strategies", 6, "full",
     lambda s: dg.split_array(8, 2, 2, span=s),
     "double it: 2 x 8 = 16, and 16 + 16 = 32"),

    # ---- L3 Two Ways to Divide ----
    ("pokemon-ch4-l3-division-meanings", 7, "full",
     lambda s: dg.array(4, 3, span=s),
     "3 rows of 4 = 12"),
    ("pokemon-ch4-l3-division-meanings", 8, "full",
     lambda s: dg.array(3, 4, span=s),
     "the tray TURNED -- 4 x 3 = 12, and it must not look like p7"),

    # ---- L4 Zero and One ----
    ("pokemon-ch4-l4-zero-and-one", 4, "full",
     lambda s: dg.equal_groups([0] * 5, span=s),
     "five baskets, all flipped EMPTY -- the setup for 5 x 0"),
    ("pokemon-ch4-l4-zero-and-one", 5, "full",
     lambda s: dg.two_sets([0] * 5, [], span=s),
     "5 x 0 = 0 (five empty baskets) | 0 x 7 = 0 (no groups at all -- bare)"),
    ("pokemon-ch4-l4-zero-and-one", 7, "full",
     lambda s: dg.zero_vs_pile(6, 6, span=s),
     "0 / 6 = 0 (six empty cups) | 6 / 0 -- the six berries still sit there"),

    # ---- L5 Division with Remainders ----
    ("pokemon-ch4-l5-remainders", 1, "wide",
     lambda s: dg.heap(13, span=s, cols=7),
     "13 berries came in on the last cart"),
    ("pokemon-ch4-l5-remainders", 2, "normal",
     lambda s: dg.equal_groups([4, 4, 4], span=s),
     "every basket the SAME size -- exactly 4 in each"),
    ("pokemon-ch4-l5-remainders", 5, "full",
     lambda s: dg.groups_and_leftover(2, 4, 5, span=s),
     "Pawmi's WRONG try: 2 baskets of 4, and 5 still in the cup -- is 2 R 5 right?"),
    ("pokemon-ch4-l5-remainders", 6, "full",
     lambda s: dg.groups_and_leftover(2, 4, 5, span=s, show_slot=True),
     "the same 2 R 5, held against an empty basket: 5 is NOT smaller than 4"),

    # ---- L6 Odd and Even ----
    ("pokemon-ch4-l6-odd-even", 2, "normal",
     lambda s: dg.heap(8, span=s, cols=8),
     "eight LOOSE berries -- will everybody find a buddy?"),

    # ---- L7 Bar Models ----
    ("pokemon-ch4-l7-bar-model-word-problems", 1, "wide",
     lambda s: dg.equal_groups([0] * 6, span=s),
     "six baskets still TO FILL -- empty, five will go in each"),
    ("pokemon-ch4-l7-bar-model-word-problems", 4, "full",
     lambda s: dg.bar_model(6, 5, span=s),
     "6 units of 5 -> 6 x 5 = 30"),
    ("pokemon-ch4-l7-bar-model-word-problems", 5, "full",
     lambda s: dg.heap(30, span=s, cols=10),
     "the 30 berries the bar just built"),
    ("pokemon-ch4-l7-bar-model-word-problems", 6, "full",
     lambda s: dg.bar_model(6, 5, span=s, highlight=0),
     "30 / 6 = 5 in each -- the same six sections, one lit"),

    # ---- L8 Times as Many ----
    ("pokemon-ch4-l8-times-as-many", 1, "wide",
     lambda s: dg.two_sets([4], [4, 4, 4], span=s),
     "Fuecoco's ONE basket of 4 | Quaxly's THREE -- 3 times as many"),
    ("pokemon-ch4-l8-times-as-many", 4, "full",
     lambda s: dg.compare_bars(4, 3, span=s),
     "two bars from the SAME left edge: 1 unit vs 3 copies"),

    # ---- L9 Two Steps in One Problem ----
    ("pokemon-ch4-l9-two-step", 1, "wide",
     lambda s: dg.equal_groups([6, 6, 6, 6], span=s),
     "four baskets, six berries in each"),
    ("pokemon-ch4-l9-two-step", 4, "full",
     lambda s: dg.equal_groups([6, 6, 6, 6], span=s),
     "4 groups of 6"),
    ("pokemon-ch4-l9-two-step", 5, "full",
     lambda s: dg.heap(24, span=s, cols=6),
     "STEP 1 -- one pile of 24, in rows of 6 so 6/12/18/24 is traceable"),
    ("pokemon-ch4-l9-two-step", 6, "full",
     lambda s: dg.take_away(24, 9, span=s, cols=8),
     "STEP 2 -- 24 - 9 = 15 left"),
]


class Command(BaseCommand):
    help = "Redraw Chapter 4's counting panels as exact, generated diagrams."

    def add_arguments(self, parser):
        parser.add_argument("--list", action="store_true",
                            help="Show what would be drawn without writing anything.")
        parser.add_argument("--only", help="Comma-separated lesson numbers, e.g. '5,9'.")

    def handle(self, *args, **options):
        only = {int(x) for x in (options.get("only") or "").split(",") if x.strip().isdecimal()}
        written = 0
        for slug, order, span, build, note in PANELS:
            lesson = int(slug.split("-l")[1].split("-")[0])
            if only and lesson not in only:
                continue
            path = os.path.join(settings.BASE_DIR, "static", "manga", slug, f"p{order}.jpg")
            if options["list"]:
                self.stdout.write(f"  L{lesson} p{order}  {span:6}  {note}")
                continue
            dg.save(build(span), path)
            written += 1
            self.stdout.write(f"  drew L{lesson} p{order} -- {note}")
        if options["list"]:
            self.stdout.write(self.style.SUCCESS(f"{len(PANELS)} diagram panels defined."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Drew {written} exact diagram panels. Re-run any time -- output is deterministic."
            ))
