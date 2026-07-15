import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import Family, FamilyMembership
from curricula.models import Chapter, Curriculum, Lesson
from students.models import Student
from tutor.models import MasteryAssessment, Question, QuestionSet, ResponseSheet

from .models import WorkLogEntry

User = get_user_model()

MEDIA = tempfile.mkdtemp()


class WorkLogModelTest(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user(
            username="p", email="p@example.com", password="pw", is_active=True,
        )
        self.child = Student.objects.create(
            parent=self.parent, first_name="Violet", grade_level="G03",
        )

    def test_str(self):
        entry = WorkLogEntry.objects.create(
            parent=self.parent, child=self.child, subject="Math",
        )
        self.assertIn("Violet", str(entry))
        self.assertIn("Math", str(entry))

    def test_is_image_property(self):
        entry = WorkLogEntry(subject="Art")
        entry.attachment.name = "work_log/2026/07/drawing.PNG"
        self.assertTrue(entry.is_image)
        entry.attachment.name = "work_log/2026/07/report.pdf"
        self.assertFalse(entry.is_image)


class WorkLogScopingTest(TestCase):
    """Family scoping + permissions, mirroring students/assignments tests."""

    @classmethod
    def setUpTestData(cls):
        cls.parent1 = User.objects.create_user(
            username="parent1", email="p1@example.com", password="pw",
        )
        cls.parent2 = User.objects.create_user(
            username="parent2", email="p2@example.com", password="pw",
        )
        cls.teacher = User.objects.create_user(
            username="teacher", email="t@example.com", password="pw",
        )
        cls.family1 = Family.objects.create(name="Family One")
        cls.family2 = Family.objects.create(name="Family Two")
        FamilyMembership.objects.create(user=cls.parent1, family=cls.family1, role="parent")
        FamilyMembership.objects.create(user=cls.parent2, family=cls.family2, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family1, role="teacher")

        cls.child1 = Student.objects.create(
            parent=cls.parent1, first_name="Violet", grade_level="G03", family=cls.family1,
        )
        cls.child2 = Student.objects.create(
            parent=cls.parent2, first_name="Other", grade_level="G05", family=cls.family2,
        )
        cls.entry1 = WorkLogEntry.objects.create(
            parent=cls.parent1, child=cls.child1, subject="Math", family=cls.family1,
        )
        cls.entry2 = WorkLogEntry.objects.create(
            parent=cls.parent2, child=cls.child2, subject="Science", family=cls.family2,
        )

    def test_list_requires_login(self):
        resp = self.client.get(reverse("worklog:worklog_list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_list_shows_only_own_family(self):
        self.client.login(username="parent1", password="pw")
        resp = self.client.get(reverse("worklog:worklog_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Math")
        self.assertNotContains(resp, "Science")

    def test_detail_404_for_other_family(self):
        self.client.login(username="parent1", password="pw")
        resp = self.client.get(reverse("worklog:worklog_detail", kwargs={"pk": self.entry2.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_teacher_can_view_but_not_edit(self):
        self.client.login(username="teacher", password="pw")
        # Can see the family's entry read-only
        list_resp = self.client.get(reverse("worklog:worklog_list"))
        self.assertContains(list_resp, "Math")
        self.assertNotContains(list_resp, "Log Work")
        # Cannot reach create/update/delete
        self.assertEqual(self.client.get(reverse("worklog:worklog_create")).status_code, 404)
        self.assertEqual(
            self.client.get(reverse("worklog:worklog_update", kwargs={"pk": self.entry1.pk})).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("worklog:worklog_delete", kwargs={"pk": self.entry1.pk})).status_code,
            404,
        )

    def test_empty_state_for_new_parent(self):
        lonely = User.objects.create_user(username="lonely", email="l@example.com", password="pw")
        self.client.login(username="lonely", password="pw")
        resp = self.client.get(reverse("worklog:worklog_list"))
        self.assertContains(resp, "Log your first day")


@override_settings(MEDIA_ROOT=MEDIA)
class WorkLogCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(
            username="parent", email="parent@example.com", password="pw", is_active=True,
        )
        self.child = Student.objects.create(
            parent=self.parent, first_name="Violet", grade_level="G03",
        )

    def test_create_entry_success(self):
        self.client.login(username="parent", password="pw")
        resp = self.client.post(reverse("worklog:worklog_create"), data={
            "child": self.child.pk,
            "date": "2026-07-07",
            "subject": "Making 100 and 1,000",
            "description": "Completed Chapter 2 Lesson 5.",
        })
        self.assertEqual(resp.status_code, 302)
        entry = WorkLogEntry.objects.get(subject="Making 100 and 1,000")
        self.assertEqual(entry.parent, self.parent)
        self.assertEqual(entry.created_by, self.parent)
        self.assertEqual(entry.child, self.child)

    def test_create_with_file_upload(self):
        self.client.login(username="parent", password="pw")
        upload = SimpleUploadedFile("work.png", b"\x89PNG\r\n\x1a\n fake", content_type="image/png")
        resp = self.client.post(reverse("worklog:worklog_create"), data={
            "child": self.child.pk,
            "date": "2026-07-07",
            "subject": "Art",
            "description": "",
            "attachment": upload,
        })
        self.assertEqual(resp.status_code, 302)
        entry = WorkLogEntry.objects.get(subject="Art")
        self.assertTrue(entry.attachment)
        self.assertTrue(entry.is_image)

    def test_subject_required(self):
        self.client.login(username="parent", password="pw")
        resp = self.client.post(reverse("worklog:worklog_create"), data={
            "child": self.child.pk,
            "date": "2026-07-07",
            "subject": "   ",  # whitespace-only is stripped to empty by CharField
            "description": "",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "This field is required.")
        self.assertFalse(WorkLogEntry.objects.filter(child=self.child).exists())

    def test_cannot_log_for_other_familys_child(self):
        other_parent = User.objects.create_user(
            username="other", email="other@example.com", password="pw",
        )
        other_child = Student.objects.create(
            parent=other_parent, first_name="NotMine", grade_level="G01",
        )
        self.client.login(username="parent", password="pw")
        resp = self.client.post(reverse("worklog:worklog_create"), data={
            "child": other_child.pk,
            "date": "2026-07-07",
            "subject": "Math",
            "description": "",
        })
        self.assertEqual(resp.status_code, 200)  # re-rendered with error
        self.assertFalse(WorkLogEntry.objects.filter(child=other_child).exists())


class WorkLogReportTest(TestCase):
    """Date-range completion report: scoping, filtering, and oversight access."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="rparent", email="rp@example.com", password="pw")
        cls.other = User.objects.create_user(username="rother", email="ro@example.com", password="pw")
        cls.teacher = User.objects.create_user(username="rteacher", email="rt@example.com", password="pw")
        cls.fam = Family.objects.create(name="Report Family")
        cls.other_fam = Family.objects.create(name="Other Family")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.fam, role="teacher")
        FamilyMembership.objects.create(user=cls.other, family=cls.other_fam, role="parent")

        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.fam,
        )
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.fam,
        )
        cls.other_child = Student.objects.create(
            parent=cls.other, first_name="Zed", grade_level="G05", family=cls.other_fam,
        )

        cls.today = timezone.localdate()
        WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.violet, subject="Fractions",
            family=cls.fam, date=cls.today - timedelta(days=2),
        )
        WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.kaylin, subject="Algebra",
            family=cls.fam, date=cls.today - timedelta(days=5),
        )
        WorkLogEntry.objects.create(  # outside the default 30-day window
            parent=cls.parent, child=cls.violet, subject="AncientHistory",
            family=cls.fam, date=cls.today - timedelta(days=100),
        )
        WorkLogEntry.objects.create(  # different family
            parent=cls.other, child=cls.other_child, subject="ForbiddenSubject",
            family=cls.other_fam, date=cls.today - timedelta(days=1),
        )

    def test_report_requires_login(self):
        resp = self.client.get(reverse("worklog:worklog_report"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_default_range_scopes_to_recent_own_family(self):
        self.client.login(username="rparent", password="pw")
        resp = self.client.get(reverse("worklog:worklog_report"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Fractions")
        self.assertContains(resp, "Algebra")
        self.assertContains(resp, "Violet")
        self.assertContains(resp, "Kaylin")
        self.assertNotContains(resp, "AncientHistory")   # 100 days ago
        self.assertNotContains(resp, "ForbiddenSubject")  # other family

    def test_explicit_wide_range_includes_old_entry(self):
        self.client.login(username="rparent", password="pw")
        resp = self.client.get(reverse("worklog:worklog_report"), {
            "start": (self.today - timedelta(days=200)).isoformat(),
            "end": self.today.isoformat(),
        })
        self.assertContains(resp, "AncientHistory")

    def test_child_filter_limits_to_one_child(self):
        self.client.login(username="rparent", password="pw")
        resp = self.client.get(reverse("worklog:worklog_report"), {"child": self.kaylin.pk})
        self.assertContains(resp, "Algebra")
        self.assertNotContains(resp, "Fractions")

    def test_invalid_range_shows_error(self):
        self.client.login(username="rparent", password="pw")
        resp = self.client.get(reverse("worklog:worklog_report"), {
            "start": self.today.isoformat(),
            "end": (self.today - timedelta(days=5)).isoformat(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "on or before")

    def test_teacher_can_view_report_read_only(self):
        self.client.login(username="rteacher", password="pw")
        resp = self.client.get(reverse("worklog:worklog_report"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Fractions")
        self.assertNotContains(resp, "ForbiddenSubject")


@override_settings(MEDIA_ROOT=MEDIA)
class CharterReportRedesignTest(TestCase):
    """The redesigned Charter Report: structured sample work + AI-suggested and
    parent-stamped mastery, inline stamping, and CSV export."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="cparent", email="cp@e.com", password="pw")
        cls.teacher = User.objects.create_user(username="cteacher", email="ct@e.com", password="pw")
        cls.fam = Family.objects.create(name="Charter Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.fam, role="teacher")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.fam,
        )
        cls.today = timezone.localdate()

        cur = Curriculum.objects.create(parent=cls.parent, name="Writing 3", subject="Writing", family=cls.fam)
        ch = Chapter.objects.create(curriculum=cur, number=1, title="Unit 1")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        cls.qset = QuestionSet.objects.create(
            lesson=lesson, title="Wolfgang Questions", family=cls.fam,
            status=QuestionSet.APPROVED, rubric="Answer thoughtfully.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="editing",
            response_type=Question.TYPE_TEXT, prompt="Why does Wolfgang feel unhappy?",
        )

        # (1) portal-submitted work with an AI DRAFT assessment (not yet stamped)
        cls.entry = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.violet, subject="Writing", family=cls.fam,
            date=cls.today - timedelta(days=2), description="portal submission",
        )
        cls.sheet = ResponseSheet.objects.create(
            question_set=cls.qset, child=cls.violet,
            answers={str(cls.q.pk): "He was little and special."},
            status=ResponseSheet.SUBMITTED, work_entry=cls.entry, submitted_at=timezone.now(),
        )
        cls.assessment = MasteryAssessment.objects.create(
            work_entry=cls.entry, rubric="r", answers="a",
            ai_level="developing", ai_summary="A good start on his feelings.",
            ai_criteria=[{"criterion": "Explains why", "met": True, "comment": "clear"}],
            status=MasteryAssessment.DRAFT,
        )
        # (2) a photo entry — no sheet, no assessment
        cls.photo = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.violet, subject="Art", family=cls.fam,
            date=cls.today - timedelta(days=1),
            attachment=SimpleUploadedFile("art.png", b"\x89PNG\r\n\x1a\n", content_type="image/png"),
        )
        # (3) a plain note entry — no sheet, no assessment
        cls.note = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.violet, subject="Nature", family=cls.fam,
            date=cls.today, description="We went on a nature walk and found acorns.",
        )

    def _report(self, **params):
        return self.client.get(reverse("worklog:charter_report"), params)

    def test_renders_structured_work_and_ai_suggestion(self):
        self.client.login(username="cparent", password="pw")
        resp = self._report()
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Why does Wolfgang feel unhappy?")   # the question prompt
        self.assertContains(resp, "He was little and special.")         # the child's actual answer
        self.assertContains(resp, "ss-answer-block")                    # structured, not a raw blob
        self.assertContains(resp, "AI suggestion")                      # AI block surfaces the DRAFT
        self.assertContains(resp, "We went on a nature walk")           # note entry sample work
        self.assertContains(resp, "Awaiting your grade")                # nothing stamped yet
        self.assertContains(resp, 'name="final_level"')                 # inline stamp control

    def test_photo_renders_inline_image(self):
        self.client.login(username="cparent", password="pw")
        resp = self._report()
        self.assertContains(resp, "ss-work-img")
        self.assertContains(resp, self.photo.attachment.url)

    def test_stamp_finalizes_and_returns_to_report(self):
        self.client.login(username="cparent", password="pw")
        resp = self.client.post(
            reverse("worklog:report_stamp", kwargs={"entry_pk": self.entry.pk}),
            {"final_level": "proficient", "start": (self.today - timedelta(days=30)).isoformat(),
             "end": self.today.isoformat()},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("charter-report", resp.url)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, MasteryAssessment.FINALIZED)
        self.assertEqual(self.assessment.final_level, "proficient")
        self.assertEqual(self.assessment.parent_override_level, "proficient")  # differs from AI's developing

    def test_stamp_creates_assessment_for_photo(self):
        self.client.login(username="cparent", password="pw")
        resp = self.client.post(
            reverse("worklog:report_stamp", kwargs={"entry_pk": self.photo.pk}),
            {"final_level": "mastered"},
        )
        self.assertEqual(resp.status_code, 302)
        a = self.photo.assessments.first()
        self.assertIsNotNone(a)
        self.assertEqual(a.final_level, "mastered")
        self.assertEqual(a.ai_level, "")
        self.assertEqual(a.status, MasteryAssessment.FINALIZED)

    def test_teacher_cannot_stamp(self):
        self.client.login(username="cteacher", password="pw")
        resp = self.client.post(
            reverse("worklog:report_stamp", kwargs={"entry_pk": self.entry.pk}),
            {"final_level": "proficient"},
        )
        self.assertEqual(resp.status_code, 404)

    def test_finalized_shows_parent_grade(self):
        self.assessment.final_level = "mastered"
        self.assessment.status = MasteryAssessment.FINALIZED
        self.assessment.save()
        self.client.login(username="cparent", password="pw")
        resp = self._report()
        self.assertContains(resp, "Your grade:")
        self.assertContains(resp, "Mastered")

    def test_csv_export(self):
        self.client.login(username="cparent", password="pw")
        resp = self._report(format="csv")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")
        self.assertIn("attachment", resp["Content-Disposition"])
        body = resp.content.decode()
        self.assertIn("Date,Child,Subject,Lesson,AI level,Final level,Status", body)
        self.assertIn("Wolfgang Questions", body)
