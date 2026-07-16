import json
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Family, FamilyMembership
from curricula.models import Curriculum, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from worklog.models import WorkLogEntry

from . import ai, grading, imagegen, mastery
from .models import Material, MasteryAssessment, Question, ResponseSheet

User = get_user_model()


def _fake_message(text):
    """Mimic an anthropic Message with a single text content block."""
    block = SimpleNamespace(type="text", text=text)
    return SimpleNamespace(content=[block])


class FakeAnthropic:
    """Stand-in for anthropic.Anthropic that returns a canned JSON response."""

    def __init__(self, text):
        self._text = text
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.last_kwargs = kwargs
        return _fake_message(self._text)


GOOD_JSON = (
    '{"level": "proficient", "summary": "Solid grasp of number bonds to 100.", '
    '"criteria": [{"criterion": "Bonds to 100", "met": true, "comment": "All correct."}], '
    '"encouragement": "Great work, Violet!"}'
)


class CheckSpellingTests(TestCase):
    """ai.check_spelling parsing — especially that it never echoes a word back
    as its own 'fix' (which produced a stuck 'bullied -> bullied' suggestion)."""

    def test_not_configured_returns_empty(self):
        self.assertFalse(ai.is_configured())
        self.assertEqual(ai.check_spelling("becuse"), [])

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_parses_misspellings(self):
        fake = FakeAnthropic('[{"wrong": "becuse", "fixes": ["because"]}]')
        out = ai.check_spelling("it happened becuse of rain", client=fake)
        self.assertEqual(out, [{"wrong": "becuse", "fixes": ["because"]}])

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_drops_noop_fix_equal_to_word(self):
        # A correctly-spelled word flagged with itself as the "fix" must vanish,
        # not render as "bullied -> bullied".
        fake = FakeAnthropic('[{"wrong": "bullied", "fixes": ["bullied"]}]')
        self.assertEqual(ai.check_spelling("he is bullied", client=fake), [])
        # Even case-different echoes ("Bullied") count as no-ops.
        fake2 = FakeAnthropic('[{"wrong": "bullied", "fixes": ["Bullied"]}]')
        self.assertEqual(ai.check_spelling("he is bullied", client=fake2), [])

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_keeps_real_fixes_drops_noop_and_case_dupes(self):
        fake = FakeAnthropic('[{"wrong": "wuz", "fixes": ["wuz", "was", "Was", "were"]}]')
        out = ai.check_spelling("it wuz fun", client=fake)
        self.assertEqual(out, [{"wrong": "wuz", "fixes": ["was", "were"]}])


class ParagraphModelTests(TestCase):
    """Paragraph question sections + how the answer formats for grading."""

    def test_defaults_and_flags(self):
        q = Question(response_type=Question.TYPE_PARAGRAPH)
        self.assertTrue(q.is_paragraph)
        self.assertTrue(q.supports_draft_coach)
        self.assertEqual(q.paragraph_sections, Question.DEFAULT_PARAGRAPH_SECTIONS)

    def test_custom_sections_from_passage(self):
        q = Question(response_type=Question.TYPE_PARAGRAPH, passage='{"sections": ["A", "B"]}')
        self.assertEqual(q.paragraph_sections, ["A", "B"])

    def test_bad_passage_falls_back_to_defaults(self):
        q = Question(response_type=Question.TYPE_PARAGRAPH, passage="not json")
        self.assertEqual(q.paragraph_sections, Question.DEFAULT_PARAGRAPH_SECTIONS)

    def test_format_grades_final_with_planning_notes(self):
        q = Question(response_type=Question.TYPE_PARAGRAPH)
        raw = json.dumps({
            "rough": ["Wolf is brave.", "He sings at night.", "He is a hero."],
            "final": "Wolf is a brave mouse who sings.",
        })
        out = ResponseSheet._format_paragraph(raw, q)
        self.assertIn("Final draft: Wolf is a brave mouse who sings.", out)
        self.assertIn("Introduction / Topic Sentence: Wolf is brave.", out)
        self.assertIn("planning notes (not graded)", out)

    def test_format_empty_answer(self):
        q = Question(response_type=Question.TYPE_PARAGRAPH)
        self.assertEqual(ResponseSheet._format_paragraph("", q), "(no answer)")
        self.assertEqual(ResponseSheet._format_paragraph("{}", q), "(no answer)")
        self.assertEqual(
            ResponseSheet._format_paragraph('{"rough": ["", ""], "final": ""}', q), "(no answer)"
        )

    def test_format_preserves_legacy_plaintext(self):
        # A text question converted to paragraph keeps a bare plain-text answer
        # readable instead of dropping it to "(no answer)".
        q = Question(response_type=Question.TYPE_PARAGRAPH)
        self.assertEqual(
            ResponseSheet._format_paragraph("Wolf is a brave little mouse.", q),
            "Wolf is a brave little mouse.",
        )


class MasteryScaleTests(TestCase):
    def test_meets_bar(self):
        self.assertTrue(mastery.meets_bar(mastery.PROFICIENT))
        self.assertTrue(mastery.meets_bar(mastery.MASTERED))
        self.assertFalse(mastery.meets_bar(mastery.DEVELOPING))
        self.assertFalse(mastery.meets_bar(""))


class AiServiceTests(TestCase):
    @override_settings(ANTHROPIC_API_KEY="")
    def test_not_configured_raises(self):
        self.assertFalse(ai.is_configured())
        with self.assertRaises(ai.GraderNotConfigured):
            ai.grade_work(rubric="r", answers="a", grade_level="3rd Grade", subject="Math")

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_grade_work_parses_result(self):
        fake = FakeAnthropic(GOOD_JSON)
        result = ai.grade_work(
            rubric="Bonds to 100", answers="98+2=100", grade_level="3rd Grade",
            subject="Math", client=fake,
        )
        self.assertEqual(result["level"], "proficient")
        self.assertEqual(result["criteria"][0]["criterion"], "Bonds to 100")

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_grade_work_parses_parent_pointers(self):
        with_pointers = (
            '{"level": "developing", "summary": "s", "criteria": [], '
            '"encouragement": "Nice try!", '
            '"parent_pointers": ["Ask her to draw the bar model.", "Reinforce with counters."]}'
        )
        result = ai.grade_work(
            rubric="r", answers="a", grade_level="3rd", subject="Math",
            client=FakeAnthropic(with_pointers),
        )
        self.assertEqual(
            result["parent_pointers"],
            ["Ask her to draw the bar model.", "Reinforce with counters."],
        )
        # A response without the field is backward-compatible → empty list.
        result2 = ai.grade_work(
            rubric="r", answers="a", grade_level="3rd", subject="Math",
            client=FakeAnthropic(GOOD_JSON),
        )
        self.assertEqual(result2["parent_pointers"], [])

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_grade_work_tolerates_markdown_fences(self):
        fake = FakeAnthropic("```json\n" + GOOD_JSON + "\n```")
        result = ai.grade_work(
            rubric="r", answers="a", grade_level="3rd Grade", subject="Math", client=fake,
        )
        self.assertEqual(result["level"], "proficient")

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_bad_json_raises_grader_error(self):
        fake = FakeAnthropic("not json at all")
        with self.assertRaises(ai.GraderError):
            ai.grade_work(rubric="r", answers="a", grade_level="3rd", subject="Math", client=fake)

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_unknown_level_raises(self):
        fake = FakeAnthropic('{"level": "A+", "summary": "", "criteria": [], "encouragement": ""}')
        with self.assertRaises(ai.GraderError):
            ai.grade_work(rubric="r", answers="a", grade_level="3rd", subject="Math", client=fake)


class AssessViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ap", email="ap@e.com", password="pw")
        cls.other = User.objects.create_user(username="ao", email="ao@e.com", password="pw")
        cls.teacher = User.objects.create_user(username="at", email="at@e.com", password="pw")
        cls.family = Family.objects.create(name="Assess Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.entry = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.child, subject="Math", family=cls.family,
            description="Ch2 L5 number bonds",
        )

    def _login(self, who="ap"):
        self.client.login(username=who, password="pw")

    @override_settings(ANTHROPIC_API_KEY="test-key", GRADE_IN_BACKGROUND=False)
    def test_create_assessment_success(self):
        # The manual grade now runs OFF the request path; GRADE_IN_BACKGROUND=False
        # runs it inline so the draft exists synchronously, then the pending page
        # forwards the parent to it.
        self._login()
        with patch("anthropic.Anthropic", return_value=FakeAnthropic(GOOD_JSON)):
            resp = self.client.post(
                reverse("tutor:assess_create", kwargs={"entry_pk": self.entry.pk}),
                data={"rubric": "Bonds to 100", "answers": "98+2=100"},
                follow=True,
            )
        assessment = MasteryAssessment.objects.get(work_entry=self.entry)
        self.assertEqual(assessment.ai_level, "proficient")
        self.assertEqual(assessment.status, MasteryAssessment.DRAFT)
        self.assertEqual(assessment.graded_by, self.parent)  # parent-initiated, not auto
        self.assertRedirects(resp, reverse("tutor:assess_detail", kwargs={"pk": assessment.pk}))

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_assess_create_backgrounds_without_blocking(self):
        # The POST must return immediately to the pending page and hand grading to
        # the background helper — never grade synchronously in-request (that H12'd).
        self._login()
        with patch("tutor.grading.start_manual_grade") as start:
            resp = self.client.post(
                reverse("tutor:assess_create", kwargs={"entry_pk": self.entry.pk}),
                data={"rubric": "r", "answers": "a"},
            )
        self.assertRedirects(
            resp, reverse("tutor:assess_pending", kwargs={"entry_pk": self.entry.pk}),
            fetch_redirect_response=False,
        )
        start.assert_called_once()
        self.assertEqual(start.call_args.args[0], self.entry.pk)

    @override_settings(ANTHROPIC_API_KEY="test-key", GRADE_IN_BACKGROUND=False,
                       GRADE_BACKGROUND_TIMEOUT=99)
    def test_manual_background_grade_uses_generous_timeout(self):
        # Off-request grades wait longer than the tight 24s in-request cap, so a
        # slow model doesn't silently drop the grade.
        with patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)) as gw:
            grading.start_manual_grade(
                self.entry.pk, rubric="r", answers="a", grade_level="3rd Grade",
                subject="Math", objectives="", graded_by_id=self.parent.pk,
            )
        gw.assert_called_once()
        self.assertEqual(gw.call_args.kwargs["timeout"], 99)
        self.assertTrue(MasteryAssessment.objects.filter(work_entry=self.entry).exists())

    def test_assess_pending_redirects_when_ready(self):
        self._login()
        a = MasteryAssessment.objects.create(
            work_entry=self.entry, graded_by=self.parent, rubric="r", answers="a",
            ai_level="proficient",
        )
        resp = self.client.get(reverse("tutor:assess_pending", kwargs={"entry_pk": self.entry.pk}))
        self.assertRedirects(resp, reverse("tutor:assess_detail", kwargs={"pk": a.pk}))

    def test_assess_pending_waits_when_not_ready(self):
        self._login()
        resp = self.client.get(reverse("tutor:assess_pending", kwargs={"entry_pk": self.entry.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Grading")

    def test_assess_status_reports_ready_with_url(self):
        self._login()
        a = MasteryAssessment.objects.create(
            work_entry=self.entry, graded_by=self.parent, rubric="r", answers="a",
            ai_level="proficient",
        )
        resp = self.client.get(reverse("tutor:assess_status", kwargs={"entry_pk": self.entry.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            "ready": True,
            "url": reverse("tutor:assess_detail", kwargs={"pk": a.pk}),
        })

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_assess_status_reports_not_ready(self):
        self._login()
        resp = self.client.get(reverse("tutor:assess_status", kwargs={"entry_pk": self.entry.pk}))
        self.assertEqual(resp.json(), {"ready": False, "grading": True})

    def test_assess_status_editor_gated(self):
        self._login("at")  # teacher is not an editor
        resp = self.client.get(reverse("tutor:assess_status", kwargs={"entry_pk": self.entry.pk}))
        self.assertEqual(resp.status_code, 404)

    @override_settings(ANTHROPIC_API_KEY="")
    def test_not_configured_shows_message_and_no_assessment(self):
        self._login()
        resp = self.client.post(
            reverse("tutor:assess_create", kwargs={"entry_pk": self.entry.pk}),
            data={"rubric": "r", "answers": "a"}, follow=True,
        )
        self.assertContains(resp, "ANTHROPIC_API_KEY")
        self.assertFalse(MasteryAssessment.objects.filter(work_entry=self.entry).exists())

    def test_teacher_cannot_assess(self):
        self._login("at")
        resp = self.client.get(reverse("tutor:assess_create", kwargs={"entry_pk": self.entry.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_cross_family_cannot_assess(self):
        self._login("ao")
        resp = self.client.get(reverse("tutor:assess_create", kwargs={"entry_pk": self.entry.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_finalize_with_override(self):
        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, graded_by=self.parent, rubric="r", answers="a",
            ai_level="developing", ai_summary="s",
        )
        self._login()
        resp = self.client.post(
            reverse("tutor:assess_finalize", kwargs={"pk": assessment.pk}),
            data={"final_level": "proficient"},
        )
        self.assertEqual(resp.status_code, 302)
        assessment.refresh_from_db()
        self.assertEqual(assessment.status, MasteryAssessment.FINALIZED)
        self.assertEqual(assessment.final_level, "proficient")
        self.assertEqual(assessment.parent_override_level, "proficient")
        self.assertTrue(assessment.meets_bar)

    def test_parent_pointers_card_renders_on_review(self):
        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, graded_by=self.parent, rubric="r", answers="a",
            ai_level="developing",
            ai_parent_pointers=["Ask Violet to explain which bar is bigger and why."],
        )
        self._login()
        resp = self.client.get(reverse("tutor:assess_detail", kwargs={"pk": assessment.pk}))
        self.assertContains(resp, "How to help")
        self.assertContains(resp, "Ask Violet to explain which bar is bigger and why.")

    def test_no_pointers_no_card(self):
        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, graded_by=self.parent, rubric="r", answers="a",
            ai_level="developing",  # ai_parent_pointers defaults to []
        )
        self._login()
        resp = self.client.get(reverse("tutor:assess_detail", kwargs={"pk": assessment.pk}))
        self.assertNotContains(resp, "How to help")

    def test_teacher_can_view_but_not_finalize(self):
        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, graded_by=self.parent, rubric="r", answers="a",
            ai_level="proficient",
        )
        self._login("at")
        # can view
        view = self.client.get(reverse("tutor:assess_detail", kwargs={"pk": assessment.pk}))
        self.assertEqual(view.status_code, 200)
        self.assertNotContains(view, "Finalize")
        # cannot finalize
        fin = self.client.post(
            reverse("tutor:assess_finalize", kwargs={"pk": assessment.pk}),
            data={"final_level": "mastered"},
        )
        self.assertEqual(fin.status_code, 404)


class MaterialTests(TestCase):
    """HH-84: manually-authored lesson materials (the comic) + seed command."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="mp", email="mp@e.com", password="pw")
        cls.other = User.objects.create_user(username="mo", email="mo@e.com", password="pw")
        cls.teacher = User.objects.create_user(username="mt", email="mt@e.com", password="pw")
        cls.family = Family.objects.create(name="Material Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family,
        )
        apply_blueprint(cls.curriculum, get_blueprint("dimensions_math_3a"))
        cls.lesson = Lesson.objects.get(
            chapter__curriculum=cls.curriculum, chapter__number=2, number=6,
        )

    def test_visible_to_student_requires_approval(self):
        m = Material(status=Material.DRAFT)
        self.assertFalse(m.visible_to_student)
        m.status = Material.APPROVED
        self.assertTrue(m.visible_to_student)

    def test_seed_command_creates_manga_idempotently(self):
        call_command("seed_violet_manga", "--curriculum", str(self.curriculum.pk), stdout=StringIO())
        call_command("seed_violet_manga", "--curriculum", str(self.curriculum.pk), stdout=StringIO())
        materials = Material.objects.filter(lesson=self.lesson, skill_type=Material.SKILL_MANGA)
        self.assertEqual(materials.count(), 1)
        m = materials.first()
        self.assertIn("Number Besties", m.title)
        self.assertIn("borrow", m.student_content.lower())
        self.assertEqual(m.child, self.child)  # linked by --child-name default "Violet"

    def test_seed_sets_child_intro_and_markdown_guide(self):
        call_command("seed_violet_manga", "--curriculum", str(self.curriculum.pk), stdout=StringIO())
        m = Material.objects.get(lesson=self.lesson, skill_type=Material.SKILL_MANGA)
        self.assertTrue(m.student_intro)                 # kid-facing explanation
        self.assertIn("secret", m.student_intro.lower())
        self.assertIn("## ", m.parent_content)           # teaching guide is Markdown

        self.client.login(username="mp", password="pw")
        resp = self.client.get(reverse("tutor:material_detail", kwargs={"pk": m.pk}))
        self.assertContains(resp, "What we're exploring")  # intro label
        self.assertContains(resp, "<h2")                    # guide Markdown -> HTML
        self.assertContains(resp, "The big idea")           # a guide heading

    def test_markdownify_filter_renders_html(self):
        from tutor.templatetags.tutor_extras import markdownify

        html = markdownify("## Title\n\nSome **bold** text.")
        self.assertIn("<h2", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertEqual(markdownify(""), "")

    def test_parent_can_view_material(self):
        m = Material.objects.create(
            lesson=self.lesson, title="Comic", student_content="hi", family=self.family,
        )
        self.client.login(username="mp", password="pw")
        resp = self.client.get(reverse("tutor:material_detail", kwargs={"pk": m.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "For the student")

    def test_cross_family_cannot_view_material(self):
        m = Material.objects.create(lesson=self.lesson, title="Comic", student_content="hi")
        self.client.login(username="mo", password="pw")
        resp = self.client.get(reverse("tutor:material_detail", kwargs={"pk": m.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_editor_can_approve(self):
        m = Material.objects.create(lesson=self.lesson, title="Comic", student_content="hi")
        self.client.login(username="mp", password="pw")
        resp = self.client.post(reverse("tutor:material_approve", kwargs={"pk": m.pk}))
        self.assertEqual(resp.status_code, 302)
        m.refresh_from_db()
        self.assertEqual(m.status, Material.APPROVED)
        self.assertIsNotNone(m.approved_at)

    def test_teacher_can_view_but_not_approve(self):
        m = Material.objects.create(lesson=self.lesson, title="Comic", student_content="hi")
        self.client.login(username="mt", password="pw")
        self.assertEqual(
            self.client.get(reverse("tutor:material_detail", kwargs={"pk": m.pk})).status_code, 200,
        )
        self.assertEqual(
            self.client.post(reverse("tutor:material_approve", kwargs={"pk": m.pk})).status_code, 404,
        )
        m.refresh_from_db()
        self.assertEqual(m.status, Material.DRAFT)


class MangaPanelTests(TestCase):
    """HH-91: illustrated manga panels, bubble rendering, and image-gen degrade."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="gp", email="gp@e.com", password="pw")
        cls.family = Family.objects.create(name="Manga Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family,
        )
        apply_blueprint(cls.curriculum, get_blueprint("dimensions_math_3a"))
        cls.lesson = Lesson.objects.get(
            chapter__curriculum=cls.curriculum, chapter__number=2, number=6,
        )
        cls.material = Material.objects.create(
            lesson=cls.lesson, title="Number Besties", skill_type=Material.SKILL_MANGA,
            student_content="script", family=cls.family, status=Material.APPROVED,
        )

    def _build(self):
        call_command(
            "generate_number_besties", "--material", str(self.material.pk), "--dry-run",
            stdout=StringIO(),
        )

    def test_dry_run_builds_panels_and_bubbles(self):
        self._build()
        self.assertTrue(self.material.has_pages)
        self.assertEqual(self.material.panels.count(), 8)
        panel = self.material.panels.get(order=2)
        self.assertFalse(panel.has_art)  # dry run leaves art unset
        self.assertIn("Two", [b["speaker"] for b in panel.bubbles])

    def test_dry_run_is_idempotent(self):
        self._build()
        self._build()
        self.assertEqual(self.material.panels.count(), 8)

    def test_detail_renders_manga_page(self):
        # Default layout is the reserved dialogue band: speech renders UNDER the art
        # (never as a floating overlay that could cover a character).
        self._build()
        self.client.login(username="gp", password="pw")
        resp = self.client.get(reverse("tutor:material_detail", kwargs={"pk": self.material.pk}))
        self.assertContains(resp, "manga-page")
        self.assertContains(resp, "manga-dialogue")
        self.assertContains(resp, "manga-line")
        self.assertContains(resp, "Then borrow me, partner")   # a dialogue line
        self.assertNotContains(resp, "manga-bubble")           # no floating overlay in band mode
        self.assertContains(resp, "manga-placeholder")          # art not generated yet

    def test_detail_renders_floating_balloons_when_selected(self):
        # Float layout overlays balloons on the art (only for art that reserves space).
        self._build()
        self.material.manga_text_layout = Material.LAYOUT_FLOAT
        self.material.save(update_fields=["manga_text_layout"])
        self.client.login(username="gp", password="pw")
        resp = self.client.get(reverse("tutor:material_detail", kwargs={"pk": self.material.pk}))
        self.assertContains(resp, "manga-bubble")
        self.assertContains(resp, "Then borrow me, partner")
        self.assertNotContains(resp, "manga-dialogue")

    def test_imagegen_degrades_without_token(self):
        with override_settings(REPLICATE_API_TOKEN=""):
            self.assertFalse(imagegen.is_configured())
            with self.assertRaises(imagegen.ImageGenNotConfigured):
                imagegen.generate_image("a prompt")

    def test_imagegen_uses_injected_client_and_reads_bytes(self):
        class FakeFileOutput:
            def read(self):
                return b"PNGDATA"

        class FakeClient:
            def run(self, model, input):
                return FakeFileOutput()

        with override_settings(REPLICATE_API_TOKEN="tok"):
            data = imagegen.generate_image("prompt", client=FakeClient())
        self.assertEqual(data, b"PNGDATA")


GRADE_DICT = {
    "level": "developing",
    "summary": "A good start.",
    "criteria": [],
    "encouragement": "Nice work, Rae!",
    "kid_highlights": ["You tried hard."],
    "parent_pointers": ["Re-read together."],
}


class SubmissionNotifyTests(TestCase):
    """Email the parent when a child's submission produces a draft assessment."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="np", email="np@e.com", password="pw")
        cls.family = Family.objects.create(name="Notify Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(parent=cls.parent, first_name="Rae", grade_level="G03", family=cls.family)

    def _make_sheet(self, family):
        from django.utils import timezone

        from curricula.models import Chapter
        from tutor.models import Question, QuestionSet, ResponseSheet

        cur = Curriculum.objects.create(parent=self.parent, name="Writing", subject="Writing", family=family, grade_level="G03")
        ch = Chapter.objects.create(curriculum=cur, number=1, title="U1")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        qset = QuestionSet.objects.create(lesson=lesson, title="Q", family=family, status=QuestionSet.APPROVED, rubric="Answer well.")
        q = Question.objects.create(question_set=qset, order=1, category="editing", prompt="Why?")
        entry = WorkLogEntry.objects.create(parent=self.parent, child=self.child, subject="Writing", family=family, date=timezone.localdate())
        return ResponseSheet.objects.create(
            question_set=qset, child=self.child, answers={str(q.pk): "Because."},
            status=ResponseSheet.SUBMITTED, work_entry=entry, submitted_at=timezone.now(),
        )

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_emails_parent_on_draft(self):
        from django.core import mail

        from tutor import grading

        sheet = self._make_sheet(self.family)
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)):
            _assessment, created = grading.auto_grade_sheet(sheet)
        self.assertTrue(created)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["np@e.com"])
        self.assertIn("Rae", mail.outbox[0].subject)

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_respects_opt_out(self):
        from django.core import mail

        from accounts.models import UserProfile
        from tutor import grading

        prof = UserProfile.get_for(self.parent)
        prof.notify_on_submission = False
        prof.save(update_fields=["notify_on_submission"])
        sheet = self._make_sheet(self.family)
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)):
            grading.auto_grade_sheet(sheet)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_mail_failure_never_breaks_grading(self):
        from tutor import grading

        sheet = self._make_sheet(self.family)
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)), \
             patch("core.notifications.send_mail", side_effect=RuntimeError("smtp down")):
            _assessment, created = grading.auto_grade_sheet(sheet)
        self.assertTrue(created)
        self.assertEqual(MasteryAssessment.objects.count(), 1)   # grading survived the mail failure

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_null_family_falls_back_to_child_parent(self):
        from django.core import mail

        from tutor import grading

        sheet = self._make_sheet(None)   # null-family work
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)):
            grading.auto_grade_sheet(sheet)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["np@e.com"])
