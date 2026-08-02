"""Seed Camino Pathway + PathwayStep catalogs per age band (LGA-88).

Idempotent on Pathway.slug. Steps are updated IN PLACE, keyed on order, so a
re-seed picks up title/target tweaks without touching children's checkmarks.
Never delete-then-recreate: PathwayCheckmark.step cascades (LGA-96).

Caveat for whoever edits the spec next: because steps are keyed on ``order``,
REORDERING them moves a child's existing tick onto whatever now sits at that
order. Renaming and retargeting are safe; renumbering is not.

    python manage.py seed_pathway
"""
from django.core.management.base import BaseCommand

from lingua import profiles, services
from lingua.models import Pathway, PathwayStep

# (order, title, kind, target_ref, pass_rule, optional)
# "@level" resolves to the learner's own ceiling at render time, so the stop follows
# her up the ladder. The old fixed "L1"/"L2" refs meant the map still said L1 after
# she had advanced past it, and gave the older band two stops that were really one.
_LVL = services.DYNAMIC_LEVEL

EARLY_STEPS = [
    (0, "Los sonidos", PathwayStep.PHONICS, "", {}, True),
    (1, "Leer historias", PathwayStep.STORY_LEVEL, _LVL, {"min_stories": 1}, False),
    (2, "Escuchar", PathwayStep.LISTEN, "", {}, False),
    (3, "Con el maestro", PathwayStep.TUTOR_PACKET, "", {}, True),
]

OLDER_STEPS = [
    (0, "Leer historias", PathwayStep.STORY_LEVEL, _LVL, {"min_stories": 1}, False),
    # Order 1 (the old fixed "Leer historias L2") is deliberately gone — @level covers
    # both rungs. The remaining orders keep their original numbers ON PURPOSE: steps
    # are keyed on `order`, so renumbering these would move a child's existing ticks
    # onto different activities. Only the dropped order's checkmarks are lost.
    (2, "Escuchar", PathwayStep.LISTEN, "", {}, False),
    (3, "Con el maestro", PathwayStep.TUTOR_PACKET, "", {}, True),
    (4, "Palabras que sabes", PathwayStep.REVIEW, "", {"min_known": 5}, True),
    # Her own sounds stop. Without it the accent rules written FOR her (LGA-98) had
    # no route in the app at all: the Sonidos stone was gated to the younger band and
    # camino-older had no PHONICS step, so she could never reach or advance them.
    (5, "Los acentos", PathwayStep.PHONICS, "", {}, True),
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
