"""Seed the classroom-management phrases a parent uses to run a session (LGA-94).

Idempotent: get_or_create keyed on ``text``, so re-running fills gaps and never
duplicates. These exist so the SESSION can run in Spanish even though the parent
isn't fluent — the research's "you are the facilitator, not the expert" point.

Deliberately small. Twenty phrases a parent will actually memorise beats a hundred
they'll scroll past. Everything here is Mexican-Spanish neutral and safe to say to a
6-12 year old.

    python manage.py seed_classroom_phrases
    python manage.py clips_build --classroom      # then bake the audio
"""
from django.core.management.base import BaseCommand

from lingua.models import ClassroomPhrase

C = ClassroomPhrase

# (text, english, category, note)
PHRASES = [
    ("Vamos a leer.", "Let's read.", C.OPENING, "Opens the session — same words every time."),
    ("¿Estás lista?", "Are you ready?", C.OPENING, "Say 'listo' for a boy."),
    ("Siéntate aquí conmigo.", "Sit here with me.", C.OPENING, ""),
    ("Abre el libro, por favor.", "Open the book, please.", C.OPENING, ""),

    ("¿Qué es esto?", "What is this?", C.ASKING, "Point at a picture. The highest-value question you know."),
    ("¿De qué color es?", "What color is it?", C.ASKING, ""),
    ("¿Cuántos hay?", "How many are there?", C.ASKING, ""),
    ("¿Qué ves aquí?", "What do you see here?", C.ASKING, "Open-ended — let her answer in one word."),
    ("¿Qué va a pasar?", "What's going to happen?", C.ASKING, "Ask before turning the page."),
    ("¿Te gusta este libro?", "Do you like this book?", C.ASKING, ""),

    ("¡Muy bien!", "Very good!", C.PRAISE, ""),
    ("¡Excelente!", "Excellent!", C.PRAISE, ""),
    ("¡Eso es!", "That's it!", C.PRAISE, "For the moment she gets it right."),
    ("Lo hiciste muy bien.", "You did that really well.", C.PRAISE, "Worth more than a one-word 'bien'."),
    ("Casi. Otra vez.", "Almost. One more time.", C.PRAISE, "Encouraging, not corrective."),

    ("Otra vez, por favor.", "Again, please.", C.REDIRECT, ""),
    ("Más despacio.", "Slower.", C.REDIRECT, ""),
    ("Escucha.", "Listen.", C.REDIRECT, "Then read the line yourself so she hears it."),
    ("Mírame.", "Look at me.", C.REDIRECT, "Gentle — for when attention drifts."),

    ("Ya terminamos.", "We're done.", C.CLOSING, "End on purpose, not when she's had enough."),
    ("Mañana leemos otra vez.", "Tomorrow we read again.", C.CLOSING, ""),
    ("Gracias por leer conmigo.", "Thank you for reading with me.", C.CLOSING, ""),
]


class Command(BaseCommand):
    help = "Seed the parent's classroom-management Spanish phrases (idempotent)."

    def handle(self, *args, **options):
        created = existing = 0
        for order, (text, english, category, note) in enumerate(PHRASES):
            _, was_created = ClassroomPhrase.objects.get_or_create(
                text=text,
                defaults={
                    "english": english,
                    "category": category,
                    "note": note,
                    "order": order,
                },
            )
            created += was_created
            existing += not was_created
        self.stdout.write(self.style.SUCCESS(
            f"Classroom phrases seeded: {created} created, {existing} already present. "
            f"Run `clips_build --classroom` to bake the audio."
        ))
