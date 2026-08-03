import json
import os
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse

from core.models import Family, FamilyMembership
from curricula.models import Curriculum, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from worklog.models import WorkLogEntry

from . import ai, grading, imagegen, mastery, spend
from .models import AiSpend, Material, MasteryAssessment, Question, ResponseSheet

User = get_user_model()


def _fake_message(text, usage=None):
    """Mimic an anthropic Message with a single text content block.

    ``usage`` defaults to absent, matching a response object whose token counts
    never arrived — the spend ledger has to survive that.
    """
    block = SimpleNamespace(type="text", text=text)
    return SimpleNamespace(content=[block], usage=usage)


def _fake_usage(input_tokens, output_tokens):
    return SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens)


class FakeAnthropic:
    """Stand-in for anthropic.Anthropic that returns a canned JSON response."""

    def __init__(self, text, usage=None):
        self._text = text
        self._usage = usage
        self.calls = 0
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.last_kwargs = kwargs
        self.calls += 1
        return _fake_message(self._text, self._usage)


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


class GradePendingTests(TestCase):
    """The grade_pending sweep — the backstop that grades submissions whose
    fire-and-forget background grade died (deploy/restart, worker recycle)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="gpd", email="gpd@e.com", password="pw")
        cls.family = Family.objects.create(name="Sweep Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Rae", grade_level="G03", family=cls.family,
        )

    def _submitted_sheet(self):
        from django.utils import timezone

        from curricula.models import Chapter
        from tutor.models import Question, QuestionSet, ResponseSheet

        cur = Curriculum.objects.create(
            parent=self.parent, name="Writing", subject="Writing", family=self.family, grade_level="G03",
        )
        ch = Chapter.objects.create(curriculum=cur, number=1, title="U1")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        qset = QuestionSet.objects.create(
            lesson=lesson, title="Q", family=self.family, status=QuestionSet.APPROVED, rubric="Answer well.",
        )
        q = Question.objects.create(question_set=qset, order=1, category="editing", prompt="Why?")
        entry = WorkLogEntry.objects.create(
            parent=self.parent, child=self.child, subject="Writing", family=self.family,
            date=timezone.localdate(),
        )
        return ResponseSheet.objects.create(
            question_set=qset, child=self.child, answers={str(q.pk): "Because."},
            status=ResponseSheet.SUBMITTED, work_entry=entry, submitted_at=timezone.now(),
        )

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_grades_ungraded_submission(self):
        sheet = self._submitted_sheet()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)):
            graded, failed = grading.grade_pending_sheets()
        self.assertEqual((graded, failed), (1, 0))
        self.assertTrue(MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).exists())

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_skips_already_graded(self):
        sheet = self._submitted_sheet()
        MasteryAssessment.objects.create(
            work_entry=sheet.work_entry, graded_by=None, ai_level="developing",
        )
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)) as gw:
            graded, failed = grading.grade_pending_sheets()
        self.assertEqual((graded, failed), (0, 0))
        gw.assert_not_called()  # nothing pending → no API call

    def test_noop_when_grader_not_configured(self):
        self._submitted_sheet()
        self.assertFalse(ai.is_configured())
        self.assertEqual(grading.grade_pending_sheets(), (0, 0))

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_limit_bounds_the_sweep(self):
        self._submitted_sheet()
        self._submitted_sheet()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)):
            graded, _failed = grading.grade_pending_sheets(limit=1)
        self.assertEqual(graded, 1)  # only one graded this run; the other stays pending

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_command_reports_counts(self):
        self._submitted_sheet()
        out = StringIO()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(GRADE_DICT)):
            call_command("grade_pending", stdout=out)
        self.assertIn("graded 1", out.getvalue())


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


class OneAssessmentPerWorkEntryTests(TestCase):
    """HH-144: the one-assessment-per-entry rule was enforced only by an application
    row lock, and prod had already accumulated an entry with THREE assessments."""

    @classmethod
    def setUpTestData(cls):
        from students.models import Student
        from worklog.models import WorkLogEntry
        User = get_user_model()
        cls.parent = User.objects.create_user("oa_parent", "oa@example.com", "pw")
        cls.kid = Student.objects.create(parent=cls.parent, first_name="Nia")
        cls.entry = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.kid, date=timezone.localdate(),
            subject="Math", description="p.40",
        )

    def _make(self, entry=None, **kw):
        from tutor.models import MasteryAssessment
        return MasteryAssessment.objects.create(
            work_entry=entry or self.entry, rubric="r", answers="a", **kw)

    def test_a_second_assessment_is_refused_by_the_database(self):
        from django.db import IntegrityError, transaction
        from tutor.models import MasteryAssessment
        self._make()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._make()
        self.assertEqual(MasteryAssessment.objects.count(), 1)

    def test_a_different_entry_is_unaffected(self):
        from tutor.models import MasteryAssessment
        from worklog.models import WorkLogEntry
        other = WorkLogEntry.objects.create(
            parent=self.parent, child=self.kid, date=timezone.localdate(),
            subject="Reading", description="ch.2",
        )
        self._make()
        self._make(entry=other)
        self.assertEqual(MasteryAssessment.objects.count(), 2)


class AssessmentDedupeMigrationTests(TestCase):
    """The migration has to dedupe BEFORE adding the constraint, or the release
    aborts on prod — which already holds a work entry with three assessments.

    The keep rule is exercised directly rather than through the ORM: once the
    constraint stands there is no way to build a duplicate to feed it (that is the
    whole point), and on SQLite the constraint is an inline table constraint that
    every schema rebuild re-applies from the model. keep_one() sorts its own input
    precisely so it can be tested this way.
    """

    @staticmethod
    def _mod():
        from importlib import import_module
        return import_module("tutor.migrations.0018_one_assessment_per_work_entry")

    def _keep_one(self):
        return self._mod().keep_one

    def _row(self, pk, status, age_days, entry=1):
        # Unsaved instances: the rule only reads pk/work_entry_id/status/created_at.
        return MasteryAssessment(
            pk=pk, status=status, work_entry_id=entry,
            created_at=timezone.now() - timedelta(days=age_days),
        )

    def test_only_the_losers_of_a_duplicated_entry_are_deleted(self):
        # The selection is what destroys data, so cover it directly: the keeper must
        # not be in the kill list, and a row that was never duplicated must not be
        # swept up with them.
        doomed_pks = self._mod().doomed_pks
        keeper = self._row(1, MasteryAssessment.FINALIZED, age_days=9, entry=100)
        rows = [
            keeper,
            self._row(2, MasteryAssessment.DRAFT, age_days=1, entry=100),
            self._row(3, MasteryAssessment.DRAFT, age_days=0, entry=100),
            self._row(4, MasteryAssessment.DRAFT, age_days=0, entry=200),  # not duped
        ]
        self.assertEqual(sorted(doomed_pks(rows)), [2, 3])

    def test_nothing_is_deleted_when_every_entry_has_one(self):
        doomed_pks = self._mod().doomed_pks
        rows = [self._row(1, MasteryAssessment.DRAFT, age_days=0, entry=100),
                self._row(2, MasteryAssessment.FINALIZED, age_days=3, entry=200)]
        self.assertEqual(doomed_pks(rows), [])

    def test_a_finalized_assessment_survives_a_newer_draft(self):
        # The stamped level is what the parent decided and what the charter report
        # counts, so keeping the most recent row would erase the wrong one.
        keep_one = self._keep_one()
        old_final = self._row(1, MasteryAssessment.FINALIZED, age_days=9)
        rows = [self._row(2, MasteryAssessment.DRAFT, age_days=1),
                old_final,
                self._row(3, MasteryAssessment.DRAFT, age_days=0)]
        self.assertEqual(keep_one(rows).pk, old_final.pk)

    def test_the_newest_wins_when_none_is_finalized(self):
        keep_one = self._keep_one()
        newest = self._row(2, MasteryAssessment.DRAFT, age_days=1)
        rows = [self._row(1, MasteryAssessment.DRAFT, age_days=4),
                newest,
                self._row(3, MasteryAssessment.DRAFT, age_days=7)]
        self.assertEqual(keep_one(rows).pk, newest.pk)

    def test_the_newest_wins_among_several_finalized(self):
        keep_one = self._keep_one()
        newer_final = self._row(1, MasteryAssessment.FINALIZED, age_days=1)
        rows = [self._row(2, MasteryAssessment.FINALIZED, age_days=6), newer_final]
        self.assertEqual(keep_one(rows).pk, newer_final.pk)

    def test_recency_is_by_timestamp_not_row_id(self):
        # A backfilled or re-imported row gets a high pk with an old created_at;
        # ranking on pk would then keep stale work.
        keep_one = self._keep_one()
        rows = [self._row(99, MasteryAssessment.DRAFT, age_days=30),
                self._row(2, MasteryAssessment.DRAFT, age_days=1)]
        self.assertEqual(keep_one(rows).pk, 2)

    def test_the_dedupe_is_a_no_op_when_there_are_no_duplicates(self):
        from importlib import import_module
        from students.models import Student
        from worklog.models import WorkLogEntry
        User = get_user_model()
        parent = User.objects.create_user("dd_parent", "dd@example.com", "pw")
        kid = Student.objects.create(parent=parent, first_name="Nia")
        entry = WorkLogEntry.objects.create(
            parent=parent, child=kid, date=timezone.localdate(),
            subject="Math", description="p.40",
        )
        only = MasteryAssessment.objects.create(
            work_entry=entry, rubric="r", answers="a")

        class _Apps:
            def get_model(self, app_label, name):
                return MasteryAssessment

        mod = import_module("tutor.migrations.0018_one_assessment_per_work_entry")
        mod.drop_duplicate_assessments(_Apps(), None)

        self.assertEqual([a.pk for a in MasteryAssessment.objects.all()], [only.pk])


@override_settings(
    ANTHROPIC_API_KEY="test-key",
    TUTOR_MONTHLY_COST_CEILING_USD=10.0,
    TUTOR_AI_PRICES={"big": (15.0, 75.0), "small": (1.0, 5.0)},
    TUTOR_AI_PRICE_FALLBACK=(15.0, 75.0),
)
class TutorSpendLedgerTests(TestCase):
    """HH-145: tutor is the higher-volume AI path and had no spend ceiling at all —
    only lingua did. A retry storm or a stuck daemon would surface as a bill."""

    def test_cost_is_priced_per_model_not_per_token_total(self):
        # The two tiers differ by 15x, so the same token count must not cost the
        # same. Deriving cost from a month's token total afterwards cannot work.
        big = spend.micro_usd_for("big", 1_000_000, 1_000_000)
        small = spend.micro_usd_for("small", 1_000_000, 1_000_000)
        self.assertEqual(big, 90_000_000)    # $15 in + $75 out
        self.assertEqual(small, 6_000_000)   # $1 in + $5 out

    def test_an_unknown_model_is_priced_at_the_expensive_tier(self):
        # Fail closed: over-estimating stops early and is recoverable; under-
        # estimating sails past the ceiling, which is the whole failure mode.
        self.assertEqual(
            spend.micro_usd_for("some-new-model", 1_000_000, 1_000_000),
            spend.micro_usd_for("big", 1_000_000, 1_000_000),
        )

    def test_usage_accumulates_across_calls(self):
        # Output tokens are the 5x side of the price table, so they are asserted
        # separately from input and the resulting cost is pinned exactly — reading
        # the wrong field would otherwise under-count the expensive half silently.
        spend.record_usage("small", _fake_usage(1_000_000, 1_000_000))
        spend.record_usage("small", _fake_usage(1_000_000, 1_000_000))
        row = AiSpend.objects.get()
        self.assertEqual(row.calls, 2)
        self.assertEqual(row.input_tokens, 2_000_000)
        self.assertEqual(row.output_tokens, 2_000_000)
        self.assertEqual(row.micro_usd, 12_000_000)   # 2 × ($1 in + $5 out)
        self.assertEqual(spend.month_to_date_usd(), 12.0)

    def test_cached_prompt_tokens_are_billed_too(self):
        # Anthropic reports cached tokens SEPARATELY from input_tokens. Reading
        # only input_tokens would under-count the moment anyone adds cache_control.
        usage = SimpleNamespace(
            input_tokens=1_000_000, output_tokens=0,
            cache_creation_input_tokens=1_000_000, cache_read_input_tokens=1_000_000,
        )
        spend.record_usage("small", usage)
        # 1M base + 1.25M weighted writes + 0.1M weighted reads
        self.assertEqual(AiSpend.objects.get().input_tokens, 2_350_000)

    def test_a_dated_snapshot_id_is_priced_as_its_family(self):
        # The API answers with the resolved snapshot, not the alias we asked for.
        # Exact-match-only pricing would bill every real call at the fallback tier.
        self.assertEqual(
            spend.prices_for("small-20260101"), spend.prices_for("small"),
        )

    def test_the_served_model_is_what_gets_priced(self):
        # A server-side substitution must not be billed at the tier we asked for.
        client = FakeAnthropic(GOOD_JSON, usage=_fake_usage(1_000_000, 0))
        client._create = lambda **kw: SimpleNamespace(
            content=[SimpleNamespace(type="text", text=GOOD_JSON)],
            usage=_fake_usage(1_000_000, 0),
            model="big",  # we asked for the grading model; the API served "big"
        )
        client.messages = SimpleNamespace(create=client._create)
        with override_settings(TUTOR_MODEL="small"):
            ai.grade_work(rubric="r", answers="a", grade_level="3rd",
                          subject="Math", client=client)
        self.assertEqual(AiSpend.objects.get().micro_usd, 15_000_000)  # big, not small

    def test_a_call_with_no_usage_object_still_counts_as_a_call(self):
        # Token counts can be missing; the call count is what reveals a runaway
        # loop even then, so it must not depend on them.
        spend.record_usage("small", None)
        self.assertEqual(AiSpend.objects.get().calls, 1)

    def test_spend_is_recorded_even_when_the_reply_cannot_be_parsed(self):
        # The seam records the instant the provider responds. A ledger that only
        # counted successful parses would under-count exactly the runaway case.
        client = FakeAnthropic("this is not JSON", usage=_fake_usage(500_000, 100_000))
        with self.assertRaises(ai.GraderError):
            ai.grade_work(rubric="r", answers="a", grade_level="3rd",
                          subject="Math", client=client)
        row = AiSpend.objects.get()
        self.assertEqual(row.calls, 1)
        self.assertEqual(row.input_tokens, 500_000)
        self.assertGreater(row.micro_usd, 0)

    def test_grading_is_refused_once_the_ceiling_is_reached(self):
        AiSpend.objects.create(period=timezone.now().strftime("%Y-%m"),
                               micro_usd=10_000_000)  # exactly $10.00 = the ceiling
        client = FakeAnthropic(GOOD_JSON, usage=_fake_usage(10, 10))
        with self.assertRaises(spend.BudgetExceeded):
            ai.grade_work(rubric="r", answers="a", grade_level="3rd",
                          subject="Math", client=client)
        # Checked BEFORE the call: crossing the ceiling costs one more call, not
        # an unbounded number.
        self.assertEqual(client.calls, 0)

    def test_just_under_the_ceiling_still_grades(self):
        AiSpend.objects.create(period=timezone.now().strftime("%Y-%m"),
                               micro_usd=9_999_999)
        client = FakeAnthropic(GOOD_JSON, usage=_fake_usage(10, 10))
        result = ai.grade_work(rubric="r", answers="a", grade_level="3rd",
                               subject="Math", client=client)
        self.assertEqual(result["level"], "proficient")
        self.assertEqual(client.calls, 1)

    def test_the_writing_helpers_degrade_instead_of_raising_at_a_child(self):
        # Deliberate asymmetry: a billing notice does not belong in a kid's
        # writing box, so these go quiet rather than erroring. Asserting the LOG is
        # what makes this discriminating — the generic `except Exception: return []`
        # underneath already returns [], so an empty list alone proves nothing.
        AiSpend.objects.create(period=timezone.now().strftime("%Y-%m"),
                               micro_usd=10_000_000)
        client = FakeAnthropic('["glad"]', usage=_fake_usage(10, 10))
        with self.assertLogs("tutor.ai", level="WARNING") as logs:
            self.assertEqual(ai.suggest_words("happy", client=client), [])
            self.assertEqual(ai.check_spelling("becuse", client=client), [])
        self.assertEqual(client.calls, 0)
        joined = "\n".join(logs.output)
        self.assertIn("Word suggestions skipped", joined)
        self.assertIn("Spellcheck skipped", joined)

    def test_the_draft_coach_degrades_rather_than_500ing_at_a_child(self):
        # review_draft's only caller is the kid's writing box, which catches
        # GraderError. Letting BudgetExceeded escape 500s a child-facing endpoint.
        AiSpend.objects.create(period=timezone.now().strftime("%Y-%m"),
                               micro_usd=10_000_000)
        client = FakeAnthropic('{"praise": "p", "suggestions": []}')
        with self.assertLogs("tutor.ai", level="WARNING"):
            with self.assertRaises(ai.GraderError):
                ai.review_draft(draft="d", assignment="a", grade_level="3rd",
                                subject="Writing", client=client)
        self.assertEqual(client.calls, 0)

    def test_the_scheduled_sweep_stops_once_instead_of_per_sheet(self):
        AiSpend.objects.create(period=timezone.now().strftime("%Y-%m"),
                               micro_usd=10_000_000)
        with self.assertLogs("tutor.grading", level="WARNING") as logs:
            self.assertEqual(grading.grade_pending_sheets(), (0, 0))
        self.assertEqual(len(logs.output), 1)
        self.assertIn("sweep skipped", logs.output[0])

    def test_the_month_rolls_over_in_local_time_not_utc(self):
        # Under America/Los_Angeles, UTC rolls the month seven hours early — the
        # ceiling would lift on the evening of the 31st while the refusal message
        # was still promising "the 1st".
        from datetime import datetime, timezone as dt_timezone
        from unittest.mock import patch as _patch
        late_august_pdt = datetime(2026, 9, 1, 1, 0, tzinfo=dt_timezone.utc)  # 6pm Aug 31 PDT
        with _patch("django.utils.timezone.now", return_value=late_august_pdt):
            self.assertEqual(spend._period(), "2026-08")

    def test_the_refusal_message_says_the_numbers_and_when_it_lifts(self):
        AiSpend.objects.create(period=timezone.now().strftime("%Y-%m"),
                               micro_usd=12_500_000)
        msg = spend.refusal_message()
        self.assertIn("$12.50", msg)
        self.assertIn("$10.00", msg)
        self.assertIn("1st", msg)

    def test_tutor_spend_does_not_touch_the_lingua_ledger(self):
        # The two ledgers are separate so lingua stays extractable (D-03); a tutor
        # call must not consume lingua's compliance budget or vice versa.
        from lingua.models import AiUsage
        spend.record_usage("small", _fake_usage(1_000, 1_000))
        self.assertEqual(AiUsage.objects.count(), 0)
        self.assertEqual(AiSpend.objects.count(), 1)


@override_settings(ANTHROPIC_API_KEY="test-key", TUTOR_MONTHLY_COST_CEILING_USD=10.0)
class SpendCeilingIsLegibleToUsersTests(TestCase):
    """The refusal has to reach a person as an explanation, not a 500 or a spinner
    that never resolves."""

    @classmethod
    def setUpTestData(cls):
        from students.models import Student
        from worklog.models import WorkLogEntry
        cls.parent = User.objects.create_user("sp", "sp@e.com", "pw")
        cls.family = Family.objects.create(name="Spend Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(parent=cls.parent, first_name="Ada",
                                           grade_level="G03", family=cls.family)
        cls.entry = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.child, subject="Math", family=cls.family,
            description="p.40",
        )

    def _max_out(self):
        AiSpend.objects.create(period=timezone.now().strftime("%Y-%m"),
                               micro_usd=10_000_000)

    def test_the_grade_button_explains_instead_of_spinning(self):
        # Past this redirect the parent would get a pending page that polls until
        # it gives up, with nothing saying why.
        self._max_out()
        self.client.login(username="sp", password="pw")
        resp = self.client.post(
            reverse("tutor:assess_create", kwargs={"entry_pk": self.entry.pk}),
            data={"rubric": "r", "answers": "a"}, follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "reached the")
        self.assertFalse(MasteryAssessment.objects.filter(work_entry=self.entry).exists())

    def test_a_childs_submitted_work_is_held_not_lost(self):
        # The kid must never meet a spending notice, and their work must survive
        # to be graded later — same behaviour as having no API key at all.
        from tutor import grading
        self._max_out()
        sheet = SimpleNamespace(is_submitted=True, work_entry_id=self.entry.pk, pk=1)
        assessment, created = grading.auto_grade_sheet(sheet)
        self.assertIsNone(assessment)
        self.assertFalse(created)


class MarkupStrokeReaderTests(TestCase):
    """The drawn-on sentence, read back as text a grader can mark (HH-154).

    A markup answer used to reach the grader as `annotated: yes` — it knew she
    had drawn, never what she marked — so all 260 mark-the-sentence exercises
    were ungradeable. Every word now renders in its own span, so the strokes over
    it can be named.
    """

    def _q(self, passage="Seth is a vet."):
        return Question(response_type=Question.TYPE_MARKUP, passage=passage)

    def _answer(self, marks, unread=0, strokes=None):
        return json.dumps({
            "strokes": strokes if strokes is not None else [{"p": [[0, 0], [1, 1]]}],
            "marks": marks, "unread": unread,
        })

    def test_words_are_numbered_across_the_whole_passage(self):
        # The index identifies a word in the passage, not its position on a line —
        # otherwise a two-line sentence has two word 0s and the marks are ambiguous.
        lines = self._q("Seth is a vet.\nHe helps pets.").markup_lines
        self.assertEqual([w["text"] for w in lines[0]], ["Seth", "is", "a", "vet."])
        self.assertEqual([w["i"] for w in lines[1]], [4, 5, 6])

    def test_the_grader_is_told_which_words_she_marked(self):
        sheet = ResponseSheet()
        out = sheet._format_markup(
            self._answer([{"i": 0, "word": "Seth", "kind": "underlined"},
                          {"i": 3, "word": "vet.", "kind": "circled"}]),
            self._q(),
        )
        self.assertIn('underlined "Seth"', out)
        self.assertIn('circled "vet."', out)

    def test_an_unread_stroke_is_reported_as_a_fact_not_a_verdict(self):
        # The answer is also what the PARENT reads in the work browser and what
        # lands in the charter report, so it states what happened. Telling the
        # grader how to treat it belongs in the rubric, not in her answer.
        sheet = ResponseSheet()
        out = sheet._format_markup(
            self._answer([{"i": 0, "word": "Seth", "kind": "underlined"}], unread=2),
            self._q(),
        )
        self.assertIn('underlined "Seth"', out)
        self.assertIn("not machine-readable", out)
        self.assertNotIn("wrong", out)
        self.assertNotIn("do not", out)

    def test_drawing_nothing_readable_says_so_plainly(self):
        sheet = ResponseSheet()
        out = sheet._format_markup(self._answer([], unread=1), self._q())
        self.assertIn("none were machine-readable", out)
        self.assertNotIn("wrong", out)

    def test_a_junk_unread_count_cannot_break_turning_work_in(self):
        # answer_display runs inside the transaction that submits the sheet, and
        # autosave accepts whatever the client posts — so junk here must degrade,
        # not raise, or the child cannot turn her work in at all.
        sheet = ResponseSheet()
        for junk in ('{"strokes": [{"p": []}], "marks": [], "unread": "x"}',
                     '{"strokes": [{"p": []}], "marks": [], "unread": [1, 2]}',
                     '{"strokes": "not a list", "marks": null, "unread": null}'):
            out = sheet._format_markup(junk, self._q())
            self.assertTrue(out.startswith("["), out)

    def test_an_untouched_sentence_reads_as_nothing_marked(self):
        sheet = ResponseSheet()
        self.assertIn("nothing marked", sheet._format_markup("", self._q()))

    def test_answers_saved_before_marks_existed_still_load(self):
        # Old answers are a bare list of strokes. The word positions they were
        # drawn over are gone, so they can only report that she drew — but they
        # must not crash or read as empty.
        sheet = ResponseSheet()
        legacy = json.dumps([{"c": "#333", "p": [[0.1, 0.5], [0.4, 0.5]]}])
        out = sheet._format_markup(legacy, self._q())
        self.assertIn("she drew 1 mark", out)
        self.assertIn("none were machine-readable", out)

    def test_a_corrupt_answer_degrades_instead_of_raising(self):
        sheet = ResponseSheet()
        self.assertIn("nothing marked", sheet._format_markup("{not json", self._q()))

    def test_the_stroke_reader_itself(self):
        """Run the JS classifier's own tests through node.

        The geometry is the part that can go subtly wrong — a misread turns a
        correct answer into a wrong one — so it is tested against realistic word
        boxes rather than trusted. Kept as JS so the shipped file is what runs.
        """
        import shutil
        import subprocess
        from django.conf import settings

        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        script = os.path.join(settings.BASE_DIR, "static", "js", "portal-markup.test.js")
        result = subprocess.run([node, script], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0,
                         f"stroke reader tests failed:\n{result.stdout}\n{result.stderr}")
        self.assertIn("0 failed", result.stdout)


class GraderIsToldTheTaskTests(TestCase):
    """The rubric sent to the grader (HH-154).

    Markup answers named the marks but the grader was never told what the
    exercise ASKED for — the instruction lives on the question set's intro and
    was not being sent — so it was marking an answer whose question it had never
    seen.
    """

    def _set(self, intro="Underline the complete subject.", markup=True):
        from curricula.models import Chapter
        from .models import QuestionSet
        user = User.objects.create_user("gt", "gt@e.com", "pw")
        cur = Curriculum.objects.create(parent=user, name="G", subject="Writing")
        ch = Chapter.objects.create(curriculum=cur, number=1, title="C")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L")
        qset = QuestionSet.objects.create(
            lesson=lesson, title="T", intro=intro, rubric="Base rubric.")
        Question.objects.create(
            question_set=qset, order=1, category="editing",
            response_type=Question.TYPE_MARKUP if markup else Question.TYPE_TEXT,
            passage="The dog ran.", prompt="" if markup else "Write.")
        return qset

    def test_the_rubric_carries_what_she_was_asked_to_do(self):
        rubric = grading._rubric_for(self._set())
        self.assertIn("Underline the complete subject.", rubric)
        self.assertIn("Base rubric.", rubric)

    def test_a_markup_set_tells_the_grader_how_to_treat_unread_marks(self):
        rubric = grading._rubric_for(self._set())
        self.assertIn("not machine-readable", rubric)
        self.assertIn("Do NOT count it wrong", rubric)

    def test_a_set_with_no_markup_does_not_carry_the_markup_note(self):
        rubric = grading._rubric_for(self._set(markup=False))
        self.assertNotIn("machine-readable", rubric)


class SaxonLessonToolTests(TestCase):
    """The Saxon lesson tools' pure cores (HH-155).

    Kept as JS so the file that ships is the file that is tested. The arithmetic
    is the part that can be subtly wrong — a curve that misses her points, or a
    click that lands one square off — and none of it needs a DOM.
    """

    def _run(self, name):
        import shutil
        import subprocess
        from django.conf import settings

        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        script = os.path.join(settings.BASE_DIR, "static", "js", name)
        result = subprocess.run([node, script], capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0,
                         f"{name} failed:\n{result.stdout}\n{result.stderr}")
        self.assertIn("0 failed", result.stdout)

    def test_the_graph_paper_core(self):
        self._run("portal-grid.test.js")

    def test_the_ratio_bar_and_decimal_slider_cores(self):
        self._run("portal-tools.test.js")


class SaxonLessonSeedTests(TestCase):
    """Seeding a Saxon lesson, and the guards that stop a broken one shipping."""

    @classmethod
    def setUpTestData(cls):
        from curricula.services import apply_blueprint, get_blueprint
        from students.models import Student
        cls.parent = User.objects.create_user("sxp", "sxp@e.com", "pw")
        cls.kid = Student.objects.create(parent=cls.parent, first_name="Kaylin",
                                         grade_level="G07")
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Saxon Pre-Algebra (DIVE)", subject="Math",
            grade_level="G07")
        apply_blueprint(cls.cur, get_blueprint("saxon_prealgebra_dive"))

    def _seed(self, lesson):
        call_command(f"seed_saxon_{lesson}", "--curriculum", str(self.cur.pk),
                     stdout=StringIO())

    def test_each_lesson_seeds_a_material_made_of_blocks(self):
        from tutor.models import LessonBlock
        for n in (71, 72, 73):
            self._seed(n)
            m = Material.objects.get(lesson__chapter__curriculum=self.cur,
                                     lesson__number=n)
            self.assertEqual(m.skill_type, Material.SKILL_LESSON)
            self.assertTrue(m.has_blocks)
            self.assertGreater(LessonBlock.objects.filter(material=m).count(), 8)
            # Seeds as DRAFT: a parent approves before a child sees it.
            self.assertEqual(m.status, Material.DRAFT)

    def test_seeding_twice_does_not_duplicate_or_grow(self):
        from tutor.models import LessonBlock
        self._seed(73)
        m = Material.objects.get(lesson__chapter__curriculum=self.cur, lesson__number=73)
        before = LessonBlock.objects.filter(material=m).count()
        self._seed(73)
        self.assertEqual(Material.objects.filter(lesson__number=73).count(), 1)
        self.assertEqual(LessonBlock.objects.filter(material=m).count(), before)

    def test_a_shortened_lesson_drops_its_leftover_blocks(self):
        from tutor.models import LessonBlock
        self._seed(73)
        m = Material.objects.get(lesson__chapter__curriculum=self.cur, lesson__number=73)
        LessonBlock.objects.create(material=m, order=99, kind=LessonBlock.KIND_MATH,
                                   data={"display": "left over"})
        self._seed(73)
        self.assertFalse(LessonBlock.objects.filter(material=m, order=99).exists())

    def test_every_lesson_teaches_the_parent_too(self):
        # The parent asked for this because he "didn't know how to really teach
        # that" — the guide is the deliverable, not a footnote.
        for n in (71, 72, 73):
            self._seed(n)
            m = Material.objects.get(lesson__chapter__curriculum=self.cur,
                                     lesson__number=n)
            self.assertIn("Teach it out loud", m.parent_content)
            self.assertIn("What to watch her do", m.parent_content)


class SaxonBlockValidationTests(TestCase):
    """The seeder refuses anything the template could not render (HH-155)."""

    def _validate(self, blocks):
        from django.core.management.base import CommandError
        from tutor.management.commands._saxon_seed import validate_blocks
        with self.assertRaises(CommandError) as ctx:
            validate_blocks(blocks)
        return str(ctx.exception)

    def test_an_unknown_block_kind_is_refused(self):
        # It would fall through every branch of the template and render as
        # nothing at all — a blank space on a child's screen, no error anywhere.
        from tutor.models import LessonBlock
        self.assertIn("unknown kind", self._validate([("hologram", {})]))

    def test_a_block_missing_its_content_is_refused(self):
        from tutor.models import LessonBlock
        msg = self._validate([(LessonBlock.KIND_PURPOSE, {"title": "Why"})])
        self.assertIn("missing 'paragraphs'", msg)

    def test_a_table_point_off_the_grid_is_refused(self):
        # The cruellest failure in the set: she reads "plot (2, 8)", finds no row
        # 8 on the paper, and concludes she has misunderstood the lesson.
        from tutor.models import LessonBlock
        msg = self._validate([(LessonBlock.KIND_TOOL, {
            "widget": "grid",
            "config": {"view": {"xmin": -6, "xmax": 6, "ymin": -6, "ymax": 6},
                       "table": [[2, 8]]},
        })])
        self.assertIn("(2, 8)", msg)
        self.assertIn("only shows", msg)

    def test_a_widget_that_does_not_exist_is_refused(self):
        from tutor.models import LessonBlock
        msg = self._validate([(LessonBlock.KIND_TOOL,
                               {"widget": "hologram", "config": {}})])
        self.assertIn("no such widget", msg)

    def test_the_real_lessons_all_validate(self):
        from tutor.management.commands._saxon_seed import validate_blocks
        for mod in ("seed_saxon_71", "seed_saxon_72", "seed_saxon_73"):
            blocks = __import__(f"tutor.management.commands.{mod}",
                                fromlist=["BLOCKS"]).BLOCKS
            validate_blocks(blocks)      # must not raise
