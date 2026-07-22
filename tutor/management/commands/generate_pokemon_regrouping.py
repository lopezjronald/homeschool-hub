"""Build the "Sprigatito's Berry Bundle" addition-with-regrouping lesson (Ch3 L1)
as an illustrated manga (idempotent). Bright Pokemon anime style; a fresh Gen 9
cast (Sprigatito & Fuecoco) — its own character sheets, drawn once into this
lesson's dir and committed so a future Gen-9 lesson can reuse them.

Two modes (mirrors generate_pokemon_two_step):

* ``--dry-run`` (default when no Replicate token): (re)creates the panel +
  speech-bubble STRUCTURE only, with placeholder art boxes — no token, no cost.
* full run (needs ``REPLICATE_API_TOKEN``): draws the Sprigatito/Fuecoco sheets
  (into this lesson's dir) and each panel using them as reference images, saves
  JPEGs under ``static/manga/pokemon-regrouping/``, and links them. Commit the
  JPEGs (+ the char sheets) to persist, then use ``--link-only`` on prod.

Examples:
    python manage.py generate_pokemon_regrouping --dry-run --curriculum 6
    python manage.py generate_pokemon_regrouping --curriculum 6                 # real art
    python manage.py generate_pokemon_regrouping --only 4,5 --curriculum 6      # redraw regroup panels
    python manage.py generate_pokemon_regrouping --link-only --curriculum 1     # prod, no cost
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from tutor import imagegen
from tutor.models import MangaPanel, Material

ART_DIR = "manga/pokemon-regrouping"
# New Gen 9 cast: draw its sheets into this lesson's own dir; commit them so a
# future Gen-9 lesson can reuse them.
CHAR_SHEET_DIR = "manga/pokemon-regrouping"

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

# Character prompts — drawn once into this lesson's dir, then reused as reference
# sheets so the Gen 9 pair stay identical across every panel.
CHARACTERS = {
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
}

# 8 panels. `refs` lists which character sheets to condition on. `bubbles`
# positions are percentages (0-100). The math lives in `caption`, the story in
# `bubbles` — the art stays text-free.
PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A sunny berry field; the grass kitten Sprigatito and the red croc Fuecoco sit beside two big baskets of berries.",
        "scene": "Wide establishing shot of a sunny berry field with rolling hills. The cream-green grass "
                 "kitten SPRIGATITO and the chunky red crocodile FUECOCO sit together on the grass beside "
                 "TWO big woven baskets brimming with round red berries. Cheerful, summery, cozy.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "A big berry-picking day in Paldea!",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 50, "y": 14, "text": "We picked SO many berries today!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Sprigatito looks between the two berry baskets, one paw raised, thinking.",
        "scene": "SPRIGATITO the grass kitten looks back and forth between the two full berry baskets, one "
                 "small paw raised as if counting, head tilted in happy concentration. FUECOCO sits nearby, "
                 "calm and friendly.",
        "refs": ["sprigatito", "fuecoco"],
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 33, "y": 13, "text": "I picked 156, Fuecoco picked 128… how many ALL TOGETHER?"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco lifts its little flame tail like a teacher; Sprigatito looks up eagerly.",
        "scene": "The friendly red crocodile FUECOCO lifts its small flame-tipped tail as if explaining, warm "
                 "and clever; SPRIGATITO looks up eagerly, ears perked, ready to learn. Cozy mentor moment.",
        "refs": ["sprigatito", "fuecoco"],
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 42, "y": 13, "text": "Add place by place — start with the ONES. But watch — they can OVERFLOW!"},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "A big pile of loose berries pooled on the grass — clearly more than a small ten-frame can hold.",
        "scene": "On the grass, a small empty wooden tray marked as the 'ones' spot (a little square tray that "
                 "obviously only fits about ten berries) is OVERFLOWING: a generous pile of loose round red "
                 "berries spills over its edges — clearly far more than the tray can hold. SPRIGATITO looks "
                 "surprised at the overflowing pile at the lower-left; FUECOCO gestures at it from the "
                 "lower-right. Keep the entire upper third of the frame as open, empty blue sky.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "6 ones + 8 ones = 14 ones. Ten or more — time to REGROUP!",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 13, "text": "Fourteen ones! That's too many to keep loose!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_FULL,
        "alt": "Ten loose berries tied into one neat bundle being carried toward the tens, with four loose berries left behind.",
        "scene": "A clear 'bundling' moment: exactly TEN loose red berries are tied together into ONE neat "
                 "bundle (banded with a little vine or ribbon) and FUECOCO slides that single bundle toward "
                 "a taller 'tens' basket on the right; back at the 'ones' tray on the left, just a FEW loose "
                 "berries remain. A soft glow highlights the new bundle. SPRIGATITO watches, delighted, at "
                 "the lower-left. Keep the entire upper third of the frame as open, empty blue sky.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "Trade 10 ones for 1 TEN. Write 4 in the ones, carry the 1 ten over.",
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 40, "y": 13, "text": "Bundle ten, carry one! Four ones stay behind."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "Neat rows of ten-bundles and a couple of big hundred-baskets pushed together into one big total pile of berries.",
        "scene": "The finished total on the grass: two big hundred-baskets side by side, then a tidy row of "
                 "several ten-bundles of berries, then a few loose berries — all gathered together into one "
                 "big cheerful heap. SPRIGATITO and FUECOCO stand together behind it, thrilled and proud. "
                 "Keep the entire upper third of the frame as open, empty blue sky.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "Now add the rest.   156 + 128 = 284",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 30, "y": 13, "text": "284 berries all together!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Fuecoco, warm and wise, shares a rule; Sprigatito nods proudly.",
        "scene": "FUECOCO sits tall and warm as if sharing a rule, flame tail raised gently; SPRIGATITO nods "
                 "proudly beside it, eyes shining with understanding. Gentle and encouraging.",
        "refs": ["sprigatito", "fuecoco"],
        "bubbles": [
            {"speaker": "Fuecoco", "kind": "speech", "x": 42, "y": 13, "text": "If a place makes 10 or more — bundle ten and carry it to the next place!"},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset over the berry field; Sprigatito snuggled happily beside Fuecoco with one big basket of berries.",
        "scene": "Warm sunset glow over the berry field. SPRIGATITO the grass kitten snuggled happily and "
                 "sleepily beside the friendly red crocodile FUECOCO; one big basket brimming with berries "
                 "rests beside them. Tender, cheerful, content finale.",
        "refs": ["sprigatito", "fuecoco"],
        "caption": "★ REGROUPING RULE ★   Add place by place. When a column makes 10 or more, bundle 10 and CARRY it to the next place. Ones → tens → hundreds.",
        "bubbles": [
            {"speaker": "Sprigatito", "kind": "speech", "x": 26, "y": 16, "text": "Bundle ten, carry one… Sprigatito can regroup! To be continued →"},
        ],
    },
]


class Command(BaseCommand):
    help = "Build the 'Sprigatito's Berry Bundle' addition-with-regrouping manga (panels + bubbles + art)."

    def add_arguments(self, parser):
        parser.add_argument("--material", type=int, help="Material id to build panels for.")
        parser.add_argument("--curriculum", type=int, help="Curriculum id whose Ch3 L1 manga to build.")
        parser.add_argument("--for-user", help="Username whose Dimensions Math 3A Ch3 L1 manga to build.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Only (re)build panel + bubble structure with placeholder art (no token needed).",
        )
        parser.add_argument(
            "--regenerate", action="store_true",
            help="Regenerate art even for panels that already have an image.",
        )
        parser.add_argument(
            "--only", help="Comma-separated panel orders to (re)draw, e.g. '4' or '4,5'.",
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
        """Draw the Sprigatito & Fuecoco sheets into this lesson's dir once, then
        reuse them so the Gen 9 pair stay identical across every panel."""
        out_dir = os.path.join(settings.BASE_DIR, "static", ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        sheets = {}
        for name, prompt in CHARACTERS.items():
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
            chapter__curriculum=curriculum, chapter__number=3, number=1,
        ).first()
        material = Material.objects.filter(
            lesson=lesson, skill_type=Material.SKILL_MANGA,
        ).first()
        if material is None:
            raise CommandError(
                "No manga material found for Ch3 L1. Run seed_violet_regrouping first."
            )
        return material
