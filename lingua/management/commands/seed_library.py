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
        valid_grades = {g for g, _ in LibraryBook.GRADE_CHOICES}
        valid_tracks = {t for t, _ in LibraryBook.TRACK_CHOICES}
        for b in books:
            title = (b.get("title") or "").strip()
            track = b.get("track") or LibraryBook.NATIVE
            grade = (b.get("grade") or "").strip()
            if not title or track not in valid_tracks:
                continue
            # Native-track books must carry a real grade; other tracks are ungraded.
            if track == LibraryBook.NATIVE and grade not in valid_grades:
                continue
            if track != LibraryBook.NATIVE:
                grade = ""
            _, was_created = LibraryBook.objects.update_or_create(
                title=title[:200], author=(b.get("author") or "").strip()[:200], grade=grade,
                defaults={"country": (b.get("country") or "").strip()[:64],
                          "note": (b.get("note") or "").strip()[:300],
                          "track": track,
                          "level_label": (b.get("level_label") or "").strip()[:40],
                          "isbn": (b.get("isbn") or "").strip()[:20],
                          "is_translation": bool(b.get("is_translation")),
                          "url": (b.get("url") or "").strip()},
            )
            created += was_created
            updated += not was_created
        by_grade = {g: LibraryBook.objects.filter(grade=g, track=LibraryBook.NATIVE).count()
                    for g in LibraryBook.GRADE_ORDER}
        by_track = {t: LibraryBook.objects.filter(track=t).count()
                    for t in LibraryBook.TRACK_ORDER}
        self.stdout.write(self.style.SUCCESS(
            f"Library seeded: {created} created, {updated} updated, "
            f"{LibraryBook.objects.count()} total.\n  Tracks: {by_track}\n  Native per grade: {by_grade}"
        ))
