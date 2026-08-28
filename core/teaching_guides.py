"""The shelf of teaching guides (HH-202).

One entry per method we actually teach from. Each is a real page — explained in
our own words, with diagrams — not a link to a PDF; the PDF stays attached to
the curriculum for the worked examples.

A code registry rather than a model, because a guide is a hand-written page with
its own diagrams. Adding one is: write the template, add an entry here. The
index page needs no changes.

``subjects`` is what ties a guide to the curricula it explains. Anything a
household teaches that no guide claims shows up on the index as a gap, so the
shelf tells you what is missing without anyone maintaining a list.
"""

from curricula.subjects import canonical, emoji_for

GUIDES = [
    {
        "slug": "literature-discovery",
        "title": "The Discovery Method",
        "publisher": "Blackbird & Company",
        "blurb": (
            "How a Literature &amp; Writing guide works: the five moves of a "
            "week, where the twenty points sit, and what good work looks like "
            "at each level."
        ),
        "template": "core/guides/literature_discovery.html",
        "emoji": "📖",
        # Matched against Curriculum.subject via canonical(), so "Reading",
        # "Language Arts" and "English" all find this one.
        # canonical() folds english / language arts into "writing", so naming
        # them here is belt and braces rather than duplication.
        "subjects": ["reading", "writing", "literature"],
        # Titles that mean "this household's copy of the teacher guide".
        "pdf_hints": ["teacher help", "teacher guide"],
    },
    {
        "slug": "math-facts",
        "title": "Facts That Stick",
        "publisher": "Strategy first, then spaced practice",
        "blurb": (
            "Why the times tables are a much smaller job than they look, the "
            "rule to say out loud for each one, why division is not a second "
            "table to learn — and what to do at the kitchen table in five "
            "minutes."
        ),
        "template": "core/guides/math_facts.html",
        "emoji": "✖️",
        "subjects": ["math", "mathematics", "maths", "arithmetic"],
        "pdf_hints": [],
        # Guides may carry their own data. The shelf stays a registry of pages;
        # a page that needs computed content says so here rather than the view
        # growing a branch per guide.
        "context": "core.math_facts:page_context",
    },
]


def by_slug(slug):
    for guide in GUIDES:
        if guide["slug"] == slug:
            return guide
    return None


def _claimed_subjects():
    out = set()
    for guide in GUIDES:
        for subject in guide["subjects"]:
            out.add(canonical(subject))
    return out


def gaps(curricula):
    """Subjects this household teaches that no guide covers yet.

    Derived rather than listed, so adding a Science course makes Science appear
    here on its own — and writing the guide makes it disappear.
    """
    claimed = _claimed_subjects()
    seen = {}
    for curriculum in curricula:
        key = canonical(curriculum.subject)
        if not key or key in claimed:
            continue
        # Keep the household's own wording for the label; canonical() is only
        # the matching key and is often lowercased or collapsed.
        seen.setdefault(key, (curriculum.subject or key).strip())
    rows = [{"label": v, "emoji": emoji_for(v)} for v in seen.values()]
    return sorted(rows, key=lambda r: r["label"].lower())
