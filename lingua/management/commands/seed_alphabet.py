"""Seed the Spanish alphabet chart tiles for Escuchar (LGA-86).

Idempotent on ``symbol``. Includes A–Z, ñ, and digraphs ll / rr as first-class
tiles (letter name in ``spoken``, optional example word).

    python manage.py seed_alphabet
"""
from django.core.management.base import BaseCommand

from lingua.models import AlphabetTile

# (symbol, spoken, example, kind) — digraphs after their single-letter neighbors.
TILES = [
    ("a", "a", "amigo", AlphabetTile.LETTER),
    ("b", "be", "barco", AlphabetTile.LETTER),
    ("c", "ce", "casa", AlphabetTile.LETTER),
    ("d", "de", "dado", AlphabetTile.LETTER),
    ("e", "e", "elefante", AlphabetTile.LETTER),
    ("f", "efe", "foca", AlphabetTile.LETTER),
    ("g", "ge", "gato", AlphabetTile.LETTER),
    ("h", "hache", "hola", AlphabetTile.LETTER),
    ("i", "i", "isla", AlphabetTile.LETTER),
    ("j", "jota", "jugar", AlphabetTile.LETTER),
    ("k", "ka", "kilo", AlphabetTile.LETTER),
    ("l", "ele", "luna", AlphabetTile.LETTER),
    ("ll", "elle", "llama", AlphabetTile.DIGRAPH),
    ("m", "eme", "mesa", AlphabetTile.LETTER),
    ("n", "ene", "nube", AlphabetTile.LETTER),
    ("ñ", "eñe", "niño", AlphabetTile.LETTER),
    ("o", "o", "oso", AlphabetTile.LETTER),
    ("p", "pe", "perro", AlphabetTile.LETTER),
    ("q", "cu", "queso", AlphabetTile.LETTER),
    ("r", "ere", "pero", AlphabetTile.LETTER),
    ("rr", "erre", "perro", AlphabetTile.DIGRAPH),
    ("s", "ese", "sol", AlphabetTile.LETTER),
    ("t", "te", "taco", AlphabetTile.LETTER),
    ("u", "u", "uva", AlphabetTile.LETTER),
    ("v", "uve", "vaca", AlphabetTile.LETTER),
    ("w", "doble uve", "kiwi", AlphabetTile.LETTER),
    ("x", "equis", "xilófono", AlphabetTile.LETTER),
    ("y", "ye", "yo", AlphabetTile.LETTER),
    ("z", "zeta", "zapato", AlphabetTile.LETTER),
]


class Command(BaseCommand):
    help = "Seed Spanish alphabet + digraph tiles for Escuchar (idempotent)."

    def handle(self, *args, **options):
        created = existing = 0
        for order, (symbol, spoken, example, kind) in enumerate(TILES):
            _, was_created = AlphabetTile.objects.get_or_create(
                symbol=symbol,
                defaults={
                    "spoken": spoken, "example": example, "kind": kind, "order": order,
                },
            )
            created += was_created
            existing += not was_created
        self.stdout.write(self.style.SUCCESS(
            f"Alphabet tiles seeded: {created} created, {existing} already present."
        ))
