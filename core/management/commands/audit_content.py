"""Shake down every student's content and report what is broken or missing.

The checks a person would otherwise do by clicking: does each curriculum still
match its lesson plan, can every child actually open every page and exercise
assigned to them, does every manga panel's art exist, and is anything in a state
that renders blank or unanswerable.

Written after a matching exercise shipped as eight text questions — four of them
the ANSWER CHOICES posing as questions — and nobody noticed until a child sat
down in front of it. Most of these checks exist because something like that got
through once.

Exits non-zero when a PROBLEM is found, so it can be run on a schedule or in CI.
Things that are merely absent (a lesson with no material yet, a draft awaiting
approval) are reported as NOTES and do not fail the run — the backlog is not a
break.

Examples:
    python manage.py audit_content
    python manage.py audit_content --student Violet
    python manage.py audit_content --quiet        # problems only
"""

import re

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.test import Client

from curricula.blueprints import BLUEPRINTS
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor.models import (LessonBlock, MangaPanel, MasteryAssessment, Material,
                          Question, QuestionSet, ResponseSheet)


class Command(BaseCommand):
    help = "Audit every student's lessons, exercises and materials for breakage."

    def add_arguments(self, parser):
        parser.add_argument("--student", help="Limit the portal sweep to one child (first name).")
        parser.add_argument("--quiet", action="store_true", help="Print problems only.")

    def handle(self, *args, **options):
        self.problems = []
        self.notes = []
        self.quiet = options["quiet"]

        self._check_blueprints()
        self._check_questions()
        self._check_manga()
        self._check_lesson_blocks()
        self._check_integrity()
        self._check_portal(options.get("student"))

        self.say("")
        for n in self.notes:
            self.stdout.write(self.style.WARNING(f"NOTE     {n}"))
        for p in self.problems:
            self.stdout.write(self.style.ERROR(f"PROBLEM  {p}"))
        self.stdout.write(
            self.style.ERROR(f"\n{len(self.problems)} problem(s), {len(self.notes)} note(s).")
            if self.problems else
            self.style.SUCCESS(f"\nNo problems. {len(self.notes)} note(s).")
        )
        if self.problems:
            raise SystemExit(1)

    # -- helpers ------------------------------------------------------------

    def say(self, msg):
        if not self.quiet:
            self.stdout.write(msg)

    def problem(self, msg):
        self.problems.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    # -- checks -------------------------------------------------------------

    def _check_blueprints(self):
        """Has any curriculum drifted from the lesson plan it was built from?"""
        self.say("— lesson plans —")
        by_name = {bp["name"]: (slug, bp) for slug, bp in BLUEPRINTS.items()}
        for c in Curriculum.objects.order_by("pk"):
            entry = by_name.get(c.name)
            if not entry:
                continue
            slug, bp = entry
            want = {
                (ch["number"], l["order"]): (l["title"], l["type"])
                for ch in bp["chapters"] for l in ch["lessons"]
            }
            have = {
                (l.chapter.number, l.order): (l.title, l.lesson_type)
                for l in Lesson.objects.filter(chapter__curriculum=c).select_related("chapter")
            }
            for k in sorted(set(want) - set(have)):
                self.problem(f"{c.name}: the plan has Ch{k[0]} order={k[1]} "
                             f"({want[k][0]}) and the database does not")
            for k in sorted(set(want) & set(have)):
                if want[k] != have[k]:
                    self.problem(f"{c.name}: Ch{k[0]} order={k[1]} drifted from the plan — "
                                 f"plan {want[k]}, database {have[k]}")
            # Extra lessons are normal: seminars and reviews get added outside the
            # plan on purpose. Say so rather than crying wolf about it.
            extra = sorted(set(have) - set(want))
            if extra:
                self.note(f"{c.name}: {len(extra)} lesson(s) added outside the plan "
                          f"({', '.join(f'Ch{a}#{b}' for a, b in extra[:3])})")
            self.say(f"   {c.name[:44]:44s} {len(have):3d} lessons, matches plan")

    def _check_questions(self):
        """Anything a child could open and find unanswerable."""
        self.say("— exercises —")
        for q in QuestionSet.objects.annotate(n=Count("questions")).filter(n=0):
            self.problem(f"question set #{q.pk} '{q.title}' has no questions at all")

        blank = lettered = 0
        for q in Question.objects.select_related("question_set"):
            prompt = (q.prompt or "").strip()
            if not prompt and not (q.passage or "").strip():
                blank += 1
                self.problem(f"question #{q.pk} in '{q.question_set.title[:40]}' renders "
                             f"blank — no prompt and no passage")
            # The bug this command was written for: a lettered option from an
            # answer bank standing alone as a question, with nothing to answer.
            if re.match(r"^[A-D]\.\s", prompt):
                lettered += 1
                self.problem(f"question #{q.pk} in '{q.question_set.title[:40]}' is an "
                             f"answer CHOICE posing as a question: {prompt[:40]!r}")
            if q.response_type in (Question.TYPE_MATCHING, Question.TYPE_FILL_BLANK):
                self._check_exercise_json(q)
        self.say(f"   {Question.objects.count()} questions, "
                 f"{blank} blank, {lettered} answer-choices-as-questions")

    def _check_exercise_json(self, q):
        data = q.vocab_data
        if not data:
            self.problem(f"question #{q.pk} ({q.response_type}) has unreadable exercise data")
            return
        if q.response_type != Question.TYPE_MATCHING:
            return
        pool = set(data.get("words") or [])
        answers = {d.get("word") for d in (data.get("definitions") or [])}
        if not pool or not answers:
            self.problem(f"question #{q.pk} matching has an empty pool or no rows")
        elif answers - pool:
            # Unwinnable: a correct answer the child cannot pick.
            self.problem(f"question #{q.pk} matching expects answers that are not in the "
                         f"pool: {sorted(answers - pool)}")

    def _check_manga(self):
        """Every panel needs art that actually exists in the deployed static files."""
        self.say("— manga —")
        for m in Material.objects.filter(skill_type=Material.SKILL_MANGA).select_related(
                "lesson__chapter"):
            panels = list(MangaPanel.objects.filter(material=m).order_by("order"))
            where = f"Ch{m.lesson.chapter.number} L{m.lesson.number}" if m.lesson else "?"
            if not panels:
                self.problem(f"manga '{m.title[:40]}' ({where}) has no panels")
                continue
            orders = [p.order for p in panels]
            if orders != list(range(1, len(orders) + 1)):
                self.problem(f"manga '{m.title[:40]}' ({where}) has gappy panel "
                             f"numbering: {orders}")
            for p in panels:
                if not p.image_path:
                    self.problem(f"manga '{m.title[:30]}' panel {p.order} has no art")
                    continue
                try:
                    # Under ManifestStaticFilesStorage a missing file raises here —
                    # and would 500 the child's page rather than show a broken image.
                    staticfiles_storage.url(p.image_path)
                except Exception:
                    self.problem(f"manga '{m.title[:30]}' panel {p.order}: art "
                                 f"{p.image_path} is not in the deployed static files")
                if not (p.bubbles or p.caption):
                    self.problem(f"manga '{m.title[:30]}' panel {p.order} has no words "
                                 f"— no caption and no speech")
            if m.status != Material.APPROVED:
                self.note(f"manga '{m.title[:40]}' ({where}) is {m.get_status_display()} — "
                          f"a parent has to approve it before the child sees it")
        self.say(f"   {Material.objects.filter(skill_type=Material.SKILL_MANGA).count()} "
                 f"manga materials checked")

    def _check_lesson_blocks(self):
        """A taught lesson is only as good as the blocks it renders.

        An unknown kind falls through every branch of _lesson_blocks.html and
        renders as NOTHING — a blank stretch of page with no error anywhere. The
        seeder validates at write time; this catches anything that reached the
        database another way.
        """
        self.say("— taught lessons —")
        from tutor.management.commands._saxon_seed import REQUIRED_KEYS, _unplottable

        known = dict(LessonBlock.KIND_CHOICES)
        lessons = Material.objects.filter(skill_type=Material.SKILL_LESSON)
        for m in lessons.select_related("lesson__chapter"):
            blocks = list(LessonBlock.objects.filter(material=m).order_by("order"))
            where = f"Ch{m.lesson.chapter.number} L{m.lesson.number}" if m.lesson else "?"
            if not blocks:
                self.problem(f"lesson '{m.title[:40]}' ({where}) has no blocks — the "
                             f"child would see an empty page")
                continue
            for b in blocks:
                if b.kind not in known:
                    self.problem(f"lesson '{m.title[:30]}' block {b.order}: unknown "
                                 f"kind {b.kind!r} — it renders as nothing")
                    continue
                for key in REQUIRED_KEYS.get(b.kind, ()):
                    if not (b.data or {}).get(key):
                        self.problem(f"lesson '{m.title[:30]}' block {b.order} "
                                     f"({b.kind}): missing {key!r}")
                if b.kind == LessonBlock.KIND_TOOL:
                    for msg in _unplottable(b.order, (b.data or {}).get("config") or {}):
                        self.problem(f"lesson '{m.title[:30]}' {msg}")
            if m.status != Material.APPROVED:
                self.note(f"lesson '{m.title[:40]}' ({where}) is "
                          f"{m.get_status_display()} — a parent has to approve it")
        self.say(f"   {lessons.count()} taught lessons checked")

    def _check_integrity(self):
        self.say("— data —")
        for d in (MasteryAssessment.objects.values("work_entry_id")
                  .annotate(n=Count("id")).filter(n__gt=1)):
            self.problem(f"work entry {d['work_entry_id']} carries {d['n']} assessments — "
                         f"the parent sees two mastery levels for one piece of work")
        # An answer keyed to a question that no longer exists is a child's work
        # with nothing left to render it against.
        for sh in ResponseSheet.objects.exclude(answers={}).select_related(
                "question_set", "child"):
            live = {str(pk) for pk in Question.objects
                    .filter(question_set=sh.question_set).values_list("pk", flat=True)}
            lost = [k for k, v in (sh.answers or {}).items()
                    if str(v).strip() and k.isdigit() and k not in live]
            if lost:
                self.problem(f"{sh.child.first_name}'s sheet #{sh.pk} has {len(lost)} "
                             f"answer(s) for deleted questions in "
                             f"'{sh.question_set.title[:35]}'")
        self.say("   assessments and saved answers checked")

    def _check_portal(self, only):
        """Open every page each child can actually reach."""
        self.say("— portal —")
        from portal.tokens import make_portal_token

        headers = {"host": settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "testserver",
                   "x-forwarded-proto": "https"}
        client = Client()
        students = Student.objects.all().order_by("first_name")
        if only:
            students = students.filter(first_name__iexact=only)
        for s in students:
            # Name AND pk: two children can share a first name, and a duplicate row
            # otherwise reads as the same problem reported twice.
            who = f"{s.first_name} (#{s.pk})"
            # ACTIVE placements only, exactly as portal/views.py:_subject_cards
            # filters them. Auditing more than the child can reach turns correct
            # refusals into reported breakage: a deactivated placement on another
            # child's curriculum made this walk open that child's material and
            # flag the 404 — which was the permission check working.
            placements = (CurriculumPlacement.objects
                          .filter(child=s, is_active=True, curriculum__is_active=True)
                          .select_related("curriculum"))
            if not placements:
                self.problem(f"{who} has no curriculum placements — their portal is empty")
            for pl in placements:
                if pl.current_lesson_id and pl.current_lesson.chapter.curriculum_id != pl.curriculum_id:
                    self.problem(f"{who}/{pl.curriculum.name}: the current lesson "
                                 f"belongs to a different curriculum")

            base = f"/portal/{make_portal_token(s)}"
            pages = ok = 0
            for path in ("/", "/lingua/", "/lingua/tutor/", "/lingua/phonics/",
                         "/lingua/listen/"):
                pages += 1
                ok += self._get(client, base + path, headers, f"{who} {path}")

            cur_ids = [pl.curriculum_id for pl in placements]
            for qs in QuestionSet.objects.filter(
                    lesson__chapter__curriculum_id__in=cur_ids,
                    mode=QuestionSet.MODE_STUDENT):
                pages += 1
                ok += self._get(client, f"{base}/questions/{qs.pk}/", headers,
                                f"{who} exercise '{qs.title[:40]}'")

            # Only APPROVED materials are reachable; a draft 404ing is the approval
            # gate working, not a fault, so don't open those.
            for m in Material.objects.filter(
                    lesson__chapter__curriculum_id__in=cur_ids,
                    status=Material.APPROVED):
                pages += 1
                ok += self._get(client, f"{base}/materials/{m.pk}/", headers,
                                f"{who} material '{m.title[:40]}'")

            self.say(f"   {who:16s} {ok}/{pages} pages OK")

    def _get(self, client, url, headers, label):
        try:
            resp = client.get(url, headers=headers)
        except Exception as exc:  # noqa: BLE001 — a raising page is the worst case
            self.problem(f"{label} raised {type(exc).__name__}: {exc}")
            return 0
        if resp.status_code != 200:
            self.problem(f"{label} returned {resp.status_code}")
            return 0
        return 1
