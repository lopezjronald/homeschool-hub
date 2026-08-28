"""California Studies Weekly — the framework both children's weeks are built on.

Studies Weekly ships one newspaper-style issue per week per grade, each with a
student article, a vocabulary list, a comprehension check, and a teacher edition
carrying the standards each question assesses. Violet is on Level 3 (Continuity
and Change) and Kaylin on Level 7 (World History and Geography: Medieval and
Early Modern Times).

WHY A FRAMEWORK AND NOT TWO CURRICULA: this is a weekly subscription. Week 2
should be a content file and a seed run, not another build. So the shapes live
here, each week is a module (`weekly_l7w1`, `weekly_l3w1`, …), and one command
seeds any of them:

    python manage.py seed_weekly --level 7 --week 1 --for-user ronald

A WEEK is:

    level, week, unit, lesson       where it sits in the year
    title, essential_question       the issue's own framing
    pages                           the real article pages, as images
    vocabulary                      [(term, definition)] from the issue's sidebar
    questions                       the comprehension check, in printed order
    standards                       what the teacher edition says each one assesses

A QUESTION is one of:

    choice      pick one, or pick several; options may be pictures
    order       a scrambled list she numbers back into sequence
    fill_two    a sentence with two blanks, each from its own small bank
    matching    match each prompt to the thing that answers it
    written     an open answer she types or writes by hand

The figures are CROPPED FROM THE ISSUE rather than sourced from the web: the
questions say "study the map", and only that map will do.
"""

# Where the cropped figures live, per week.
FIGURE_ROOT = "weekly"

# Where a step of the routine happens. No third value on purpose: the useful
# distinction is "this needs me" versus "this runs without me".
VOICE = "out loud"
SCREEN = "her screen"


def figure(level, week, name):
    """Static path for one of a week's cropped figures."""
    return "%s/l%dw%d/%s.jpg" % (FIGURE_ROOT, level, week, name)


def page_images(level, week, count):
    """The issue's own article pages, in order."""
    return ["%s/l%dw%d/page%d.jpg" % (FIGURE_ROOT, level, week, n)
            for n in range(1, count + 1)]


# ---------------------------------------------------------------------------
# Question builders. These return the dicts the seed turns into Question rows,
# so a week file reads like the printed page rather than like the ORM.
# ---------------------------------------------------------------------------

def choice(prompt, options, correct, *, multi=False, figure=None,
           figure_caption="", hint="", standard=""):
    """Pick one (or several). `options` is [(key, text)] or [(key, text, image)]."""
    opts = []
    for o in options:
        key, text = o[0], o[1]
        opts.append({"key": key, "text": text,
                     "image": o[2] if len(o) > 2 else ""})
    return {
        "kind": "choice", "prompt": prompt, "options": opts,
        "correct": [correct] if isinstance(correct, str) else list(correct),
        "multi": multi, "figure": figure or "", "figure_caption": figure_caption,
        "hint": hint, "standard": standard,
    }


def fill_two(prompt, bank_a, bank_b, correct_a, correct_b, *, figure=None,
             figure_caption="", hint="", standard=""):
    """A sentence with two blanks, each chosen from its own short list.

    Rendered as two choice questions rather than one, because the printed page
    gives each blank its own bank and a child who gets A right and B wrong has
    got half of it right — which a single combined answer cannot record.
    """
    return {
        "kind": "fill_two", "prompt": prompt,
        "bank_a": bank_a, "bank_b": bank_b,
        "correct_a": correct_a, "correct_b": correct_b,
        "figure": figure or "", "figure_caption": figure_caption,
        "hint": hint, "standard": standard,
    }


def matching(prompt, pairs, *, word_order=None, hint="", standard=""):
    """Match each question to the thing that answers it. `pairs` is [(left, right)].

    `word_order` is the order the right-hand column is PRINTED in. Give it
    whenever the page scrambles that column, which it usually does: without it
    the two columns come out row-aligned and she can match them by position
    without reading either side.
    """
    pairs = list(pairs)
    answers = [right for _left, right in pairs]
    # The widget keys a match on the answer's TEXT, so two identical answers are
    # one button she can only ever match to one of the two questions.
    if len(set(answers)) != len(answers):
        raise ValueError(
            "matching(): two questions share an answer, and the widget matches "
            "on the answer text — one of them could never be completed.")
    if word_order is not None:
        word_order = list(word_order)
        if sorted(word_order) != sorted(answers):
            raise ValueError(
                "matching(): word_order must be the same answers as the pairs, "
                "reordered — a word only in one of them can never be matched.")
    return {"kind": "matching", "prompt": prompt, "pairs": pairs,
            "word_order": word_order, "hint": hint, "standard": standard}


def order(prompt, steps, correct, *, hint="", standard=""):
    """Put a scrambled list back into its right sequence.

    Studies Weekly calls this "sorting". `steps` is the order they are PRINTED
    in; `correct` is the order they belong in. They must be the same strings —
    a step in one list and not the other is a question she cannot get right.
    """
    steps, correct = list(steps), list(correct)
    # The widget keys each step on its TEXT, so two identical steps hydrate to
    # the same number and there is no ordering she can enter that is right.
    if len(set(steps)) != len(steps):
        raise ValueError(
            "order(): two steps read the same, and the widget keys a step on "
            "its text — no ordering of them could be marked correct.")
    if sorted(steps) != sorted(correct):
        raise ValueError(
            "order(): the printed steps and the answer are not the same set — "
            "%r vs %r" % (sorted(steps), sorted(correct)))
    return {"kind": "order", "prompt": prompt, "steps": steps,
            "correct": correct, "hint": hint, "standard": standard}


def written(prompt, *, hint="", standard="", answer_mode=True, figure=None,
            figure_caption=""):
    """An open answer. `answer_mode` offers her the type-it/write-it picker.

    Takes a `figure` for the same reason the choice questions do: the printed
    check asks several open questions ABOUT a picture ("study the image", "study
    sources A and B"), and without it those arrive as a wall of words asking her
    to look at something that is not there.
    """
    return {"kind": "written", "prompt": prompt, "hint": hint,
            "standard": standard, "answer_mode": answer_mode,
            "figure": figure or "", "figure_caption": figure_caption}


def step(do, where=VOICE):
    """One step of the week's routine, and where it happens.

    `where` is the whole point of the table. Half of what the teacher edition
    prescribes is spoken, away from any screen, and half runs on the child's
    page without you. Marking which is which is what lets a parent see, at a
    glance, the part that needs them.
    """
    return {"do": do, "where": where}


def routine(steps, short=()):
    """The week's teaching sequence, plus the version for a bad day.

    `short` is not an afterthought. Rigid schedules fail on the first disrupted
    day, and a parent who has run out of afternoon will drop something whether
    the guide says so or not — so the guide says which, in advance, instead of
    leaving it to be decided at 4pm.
    """
    return {"steps": list(steps), "short": list(short)}


def week_module(level, week):
    """Import a week's content module, or raise something a human can act on."""
    import importlib

    name = "tutor.weekly_l%dw%d" % (level, week)
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "No content for Level %d Week %d — expected %s.py. Each week is its "
            "own module; copy the nearest one and work from the issue."
            % (level, week, name.replace(".", "/"))
        ) from exc


# ---------------------------------------------------------------------------
# Units, sub-units and the film that opens one.
#
# A Studies Weekly unit is not a flat run of weeks: Unit 1 is Lesson 1, Lesson 2
# (printed as 2.1 and 2.2) and Lesson 3 (3.1 and an activity, 3.2), with one
# comprehension check per LESSON and one assessment per UNIT. A week module
# therefore describes one lesson and lists its parts, and the booklet page reads
# that structure back out.
# ---------------------------------------------------------------------------

def video(youtube_id, title, *, channel, length, why, question=""):
    """A short film that sets a part up, played before any reading.

    `length` is written as a human string ("about 5 minutes") rather than a
    number of seconds: YouTube does not publish a duration we can read without
    an API key, so a precise figure here would be invented. `question` is what
    she should be able to answer afterwards — a video nobody has to think about
    is a break, not a lesson.
    """
    if not youtube_id or " " in youtube_id:
        raise ValueError("video(): %r is not a YouTube id" % (youtube_id,))
    return {"youtube_id": youtube_id, "video_title": title, "channel": channel,
            "length": length, "why": why, "question": question}


def part(number, title, *, pages, watch=None, vocabulary=(), intro="",
         activity=False):
    """One sub-unit — the "2.1" of Unit 1, Lesson 2.

    `pages` are its printed pages, in order. `watch` is an optional video()
    shown before them. `activity` marks a part that is something to DO rather
    than something to read, so the booklet can say so.
    """
    return {"number": str(number), "title": title, "pages": list(pages),
            "watch": watch, "vocabulary": list(vocabulary), "intro": intro,
            "activity": bool(activity)}


def parts_of(mod):
    """A module's parts, or one implicit part for the older flat weeks.

    Level 3 and the first Level 7 issue were written before units had sub-units,
    and they still seed and still render — a week with no PARTS is a lesson with
    exactly one part, which is what those are.
    """
    declared = getattr(mod, "PARTS", None)
    if declared:
        return list(declared)
    return [part(getattr(mod, "LESSON", "1"), mod.TITLE, pages=mod.PAGES,
                 watch=getattr(mod, "WATCH", None),
                 vocabulary=getattr(mod, "VOCABULARY", ()),
                 intro=getattr(mod, "STUDENT_NOTE", ""))]
