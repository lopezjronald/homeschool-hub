"""Seed the full Spanish accent rules as phonics rules for the older band (LGA-98).

Idempotent: `PhonicsRule` is keyed on `pattern`, so re-running fills gaps only.

These follow the **2010 RAE Ortografía**, which is the version worth teaching: it
removed the tilde from adverbial "solo" and from demonstrative pronouns (este/ese),
made "guion" monosyllabic, and dropped the accent on "o" between numbers. Teaching the
pre-2010 rules would have her correcting things that are now correct.

Spread across the year for the 12-year-old. The 9-year-old gets only stressed-syllable
awareness plus the top diacritics (tú/tu, él/el, sí/si) — the research is explicit that
explicit metalanguage should stay light at that age.

    python manage.py seed_accent_rules
    python manage.py clips_build --phonics    # then bake the example words
"""
from django.core.management.base import BaseCommand

from lingua.models import PhonicsRule

# (pattern, title, tip, example practice words)
RULES = [
    ("agudas", "Agudas",
     "Stress on the LAST syllable. Tilde when the word ends in a vowel, n, or s.",
     "café · canción · revés · comité"),
    ("llanas", "Llanas (graves)",
     "Stress on the SECOND-TO-LAST syllable. Tilde when it does NOT end in a vowel, n, or s.",
     "lápiz · árbol · túnel · césped"),
    ("esdrujulas", "Esdrújulas",
     "Stress on the THIRD-to-last syllable. These ALWAYS take a tilde — no exceptions.",
     "rápido · análisis · pájaro · música"),
    ("diacritica", "Tilde diacrítica",
     "The tilde separates two words that sound identical but mean different things.",
     "tú/tu · él/el · sí/si · más/mas · qué/que · sé/se"),
    ("hiato", "Hiato",
     "A stressed i or u next to a strong vowel breaks the diphthong and takes a tilde.",
     "día · país · río · María"),
]


class Command(BaseCommand):
    help = "Seed the full accent rules (agudas/llanas/esdrújulas/diacrítica/hiato)."

    def handle(self, *args, **options):
        created = existing = 0
        # Start after the eight base sounds so the accent set reads as a later unit.
        for offset, (pattern, title, tip, example) in enumerate(RULES):
            _, was_created = PhonicsRule.objects.get_or_create(
                pattern=pattern,
                defaults={"title": title, "tip": tip, "example": example,
                          "order": 100 + offset},
            )
            created += was_created
            existing += not was_created
        self.stdout.write(self.style.SUCCESS(
            f"Accent rules seeded: {created} created, {existing} already present. "
            f"Run `clips_build --phonics` to bake the example words."
        ))
