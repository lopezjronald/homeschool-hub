"""Seed the curated Spanish Library List (LGA-75) from lingua/data/library_books.json.

The catalog is transcribed from the parent's own researched reading list — every book,
grade band, CI level/tense, adult stage and free text comes from that document. The
seed PRUNES anything absent from the JSON, so re-running is how you retire titles.

Idempotent: keyed on (title, author, grade, track), so re-running updates a book in
place without duplicating, and the same title may appear in two tracks (e.g. Quiroga's
"Cuentos de la selva" is both an adult-track read and a free public-domain text).
Run locally and on prod: ``python manage.py seed_library``.
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
        created = updated = skipped = 0
        seen = set()
        valid_grades = {g for g, _ in LibraryBook.GRADE_CHOICES}
        valid_tracks = {t for t, _ in LibraryBook.TRACK_CHOICES}
        for b in books:
            title = (b.get("title") or "").strip()
            track = b.get("track") or LibraryBook.NATIVE
            grade = (b.get("grade") or "").strip()
            if not title or track not in valid_tracks:
                skipped += 1
                self.stderr.write(f"  skipped (bad title/track): {title[:60]!r}")
                continue
            # Native-track books must carry a real grade; other tracks are ungraded.
            if track == LibraryBook.NATIVE and grade not in valid_grades:
                skipped += 1
                self.stderr.write(f"  skipped (bad grade {grade!r}): {title[:60]!r}")
                continue
            if track != LibraryBook.NATIVE:
                grade = ""
            seen.add((title[:200], (b.get("author") or "").strip()[:200], grade, track))
            _, was_created = LibraryBook.objects.update_or_create(
                title=title[:200], author=(b.get("author") or "").strip()[:200], grade=grade,
                track=track,
                defaults={"country": (b.get("country") or "").strip()[:64],
                          "note": (b.get("note") or "").strip()[:300],
                          "level_label": (b.get("level_label") or "").strip()[:40],
                          "tense": (b.get("tense") or "").strip()[:40],
                          "isbn": (b.get("isbn") or "").strip()[:20],
                          "is_translation": bool(b.get("is_translation")),
                          "url": (b.get("url") or "").strip()},
            )
            created += was_created
            updated += not was_created

        # Prune rows that are no longer in the JSON. The uniqueness key is
        # (title, author, grade), so a book whose GRADE or TRACK changed upstream would
        # otherwise linger under its old grade as a phantom duplicate.
        pruned = 0
        for row in LibraryBook.objects.all().only("id", "title", "author", "grade", "track"):
            if (row.title, row.author, row.grade, row.track) not in seen:
                row.delete()
                pruned += 1

        by_grade = {g: LibraryBook.objects.filter(grade=g, track=LibraryBook.NATIVE).count()
                    for g in LibraryBook.GRADE_ORDER}
        by_track = {t: LibraryBook.objects.filter(track=t).count()
                    for t in LibraryBook.TRACK_ORDER}
        style = self.style.WARNING if skipped else self.style.SUCCESS
        self.stdout.write(style(
            f"Library seeded: {created} created, {updated} updated, {pruned} pruned, "
            f"{skipped} skipped, {LibraryBook.objects.count()} total."
            f"\n  Tracks: {by_track}\n  Native per grade: {by_grade}"
        ))
