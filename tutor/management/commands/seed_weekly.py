"""Seed one week of California Studies Weekly (idempotent).

    python manage.py seed_weekly --level 7 --week 1 --for-user ronald
    python manage.py seed_weekly --level 3 --week 1 --for-user ronald --dry-run

Studies Weekly is a SUBSCRIPTION: a new issue every week, per grade. So this
command is deliberately generic — it reads a week's content module
(tutor/weekly_l<level>w<week>.py) and builds the lesson from it. Adding week 2
means writing that module and running this; it does not mean writing a seeder.

One curriculum per child per level, one Lesson per week, one QuestionSet per
week. The week's article pages hang off the lesson as a Material so she can read
the real issue before answering — the layout is the lesson in a newspaper.
"""

import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor import weekly
from tutor.models import LessonBlock, Material, Question, QuestionSet, ResponseSheet

# Which child a level belongs to, and what the course is called. Level is the
# publisher's own grade banding, so this is also the grade check: seeding a
# Level 7 issue for a third-grader is a mistake worth refusing.
LEVELS = {
    3: {"child": "Violet", "grade": "G03",
        "name": "Studies Weekly 3 — Continuity and Change",
        "subject": "Social Studies"},
    7: {"child": "Kaylin", "grade": "G07",
        "name": "Studies Weekly 7 — World History and Geography",
        "subject": "Social Studies"},
}


def _unit_title(mod):
    """"Unit 1 — Historical Thinking Skills", or just "Unit 1" if unnamed."""
    named = getattr(mod, "UNIT_TITLE", "")
    return "Unit %s — %s" % (mod.UNIT, named) if named else "Unit %s" % mod.UNIT


# What to say to the grader when a week does not say it itself.
_DEFAULT_GRADER_NOTE = (
    "Look for whether she points at something the issue actually shows, rather "
    "than repeating a sentence from it."
)


def _routine_section(mod):
    """The week's teaching sequence, for the guide the parent already opens.

    The publisher prescribes a real weekly routine and prints it in a teacher
    edition — which is to say, somewhere other than where the teaching happens.
    Splitting a parent's attention between a PDF and the app is the reliable way
    to make the spoken half of a lesson quietly stop happening around week four.

    Ordered, and marked by WHERE each step happens, so the parts that need a
    grown-up separate at a glance from the parts that run on her screen. No
    timings: the publisher gives pacing for some weeks and marks others N/A, and
    a number I invented would read as theirs.
    """
    spec = getattr(mod, "ROUTINE", None)
    if not spec or not spec.get("steps"):
        return ""
    rows = "\n".join(
        "| %d | %s | %s |" % (i, s["do"], s["where"])
        for i, s in enumerate(spec["steps"], start=1))
    out = [
        "",
        "### This week, in order",
        "",
        "| # | Do this | Where |",
        "|---|---|---|",
        rows,
        "",
    ]
    if spec.get("short"):
        out += [
            "**If today is a write-off, do these three.** Not a lesser week — "
            "the rest is worth doing and this is what carries it when the "
            "afternoon has gone.",
            "",
            "\n".join("%d. %s" % (i, line)
                      for i, line in enumerate(spec["short"], start=1)),
            "",
        ]
    return "\n".join(out)


def _rubric(mod):
    """What the grader is told, in the issue's own terms."""
    standards = sorted({q.get("standard", "") for q in mod.QUESTIONS if q.get("standard")})
    return """## {pub} — Week {week}: {title}

{eq}

Most of this week is a comprehension check with right answers, and those are
marked automatically — you do not need to re-mark them. Judge the WRITTEN answer
at the end.

{grader_note}

If she answered by hand, the strokes are her answer; say so rather than guessing
at the words.

### What this week assesses
{standards}

Grade-{grade} mastery: Beginning → Developing → Proficient → Mastered.
""".format(pub=mod.PUBLICATION, week=mod.WEEK, title=mod.TITLE,
           eq="**Essential question:** " + mod.ESSENTIAL_QUESTION,
           grader_note=getattr(mod, "GRADER_NOTE", "").strip() or _DEFAULT_GRADER_NOTE,
           standards="\n".join("- " + s for s in standards) or "- (not recorded)",
           grade=mod.LEVEL)


class Command(BaseCommand):
    help = "Seed one week of California Studies Weekly for the level's child."

    def add_arguments(self, parser):
        parser.add_argument("--level", type=int, required=True, choices=sorted(LEVELS))
        parser.add_argument("--week", type=int, required=True)
        parser.add_argument("--for-user", required=True)
        parser.add_argument("--child-name", default="")
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        level, week = options["level"], options["week"]
        spec = LEVELS[level]
        mod = weekly.week_module(level, week)
        if mod.LEVEL != level or mod.WEEK != week:
            raise CommandError(
                "tutor/weekly_l%dw%d.py says it is Level %d Week %d — the file "
                "and its name disagree." % (level, week, mod.LEVEL, mod.WEEK))

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        name = options["child_name"] or spec["child"]
        child = Student.objects.filter(parent=user, first_name__iexact=name).first()
        if child is None:
            raise CommandError(f"No child named '{name}'.")
        if child.grade_level != spec["grade"]:
            raise CommandError(
                "%s is %s and Level %d is %s. Studies Weekly levels ARE grades; "
                "pass --child-name only if you mean to override that."
                % (child.first_name, child.grade_level, level, spec["grade"]))

        built = self._build(mod)
        if options["dry_run"]:
            for kind, prompt in built["preview"]:
                self.stdout.write("  %-9s %s" % (kind, prompt[:66]))
            self.stdout.write(self.style.WARNING(
                "Dry run — nothing written. Would seed Level %d Unit %s "
                "Lesson %s for %s: %d part(s), %d questions, %d article "
                "page(s)."
                % (level, mod.UNIT, getattr(mod, "LESSON", week),
                   child.first_name, len(weekly.parts_of(mod)),
                   built["count"], len(mod.PAGES))))
            return

        family = get_active_family(user)
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=spec["name"],
            defaults={"subject": spec["subject"], "grade_level": spec["grade"],
                      "family": family},
        )
        self.stdout.write("%s curriculum #%d"
                          % ("Created" if created else "Using", curriculum.pk))
        chapter, _ = Chapter.objects.get_or_create(
            curriculum=curriculum, number=mod.UNIT,
            defaults={"title": _unit_title(mod)},
        )
        # A unit that has since been given a name should get it on a reseed;
        # get_or_create only writes defaults when it creates.
        if chapter.title != _unit_title(mod):
            chapter.title = _unit_title(mod)
            chapter.save(update_fields=["title"])
        lesson, _ = Lesson.objects.update_or_create(
            chapter=chapter, order=week,
            defaults={"number": week,
                      "title": "Lesson %s · %s"
                               % (getattr(mod, "LESSON", week), mod.TITLE),
                      "objectives": mod.ESSENTIAL_QUESTION},
        )

        self._materials(lesson, child, family, mod)
        qset = self._question_set(lesson, family, mod)
        n = self._fill(qset, built["rows"])

        first = Lesson.objects.filter(chapter__curriculum=curriculum).order_by("order").first()
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum, defaults={"current_lesson": first})
        self.stdout.write(self.style.SUCCESS(
            "Seeded Level %d Week %d (%s) for %s — %d questions. %s"
            % (level, week, mod.TITLE, child.first_name, n,
               "Placed at week 1." if made else "Progress kept.")))

    # -- the week's reading -------------------------------------------------

    def _materials(self, lesson, child, family, mod):
        """One Material per SUB-UNIT — the 2.1 and 2.2 of a lesson.

        The publisher prints a lesson in numbered parts and the parts are
        genuinely different things: 3.1 is an article to read, 3.2 is a poster
        to build. Collapsing them into one page made the reading a wall of eight
        scans and gave the activity nowhere to live. A week with no PARTS still
        produces exactly one material, which is what the flat weeks were.
        """
        parts = weekly.parts_of(mod)
        made = []
        for index, spec in enumerate(parts, start=1):
            made.append(self._part_material(lesson, child, family, mod, spec,
                                            index, len(parts)))
        # A lesson that lost a part on a reseed should not keep its orphan page.
        Material.objects.filter(lesson=lesson).exclude(
            pk__in=[m.pk for m in made]).delete()
        return made

    def _part_material(self, lesson, child, family, mod, spec, index, total):
        label = "%s %s" % ("Activity" if spec["activity"] else "Part",
                           spec["number"])
        title = "%s · %s" % (label, spec["title"])
        # A reseed must not un-approve a part a parent has already approved:
        # the portal only shows APPROVED materials, so forcing DRAFT here would
        # make the reading vanish from the child's page mid-week. New ones still
        # start as drafts.
        existing = Material.objects.filter(lesson=lesson, title=title).first()
        pages = spec["pages"]
        if spec["activity"]:
            doing = "Work through the pages below, then build it."
        else:
            doing = ("Read %s below, then answer the questions."
                     % ("both pages" if len(pages) == 2
                        else "all %d pages" % len(pages)))
        intro = " ".join(x for x in (spec["intro"].strip(), doing,
                                     getattr(mod, "STUDENT_NOTE", "").strip())
                         if x)
        material, _ = Material.objects.update_or_create(
            lesson=lesson, title=title,
            defaults={
                "child": child, "family": family,
                "skill_type": Material.SKILL_LESSON,
                "student_intro": intro,
                "student_content": "",
                # The parent guide belongs on the FIRST part only. Repeating the
                # whole week's guidance under every part trains a parent to
                # scroll past it.
                "parent_content": self._parent_guide(mod) if index == 1 else "",
                "status": existing.status if existing else Material.DRAFT,
            },
        )
        blocks = [
            (LessonBlock.KIND_MASTHEAD, {
                "eyebrow": "%s · Unit %s · Lesson %s"
                           % (mod.PUBLICATION, mod.UNIT,
                              getattr(mod, "LESSON", mod.WEEK)),
                "title": "%s  %s" % (spec["number"], spec["title"]),
                "thesis": "**Essential question:** " + mod.ESSENTIAL_QUESTION,
            }),
        ]
        # The film goes FIRST, ahead of the reading it is there to set up.
        if spec["watch"]:
            blocks.append((LessonBlock.KIND_WATCH, dict(
                spec["watch"], title="Watch this first")))
        blocks.append((LessonBlock.KIND_PAGES, {
            "title": "%s in the issue" % label,
            "intro": "Tap a page to open it big enough to read.",
            "images": list(pages),
        }))
        if spec["vocabulary"]:
            blocks.append((LessonBlock.KIND_TRANSLATION, {
                "title": "Words in this part",
                "rows": [{"symbol": t, "plain": d, "example": ""}
                         for t, d in spec["vocabulary"]],
            }))
        LessonBlock.objects.filter(material=material).delete()
        for i, (kind, payload) in enumerate(blocks, start=1):
            LessonBlock.objects.create(material=material, order=i, kind=kind,
                                       data=payload)
        return material

    @staticmethod
    def _parent_guide(mod):
        graded = [("%d" % i, q.get("standard", "—"))
                  for i, q in enumerate(mod.QUESTIONS, start=1)]
        if getattr(mod, "REFLECTION", None):
            # Labelled, not numbered: the printed check stops at the last
            # question, and the writing task is the issue's own extra.
            graded.append(("Let's write",
                           mod.REFLECTION.get("standard", "—")))
        # By standard, not by question. Violet's week files all eight questions
        # under one ELA standard, and eight identical rows of standard text is
        # a table nobody reads — including the reviewer it exists for.
        by_standard = {}
        for label, standard in graded:
            by_standard.setdefault(standard, []).append(label)
        rows = "\n".join("| %s | %s |" % (standard, ", ".join(labels))
                         for standard, labels in by_standard.items())
        return """## Week {week}: {title}

**Essential question:** {eq}

The comprehension check is the issue's own, in its printed order and wording,
and its answers are the teacher edition's. Right answers are marked
automatically, so the only thing needing your eye is the written question at the
end — and whether she actually read the issue.

{note}
{routine}
### What this week assesses
| Framework | Questions |
|---|---|
{rows}

Source: {pub}, Unit {unit}, Lesson {lesson}. Digitized from the family's
purchased issue for private use.
""".format(week=mod.WEEK, title=mod.TITLE, eq=mod.ESSENTIAL_QUESTION,
           note=getattr(mod, "PARENT_NOTE", "").strip(),
           routine=_routine_section(mod),
           rows=rows, pub=mod.PUBLICATION, unit=mod.UNIT, lesson=mod.LESSON)

    # -- the check ----------------------------------------------------------

    def _question_set(self, lesson, family, mod):
        intro = (
            "**{title}** — {pub}, Unit {unit}, Lesson {lesson}.\n\n"
            "**Essential question:** {eq}\n\n"
            "Read this week's issue first (the pages are on the lesson page), "
            "then work through the check.{pictures}"
        ).format(title=mod.TITLE, pub=mod.PUBLICATION, unit=mod.UNIT,
                 lesson=mod.LESSON, eq=mod.ESSENTIAL_QUESTION,
                 pictures=(" Some questions have a picture printed with them — "
                           "tap it to make it bigger."
                           if any(q.get("figure") for q in mod.QUESTIONS) else ""))
        # Named for the LESSON, which is what the printed check is called
        # ("Lesson 2 Comprehension Check") and what she will be looking for.
        # The old "Week 2 ·" was our word, not the publisher's.
        title = ("Lesson %s · %s — Comprehension Check"
                 % (getattr(mod, "LESSON", mod.WEEK), mod.TITLE))
        fields = {"family": family, "intro": intro, "rubric": _rubric(mod),
                  "status": QuestionSet.APPROVED, "reading": "",
                  "mode": QuestionSet.MODE_STUDENT}
        # Matched on the LESSON, not on the title. A lesson has exactly one
        # check, and keying on the title meant renaming one would silently
        # create a second set beside it — orphaning every answer already
        # submitted against the old name.
        qset = QuestionSet.objects.filter(lesson=lesson).order_by("pk").first()
        if qset is None:
            return QuestionSet.objects.create(lesson=lesson, title=title, **fields)
        for field, value in dict(fields, title=title).items():
            setattr(qset, field, value)
        qset.save()
        return qset

    def _build(self, mod):
        """Flatten the week's questions into rows the seeder can write.

        A two-blank sentence becomes TWO questions, because the printed page
        gives each blank its own bank and half-right is a real outcome the
        record should keep.
        """
        rows, preview = [], []
        for q in list(mod.QUESTIONS) + ([mod.REFLECTION] if getattr(mod, "REFLECTION", None) else []):
            kind = q["kind"]
            if kind == "choice":
                rows.append(dict(
                    response_type=Question.TYPE_CHOICE, category="reading",
                    prompt=q["prompt"], hint=q["hint"],
                    passage=json.dumps({
                        "options": q["options"], "correct": q["correct"],
                        "multi": q["multi"], "figure": q["figure"],
                        "figure_caption": q["figure_caption"]}),
                ))
                preview.append(("choice", q["prompt"]))
            elif kind == "fill_two":
                for half, bank, correct in (("A", q["bank_a"], q["correct_a"]),
                                            ("B", q["bank_b"], q["correct_b"])):
                    opts = [{"key": chr(97 + i), "text": t, "image": ""}
                            for i, t in enumerate(bank)]
                    key = next(o["key"] for o in opts if o["text"] == correct)
                    rows.append(dict(
                        response_type=Question.TYPE_CHOICE, category="reading",
                        prompt="%s\n\n**Blank %s**" % (q["prompt"], half)
                               if half == "A" else "**Blank %s**" % half,
                        hint=q["hint"] if half == "A" else "",
                        passage=json.dumps({
                            "options": opts, "correct": [key], "multi": False,
                            # The figure rides with blank A only — printing the
                            # same map twice in a row just pushes B off screen.
                            "figure": q["figure"] if half == "A" else "",
                            "figure_caption": q["figure_caption"] if half == "A" else ""}),
                    ))
                preview.append(("fill_two", q["prompt"]))
            elif kind == "matching":
                # As PRINTED, which scrambles the right-hand column. Falling
                # back to pair order would line the columns up row for row and
                # let her match by position without reading either side.
                words = list(q.get("word_order") or [r for _l, r in q["pairs"]])
                defs = [{"n": i + 1, "text": left, "word": right}
                        for i, (left, right) in enumerate(q["pairs"])]
                rows.append(dict(
                    response_type=Question.TYPE_MATCHING, category="reading",
                    prompt=q["prompt"], hint=q["hint"],
                    passage=json.dumps({"words": words, "definitions": defs}),
                ))
                preview.append(("matching", q["prompt"]))
            elif kind == "order":
                rows.append(dict(
                    response_type=Question.TYPE_ORDER, category="reading",
                    prompt=q["prompt"], hint=q["hint"],
                    passage=json.dumps({"steps": q["steps"],
                                        "correct": q["correct"]}),
                ))
                preview.append(("order", q["prompt"]))
            else:
                rows.append(dict(
                    response_type=Question.TYPE_TEXT, category="writing",
                    prompt=q["prompt"], hint=q["hint"],
                    passage=json.dumps({
                        "answer_mode": q.get("answer_mode", True),
                        "figure": q.get("figure", ""),
                        "figure_caption": q.get("figure_caption", "")}),
                ))
                preview.append(("written", q["prompt"]))
        return {"rows": rows, "preview": preview, "count": len(rows)}

    def _fill(self, qset, rows):
        for order, row in enumerate(rows, start=1):
            Question.objects.update_or_create(
                question_set=qset, order=order, defaults=row)
        self._prune(qset, len(rows))
        return len(rows)

    @staticmethod
    def _prune(qset, keep_through):
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()
