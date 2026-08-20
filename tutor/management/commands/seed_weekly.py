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


def _rubric(mod):
    """What the grader is told, in the issue's own terms."""
    standards = sorted({q.get("standard", "") for q in mod.QUESTIONS if q.get("standard")})
    return """## {pub} — Week {week}: {title}

{eq}

Most of this week is a comprehension check with right answers, and those are
marked automatically — you do not need to re-mark them. Judge the WRITTEN answer
at the end: it asks her to use the maps in the issue as evidence, so look for
whether she points at something a map actually shows rather than repeating the
article.

If she answered by hand, the strokes are her answer; say so rather than guessing
at the words.

### What this week assesses
{standards}

Grade-{grade} mastery: Beginning → Developing → Proficient → Mastered.
""".format(pub=mod.PUBLICATION, week=mod.WEEK, title=mod.TITLE,
           eq="**Essential question:** " + mod.ESSENTIAL_QUESTION,
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
                "Dry run — nothing written. Would seed Level %d Week %d for %s: "
                "%d questions, %d vocabulary, %d article page(s)."
                % (level, week, child.first_name, built["count"],
                   len(mod.VOCABULARY), len(mod.PAGES))))
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
            defaults={"title": "Unit %d" % mod.UNIT},
        )
        lesson, _ = Lesson.objects.update_or_create(
            chapter=chapter, order=week,
            defaults={"number": week,
                      "title": "Week %d · %s" % (week, mod.TITLE),
                      "objectives": mod.ESSENTIAL_QUESTION},
        )

        self._material(lesson, child, family, mod)
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

    def _material(self, lesson, child, family, mod):
        """The issue itself, as its own pages, plus the vocabulary as blocks."""
        material, _ = Material.objects.update_or_create(
            lesson=lesson, title="%s — the issue" % mod.TITLE,
            defaults={
                "child": child, "family": family,
                "skill_type": Material.SKILL_LESSON,
                "student_intro": (
                    "This week's issue. Read both pages, then answer the "
                    "questions — the maps are the part most of the questions "
                    "are about, so give them a proper look."),
                "student_content": "",
                "parent_content": self._parent_guide(mod),
                "status": Material.DRAFT,
            },
        )
        blocks = [
            (LessonBlock.KIND_MASTHEAD, {
                "eyebrow": "%s · Unit %d · Lesson %s"
                           % (mod.PUBLICATION, mod.UNIT, mod.LESSON),
                "title": mod.SUBTITLE,
                "thesis": "**Essential question:** " + mod.ESSENTIAL_QUESTION,
            }),
            (LessonBlock.KIND_TRANSLATION, {
                "title": "Words this week",
                "rows": [{"symbol": t, "plain": d, "example": ""}
                         for t, d in mod.VOCABULARY],
            }),
        ]
        LessonBlock.objects.filter(material=material).delete()
        for i, (kind, payload) in enumerate(blocks, start=1):
            LessonBlock.objects.create(material=material, order=i, kind=kind,
                                       data=payload)
        return material

    @staticmethod
    def _parent_guide(mod):
        rows = "\n".join("| %d | %s |" % (i, q.get("standard", "—"))
                         for i, q in enumerate(mod.QUESTIONS, start=1))
        return """## Week {week}: {title}

**Essential question:** {eq}

The comprehension check is the issue's own, in its printed order and wording,
and its answers are the teacher edition's. Right answers are marked
automatically, so the only thing needing your eye is the written question at the
end — and whether she actually read the maps.

**Where the answers come from.** Questions 6, 8 and 9 cannot be answered from
the article; they are read off the maps printed with them. If she is guessing,
that is usually the reason — sit with her and the map rather than the text.

### What each question assesses
| # | Framework |
|---|---|
{rows}

Source: {pub}, Unit {unit}, Lesson {lesson}. Digitized from the family's
purchased issue for private use.
""".format(week=mod.WEEK, title=mod.TITLE, eq=mod.ESSENTIAL_QUESTION,
           rows=rows, pub=mod.PUBLICATION, unit=mod.UNIT, lesson=mod.LESSON)

    # -- the check ----------------------------------------------------------

    def _question_set(self, lesson, family, mod):
        intro = (
            "**{title}** — {pub}, Unit {unit}, Lesson {lesson}.\n\n"
            "**Essential question:** {eq}\n\n"
            "Read this week's issue first (the pages are on the lesson page), "
            "then work through the check. Several questions are about a map "
            "printed with them — tap a map to make it bigger."
        ).format(title=mod.TITLE, pub=mod.PUBLICATION, unit=mod.UNIT,
                 lesson=mod.LESSON, eq=mod.ESSENTIAL_QUESTION)
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson, title="Week %d · %s — Comprehension Check"
                                 % (mod.WEEK, mod.TITLE),
            defaults={"family": family, "intro": intro, "rubric": _rubric(mod),
                      "status": QuestionSet.APPROVED, "reading": "",
                      "mode": QuestionSet.MODE_STUDENT},
        )
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
                words = [r for _l, r in q["pairs"]]
                defs = [{"n": i + 1, "text": left, "word": right}
                        for i, (left, right) in enumerate(q["pairs"])]
                rows.append(dict(
                    response_type=Question.TYPE_MATCHING, category="reading",
                    prompt=q["prompt"], hint=q["hint"],
                    passage=json.dumps({"words": words, "definitions": defs}),
                ))
                preview.append(("matching", q["prompt"]))
            else:
                rows.append(dict(
                    response_type=Question.TYPE_TEXT, category="writing",
                    prompt=q["prompt"], hint=q["hint"],
                    passage=json.dumps({"answer_mode": q.get("answer_mode", True)}),
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
