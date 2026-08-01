"""Seed the Spanish phonics mini-lesson rules (F-04, LGA-64).

Idempotent: get_or_create keyed on ``pattern``, so re-running only fills gaps and
never duplicates. One small lesson on the handful of Spanish-specific decoding rules —
not a subsystem (synced-audio reading is the real phonics for a shallow orthography).

    python manage.py seed_phonics
"""
from django.core.management.base import BaseCommand

from lingua.models import PhonicsRule

# (pattern, title, tip, example practice words)
RULES = [
    ("vowels", "Vocales puras", "Each vowel makes ONE clear sound, always the same: a-e-i-o-u.", "mesa · piso · luna · oso"),
    ("h", "La h muda", "The letter h is always silent in Spanish.", "hola · hoy · huevo · hermano"),
    ("ñ", "La ñ", "ñ sounds like the 'ny' in canyon.", "niño · España · mañana · señor"),
    ("ll", "La ll", "ll usually sounds like the 'y' in yes.", "llama · pollo · calle · lluvia"),
    ("rr", "La rr fuerte", "rr is a strong rolled r (roll your tongue).", "perro · carro · gorra · tierra"),
    ("j", "La j", "j is a strong 'h' sound from the back of the throat.", "jugar · caja · rojo · trabajo"),
    ("g/gu", "g y gu", "g is soft (like j) before e/i; gu keeps the hard g before e/i.", "gato · gente · guitarra · guerra"),
    ("accents", "El acento", "The accent mark (´) tells you which syllable to stress.", "café · árbol · lápiz · pájaro"),
    # The accented vowels are their own thing to RECOGNISE before any rule about when
    # to write them: they are the same five sounds, just louder. Without this a child
    # meets á for the first time inside a word and reads it as a new letter.
    ("acentuadas", "Las vocales con acento",
     "á é í ó ú are the SAME sounds as a e i o u — you just say that part louder.",
     "papá · bebé · aquí · avión · menú"),
    ("dieresis", "La ü",
     "In güe and güi the two dots mean you DO say the u: gwe, gwi.",
     "pingüino · vergüenza · bilingüe · cigüeña"),
]


class Command(BaseCommand):
    help = "Seed the Spanish phonics mini-lesson rules (idempotent)."

    def handle(self, *args, **options):
        created = existing = 0
        for order, (pattern, title, tip, example) in enumerate(RULES):
            _, was_created = PhonicsRule.objects.get_or_create(
                pattern=pattern,
                defaults={"title": title, "tip": tip, "example": example, "order": order},
            )
            created += was_created
            existing += not was_created
        self.stdout.write(self.style.SUCCESS(
            f"Phonics rules seeded: {created} created, {existing} already present."
        ))
