"""Build the "Chi Counts the Cats" sum-and-difference lesson as an illustrated
manga (idempotent). Cozy, soft-color art in the spirit of Chi's Sweet Home.

Two modes (mirrors generate_number_besties):

* ``--dry-run`` (default when no Replicate token): (re)creates the panel +
  speech-bubble STRUCTURE only, with placeholder art boxes — no token, no cost.
* full run (needs ``REPLICATE_API_TOKEN``): generates a character sheet per cat,
  then draws each panel with those sheets as reference images for consistency,
  saves the PNGs under ``static/manga/chi-sum-difference/``, and links them.
  Commit the generated PNGs to persist them, then use ``--link-only`` on prod.

Examples:
    python manage.py generate_chi_sum_difference --dry-run --for-user localron
    python manage.py generate_chi_sum_difference --for-user localron            # real art
    python manage.py generate_chi_sum_difference --link-only --for-user ronald  # prod, no cost
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from tutor import imagegen
from tutor.models import MangaPanel, Material

ART_DIR = "manga/chi-sum-difference"

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
    "high detail. IMPORTANT: do not draw any text, letters, numbers as writing, "
    "speech bubbles, or captions — leave clear open space for bubbles to be added later."
)

# Character sheets — generated once, then used as reference for every panel so
# Chi and Blackie stay consistent.
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
        "alt": "A sunny park: a group of cats resting by a big tree, a few more by a little pond, with the kitten Chi looking around in wonder.",
        "scene": "Wide establishing shot of a sunny park: a group of cats resting under a big "
                 "leafy tree on one side, and a few more cats by a small pond on the other. "
                 "The tiny grey kitten CHI in the foreground looks around in wonder. Peaceful, warm afternoon.",
        "refs": ["chi"],
        "caption": "One warm afternoon in the park. Cats everywhere!",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 45, "y": 16, "text": "So many kitties! Chi never saw so many!"},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Chi counts on her little paws while Blackie sits calmly beside her.",
        "scene": "CHI the kitten sits up and reaches out one front paw, pointing toward a small "
                 "group of cats resting in the background as if counting them one by one; her head "
                 "is tilted and her eyes are wide with happy concentration. The big calm black cat "
                 "BLACKIE sits beside her, watching patiently. The counting gesture is clear and obvious.",
        "refs": ["chi", "blackie"],
        "bubbles": [
            {"speaker": "Chi", "kind": "thought", "x": 27, "y": 15, "text": "Eight kitties here… five kitties there…"},
            {"speaker": "Chi", "kind": "speech", "x": 27, "y": 44, "text": "How many all together? Chi wants to know!"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Blackie lifts a paw as if teaching; Chi looks up eagerly.",
        "scene": "The wise black cat BLACKIE lifts one paw as if teaching, kind and patient; "
                 "little CHI looks up at him eagerly. Warm mentor moment.",
        "refs": ["chi", "blackie"],
        "bubbles": [
            {"speaker": "Blackie", "kind": "speech", "x": 30, "y": 15, "text": "Two ways, Chi. Put 'em together… or line 'em up."},
            {"speaker": "Blackie", "kind": "speech", "x": 68, "y": 74, "text": "Draw a bar. You'll see."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "All the park cats gathered together in one happy group around Chi and Blackie.",
        "scene": "A SMALL, easily countable gathering of cats on the grass: a group of about eight "
                 "cats on the left and a group of about five cats on the right, gently coming together, "
                 "with CHI and BLACKIE among them. Keep the two groups distinguishable and the total "
                 "small — around a dozen cats, NOT a big crowd. Cheerful and cozy.",
        "refs": ["chi", "blackie"],
        "caption": "Put the parts together — the whole is the SUM.   [ 8 ][ 5 ] = 13",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 32, "y": 14, "text": "Thirteen! Chi counted thirteen kitties!"},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Blackie gently points at the ground as if at a diagram; Chi leans in, curious.",
        "scene": "BLACKIE gently taps the ground with a paw as if pointing at an invisible diagram; "
                 "CHI leans in, curious and delighted. Teaching moment, cozy.",
        "refs": ["chi", "blackie"],
        "caption": "Whole 13, one part 8 — take it away:   13 − 8 = 5",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 66, "y": 15, "text": "Ohh! Five kitties by the pond!"},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Two small bowls of fish-shaped treats, one fuller than the other; Chi pouts, Blackie is amused.",
        "scene": "Two small cat-food bowls of little fish-shaped treats on the ground: one fuller, "
                 "one with fewer. CHI looks at them with a cute pout; BLACKIE beside her, amused and kind.",
        "refs": ["chi", "blackie"],
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 28, "y": 15, "text": "Blackieee… you got MORE fishies than Chi!"},
            {"speaker": "Blackie", "kind": "speech", "x": 70, "y": 15, "text": "Line 'em up. Count what's extra."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_WIDE,
        "alt": "A longer row of eight fish treats above a shorter row of five, ends matched, the extra three at the end gently glowing.",
        "scene": "Two neat rows on the ground: a longer row of EIGHT little fish-shaped treats above "
                 "a shorter row of FIVE, their left ends carefully lined up so the extra three treats "
                 "at the end of the top row clearly stick out and gently glow. CHI and BLACKIE watch "
                 "from the side. Tidy, clear, cute.",
        "refs": ["chi", "blackie"],
        "caption": "Line them up — the extra piece is the DIFFERENCE.   8 − 5 = 3",
        "bubbles": [
            {"speaker": "Blackie", "kind": "speech", "x": 28, "y": 16, "text": "Three more for me. Three fewer for you. Here — share."},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Sunset: Chi snuggled sleepily against Blackie, two little bowls side by side.",
        "scene": "Warm sunset glow. CHI the kitten snuggled sleepily and happily against big "
                 "BLACKIE; two little bowls sit side by side nearby. Tender, cozy, content finale.",
        "refs": ["chi", "blackie"],
        "caption": "★ CHI'S RULE ★   Put groups TOGETHER to find the SUM.   Line groups UP to find the DIFFERENCE.   A ? is just the number we're looking for.",
        "bubbles": [
            {"speaker": "Chi", "kind": "speech", "x": 25, "y": 40, "text": "Sums and diff'rences… Chi loves counting kitties! To be continued →"},
        ],
    },
]


class Command(BaseCommand):
    help = "Build the 'Chi Counts the Cats' sum-and-difference manga (panels + bubbles + art)."

    def add_arguments(self, parser):
        parser.add_argument("--material", type=int, help="Material id to build panels for.")
        parser.add_argument("--for-user", help="Username whose Dimensions Math 3A Ch2 L8 manga to build.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Only (re)build panel + bubble structure with placeholder art (no token needed).",
        )
        parser.add_argument(
            "--regenerate", action="store_true",
            help="Regenerate art even for panels that already have an image.",
        )
        parser.add_argument(
            "--link-only", action="store_true",
            help="Point panels at the committed static art without generating "
                 "(use on prod after the PNGs are deployed — no token, no cost).",
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

        sheets = {} if (dry_run or link_only) else self._generate_character_sheets(options["regenerate"])

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
            if not dry_run and not link_only and (options["regenerate"] or not panel.has_art):
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
        """Save generated COLOR art web-lean: capped width; JPEG for panels
        (much smaller than PNG for full-color art), PNG only if a .png path is given."""
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
        return f"{spec['scene']} {STYLE}"

    def _generate_character_sheets(self, regenerate):
        """Generate (or reuse) each cat's character sheet; return {name: local_path}."""
        import os

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
        import os

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
        if options.get("for_user"):
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user = User.objects.get(username=options["for_user"])
            except User.DoesNotExist:
                raise CommandError(f"User '{options['for_user']}' does not exist.")
            curriculum = Curriculum.objects.filter(parent=user, name="Dimensions Math 3A").first()
            if curriculum is None:
                raise CommandError(f"No 'Dimensions Math 3A' curriculum found for {user.username}.")
            lesson = Lesson.objects.filter(
                chapter__curriculum=curriculum, chapter__number=2, number=8,
            ).first()
            material = Material.objects.filter(
                lesson=lesson, skill_type=Material.SKILL_MANGA,
            ).first()
            if material is None:
                raise CommandError(
                    "No manga material found. Run seed_violet_sum_difference first."
                )
            return material
        raise CommandError("Provide --material <id> or --for-user <username>.")
