from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from core.models import Family, FamilyMembership
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor import mastery
from tutor.models import MasteryAssessment
from worklog.models import WorkLogEntry


def curriculum_with_lessons(parent, family, name, subject, n=4):
    cur = Curriculum.objects.create(parent=parent, family=family, name=name, subject=subject)
    ch = Chapter.objects.create(curriculum=cur, number=1, title="Chapter 1")
    lessons = [
        Lesson.objects.create(chapter=ch, order=i, number=i, title=f"L{i}")
        for i in range(1, n + 1)
    ]
    return cur, lessons


class ProgressDashboardTests(TestCase):
    """The dashboard now reflects real signals: placement progress, Work Log,
    and finalized mastery — not the legacy Assignment model."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = CustomUser.objects.create_user(username="p1", email="p1@e.com", password="pw")
        cls.family = Family.objects.create(name="Fam1")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.alice = Student.objects.create(parent=cls.parent, first_name="Alice", grade_level="G03", family=cls.family)
        cls.bob = Student.objects.create(parent=cls.parent, first_name="Bob", grade_level="G05", family=cls.family)

        # A second family whose data must never appear.
        cls.other = CustomUser.objects.create_user(username="p2", email="p2@e.com", password="pw")
        cls.other_family = Family.objects.create(name="Fam2")
        FamilyMembership.objects.create(user=cls.other, family=cls.other_family, role="parent")
        cls.eve = Student.objects.create(parent=cls.other, first_name="Eve", grade_level="G01", family=cls.other_family)

        # Alice: Math placement on lesson 3 of 4 → done=2.
        cls.math, math_lessons = curriculum_with_lessons(cls.parent, cls.family, "Math 3A", "Math")
        CurriculumPlacement.objects.create(child=cls.alice, curriculum=cls.math, current_lesson=math_lessons[2])

        other_cur, other_lessons = curriculum_with_lessons(cls.other, cls.other_family, "Secret Math", "Math")
        CurriculumPlacement.objects.create(child=cls.eve, curriculum=other_cur, current_lesson=other_lessons[1])

        cls.today = date.today()
        for _ in range(2):
            WorkLogEntry.objects.create(parent=cls.parent, family=cls.family, child=cls.alice, subject="Math", date=cls.today)
        cls.old_entry = WorkLogEntry.objects.create(
            parent=cls.parent, family=cls.family, child=cls.alice, subject="Reading",
            date=cls.today - timedelta(days=30),
        )
        WorkLogEntry.objects.create(parent=cls.other, family=cls.other_family, child=cls.eve, subject="SecretWork", date=cls.today)

        # Alice mastery: one Proficient (meets bar), one Beginning (doesn't).
        e = WorkLogEntry.objects.filter(child=cls.alice).first()
        MasteryAssessment.objects.create(work_entry=e, rubric="r", answers="a", final_level=mastery.PROFICIENT, status=MasteryAssessment.FINALIZED)
        MasteryAssessment.objects.create(work_entry=e, rubric="r", answers="a", final_level=mastery.BEGINNING, status=MasteryAssessment.FINALIZED)

        cls.url = reverse("dashboard:dashboard")

    def test_requires_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)

    def test_shows_placement_progress(self):
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        cards = {c["child"].first_name: c for c in resp.context["child_cards"]}
        prog = cards["Alice"]["subjects"][0]["progress"]
        self.assertEqual((prog["done"], prog["total"]), (2, 4))
        self.assertContains(resp, "Math 3A")

    def test_worklog_count_and_family_scoping(self):
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["summary"]["worklog_count"], 3)   # Alice's 3, Bob's 0
        self.assertNotContains(resp, "SecretWork")                      # other family hidden
        self.assertNotContains(resp, "Eve")

    def test_date_range_excludes_old_entries(self):
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url, {"start_date": (self.today - timedelta(days=7)).isoformat()})
        self.assertEqual(resp.context["summary"]["worklog_count"], 2)   # the 30-day-old one drops

    def test_mastery_surfaced(self):
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["summary"]["assessed"], 2)
        self.assertEqual(resp.context["summary"]["meets_bar"], 1)       # only the Proficient one
        self.assertContains(resp, "Proficient")

    def test_filter_by_child(self):
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url, {"child_id": self.bob.id})
        self.assertEqual(resp.context["summary"]["children"], 1)
        self.assertEqual([c["child"].first_name for c in resp.context["child_cards"]], ["Bob"])

    def test_filter_other_family_child_is_empty(self):
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url, {"child_id": self.eve.id})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["summary"]["children"], 0)

    def test_draft_assessment_not_counted(self):
        # An unreviewed AI draft must NOT inflate the mastery numbers.
        e = WorkLogEntry.objects.filter(child=self.alice).first()
        MasteryAssessment.objects.create(
            work_entry=e, rubric="r", answers="a",
            ai_level=mastery.MASTERED, status=MasteryAssessment.DRAFT,
        )
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["summary"]["assessed"], 2)   # still just the 2 finalized
        self.assertEqual(resp.context["summary"]["meets_bar"], 1)

    def test_malformed_params_do_not_500(self):
        self.client.login(username="p1", password="pw")
        resp = self.client.get(self.url, {"child_id": "abc", "start_date": "notadate", "end_date": "x"})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context["has_filters"])              # junk params ignored
        self.assertEqual(resp.context["summary"]["worklog_count"], 3)

    def test_no_assignment_dependency(self):
        # The Progress page must render even with zero Assignment rows.
        from assignments.models import Assignment
        self.assertEqual(Assignment.objects.count(), 0)
        self.client.login(username="p1", password="pw")
        self.assertEqual(self.client.get(self.url).status_code, 200)


class TeacherProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = CustomUser.objects.create_user(username="tp", email="tp@e.com", password="pw")
        cls.teacher = CustomUser.objects.create_user(username="tt", email="tt@e.com", password="pw")
        cls.family = Family.objects.create(name="TFam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.child = Student.objects.create(parent=cls.parent, first_name="Dash", grade_level="G03", family=cls.family)
        WorkLogEntry.objects.create(parent=cls.parent, family=cls.family, child=cls.child, subject="Math", date=date.today())
        cls.url = reverse("dashboard:dashboard")

    def test_teacher_sees_family_progress(self):
        self.client.login(username="tt", password="pw")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["summary"]["worklog_count"], 1)
        self.assertContains(resp, "Dash")


class FamilySwitcherProgressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = CustomUser.objects.create_user(username="sw", email="sw@e.com", password="pw")
        cls.fam_a = Family.objects.create(name="A Fam")
        cls.fam_b = Family.objects.create(name="B Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam_a, role="parent")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam_b, role="parent")
        cls.child_a = Student.objects.create(parent=cls.parent, first_name="ChildA", grade_level="G03", family=cls.fam_a)
        cls.child_b = Student.objects.create(parent=cls.parent, first_name="ChildB", grade_level="G05", family=cls.fam_b)
        cls.url = reverse("dashboard:dashboard")

    def test_default_shows_first_family(self):
        self.client.login(username="sw", password="pw")
        resp = self.client.get(self.url)
        self.assertContains(resp, "ChildA")
        self.assertNotContains(resp, "ChildB")

    def test_switch_family(self):
        self.client.login(username="sw", password="pw")
        resp = self.client.get(self.url, {"family_id": self.fam_b.id})
        self.assertContains(resp, "ChildB")
        self.assertNotContains(resp, "ChildA")


class MasteryTrendsAndCharterTests(TestCase):
    """Mastery-over-time sparklines + the print-ready charter report."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = CustomUser.objects.create_user(username="cr", email="cr@e.com", password="pw")
        cls.family = Family.objects.create(name="CR Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(parent=cls.parent, first_name="Violet",
                                            grade_level="G03", family=cls.family)
        cls.today = date.today()

        def finalized(subject, level, days_ago):
            d = cls.today - timedelta(days=days_ago)
            e = WorkLogEntry.objects.create(parent=cls.parent, family=cls.family, child=cls.violet,
                                            subject=subject, date=d)
            return MasteryAssessment.objects.create(
                work_entry=e, rubric="r", answers="a", ai_level=level,
                final_level=level, status=MasteryAssessment.FINALIZED,
            )

        finalized("Math", mastery.BEGINNING, 21)
        finalized("Math", mastery.DEVELOPING, 14)
        finalized("Math", mastery.PROFICIENT, 3)
        finalized("Reading", mastery.MASTERED, 5)   # single point → no trend line

        # other family (never appears)
        other = CustomUser.objects.create_user(username="cr2", email="cr2@e.com", password="pw")
        fam2 = Family.objects.create(name="Other CR")
        FamilyMembership.objects.create(user=other, family=fam2, role="parent")
        kid2 = Student.objects.create(parent=other, first_name="Zed", grade_level="G01", family=fam2)
        e = WorkLogEntry.objects.create(parent=other, family=fam2, child=kid2, subject="SecretSubj",
                                        date=cls.today)
        MasteryAssessment.objects.create(work_entry=e, rubric="r", answers="a",
                                         final_level=mastery.PROFICIENT, status=MasteryAssessment.FINALIZED)

    def test_series_builds_rising_line(self):
        from tutor.trends import mastery_series
        series = {s["subject"]: s for s in mastery_series(list(MasteryAssessment.objects.filter(
            work_entry__child=self.violet)))}
        self.assertEqual(series["Math"]["count"], 3)
        ys = [p["y"] for p in series["Math"]["points"]]
        self.assertGreater(ys[0], ys[-1])                 # rising mastery → y decreases (SVG top)
        self.assertEqual(series["Math"]["latest"]["label"], "Proficient")

    def test_progress_page_renders_trend(self):
        self.client.login(username="cr", password="pw")
        resp = self.client.get(reverse("dashboard:dashboard"))
        self.assertContains(resp, "Mastery over time")
        self.assertContains(resp, "<polyline")           # the Math sparkline
        self.assertContains(resp, "Charter report")

    def test_charter_report_combines_worklog_and_mastery(self):
        self.client.login(username="cr", password="pw")
        resp = self.client.get(reverse("worklog:charter_report"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Homeschool Progress Report")
        self.assertContains(resp, "Print / Save PDF")
        self.assertContains(resp, "Violet")
        self.assertContains(resp, "Mastery")
        self.assertContains(resp, "Work log")
        self.assertContains(resp, "<polyline")           # trend included
        self.assertNotContains(resp, "SecretSubj")       # family-scoped
        self.assertNotContains(resp, "Zed")

    def test_charter_report_child_and_date_filter(self):
        self.client.login(username="cr", password="pw")
        # window that excludes the 21-day-old Beginning assessment
        resp = self.client.get(reverse("worklog:charter_report"), {
            "child": self.violet.id,
            "start": (self.today - timedelta(days=7)).isoformat(),
            "end": self.today.isoformat(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Proficient")
        self.assertNotContains(resp, "Beginning")

    def test_report_requires_login(self):
        resp = self.client.get(reverse("worklog:charter_report"))
        self.assertEqual(resp.status_code, 302)
