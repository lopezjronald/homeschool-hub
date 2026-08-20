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


def written(prompt, *, hint="", standard="", answer_mode=True):
    """An open answer. `answer_mode` offers her the type-it/write-it picker."""
    return {"kind": "written", "prompt": prompt, "hint": hint,
            "standard": standard, "answer_mode": answer_mode}


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
