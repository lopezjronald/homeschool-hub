from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import UserProfile
from activities.models import ExternalActivity
from core.models import Family, FamilyMembership
from core.services import get_inbox_buckets, inbox_count
from curricula.models import Chapter, Curriculum, Lesson
from students.models import Student
from tutor.models import MasteryAssessment, Material, Question, QuestionSet, ResponseSheet
from worklog.models import WorkLogEntry

User = get_user_model()


class InboxTests(TestCase):
    """The action inbox aggregates everything needing an editor, family-scoped."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ip", email="ip@e.com", password="pw")
        cls.teacher = User.objects.create_user(username="it", email="it@e.com", password="pw")
        cls.family = Family.objects.create(name="Inbox Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Rae", grade_level="G03", family=cls.family,
        )

        # A second family whose items must never appear.
        cls.other = User.objects.create_user(username="io", email="io@e.com", password="pw")
        cls.other_family = Family.objects.create(name="Other Fam")
        FamilyMembership.objects.create(user=cls.other, family=cls.other_family, role="parent")
        cls.other_child = Student.objects.create(
            parent=cls.other, first_name="Zed", grade_level="G03", family=cls.other_family,
        )

        cls.today = timezone.localdate()
        cur = Curriculum.objects.create(parent=cls.parent, name="Writing 3", subject="Writing", family=cls.family)
        ch = Chapter.objects.create(curriculum=cur, number=1, title="Unit 1")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")

        # (1a) finalize: an agent-drafted DRAFT assessment (child submitted).
        e1 = WorkLogEntry.objects.create(parent=cls.parent, child=cls.child, subject="Writing", family=cls.family, date=cls.today)
        MasteryAssessment.objects.create(
            work_entry=e1, rubric="r", answers="a", ai_level="developing", ai_summary="s",
            ai_criteria=[], ai_encouragement="Nice work Rae!", graded_by=None, status=MasteryAssessment.DRAFT,
        )
        # (1b) finalize: a parent-STARTED DRAFT — must also surface (graded_by set).
        e2 = WorkLogEntry.objects.create(parent=cls.parent, child=cls.child, subject="Reading", family=cls.family, date=cls.today)
        MasteryAssessment.objects.create(
            work_entry=e2, rubric="r", answers="a", ai_level="proficient", ai_summary="s",
            ai_criteria=[], graded_by=cls.parent, status=MasteryAssessment.DRAFT,
        )

        # (2) ungraded: a submitted sheet with no assessment.
        qset = QuestionSet.objects.create(lesson=cls.lesson, title="Q", family=cls.family, status=QuestionSet.APPROVED, rubric="r")
        cls.q = Question.objects.create(question_set=qset, order=1, category="editing", prompt="Why?")
        e3 = WorkLogEntry.objects.create(parent=cls.parent, child=cls.child, subject="Math", family=cls.family, date=cls.today)
        ResponseSheet.objects.create(
            question_set=qset, child=cls.child, answers={str(cls.q.pk): "..."},
            status=ResponseSheet.SUBMITTED, work_entry=e3, submitted_at=timezone.now(),
        )

        # (3) a draft material awaiting approval.
        Material.objects.create(lesson=cls.lesson, family=cls.family, title="Draft comic", student_content="...", status=Material.DRAFT)

        # (4) an activity check-in that's due (weekly, last logged 30 days ago).
        ExternalActivity.objects.create(
            parent=cls.parent, family=cls.family, title="Guitar", url="https://x.example",
            cadence=ExternalActivity.CADENCE_WEEKLY, last_logged_at=cls.today - timedelta(days=30), is_active=True,
        )

        # second-family noise: a draft assessment that must NOT show.
        oe = WorkLogEntry.objects.create(parent=cls.other, child=cls.other_child, subject="Writing", family=cls.other_family, date=cls.today)
        MasteryAssessment.objects.create(work_entry=oe, rubric="r", answers="a", ai_level="developing", ai_summary="s", ai_criteria=[], status=MasteryAssessment.DRAFT)

        cls.url = reverse("inbox:inbox")

    def _req(self, user):
        req = RequestFactory().get(self.url)
        req.user = user
        return req

    # ---- service-level (precise counts) ----

    def test_editor_bucket_counts(self):
        buckets = get_inbox_buckets(self._req(self.parent), self.family)
        by_key = {b["key"]: b for b in buckets["buckets"]}
        self.assertEqual(len(by_key["finalize"]["items"]), 2)   # both draft types
        self.assertEqual(len(by_key["ungraded"]["items"]), 1)   # not double-counted with finalize
        self.assertEqual(len(by_key["materials"]["items"]), 1)
        self.assertEqual(len(by_key["activities"]["items"]), 1)
        self.assertEqual(buckets["total"], 5)

    def test_badge_count_excludes_activities(self):
        # 2 finalize + 1 ungraded + 1 material = 4 (activity is Python-only).
        self.assertEqual(inbox_count(self._req(self.parent), self.family), 4)

    def test_reviewer_gets_empty_inbox(self):
        self.assertEqual(get_inbox_buckets(self._req(self.teacher), self.family)["buckets"], [])
        self.assertEqual(inbox_count(self._req(self.teacher), self.family), 0)

    def test_new_flag_uses_last_seen(self):
        # Never opened → nothing flagged new (calm first visit).
        self.assertEqual(get_inbox_buckets(self._req(self.parent), self.family)["new"], 0)
        # Opened in the past → the four DB items read as new.
        prof = UserProfile.get_for(self.parent)
        prof.inbox_seen_at = timezone.now() - timedelta(hours=1)
        prof.save(update_fields=["inbox_seen_at"])
        self.assertEqual(get_inbox_buckets(self._req(self.parent), self.family)["new"], 4)

    # ---- view-level ----

    def test_requires_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)

    def test_editor_page_shows_all_buckets(self):
        self.client.login(username="ip", password="pw")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        for title in ("Finalize proficiency", "Work to grade", "Materials to approve", "Activity check-ins"):
            self.assertContains(resp, title)
        self.assertContains(resp, "Draft comic")
        self.assertContains(resp, "Guitar")
        self.assertNotContains(resp, "Zed")            # second family excluded

    def test_reviewer_page_is_empty(self):
        self.client.login(username="it", password="pw")
        resp = self.client.get(self.url)
        self.assertContains(resp, "all caught up")
        self.assertNotContains(resp, "Finalize proficiency")

    def test_visiting_stamps_seen(self):
        self.assertIsNone(UserProfile.get_for(self.parent).inbox_seen_at)
        self.client.login(username="ip", password="pw")
        self.client.get(self.url)
        self.assertIsNotNone(UserProfile.get_for(self.parent).inbox_seen_at)

    def test_nav_bell_visible_to_editor_only(self):
        # The nav bell is the only link to /inbox/; check it on a page whose own
        # content doesn't mention the inbox (home) to avoid a false match.
        home = reverse("home")
        self.client.login(username="ip", password="pw")
        self.assertContains(self.client.get(home), 'href="/inbox/"')       # editor gets the bell
        self.client.logout()
        self.client.login(username="it", password="pw")
        self.assertNotContains(self.client.get(home), 'href="/inbox/"')    # reviewer: no bell
