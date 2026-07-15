import json
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Family, FamilyMembership
from curricula.models import Chapter, Curriculum, CurriculumPlacement, CurriculumResource, Lesson
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
        # The Journal's Q1 is now a per-character question; text-answer flow
        # tests target a plain typed question instead.
        cls.first_text_q = cls.first_set.questions.filter(
            response_type=Question.TYPE_TEXT,
        ).order_by("order").first()

    def _url(self, name, **kwargs):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kwargs})

    def test_seed_created_full_course(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        self.assertEqual(curriculum.grade_level, "G07")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        self.assertEqual(sets.count(), 27)  # 6/section x 4 + Glean + seminar + toolbox
        self.assertEqual(
            Question.objects.filter(question_set__in=sets).count(), 232,
        )
        # Acquire keeps the Level 7 guide's own format (look it up and write it),
        # with the official Blackbird definitions attached as a TEACHER key.
        vocab = sets.get(title="Section 1 · Vocabulary")
        vq = vocab.questions.order_by("order").first()
        self.assertEqual(vq.response_type, Question.TYPE_TEXT)
        self.assertIn("Define:", vq.prompt)
        self.assertIn("Official Blackbird definitions", vocab.answer_key)
        self.assertIn("catastrophe —", vocab.answer_key)
        # comprehension sets carry the answer key (grader reference, never shown)
        self.assertTrue(sets.filter(title__contains="Comprehension").exclude(answer_key="").exists())
        # the reusable literature standard sets exist (teacher-led)
        self.assertTrue(
            sets.filter(title__contains="Story-Grammar", mode=QuestionSet.MODE_DISCUSSION).exists()
        )
        self.assertTrue(
            sets.filter(title__contains="Literary Toolbox", mode=QuestionSet.MODE_DISCUSSION).exists()
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
        self.assertEqual(QuestionSet.objects.count(), 27)
        self.assertEqual(Question.objects.count(), 232)

    def test_portal_home_shows_one_calm_subject_card(self):
        # The "What's Next" home shows a subject CARD (curriculum name), not the
        # old wall of 27 set titles / section headings — those move to the drill-in.
        resp = self.client.get(self._url("portal_home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Kaylin")
        self.assertContains(resp, "I Am David")                 # the subject card
        self.assertContains(resp, "portal-subject-card")
        self.assertNotContains(resp, "Section 1: Chapters 1–2")  # no chapter dump on home
        self.assertNotContains(resp, "Comprehension")            # no set titles on home

    def test_portal_subject_drilldown_groups_by_chapter(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        resp = self.client.get(self._url("portal_subject", curriculum_id=curriculum.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Section 1: Chapters 1–2")     # chapter heading here
        self.assertContains(resp, "Comprehension")               # set titles here
        # the current chapter is expanded on load
        self.assertContains(resp, 'class="collapse show"')
        # and a big Continue points at the next unstarted set
        self.assertContains(resp, "Continue")

    def test_seeded_journal_uses_per_character_boxes(self):
        from tutor.models import Question

        journal = QuestionSet.objects.filter(title__endswith="Journal").first()
        char_q = journal.questions.get(order=1)
        self.assertEqual(char_q.response_type, Question.TYPE_CHARACTERS)
        self.assertIn("David", char_q.character_names)          # names live in passage now
        self.assertGreaterEqual(len(char_q.character_names), 2)  # a box per character
        self.assertNotIn("·", char_q.prompt)                    # names no longer crammed in the prompt

    def test_portal_subject_rejects_sibling(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        violet_token = make_portal_token(self.violet)
        resp = self.client.get(reverse("portal:portal_subject", kwargs={
            "token": violet_token, "curriculum_id": curriculum.pk,
        }))
        self.assertEqual(resp.status_code, 404)

    def test_next_set_advances_after_submit(self):
        from portal.views import _subject_cards

        first_next = _subject_cards(self.kaylin)[0]["next_set"]
        self.assertIsNotNone(first_next)
        # turn in the first set
        q = first_next.questions.first()
        data = {f"answer_{q.pk}": "done."} if q else {}
        self.client.post(self._url("portal_questions", set_pk=first_next.pk), data=data)
        second_next = _subject_cards(self.kaylin)[0]["next_set"]
        self.assertIsNotNone(second_next)
        self.assertNotEqual(second_next.pk, first_next.pk)       # skips the submitted one

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

    def test_typed_fields_offer_spelling_help_but_no_autocorrect(self):
        # It's not a spelling class — the browser flags misspellings (spellcheck),
        # but autocorrect stays off so nothing silently rewrites the child's words.
        resp = self.client.get(self._url("portal_questions", set_pk=self.first_set.pk))
        self.assertContains(resp, 'spellcheck="true"')
        self.assertNotContains(resp, 'spellcheck="false"')
        self.assertContains(resp, 'autocorrect="off"')
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
        q = self.first_text_q
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
        q = self.first_text_q
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
        q = self.first_text_q
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


class SpellcheckAndWordHelpTests(TestCase):
    """Red-squiggle spellcheck + 'better words' helper on writing curricula,
    both switched OFF on spelling curricula."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="wh", email="wh@e.com", password="pw")
        cls.family = Family.objects.create(name="WordHelp Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.writing_set = cls._make_set("Blackbird Writing", "Writing")
        cls.spelling_set = cls._make_set("Spelling Week 1", "Spelling")
        cls.token = make_portal_token(cls.violet)

    @classmethod
    def _make_set(cls, name, subject):
        cur = Curriculum.objects.create(
            parent=cls.parent, name=name, subject=subject, family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cur, number=1, title="Unit 1")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cur, current_lesson=lesson)
        qset = QuestionSet.objects.create(
            lesson=lesson, title=name, family=cls.family, status=QuestionSet.APPROVED,
        )
        Question.objects.create(
            question_set=qset, order=1, category="editing",
            response_type=Question.TYPE_TEXT, prompt="Write about it.",
        )
        return qset

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_writing_curriculum_enables_spellcheck_and_wordhelp(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.writing_set.pk))
        self.assertContains(resp, 'spellcheck="true"')
        self.assertContains(resp, "wordhelp-hint")
        self.assertContains(resp, "data-wordhelp-url")
        self.assertContains(resp, "data-spellcheck-url")

    def test_spelling_curriculum_disables_spellcheck_and_wordhelp(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.spelling_set.pk))
        self.assertContains(resp, 'spellcheck="false"')
        self.assertNotContains(resp, 'spellcheck="true"')
        self.assertNotContains(resp, "wordhelp-hint")
        self.assertNotContains(resp, "data-wordhelp-url")
        self.assertNotContains(resp, "data-spellcheck-url")

    @mock.patch("tutor.ai.check_spelling", return_value=[
        {"wrong": "speshel", "fixes": ["special"]},
        {"wrong": "becuse", "fixes": ["because"]},
    ])
    def test_spellcheck_endpoint_returns_misspellings(self, _chk):
        resp = self.client.post(
            self._url("portal_spellcheck", set_pk=self.writing_set.pk),
            data=json.dumps({"text": "He was little and speshel becuse of it."}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        wrongs = [m["wrong"] for m in data["misspelled"]]
        self.assertEqual(wrongs, ["speshel", "becuse"])

    @mock.patch("tutor.ai.check_spelling", return_value=[{"wrong": "cat", "fixes": ["cat"]}])
    def test_spellcheck_disabled_on_spelling_curricula(self, chk):
        resp = self.client.post(
            self._url("portal_spellcheck", set_pk=self.spelling_set.pk),
            data=json.dumps({"text": "kat"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["misspelled"], [])
        chk.assert_not_called()

    @mock.patch("portal.thesaurus.synonyms", return_value=["glad", "joyful", "cheerful"])
    def test_word_help_returns_suggestions(self, _syn):
        resp = self.client.post(
            self._url("portal_word_help", set_pk=self.writing_set.pk),
            data=json.dumps({"word": "happy"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["words"], ["glad", "joyful", "cheerful"])

    @mock.patch("portal.thesaurus.synonyms", return_value=["glad"])
    def test_word_help_is_disabled_on_spelling_curricula(self, syn):
        resp = self.client.post(
            self._url("portal_word_help", set_pk=self.spelling_set.pk),
            data=json.dumps({"word": "happy"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["words"], [])
        syn.assert_not_called()


class SocraticStandardTests(TestCase):
    """The reusable CenterForLit question ladder scales by the reader's level."""

    def test_questions_scale_by_level(self):
        from tutor import socratic

        g3 = socratic.questions_for("G03")
        g7 = socratic.questions_for("G07")
        self.assertGreater(len(g7), len(g3))  # older readers get more/deeper questions
        # every element is represented at the top band
        cats = {c for c, _t, _h in g7}
        for expected in ("context", "setting", "character", "conflict", "plot", "theme", "style"):
            self.assertIn(expected, cats)

    def test_band_mapping(self):
        from tutor import socratic

        self.assertEqual(socratic.band_for_level("G02"), 1)
        self.assertEqual(socratic.band_for_level("G05"), 2)
        self.assertEqual(socratic.band_for_level("G09"), 3)


class LiteratureStandardTests(TestCase):
    """The reusable framework ties any literature curriculum to Socratic + tools."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="lit", email="lit@e.com", password="pw")
        cls.family = Family.objects.create(name="Lit Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )

    def test_devices_scale_by_level(self):
        from tutor import literature

        self.assertLess(len(literature.devices_for("G03")), len(literature.devices_for("G07")))
        names_g3 = {d["name"] for d in literature.devices_for("G03")}
        self.assertIn("Onomatopoeia", names_g3)         # band-1 tool for a 3rd grader
        self.assertNotIn("Irony", names_g3)             # band-3 tool held back
        self.assertIn("Irony", {d["name"] for d in literature.devices_for("G07")})

    def test_command_scaffolds_and_applies(self):
        call_command(
            "seed_literature_standard", "--for-user", "lit", "--child-name", "Violet",
            "--name", "Blackbird Literature (Grade 3)", "--level", "G03", stdout=StringIO(),
        )
        curriculum = Curriculum.objects.get(name="Blackbird Literature (Grade 3)")
        self.assertEqual(curriculum.subject, "Literature")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        # exactly the two teacher-led standard sets, both discussion mode
        self.assertEqual(sets.count(), 2)
        self.assertTrue(all(s.mode == QuestionSet.MODE_DISCUSSION for s in sets))
        self.assertTrue(sets.filter(title__contains="Story-Grammar").exists())
        self.assertTrue(sets.filter(title__contains="Literary Toolbox").exists())
        # child is placed
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.child, curriculum=curriculum).exists()
        )

    def test_apply_is_idempotent(self):
        from tutor import literature

        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Some Novel", subject="Literature",
            grade_level="G05", family=self.family,
        )
        literature.apply_literature_standard(curriculum, "G05")
        literature.apply_literature_standard(curriculum, "G05")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        self.assertEqual(sets.count(), 2)  # no duplication on re-run

    def test_reapply_at_new_level_does_not_duplicate_toolbox(self):
        from tutor import literature

        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Aging Reader", subject="Literature", family=self.family,
        )
        literature.apply_literature_standard(curriculum, "G05")   # band 2
        literature.apply_literature_standard(curriculum, "G07")   # band 3 — a grade bump
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        toolboxes = sets.filter(title__startswith="Literary Toolbox")
        self.assertEqual(toolboxes.count(), 1)                    # exactly one, not two
        # and it now holds the higher-band tool set
        self.assertEqual(toolboxes.first().questions.count(), len(literature.devices_for("G07")))

    def test_scaffold_uses_childs_level_when_level_omitted(self):
        kaylin = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07", family=self.family,
        )
        call_command(
            "seed_literature_standard", "--for-user", "lit", "--child-name", "Kaylin",
            "--name", "Kaylin Lit", stdout=StringIO(),   # NO --level
        )
        from tutor import literature

        curriculum = Curriculum.objects.get(name="Kaylin Lit")
        self.assertEqual(curriculum.grade_level, "G07")           # inferred from Kaylin
        toolbox = QuestionSet.objects.get(
            lesson__chapter__curriculum=curriculum, title="Literary Toolbox",
        )
        self.assertEqual(toolbox.questions.count(), len(literature.devices_for("G07")))

    def test_toolbox_hidden_from_student_but_in_discussion_guide(self):
        from tutor import literature

        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Novel 2", subject="Literature",
            grade_level="G03", family=self.family,
        )
        anchor = literature.ensure_anchor_lesson(curriculum)
        CurriculumPlacement.objects.create(child=self.child, curriculum=curriculum, current_lesson=anchor)
        literature.apply_literature_standard(curriculum, "G03")
        # not in the student's portal
        token = make_portal_token(self.child)
        home = self.client.get(reverse("portal:portal_home", kwargs={"token": token}))
        self.assertNotContains(home, "Literary Toolbox")
        # but present in the parent discussion guide
        self.client.login(username="lit", password="pw")
        guide = self.client.get(reverse("tutor:discussion_guide", kwargs={"curriculum_pk": curriculum.pk}))
        self.assertContains(guide, "Literary Toolbox")
        self.assertContains(guide, "Onomatopoeia")


class CharacterQuestionTests(TestCase):
    """A 'characters' question renders one labeled box per character."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ch", email="ch@e.com", password="pw")
        cls.family = Family.objects.create(name="Char Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="I Am David", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="Chapters 1–2")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="Journal")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Section 1 · Journal", family=cls.family,
            status=QuestionSet.APPROVED, intro="Note who each character is.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="character",
            response_type=Question.TYPE_CHARACTERS, passage="David · The Man · Johannes",
            prompt="CHARACTERS — note who each person is.",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_character_names_parses(self):
        self.assertEqual(self.q.character_names, ["David", "The Man", "Johannes"])

    def test_renders_a_box_per_character(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.qset.pk))
        self.assertEqual(resp.status_code, 200)
        for name in ("David", "The Man", "Johannes"):
            self.assertContains(resp, name)
        self.assertContains(resp, "character-widget")
        self.assertEqual(resp.content.decode().count("character-box"), 3)   # one box each
        self.assertContains(resp, "portal-characters")                      # widget JS loaded
        self.assertNotContains(resp, f'id="q{self.q.pk}"')                  # NOT one shared textarea

    def test_autosave_then_submit_stores_per_character_map(self):
        answer = '{"David": "A brave, careful boy.", "Johannes": "David\'s wise friend."}'
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.qset.pk),
            data=json.dumps({"answers": {str(self.q.pk): answer}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.client.post(self._url("portal_questions", set_pk=self.qset.pk), data={f"answer_{self.q.pk}": answer})
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertTrue(sheet.is_submitted)
        self.assertEqual(sheet.answers[str(self.q.pk)], answer)
        text = sheet.as_worklog_text()
        self.assertIn("David: A brave, careful boy.", text)
        self.assertIn("Johannes: David's wise friend.", text)

    def test_worklog_text_handles_blank_and_garbage(self):
        sheet = ResponseSheet.objects.create(question_set=self.qset, child=self.violet, answers={str(self.q.pk): ""})
        self.assertIn("(no answer)", sheet.as_worklog_text())
        sheet.answers = {str(self.q.pk): "not json"}
        self.assertIn("(no answer)", sheet.as_worklog_text())   # never crashes


class VocabWidgetTests(TestCase):
    """Workbook-style vocabulary: match-the-number + fill-in-the-blank."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="vw", email="vw@e.com", password="pw")
        cls.family = Family.objects.create(name="Vocab Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Vocab Course", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="Acquire")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Vocabulary", family=cls.family,
            status=QuestionSet.APPROVED,
        )
        cls.match_q = Question.objects.create(
            question_set=cls.qset, order=1, category="vocabulary",
            response_type=Question.TYPE_MATCHING,
            prompt="Write in the number of the correct definition for each word.",
            passage=json.dumps({
                "words": ["gleam", "edible"],
                "definitions": [
                    {"n": 1, "text": "able to be eaten", "word": "edible"},
                    {"n": 2, "text": "to shine", "word": "gleam"},
                ],
            }),
        )
        cls.blank_q = Question.objects.create(
            question_set=cls.qset, order=2, category="vocabulary",
            response_type=Question.TYPE_FILL_BLANK,
            prompt="Fill in each blank with the best word.",
            passage=json.dumps({
                "words": ["gleam", "edible"],
                "sentences": [
                    {"text": "Polish it until you make it ______.", "word": "gleam"},
                    {"text": "Not everything ______ tastes good.", "word": "edible"},
                ],
            }),
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_renders_matching_and_fill_blank_widgets(self):
        html = self.client.get(self._url("portal_questions", set_pk=self.qset.pk)).content.decode()
        self.assertIn("vocab-matching", html)
        self.assertIn("vocab-fillblank", html)
        for token in ("gleam", "edible", "able to be eaten", "to shine"):
            self.assertIn(token, html)
        self.assertEqual(html.count('class="vocab-word"'), 2)   # a button per word
        self.assertEqual(html.count('class="vocab-def"'), 2)    # a button per definition
        self.assertIn("vocab-blank-select", html)
        self.assertIn("portal-vocab", html)          # widget JS loaded
        # No free-text box for either question — the widgets replace the textarea.
        self.assertNotIn(f'id="q{self.match_q.pk}"', html)
        self.assertNotIn(f'id="q{self.blank_q.pk}"', html)

    def test_autosave_and_submit_store_json_and_render_worklog(self):
        match_answer = json.dumps({"matches": {"gleam": 2, "edible": 1}, "tries": 1})
        blank_answer = json.dumps({"blanks": {"0": "gleam", "1": "edible"}, "tries": 0})
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.qset.pk),
            data=json.dumps({"answers": {
                str(self.match_q.pk): match_answer,
                str(self.blank_q.pk): blank_answer,
            }}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.client.post(self._url("portal_questions", set_pk=self.qset.pk), data={
            f"answer_{self.match_q.pk}": match_answer,
            f"answer_{self.blank_q.pk}": blank_answer,
        })
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertTrue(sheet.is_submitted)
        text = sheet.as_worklog_text()
        self.assertIn("gleam → 2 (to shine) ✓", text)
        self.assertIn("edible → 1 (able to be eaten) ✓", text)
        self.assertIn("(1 wrong try along the way)", text)
        self.assertIn("[gleam]", text)                # sentence rendered with the word
        self.assertIn("Polish it until you make it", text)

    def test_worklog_text_survives_blank_and_garbage(self):
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.violet,
            answers={str(self.match_q.pk): "", str(self.blank_q.pk): "not json"},
        )
        text = sheet.as_worklog_text()
        self.assertEqual(text.count("(no answer)"), 2)   # never crashes

    def test_vocab_data_survives_garbage_passage(self):
        self.match_q.passage = "{broken json"
        self.assertEqual(self.match_q.vocab_data, {})          # malformed JSON → {}
        # And the fill-blank helper pre-splits sentences at the blank.
        first = self.blank_q.fill_blank_sentences[0]
        self.assertEqual(first["word"], "gleam")
        self.assertEqual(first["before"], "Polish it until you make it ")
        self.assertEqual(first["after"], ".")


class ClozeWidgetTests(TestCase):
    """EIW-style fill-in-the-blanks: inline inputs at each blank (own words)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="cz", email="cz@e.com", password="pw")
        cls.family = Family.objects.create(name="Cloze Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="EIW Test", subject="Writing", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Fill in the blanks", family=cls.family,
            status=QuestionSet.APPROVED, intro="Add subjects where they are missing.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="grammar",
            response_type=Question.TYPE_CLOZE,
            passage="____________ liked to ride his bike. One day, ____________ met a girl.",
            prompt="",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_segments_and_blank_count(self):
        self.assertEqual(self.q.cloze_blank_count, 2)
        segs = self.q.cloze_segments
        self.assertEqual(segs[0]["blank"], 0)                     # starts with a blank
        self.assertIn("liked to ride his bike", segs[1]["text"])
        self.assertEqual(segs[2]["blank"], 1)

    def test_renders_inline_inputs_not_underscores(self):
        html = self.client.get(self._url("portal_questions", set_pk=self.qset.pk)).content.decode()
        self.assertIn("cloze-input", html)
        self.assertEqual(html.count('class="cloze-input"'), 2)   # one input per blank
        self.assertNotIn("____", html)                           # no underscore walls
        self.assertIn("liked to ride his bike", html)

    def test_submit_renders_words_into_worklog(self):
        answer = json.dumps({"blanks": {"0": "Marcus", "1": "he"}})
        self.client.post(self._url("portal_questions", set_pk=self.qset.pk),
                         data={f"answer_{self.q.pk}": answer})
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        text = sheet.as_worklog_text()
        self.assertIn("[Marcus] liked to ride his bike", text)
        self.assertIn("[he] met a girl", text)

    def test_blank_answer_and_garbage_degrade(self):
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.violet, answers={str(self.q.pk): "junk"},
        )
        self.assertIn("(no answer)", sheet.as_worklog_text())

    def test_eiw_seed_converts_fill_blank_to_cloze(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_eiw_violet", "--for-user", "cz", stdout=StringIO())
        cloze = Question.objects.filter(response_type=Question.TYPE_CLOZE)
        self.assertGreater(cloze.count(), 10)                    # the workbook's blanks
        self.assertTrue(all("___" in c.passage for c in cloze.exclude(pk=self.q.pk)))


class FeedbackAgentTests(TestCase):
    """HH-97: submit → kid feedback page → parent 'feedback to review' card."""

    GRADE_RESULT = {
        "level": "proficient",
        "summary": "Solid comprehension against the rubric.",
        "criteria": [{"criterion": "Complete sentences", "met": True, "comment": "Yes"}],
        "encouragement": "Violet, your answer about Wolf's bravery was wonderful!",
        "kid_highlights": ["You used complete sentences.", "Next time, add one more detail."],
        "parent_pointers": ["Ask Violet to point to the part that shows bravery.",
                            "Reinforce with a re-read of that page together."],
    }

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="fb", email="fb@e.com", password="pw")
        cls.family = Family.objects.create(name="FB Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="FB Course", subject="Literature",
            grade_level="G03", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Comprehension", family=cls.family,
            status=QuestionSet.APPROVED, rubric="Answer in complete sentences.",
            answer_key="1. Wolf is brave.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="comprehension", prompt="Why is Wolf brave?",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def _submit(self):
        return self.client.post(
            self._url("portal_questions", set_pk=self.qset.pk),
            data={f"answer_{self.q.pk}": "Wolf sings for help even though he is small."},
        )

    def test_submit_redirects_to_feedback_page(self):
        resp = self._submit()
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/feedback/", resp["Location"])
        page = self.client.get(resp["Location"])
        self.assertContains(page, "Turned in!")
        self.assertContains(page, "What's next?")

    def test_feedback_page_before_submit_redirects_back(self):
        resp = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn("/feedback/", resp["Location"])

    def test_generate_creates_one_draft_and_returns_kid_fields_only(self):
        from unittest.mock import patch
        from tutor.models import MasteryAssessment

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)) as mocked:
            r1 = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
            r2 = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        data = r1.json()
        self.assertTrue(data["ok"])
        self.assertIn("bravery", data["encouragement"])
        self.assertEqual(len(data["highlights"]), 2)
        self.assertNotIn("level", data)                       # the child never sees a level
        self.assertNotIn("proficient", str(data))
        self.assertTrue(r2.json()["ok"])                      # idempotent
        self.assertEqual(mocked.call_count, 1)                # graded exactly once
        a = MasteryAssessment.objects.get()
        self.assertEqual(a.status, MasteryAssessment.DRAFT)
        self.assertIsNone(a.graded_by)                        # agent-drafted
        self.assertTrue(a.is_auto)
        self.assertEqual(a.ai_level, "proficient")
        self.assertIn("Reference answers", a.rubric)          # answer key folded in
        self.assertEqual(a.ai_parent_pointers, self.GRADE_RESULT["parent_pointers"])  # stored for the parent
        self.assertNotIn("point to the part", str(data))      # parent pointers never leak to the child

    def test_unconfigured_and_error_fall_back_without_assessment(self):
        from unittest.mock import patch
        from tutor import ai
        from tutor.models import MasteryAssessment

        self._submit()
        r = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        self.assertFalse(r.json()["ok"])                      # no key configured in tests
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", side_effect=ai.GraderError("boom")):
            r = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        self.assertFalse(r.json()["ok"])
        self.assertEqual(MasteryAssessment.objects.count(), 0)
        # and the page itself still celebrates
        page = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertContains(page, "Turned in!")
        self.assertContains(page, "look at it soon")

    def test_feedback_page_renders_existing_assessment_without_level(self):
        from unittest.mock import patch

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        page = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertContains(page, "A note about your work")
        self.assertContains(page, "bravery")
        self.assertContains(page, "complete sentences.")
        self.assertNotContains(page, "Proficient")            # no levels for the child
        self.assertNotContains(page, "proficient")

    def test_feedback_page_holds_until_ai_is_ready(self):
        # Track C: while grading is pending, show a "reading your work" hold state
        # and keep the feedback + "what's next" gated (hidden) until JS reveals them.
        from unittest.mock import patch

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True):
            page = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertContains(page, "reading your work")           # the hold state
        self.assertContains(page, 'id="portal-hold"')
        self.assertContains(page, 'id="portal-reveal" hidden')    # reveal gated until ready

    def test_sibling_token_cannot_reach_feedback(self):
        self._submit()
        sibling = make_portal_token(self.kaylin)
        for name in ("portal_feedback", "portal_feedback_generate"):
            url = reverse(f"portal:{name}", kwargs={"token": sibling, "set_pk": self.qset.pk})
            resp = self.client.post(url) if "generate" in name else self.client.get(url)
            self.assertEqual(resp.status_code, 404)

    def test_parent_hub_shows_feedback_to_review_until_finalized(self):
        from unittest.mock import patch
        from tutor.models import MasteryAssessment

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        self.client.login(username="fb", password="pw")
        home = self.client.get(reverse("home"))
        self.assertContains(home, "Feedback to review")
        self.assertContains(home, "Violet")
        a = MasteryAssessment.objects.get()
        detail = self.client.get(reverse("tutor:assess_detail", kwargs={"pk": a.pk}))
        self.assertContains(detail, "What Violet was told at turn-in")
        self.assertContains(detail, "bravery")
        # finalize → the hub card clears
        self.client.post(reverse("tutor:assess_finalize", kwargs={"pk": a.pk}),
                         data={"final_level": "proficient"})
        home = self.client.get(reverse("home"))
        self.assertNotContains(home, "Feedback to review")


class WritingCoachTests(TestCase):
    """HH-98: draft feedback on rough drafts — formative, never a grade."""

    COACH_RESULT = {
        "praise": "Your first sentence really hooks the reader!",
        "suggestions": ["Add one detail about how Wolf feels.", "Read it out loud to catch the missing word."],
    }

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="wc", email="wc@e.com", password="pw")
        cls.family = Family.objects.create(name="WC Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="WC Course", subject="Literature",
            grade_level="G03", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Writing", family=cls.family,
            status=QuestionSet.APPROVED,
        )
        cls.draft_q = Question.objects.create(
            question_set=cls.qset, order=1, category="application",
            prompt="ROUGH DRAFT — Write a paragraph about Wolfgang Amadeus Mouse.",
        )
        cls.comp_q = Question.objects.create(
            question_set=cls.qset, order=2, category="comprehension",
            prompt="Why is Wolf brave?",
        )
        cls.token = make_portal_token(cls.violet)

    def _coach(self, qid, text, token=None):
        url = reverse("portal:portal_draft_feedback", kwargs={
            "token": token or self.token, "set_pk": self.qset.pk,
        })
        return self.client.post(url, data=json.dumps({"question": str(qid), "text": text}),
                                content_type="application/json")

    def test_supports_draft_coach_gating(self):
        self.assertTrue(self.draft_q.supports_draft_coach)     # ROUGH DRAFT marker
        self.assertFalse(self.comp_q.supports_draft_coach)     # comprehension: no coach
        eiw_q = Question.objects.create(
            question_set=self.qset, order=3, category="writing", prompt="Write a paragraph.",
        )
        self.assertTrue(eiw_q.supports_draft_coach)            # EIW writing category

    def test_coach_stores_feedback_and_draft(self):
        from unittest.mock import patch

        draft = "Wolf is a very small mouse but he has a very big dream about singing."
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.review_draft", return_value=dict(self.COACH_RESULT)) as mocked:
            resp = self._coach(self.draft_q.pk, draft)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertIn("hooks", data["praise"])
        self.assertEqual(len(data["suggestions"]), 2)
        self.assertEqual(mocked.call_count, 1)
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertEqual(sheet.answers[str(self.draft_q.pk)], draft)   # draft saved too
        self.assertIn(str(self.draft_q.pk), sheet.draft_feedback)
        # and it renders back on reload
        page = self.client.get(reverse("portal:portal_questions", kwargs={
            "token": self.token, "set_pk": self.qset.pk,
        }))
        self.assertContains(page, "Your writing coach says")
        self.assertContains(page, "hooks the reader")
        self.assertContains(page, "Get feedback on my draft")

    def test_coach_rejects_non_draft_question_and_short_text(self):
        from unittest.mock import patch

        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.review_draft", return_value=dict(self.COACH_RESULT)):
            self.assertEqual(self._coach(self.comp_q.pk, "x" * 50).status_code, 400)
            self.assertEqual(self._coach(self.draft_q.pk, "too short").json()["error"], "too_short")

    def test_coach_blocked_after_submit_and_for_siblings(self):
        from unittest.mock import patch

        kaylin = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07", family=self.family,
        )
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.review_draft", return_value=dict(self.COACH_RESULT)):
            resp = self._coach(self.draft_q.pk, "x" * 40, token=make_portal_token(kaylin))
            self.assertEqual(resp.status_code, 404)            # not her course
            self.client.post(reverse("portal:portal_questions", kwargs={
                "token": self.token, "set_pk": self.qset.pk,
            }), data={f"answer_{self.draft_q.pk}": "final text here"})
            resp = self._coach(self.draft_q.pk, "x" * 40)
            self.assertEqual(resp.status_code, 409)            # already turned in

    def test_coach_unconfigured_degrades(self):
        resp = self._coach(self.draft_q.pk, "x" * 40)
        self.assertFalse(resp.json()["ok"])                    # no key in tests → soft fail
        self.assertFalse(ResponseSheet.objects.filter(draft_feedback__isnull=False,
                                                      question_set=self.qset).exclude(draft_feedback={}).exists())


class GradingHistoryTests(TestCase):
    """HH-98: the family's grading history — drafts first, then the record."""

    @classmethod
    def setUpTestData(cls):
        from tutor.models import MasteryAssessment

        cls.parent = User.objects.create_user(username="gh", email="gh@e.com", password="pw")
        cls.family = Family.objects.create(name="GH Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )
        e1 = WorkLogEntry.objects.create(parent=cls.parent, family=cls.family,
                                         child=cls.violet, subject="Literature")
        e2 = WorkLogEntry.objects.create(parent=cls.parent, family=cls.family,
                                         child=cls.kaylin, subject="Writing")
        cls.draft = MasteryAssessment.objects.create(
            work_entry=e1, rubric="r", answers="a", ai_level="proficient",
        )
        cls.final = MasteryAssessment.objects.create(
            work_entry=e2, rubric="r", answers="a", ai_level="mastered",
            final_level="mastered", status=MasteryAssessment.FINALIZED,
        )
        # another family's assessment must never appear
        other = User.objects.create_user(username="gh2", email="gh2@e.com", password="pw")
        fam2 = Family.objects.create(name="Other GH")
        FamilyMembership.objects.create(user=other, family=fam2, role="parent")
        kid2 = Student.objects.create(parent=other, first_name="Eve", grade_level="G01", family=fam2)
        e3 = WorkLogEntry.objects.create(parent=other, family=fam2, child=kid2, subject="SecretSubj")
        MasteryAssessment.objects.create(work_entry=e3, rubric="r", answers="a", ai_level="beginning")

    def test_history_lists_drafts_then_finalized_scoped_to_family(self):
        self.client.login(username="gh", password="pw")
        resp = self.client.get(reverse("tutor:assessment_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([a.pk for a in resp.context["drafts"]], [self.draft.pk])
        self.assertEqual([a.pk for a in resp.context["finalized"]], [self.final.pk])
        self.assertContains(resp, "Awaiting your review")
        self.assertContains(resp, "Agent draft")
        self.assertNotContains(resp, "SecretSubj")
        self.assertNotIn("Eve", [c.first_name for c in resp.context["children"]])

    def test_child_filter(self):
        self.client.login(username="gh", password="pw")
        resp = self.client.get(reverse("tutor:assessment_list"), {"child_id": self.kaylin.id})
        self.assertEqual(resp.context["drafts"], [])
        self.assertEqual([a.pk for a in resp.context["finalized"]], [self.final.pk])

    def test_requires_login(self):
        resp = self.client.get(reverse("tutor:assessment_list"))
        self.assertEqual(resp.status_code, 302)

    def test_progress_page_links_to_history(self):
        self.client.login(username="gh", password="pw")
        resp = self.client.get(reverse("dashboard:dashboard"))
        self.assertContains(resp, reverse("tutor:assessment_list"))   # the grading-history link


class OnlineCurriculumTests(TestCase):
    """A core subject done on an external site launches out of the portal."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="oc", email="oc@e.com", password="pw")
        cls.family = Family.objects.create(name="OC Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.online = Curriculum.objects.create(
            parent=cls.parent, name="Beast Academy", subject="Math", grade_level="G03",
            family=cls.family, is_online=True, website_url="https://beastacademy.com/",
        )
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.online)
        cls.token = make_portal_token(cls.violet)

    def test_is_external_needs_flag_and_url(self):
        self.assertTrue(self.online.is_external)
        self.online.website_url = ""
        self.assertFalse(self.online.is_external)     # flag alone isn't enough

    def test_home_card_launches_out(self):
        from portal.views import _subject_cards
        card = _subject_cards(self.violet)[0]
        self.assertTrue(card["is_external"])
        self.assertEqual(card["launch_url"], "https://beastacademy.com/")
        html = self.client.get(reverse("portal:portal_home", kwargs={"token": self.token})).content.decode()
        self.assertIn("Beast Academy", html)
        self.assertIn('href="https://beastacademy.com/"', html)
        self.assertIn('rel="noopener noreferrer"', html)
        self.assertIn("opens your lessons ↗", html)
        # NOT an in-app drill-in link for this subject
        self.assertNotIn(f"/subject/{self.online.pk}/", html)

    def test_drilldown_shows_launch_button(self):
        resp = self.client.get(reverse("portal:portal_subject", kwargs={
            "token": self.token, "curriculum_id": self.online.pk,
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Open Beast Academy ↗")
        self.assertContains(resp, "this subject online")

    def test_form_exposes_is_online(self):
        from curricula.forms import CurriculumForm
        self.assertIn("is_online", CurriculumForm().fields)


class PortalMarkdownRenderTests(TestCase):
    """Prompts/intros render Markdown (bold, lists) instead of showing raw **."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="mdp", email="mdp@e.com", password="pw")
        cls.family = Family.objects.create(name="MD Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="MD Course", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Vocab", family=cls.family,
            status=QuestionSet.APPROVED, intro="Do **all** of these:",
        )
        Question.objects.create(question_set=cls.qset, order=1, category="vocabulary",
                                prompt="Define: **scamper**")
        cls.token = make_portal_token(cls.violet)

    def test_bold_prompt_renders_strong_not_asterisks(self):
        url = reverse("portal:portal_questions", kwargs={"token": self.token, "set_pk": self.qset.pk})
        html = self.client.get(url).content.decode()
        self.assertIn("<strong>scamper</strong>", html)   # bold, not raw
        self.assertNotIn("**scamper**", html)             # no literal asterisks
        self.assertIn("<strong>all</strong>", html)       # intro bold too


class AMouseCalledWolfSeedTests(TestCase):
    """Violet's Blackbird 'A Mouse Called Wolf' course (original, book-grounded)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="mw", email="mw@e.com", password="pw")
        cls.family = Family.objects.create(name="MW Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        call_command("seed_a_mouse_called_wolf", "--for-user", "mw", stdout=StringIO())
        cls.curriculum = Curriculum.objects.get(name__contains="Mouse Called Wolf")

    def test_course_shape_and_teacher_answer_keys(self):
        self.assertEqual(self.curriculum.grade_level, "G03")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=self.curriculum)
        # 6 sets/section x 4 sections + Glean + Story-Grammar + Toolbox = 27
        self.assertEqual(sets.count(), 27)
        # every Comprehension set carries a teacher answer key (never shown to students)
        comp = sets.filter(title__contains="Comprehension")
        self.assertEqual(comp.count(), 4)
        self.assertTrue(all(c.answer_key.strip() for c in comp))
        self.assertTrue(comp.filter(answer_key__contains="teacher reference only").exists())

    def test_answer_key_resource_seeded_teacher_only(self):
        r = CurriculumResource.objects.get(
            curriculum=self.curriculum, resource_type=CurriculumResource.ANSWER_KEY,
        )
        self.assertTrue(r.teacher_only)             # never shown to the student
        self.assertIn("blackbirdandcompany.com", r.url)

    def test_journal_uses_per_character_boxes(self):
        journal = QuestionSet.objects.get(
            lesson__chapter__curriculum=self.curriculum, title="Section 1 · Journal",
        )
        q = journal.questions.get(order=1)
        self.assertEqual(q.response_type, Question.TYPE_CHARACTERS)
        # The guide's own character list for Section 1.
        self.assertIn("Wolfgang Amadeus Mouse", q.character_names)
        self.assertEqual(len(q.character_names), 2)

    def test_vocabulary_is_workbook_matching_plus_fill_blank(self):
        vocab = QuestionSet.objects.get(
            lesson__chapter__curriculum=self.curriculum, title="Section 1 · Vocabulary",
        )
        qs = list(vocab.questions.order_by("order"))
        self.assertEqual([q.response_type for q in qs],
                         [Question.TYPE_MATCHING, Question.TYPE_FILL_BLANK])
        matching = qs[0].vocab_data
        # The guide's real Section 1 words, with its fixed answer numbering.
        self.assertEqual(matching["words"],
                         ["ordinary", "venture", "gleam", "edible", "dwindle", "curiosity"])
        by_word = {d["word"]: d["n"] for d in matching["definitions"]}
        self.assertEqual(by_word["ordinary"], 3)
        self.assertEqual(by_word["curiosity"], 1)
        # Fill-blank: 6 sentences, one blank each, answers drawn from the same words.
        sentences = qs[1].vocab_data["sentences"]
        self.assertEqual(len(sentences), 6)
        self.assertTrue(all("______" in s["text"] for s in sentences))
        self.assertTrue(all(s["word"] in matching["words"] for s in sentences))
        # Teacher key on the set covers both halves.
        self.assertIn("Matching:", vocab.answer_key)
        self.assertIn("Fill in the blank:", vocab.answer_key)

    def test_section4_is_chapters_10_to_11(self):
        # The guide's Section 4 covers chapters 10–11 (the book has 11 chapters).
        from curricula.models import Chapter as Ch
        title = Ch.objects.get(curriculum=self.curriculum, number=4).title
        self.assertIn("10–11", title)

    def test_violet_placed_and_discussion_hidden_from_student(self):
        from portal.views import _visible_question_sets

        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.violet, curriculum=self.curriculum).exists()
        )
        titles = set(_visible_question_sets(self.violet).values_list("title", flat=True))
        self.assertIn("Section 1 · Comprehension", titles)     # student work is visible
        self.assertNotIn("Section 1 · Discussion", titles)     # teacher-led stays hidden
        self.assertNotIn("Section 1 · Socratic Seminar", titles)

    def test_idempotent(self):
        before = QuestionSet.objects.filter(lesson__chapter__curriculum=self.curriculum).count()
        call_command("seed_a_mouse_called_wolf", "--for-user", "mw", stdout=StringIO())
        after = QuestionSet.objects.filter(lesson__chapter__curriculum=self.curriculum).count()
        self.assertEqual(before, after)


class BackgroundGradingTests(TestCase):
    """HH: submit-time grading runs off the request path; the page polls for it."""

    GRADE_RESULT = {
        "level": "proficient",
        "summary": "Solid comprehension against the rubric.",
        "criteria": [{"criterion": "Complete sentences", "met": True, "comment": "Yes"}],
        "encouragement": "Rae, your answer about Wolf's bravery was wonderful!",
        "kid_highlights": ["You used complete sentences.", "Add one more detail next time."],
        "parent_pointers": ["Ask Rae to point to the part that shows bravery."],
    }

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="bg", email="bg@e.com", password="pw")
        cls.family = Family.objects.create(name="BG Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Rae", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="BG Course", subject="Literature",
            grade_level="G03", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.child, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Comprehension", family=cls.family,
            status=QuestionSet.APPROVED, rubric="Answer in complete sentences.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="comprehension", prompt="Why is Wolf brave?",
        )
        cls.token = make_portal_token(cls.child)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def _submit(self):
        return self.client.post(
            self._url("portal_questions", set_pk=self.qset.pk),
            data={f"answer_{self.q.pk}": "Wolf sings for help even though he is small."},
        )

    def test_status_reports_not_ready_then_ready(self):
        self._submit()
        body = self.client.get(self._url("portal_feedback_status", set_pk=self.qset.pk)).json()
        self.assertFalse(body["ready"])
        self.assertFalse(body["grading"])        # no key configured in tests → nothing to wait for
        # Grade it (inline via the synchronous fallback with a mocked grader).
        with mock.patch("tutor.ai.is_configured", return_value=True), \
             mock.patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        body = self.client.get(self._url("portal_feedback_status", set_pk=self.qset.pk)).json()
        self.assertTrue(body["ready"])
        self.assertIn("bravery", body["encouragement"])
        self.assertEqual(len(body["highlights"]), 2)
        self.assertNotIn("level", body)          # the child never sees a level

    @override_settings(GRADE_IN_BACKGROUND=False)
    def test_start_grades_and_is_idempotent(self):
        from tutor.models import MasteryAssessment

        self._submit()
        with mock.patch("tutor.ai.is_configured", return_value=True), \
             mock.patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)) as mocked:
            r1 = self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk))
            self.assertTrue(r1.json()["grading"])            # grade kicked off
            self.assertEqual(MasteryAssessment.objects.count(), 1)   # ran inline (background off)
            r2 = self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk))
            self.assertTrue(r2.json()["ready"])              # already graded → ready, no re-grade
        self.assertEqual(mocked.call_count, 1)               # graded exactly once

    def test_start_reports_grader_off_when_unconfigured(self):
        from tutor.models import MasteryAssessment

        self._submit()
        body = self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk)).json()
        self.assertFalse(body["grading"])                    # no key in tests
        self.assertEqual(MasteryAssessment.objects.count(), 0)

    @override_settings(GRADE_IN_BACKGROUND=False)
    def test_grading_is_deferred_to_the_feedback_page(self):
        # Grading is triggered once, by the feedback page's start endpoint — not
        # at submit time — so a submission is never graded twice.
        from tutor.models import MasteryAssessment

        with mock.patch("tutor.ai.is_configured", return_value=True), \
             mock.patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self._submit()
            self.assertEqual(MasteryAssessment.objects.count(), 0)   # submit alone doesn't grade
            self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk))
            self.assertEqual(MasteryAssessment.objects.count(), 1)   # the feedback page grades it

    def test_status_scoped_to_own_token(self):
        self._submit()
        stranger = Student.objects.create(
            parent=self.parent, first_name="Nope", grade_level="G03", family=self.family,
        )
        url = reverse("portal:portal_feedback_status",
                      kwargs={"token": make_portal_token(stranger), "set_pk": self.qset.pk})
        # A different child's token can't even see this question set (not placed in it).
        self.assertEqual(self.client.get(url).status_code, 404)


class ParentGateTests(TestCase):
    """Portal → parent dashboard: a password-only re-auth that lands on the dashboard."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="pg", email="pg@e.com", password="s3cret", first_name="Dana",
        )
        cls.family = Family.objects.create(name="Gate Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Rae", grade_level="G03", family=cls.family,
        )
        cls.token = make_portal_token(cls.child)

    def setUp(self):
        cache.clear()  # the brute-force lockout counter lives in the process cache

    def _gate_url(self):
        return reverse("portal:portal_parent_gate", kwargs={"token": self.token})

    def test_gate_prompts_for_password_not_the_login_page(self):
        resp = self.client.get(self._gate_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Parent access")
        self.assertContains(resp, "Dana")            # greets the known parent from the token
        self.assertContains(resp, "password")

    def test_correct_password_signs_in_and_lands_on_dashboard(self):
        resp = self.client.post(self._gate_url(), data={"password": "s3cret"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("dashboard:dashboard"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.parent.pk)

    def test_wrong_password_shows_error_and_stays_signed_out(self):
        resp = self.client.post(self._gate_url(), data={"password": "wrong"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Please try again")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_live_session_skips_the_gate(self):
        self.client.login(username="pg", password="s3cret")
        resp = self.client.get(self._gate_url())
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("dashboard:dashboard"))

    def test_repeated_wrong_passwords_lock_out_brute_force(self):
        for _ in range(8):
            self.client.post(self._gate_url(), data={"password": "wrong"})
        # further attempts are refused — even the correct password, while locked.
        resp = self.client.post(self._gate_url(), data={"password": "wrong"})
        self.assertContains(resp, "Too many tries")
        resp = self.client.post(self._gate_url(), data={"password": "s3cret"})
        self.assertContains(resp, "Too many tries")
        self.assertNotIn("_auth_user_id", self.client.session)
