import json
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import Family, FamilyMembership
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet
from worklog.models import WorkLogEntry

from .tokens import make_portal_token, student_from_token

User = get_user_model()


class PortalTokenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="pp", email="pp@e.com", password="pw")
        cls.family = Family.objects.create(name="Portal Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.kid = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )

    def test_round_trip(self):
        token = make_portal_token(self.kid)
        self.assertEqual(student_from_token(token), self.kid)

    def test_bad_token_returns_none_and_404(self):
        self.assertIsNone(student_from_token("garbage"))
        resp = self.client.get(reverse("portal:portal_home", kwargs={"token": "garbage"}))
        self.assertEqual(resp.status_code, 404)

    def test_rotating_key_revokes_link(self):
        from students.models import _new_portal_key

        token = make_portal_token(self.kid)
        self.assertEqual(student_from_token(token), self.kid)
        self.kid.portal_key = _new_portal_key()
        self.kid.save(update_fields=["portal_key"])
        # old token no longer resolves; a fresh one does
        self.assertIsNone(student_from_token(token))
        self.assertEqual(student_from_token(make_portal_token(self.kid)), self.kid)


class PortalCourseTests(TestCase):
    """The full Kaylin flow: seeded course -> portal -> autosave -> submit."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="dad", email="dad@e.com", password="pw")
        cls.family = Family.objects.create(name="Course Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        call_command("seed_i_am_david", "--for-user", "dad", stdout=StringIO())
        cls.token = make_portal_token(cls.kaylin)
        cls.first_set = QuestionSet.objects.order_by("pk").first()

    def _url(self, name, **kwargs):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kwargs})

    def test_seed_created_full_course(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        self.assertEqual(curriculum.grade_level, "G07")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        self.assertEqual(sets.count(), 25)  # 6 per section x 4 + Glean
        self.assertEqual(
            Question.objects.filter(question_set__in=sets).count(), 162,
        )
        # Socratic sets exist per section with story-grammar categories
        socratic = sets.filter(title__contains="Socratic")
        self.assertEqual(socratic.count(), 4)
        cats = set(
            Question.objects.filter(question_set__in=socratic).values_list("category", flat=True)
        )
        for expected in ("setting", "character", "conflict", "plot", "theme"):
            self.assertIn(expected, cats)
        # Kaylin is placed
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.kaylin, curriculum=curriculum).exists()
        )

    def test_seed_is_idempotent(self):
        call_command("seed_i_am_david", "--for-user", "dad", stdout=StringIO())
        self.assertEqual(QuestionSet.objects.count(), 25)
        self.assertEqual(Question.objects.count(), 162)

    def test_portal_home_groups_by_section(self):
        resp = self.client.get(self._url("portal_home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Kaylin")
        self.assertContains(resp, "Section 1: Chapters 1–2")
        self.assertContains(resp, "Comprehension")

    def test_discussion_sets_hidden_from_student_portal(self):
        # Socratic + Discussion are teacher-led — never shown to the child.
        resp = self.client.get(self._url("portal_home"))
        self.assertNotContains(resp, "Socratic Seminar")
        socratic = QuestionSet.objects.filter(title__contains="Socratic").first()
        opened = self.client.get(self._url("portal_questions", set_pk=socratic.pk))
        self.assertEqual(opened.status_code, 404)  # not openable as a student form

    def test_discussion_guide_shows_socratic_to_parent(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        self.client.login(username="dad", password="pw")
        resp = self.client.get(reverse("tutor:discussion_guide", kwargs={"curriculum_pk": curriculum.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Socratic Seminar")
        self.assertContains(resp, "Discussion")
        self.assertContains(resp, "lead")  # facilitation guidance

    def test_form_disables_autocorrect(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.first_set.pk))
        self.assertContains(resp, 'spellcheck="false"')
        self.assertContains(resp, 'autocorrect="off"')
        self.assertContains(resp, 'autocapitalize="off"')
        self.assertContains(resp, 'data-gramm="false"')
        self.assertContains(resp, "portal-autosave")  # hashed filename under manifest storage

    def test_autosave_saves_and_scopes(self):
        q = self.first_set.questions.first()
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.first_set.pk),
            data=json.dumps({"answers": {str(q.pk): "My notes on David.", "99999": "evil"}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["ok"])
        sheet = ResponseSheet.objects.get(question_set=self.first_set, child=self.kaylin)
        self.assertEqual(sheet.answers[str(q.pk)], "My notes on David.")
        self.assertNotIn("99999", sheet.answers)

    def test_submit_creates_worklog_entry_and_locks(self):
        q = self.first_set.questions.first()
        resp = self.client.post(
            self._url("portal_questions", set_pk=self.first_set.pk),
            data={f"answer_{q.pk}": "David escapes bravely."},
        )
        self.assertEqual(resp.status_code, 302)
        sheet = ResponseSheet.objects.get(question_set=self.first_set, child=self.kaylin)
        self.assertTrue(sheet.is_submitted)
        self.assertIsNotNone(sheet.work_entry)
        self.assertEqual(sheet.work_entry.child, self.kaylin)
        self.assertIn("David escapes bravely.", sheet.work_entry.description)
        # further autosaves are rejected
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.first_set.pk),
            data=json.dumps({"answers": {str(q.pk): "sneaky edit"}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)
        # and the page renders read-only celebration
        resp = self.client.get(self._url("portal_questions", set_pk=self.first_set.pk))
        self.assertContains(resp, "Turned in!")
        self.assertContains(resp, "readonly")

    def test_double_submit_creates_one_worklog_entry(self):
        q = self.first_set.questions.first()
        url = self._url("portal_questions", set_pk=self.first_set.pk)
        self.client.post(url, data={f"answer_{q.pk}": "First submit."})
        # a second POST (double-click / stale tab) must NOT create a 2nd entry
        self.client.post(url, data={f"answer_{q.pk}": "Second submit changes nothing."})
        sheets = ResponseSheet.objects.filter(question_set=self.first_set, child=self.kaylin)
        self.assertEqual(sheets.count(), 1)
        self.assertEqual(
            WorkLogEntry.objects.filter(child=self.kaylin, description__contains="Section 1").count(),
            1,
        )
        self.assertIn("First submit.", sheets.first().work_entry.description)

    def test_autosave_rejects_non_object_payload(self):
        for bad in ("[]", '"hi"', "5", "null"):
            resp = self.client.post(
                self._url("portal_autosave", set_pk=self.first_set.pk),
                data=bad, content_type="application/json",
            )
            self.assertEqual(resp.status_code, 400, bad)

    def test_sibling_cannot_open_other_childs_course(self):
        violet_token = make_portal_token(self.violet)
        resp = self.client.get(
            reverse("portal:portal_questions", kwargs={
                "token": violet_token, "set_pk": self.first_set.pk,
            })
        )
        self.assertEqual(resp.status_code, 404)
        home = self.client.get(reverse("portal:portal_home", kwargs={"token": violet_token}))
        self.assertNotContains(home, "I Am David")

    def test_draft_sets_hidden(self):
        QuestionSet.objects.all().update(status=QuestionSet.DRAFT)
        resp = self.client.get(self._url("portal_home"))
        self.assertNotContains(resp, "Socratic Seminar")

    def test_parent_sees_portal_link_on_student_page(self):
        self.client.login(username="dad", password="pw")
        resp = self.client.get(reverse("students:student_detail", kwargs={"pk": self.kaylin.pk}))
        self.assertContains(resp, "portal")
        self.assertContains(resp, "Copy link")

    def test_assess_form_prefills_blackbird_rubric(self):
        q = self.first_set.questions.first()
        self.client.post(
            self._url("portal_questions", set_pk=self.first_set.pk),
            data={f"answer_{q.pk}": "My journal notes."},
        )
        sheet = ResponseSheet.objects.get(question_set=self.first_set, child=self.kaylin)
        self.client.login(username="dad", password="pw")
        resp = self.client.get(
            reverse("tutor:assess_create", kwargs={"entry_pk": sheet.work_entry.pk})
        )
        self.assertContains(resp, "Blackbird grading")     # rubric prefilled
        self.assertContains(resp, "My journal notes.")     # answers prefilled


class MarkupTests(TestCase):
    """Draw-on-the-sentence markup questions (Essentials in Writing)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="mup", email="mup@e.com", password="pw")
        cls.family = Family.objects.create(name="Markup Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Essentials in Writing 3", subject="Writing", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="Writing Sentences")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Mark it", family=cls.family,
            status=QuestionSet.APPROVED, intro="Underline the subject.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="editing",
            response_type=Question.TYPE_MARKUP, passage="The dog ran.", prompt="",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_markup_renders_canvas_and_passage(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.qset.pk))
        self.assertContains(resp, "markup-widget")
        self.assertContains(resp, "markup-canvas")
        self.assertContains(resp, "The dog ran.")
        self.assertContains(resp, "portal-markup")

    def test_markup_strokes_autosave_and_submit(self):
        strokes = '[{"c":"#333333","w":3,"p":[[0.1,0.5],[0.4,0.5]]}]'
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.qset.pk),
            data=json.dumps({"answers": {str(self.q.pk): strokes}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertEqual(sheet.answers[str(self.q.pk)], strokes)

        self.client.post(
            self._url("portal_questions", set_pk=self.qset.pk),
            data={f"answer_{self.q.pk}": strokes},
        )
        sheet.refresh_from_db()
        self.assertTrue(sheet.is_submitted)
        self.assertIn("marked up", sheet.work_entry.description)

    def test_eiw_seed_builds_markup_forms(self):
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        markup = Question.objects.filter(response_type=Question.TYPE_MARKUP)
        self.assertGreater(markup.count(), 100)
        self.assertTrue(markup.exclude(passage="").exists())
        # re-running is idempotent (no duplicate sets)
        before = QuestionSet.objects.count()
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        self.assertEqual(QuestionSet.objects.count(), before)
