"""Build the "Number Besties" lesson as an illustrated manga (idempotent).

Two modes:

* ``--dry-run`` (default when no Replicate token): (re)creates the panel +
  speech-bubble STRUCTURE only. The page renders immediately as a real comic
  layout with placeholder art boxes — no token, no cost.
* full run (needs ``REPLICATE_API_TOKEN``): also generates a character sheet
  per hero, then draws each panel with those sheets as reference images for
  consistency, saves the PNGs under ``static/manga/number-besties/``, and links
  them to the panels. Commit the generated PNGs to persist them.

Examples:
    python manage.py generate_number_besties --dry-run --for-user ronald
    python manage.py generate_number_besties --for-user ronald            # real art
    python manage.py generate_number_besties --for-user ronald --regenerate
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from tutor import imagegen
from tutor.models import MangaPanel, Material

ART_DIR = "manga/number-besties"

# Shared look so every panel matches. The model must NOT draw text — our speech
# bubbles are overlaid in the template.
STYLE = (
    "black-and-white shonen manga panel, clean ink line art, screentone shading, "
    "dynamic expressive composition, kid-friendly, wholesome, high detail. "
    "IMPORTANT: do not draw any text, letters, numbers as writing, speech bubbles, "
    "or captions — leave clear space for bubbles to be added later."
)

# Character sheets — generated once, then used as reference for every panel.
CHARACTERS = {
    "98": (
        "Character reference sheet, front and 3/4 views, of NINETY-EIGHT: a brave "
        "young manga hero with spiky teal hair and an athletic hooded tunic bearing "
        "a large glowing golden emblem shaped like the numeral 98 on the chest; "
        "confident determined eyes. " + STYLE
    ),
    "2": (
        "Character reference sheet of TWO: a small energetic manga sidekick with "
        "short amber hair and round cheeks, wearing a bright green scarf with a "
        "round badge marked 2; mischievous cheerful grin. " + STYLE
    ),
    "3": (
        "Character reference sheet of THREE: a calm, kind manga ally with a long "
        "braid and a sash bearing a crest marked 3; gentle steady expression. " + STYLE
    ),
}

# The 8 panels. `refs` lists which character sheets to condition on. `bubbles`
# positions are percentages (0-100) of the panel box. kind: speech|thought|caption|sfx.
PANELS = [
    {
        "order": 1, "span": MangaPanel.SPAN_WIDE,
        "alt": "Ninety-Eight stands on an HQ rooftop at dusk, gazing at a hundred-shaped moon.",
        "scene": "Wide establishing shot: NINETY-EIGHT stands on a rooftop headquarters at "
                 "dusk, gazing up at a large round moon. Lonely, determined mood.",
        "refs": ["98"],
        "caption": "Every number has a secret partner. Together, they make one hundred.",
        "bubbles": [
            {"speaker": "Ninety-Eight", "kind": "thought", "x": 62, "y": 30,
             "text": "I'm only 2 away from a full hundred… so close it hurts."},
        ],
    },
    {
        "order": 2, "span": MangaPanel.SPAN_NORMAL,
        "alt": "Two leaps into frame grinning, reaching out a hand to Ninety-Eight.",
        "scene": "Close action: TWO leaps into frame grinning, reaching out a hand toward "
                 "NINETY-EIGHT. Warm, energetic.",
        "refs": ["98", "2"],
        "bubbles": [
            {"speaker": "Two", "kind": "speech", "x": 30, "y": 20,
             "text": "Then borrow me, partner! You + me = 100. That's what besties are for."},
            {"speaker": "", "kind": "sfx", "x": 70, "y": 70, "text": "BA-DUMP"},
        ],
    },
    {
        "order": 3, "span": MangaPanel.SPAN_NORMAL,
        "alt": "A glowing mission-briefing screen lights the heroes' faces.",
        "scene": "NINETY-EIGHT and TWO lit by a glowing holographic mission-briefing screen. "
                 "Focused, adventurous.",
        "refs": ["98", "2"],
        "caption": "MISSION:  234 + 98",
        "bubbles": [
            {"speaker": "Ninety-Eight", "kind": "speech", "x": 34, "y": 68,
             "text": "Adding 98 is a trap. But adding 100? Child's play."},
        ],
    },
    {
        "order": 4, "span": MangaPanel.SPAN_FULL,
        "alt": "Ninety-Eight powers up, glowing, transforming toward a radiant 100.",
        "scene": "BIG hero moment: NINETY-EIGHT powers up mid-air, radiant energy aura "
                 "surging upward, transforming. Explosive light rays.",
        "refs": ["98"],
        "caption": "234 + 100 = 334",
        "bubbles": [
            {"speaker": "", "kind": "sfx", "x": 12, "y": 16, "text": "DODON!!"},
            {"speaker": "Two", "kind": "speech", "x": 66, "y": 74,
             "text": "Careful — we borrowed 2 EXTRA power."},
        ],
    },
    {
        "order": 5, "span": MangaPanel.SPAN_NORMAL,
        "alt": "The heroes cool down, gently releasing two sparks of borrowed energy.",
        "scene": "Calm cooldown: NINETY-EIGHT and TWO release two small sparks of energy back "
                 "into the air, relieved. Soft, satisfied.",
        "refs": ["98", "2"],
        "caption": "Give the 2 back:  334 − 2 = 332",
        "bubbles": [
            {"speaker": "Ninety-Eight", "kind": "thought", "x": 30, "y": 24,
             "text": "Mission… complete."},
        ],
    },
    {
        "order": 6, "span": MangaPanel.SPAN_NORMAL,
        "alt": "A rival figure smirks from the shadows at the edge of the panel.",
        "scene": "A mysterious rival figure smirks from the shadows at the panel's edge, half-lit. "
                 "Intriguing, playful tension.",
        "refs": [],
        "caption": "Another way:  adjust first → 234 − 2 = 232,  then 232 + 100 = 332",
        "bubbles": [
            {"speaker": "Rival", "kind": "speech", "x": 40, "y": 22,
             "text": "There's more than one way, you know."},
        ],
    },
    {
        "order": 7, "span": MangaPanel.SPAN_WIDE,
        "alt": "A huge foe rises; Three joins the heroes back-to-back for the final battle.",
        "scene": "Epic wide shot: a huge shadowy foe rises before the heroes; THREE arrives and "
                 "stands with NINETY-EIGHT and TWO, ready. Grand, heroic.",
        "refs": ["98", "3"],
        "caption": "456 + 397  →  456 + 400 = 856  →  return the 3  →  856 − 3 = 853",
        "bubbles": [
            {"speaker": "", "kind": "sfx", "x": 74, "y": 20, "text": "KA-KOOM!!"},
        ],
    },
    {
        "order": 8, "span": MangaPanel.SPAN_FULL,
        "alt": "Victory pose: the number besties stand triumphant, back-to-back.",
        "scene": "Triumphant victory pose: NINETY-EIGHT, TWO and THREE stand back-to-back, "
                 "smiling, sunrise behind them. Warm, uplifting finale.",
        "refs": ["98", "2", "3"],
        "caption": "★ RULE OF THE NUMBER BESTIES ★  When a number is 1, 2, or 3 away from a "
                   "hundred — borrow its bestie to make the hundred, do the easy math, then give "
                   "the bestie back.",
        "bubbles": [
            {"speaker": "Ninety-Eight", "kind": "speech", "x": 30, "y": 74,
             "text": "Never underestimate a number close to a hundred. To be continued →"},
        ],
    },
]


class Command(BaseCommand):
    help = "Build the Number Besties lesson as an illustrated manga (panels + bubbles + art)."

    def add_arguments(self, parser):
        parser.add_argument("--material", type=int, help="Material id to build panels for.")
        parser.add_argument("--for-user", help="Username whose Dimensions Math 3A Ch2 L6 manga to build.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Only (re)build panel + bubble structure with placeholder art (no token needed).",
        )
        parser.add_argument(
            "--regenerate", action="store_true",
            help="Regenerate art even for panels that already have an image.",
        )

    def handle(self, *args, **options):
        material = self._resolve_material(options)
        dry_run = options["dry_run"] or not imagegen.is_configured()

        if dry_run and not options["dry_run"]:
            self.stdout.write(self.style.WARNING(
                "No REPLICATE_API_TOKEN set — building structure only (placeholder art)."
            ))

        sheets = {} if dry_run else self._generate_character_sheets(options["regenerate"])

        built = 0
        for spec in PANELS:
            panel, _ = MangaPanel.objects.update_or_create(
                material=material, order=spec["order"],
                defaults={
                    "span": spec["span"],
                    "alt": spec["alt"],
                    "caption": spec.get("caption", ""),
                    "bubbles": spec["bubbles"],
                    "prompt": self._panel_prompt(spec),
                },
            )
            if not dry_run and (options["regenerate"] or not panel.has_art):
                self._draw_panel(panel, spec, sheets)
            built += 1

        # Drop any stale panels beyond the current script.
        MangaPanel.objects.filter(material=material).exclude(
            order__in=[p["order"] for p in PANELS]
        ).delete()

        mode = "structure only" if dry_run else "with art"
        self.stdout.write(self.style.SUCCESS(
            f"Built {built} panels ({mode}) for Material #{material.pk} '{material.title}'."
        ))
        if dry_run:
            self.stdout.write(
                "Set REPLICATE_API_TOKEN and re-run without --dry-run to draw the panels."
            )

    # -- helpers ------------------------------------------------------------

    def _panel_prompt(self, spec):
        return f"{spec['scene']} {STYLE}"

    def _generate_character_sheets(self, regenerate):
        """Generate (or reuse) each hero's character sheet; return {name: local_path}."""
        import os

        out_dir = os.path.join(settings.BASE_DIR, "static", ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        sheets = {}
        for name, prompt in CHARACTERS.items():
            path = os.path.join(out_dir, f"char-{name}.png")
            if regenerate or not os.path.exists(path):
                self.stdout.write(f"  drawing character sheet: {name}…")
                data = imagegen.generate_image(prompt)
                with open(path, "wb") as fh:
                    fh.write(data)
            sheets[name] = path
        return sheets

    def _draw_panel(self, panel, spec, sheets):
        import os

        refs = [sheets[name] for name in spec.get("refs", []) if name in sheets]
        self.stdout.write(f"  drawing panel {spec['order']}…")
        data = imagegen.generate_image(self._panel_prompt(spec), reference_paths=refs)

        out_dir = os.path.join(settings.BASE_DIR, "static", ART_DIR)
        os.makedirs(out_dir, exist_ok=True)
        filename = f"p{spec['order']}.png"
        with open(os.path.join(out_dir, filename), "wb") as fh:
            fh.write(data)
        panel.image_path = f"{ART_DIR}/{filename}"
        panel.save(update_fields=["image_path"])

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
                chapter__curriculum=curriculum, chapter__number=2, number=6,
            ).first()
            material = Material.objects.filter(
                lesson=lesson, skill_type=Material.SKILL_MANGA,
            ).first()
            if material is None:
                raise CommandError(
                    "No manga material found. Run seed_violet_manga first."
                )
            return material
        raise CommandError("Provide --material <id> or --for-user <username>.")
