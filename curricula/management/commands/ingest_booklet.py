"""Attach a source booklet to a curriculum, and build the child-safe copy.

    python manage.py ingest_booklet --curriculum 29 \
        --pdf "C:/Users/lopez/Downloads/WS-Level-3-Week-1.pdf" \
        --title "Studies Weekly 3 — Week 1 (teacher edition)" \
        --student-pages 23-26 \
        --student-label "This week's issue"

WHY THE CHILD NEVER GETS THE FILE YOU HAND IN. These PDFs are teacher editions.
Violet's Studies Weekly issue has the marked answer key on pages 8-9 and the
teacher's lesson plans — with their answers printed inline — on 11-19. Handing
her the file would hand her the answers.

So this stores TWO things: the source, which stays parent-only, and a NEW pdf
containing only `--student-pages`, which is the one her viewer serves. The
answer key is not hidden from her by a permission check that could be got
around; it is not in her file at all.

`--dry-run` prints the first line of every page it would give her, which is the
cheapest way to catch an off-by-one before a child sees it.
"""

import io
import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from curricula.models import Curriculum, CurriculumDocument


class Command(BaseCommand):
    help = "Attach a booklet PDF to a curriculum and extract the child-safe pages."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int)
        parser.add_argument("--pdf")
        parser.add_argument(
            "--doc", type=int,
            help="Build the child copy from a document ALREADY uploaded "
                 "(the parent's own upload form). This is how it is done on "
                 "production, where the PDF is in storage and not on the box "
                 "running the command — and it keys on the row, so a "
                 "correction always replaces rather than adding a second "
                 "booklet.")
        parser.add_argument("--title")
        parser.add_argument(
            "--student-pages", required=True,
            help="1-based pages of the source a child may see, e.g. '23-26'.")
        parser.add_argument("--student-label", default="")
        parser.add_argument("--doc-type", default=CurriculumDocument.TYPE_WORKBOOK)
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            import pymupdf as fitz
        except ImportError:                                  # pragma: no cover
            import fitz

        existing = None
        if options["doc"]:
            if options["pdf"] or options["curriculum"]:
                raise CommandError("--doc replaces --pdf and --curriculum.")
            try:
                existing = CurriculumDocument.objects.get(pk=options["doc"])
            except CurriculumDocument.DoesNotExist:
                raise CommandError(f"No document #{options['doc']}.")
            if not existing.file:
                raise CommandError(
                    f"Document #{existing.pk} has no file to extract from.")
            curriculum = existing.curriculum
            label = os.path.basename(existing.file.name)
            with existing.file.open("rb") as fh:
                source = fitz.open(stream=fh.read(), filetype="pdf")
        else:
            if not (options["pdf"] and options["curriculum"] and options["title"]):
                raise CommandError(
                    "Give either --doc, or all of --pdf, --curriculum and "
                    "--title.")
            path = options["pdf"]
            if not os.path.exists(path):
                raise CommandError(f"No such file: {path}")
            try:
                curriculum = Curriculum.objects.get(pk=options["curriculum"])
            except Curriculum.DoesNotExist:
                raise CommandError(f"No curriculum #{options['curriculum']}.")
            label = os.path.basename(path)
            # Closed in every path, including the error one: an open handle
            # keeps a Windows lock on the source file, and the caller usually
            # wants to move or delete it straight afterwards.
            source = fitz.open(path)
        try:
            try:
                pages = CurriculumDocument.parse_pages(
                    options["student_pages"], page_count=source.page_count)
            except ValueError as exc:
                raise CommandError(f"--student-pages: {exc}")

            self.stdout.write(
                "%s — %d pages; giving the child %d of them: %s"
                % (label, source.page_count, len(pages),
                   options["student_pages"]))
            for n in pages:
                first = (source[n - 1].get_text().strip().splitlines()
                         or ["(image only)"])[0]
                self.stdout.write("   p%-3d %s" % (n, first[:72]))

            child_pdf = fitz.open()
            try:
                for n in pages:
                    child_pdf.insert_pdf(source, from_page=n - 1, to_page=n - 1)
                buf = io.BytesIO()
                child_pdf.save(buf)
                child_bytes = buf.getvalue()
            finally:
                child_pdf.close()
        finally:
            source.close()

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(
                "Dry run — nothing written. The child's copy would be %d page(s), "
                "%.1f KB." % (len(pages), len(child_bytes) / 1024)))
            return

        if existing is not None:
            # Keyed on the ROW, so re-running always replaces this booklet
            # rather than adding a second one beside it.
            doc, created = existing, False
            doc.student_pages = options["student_pages"]
            if options["student_label"]:
                doc.student_label = options["student_label"]
            if options["title"]:
                doc.title = options["title"]
        else:
            doc, created = CurriculumDocument.objects.update_or_create(
                curriculum=curriculum, title=options["title"],
                defaults={
                    "doc_type": options["doc_type"],
                    "student_pages": options["student_pages"],
                    "student_label": options["student_label"],
                },
            )

        # A correction filed under a slightly different title does not replace
        # the booklet it was correcting — it ADDS one, and the child is offered
        # both. That is the only realistic way the wide extract of a teacher
        # edition stays reachable after someone has already noticed and fixed
        # it, so say so loudly rather than leaving it to be discovered.
        siblings = (CurriculumDocument.objects
                    .filter(curriculum=curriculum)
                    .exclude(pk=doc.pk)
                    .exclude(student_file="").exclude(student_pages=""))
        if siblings.exists():
            self.stdout.write(self.style.ERROR(
                "WARNING: %s already offers %d other booklet(s) to the child:"
                % (curriculum.name, siblings.count())))
            for other in siblings:
                self.stdout.write(self.style.ERROR(
                    "  #%d %r — pages %s" % (other.pk, other.title,
                                             other.student_pages)))
            self.stdout.write(self.style.ERROR(
                "  She will see ALL of them. If one of these was meant to be "
                "replaced, re-run with its exact --title, or delete it."))
        if existing is None:
            # Only the --pdf path uploads a source; --doc extracts from one
            # that is already in storage and must not re-upload it.
            with open(path, "rb") as fh:
                doc.file.save(os.path.basename(path), ContentFile(fh.read()),
                              save=False)
        stem = os.path.splitext(label)[0]
        doc.student_file.save(f"{stem}-student.pdf",
                              ContentFile(child_bytes), save=False)
        doc.save()

        self.stdout.write(self.style.SUCCESS(
            "%s document #%d for '%s'. The child's copy is %d page(s); the "
            "teacher edition stays parent-only."
            % ("Created" if created else "Updated", doc.pk,
               curriculum.name, len(pages))))
