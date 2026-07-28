"""Seed the curated Spanish Library List (LGA-75) from lingua/data/library_books.json.

Idempotent: keyed on (title, author, grade), so re-running updates country/note and
adds any new books without duplicating. The JSON was compiled by a verified multi-agent
research pass — real, published Spanish books (Pre-K..8th) from across Latin America +
Spain. Run locally and on prod: ``python manage.py seed_library``.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from lingua.models import LibraryBook

DATA = Path(__file__).resolve().parent.parent.parent / "data" / "library_books.json"


class Command(BaseCommand):
    help = "Seed/refresh the curated Spanish Library List from the bundled JSON."

    def handle(self, *args, **options):
        books = json.loads(DATA.read_text(encoding="utf-8"))
        created = updated = 0
        valid = {g for g, _ in LibraryBook.GRADE_CHOICES}
        for b in books:
            grade = b.get("grade")
            title = (b.get("title") or "").strip()
            if not title or grade not in valid:
                continue
            _, was_created = LibraryBook.objects.update_or_create(
                title=title[:200], author=(b.get("author") or "").strip()[:200], grade=grade,
                defaults={"country": (b.get("country") or "").strip()[:64],
                          "note": (b.get("note") or "").strip()[:300]},
            )
            created += was_created
            updated += not was_created
        by_grade = {g: LibraryBook.objects.filter(grade=g).count()
                    for g in LibraryBook.GRADE_ORDER}
        self.stdout.write(self.style.SUCCESS(
            f"Library seeded: {created} created, {updated} updated, "
            f"{LibraryBook.objects.count()} total. Per grade: {by_grade}"
        ))
