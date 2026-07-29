"""Seed Kaylin's italki Lección 1 tutor packet (LGA-85).

Idempotent on ``title``. The DOCX handout is uploaded via Django admin (private
storage / R2) — this seed only creates the packet + practice phrases from the
teacher's chat homework. Pass ``--host-student-id`` or we look up a Student
named Kaylin when the host app is available.

    python manage.py seed_tutor_leccion1
    python manage.py seed_tutor_leccion1 --host-student-id 2
"""
from django.core.management.base import BaseCommand

from lingua.models import TutorPacket

TITLE = "Lección 1 — Mis primeros pasos"

BODY = """# Practice lines from italki (Juan Cárdenas) — read aloud
# Vocab: inteligente, amigable, alta/alto, bajo/a, bonito/a, fuerte, realmente, porque, tú eres
Mi mamá es inteligente.
Mi abuela es inteligente.
Mi papá no es amigable, mi papá es muy amigable.
Yo amo a mi hermana.
Yo amo a mi papá.
Yo soy amigable.
Mi amigo es amigable.
Mi hermana es alta.
Yo soy alta.
Mi papá es alto, amigable y fuerte.
Tú eres amigable.
"""


class Command(BaseCommand):
    help = "Seed the italki Lección 1 tutor packet (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--host-student-id", type=int, default=None,
            help="Restrict packet to this students.Student.pk (Kaylin).",
        )

    def handle(self, *args, **options):
        host_id = options["host_student_id"]
        if host_id is None:
            try:
                from students.models import Student
                kaylin = Student.objects.filter(first_name__iexact="Kaylin").first()
                if kaylin:
                    host_id = kaylin.pk
            except Exception:  # noqa: BLE001 — host app may be absent when extracted
                host_id = None

        obj, created = TutorPacket.objects.get_or_create(
            title=TITLE,
            defaults={
                "source": "italki · Juan Cárdenas",
                "body": BODY,
                "host_student_id": host_id,
                "order": 1,
                "active": True,
            },
        )
        if not created:
            # Refresh body/source on re-seed, but don't wipe a manually set host id
            # unless the operator passed one explicitly.
            updates = {"source": "italki · Juan Cárdenas", "body": BODY, "active": True}
            if options["host_student_id"] is not None:
                updates["host_student_id"] = host_id
            elif host_id is not None and obj.host_student_id is None:
                updates["host_student_id"] = host_id
            TutorPacket.objects.filter(pk=obj.pk).update(**updates)
            action = "updated"
        else:
            action = "created"
        who = f"host_student_id={host_id}" if host_id else "shared (all learners)"
        self.stdout.write(self.style.SUCCESS(
            f"TutorPacket {action}: {TITLE!r} ({who}). Upload the DOCX via admin."
        ))
