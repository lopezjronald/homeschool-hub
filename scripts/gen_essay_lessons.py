"""Emit tutor/essay_lessons.py from the verified page transcriptions.

Generated rather than hand-typed: the prompts are the guide's words, and
retyping five lessons of them by hand is exactly how a transcription picks up
errors the reviewers then have to find.

Two normalisations, both because the app has no page breaks:
  - a section with an EMPTY heading is a continuation of the one before it onto
    the next printed page, and is merged into it;
  - a prompt with no ruled answer line is not a question. It is either a
    checklist lead-in ("Now ask yourself:") or one of the self-check questions
    under it, so those become the section's `checks` rather than answer boxes.
"""

import json
import sys
import textwrap

SRC, OUT = sys.argv[1], sys.argv[2]
LESSONS = json.load(open(SRC, encoding="utf-8"))

TITLES = {1: "Write an Orange", 2: "Write a Person", 3: "Write an Object",
          4: "Write a Photograph", 5: "Write a Room"}

# Where the printed guide would send her wrong. Everything here was read off the
# page twice, by two readers, and is transcribed into the prompts VERBATIM — the
# note sits beside the printed words rather than replacing them, because the
# book on the table still says what it says.
NOTES = {
    1: [("odd", "The guide asks about “complimentary colors” and tells you to go "
        "and research it. The colour-theory word is COMPLEMENTARY — colours "
        "that complete each other, like blue and orange. “Complimentary” "
        "means flattering, or free of charge. Research the one the guide means, "
        "not the one it spells.")],
    3: [("odd",
        "The Monet quotation opens with the wrong curly quote — the mark that "
        "should close a quotation is used to open it. Copy the words, not the "
        "typo.")],
}

# "Thinking In Threes" is referred to in EVERY lesson — once in a task and once
# in the self-check — and exists in none of them; it is a section of another
# book in the series. The note was first written for two lessons only, which
# left her sent to a missing section unexplained in the other three.
THREES_NOTE = ("This lesson points you at an exercise called “Thinking In "
               "Threes”. There is no section by that name in this book — it is "
               "in another book in the series. It means what the thesis "
               "statement work has been doing all along: THREE sub-topics, all "
               "phrased in the same grammatical shape.")

# The guide sends her back to a printed page for work she did on screen.
PAPER_PAGE_NOTE = ("The Body Paragraphs task says to take a sub-topic “from "
                   "page %s”. That is a page of the paper book, and yours are "
                   "up above on this page — scroll back to the three sub-topics "
                   "you wrote and pick one of those.")

# The blueprint checklist labels its last paragraph "PS»" instead of "P5»" in
# three of the five lessons — verified page by page, not assumed. It is a
# typesetting slip in the same list that runs P1», P2», P3», P4».
PS_TYPO_LESSONS = {1, 3, 5}
PS_WEEK = "even"  # the blueprint checklist is on the drafting week, not the first
PS_NOTE = ("In your PAPER book, the last row of this lesson's blueprint "
           "checklist is labelled “PS» CONCLUSION”. That is a "
           "typo for “P5»” — it is paragraph 5, the conclusion. "
           "Lessons 2 and 4 print it correctly, which is how we know. The "
           "checklist on this page says P5.")


def merge(sections):
    """Fold page-break continuations into the section they continue."""
    out = []
    for s in sections:
        if s["week"] % 2 == 0:
            continue  # the even week is identical in every lesson; see essay.py
        if not (s["heading"] or "").strip() and out:
            out[-1]["prompts"].extend(s["prompts"])
            if s.get("instruction") and not out[-1].get("instruction"):
                out[-1]["instruction"] = s["instruction"]
            continue
        out.append(dict(s, prompts=list(s["prompts"])))
    return out


# Quotation marks the second reader found had been silently "upgraded": the
# page prints straight typewriter quotes around these, and a transcription that
# reads tidier than the page is a defect, not a courtesy. Keyed by a stable
# fragment so a re-run cannot apply them to the wrong prompt.
STRAIGHTEN = ["I like to see a man proud of the place in which he lives"]


def straighten(text):
    if not any(k in text for k in STRAIGHTEN):
        return text
    return text.replace("“", '"').replace("”", '"')


def descaffold(text):
    """Strip the readers' own layout markers.

    They were asked to describe the page, and "[arrow callout]" is them saying
    "the next sentence sits in one of the guide's arrow boxes". That is a note
    about the paper, not something the book says — and these instructions
    become the hint she opens when she is stuck, so it was being shown to her
    fifteen times over.
    """
    for marker in ("[arrow callout]", "[Each scored line has a rule]"):
        text = text.replace(marker, " ")
    return " ".join(text.split())


SUBTOPIC_LEAD = "Choose three sub-topics to focus on in your essay."


def expand_subtopics(prompts):
    """Three numbered rules, not one three-line box.

    Two of the five readers recorded the slots the page actually prints ("1."
    "2." "3." each on its own rule) and three collapsed them into a single
    prompt with three blank lines; the second reader confirmed the slots on
    p21. The layout is the same in all five lessons, so it is normalised here
    rather than left to differ by whoever read the page.
    """
    out = []
    i = 0
    while i < len(prompts):
        p = prompts[i]
        text = " ".join((p["text"] or "").split())
        if text != SUBTOPIC_LEAD:
            out.append(p)
            i += 1
            continue
        # Swallow any slots a reader already captured, so they are not counted twice.
        i += 1
        while i < len(prompts) and not (prompts[i]["text"] or "").strip() \
                and (prompts[i].get("number") or "").strip():
            i += 1
        for n in (1, 2, 3):
            head = "Sub-topic %d of 3" % n
            out.append({
                "text": "%s\n\n%s" % (SUBTOPIC_LEAD, head) if n == 1 else head,
                "number": "%d." % n,
                "answer_lines": 1,
            })
    return out


CHECK_LEAD = "Now ask yourself:"


def split_checks(prompts):
    """Sort the page's lines into answer boxes, self-checks, and instructions.

    A prompt with no ruled line under it is not a question, but it is not all
    one thing either. Across the five lessons there are exactly three kinds,
    and the first cut at this ("ends with a colon ⇒ it introduces a checklist")
    got two of them wrong — it turned "Now write the final pair of sentences
    and the clincher." into a self-check she was asked to rate Yes/Not yet, and
    it would have done the same to "Choose one of your three sub-topics … and
    outline three pairs of factual and sensory details:", which introduces the
    boxes rather than a checklist.

      ends with "?"          a genuine self-check ("Have I thought in threes?")
      exactly CHECK_LEAD     the checklist's own lead-in
      anything else          an instruction for the boxes below it, which
                             belongs with the section's instruction text
    """
    asks, lead, checks, told = [], "", [], []
    for p in prompts:
        text = straighten("\n".join(
            " ".join(line.split()) for line in (p["text"] or "").splitlines()))
        if not text:
            # Nothing should reach here once the numbered sub-topic slots are
            # expanded. Shout rather than drop it: a prompt that vanishes
            # silently is a page of her work that never gets asked.
            raise SystemExit("empty prompt text with number=%r — a slot was "
                             "dropped; teach the generator about it"
                             % (p.get("number"),))
        if p["answer_lines"] > 0:
            number = (p.get("number") or "").strip()
            # The book's own numbering goes INTO the prompt. The body-paragraph
            # warm-up prints "1a. FACTUAL (TELL): / 1b. SENSORY (SHOW): / 2a. …"
            # — six rules, three distinct labels — and one reader baked the
            # numerals into the text while three left them in `number`. Left
            # there, half the lessons showed her "FACTUAL (TELL):" twice and
            # "SENSORY (SHOW):" three times with no way to tell the pairs apart.
            if number and not text.startswith(number):
                text = "%s %s" % (number, text)
            asks.append({"text": text, "number": number,
                         "lines": p["answer_lines"]})
        elif text.endswith("?"):
            checks.append(text)
        elif text == CHECK_LEAD:
            lead = text
        else:
            told.append(text)
    return asks, lead, checks, told


def py(value, indent):
    """A readable literal — long strings wrapped, not run off the screen.

    `replace_whitespace=False` matters: textwrap turns a newline into a space by
    default, which silently rewrote the sub-topic lead — "…in your essay.\\n\\n
    Sub-topic 1 of 3" was emitted as one line with a double space, in the file
    the whole design treats as the source of truth. Only strings over the wrap
    width were affected, which is why it went unnoticed.
    """
    pad = " " * indent
    if isinstance(value, str):
        if len(value) <= 68 or "\n" in value:
            return repr(value)
        parts = textwrap.wrap(value, 66, break_long_words=False,
                              drop_whitespace=False, replace_whitespace=False)
        return ("\n" + pad).join(repr(p) for p in parts)
    return repr(value)


lines = ['"""The five essays of The Essay, Volume 2 — the guide\'s own pages.',
         "",
         "GENERATED by scripts/gen_essay_lessons.py from the page transcriptions;",
         "edit that, or the guide, rather than this file. The front matter, the",
         "blueprint and both grading forms live in tutor/essay.py, and the EVEN week",
         "of every lesson is built from them — it is the same five pages each time",
         "(rough draft, blueprint checklist, self-evaluation, final draft, teacher's",
         "form), so only the ODD week is described here.",
         "",
         "Printed quirks are preserved verbatim and called out in `notes`.",
         '"""', "", "LESSONS = ["]

for L in LESSONS:
    n = L["lesson_number"]
    secs = merge(L["sections"])
    vocab = []
    steps = []
    for s in secs:
        asks, lead, checks, told = split_checks(expand_subtopics(s["prompts"]))
        head = " ".join((s["heading"] or "").split())
        if s["kind"] == "reference" and head.lower().startswith("use a dictionary"):
            vocab = [a["text"] for a in asks]
            continue
        steps.append({
            "heading": head,
            # The unlined instruction lines join the section's own instruction,
            # in printed order after it. That is where "Hand write your rough
            # draft on the following pages" and "Type your final draft with
            # double line spacing" live — the guide's directions about HOW to
            # produce the essay, which she should read even though the app
            # gives her boxes.
            "instruction": descaffold(" ".join(
                x for x in [" ".join((s.get("instruction") or "").split())] + told
                if x)),
            "kind": s["kind"],
            "prompts": asks,
            "check_lead": lead,
            "checks": checks,
        })
    lines.append("    {")
    lines.append("        'number': %d," % n)
    lines.append("        'title': %r," % TITLES[n])
    lines.append("        'weeks': (%d, %d)," % (2 * n - 1, 2 * n))
    lines.append("        'banner': %s," % py(" ".join((L.get("intro_banner") or "").split()), 12))
    lines.append("        'vocabulary': %r," % (vocab,))
    lines.append("        'steps': [")
    for st in steps:
        lines.append("            {")
        lines.append("                'heading': %r," % st["heading"])
        lines.append("                'kind': %r," % st["kind"])
        if st["instruction"]:
            lines.append("                'instruction': %s," % py(st["instruction"], 20))
        lines.append("                'prompts': [")
        for a in st["prompts"]:
            lines.append("                    {'text': %s," % py(a["text"], 22))
            lines.append("                     'number': %r, 'lines': %d}," % (a["number"], a["lines"]))
        lines.append("                ],")
        if st["checks"]:
            if st["check_lead"]:
                lines.append("                'check_lead': %r," % st["check_lead"])
            lines.append("                'checks': [")
            for c in st["checks"]:
                lines.append("                    %s," % py(c, 20))
            lines.append("                ],")
        lines.append("            },")
    lines.append("        ],")
    notes = list(NOTES.get(n, []))
    # Derived from the pages, not from a hand-kept list of which lessons need
    # it: every lesson that actually mentions the missing section gets warned.
    # Two plain scans rather than one nested comprehension. The compact version
    # of this looped `for st in steps for p in st["prompts"] for c in st["checks"]`,
    # which cannot see a step that carries checks but no prompts — the inner
    # loop never runs. It happened to give the right answer on these five
    # lessons and would have silently stopped doing so the moment the guide, or
    # a re-transcription, put a self-check on a page with no answer boxes.
    mentions_threes = any(
        "Thinking In Threes" in p["text"]
        for st in steps for p in st["prompts"])
    mentions_threes = mentions_threes or any(
        "thought in threes" in c.lower()
        for st in steps for c in st["checks"])
    if mentions_threes:
        notes.insert(0, ("odd", THREES_NOTE))
    # "Choose one of your three sub-topics from page 32…" — she typed those
    # sub-topics into this app a few questions ago, so the paper page the guide
    # names is blank. Derived from the text so no lesson can be missed.
    import re as _re
    paper_ref = sorted({m for st in steps
                        for m in _re.findall(r"from page (\d+)", st["instruction"])})
    if paper_ref:
        notes.append(("odd", PAPER_PAGE_NOTE % ", ".join(paper_ref)))
    if n in PS_TYPO_LESSONS:
        notes.append((PS_WEEK, PS_NOTE))
    if notes:
        lines.append("        'notes': [")
        for where, note in notes:
            assert where in ("odd", "even", "both"), where
            lines.append("            {'where': %r," % where)
            lines.append("             'text': %s}," % py(note, 22))
        lines.append("        ],")
    lines.append("    },")
lines.append("]")
lines.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("wrote", OUT, len(lines), "lines")
