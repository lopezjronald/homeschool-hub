import json
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


class WorkLogMinutesTest(TestCase):
    """F3: optional per-entry minutes, the raw material for the hours report."""

    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(
            username="mparent", email="mp@example.com", password="pw", is_active=True,
        )
        self.child = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07",
        )
        self.client.login(username="mparent", password="pw")

    def _post(self, **extra):
        data = {"child": self.child.pk, "date": "2026-08-06",
                "subject": "Math", "description": ""}
        data.update(extra)
        return self.client.post(reverse("worklog:worklog_create"), data=data)

    def test_minutes_are_stored_when_given(self):
        self.assertEqual(self._post(minutes="45").status_code, 302)
        self.assertEqual(WorkLogEntry.objects.get(child=self.child).minutes, 45)

    def test_minutes_are_optional(self):
        self.assertEqual(self._post().status_code, 302)
        self.assertIsNone(WorkLogEntry.objects.get(child=self.child).minutes)

    def test_zero_minutes_is_treated_as_not_recorded(self):
        """0 is meaningless as a session; clean_minutes coerces it to None so it
        never lands as a real zero that skews an average or a total."""
        self.assertEqual(self._post(minutes="0").status_code, 302)
        self.assertIsNone(WorkLogEntry.objects.get(child=self.child).minutes)

    def test_absurd_minutes_are_rejected(self):
        """More than a full day is a fat-finger; reject rather than corrupt the
        hours report. Nothing is saved."""
        resp = self._post(minutes="99999")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(WorkLogEntry.objects.filter(child=self.child).exists())

    def test_minutes_field_is_positive_integer_not_small(self):
        """SQLite ignores column width, so a PositiveSmallIntegerField (Postgres
        cap 32767) would pass every local test and only fail in prod once minutes
        add up in a query. Pin the wider type + nullability at the schema level so
        a downgrade of the field type fails here, not on prod."""
        field = WorkLogEntry._meta.get_field("minutes")
        self.assertEqual(field.get_internal_type(), "PositiveIntegerField")
        self.assertTrue(field.null)

    def test_minutes_row_shows_on_detail_and_hides_when_absent(self):
        with_min = WorkLogEntry.objects.create(
            parent=self.parent, child=self.child, subject="Math", minutes=30)
        without = WorkLogEntry.objects.create(
            parent=self.parent, child=self.child, subject="Reading")
        shown = self.client.get(reverse("worklog:worklog_detail", kwargs={"pk": with_min.pk}))
        self.assertContains(shown, "30 min")
        hidden = self.client.get(reverse("worklog:worklog_detail", kwargs={"pk": without.pk}))
        self.assertNotContains(hidden, "Time</dt>")


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


class HoursReportTest(TestCase):
    """B1: instructional-hours / attendance / days-of-instruction report."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="hp", email="hp@e.com", password="pw")
        cls.other = User.objects.create_user(username="ho", email="ho@e.com", password="pw")
        cls.fam = Family.objects.create(name="Hours Family")
        cls.other_fam = Family.objects.create(name="Other Family")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam, role="parent")
        FamilyMembership.objects.create(user=cls.other, family=cls.other_fam, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.fam)
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.fam)
        cls.quiet = Student.objects.create(
            parent=cls.parent, first_name="Quiet", grade_level="G01", family=cls.fam)
        cls.other_child = Student.objects.create(
            parent=cls.other, first_name="Zed", grade_level="G05", family=cls.other_fam)

        cls.today = timezone.localdate()
        # Violet: two subjects, SAME day -> one day of instruction, 45+15 minutes.
        WorkLogEntry.objects.create(parent=cls.parent, family=cls.fam, child=cls.violet,
                                    subject="Math", date=cls.today, minutes=45)
        WorkLogEntry.objects.create(parent=cls.parent, family=cls.fam, child=cls.violet,
                                    subject="Reading", date=cls.today, minutes=15)
        # Other family — must never appear.
        WorkLogEntry.objects.create(parent=cls.other, family=cls.other_fam, child=cls.other_child,
                                    subject="ForbiddenSubject", date=cls.today, minutes=99)

    def _url(self, **params):
        base = reverse("worklog:hours_report")
        return base + ("?" + "&".join(f"{k}={v}" for k, v in params.items()) if params else "")

    def test_requires_login(self):
        resp = self.client.get(reverse("worklog:hours_report"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_a_day_in_two_subjects_counts_once_but_time_sums(self):
        self.client.login(username="hp", password="pw")
        resp = self.client.get(reverse("worklog:hours_report"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Violet")
        # One day of instruction even though two subjects were worked...
        self.assertContains(resp, "1 day of instruction")
        # ...and the minutes of both subjects are present.
        self.assertContains(resp, "45")
        self.assertContains(resp, "15")
        self.assertContains(resp, "Math")
        self.assertContains(resp, "Reading")
        self.assertNotContains(resp, "ForbiddenSubject")   # other family excluded

    def test_spanish_minutes_from_lingua_are_counted(self):
        """Proves the aggregator wiring: a lingua listening session shows up as
        Spanish time in the host's hours report, no Work Log entry needed."""
        from lingua import profiles
        from lingua.models import Learner, ListeningSession
        learner = Learner.create_for_host_student(self.kaylin.pk, profiles.KIDS_OLDER)
        ListeningSession.objects.create(learner=learner, minutes=20)
        self.client.login(username="hp", password="pw")
        resp = self.client.get(reverse("worklog:hours_report"))
        self.assertContains(resp, "Kaylin")
        self.assertContains(resp, "Spanish")
        self.assertContains(resp, "20")

    def test_quiet_child_hidden_by_default_but_shown_when_selected(self):
        # The name is always in the filter dropdown; assert on the CARD heading
        # (`mb-0">Quiet`) so we test the data card, not the <option>.
        self.client.login(username="hp", password="pw")
        default = self.client.get(reverse("worklog:hours_report"))
        self.assertNotContains(default, 'mb-0">Quiet')       # no activity -> no card
        picked = self.client.get(reverse("worklog:hours_report"), {"child": self.quiet.pk})
        self.assertContains(picked, 'mb-0">Quiet')           # explicit pick shows the empty child

    def test_csv_has_per_subject_rows_and_a_child_total(self):
        self.client.login(username="hp", password="pw")
        resp = self.client.get(reverse("worklog:hours_report"), {"format": "csv"})
        self.assertEqual(resp["Content-Type"], "text/csv")
        body = resp.content.decode()
        self.assertIn("Child,Subject,Days,Minutes,Hours", body)
        self.assertIn("Math", body)
        self.assertIn("— All subjects —", body)
        # Violet's total row: 1 day, 60 minutes.
        self.assertIn("— All subjects —,1,60", body)

    def test_other_family_parent_sees_only_their_own(self):
        self.client.login(username="ho", password="pw")
        resp = self.client.get(reverse("worklog:hours_report"))
        self.assertContains(resp, "Zed")
        self.assertNotContains(resp, "Violet")

    def test_multi_family_user_sees_only_the_selected_family(self):
        """A user in two families who selects family A must not see family B's child
        here — matching how worklog_report/charter_report scope to the selected
        family (regression guard for the review's Low-2)."""
        second_fam = Family.objects.create(name="Second Family")
        FamilyMembership.objects.create(user=self.parent, family=second_fam, role="parent")
        far_child = Student.objects.create(
            parent=self.parent, first_name="Faraway", grade_level="G02", family=second_fam)
        WorkLogEntry.objects.create(parent=self.parent, family=second_fam, child=far_child,
                                    subject="Math", date=self.today, minutes=30)
        self.client.login(username="hp", password="pw")
        # Select the FIRST family explicitly.
        resp = self.client.get(reverse("worklog:hours_report"), {"family_id": self.fam.pk})
        self.assertContains(resp, 'mb-0">Violet')            # selected family's child
        self.assertNotContains(resp, 'mb-0">Faraway')        # other family's child, hidden


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

    def test_stamp_updates_existing_never_duplicates(self):
        # Re-stamping an entry updates its single assessment rather than inserting a
        # second — the create/update guard behind report_stamp's idempotency (the view
        # now also locks the entry so a concurrent double-submit can't race a duplicate).
        self.client.login(username="cparent", password="pw")
        url = reverse("worklog:report_stamp", kwargs={"entry_pk": self.photo.pk})
        self.client.post(url, {"final_level": "developing"})    # creates
        self.assertEqual(self.photo.assessments.count(), 1)
        self.client.post(url, {"final_level": "mastered"})      # updates, not duplicates
        self.assertEqual(self.photo.assessments.count(), 1)
        self.assertEqual(self.photo.assessments.first().final_level, "mastered")

    def test_charter_report_hides_edit_from_cross_family_viewer(self):
        # An editor of ANOTHER family who is only a viewer of THIS family must not see
        # the inline stamp controls on the selected family's report (display can_edit
        # gated per selected family, not the global user_can_edit).
        cross = User.objects.create_user(username="crossgrader", email="cg@e.com", password="pw")
        other = Family.objects.create(name="Other CG Fam")
        FamilyMembership.objects.create(user=cross, family=other, role="parent")   # editor elsewhere
        FamilyMembership.objects.create(user=cross, family=self.fam, role="teacher")  # viewer here
        self.client.force_login(cross)
        resp = self._report(family_id=self.fam.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context["can_edit"])          # no stamp controls for a viewer
        # sanity: the actual editing parent still gets can_edit on the same report
        self.client.force_login(self.parent)
        self.assertTrue(self._report(family_id=self.fam.pk).context["can_edit"])

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


class CompletionReportShowsTheWorkTests(TestCase):
    """The Completion Report has to show what she DID, not a sentence about it.

    It used to print `WorkLogEntry.description` — a prose summary baked in at
    submit time — inside a five-column table. Two things were wrong with that,
    and a parent printing a month of work hit both:

      - a mark-the-sentence exercise came out as
        "[marked up the sentence "Ron built a table." — annotated: yes]",
        which records that she drew something without showing what she drew;
      - a long answer got only the width of one table column, so an essay
        printed as a thirty-character ribbon running over dozens of pages.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="rparent", email="rp@e.com", password="pw")
        cls.fam = Family.objects.create(name="Report Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.fam)
        cls.today = timezone.localdate()

        cur = Curriculum.objects.create(
            parent=cls.parent, name="Essentials in Writing 3", subject="Writing",
            family=cls.fam)
        ch = Chapter.objects.create(curriculum=cur, number=1, title="Unit 1")
        lesson = Lesson.objects.create(chapter=ch, order=6, number=6, title="L6")
        cls.qset = QuestionSet.objects.create(
            lesson=lesson, title="Complete and Incomplete Sentences", family=cls.fam,
            status=QuestionSet.APPROVED, rubric="Mark the sentences.")
        cls.drawn = Question.objects.create(
            question_set=cls.qset, order=1, category="editing",
            response_type=Question.TYPE_MARKUP,
            prompt="Mark the complete sentences.",
            passage="Ron built a table.")
        cls.typed = Question.objects.create(
            question_set=cls.qset, order=2, category="writing",
            response_type=Question.TYPE_TEXT,
            prompt="Write about something you love.")

        cls.entry = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.violet, subject="Writing", family=cls.fam,
            date=cls.today,
            # The old prose summary, still stored on the entry.
            description=('Lesson 6 · Mark the sentences — submitted from '
                         "Violet's portal.\n\nQ1 [Editing]:\nA: [marked up the "
                         'sentence "Ron built a table." — annotated: yes]'))
        cls.sheet = ResponseSheet.objects.create(
            question_set=cls.qset, child=cls.violet,
            answers={
                str(cls.drawn.pk): json.dumps({
                    "strokes": [{"c": "#d64545", "w": 3,
                                 "p": [[0.1, 0.5], [0.4, 0.5], [0.7, 0.52]]}],
                    "surface": {"w": 600, "h": 90},
                    "marks": [{"i": 0, "word": "Ron", "kind": "underlined"}],
                    "unread": 0,
                }),
                str(cls.typed.pk): "I love the forest because it is quiet.",
            },
            status=ResponseSheet.SUBMITTED, work_entry=cls.entry,
            submitted_at=timezone.now())

    def _report(self, **params):
        self.client.login(username="rparent", password="pw")
        return self.client.get(reverse("worklog:worklog_report"), params)

    def test_drawn_work_is_replayed_not_described(self):
        resp = self._report()
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # Her actual strokes reach the page…
        self.assertIn("markup-replay", html)
        self.assertIn("<svg", html)
        # …and the prose stand-in for them does not.
        self.assertNotIn("annotated: yes", html)
        self.assertNotIn("[marked up the sentence", html)

    def test_typed_answers_and_their_questions_both_appear(self):
        """A report that shows answers without their questions is a list of
        sentences nobody can mark."""
        html = self._report().content.decode()
        self.assertIn("Write about something you love.", html)
        self.assertIn("I love the forest because it is quiet.", html)
        self.assertIn("Mark the complete sentences.", html)

    def test_the_work_is_not_squeezed_into_a_table_column(self):
        """The five-column table is what made an essay print as a ribbon."""
        html = self._report().content.decode()
        self.assertNotIn("What was done", html)      # the old column header
        self.assertIn("ss-entry", html)              # the full-width block

    def test_an_entry_with_no_sheet_still_shows_its_note(self):
        """Photos and hand-written notes have no answer sheet, and must not
        vanish now that the report renders sheets."""
        WorkLogEntry.objects.create(
            parent=self.parent, child=self.violet, subject="Nature",
            family=self.fam, date=self.today,
            description="We went on a nature walk and found acorns.")
        html = self._report().content.decode()
        self.assertIn("We went on a nature walk and found acorns.", html)

    def test_the_range_and_child_filters_still_apply(self):
        """The report is a date-range record; showing work outside the range
        would misstate what was done in the period."""
        old = WorkLogEntry.objects.create(
            parent=self.parent, child=self.violet, subject="History",
            family=self.fam, date=self.today - timedelta(days=400),
            description="Ancient Egypt lapbook.")
        html = self._report(start=(self.today - timedelta(days=7)).isoformat(),
                            end=self.today.isoformat()).content.decode()
        self.assertNotIn("Ancient Egypt lapbook.", html)
        self.assertIn("I love the forest because it is quiet.", html)
        old.delete()

    def _extra_entries(self, n, offset=0):
        lesson = self.qset.lesson
        for i in range(offset, offset + n):
            # A sheet is unique per (question_set, child), so each extra entry
            # needs its own set — which is also the realistic shape: six days of
            # work is six different worksheets.
            qs = QuestionSet.objects.create(
                lesson=lesson, title="Extra %d" % i, family=self.fam,
                status=QuestionSet.APPROVED, rubric="r")
            q = Question.objects.create(
                question_set=qs, order=1, category="writing",
                response_type=Question.TYPE_TEXT, prompt="Prompt %d" % i)
            e = WorkLogEntry.objects.create(
                parent=self.parent, child=self.violet, subject="Writing",
                family=self.fam, date=self.today, description="extra %d" % i)
            ResponseSheet.objects.create(
                question_set=qs, child=self.violet,
                answers={str(q.pk): "answer %d" % i},
                status=ResponseSheet.SUBMITTED, work_entry=e,
                submitted_at=timezone.now())
    def test_the_query_count_does_not_grow_with_the_number_of_entries(self):
        """A month of work is ~80 entries and this page renders every one.

        Asserting an absolute number would just encode today's overhead; what
        matters is the SHAPE. Doubling the entries must not change the query
        count — if it does, the sheets, their questions or the assessments are
        being fetched per row, and printing a term's work walks off a cliff.
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        self.client.login(username="rparent", password="pw")

        def count():
            with CaptureQueriesContext(connection) as ctx:
                resp = self.client.get(reverse("worklog:worklog_report"))
            self.assertEqual(resp.status_code, 200)
            return len(ctx.captured_queries)

        self._extra_entries(6)
        count()          # warm up: the first request also creates the session
        few = count()
        self._extra_entries(12, offset=6)
        many = count()
        self.assertEqual(few, many,
                         "queries grew from %d to %d when the entries tripled"
                         % (few, many))


@override_settings(MEDIA_ROOT=MEDIA)
class PaperCopyCompletionTests(TestCase):
    """Work done on paper: uploaded, then approved — and complete only if both.

    Joyce does some of the Blackbird sections on paper, because the guide is a
    paper book. The rule she asked for is deliberately two-key: a file with no
    approval is a section still waiting, and an approval with no file would be
    a completed section with nothing behind it — which is the one thing a work
    log must never contain.
    """

    @classmethod
    def setUpTestData(cls):
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(
            username="pp", email="pp@e.com", password="pw")
        cls.fam = Family.objects.create(name="Paper Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam, role="parent")
        cls.kid = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.fam)
        cls.token = make_portal_token(cls.kid)
        cls.today = timezone.localdate()

        cur = Curriculum.objects.create(
            parent=cls.parent, name="Rickshaw Girl — Literature Discovery",
            subject="Literature", family=cls.fam)
        ch = Chapter.objects.create(curriculum=cur, number=1, title="Sections")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="S1")
        cls.qset = QuestionSet.objects.create(
            lesson=lesson, title="Section 1 · Explore", family=cls.fam,
            status=QuestionSet.APPROVED, rubric="r")
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="writing",
            response_type=Question.TYPE_TEXT, prompt="What did you notice?")
        # The portal only exposes sets for curricula the child is PLACED on —
        # that gate is the portal's authorization, so a fixture without it
        # tests a page she could never reach.
        from curricula.models import CurriculumPlacement
        CurriculumPlacement.objects.create(child=cls.kid, curriculum=cur,
                                           current_lesson=lesson)

    def _png(self, name="page.png"):
        return SimpleUploadedFile(name, b"\x89PNG\r\n\x1a\n" + b"0" * 64,
                                  content_type="image/png")

    def _upload_url(self):
        return reverse("portal:portal_project_upload",
                       args=[self.token, self.qset.pk])

    def _approve_url(self):
        return reverse("students:student_work_set_approve",
                       args=[self.kid.pk, self.qset.pk])

    def _sheet(self):
        return ResponseSheet.objects.get(question_set=self.qset, child=self.kid)

    # -- the two-key rule --------------------------------------------------

    def test_an_upload_alone_does_not_complete_the_section(self):
        """The child hands work in; it waits for a parent."""
        self.client.post(self._upload_url(), {"project": self._png()})
        sheet = self._sheet()
        self.assertTrue(sheet.has_project_file)
        self.assertFalse(sheet.is_submitted)
        self.assertTrue(sheet.awaiting_approval)
        self.assertIsNone(sheet.work_entry)
        self.assertIsNone(sheet.approved_at)

    def test_approval_alone_is_refused_when_nothing_is_attached(self):
        """A section cannot be marked done with nothing to show for it."""
        self.client.login(username="pp", password="pw")
        resp = self.client.post(self._approve_url(), follow=True)
        self.assertEqual(resp.status_code, 200)
        sheet = self._sheet()
        self.assertFalse(sheet.is_submitted)
        self.assertIsNone(sheet.work_entry)
        self.assertContains(resp, "can&#x27;t be marked complete")

    def test_upload_then_approve_completes_it_and_logs_the_work(self):
        self.client.post(self._upload_url(), {"project": self._png()})
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url())

        sheet = self._sheet()
        self.assertTrue(sheet.is_submitted)
        self.assertTrue(sheet.is_on_paper)
        self.assertIsNotNone(sheet.approved_at)
        self.assertEqual(sheet.approved_by, self.parent)
        self.assertIsNotNone(sheet.work_entry)
        self.assertEqual(sheet.work_entry.child, self.kid)
        self.assertIn("on paper", sheet.work_entry.description)

    def test_the_parent_can_attach_and_complete_in_one_go(self):
        """Joyce scans the paper herself rather than handing over the tablet."""
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url(), {"project": self._png("scan.png")})
        sheet = self._sheet()
        self.assertTrue(sheet.is_submitted)
        self.assertTrue(sheet.has_project_file)
        self.assertIn("scan", sheet.project_filename)

    # -- the file reaches the record --------------------------------------

    def test_the_paper_copy_appears_in_the_completion_report(self):
        """The whole point: a reviewing teacher sees the work, not a filename
        in a row that says something happened."""
        self.client.post(self._upload_url(), {"project": self._png("mywork.png")})
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url())

        html = self.client.get(reverse("worklog:worklog_report")).content.decode()
        self.assertIn("Completed on paper", html)
        self.assertIn("mywork", html)
        # An image is shown, not merely linked.
        self.assertIn("ss-work-img", html)

    def test_a_pdf_is_linked_rather_than_shown_as_a_broken_image(self):
        pdf = SimpleUploadedFile("project.pdf", b"%PDF-1.4 ...",
                                 content_type="application/pdf")
        self.client.post(self._upload_url(), {"project": pdf})
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url())

        sheet = self._sheet()
        self.assertFalse(sheet.project_is_image)
        html = self.client.get(reverse("worklog:worklog_report")).content.decode()
        self.assertIn("project", html)
        self.assertIn("📎", html)

    def test_heic_is_never_rendered_as_an_image(self):
        """Browsers cannot draw HEIC — an <img> would be a broken icon in the
        middle of a printed report, and phones produce HEIC by default."""
        self.client.post(self._upload_url(),
                         {"project": self._png("photo.heic")})
        self.assertFalse(self._sheet().project_is_image)

    # -- what must be refused ---------------------------------------------

    def test_an_executable_is_refused(self):
        bad = SimpleUploadedFile("run.exe", b"MZ\x90\x00", content_type="application/exe")
        resp = self.client.post(self._upload_url(), {"project": bad}, follow=True)
        self.assertContains(resp, "isn&#x27;t one we can take")
        self.assertFalse(
            ResponseSheet.objects.filter(question_set=self.qset).exists()
            and self._sheet().has_project_file)

    def test_an_oversized_file_is_refused(self):
        big = SimpleUploadedFile(
            "huge.png", b"\x89PNG\r\n\x1a\n" + b"0" * (26 * 1024 * 1024),
            content_type="image/png")
        resp = self.client.post(self._upload_url(), {"project": big}, follow=True)
        self.assertContains(resp, "too big")
        self.assertFalse(self._sheet().has_project_file)

    def test_a_submitted_section_stops_accepting_uploads(self):
        self.client.post(self._upload_url(), {"project": self._png()})
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url())
        self.client.logout()

        before = self._sheet().project_filename
        self.client.post(self._upload_url(), {"project": self._png("later.png")})
        self.assertEqual(self._sheet().project_filename, before)

    def test_approving_twice_does_not_log_the_work_twice(self):
        self.client.post(self._upload_url(), {"project": self._png()})
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url())
        first = self._sheet().work_entry_id
        self.client.post(self._approve_url())
        self.assertEqual(self._sheet().work_entry_id, first)
        self.assertEqual(WorkLogEntry.objects.filter(child=self.kid).count(), 1)

    def test_a_stranger_cannot_approve_another_familys_work(self):
        other = User.objects.create_user(
            username="nosy", email="n@e.com", password="pw")
        Family.objects.create(name="Other Fam")
        self.client.post(self._upload_url(), {"project": self._png()})
        self.client.login(username="nosy", password="pw")
        resp = self.client.post(self._approve_url())
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(self._sheet().is_submitted)
        self.assertTrue(other.pk)

    def test_the_upload_is_not_reachable_without_the_token(self):
        """Portal auth is the signed token; a guessed set id is not enough."""
        bad = reverse("portal:portal_project_upload",
                      args=["not-a-real-token", self.qset.pk])
        resp = self.client.post(bad, {"project": self._png()})
        self.assertIn(resp.status_code, (403, 404))

    # -- gaps a second reader found in the tests above ---------------------

    def test_the_scan_is_shown_inline_not_merely_linked(self):
        """The first version of this asserted `"ss-work-img" in html`, which is
        in the page's own <style> block on every render — it passed with the
        <img> branch deleted entirely. Match the TAG, and prove the link form
        is not what was rendered."""
        import re

        self.client.post(self._upload_url(), {"project": self._png("scan.png")})
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url())

        html = self.client.get(reverse("worklog:worklog_report")).content.decode()
        self.assertRegex(html, r'<img[^>]*class="ss-work-img"')
        self.assertNotIn("📎", html)

    def test_the_scan_reaches_the_charter_report_too(self):
        """That is the one that leaves the house. Nothing fetched it."""
        import re

        self.client.post(self._upload_url(), {"project": self._png("scan.png")})
        self.client.login(username="pp", password="pw")
        self.client.post(self._approve_url())

        html = self.client.get(reverse("worklog:charter_report")).content.decode()
        self.assertIn("Completed on paper", html)
        self.assertRegex(html, r'<img[^>]*class="ss-work-img"')

    def test_typing_the_answers_and_turning_them_in_keeps_them_in_the_report(self):
        """Both controls are on the same page. Uploading a photo and THEN
        answering on screen used to file the section as paper work — the report
        showed the photo instead of her writing, over a file no parent had
        approved."""
        self.client.post(self._upload_url(), {"project": self._png()})
        self.client.post(
            reverse("portal:portal_questions", args=[self.token, self.qset.pk]),
            {"answer_%d" % self.q.pk: "The rickshaw was bright yellow.",
             "action": "submit"})

        sheet = self._sheet()
        self.assertTrue(sheet.is_submitted)
        self.assertFalse(sheet.is_on_paper, "answering on screen is on-screen work")
        self.assertIsNone(sheet.approved_at)

        self.client.login(username="pp", password="pw")
        html = self.client.get(reverse("worklog:worklog_report")).content.decode()
        self.assertIn("The rickshaw was bright yellow.", html)
        self.assertNotIn("Completed on paper", html)

    def test_an_unapproved_upload_is_never_labelled_complete_on_paper(self):
        """Belt and braces on the same hole: the report's paper label requires
        a parent's approval, not merely a file."""
        self.client.post(self._upload_url(), {"project": self._png()})
        entry = WorkLogEntry.objects.create(
            parent=self.parent, child=self.kid, subject="Literature",
            family=self.fam, date=self.today, description="manual row")
        sheet = self._sheet()
        sheet.work_entry = entry
        sheet.save(update_fields=["work_entry"])

        self.client.login(username="pp", password="pw")
        html = self.client.get(reverse("worklog:worklog_report")).content.decode()
        self.assertNotIn("Completed on paper", html)

    def test_a_parent_cannot_approve_against_another_familys_section(self):
        """The child was scoped; the SET id was a free parameter. Posting
        another family's set_pk created a sheet against their section and a
        work-log row carrying their curriculum and section title."""
        from tutor.models import QuestionSet as QS

        other_parent = User.objects.create_user(
            username="op", email="op@e.com", password="pw")
        other_fam = Family.objects.create(name="Other Fam")
        FamilyMembership.objects.create(
            user=other_parent, family=other_fam, role="parent")
        other_cur = Curriculum.objects.create(
            parent=other_parent, name="Their Secret Curriculum",
            subject="Literature", family=other_fam)
        other_ch = Chapter.objects.create(curriculum=other_cur, number=1, title="C")
        other_lesson = Lesson.objects.create(
            chapter=other_ch, order=1, number=1, title="L")
        other_set = QS.objects.create(
            lesson=other_lesson, title="Their Private Section", family=other_fam,
            status=QS.APPROVED, rubric="r")

        self.client.login(username="pp", password="pw")
        resp = self.client.post(
            reverse("students:student_work_set_approve",
                    args=[self.kid.pk, other_set.pk]),
            {"project": self._png()})
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(
            ResponseSheet.objects.filter(question_set=other_set).exists())
        self.assertFalse(
            WorkLogEntry.objects.filter(curriculum=other_cur).exists())

    def test_the_parent_endpoint_validates_the_file_too(self):
        """A second, independent copy of the validation lives there and had no
        test on it at all."""
        self.client.login(username="pp", password="pw")
        bad = SimpleUploadedFile("run.exe", b"MZ\x90\x00",
                                 content_type="application/exe")
        resp = self.client.post(self._approve_url(), {"project": bad}, follow=True)
        self.assertContains(resp, "Use a photo, a PDF or a Word document")
        self.assertFalse(self._sheet().has_project_file)
        self.assertFalse(self._sheet().is_submitted)

        big = SimpleUploadedFile(
            "huge.png", b"\x89PNG\r\n\x1a\n" + b"0" * (26 * 1024 * 1024),
            content_type="image/png")
        resp = self.client.post(self._approve_url(), {"project": big}, follow=True)
        self.assertContains(resp, "over the")
        self.assertFalse(self._sheet().has_project_file)

    def test_the_portal_upload_is_scoped_to_sets_the_child_can_open(self):
        """A valid token is not a licence to write to any set in the database.
        The earlier test used a bad TOKEN, which fails one step earlier."""
        from tutor.models import QuestionSet as QS

        stranger_parent = User.objects.create_user(
            username="sp", email="sp@e.com", password="pw")
        stranger_fam = Family.objects.create(name="Stranger Fam")
        cur = Curriculum.objects.create(
            parent=stranger_parent, name="Not Hers", subject="Literature",
            family=stranger_fam)
        ch = Chapter.objects.create(curriculum=cur, number=1, title="C")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L")
        theirs = QS.objects.create(
            lesson=lesson, title="Not Hers", family=stranger_fam,
            status=QS.APPROVED, rubric="r")

        resp = self.client.post(
            reverse("portal:portal_project_upload", args=[self.token, theirs.pk]),
            {"project": self._png()})
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(ResponseSheet.objects.filter(question_set=theirs).exists())

    def test_the_autosave_endpoint_keeps_its_csrf_exemption(self):
        """It is exempt so navigator.sendBeacon can deliver the last-chance
        save when a tablet backgrounds the app — a beacon cannot set a CSRF
        header. Inserting a view above it once stole its decorators, and the
        only symptom was children's typed work silently not saving."""
        from portal import views as portal_views

        self.assertTrue(getattr(portal_views.portal_autosave, "csrf_exempt", False))
        # …and it is still POST-only.
        resp = self.client.get(
            reverse("portal:portal_autosave", args=[self.token, self.qset.pk]))
        self.assertEqual(resp.status_code, 405)
