"""Build the "Pikachu's Two-Step Catch" 2-step word-problems lesson (Ch2 L11) as an
illustrated manga (idempotent). Bright Pokemon anime style; REUSES the committed
Pikachu & Bulbasaur character sheets from the Ch2 L10 comparison lesson so the
cast stays identical across the Pokemon series.

Two modes (mirrors generate_pokemon_comparison):

* ``--dry-run`` (default when no Replicate token): (re)creates the panel +
  speech-bubble STRUCTURE only, with placeholder art boxes — no token, no cost.
* full run (needs ``REPLICATE_API_TOKEN``): draws each panel using the existing
  Pikachu/Bulbasaur sheets as reference images, saves JPEGs under
  ``static/manga/pokemon-two-step/``, and links them. Commit the JPEGs to
  persist, then use ``--link-only`` on prod.

Examples:
    python manage.py generate_pokemon_two_step --dry-run --curriculum 6
    python manage.py generate_pokemon_two_step --curriculum 6                 # real art
    python manage.py generate_pokemon_two_step --only 4,6 --curriculum 6      # redraw bars
    python manage.py generate_pokemon_two_step --link-only --curriculum 1     # prod, no cost
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from tutor import imagegen
from tutor.models import MangaPanel, Material

ART_DIR = "manga/pokemon-two-step"
# Reuse the committed Pikachu & Bulbasaur sheets from the Ch2 L10 lesson so the
# cast stays visually identical across the Pokemon series.
CHAR_SHEET_DIR = "manga/pokemon-comparison"

# Match each panel's on-page shape so the art isn't cropped awkwardly.
SPAN_ASPECT = {
    MangaPanel.SPAN_NORMAL: "4:3",
    MangaPanel.SPAN_WIDE: "16:9",
    MangaPanel.SPAN_FULL: "21:9",
    MangaPanel.SPAN_TALL: "3:4",
}

# Shared bright look so every panel matches. The model must NOT draw text — our
# speech bubbles + math captions are overlaid in the template.
STYLE = (
    "bright, cheerful anime illustration in the style of the classic Pokémon "
    "animated series: bold clean black outlines, vivid saturated colors, smooth "
    "cel shading, big expressive eyes, dynamic and playful, kid-friendly, high "
    "detail. IMPORTANT: do NOT draw any text, letters, numbers, writing, speech "
    "bubbles, word balloons, or captions anywhere in the image."
)

# Composition rule for PANELS only: reserve empty space at the TOP for speech
# balloons and keep the characters low, so the overlay lands on open background.
PANEL_COMPOSITION = (
    " COMPOSITION: stage the characters in the LOWER two-thirds of the frame and keep "
    "the UPPER third as calm, plain, low-detail open background (bright sky or soft "
    "distant scenery) — generous empty negative space reserved for speech balloons. Do "
    "NOT let any character's head rise into the top third of the frame; leave that band clean and empty."
)

# Fallback character prompts — only used if the shared committed sheet is missing.
CHARACTERS = {
    "pikachu": (
        "Character reference sheet, front and 3/4 views, of PIKACHU the Pokémon: a small, "
        "round, chubby YELLOW mouse creature with long pointed ears tipped with black, two "
        "red circular cheeks, short brown stripes on the lower back, short arms and legs, and "
        "a flat lightning-bolt-shaped tail; cheerful, energetic, big friendly eyes. " + STYLE
    ),
    "bulbasaur": (
        "Character reference sheet, front and 3/4 views, of BULBASAUR the Pokémon: a small "
        "blue-green (turquoise) quadruped creature resembling a friendly young dinosaur or "
        "toad, with darker teal spots, red eyes, small pointed ears, stubby legs with small "
        "claws, and a large green PLANT BULB on its back; calm, kind, gentle. " + STYLE
    ),
}

# 8 panels. `refs` lists which character sheets to condition on. `bubbles`
# positions are percentages (0-100). kind: speech|thought|caption|sfx. The math
# lives in `caption`, the story in `bubbles` — the art stays text-free.
PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A sunny Pokémon Catching Contest field; Pikachu and Bulbasaur stand with two full catch bags as a contest judge looks on.",
        "scene": "Wide establishing shot of a bright, grassy Catching Contest field on a sunny day. The "
                 "yellow mouse PIKACHU and the blue-green BULBASAUR stand together beside TWO plump, clearly "
                 "separate catch bags. A cheerful contest judge (a friendly human referee in a cap) stands "
                 "to one side with a clipboard as if asking a question. Celebratory, energetic.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "Back at the Catching Contest — and today there's a TRICKY question!",
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 50, "y": 14, "text": "Pika! The judge wants our TOTAL, all together!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pikachu scratches its head, puzzling over the two catch bags.",
        "scene": "PIKACHU scratches its head with one paw, looking back and forth between the two stuffed "
                 "catch bags on the grass, brow furrowed in puzzled concentration. BULBASAUR sits nearby, "
                 "calm and patient.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 33, "y": 13, "text": "I caught 250… Bulba caught 100 FEWER… how many ALL TOGETHER?"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Bulbasaur raises two vines, one for each step, teaching; Pikachu looks up eagerly.",
        "scene": "The calm BULBASAUR extends TWO green vines from its bulb, holding them up side by side as "
                 "if counting 'step one, step two', wise and kind; PIKACHU looks up eagerly, ears perked, "
                 "ready to learn. Warm mentor moment.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Bulbasaur", "kind": "speech", "x": 42, "y": 13, "text": "Two-step question! First find MY number… then put both together."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Step 1 comparison bars: two rows of Poké Balls aligned at the left, Pikachu's top row longer than Bulbasaur's shorter bottom row, the missing gap at the right marked as unknown.",
        "scene": "TWO long horizontal rows of classic red-and-white Poké Balls laid neatly on the grass, one "
                 "directly ABOVE the other, BOTH starting aligned at the exact same left edge. The TOP row "
                 "(Pikachu's) is clearly LONGER; the BOTTOM row (Bulbasaur's) is clearly SHORTER, ending a "
                 "little sooner. The empty gap at the right end of the bottom row, where it falls short of "
                 "the top row, is left clearly open. The two rows look like two measuring bars of different "
                 "lengths. PIKACHU stands proudly at the lower-left by the top row; BULBASAUR at the "
                 "lower-right by the bottom row. Keep the entire upper third of the frame as open, empty blue sky.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "Step 1 — Bulbasaur caught 100 FEWER. Compare and subtract.   250 − 100 = 150",
        "bubbles": [
            {"speaker": "Bulbasaur", "kind": "speech", "x": 30, "y": 13, "text": "So Bulba caught 150. Now we know BOTH numbers!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pikachu's eyes light up, then it points a paw back toward the judge's question.",
        "scene": "PIKACHU's eyes light up with an 'aha' spark, one paw raised; then it points back over its "
                 "shoulder as if remembering the judge's question. BULBASAUR beside it, encouraging. Bright, "
                 "lively.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 34, "y": 13, "text": "150 for Bulba! But the judge asked ALL TOGETHER… one more step!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "Step 2 part-whole bar: Pikachu's group of Poké Balls and Bulbasaur's group pushed together into one long combined row forming the total.",
        "scene": "TWO groups of red-and-white Poké Balls pushed together end-to-end into ONE long combined "
                 "row on the grass: PIKACHU's group on the LEFT half and BULBASAUR's group on the RIGHT half, "
                 "touching in the middle to form a single long total bar (a soft glow highlights where the "
                 "two groups join into one whole). PIKACHU at the lower-left, BULBASAUR at the lower-right, "
                 "both delighted. Keep the entire upper third of the frame as open, empty blue sky.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "Step 2 — now put BOTH parts together. Add.   250 + 150 = 400",
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 70, "y": 13, "text": "400! We caught four hundred all together!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Bulbasaur, warm and wise, shares a rule; Pikachu nods proudly.",
        "scene": "BULBASAUR sits tall and warm as if sharing a rule, one vine raised gently; PIKACHU nods "
                 "proudly beside it, eyes shining with understanding. Gentle and encouraging.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Bulbasaur", "kind": "speech", "x": 42, "y": 13, "text": "Find the hidden middle number FIRST — then answer what was really asked."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset over the contest field with a big prize ribbon; Pikachu snuggled happily beside Bulbasaur with their two catch bags.",
        "scene": "Warm sunset glow over the Catching Contest field, a big prize ribbon fluttering on a post. "
                 "PIKACHU snuggled happily and sleepily beside big friendly BULBASAUR; their two catch bags "
                 "rest side by side nearby. Tender, cheerful, content finale.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "★ PIKA'S TWO-STEP RULE ★   Step 1: find the hidden number (draw a bar). Step 2: use it to answer the real question (draw another bar). One step at a time!",
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 26, "y": 16, "text": "One step, then the next… Pika can do two-step problems! To be continued →"},
        ],
    },
]


class Command(BaseCommand):
    help = "Build the 'Pikachu's Two-Step Catch' 2-step word-problems manga (panels + bubbles + art)."

    def add_arguments(self, parser):
        parser.add_argument("--material", type=int, help="Material id to build panels for.")
        parser.add_argument("--curriculum", type=int, help="Curriculum id whose Ch2 L11 manga to build.")
        parser.add_argument("--for-user", help="Username whose Dimensions Math 3A Ch2 L11 manga to build.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Only (re)build panel + bubble structure with placeholder art (no token needed).",
        )
        parser.add_argument(
            "--regenerate", action="store_true",
            help="Regenerate art even for panels that already have an image.",
        )
        parser.add_argument(
            "--only", help="Comma-separated panel orders to (re)draw, e.g. '4' or '4,6'.",
        )
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

        sheets = {} if (dry_run or link_only) else self._character_sheets(regenerate=False)

        built = 0
        for spec in PANELS:
            defaults = {
                "span": spec["span"],
                "alt": spec["alt"],
                "caption": spec.get("caption", ""),
                "bubbles": spec["bubbles"],
                "prompt": self._panel_prompt(spec),
            }
            if link_only:
                defaults["image_path"] = f"{ART_DIR}/p{spec['order']}.jpg"
            panel, _ = MangaPanel.objects.update_or_create(
                material=material, order=spec["order"], defaults=defaults,
            )
            should_draw = options["regenerate"] or (spec["order"] in only) or not panel.has_art
            if not dry_run and not link_only and should_draw:
                self._draw_panel(panel, spec, sheets)
            built += 1

        # Drop any stale panels beyond the current script.
        MangaPanel.objects.filter(material=material).exclude(
            order__in=[p["order"] for p in PANELS]
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
        """Save generated COLOR art web-lean: capped width; JPEG for panels."""
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

    def _character_sheets(self, regenerate):
        """Reuse the committed Pikachu & Bulbasaur sheets from the L10 lesson so the
        cast stays identical across the series; only draw one if it is truly missing."""
        shared_dir = os.path.join(settings.BASE_DIR, "static", CHAR_SHEET_DIR)
        out_dir = os.path.join(settings.BASE_DIR, "static", ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        sheets = {}
        for name, prompt in CHARACTERS.items():
            shared = os.path.join(shared_dir, f"char-{name}.jpg")
            if os.path.exists(shared):
                sheets[name] = shared
                continue
            # Fallback: draw into this lesson's dir if the shared sheet is absent.
            path = os.path.join(out_dir, f"char-{name}.jpg")
            if regenerate or not os.path.exists(path):
                self.stdout.write(f"  drawing character sheet: {name}… (shared sheet missing)")
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

        out_dir = os.path.join(settings.BASE_DIR, "static", ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        filename = f"p{spec['order']}.jpg"
        self._save_optimized(data, os.path.join(out_dir, filename))
        panel.image_path = f"{ART_DIR}/{filename}"
        panel.save(update_fields=["image_path"])
        self._throttle()

    def _resolve_material(self, options):
        if options.get("material"):
            try:
                return Material.objects.get(pk=options["material"])
            except Material.DoesNotExist:
                raise CommandError(f"Material #{options['material']} does not exist.")

        curriculum = None
        if options.get("curriculum"):
            try:
                curriculum = Curriculum.objects.get(pk=options["curriculum"])
            except Curriculum.DoesNotExist:
                raise CommandError(f"Curriculum #{options['curriculum']} does not exist.")
        elif options.get("for_user"):
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user = User.objects.get(username=options["for_user"])
            except User.DoesNotExist:
                raise CommandError(f"User '{options['for_user']}' does not exist.")
            curriculum = Curriculum.objects.filter(parent=user, name="Dimensions Math 3A").first()
            if curriculum is None:
                raise CommandError(f"No 'Dimensions Math 3A' curriculum found for {user.username}.")
        else:
            raise CommandError("Provide --material <id>, --curriculum <id>, or --for-user <username>.")

        lesson = Lesson.objects.filter(
            chapter__curriculum=curriculum, chapter__number=2, number=11,
        ).first()
        material = Material.objects.filter(
            lesson=lesson, skill_type=Material.SKILL_MANGA,
        ).first()
        if material is None:
            raise CommandError(
                "No manga material found for Ch2 L11. Run seed_violet_two_step first."
            )
        return material
