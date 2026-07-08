import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import Family, FamilyMembership
from students.models import Student

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
        self.assertContains(resp, "No work logged yet")


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
