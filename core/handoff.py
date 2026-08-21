"""What the girls finished, and where they are up to — for the other household.

WHY THIS EXISTS. The children's school work moves between two houses. Without
this, the handover conversation is "what did you do?" followed by somebody
guessing, and the receiving parent either repeats a week or skips one.

WHAT IT IS, PRECISELY: an outbound report, not a messaging system. No inbox, no
threads, no replies to keep on top of. One parent composes it, reads it, and
sends it. Building the small thing well beats building a chat nobody opens.

THE PART THAT ACTUALLY MATTERS is not the list of what was finished — it is
``next_up``. Whoever picks the children up on Thursday does not need a
transcript; they need to know to start Violet on Week 2. Everything else is
supporting detail.

Nothing here sends anything. Composing and sending live in the view, because a
message to somebody outside the app is never something this should decide on
its own.
"""

from dataclasses import dataclass, field
from datetime import timedelta

from django.utils import timezone


@dataclass
class Item:
    """One finished piece of work, as a line the other parent can act on."""

    key: str                      # stable id for the checkbox: "sheet:123"
    subject: str
    title: str
    detail: str = ""              # "8 of 8 answered · Proficient"
    finished_on: object = None
    lesson_id: object = None      # what she finished, for working out what is next

    def as_line(self):
        return "✓ %s%s" % (self.title, " — %s" % self.detail if self.detail else "")


@dataclass
class SubjectSummary:
    """One course: what was finished in it, and what follows.

    Grouped by course rather than listed flat because the pairing IS the
    message — "we did week 1, so she starts week 2" — and a next-up line
    floating away from the work it follows makes the reader do that join
    themselves.
    """

    curriculum: object
    items: list = field(default_factory=list)
    next_up: str = ""

    @property
    def name(self):
        return self.curriculum.name

    @property
    def lesson_ids(self):
        return {i.lesson_id for i in self.items if i.lesson_id}


@dataclass
class ChildSummary:
    child: object
    subjects: list = field(default_factory=list)

    @property
    def items(self):
        return [item for s in self.subjects for item in s.items]

    @property
    def has_anything(self):
        return bool(self.subjects)


def default_since(family, *, days=7):
    """The window, defaulting to whenever the last handoff went out.

    Falling back to a week rather than to "everything" — a first handoff that
    dumps the entire school year is not a handoff, it is an archive.
    """
    from core.models import Handoff

    last = (Handoff.objects.filter(family=family, sent_at__isnull=False)
            .order_by("-sent_at").first())
    if last is not None:
        return last.covers_since
    return timezone.now() - timedelta(days=days)


def summarise(child, since, until=None):
    """Everything `child` finished in the window, plus where they are now."""
    from curricula.models import CurriculumPlacement, LessonProgress
    from tutor.models import ResponseSheet

    until = until or timezone.now()
    by_curriculum = {}

    def bucket(curriculum):
        if curriculum.pk not in by_curriculum:
            by_curriculum[curriculum.pk] = SubjectSummary(curriculum=curriculum)
        return by_curriculum[curriculum.pk]

    sheets = (ResponseSheet.objects
              .filter(child=child, submitted_at__gte=since, submitted_at__lte=until)
              .select_related("question_set__lesson__chapter__curriculum")
              .order_by("submitted_at"))
    for sheet in sheets:
        qset = sheet.question_set
        curriculum = qset.lesson.chapter.curriculum
        bucket(curriculum).items.append(Item(
            key="sheet:%d" % sheet.pk,
            subject=curriculum.name,
            title=qset.title,
            detail=_sheet_detail(sheet),
            finished_on=sheet.submitted_at,
            lesson_id=qset.lesson_id,
        ))

    marks = (LessonProgress.objects
             .filter(child=child, status=LessonProgress.COMPLETED,
                     updated_at__gte=since, updated_at__lte=until)
             .select_related("lesson__chapter__curriculum")
             .order_by("updated_at"))
    for mark in marks:
        curriculum = mark.lesson.chapter.curriculum
        bucket(curriculum).items.append(Item(
            key="lesson:%d" % mark.pk,
            subject=curriculum.name,
            title=mark.lesson.title,
            detail="marked finished",
            finished_on=mark.updated_at,
            lesson_id=mark.lesson_id,
        ))

    # Next-up ONLY for courses that were actually worked on. Listing every
    # active placement turned an eight-subject child into an eight-line wall
    # of "next", which is the opposite of telling somebody where to start.
    placements = {p.curriculum_id: p for p in
                  CurriculumPlacement.objects
                  .filter(child=child, curriculum_id__in=by_curriculum,
                          is_active=True, curriculum__is_active=True)
                  .select_related("curriculum", "current_lesson")}
    for pk, subject in by_curriculum.items():
        subject.items.sort(key=lambda i: i.finished_on or until)
        placement = placements.get(pk)
        nxt = _next_lesson(placement, subject.lesson_ids) if placement else None
        if nxt is not None:
            subject.next_up = nxt.title

    return ChildSummary(
        child=child,
        subjects=sorted(by_curriculum.values(), key=lambda s: s.name),
    )


def _sheet_detail(sheet):
    """How it went, in the fewest words that are still true.

    The mastery level only appears once a parent has FINALIZED it. An AI draft
    is not a grade, and sending one to the other household as though it were
    would put a number on a child's work that nobody has agreed to yet.
    """
    bits = []
    # Work done on PAPER stores no answers, so a count would report a child who
    # filled in a whole worksheet by hand as "0 of 10 answered" — to the other
    # parent, who would reasonably read that as her having done nothing.
    if getattr(sheet, "is_on_paper", False):
        bits.append("on paper")
    else:
        total = sheet.question_set.questions.count()
        answered = sheet.answered_count
        if total and answered:
            bits.append("%d of %d answered" % (answered, total))
        elif total:
            bits.append("turned in blank")
    level = _finalized_level(sheet)
    if level:
        bits.append(level)
    return " · ".join(bits)


def _finalized_level(sheet):
    from tutor.models import MasteryAssessment

    if not sheet.work_entry_id:
        return ""
    assessment = (MasteryAssessment.objects
                  .filter(work_entry_id=sheet.work_entry_id,
                          status=MasteryAssessment.FINALIZED)
                  .exclude(final_level="")
                  .order_by("-finalized_at").first())
    return assessment.get_final_level_display() if assessment else ""


def _next_lesson(placement, just_finished=()):
    """The lesson she should start next — the whole point of the message.

    `just_finished` is what this handoff is reporting. Turning work in does not
    move the placement pointer — a parent moves that — so without this the
    message would say "next: Week 1" in the same breath as "finished Week 1",
    and the other household would dutifully repeat the week. Which is the exact
    thing this feature exists to prevent.
    """
    lessons = list(placement.ordered_lessons()) if hasattr(placement, "ordered_lessons") else []
    if not lessons:
        from curricula.models import Lesson
        lessons = list(Lesson.objects
                       .filter(chapter__curriculum=placement.curriculum)
                       .order_by("chapter__number", "order"))
    if not lessons:
        return None
    try:
        _all_ids, resolved = placement.resolved_lesson_ids()
    except Exception:
        resolved = set()
    resolved = set(resolved) | set(just_finished)
    for lesson in lessons:
        if lesson.pk not in resolved:
            return lesson
    return None


def compose(summaries, note="", author=None):
    """The message itself, as plain text.

    Plain text on purpose. It has to survive being pasted into a Messages app
    as readily as it renders in an email, and a co-parent reading it on a phone
    in a car park should get the point from the first two lines.
    """
    blocks = []
    for summary in summaries:
        if not summary.has_anything:
            continue
        lines = [summary.child.first_name]
        for subject in summary.subjects:
            lines.append("  %s" % subject.name)
            lines += ["    %s" % item.as_line() for item in subject.items]
            if subject.next_up:
                lines.append("    → Next: %s" % subject.next_up)
        blocks.append("\n".join(lines))

    if note.strip():
        who = getattr(author, "first_name", "") or getattr(author, "username", "")
        label = "%s's note" % who if who else "Note"
        blocks.append("%s: %s" % (label, note.strip()))
    return "\n\n".join(blocks) if blocks else "Nothing to report for this stretch."
