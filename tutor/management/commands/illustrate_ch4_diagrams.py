"""Give Chapter 4's counting panels real art without letting the count drift.

WHY BOTH. draw_ch4_diagrams settled the maths: the panels the lesson depends on
are drawn from the numbers by tutor/mangadiagram.py, so the picture can never
disagree with its caption. It also made them the worst-looking panels in every
lesson — a flat sky, a flat lawn, a row of clip-art berries, and none of the
cast. The parent approved the lessons without seeing them side by side and, once
he did, called them terrible. He was right.

Handing the diagram to the image model and asking it to paint AROUND the
objects was tried first. It is very good at that — and it still moved the
count: on the misconception panel (2 baskets of 4, a cup of 5) it emptied the
cup on one attempt and stacked SIX in it on the next. That is the exact failure
the diagrams exist to prevent, so it cannot be the mechanism.

So the split is: the model paints the SCENE — the shed, the orchard, the dock,
the cast at the edges, the light — with the stage left deliberately bare, and
the objects are laid on top from the same deterministic renderer as before, on
a transparent layer. Counts stay exact by construction. The composite keeps the
house rules: nothing in the upper third (balloons), no text, no fruit anywhere
in the scene that a child could count by mistake.

    python manage.py illustrate_ch4_diagrams --list
    python manage.py illustrate_ch4_diagrams --only 5            # one lesson
    python manage.py illustrate_ch4_diagrams --panel l5:5        # one panel
    python manage.py illustrate_ch4_diagrams --recomposite       # no model call

Scenes are cached under _illustrate_cache/ so a re-composite (a renderer fix,
a shadow tweak) costs nothing; --redraw-scene throws a cached scene away.
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFilter

from tutor import imagegen
from tutor import mangadiagram as dg

from ._manga_art import STYLE
from .draw_ch4_diagrams import PANELS

SPAN_ASPECT = {"full": "21:9", "wide": "16:9", "normal": "4:3", "tall": "3:4"}

# The character sheets every Chapter 4 lesson reuses.
SHEETS = {
    "sprigatito": "manga/pokemon-regrouping/char-sprigatito.jpg",
    "fuecoco": "manga/pokemon-regrouping/char-fuecoco.jpg",
    "quaxly": "manga/pokemon-sub-regroup-1/char-quaxly.jpg",
    "pawmi": "manga/pokemon-estimating-1/char-pawmi.jpg",
    "lechonk": "manga/pokemon-estimating-1/char-lechonk.jpg",
}

# What every scene prompt insists on, whatever the panel. The objects go onto
# the middle of the stage afterwards, so the stage must be empty, the cast must
# hug the edges, and nothing countable may appear anywhere else.
STAGE_RULES = (
    " STAGING RULES, all mandatory. THE STAGE: the flat ground surface described "
    "above is one smooth, level, open PLANE seen from slightly above; it fills the "
    "entire BOTTOM 40% of the frame from the left edge to the right edge, and its "
    "far edge sits about 60% of the way down the frame — a wide floor, NOT a narrow "
    "ledge, table-edge or strip. Its whole MIDDLE, from the left quarter to the right "
    "quarter, is COMPLETELY BARE and EMPTY: nothing on it at all, no fruit, no "
    "baskets, no cups, no tools, no marks, no shadows of things; objects will be "
    "placed there later. Every character stays at the EXTREME LEFT or EXTREME RIGHT "
    "EDGE of the frame and LOW, never in the middle and never overlapping the bare "
    "stage. There is NO fruit of any kind ANYWHERE in the picture — no berries on "
    "any tree, bush, cart, basket or ground — nothing a child could count by "
    "mistake. No people. No signs. NO roof, canopy, awning, beams, posts or any "
    "overhead structure: the scene is under open sky. Keep the entire UPPER THIRD "
    "of the frame as calm, plain, empty sky with nothing in it — no heads, ears, "
    "branches, beams or objects. Draw NO text, numbers, letters, speech bubbles or "
    "captions."
)

SHED = (
    "the packing yard of a sunny Paldea berry orchard in warm late-afternoon light, "
    "plain leafy fruit-free trees far behind under open sky; the flat ground surface "
    "is the yard's smooth, level, bare packed-earth floor, and a low plain wooden "
    "packing counter stands off at one EDGE of the frame, never across the middle"
)
DIRT = (
    "a sunlit berry orchard under open sky; the flat ground surface is a wide, "
    "smooth, level patch of bare packed orchard dirt, with plain leafy fruit-free "
    "trees far behind"
)

# (slug, order) -> prose for the scene only. Counts are never mentioned: the
# renderer supplies every object, and the model is told to draw none.
SCENES = {
    ("pokemon-ch4-l5-remainders", 1): (SHED + ". At the far LEFT edge the tidy blue-headed "
        "duckling QUAXLY stands behind the counter and the grass kitten SPRIGATITO peeks "
        "over its front corner; at the far RIGHT edge the plump piglet LECHONK dozes "
        "against a crate. A stack of EMPTY round baskets and one small plain tin cup sit "
        "at the very left end of the counter, tight against the edge.",
        ["quaxly", "sprigatito", "lechonk"]),
    ("pokemon-ch4-l5-remainders", 2): (SHED + ". At the far LEFT edge the grass kitten "
        "SPRIGATITO leans over the counter's corner, eager; at the far RIGHT edge the "
        "tiny electric mouse PAWMI wrings its paws with tiny sparks, ears flat and "
        "alarmed, while the chunky red crocodile FUECOCO sits calmly just behind it, "
        "unbothered.",
        ["sprigatito", "pawmi", "fuecoco"]),
    ("pokemon-ch4-l5-remainders", 5): (SHED + ", with a plain EMPTY wooden cart, nothing "
        "loaded on it, parked behind the counter at the left. At the far LEFT edge the tiny "
        "electric mouse PAWMI stands in front of the counter looking enormously pleased "
        "with itself, paws spread; at the far RIGHT edge the blue-headed duckling QUAXLY "
        "leans in with one narrowed, doubtful eye. Comic, suspicious mood.",
        ["pawmi", "quaxly"]),
    ("pokemon-ch4-l5-remainders", 6): (SHED + ". The chunky red crocodile FUECOCO is "
        "SMALL and tucked tight into the bottom-LEFT corner, half hidden behind the "
        "counter's end, looking thoughtfully toward the middle; the grass kitten "
        "SPRIGATITO is SMALL and tucked tight into the bottom-RIGHT corner, pointing "
        "toward the middle with wide eyes. Both leave the whole width between them empty.",
        ["fuecoco", "sprigatito"]),

    ("pokemon-ch4-l6-odd-even", 2): ("a sunlit wooden dock over calm blue water in a "
        "Paldea harbour under open sky, small empty rowing boats moored beyond; the flat "
        "ground surface is the dock's wide, level, smooth plank deck. At the far LEFT edge the grass kitten SPRIGATITO "
        "stands with one front paw resting on a tipped-over EMPTY woven basket lying on "
        "its side; at the far RIGHT edge the tiny electric mouse PAWMI looks worried, "
        "paws clasped.",
        ["sprigatito", "pawmi"]),

    ("pokemon-ch4-l7-bar-model-word-problems", 1): ("an orchard at dawn under open sky, low golden light; the flat ground surface "
        "is a wide, smooth, level, bare dirt clearing. Every bush, hedge and tree behind "
        "it is plain solid green leaf — NO dots, NO berries, NO fruit, NO flowers on any "
        "of them, not even tiny ones. A small EMPTY wooden hand-wagon sits far back at "
        "the LEFT edge. The blue-headed duckling QUAXLY and the grass kitten SPRIGATITO "
        "are SMALL and tucked tight into the bottom-LEFT corner; the plump piglet LECHONK "
        "dozes SMALL and tucked tight into the bottom-RIGHT corner. Nothing and nobody "
        "else stands anywhere near the edges; the whole width between the two corners "
        "is empty ground.",
        ["quaxly", "sprigatito", "lechonk"]),
    ("pokemon-ch4-l7-bar-model-word-problems", 4): (DIRT + ". At the far LEFT edge the "
        "blue-headed duckling QUAXLY stands proudly with a stick in one wing; at the far "
        "RIGHT edge the grass kitten SPRIGATITO and the red crocodile FUECOCO watch.",
        ["quaxly", "sprigatito", "fuecoco"]),
    ("pokemon-ch4-l7-bar-model-word-problems", 5): ("a sunlit orchard under open sky, comic and affectionate; the flat ground "
        "surface is wide, smooth, level, bare short grass; every tree and bush is plain "
        "solid green leaf with NO dots, NO fruit and NO flowers on it. "
        "At the far LEFT edge the grass kitten SPRIGATITO is mid-pounce after a small "
        "fluttering butterfly, and two EMPTY woven baskets lie tumbled on their sides "
        "right at the left edge; at the far RIGHT edge the blue-headed duckling QUAXLY "
        "throws its wings up in dismay and the plump piglet LECHONK lies unbothered.",
        ["sprigatito", "quaxly", "lechonk"]),
    ("pokemon-ch4-l7-bar-model-word-problems", 6): (DIRT + ". At the far LEFT edge the "
        "red crocodile FUECOCO gestures toward the middle with one claw; at the far RIGHT "
        "edge the tiny electric mouse PAWMI watches with a happy spark.",
        ["fuecoco", "pawmi"]),

    ("pokemon-ch4-l8-times-as-many", 1): ("a sunny orchard packing yard under open sky, rows of plain leafy fruit-free "
        "trees behind; the flat ground surface is the yard's wide, level, bare "
        "packed-earth floor, and a low sorting bench stands off at one edge. At the far LEFT edge the red crocodile "
        "FUECOCO stands beside the bench; at the far RIGHT edge the blue-headed duckling "
        "QUAXLY stands with a small EMPTY wooden barrow, and the tiny electric mouse "
        "PAWMI and the plump piglet LECHONK crowd low beside it.",
        ["fuecoco", "quaxly", "pawmi", "lechonk"]),
    ("pokemon-ch4-l8-times-as-many", 4): ("a sunny orchard packing yard under open sky; the flat ground surface is the "
        "yard's wide, level, bare packed-earth floor, plain leafy fruit-free trees far "
        "behind. At the far LEFT edge the grass kitten "
        "SPRIGATITO peers along the bench; at the far RIGHT edge the blue-headed "
        "duckling QUAXLY stands with one wing raised as if explaining.",
        ["sprigatito", "quaxly"]),

    ("pokemon-ch4-l9-two-step", 1): ("a hilltop orchard at warm golden hour under open sky; the flat ground "
        "surface is wide, smooth, level, bare short grass; plain leafy fruit-free trees "
        "sit far behind and low, none reaching the top third. The blue-headed duckling "
        "QUAXLY and the tiny electric mouse PAWMI are SMALL and tucked tight into the "
        "bottom-LEFT corner; the plump piglet LECHONK dozes SMALL and tucked tight into "
        "the bottom-RIGHT corner. Nothing and nobody else stands anywhere near the "
        "edges; the whole width between the two corners is empty ground.",
        ["quaxly", "pawmi", "lechonk"]),
    ("pokemon-ch4-l9-two-step", 4): (DIRT + ". At the far LEFT edge the red crocodile "
        "FUECOCO watches the middle; at the far RIGHT edge the grass kitten SPRIGATITO "
        "stands with both paws hidden behind its back, ears flat, looking away "
        "innocently and guiltily.",
        ["fuecoco", "sprigatito"]),
    ("pokemon-ch4-l9-two-step", 5): (DIRT + "; the bare dirt is GENEROUS — it fills the "
        "bottom HALF of the frame, its far edge no higher than halfway down, and the "
        "trees are pushed back small above it. At the far LEFT edge the tiny electric "
        "mouse PAWMI bounces with happy sparks; at the far RIGHT edge the blue-headed "
        "duckling QUAXLY watches approvingly.",
        ["pawmi", "quaxly"]),
    ("pokemon-ch4-l9-two-step", 6): (DIRT + ". At the far LEFT edge the blue-headed "
        "duckling QUAXLY points toward the middle, delighted; at the far RIGHT edge the "
        "grass kitten SPRIGATITO looks sheepish, ears back.",
        ["quaxly", "sprigatito"]),
}

CACHE = os.path.join(settings.BASE_DIR, "_illustrate_cache")


class _KeepAlpha:
    """Lets a builder call ``.convert("RGB")`` on its composite without
    flattening our transparent layer onto black."""

    def __init__(self, image):
        self.image = image

    def convert(self, _mode):
        return self.image


class _ImageProxy:
    new = staticmethod(Image.new)

    @staticmethod
    def alpha_composite(a, b):
        return _KeepAlpha(Image.alpha_composite(a, b))


def render_layer(build, span):
    """The diagram's OBJECTS on a transparent layer — same builder, same
    counts — with a soft real shadow instead of a painted lawn disc."""
    def clear_canvas(span="full"):
        img = Image.new("RGBA", dg.SPAN_SIZE[span], (0, 0, 0, 0))
        return img, ImageDraw.Draw(img)

    def soft_shadow(d, cx, cy, rx, ry=None):
        ry = ry if ry is not None else max(rx // 3, 4)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(0, 0, 0, 70))

    saved = (dg._canvas, dg._shadow, dg.Image)
    dg._canvas, dg._shadow, dg.Image = clear_canvas, soft_shadow, _ImageProxy
    try:
        layer = build(span)
    finally:
        dg._canvas, dg._shadow, dg.Image = saved
    if isinstance(layer, _KeepAlpha):
        layer = layer.image
    return layer.convert("RGBA")


#: How much of the frame's width the objects may use, by span. A full-width
#: panel's bar model runs edge to edge and lands on top of the cast in the
#: corners; pulled in to four-fifths it clears them and is still large.
INSET = {"full": 0.80, "wide": 0.90, "normal": 1.0, "tall": 1.0}

#: manga.css shows a full-span panel in a 16/6 box and the art is 21:9, so
#: `object-fit: cover` hides the top and bottom 29px. The objects are anchored
#: above that line so a bar model's bottom border is never the part that is
#: cropped. (Wide panels lose 69px each side the same way; their inset leaves
#: too little room to lift, and only basket shadows fall in the hidden band.)
CSS_HIDDEN_BOTTOM = {"full": 29}

#: Per-panel overrides of INSET. Six baskets across a wide panel reach the
#: corners even at nine-tenths, and land on whoever is standing there.
INSET_OVERRIDE = {("pokemon-ch4-l7-bar-model-word-problems", 1): 0.78}


def composite(scene_path, build, span, key=None):
    w, h = dg.SPAN_SIZE[span]
    scene = Image.open(scene_path).convert("RGB").resize((w, h), Image.LANCZOS)
    layer = render_layer(build, span)
    factor = INSET_OVERRIDE.get(key, INSET.get(span, 1.0))
    if factor < 1.0:
        lw, lh = round(w * factor), round(h * factor)
        layer = layer.resize((lw, lh), Image.LANCZOS)
        # Anchored bottom-centre so the objects stay standing on the ground,
        # lifted clear of the band the page's CSS crops away.
        offset = ((w - lw) // 2, h - lh - CSS_HIDDEN_BOTTOM.get(span, 0))
    else:
        offset = (0, 0)
    scene.paste(layer, offset, layer)
    return scene.filter(ImageFilter.SMOOTH)


class Command(BaseCommand):
    help = "Paint real scenes behind Chapter 4's exact diagram panels."

    def add_arguments(self, parser):
        parser.add_argument("--list", action="store_true")
        parser.add_argument("--only", help="Comma-separated lesson numbers, e.g. '5,9'.")
        parser.add_argument("--panel", help="One panel, e.g. 'l5:5'.")
        parser.add_argument("--recomposite", action="store_true",
                            help="Reuse every cached scene; call the model for none.")
        parser.add_argument("--redraw-scene", action="store_true",
                            help="Ignore the cached scene and paint a fresh one.")
        parser.add_argument("--delay", type=float, default=8.0)

    def handle(self, *args, **options):
        only = {int(x) for x in (options.get("only") or "").split(",") if x.strip().isdecimal()}
        one = None
        if options.get("panel"):
            lesson, order = options["panel"].lower().lstrip("l").split(":")
            one = (int(lesson), int(order))

        chosen = []
        for slug, order, span, build, note in PANELS:
            lesson = int(slug.split("-l")[1].split("-")[0])
            if (slug, order) not in SCENES:
                continue
            if only and lesson not in only:
                continue
            if one and (lesson, order) != one:
                continue
            chosen.append((slug, lesson, order, span, build, note))

        if options["list"]:
            for slug, lesson, order, span, _b, note in chosen:
                self.stdout.write(f"  L{lesson} p{order}  {span:6}  {note}")
            self.stdout.write(self.style.SUCCESS(f"{len(chosen)} panels."))
            return
        if not chosen:
            raise CommandError("Nothing selected.")
        if options["recomposite"] and options["redraw_scene"]:
            raise CommandError("--recomposite reuses cached scenes and "
                               "--redraw-scene deletes them; pick one.")
        if not options["recomposite"] and not imagegen.is_configured():
            raise CommandError("REPLICATE_API_TOKEN is not set; use --recomposite "
                               "to rebuild from cached scenes only.")

        os.makedirs(CACHE, exist_ok=True)
        for slug, lesson, order, span, build, note in chosen:
            scene_path = os.path.join(CACHE, f"{slug}-p{order}.png")
            if options["redraw_scene"] and os.path.exists(scene_path):
                os.remove(scene_path)
            if not os.path.exists(scene_path):
                if options["recomposite"]:
                    self.stdout.write(self.style.WARNING(
                        f"  L{lesson} p{order}: no cached scene, skipped"))
                    continue
                self._paint_scene(slug, order, span, scene_path)
                self._throttle(options["delay"])
            out = os.path.join(settings.BASE_DIR, "static", "manga", slug, f"p{order}.jpg")
            composite(scene_path, build, span, key=(slug, order)).save(
                out, format="JPEG", quality=88, optimize=True, progressive=True)
            self.stdout.write(f"  L{lesson} p{order} -- {note}")
        self.stdout.write(self.style.SUCCESS(f"Illustrated {len(chosen)} panels."))

    def _paint_scene(self, slug, order, span, path):
        prose, refs = SCENES[(slug, order)]
        prompt = (f"Illustrated scene: {prose}." + STAGE_RULES + " " + STYLE)
        sheets = [os.path.join(settings.BASE_DIR, "static", SHEETS[r]) for r in refs]
        self.stdout.write(f"  painting scene for {slug} p{order}…")
        data = imagegen.generate_image(
            prompt, reference_paths=sheets,
            extra_input={"aspect_ratio": SPAN_ASPECT[span], "output_format": "png"})
        with open(path, "wb") as fh:
            fh.write(data)

    @staticmethod
    def _throttle(delay):
        import time

        if delay > 0:
            time.sleep(delay)
