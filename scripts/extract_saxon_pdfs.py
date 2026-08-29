"""Extract the text of Saxon/DIVE lesson PDFs to a file that survives.

WHY THIS EXISTS. The lesson PDFs for 74-100 were uploaded into a conversation and
were gone by the time they were needed — a context window is not storage. Only
lessons 71-73 had been extracted to disk, so only those could be authored
faithfully. Anything a lesson is authored FROM has to land in a file first.

    python scripts/extract_saxon_pdfs.py <dir-or-pdf>... -o saxon_source/

Writes one .txt per lesson, named by the lesson number found in the PDF, plus an
index. Output is meant to be gitignored: it is a digitisation of the family's
purchased guide ((c) DIVE, LLC) for private use, not something to publish.

Reads PDFs with PyMuPDF, the same library the rest of the repo's PDF work
uses (`curricula/management/commands/ingest_booklet.py`) — it is declared in
requirements.txt, so this needs nothing extra. If it is missing, this says so
plainly rather than half-working.
"""

import argparse
import os
import re
import sys


def lesson_number(text, fallback):
    """The printed lesson number, read from the first page's heading."""
    m = re.search(r"Lesson\s+(\d{1,3})\b", text[:400])
    return int(m.group(1)) if m else fallback


def extract(path):
    try:
        import pymupdf
    except ImportError:                                      # pragma: no cover
        sys.exit("PyMuPDF is not installed:  pip install -r requirements.txt")
    with pymupdf.open(path) as doc:
        pages = [(i + 1, (page.get_text() or "").strip())
                 for i, page in enumerate(doc)]
    body = "\n\n".join(f"--- page {n} ---\n{t}" for n, t in pages if t)
    return body, len(pages)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inputs", nargs="+", help="PDF files, or directories of them")
    ap.add_argument("-o", "--out", default="saxon_source",
                    help="directory to write .txt files into")
    args = ap.parse_args()

    pdfs = []
    for item in args.inputs:
        if os.path.isdir(item):
            pdfs += [os.path.join(item, n) for n in sorted(os.listdir(item))
                     if n.lower().endswith(".pdf")]
        else:
            pdfs.append(item)
    if not pdfs:
        sys.exit("no PDFs found in: " + ", ".join(args.inputs))

    os.makedirs(args.out, exist_ok=True)
    index, empty = [], []
    for i, path in enumerate(pdfs):
        body, page_count = extract(path)
        if not body.strip():
            # A scanned PDF extracts to nothing. Silence here would look like a
            # successful run and produce a lesson authored from an empty file.
            empty.append(os.path.basename(path))
            continue
        n = lesson_number(body, fallback=i)
        dest = os.path.join(args.out, f"lesson_{n:03d}.txt")
        header = (f"{'=' * 78}\nLESSON {n} — {os.path.basename(path)} "
                  f"— {page_count} pages\n{'=' * 78}\n\n")
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(header + body + "\n")
        index.append((n, dest, page_count, len(body)))
        print(f"  lesson {n:>3}  {page_count:>2}pp  {len(body):>6} chars  -> {dest}")

    if index:
        with open(os.path.join(args.out, "INDEX.txt"), "w", encoding="utf-8") as fh:
            for n, dest, pages, size in sorted(index):
                fh.write(f"{n}\t{os.path.basename(dest)}\t{pages} pages\t{size} chars\n")

    print(f"\n{len(index)} lesson(s) extracted to {args.out}/")
    if empty:
        print("EXTRACTED NOTHING (scanned images? needs OCR):")
        for name in empty:
            print("   ", name)
        sys.exit(1)


if __name__ == "__main__":
    main()
