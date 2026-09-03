"""Writing a module's questions onto a set without moving a child's answers.

THE BUG THIS EXISTS TO END. Every seeder used to upsert on POSITION:

    Question.objects.update_or_create(question_set=qset, order=order,
                                      defaults={"prompt": ..., ...})

Her answers are keyed on the question's PK, and the pk belongs to the position.
So deleting or inserting a question in the MIDDLE of a guide rewrote the content
of every row after it while the pks stayed put: her answer to "Who is Rose Lee
afraid of?" silently became her answer to whatever question moved up into that
slot. The seeder printed a success line. Nothing warned anybody, and the wrong
answer then printed under the wrong prompt in the charter report.

These modules are hand transcriptions of printed guides that openly invite
corrections — "this question is a duplicate", "the guide misnumbered these" —
so editing the middle is the ORDINARY case, not an exotic one.

THE FIX: match on the PROMPT instead. A question then keeps its pk wherever it
moves to, so her answer follows the words she actually answered; a corrected
hint or response type still lands; and only genuinely new wording gets a new
row. The same approach is in seed_weekly.py, where this was found first.

Two details that are not optional:

* Existing rows are PARKED above the range before anything is assigned.
  (question_set, order) is unique, so renumbering in place collides the moment
  two questions swap places.
* Prompts are NOT unique — a guide can ask "What surprised you?" in two
  sections — so the index holds a LIST per prompt and hands them out oldest
  first. A plain dict would collapse them and re-attribute an answer.
"""

from django.db.models import F

#: Existing rows are moved above this before new orders are assigned. Higher
#: than any real question count by a wide margin.
_PARK = 10000

#: How alike two promptings must read before the position fallback will treat
#: them as the same question REWORDED rather than a different question put in
#: the same slot. Only consulted for a question she has actually answered —
#: for an unanswered row it does not matter who claims it.
SIMILAR_ENOUGH = 0.6


def looks_reworded(before, after):
    """Is `after` a corrected version of `before`, or a different question?

    "teh quarrel" -> "the quarrel" is a typo fix and must keep its pk, so her
    answer stays attached. "Who is Rose Lee afraid of?" -> "What does Naima
    paint on the walls?" is a REPLACEMENT, and claiming that slot would leave
    her answer sitting under a question she never read.
    """
    import difflib

    if before == after:
        return True
    return difflib.SequenceMatcher(None, before, after).ratio() >= SIMILAR_ENOUGH


def as_row(item):
    """Normalise a seeder's (category, prompt, hint[, extra]) tuple.

    Every literature seeder in this app builds questions in that shape, with an
    optional 4th element carrying response_type/passage.
    """
    from tutor.models import Question

    category, prompt, hint = item[0], item[1], item[2]
    # `or {}` because two seeders pass an explicit None for "no extras".
    extra = (item[3] if len(item) > 3 else None) or {}
    return {
        "category": category,
        "prompt": prompt,
        "hint": hint,
        "response_type": extra.get("response_type", Question.TYPE_TEXT),
        "passage": extra.get("passage", ""),
    }


def answered_pks(qset):
    """Every question in this set that carries work of hers.

    Typed answers live in ResponseSheet.answers, keyed by question pk. A
    PHOTOGRAPH does not: it is an AnswerPhoto row whose question FK is CASCADE,
    so a step she photographed and never typed on looked unanswered and was
    deleted along with her image.
    """
    from tutor.models import AnswerPhoto, ResponseSheet

    answered = set()
    for sheet in ResponseSheet.objects.filter(question_set=qset):
        answered |= {int(k) for k, v in (sheet.answers or {}).items()
                     if str(v).strip() and str(k).isdecimal()}
    answered |= set(AnswerPhoto.objects.filter(
        question__question_set=qset).values_list("question_id", flat=True))
    return answered


def sync_questions(qset, items):
    """Make `qset`'s questions match `items`, keeping her answers attached.

    Returns the pks of rows the module no longer declares but which were KEPT
    because she has answered them — the caller decides whether to say so.
    """
    from tutor.models import Question

    rows = [as_row(item) for item in items]

    # Prompt -> its rows, oldest first. A list, because prompts repeat: a guide
    # can ask "What surprised you?" in two sections, and a plain dict would
    # collapse them and hand one child's answer to the other question.
    by_prompt = {}
    by_order = {}
    for question in qset.questions.order_by("order", "pk"):
        by_prompt.setdefault(question.prompt, []).append(question)
        by_order.setdefault(question.order, question)

    # Needed BEFORE the claiming, not just for the prune: pass 2 must know
    # which rows carry her work before it decides to overwrite one.
    answered = answered_pks(qset)

    # Park them all above the range we are about to assign.
    qset.questions.update(order=F("order") + _PARK)

    # TWO passes, and the second one is why a corrected typo still lands.
    #
    # Pass 1 claims by prompt: that is what makes an answer follow its question
    # when a deletion in the middle shifts everything up.
    #
    # Pass 2 claims what is left by POSITION. Without it, editing the wording of
    # a question — fixing a transcription typo, which is most of what these
    # modules get — would find no prompt match, build a NEW row, and strand her
    # answer on the old one. With it, a reworded question keeps its pk and her
    # answer, because nothing else claimed that slot.
    claimed = {}
    taken = set()
    for index, row in enumerate(rows):
        candidates = by_prompt.get(row["prompt"])
        while candidates:
            question = candidates.pop(0)
            if question.pk not in taken:
                claimed[index] = question
                taken.add(question.pk)
                break
    for index, row in enumerate(rows):
        if index in claimed:
            continue
        question = by_order.get(index + 1)
        if question is None or question.pk in taken:
            continue
        # ...but never over the top of her work. Claiming by position is a
        # guess that the slot still means the same thing, and for a question
        # she has ANSWERED a wrong guess is the very corruption this module
        # exists to prevent: her answer would end up under wording she never
        # read. When the new prompt is not recognisably the old one reworded,
        # leave the row alone — the prune below keeps it, and the new wording
        # gets a row of its own.
        if question.pk in answered and not looks_reworded(question.prompt,
                                                          row["prompt"]):
            continue
        claimed[index] = question
        taken.add(question.pk)

    seen = []
    for index, row in enumerate(rows):
        order = index + 1
        question = claimed.get(index)
        if question is None:
            question = Question.objects.create(
                question_set=qset, order=order, **row)
        else:
            for field, value in dict(row, order=order).items():
                setattr(question, field, value)
            question.save()
        seen.append(question.pk)

    # Anything the module no longer declares goes — unless she answered it.
    stale = qset.questions.exclude(pk__in=seen)
    kept = sorted(stale.filter(pk__in=answered).values_list("pk", flat=True))
    stale.exclude(pk__in=answered).delete()

    # Bring the kept ones back down, after the real questions, so nothing is
    # left sitting at 10000-something where the page would order it oddly.
    #
    # They land AFTER the live rows, which is also the range a growing guide
    # claims next — so the position fallback above deliberately refuses to
    # overwrite them. Without that refusal, adding a question to the guide
    # would silently drop new wording onto the row holding her old answer.
    for offset, pk in enumerate(kept, start=1):
        Question.objects.filter(pk=pk).update(order=len(rows) + offset)
    return kept
