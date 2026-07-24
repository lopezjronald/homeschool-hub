"""Seed the age-banded content themes that drive the rotation (LGA-46, D-51/N-01).

Idempotent: get_or_create is keyed on ``slug``, so re-running only fills gaps and
never duplicates. v1 seeds the two kid bands (profiles.V1_ACTIVE); TEEN/ADULT
themes are a later data change, not a code change (D-36). The theme set is
intentionally small and concrete for the young bands and more narrative-driven
for the older band — the rotation (services.rotate_themes) then balances coverage
across whichever themes exist.

    python manage.py seed_themes            # all v1 bands
    python manage.py seed_themes --band KIDS_EARLY
"""
from django.core.management.base import BaseCommand

from lingua import profiles
from lingua.models import Theme

DEFAULT_THEMES = {
    profiles.KIDS_EARLY: [
        ("animals", "Animals"),
        ("family-home", "Family & home"),
        ("food-meals", "Food & meals"),
        ("colors-shapes", "Colors & shapes"),
        ("nature-weather", "Nature & weather"),
        ("play-toys", "Play & toys"),
        ("everyday-routines", "Everyday routines"),
    ],
    profiles.KIDS_OLDER: [
        ("adventure", "Adventure"),
        ("mystery", "Mystery"),
        ("friendship", "Friendship"),
        ("sports-games", "Sports & games"),
        ("space-science", "Space & science"),
        ("myths-legends", "Myths & legends"),
        ("animals-wildlife", "Animals & wildlife"),
        ("daily-life", "Everyday life"),
    ],
}


class Command(BaseCommand):
    help = "Seed the default age-banded content themes for the rotation (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--band",
            choices=sorted(DEFAULT_THEMES),
            default=None,
            help="Seed only this age band (default: all v1 bands).",
        )

    def handle(self, *args, **options):
        band = options["band"]
        bands = [band] if band else list(DEFAULT_THEMES)
        created = existing = 0
        for b in bands:
            for slug, name in DEFAULT_THEMES[b]:
                _, was_created = Theme.objects.get_or_create(
                    slug=slug, defaults={"name": name, "age_band": b},
                )
                if was_created:
                    created += 1
                else:
                    existing += 1
        self.stdout.write(self.style.SUCCESS(
            f"Themes seeded: {created} created, {existing} already present."
        ))
