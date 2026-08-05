"""Seed the curated Spanish listening resources (F-02/N-02, LGA-55/56, LGA-102).

Idempotent: get_or_create keyed on ``(url, age_band)`` — a channel can serve two bands.
Hand-picked comprehensible-input channels
and playlists with strong visual support, split by age band. es-MX / neutral Latin
American, kid-appropriate. Only links + metadata are stored — no copyrighted media.

TWO KINDS, and the difference is what makes rotation possible (LGA-102):

* SHELVES — channels and playlists. Endless wells; "she already watched it" is not
  a fact that can be true of one, so they stay on the page permanently. They are
  also the backstop: a rotted video link never leaves her with an empty page.
* VIDEOS — one video each. These are what the 3-choice rotation draws from.

``kind`` is CLASSIFIED FROM THE URL rather than typed by hand, so a channel added
later cannot accidentally be marked rotatable. The model default is VIDEO, which
would have been wrong for every row here — the seed must set it explicitly.

Every video below was checked with ``check_listening_links`` and its channel
confirmed against ``author_name``: two search hits turned out to be a different
channel wearing a similar name, and two more were already dead. Verification says
the link resolves and who published it — NOT that anyone watched it. Approve the
list yourself before pointing a child at it.

    python manage.py seed_listening
"""
from django.core.management.base import BaseCommand

from lingua import profiles
from lingua.listening import classify_url
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
    # Also offered to the older band — Once Niñas y Niños spans ages 4-12, so it's
    # authentic es-MX variety alongside Dreaming Spanish (same channel as KIDS_EARLY,
    # which is why the seed keys on (url, age_band), not url alone).
    ("Once Niñas y Niños (Canal Once, México)", "Canal Once",
     "https://www.youtube.com/channel/UC0zvIM2UXP8tgBzAlW2ffCQ",
     profiles.KIDS_OLDER, "L2", True, 12, 3),

    # --- Single videos: the pool the 3-choice rotation draws from (LGA-102) ---
    # Rockalingua and 123 Andrés, both already curated above as channels. Ordered
    # roughly easiest-first within the band.
    ("Los números", "Rockalingua",
     "https://www.youtube.com/watch?v=oUvyhStbFy8", profiles.KIDS_EARLY, "L1", True, 3, 10),
    ("Colores y números", "Rockalingua",
     "https://www.youtube.com/watch?v=ZiNFXntWOJw", profiles.KIDS_EARLY, "L1", True, 3, 11),
    ("Las partes del cuerpo", "Rockalingua",
     "https://www.youtube.com/watch?v=pOg6y-Q59eM", profiles.KIDS_EARLY, "L1", True, 3, 12),
    ("La familia", "Rockalingua",
     "https://www.youtube.com/watch?v=_T1svGpYS28", profiles.KIDS_EARLY, "L1", True, 3, 13),
    ("De colores / amistad", "Rockalingua",
     "https://www.youtube.com/watch?v=oMRZhR6SOmc", profiles.KIDS_EARLY, "L1", True, 4, 14),
    ("Yo soy especial", "123 Andrés",
     "https://www.youtube.com/watch?v=dW_xBF1CDnY", profiles.KIDS_EARLY, "L1", True, 4, 15),
    # A movement song — she drums, so a song that asks the body to keep time is
    # doing two jobs at once.
    ("La clave (canción de movimiento)", "123 Andrés",
     "https://www.youtube.com/watch?v=RY3n0k73PJk", profiles.KIDS_EARLY, "L1", True, 4, 16),
    ("¡Voy a la escuela!", "123 Andrés",
     "https://www.youtube.com/watch?v=sZ_OkNqnzTk", profiles.KIDS_EARLY, "L1", True, 4, 17),

    # KIDS_OLDER has ONE verified single video so far. Dreaming Spanish turns
    # embedding off, so oEmbed cannot confirm most of its catalogue and those were
    # left out rather than guessed at — the shelves above still cover this band,
    # and `test_every_band_has_videos_to_rotate` names the shortfall out loud.
    ("Lost in NYC — historia para principiantes", "Dreaming Spanish",
     "https://www.youtube.com/watch?v=p5ZHNWifka4", profiles.KIDS_OLDER, "L1", True, 8, 10),
]


class Command(BaseCommand):
    help = "Seed the curated Spanish listening resources (idempotent)."

    def handle(self, *args, **options):
        created = existing = 0
        for title, provider, url, band, level, visual, minutes, order in RESOURCES:
            resource, was_created = ListeningResource.objects.get_or_create(
                url=url, age_band=band,   # a channel may serve two bands, so key on both
                defaults={
                    "title": title, "provider": provider, "level": level,
                    "visual_support": visual, "minutes": minutes, "order": order,
                    "kind": classify_url(url),
                },
            )
            # `kind` is derived, never hand-edited, so correcting it on an existing
            # row is safe — unlike title/order, which a parent may have tuned in the
            # admin and which get_or_create rightly leaves alone.
            wanted = classify_url(url)
            if not was_created and resource.kind != wanted:
                resource.kind = wanted
                resource.save(update_fields=["kind"])
            created += was_created
            existing += not was_created
        self.stdout.write(self.style.SUCCESS(
            f"Listening resources seeded: {created} created, {existing} already present."
        ))

        # A thin band still WORKS — the rotation recycles sooner and says "otra vez"
        # — so this is a nudge, not an error. It is reported here rather than as a
        # failing test because the fix is curation, and this is where the person
        # doing the curating is looking. Roughly a week at 3 a day is the bar.
        WEEK = 8
        for band in sorted({row[3] for row in RESOURCES}):
            n = ListeningResource.objects.filter(
                age_band=band, kind=ListeningResource.VIDEO, active=True).count()
            if n < WEEK:
                self.stdout.write(self.style.WARNING(
                    f"  {band}: only {n} single video(s) — at 3 a day that is under "
                    f"{max(n // 3, 1)} day(s) before repeats. Add more with:\n"
                    f"    manage.py add_listening_video --band {band} <youtube url>"
                ))
