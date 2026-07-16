"""Build the "Pikachu's Catching Contest" comparison word-problems lesson (Ch2 L10)
as an illustrated manga (idempotent). Bright Pokemon anime style; a fresh cast
(Pikachu & Bulbasaur) after the Chi's Sweet Home part-whole lessons.

Two modes (mirrors generate_chi_word_problems):

* ``--dry-run`` (default when no Replicate token): (re)creates the panel +
  speech-bubble STRUCTURE only, with placeholder art boxes — no token, no cost.
* full run (needs ``REPLICATE_API_TOKEN``): draws the Pikachu/Bulbasaur sheets
  (into this lesson's dir) and each panel using them as reference images, saves
  JPEGs under ``static/manga/pokemon-comparison/``, and links them. Commit the
  JPEGs (+ the char sheets, so the cast can be reused) to persist, then use
  ``--link-only`` on prod.

Examples:
    python manage.py generate_pokemon_comparison --dry-run --curriculum 6
    python manage.py generate_pokemon_comparison --curriculum 6                 # real art
    python manage.py generate_pokemon_comparison --only 4,6 --curriculum 6      # redraw bars
    python manage.py generate_pokemon_comparison --link-only --curriculum 1     # prod, no cost
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from tutor import imagegen
from tutor.models import MangaPanel, Material

ART_DIR = "manga/pokemon-comparison"
# This lesson introduces a new cast, so its character sheets live in (and are
# drawn into) its own dir; commit them so a future Pokemon lesson can reuse them.
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

# Character prompts — drawn once into this lesson's dir, then reused as reference
# sheets so Pikachu & Bulbasaur stay identical across every panel.
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
        "alt": "A sunny Pokémon Catching Contest field after a big swarm; Pikachu and Bulbasaur stand with two bulging catch bags.",
        "scene": "Wide establishing shot of a bright, grassy Catching Contest field on a sunny day, a "
                 "few tall-grass patches around. The yellow mouse PIKACHU and the blue-green BULBASAUR "
                 "stand together on the grass beside TWO plump, clearly separate catch bags stuffed full. "
                 "Cheerful, celebratory, energetic.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "The Catching Contest! What a swarm today!",
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 50, "y": 14, "text": "Pika-pika! We caught SO many today!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Pikachu looks between the two catch bags, one paw raised, thinking hard.",
        "scene": "PIKACHU looks back and forth between the two stuffed catch bags on the grass, one small "
                 "paw raised as if counting, brow furrowed in happy concentration. BULBASAUR sits nearby, "
                 "calm and patient.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 33, "y": 13, "text": "I caught 340, Bulba caught 210… how many MORE did I catch?"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Bulbasaur lifts a vine like a teacher; Pikachu looks up eagerly.",
        "scene": "The calm BULBASAUR extends one green vine from its bulb as if explaining, wise and kind; "
                 "PIKACHU looks up eagerly, ears perked, ready to learn. Warm mentor moment.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Bulbasaur", "kind": "speech", "x": 42, "y": 13, "text": "Line them up, Pika — a longer bar, a shorter bar. The gap is the difference."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Two long rows of Poké Balls laid on the grass, aligned at the left; the top row (Pikachu's) clearly longer than the bottom row (Bulbasaur's), with the extra Poké Balls at the right set slightly apart.",
        "scene": "TWO long horizontal rows of classic red-and-white Poké Balls laid neatly on the grass, "
                 "one directly ABOVE the other, BOTH starting aligned at the exact same left edge. The TOP "
                 "row is clearly LONGER; the BOTTOM row is clearly SHORTER. The extra Poké Balls sticking "
                 "out past the end of the bottom row, at the right, are set slightly apart as a distinct "
                 "little cluster. The two rows look like two measuring bars of different lengths. PIKACHU "
                 "stands proudly at the lower-left beside the top row; BULBASAUR at the lower-right by the "
                 "bottom row. Keep the entire upper third of the frame as open, empty blue sky.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "Both amounts known — line up the bars. The extra part is the difference. Subtract.   340 − 210 = 130",
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 28, "y": 13, "text": "130 more! I caught 130 more than Bulba!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Bulbasaur proudly shows its full catch bag; Pikachu's bag is hidden under a big leaf.",
        "scene": "BULBASAUR proudly nudges its own stuffed catch bag forward with a vine; PIKACHU's catch "
                 "bag sits nearby half-hidden under a big green leaf, a mystery. BULBASAUR looks playful, "
                 "posing a riddle; PIKACHU tilts its head, curious.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Bulbasaur", "kind": "speech", "x": 40, "y": 13, "text": "I caught 210, and you caught 130 MORE. How many did YOU catch?"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "Two Poké Ball bars: Bulbasaur's shorter row with a glowing cluster of extra Poké Balls added onto its right end, reaching the same length as Pikachu's longer row above.",
        "scene": "TWO horizontal rows of red-and-white Poké Balls again, aligned at the left. The BOTTOM "
                 "row is BULBASAUR's shorter row; onto its RIGHT END is added a small GLOWING, sparkling "
                 "cluster of extra Poké Balls, so the bottom row plus the glowing extra together reach the "
                 "SAME length as the TOP row (PIKACHU's longer row). BULBASAUR at the lower-left, PIKACHU "
                 "peeking eagerly at the lower-right. Keep the entire upper third as open, empty blue sky.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "One amount and the difference known — add them to find the bigger.   210 + 130 = 340",
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 70, "y": 13, "text": "340! Adding the extra gives my total!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Bulbasaur, warm and wise, shares a rule; Pikachu nods proudly.",
        "scene": "BULBASAUR sits tall and warm as if sharing a rule, vine raised gently; PIKACHU nods "
                 "proudly beside it, eyes shining with understanding. Gentle and encouraging.",
        "refs": ["pikachu", "bulbasaur"],
        "bubbles": [
            {"speaker": "Bulbasaur", "kind": "speech", "x": 42, "y": 13, "text": "Both known? Subtract for the gap. Know the gap? Add for the other."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset over the contest field with fluttering ribbons; Pikachu snuggled happily beside Bulbasaur with their catch bags.",
        "scene": "Warm sunset glow over the Catching Contest field, a couple of prize ribbons fluttering on "
                 "a post. PIKACHU snuggled happily and sleepily beside big friendly BULBASAUR; their two "
                 "catch bags rest side by side nearby. Tender, cheerful, content finale.",
        "refs": ["pikachu", "bulbasaur"],
        "caption": "★ PIKA'S RULE ★   Line up two bars. The gap is the difference. Both amounts → SUBTRACT. One amount + the gap → ADD. A ? is the number we're looking for.",
        "bubbles": [
            {"speaker": "Pikachu", "kind": "speech", "x": 26, "y": 16, "text": "Line up the bars… then compare! Pika can do comparing! To be continued →"},
        ],
    },
]


class Command(BaseCommand):
    help = "Build the 'Pikachu's Catching Contest' comparison-bar word-problems manga (panels + bubbles + art)."

    def add_arguments(self, parser):
        parser.add_argument("--material", type=int, help="Material id to build panels for.")
        parser.add_argument("--curriculum", type=int, help="Curriculum id whose Ch2 L10 manga to build.")
        parser.add_argument("--for-user", help="Username whose Dimensions Math 3A Ch2 L10 manga to build.")
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
        """Draw (once) and reuse the Pikachu & Bulbasaur sheets so the cast stays
        identical across panels. Reuses committed sheets on a rerun; only draws a
        sheet that is genuinely missing."""
        shared_dir = os.path.join(settings.BASE_DIR, "static", CHAR_SHEET_DIR)
        out_dir = os.path.join(settings.BASE_DIR, "static", ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        sheets = {}
        for name, prompt in CHARACTERS.items():
            shared = os.path.join(shared_dir, f"char-{name}.jpg")
            if not regenerate and os.path.exists(shared):
                sheets[name] = shared
                continue
            path = os.path.join(out_dir, f"char-{name}.jpg")
            if regenerate or not os.path.exists(path):
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
            chapter__curriculum=curriculum, chapter__number=2, number=10,
        ).first()
        material = Material.objects.filter(
            lesson=lesson, skill_type=Material.SKILL_MANGA,
        ).first()
        if material is None:
            raise CommandError(
                "No manga material found for Ch2 L10. Run seed_violet_word_problems_2 first."
            )
        return material
