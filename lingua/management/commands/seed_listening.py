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
    # --- KIDS_EARLY (~6-9): STORIES, not songs (LGA-104) ---
    # Violet (9) is at the top of this band and asked for stories like the ones on
    # the older band's channels, not the number/colour songs. So the band is now
    # comprehensible-input STORYTELLING: animated cuentos with subtitles, told
    # slowly enough to follow. The song rows are retired below, not deleted.
    ("Cuentos animados con subtítulos (BookBox)", "BookBox",
     "https://www.youtube.com/playlist?list=PLfs5ju_X8bFbuTMgAFUjHQ3A0HAFgFu58",
     profiles.KIDS_EARLY, "L1", True, 6, 1),
    ("Dreaming Spanish — historias para principiantes", "Dreaming Spanish",
     "https://www.youtube.com/playlist?list=PLlpPf-YgbU7GbOHc3siOGQ5KmVSngZucl",
     profiles.KIDS_EARLY, "L1", True, 8, 2),
    # Kept: Canal Once is a real es-MX kids' channel with stories, not just songs.
    ("Once Niñas y Niños (Canal Once, México)", "Canal Once",
     "https://www.youtube.com/channel/UC0zvIM2UXP8tgBzAlW2ffCQ",
     profiles.KIDS_EARLY, "L1", True, 10, 3),
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

    # --- Single STORY videos: the pool the 3-choice rotation draws from (LGA-102).
    # Animated cuentos with subtitles, each verified through oEmbed by title AND
    # channel. Ordered easiest/shortest first. ---
    ("El tesoro más grande (cuento animado)", "BookBox",
     "https://www.youtube.com/watch?v=3O8RUPDzUcI", profiles.KIDS_EARLY, "L1", True, 5, 10),
    ("Los cuatro amigos (cuento animado)", "BookBox",
     "https://www.youtube.com/watch?v=5k8OMdstOKI", profiles.KIDS_EARLY, "L1", True, 5, 11),
    ("Hugo el cubo (cuento animado)", "BookBox",
     "https://www.youtube.com/watch?v=4mCuUP-ePcc", profiles.KIDS_EARLY, "L1", True, 5, 12),
    ("¡Sonríe, por favor! (cuento animado)", "BookBox",
     "https://www.youtube.com/watch?v=jgj3PnD2-Us", profiles.KIDS_EARLY, "L1", True, 5, 13),
    ("El chacal azul (cuento animado)", "BookBox",
     "https://www.youtube.com/watch?v=U36_u9nxIwI", profiles.KIDS_EARLY, "L2", True, 6, 14),
    ("Caperucita Roja (cuento de hadas)", "SPANISH with Cartoons",
     "https://www.youtube.com/watch?v=kAL0rtFHyrs", profiles.KIDS_EARLY, "L2", True, 7, 15),
    ("Rapunzel (cuento de hadas)", "SPANISH with Cartoons",
     "https://www.youtube.com/watch?v=o3wZRwoBz_A", profiles.KIDS_EARLY, "L2", True, 8, 16),
    ("Cuentos de hadas para principiantes", "Tinto and Tea",
     "https://www.youtube.com/watch?v=mj0-EiQNjt4", profiles.KIDS_EARLY, "L2", True, 10, 17),

    # KIDS_OLDER has ONE verified single video so far. Dreaming Spanish turns
    # embedding off, so oEmbed cannot confirm most of its catalogue and those were
    # left out rather than guessed at — the shelves above still cover this band,
    # and `test_every_band_has_videos_to_rotate` names the shortfall out loud.
    ("Lost in NYC — historia para principiantes", "Dreaming Spanish",
     "https://www.youtube.com/watch?v=p5ZHNWifka4", profiles.KIDS_OLDER, "L1", True, 8, 10),

    # --- ADULT (LGA-103): the parent's own input ladder ---
    # SHELVES on purpose. The 3-choice rotation exists to stop a child seeing the
    # same video forever; an adult picks for himself and does not need protecting
    # from a rewatch, so channels and playlists — which do not rot — are the right
    # shape here. Ordered easiest first.
    #
    # es-MX leaning, because that is the anchor dialect and the trip is to Mexico.
    # Dreaming Spanish is pan-Latin-American and goes first only because its
    # graded ladder is the gentlest on-ramp for a beginner.
    ("Dreaming Spanish — el canal", "Dreaming Spanish",
     "https://www.youtube.com/@DreamingSpanish", profiles.ADULT, "L1", True, 15, 1),
    ("Dreaming Spanish — Súper principiante", "Dreaming Spanish",
     "https://www.youtube.com/playlist?list=PLlpPf-YgbU7GbOHc3siOGQ5KmVSngZucl",
     profiles.ADULT, "L1", True, 10, 2),
    ("Dreaming Spanish — Principiante", "Dreaming Spanish",
     "https://www.youtube.com/playlist?list=PLlpPf-YgbU7HWrrenMs3-nuhxgzyAiA-C",
     profiles.ADULT, "L2", True, 12, 3),
    # Explicitly Mexican, and conversational rather than narrated — closer to what
    # he will actually have to follow at a hotel desk.
    ("Learn Mexican Spanish — Temporada 1", "Doorway To Mexico",
     "https://www.youtube.com/playlist?list=PLoJBD5jxm7BXNJ_Ma6mXjActy_m2SkXMR",
     profiles.ADULT, "L3", False, 20, 4),
    ("Doorway to Mexico — el canal", "Doorway To Mexico",
     "https://www.youtube.com/channel/UCoghXiWV7PxWp1e4Aj9LaVA",
     profiles.ADULT, "L3", False, 20, 5),
    ("How to Spanish — español mexicano real", "How to Spanish",
     "https://www.youtube.com/c/HowtoSpanishLessons", profiles.ADULT, "L4", False, 25, 6),
]

# --- RETIRED (LGA-104) ---------------------------------------------------------
# Rows that were seeded once and are now switched OFF. Violet (9) outgrew the
# KIDS_EARLY number/colour songs and asked for stories instead, so her band's song
# rows are removed from RESOURCES above — but get_or_create only ever CREATES, it
# never deactivates, so the rows would linger `active=True` in every database that
# already ran the seed. This list is the surgical off-switch: the seed sets
# `active=False` on EXACTLY these (url, age_band) pairs and touches nothing else's
# `active`, so a parent's admin edit on some other resource is never clobbered.
#
# They are retired, not deleted: a genuinely younger child could want them back,
# and a re-add is one `active=True` in the admin. Nothing here is on RESOURCES, so
# a later seed run will not resurrect them.
RETIRED = [
    # (url, age_band) — Violet's former song rotation + the two song shelves
    ("https://www.youtube.com/watch?v=oUvyhStbFy8", profiles.KIDS_EARLY),
    ("https://www.youtube.com/watch?v=ZiNFXntWOJw", profiles.KIDS_EARLY),
    ("https://www.youtube.com/watch?v=pOg6y-Q59eM", profiles.KIDS_EARLY),
    ("https://www.youtube.com/watch?v=_T1svGpYS28", profiles.KIDS_EARLY),
    ("https://www.youtube.com/watch?v=oMRZhR6SOmc", profiles.KIDS_EARLY),
    ("https://www.youtube.com/watch?v=dW_xBF1CDnY", profiles.KIDS_EARLY),
    ("https://www.youtube.com/watch?v=RY3n0k73PJk", profiles.KIDS_EARLY),
    ("https://www.youtube.com/watch?v=sZ_OkNqnzTk", profiles.KIDS_EARLY),
    ("https://www.youtube.com/playlist?list=PLUnYkVlaxVK5cGl12JITNPeTtJrNT-crG",
     profiles.KIDS_EARLY),   # Canciones de Rockalingua (shelf)
    ("https://www.youtube.com/channel/UCrNRnxyY4zC2KKE9Aos2mPw",
     profiles.KIDS_EARLY),   # Canciones de 123 Andrés (shelf)
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

        # Retire the rows Violet outgrew (LGA-104). Only ever flips active True->False,
        # and only for the named pairs — an already-off row is a no-op, and nothing
        # else's `active` is read or written. filter().update() so a fresh database
        # that never had these rows simply retires 0.
        retired = 0
        for url, band in RETIRED:
            retired += ListeningResource.objects.filter(
                url=url, age_band=band, active=True).update(active=False)
        if retired:
            self.stdout.write(self.style.SUCCESS(
                f"Retired {retired} outgrown resource(s) (LGA-104)."
            ))

        # A thin band still WORKS — the rotation recycles sooner and says "otra vez"
        # — so this is a nudge, not an error. It is reported here rather than as a
        # failing test because the fix is curation, and this is where the person
        # doing the curating is looking. Roughly a week at 3 a day is the bar.
        WEEK = 8
        # Kid bands only. The ADULT band is shelves by design — rotation exists to
        # stop a child seeing the same video forever, and an adult picks for
        # himself — so warning that he has "no videos to rotate" would be noise
        # that trains someone to ignore this whole block.
        kid_bands = {profiles.KIDS_EARLY, profiles.KIDS_OLDER}
        for band in sorted({row[3] for row in RESOURCES} & kid_bands):
            n = ListeningResource.objects.filter(
                age_band=band, kind=ListeningResource.VIDEO, active=True).count()
            if n < WEEK:
                self.stdout.write(self.style.WARNING(
                    f"  {band}: only {n} single video(s) — at 3 a day that is under "
                    f"{max(n // 3, 1)} day(s) before repeats. Add more with:\n"
                    f"    manage.py add_listening_video --band {band} <youtube url>"
                ))
