"""Seed the curated Spanish listening resources (F-02/N-02, LGA-55/56).

Idempotent: get_or_create keyed on ``url``. Hand-picked comprehensible-input channels
and playlists with strong visual support, split by age band. es-MX / neutral Latin
American, kid-appropriate. Only links + metadata are stored — no copyrighted media.

    python manage.py seed_listening
"""
from django.core.management.base import BaseCommand

from lingua import profiles
from lingua.models import ListeningResource

# (title, provider, url, age_band, level, visual_support, minutes, order)
RESOURCES = [
    # --- KIDS_EARLY (~6-9): songs + animated stories, very high visual support ---
    ("Canciones de Rockalingua", "Rockalingua",
     "https://www.youtube.com/playlist?list=PLUnYkVlaxVK5cGl12JITNPeTtJrNT-crG",
     profiles.KIDS_EARLY, "L1", True, 5, 1),
    ("Once Niñas y Niños (Canal Once, México)", "Canal Once",
     "https://www.youtube.com/channel/UC0zvIM2UXP8tgBzAlW2ffCQ",
     profiles.KIDS_EARLY, "L1", True, 10, 2),
    ("Canciones de 123 Andrés", "123 Andrés",
     "https://www.youtube.com/channel/UCrNRnxyY4zC2KKE9Aos2mPw",
     profiles.KIDS_EARLY, "L1", True, 5, 3),
    # --- KIDS_OLDER (~10-13): comprehensible-input storytelling with gestures/drawings ---
    ("Dreaming Spanish — Súper principiante", "Dreaming Spanish",
     "https://www.youtube.com/playlist?list=PLlpPf-YgbU7GbOHc3siOGQ5KmVSngZucl",
     profiles.KIDS_OLDER, "L1", True, 8, 1),
    ("Dreaming Spanish — Principiante", "Dreaming Spanish",
     "https://www.youtube.com/playlist?list=PLlpPf-YgbU7HWrrenMs3-nuhxgzyAiA-C",
     profiles.KIDS_OLDER, "L2", True, 10, 2),
]


class Command(BaseCommand):
    help = "Seed the curated Spanish listening resources (idempotent)."

    def handle(self, *args, **options):
        created = existing = 0
        for title, provider, url, band, level, visual, minutes, order in RESOURCES:
            _, was_created = ListeningResource.objects.get_or_create(
                url=url,
                defaults={
                    "title": title, "provider": provider, "age_band": band, "level": level,
                    "visual_support": visual, "minutes": minutes, "order": order,
                },
            )
            created += was_created
            existing += not was_created
        self.stdout.write(self.style.SUCCESS(
            f"Listening resources seeded: {created} created, {existing} already present."
        ))
