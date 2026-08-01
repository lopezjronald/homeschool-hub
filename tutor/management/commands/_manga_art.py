"""Shared base for the ``generate_*`` manga-art commands.

Same three modes every lesson needs:

* ``--dry-run`` (the default with no Replicate token): builds the panel and
  speech-bubble STRUCTURE with placeholder art. No token, no cost.
* full run (needs ``REPLICATE_API_TOKEN``): draws any missing character sheets,
  then each panel conditioned on them, saves JPEGs under ``static/<ART_DIR>/``
  and links them. Commit the JPEGs to persist.
* ``--link-only``: point panels at the committed static art without drawing.
  This is the prod mode — no token, no cost.

A subclass supplies ART_DIR, CHARACTERS, PANELS and which lesson it belongs to.

Two things here are load-bearing rather than incidental:

* ``SHEET_DIRS`` lets a lesson reuse character sheets another lesson already
  committed. Redrawing a cast gives you a *different-looking* cast — the sheets
  are what keeps Sprigatito the same Sprigatito across lessons — and it costs
  money to become inconsistent.
* ``PANEL_COMPOSITION`` reserves empty space in the ART prompt. Balloons are
  positioned as percentages over the image, so the room for them has to be
  drawn in; nudging balloon coordinates after the fact only moves the collision.
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from curricula.models import Lesson
from tutor import imagegen
from tutor.models import MangaPanel, Material

from ._manga_seed import resolve_curriculum

SPAN_ASPECT = {
    MangaPanel.SPAN_NORMAL: "4:3",
    MangaPanel.SPAN_WIDE: "16:9",
    MangaPanel.SPAN_FULL: "21:9",
    MangaPanel.SPAN_TALL: "3:4",
}

STYLE = (
    "bright, cheerful anime illustration in the style of the classic Pokémon "
    "animated series: bold clean black outlines, vivid saturated colors, smooth "
    "cel shading, big expressive eyes, dynamic and playful, kid-friendly, high "
    "detail. IMPORTANT: do NOT draw any text, letters, numbers, writing, speech "
    "bubbles, word balloons, or captions anywhere in the image."
)

PANEL_COMPOSITION = (
    " COMPOSITION: stage the characters in the LOWER two-thirds of the frame and keep "
    "the UPPER third as calm, plain, low-detail open background (bright sky or soft "
    "distant scenery) — generous empty negative space reserved for speech balloons. Do "
    "NOT let any character's head rise into the top third of the frame; leave that band clean and empty."
)

# The Paldea (Gen 9) cast, shared across the Chapter 3 lessons. A lesson lists
# only the characters it actually stages; anyone whose sheet another lesson has
# already committed is reused rather than redrawn (see SHEET_DIRS), so listing a
# returning character here is free.
GEN9_CHARACTERS = {
    "sprigatito": (
        "Character reference sheet, front and 3/4 views, of SPRIGATITO the Pokémon (a "
        "Generation 9 grass-type starter): a small quadruped KITTEN creature with soft "
        "cream-and-pale-green fur, big round expressive eyes, a tiny pink nose, rounded "
        "ears, and a fluffy leaf-like green collar-ruff around its neck; cat-like, "
        "playful, mischievous and cute. " + STYLE
    ),
    "fuecoco": (
        "Character reference sheet, front and 3/4 views, of FUECOCO the Pokémon (a "
        "Generation 9 fire-type starter): a small, chunky, round crocodile creature with "
        "a bright RED body, a pale yellow belly and throat, a big rounded snout with a "
        "friendly toothy smile, short stubby legs, and a squarish reddish scale like a "
        "little pepper on top of its head; cheerful, easygoing, warm. " + STYLE
    ),
    "quaxly": (
        "Character reference sheet, front and 3/4 views, of QUAXLY the Pokémon (a "
        "Generation 9 water-type starter): a small tidy DUCKLING with white body "
        "feathers, a bright blue head and face, a neat swept blue quiff of feathers "
        "curling over its forehead like styled hair, a small orange bill and orange "
        "webbed feet, and a fluffy white ruff at its neck like a collar; poised, "
        "polite, a little dapper. " + STYLE
    ),
    "pawmi": (
        "Character reference sheet, front and 3/4 views, of PAWMI the Pokémon (a "
        "Generation 9 electric-type): a tiny round MOUSE creature with pale orange-tan "
        "fur, a cream belly, big round eyes, small rounded ears with yellow inner "
        "markings, round yellow electric cheek-pouches on its forepaws, and a short "
        "stubby tail; jittery, eager, endearingly anxious. " + STYLE
    ),
    "lechonk": (
        "Character reference sheet, front and 3/4 views, of LECHONK the Pokémon (a "
        "Generation 9 normal-type): a small plump PIGLET with grey-brown bristly fur, a "
        "paler cream underside, a large round pink snout, small dark eyes, floppy "
        "triangular ears and short stubby legs; placid, hungry, unbothered. " + STYLE
    ),
}

# Where Chapter 3's committed character sheets live, newest lessons last. Any
# lesson can point SHEET_DIRS at this to inherit every sheet drawn so far.
GEN9_SHEET_DIRS = [
    "manga/pokemon-regrouping",
    "manga/pokemon-sub-regroup-1",
    "manga/pokemon-sub-regroup-2",
    "manga/pokemon-estimating-1",
    "manga/pokemon-estimating-2",
    "manga/pokemon-ch3-word-problems",
]


def gen9(*names):
    """The character prompts for ``names`` — a lesson's cast, in one line."""
    return {name: GEN9_CHARACTERS[name] for name in names}


class MangaArtCommand(BaseCommand):
    """Build one manga lesson's panels, bubbles and art."""

    CHAPTER = 3
    LESSON_NUMBER = None
    ART_DIR = ""
    SEED_COMMAND = ""
    CHARACTERS = {}
    PANELS = []
    # Directories to look in for an already-committed character sheet, in order.
    # ART_DIR is always searched last, so a sheet this lesson drew itself wins
    # only when no earlier lesson has one.
    SHEET_DIRS = []

    def add_arguments(self, parser):
        parser.add_argument("--material", type=int, help="Material id to build panels for.")
        parser.add_argument("--curriculum", type=int, help="Curriculum id whose lesson to build.")
        parser.add_argument("--for-user", help="Username whose Dimensions Math 3A lesson to build.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Only (re)build panel + bubble structure with placeholder art (no token needed).",
        )
        parser.add_argument(
            "--regenerate", action="store_true",
            help="Regenerate art even for panels that already have an image.",
        )
        parser.add_argument("--only", help="Comma-separated panel orders to (re)draw, e.g. '4,5'.")
        parser.add_argument(
            "--link-only", action="store_true",
            help="Point panels at the committed static art without generating "
                 "(use on prod after the JPEGs are deployed — no token, no cost).",
        )
        parser.add_argument(
            "--delay", type=float, default=11.0,
            help="Seconds to wait between image requests (Replicate throttles while credit is low).",
        )

    def handle(self, *args, **options):
        material = self._resolve_material(options)
        self.delay = options["delay"]
        link_only = options["link_only"]
        dry_run = not link_only and (options["dry_run"] or not imagegen.is_configured())

        if dry_run and not options["dry_run"]:
            self.stdout.write(self.style.WARNING(
                "No REPLICATE_API_TOKEN set — building structure only (placeholder art)."
            ))

        only = {int(x) for x in (options.get("only") or "").split(",") if x.strip().isdigit()}
        sheets = {} if (dry_run or link_only) else self._character_sheets()

        built = 0
        for spec in self.PANELS:
            defaults = {
                "span": spec["span"],
                "alt": spec["alt"],
                "caption": spec.get("caption", ""),
                "bubbles": spec["bubbles"],
                "prompt": self._panel_prompt(spec),
            }
            if link_only:
                defaults["image_path"] = f"{self.ART_DIR}/p{spec['order']}.jpg"
            panel, _ = MangaPanel.objects.update_or_create(
                material=material, order=spec["order"], defaults=defaults,
            )
            should_draw = options["regenerate"] or (spec["order"] in only) or not panel.has_art
            if not dry_run and not link_only and should_draw:
                self._draw_panel(panel, spec, sheets)
            built += 1

        MangaPanel.objects.filter(material=material).exclude(
            order__in=[p["order"] for p in self.PANELS]
        ).delete()

        mode = "structure only" if dry_run else ("linked" if link_only else "with art")
        self.stdout.write(self.style.SUCCESS(
            f"Built {built} panels ({mode}) for Material #{material.pk} '{material.title}'."
        ))
        if dry_run:
            self.stdout.write(
                "Set REPLICATE_API_TOKEN and re-run without --dry-run to draw the panels."
            )

    # -- helpers ------------------------------------------------------------

    def _throttle(self):
        import time

        if self.delay > 0:
            time.sleep(self.delay)

    def _save_optimized(self, data, path, max_width=1100):
        import io

        from PIL import Image

        image = Image.open(io.BytesIO(data)).convert("RGB")
        if image.width > max_width:
            height = round(image.height * max_width / image.width)
            image = image.resize((max_width, height), Image.LANCZOS)
        if path.lower().endswith((".jpg", ".jpeg")):
            image.save(path, format="JPEG", quality=88, optimize=True, progressive=True)
        else:
            image.save(path, format="PNG", optimize=True)

    def _panel_prompt(self, spec):
        return f"{spec['scene']} {STYLE}{PANEL_COMPOSITION}"

    def _existing_sheet(self, name):
        """An already-committed sheet for ``name``, or None.

        Reuse beats redrawing on both axes: a redrawn cast looks different, and
        paying for that difference is the worst of both.
        """
        for directory in [*self.SHEET_DIRS, self.ART_DIR]:
            path = os.path.join(settings.BASE_DIR, "static", directory, f"char-{name}.jpg")
            if os.path.exists(path):
                return path
        return None

    def _character_sheets(self):
        out_dir = os.path.join(settings.BASE_DIR, "static", self.ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        sheets = {}
        for name, prompt in self.CHARACTERS.items():
            existing = self._existing_sheet(name)
            if existing:
                sheets[name] = existing
                continue
            path = os.path.join(out_dir, f"char-{name}.jpg")
            self.stdout.write(f"  drawing character sheet: {name}…")
            data = imagegen.generate_image(
                prompt, extra_input={"aspect_ratio": "3:4", "output_format": "png"},
            )
            self._save_optimized(data, path)
            self._throttle()
            sheets[name] = path
        return sheets

    def _draw_panel(self, panel, spec, sheets):
        refs = [sheets[name] for name in spec.get("refs", []) if name in sheets]
        self.stdout.write(f"  drawing panel {spec['order']}…")
        data = imagegen.generate_image(
            self._panel_prompt(spec),
            reference_paths=refs,
            extra_input={
                "aspect_ratio": SPAN_ASPECT.get(spec["span"], "4:3"),
                "output_format": "png",
            },
        )
        out_dir = os.path.join(settings.BASE_DIR, "static", self.ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        filename = f"p{spec['order']}.jpg"
        self._save_optimized(data, os.path.join(out_dir, filename))
        panel.image_path = f"{self.ART_DIR}/{filename}"
        panel.save(update_fields=["image_path"])
        self._throttle()

    def _resolve_material(self, options):
        if options.get("material"):
            try:
                return Material.objects.get(pk=options["material"])
            except Material.DoesNotExist:
                raise CommandError(f"Material #{options['material']} does not exist.")

        curriculum = resolve_curriculum(options)
        lesson = Lesson.objects.filter(
            chapter__curriculum=curriculum,
            chapter__number=self.CHAPTER,
            number=self.LESSON_NUMBER,
        ).first()
        material = Material.objects.filter(
            lesson=lesson, skill_type=Material.SKILL_MANGA,
        ).first()
        if material is None:
            raise CommandError(
                f"No manga material found for Ch{self.CHAPTER} L{self.LESSON_NUMBER}. "
                f"Run {self.SEED_COMMAND} first."
            )
        return material
