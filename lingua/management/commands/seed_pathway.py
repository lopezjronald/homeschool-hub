"""Seed Camino Pathway + PathwayStep catalogs per age band (LGA-88).

Idempotent on Pathway.slug. Steps are replaced for each pathway so re-seed
picks up order/title tweaks without duplicating rows.

    python manage.py seed_pathway
"""
from django.core.management.base import BaseCommand

from lingua import profiles
from lingua.models import Pathway, PathwayStep

# (order, title, kind, target_ref, pass_rule, optional)
EARLY_STEPS = [
    (0, "Los sonidos", PathwayStep.PHONICS, "", {}, True),
    (1, "Leer historias L1", PathwayStep.STORY_LEVEL, "L1", {"min_stories": 1}, False),
    (2, "Escuchar", PathwayStep.LISTEN, "", {}, False),
    (3, "Con el maestro", PathwayStep.TUTOR_PACKET, "", {}, True),
]

OLDER_STEPS = [
    (0, "Leer historias L1", PathwayStep.STORY_LEVEL, "L1", {"min_stories": 1}, False),
    (1, "Leer historias L2", PathwayStep.STORY_LEVEL, "L2", {"min_stories": 1}, False),
    (2, "Escuchar", PathwayStep.LISTEN, "", {}, False),
    (3, "Con el maestro", PathwayStep.TUTOR_PACKET, "", {}, True),
    (4, "Palabras que sabes", PathwayStep.REVIEW, "", {"min_known": 5}, True),
]

PATHWAYS = [
    ("camino-early", "Camino · primeros pasos", profiles.KIDS_EARLY, 0, EARLY_STEPS),
    ("camino-older", "Camino · siguiendo el rastro", profiles.KIDS_OLDER, 1, OLDER_STEPS),
]


class Command(BaseCommand):
    help = "Seed Camino Pathway catalogs for KIDS_EARLY / KIDS_OLDER (idempotent)."

    def handle(self, *args, **options):
        created = updated = 0
        for slug, title, band, order, steps in PATHWAYS:
            pathway, was_created = Pathway.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "age_band": band,
                    "order": order,
                    "active": True,
                },
            )
            created += was_created
            updated += not was_created
            # Update steps IN PLACE, keyed on order. Never delete-then-recreate:
            # PathwayCheckmark.step cascades, so wiping the steps wipes every child's
            # "Hecho" — the one thing this feature stores. Row counts come out
            # identical either way, so the damage is invisible from the summary line.
            for o, t, k, ref, rule, opt in steps:
                PathwayStep.objects.update_or_create(
                    pathway=pathway,
                    order=o,
                    defaults={
                        "title": t,
                        "kind": k,
                        "target_ref": ref,
                        "pass_rule": rule,
                        "optional": opt,
                    },
                )
            # Drop only the orders this pathway no longer defines.
            pathway.steps.exclude(order__in=[s[0] for s in steps]).delete()
        self.stdout.write(self.style.SUCCESS(
            f"Pathways seeded: {created} created, {updated} updated; "
            f"{sum(len(s) for *_, s in PATHWAYS)} steps written."
        ))
