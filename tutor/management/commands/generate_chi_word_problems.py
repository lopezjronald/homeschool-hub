"""Build the "Chi Shares the Catch" part-whole word-problems lesson (Ch2 L9) as an
illustrated manga (idempotent). Cozy Chi's Sweet Home style; sequel to the Ch2 L8
sum/difference lesson, so it REUSES the committed Chi & Blackie character sheets
for a consistent cast.

Two modes (mirrors generate_chi_sum_difference):

* ``--dry-run`` (default when no Replicate token): (re)creates the panel +
  speech-bubble STRUCTURE only, with placeholder art boxes — no token, no cost.
* full run (needs ``REPLICATE_API_TOKEN``): draws each panel using the existing
  Chi/Blackie sheets as reference images, saves JPEGs under
  ``static/manga/chi-word-problems/``, and links them. Commit the JPEGs to
  persist, then use ``--link-only`` on prod.

Examples:
    python manage.py generate_chi_word_problems --dry-run --curriculum 6
    python manage.py generate_chi_word_problems --curriculum 6            # real art
    python manage.py generate_chi_word_problems --link-only --for-user ronald  # prod, no cost
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from tutor import imagegen
from tutor.models import MangaPanel, Material

ART_DIR = "manga/chi-word-problems"
# Reuse the committed Chi & Blackie sheets from the Ch2 L8 lesson so the cats stay
# visually identical across the series.
CHAR_SHEET_DIR = "manga/chi-sum-difference"

# Match each panel's on-page shape so the art isn't cropped awkwardly.
SPAN_ASPECT = {
    MangaPanel.SPAN_NORMAL: "4:3",
    MangaPanel.SPAN_WIDE: "16:9",
    MangaPanel.SPAN_FULL: "21:9",
    MangaPanel.SPAN_TALL: "3:4",
}

# Shared cozy look so every panel matches. The model must NOT draw text — our
# speech bubbles + math captions are overlaid in the template.
STYLE = (
    "soft, warm, wholesome COLOR illustration in the gentle style of a cozy "
    "Japanese picture-book about cats: rounded shapes, big expressive eyes, "
    "soft watercolor-like shading, pastel palette, kid-friendly and cheerful, "
    "high detail. IMPORTANT: do NOT draw any text, letters, numbers, writing, "
    "speech bubbles, word balloons, or captions anywhere in the image."
)

# Composition rule for PANELS only: reserve empty space at the TOP for speech
# balloons and keep the cats low, so the overlay lands on open background.
PANEL_COMPOSITION = (
    " COMPOSITION: stage the cats in the LOWER two-thirds of the frame and keep the "
    "UPPER third as calm, plain, low-detail open background (soft sky, a blank wall, "
    "or ceiling) — generous empty negative space reserved for speech balloons. Do NOT "
    "let any cat's head rise into the top third of the frame; leave that band clean and empty."
)

# Fallback character prompts — only used if a shared sheet is somehow missing.
CHARACTERS = {
    "chi": (
        "Character reference sheet, front and 3/4 views, of CHI: a tiny, adorable "
        "grey-and-white KITTEN with dark grey tabby stripes across her face, back "
        "and tail, a small pink nose, rounded ears, very big round expressive "
        "eyes, and a wide happy grin; bubbly, innocent, babyish. " + STYLE
    ),
    "blackie": (
        "Character reference sheet of BLACKIE: a large black TOMCAT with a bearlike "
        "build, a small white crescent-shaped marking under his neck, a short tail "
        "with a fluffy tip, and narrow eyes with thin slit pupils; stern and "
        "serious-looking but quietly kind. " + STYLE
    ),
}

# 8 panels. `refs` lists which character sheets to condition on. `bubbles`
# positions are percentages (0-100). kind: speech|thought|caption|sfx. The math
# lives in `caption`, the story in `bubbles` — the art stays text-free.
PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "A bright morning by a pond; the kitten Chi and the black tomcat Blackie sit beside two little piles of fish they caught.",
        "scene": "Wide establishing shot of a calm pond on a bright morning. The tiny grey kitten CHI "
                 "and the large black cat BLACKIE sit together on the grassy bank beside TWO small, "
                 "clearly separate piles of fresh fish they have caught. Peaceful, cheerful, cozy.",
        "refs": ["chi", "blackie"],
        "caption": "A bright morning by the pond. Two happy fishers!",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 50, "y": 14, "text": "We caught SO many fishies today!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Chi looks between the two fish piles, counting on a paw, head tilted.",
        "scene": "CHI the kitten looks back and forth between two clearly separate fish piles on the "
                 "grass, one small front paw raised as if counting, her head tilted with happy "
                 "concentration. BLACKIE sits nearby, calm and patient.",
        "refs": ["chi", "blackie"],
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 32, "y": 13, "text": "Chi caught six, Blackie caught eight… how many all together?"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Blackie lifts a paw as if teaching; Chi looks up eagerly.",
        "scene": "The wise black cat BLACKIE lifts one paw as if explaining, calm and kind; little CHI "
                 "looks up at him eagerly, ready to learn. Warm mentor moment.",
        "refs": ["chi", "blackie"],
        "bubbles": [
            {"speaker": "Blackie", "kind": "speech", "x": 40, "y": 13, "text": "A story with numbers? Draw a bar, Chi — two parts, one whole."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Two groups of fish on the grass — a smaller group of six on the left, a clearly bigger group of eight on the right — with Chi between them.",
        "scene": "On green grass, TWO clearly separate groups of fish with a wide gap between them. "
                 "The LEFT group has EXACTLY SIX fish arranged in two tidy rows of three, a clearly "
                 "SMALLER pile. The RIGHT group has EXACTLY EIGHT fish arranged in two tidy rows of "
                 "four, a clearly BIGGER pile. Draw each fish separately, fully visible, evenly spaced "
                 "and NOT overlapping, so every single fish is easy to count one by one. The right "
                 "group must look visibly larger than the left group. The grey kitten CHI sits in the "
                 "gap between the two groups looking delighted. Do NOT draw any extra fish — exactly "
                 "six on the left and exactly eight on the right, no more. Cheerful and cozy.",
        "refs": ["chi"],
        "caption": "Both parts known — the whole is the SUM. Add.   6 + 8 = 14",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 28, "y": 13, "text": "Fourteen fishies! We caught fourteen!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "A treat bowl with a few fish-shaped treats and some crumbs where others were nibbled; Chi looks worried-cute.",
        "scene": "A small cat-food bowl on the ground holding a few little fish-shaped treats, with a "
                 "few crumbs beside it showing some were nibbled away. CHI looks at the bowl with a cute, "
                 "slightly worried pout; BLACKIE beside her, calm.",
        "refs": ["chi", "blackie"],
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 33, "y": 13, "text": "Twelve treats… five got nibbled up… how many are LEFT?"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_FULL,
        "alt": "Blackie gently points at the treat bowl as if at a diagram; Chi leans in, curious and hopeful.",
        "scene": "BLACKIE gently taps the ground beside the treat bowl with a paw as if pointing at an "
                 "invisible diagram; CHI leans in, curious and hopeful. The bowl with a few treats sits "
                 "between them. Teaching moment, cozy.",
        "refs": ["chi", "blackie"],
        "caption": "Whole 12, one part 5 — find the missing PART. Take away.   12 − 5 = 7",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 70, "y": 13, "text": "Seven treats left! Phew!"},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Blackie, wise and warm, shares a rule; Chi nods proudly.",
        "scene": "BLACKIE sits tall and warm as if sharing a rule; little CHI nods proudly beside him, "
                 "eyes shining with understanding. Gentle and encouraging.",
        "refs": ["chi", "blackie"],
        "bubbles": [
            {"speaker": "Blackie", "kind": "speech", "x": 42, "y": 13, "text": "Looking for the WHOLE? Add. Looking for a PART? Take the known part away."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset: Chi snuggled sleepily against Blackie, the fish pile and treat bowl side by side.",
        "scene": "Warm sunset glow over the pond. CHI the kitten snuggled sleepily and happily against "
                 "big BLACKIE; a little pile of fish and the treat bowl sit side by side nearby. Tender, "
                 "cozy, content finale.",
        "refs": ["chi", "blackie"],
        "caption": "★ CHI'S RULE ★   Draw the bar. Whole = ADD the parts. A missing part = SUBTRACT. A ? is just the number we're looking for.",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 26, "y": 16, "text": "Draw the bar… then add or take away. Chi can do word problems! To be continued →"},
        ],
    },
]


class Command(BaseCommand):
    help = "Build the 'Chi Shares the Catch' part-whole word-problems manga (panels + bubbles + art)."

    def add_arguments(self, parser):
        parser.add_argument("--material", type=int, help="Material id to build panels for.")
        parser.add_argument("--curriculum", type=int, help="Curriculum id whose Ch2 L9 manga to build.")
        parser.add_argument("--for-user", help="Username whose Dimensions Math 3A Ch2 L9 manga to build.")
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
        """Reuse the committed Chi & Blackie sheets from the L8 lesson so the cats
        stay identical across the series; only draw one if it is genuinely missing."""
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
            chapter__curriculum=curriculum, chapter__number=2, number=9,
        ).first()
        material = Material.objects.filter(
            lesson=lesson, skill_type=Material.SKILL_MANGA,
        ).first()
        if material is None:
            raise CommandError(
                "No manga material found for Ch2 L9. Run seed_violet_word_problems_1 first."
            )
        return material
