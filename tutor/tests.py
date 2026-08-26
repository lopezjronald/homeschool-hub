from django.core.management.base import CommandError
import json
import os
import tempfile
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from django.urls import reverse

from core.models import Family, FamilyMembership
from curricula.models import Curriculum, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from worklog.models import WorkLogEntry

from . import ai, grading, imagegen, mastery, spend
from .models import (AiSpend, Material, MasteryAssessment, Question,
                     QuestionSet, ResponseSheet)

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

    def test_external_links_open_in_a_new_tab(self):
        """A kid following a video/article link shouldn't lose their lesson: external
        links open in a new tab; internal (relative) links stay in the same tab."""
        from tutor.templatetags.tutor_extras import markdownify, markdownify_inline

        ext = markdownify("[Watch](https://www.youtube.com/watch?v=abc)")
        self.assertIn('target="_blank"', ext)
        self.assertIn('rel="noopener noreferrer"', ext)
        # The href (scheme included) must survive intact — a scheme-less href would
        # be a broken relative link, defeating the whole point.
        self.assertIn('href="https://www.youtube.com/watch?v=abc"', ext)
        # Same treatment for a question prompt rendered inline.
        inline = markdownify_inline("See [this](http://phet.colorado.edu)")
        self.assertIn('target="_blank"', inline)
        self.assertIn('href="http://phet.colorado.edu"', inline)
        # Internal links are left in-tab (no new window for the kid's own portal).
        internal = markdownify("[Back to portal](/portal/)")
        self.assertNotIn("target=", internal)
        self.assertIn('href="/portal/"', internal)
        # Idempotent: a second pass must not double-inject target=.
        self.assertEqual(markdownify(markdownify("[x](https://a.com)")).count("target="), 1)

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

    def _run(self, name, env=None):
        import shutil
        import subprocess
        from django.conf import settings

        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        script = os.path.join(settings.BASE_DIR, "static", "js", name)
        child_env = dict(os.environ, **(env or {}))
        result = subprocess.run([node, script], capture_output=True, text=True,
                                timeout=90, env=child_env)
        self.assertEqual(result.returncode, 0,
                         f"{name} failed:\n{result.stdout}\n{result.stderr}")
        self.assertIn("0 failed", result.stdout)
        return result.stdout

    def test_the_graph_paper_core(self):
        # Hand the checker the REAL seeded tables. Without this the .test.js file
        # asserts against its own typed copies of them, and the tool and the
        # lesson can drift apart in silence — which is how a child ends up being
        # told her correct answer is wrong.
        import json

        from tutor.management.commands.seed_saxon_73 import BLOCKS
        from tutor.models import LessonBlock

        tables = {}
        for kind, data in BLOCKS:
            if kind == LessonBlock.KIND_TOOL and data.get("widget") == "grid":
                rows = (data.get("config") or {}).get("table")
                if rows:
                    tables["practice"] = rows
        self.assertTrue(tables, "lesson 73 no longer ships a plottable table")
        out = self._run("portal-grid.test.js",
                        {"SAXON_GRID_TABLES": json.dumps(tables)})
        self.assertIn("the seeded practice table is the cubic table", out,
                      "the seeded tables were not actually checked")

    def test_the_ratio_bar_and_decimal_slider_cores(self):
        self._run("portal-tools.test.js")

    def test_the_chart_and_binary_cores(self):
        self._run("portal-chart.test.js")

    def test_the_triangle_and_inequality_cores(self):
        self._run("portal-triangle.test.js")

    def test_the_ordering_widget_core(self):
        """It decides whether a question counts as answered, and that counter
        sits above a submit button she cannot undo."""
        out = self._run("portal-choice.test.js")
        self.assertIn("one number in the last slot is not a finished answer", out,
                      "the half-answered case was not actually checked")


def saxon_lesson_numbers():
    """Every Saxon lesson that has a seed command, found by looking.

    The sweeping tests below used to carry a hardcoded (71, 72, 73). Adding a
    lesson then silently added UNCHECKED mathematics — the arithmetic guards
    would keep passing while covering nothing new, which is the worst kind of
    green. Discovery means a lesson is covered the moment its seeder exists.
    """
    import os
    import re

    here = os.path.join(os.path.dirname(__file__), "management", "commands")
    found = sorted(
        int(m.group(1))
        for name in os.listdir(here)
        for m in [re.fullmatch(r"seed_saxon_(\d+)\.py", name)]
        if m
    )
    if not found:                       # a rename would otherwise mute every sweep
        raise AssertionError("no seed_saxon_<n>.py commands found")
    return found


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
        for n in saxon_lesson_numbers():
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

    def test_changed_content_returns_an_approved_lesson_to_draft(self):
        """Approval is of specific content, not of a slot.

        The parent approves what the child will see. If a re-seed could rewrite
        an approved lesson in place, a corrected — or broken — page would reach
        her carrying an approval she never gave it.
        """
        from tutor.models import LessonBlock
        self._seed(73)
        m = Material.objects.get(lesson__chapter__curriculum=self.cur, lesson__number=73)
        m.status = Material.APPROVED
        m.save(update_fields=["status"])

        # A re-seed that changes nothing must NOT nag him to approve it again.
        self._seed(73)
        m.refresh_from_db()
        self.assertEqual(m.status, Material.APPROVED)

        # A re-seed that changes the content must.
        LessonBlock.objects.filter(material=m).update(data={"prose": "tampered"})
        self._seed(73)
        m.refresh_from_db()
        self.assertEqual(m.status, Material.DRAFT)

    def test_rewritten_intro_or_guide_also_needs_re_approval(self):
        """The blocks are not the only thing the child reads.

        title and student_intro are rendered at the top of her page and
        parent_content IS the teaching guide. A review found all three could be
        rewritten in place while an APPROVED lesson stayed approved.
        """
        from tutor.management.commands import seed_saxon_73 as mod
        self._seed(73)
        m = Material.objects.get(lesson__chapter__curriculum=self.cur, lesson__number=73)
        m.status = Material.APPROVED
        m.save(update_fields=["status"])

        original = mod.Command.STUDENT_INTRO
        try:
            mod.Command.STUDENT_INTRO = "Words the parent has never seen."
            self._seed(73)
        finally:
            mod.Command.STUDENT_INTRO = original
        m.refresh_from_db()
        self.assertEqual(m.student_intro, "Words the parent has never seen.")
        self.assertEqual(m.status, Material.DRAFT)

    def test_broken_widget_config_is_reported_not_crashed(self):
        """audit_content sweeps live rows; one malformed row must not abort it."""
        from django.core.management.base import CommandError

        from tutor.management.commands._saxon_seed import _unplottable, validate_blocks
        from tutor.models import LessonBlock

        # Never raises, whatever shape the row is.
        for config in ({"view": "big"}, {"view": []}, "not a dict", {"table": "nope"},
                       {"view": {"xmin": None}}, {"table": [[1]]}):
            self.assertIsInstance(_unplottable(1, config), list)

        # And validate_blocks names the problem rather than throwing AttributeError.
        with self.assertRaises(CommandError):
            validate_blocks([(LessonBlock.KIND_TOOL,
                              {"widget": "grid", "config": "not a dict"})])

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
        for n in saxon_lesson_numbers():
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


class SaxonLessonMathTests(TestCase):
    """The mathematics in the lessons themselves (HH-155).

    Written after a review swapped the x² and x³ tables in Lesson 73 and all 306
    tests still passed. Nothing asserted a single number in any lesson — for
    content whose whole purpose is being correct in front of a child.
    """

    def _blocks(self, lesson):
        mod = __import__(f"tutor.management.commands.seed_saxon_{lesson}",
                         fromlist=["BLOCKS"])
        return mod.BLOCKS

    def _grid_tools(self, lesson):
        from tutor.models import LessonBlock
        return [d for kind, d in self._blocks(lesson)
                if kind == LessonBlock.KIND_TOOL and d.get("widget") == "grid"]

    # The families, mirrored from portal-grid.js. If these drift apart the tool
    # and the content disagree, which is exactly how a right answer gets marked
    # wrong — so the test that pins the content uses the same definitions.
    FAMILIES = {
        "x": lambda x: x,
        "x^2": lambda x: x * x,
        "x^3": lambda x: x ** 3,
        "|x|": abs,
    }

    def test_every_table_a_child_is_asked_to_plot_is_a_real_function(self):
        for tool in self._grid_tools(73):
            table = tool["config"].get("table")
            if not table:
                continue
            fits = [name for name, f in self.FAMILIES.items()
                    if all(abs(f(x) - y) < 1e-9 for x, y in table)]
            self.assertTrue(fits, f"{table} is not any function family at all")

    def test_the_practice_table_is_the_cubic_the_reveal_claims(self):
        # The reveal block tells her the answer. If the table were swapped, the
        # lesson would be confidently wrong at her.
        from tutor.models import LessonBlock
        table = None
        for tool in self._grid_tools(73):
            if tool["config"].get("table"):
                table = tool["config"]["table"]
        self.assertIsNotNone(table)
        self.assertTrue(all(abs(x ** 3 - y) < 1e-9 for x, y in table),
                        f"the practice table {table} is not x³")
        self.assertFalse(all(abs(x * x - y) < 1e-9 for x, y in table),
                         "the practice table is ALSO x² — it cannot discriminate")
        reveal = [d for k, d in self._blocks(73) if k == LessonBlock.KIND_REVEAL]
        self.assertTrue(any("x³" in (d.get("answer") or "") for d in reveal))

    def test_the_x2_vs_x3_comparison_table_is_arithmetically_right(self):
        from tutor.models import LessonBlock
        table = next(d for k, d in self._blocks(73)
                     if k == LessonBlock.KIND_TABLE and d.get("headers") == ["x", "x²", "x³"])
        for row in table["rows"]:
            x, sq, cu = (int(c) for c in row["cells"])
            self.assertEqual(sq, x * x, f"x={x}: x² column says {sq}")
            self.assertEqual(cu, x ** 3, f"x={x}: x³ column says {cu}")

    def test_every_plottable_table_fits_on_the_grid_it_ships_with(self):
        for lesson in saxon_lesson_numbers():
            for tool in self._grid_tools(lesson):
                cfg = tool["config"]
                view = cfg.get("view") or {}
                for x, y in cfg.get("table") or []:
                    self.assertTrue(view["xmin"] <= x <= view["xmax"], f"({x},{y}) off grid")
                    self.assertTrue(view["ymin"] <= y <= view["ymax"], f"({x},{y}) off grid")

    def test_the_ratio_bar_reaches_the_number_the_lesson_asks_for(self):
        # Lesson 71's tool asks her to slide until Red reads 60. If the target
        # were not a whole multiple of the ratio part, it could never land.
        from tutor.models import LessonBlock
        tool = next(d for k, d in self._blocks(71)
                    if k == LessonBlock.KIND_TOOL and d.get("widget") == "ratiobar")
        cfg = tool["config"]
        part = next(p for p in cfg["parts"] if p["name"] == cfg["target"]["name"])
        target = cfg["target"]["actual"]
        self.assertEqual(target % part["ratio"], 0,
                         f"{target} is not a whole multiple of {part['ratio']}")
        self.assertLessEqual(target // part["ratio"], cfg["maxScale"],
                             "the slider cannot reach the target")
        # And the total the lesson claims (140) is what the tool would show.
        scale = target // part["ratio"]
        self.assertEqual(sum(p["ratio"] for p in cfg["parts"]) * scale, 140)

    def test_the_decimal_slider_starts_from_the_number_the_lesson_works(self):
        from tutor.models import LessonBlock
        tool = next(d for k, d in self._blocks(72)
                    if k == LessonBlock.KIND_TOOL and d.get("widget") == "scislide")
        cfg = tool["config"]
        # Example 72.1a is 3.2 x 10^3 — the tool should be showing that number.
        self.assertAlmostEqual(cfg["mantissa"] * 10 ** cfg["exponent"], 3200.0, places=6)


class SaxonWorkedExampleArithmeticTests(TestCase):
    """Every equation the lessons show a child must actually be true (HH-155).

    A review mutated five numbers across Lessons 71 and 72 — turning 9H = 270
    into H = 35, and 2 x 10^-3 into 2 x 10^3 — and the whole suite still passed.
    These lessons are almost entirely worked arithmetic, so nothing about them
    was guarded at all.

    The equations are parsed and EVALUATED rather than compared to copies of
    themselves. A test that holds the expected answer as a literal is only
    testing that someone typed the same thing twice.
    """

    SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾", "0123456789+-()")

    def _blocks(self, lesson):
        mod = __import__(f"tutor.management.commands.seed_saxon_{lesson}",
                         fromlist=["BLOCKS"])
        return mod.BLOCKS

    def _math_lines(self, lesson):
        """Every equation shown to the child, wherever it lives in the lesson.

        Includes the `right` line of an error block. Those carry the lesson's full
        authority — they are labelled "this is the correct way" — and were the
        least-guarded mathematics in the ticket.

        Includes a reveal's `answer`. A reveal is the block that says "here is the
        answer" after she has tried it herself, so it is about as authoritative as
        a page gets — and it was guarded by nothing at all.

        Deliberately EXCLUDES `wrong`: those are false on purpose, and a balance
        test would fail on exactly the lines that are supposed to be broken.

        Prose is safe to feed in. A side holding words evaluates to None and is
        skipped, so only genuinely arithmetic claims are checked.
        """
        lines = []
        for _kind, data in self._blocks(lesson):
            # "formula" is the masthead — the single most visible equation on
            # the page, and it was swept by nothing.
            for key in ("math", "answer", "display", "formula"):
                if isinstance(data.get(key), str) and data[key]:
                    lines.append(data[key])
            for step in (data.get("steps") or []):
                if isinstance(step, dict) and step.get("math"):
                    lines.append(step["math"])
            for item in (data.get("items") or []):
                if isinstance(item, dict) and item.get("right"):
                    lines.append(item["right"])
        return lines

    def _value(self, text):
        """The number a side of an equation comes out to, or None if it isn't one.

        Returns None for anything holding a variable or a unit word, so `3T` and
        `140 hats` are skipped rather than guessed at.
        """
        import re

        s = text.translate(self.SUPER)
        s = (s.replace("×", "*").replace("÷", "/").replace("−", "-")
              .replace("–", "-").replace("·", "*").replace(",", ""))
        s = s.strip().rstrip(".")
        # A trailing UNIT is separated by a space ("140 hats"); a variable is not
        # ("3T"). Strip the first, keep the second so it disqualifies the side.
        s = re.sub(r"\s+[A-Za-z]+$", "", s).strip()
        if not s or re.search(r"[A-Za-z]", s):
            return None
        # implicit multiplication: (5)(3)
        s = re.sub(r"\)\s*\(", ")*(", s)
        if not re.fullmatch(r"[\d\s.+\-*/()]+", s):
            return None
        try:
            return eval(s, {"__builtins__": {}}, {})  # noqa: S307 - digits only
        except (SyntaxError, ZeroDivisionError, TypeError, NameError):
            return None

    def _powers(self, text):
        """Rewrite `4.1 × 10⁴` as `4.1 * 10**4` before any other normalising."""
        import re

        def repl(m):
            return f"*10**({m.group(1).translate(self.SUPER)})"

        return re.sub(r"[×x]\s*10([⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾]+)", repl, text)

    def _sides(self, statement, binary=False):
        """Every value the statement asserts equal.

        A side may offer alternatives ("32 x 10^2 or 0.32 x 10^4"). Both are
        claimed equal to the other side, so both are returned and both are
        checked — that is what the line actually promises the child.

        With binary=True, a side that is a bare run of 0s and 1s is read in base
        two. Only used as a second attempt, so ordinary decimals like 100 and 101
        keep their obvious meaning everywhere else.
        """
        import re

        values = []
        for part in statement.split("="):
            for alt in part.split(" or "):
                bare = alt.strip()
                if binary and re.fullmatch(r"[01]{2,}", bare):
                    values.append(float(int(bare, 2)))
                else:
                    values.append(self._value(self._powers(alt)))
        return values

    def _balances(self, statement, slack):
        """Do all the sides of this statement come out the same?

        A numeral written only in 0s and 1s is ambiguous in a course that teaches
        binary: Lesson 75's "1011 = 8 + 2 + 1 = 11" is true with the left side in
        base two and false with it in base ten. Such a side is allowed EITHER
        reading, anchored to the sides that are not ambiguous ("8 + 2 + 1" can
        only mean eleven). That turns what would be a false alarm into a real
        check of the conversion.

        If every side is ambiguous there is nothing to anchor to, and base ten is
        used — the ordinary meaning.
        """
        import re

        tol = max(slack, 1e-9)
        anchors, ambiguous = [], []
        for part in statement.split("="):
            for alt in part.split(" or "):
                bare = alt.strip()
                v = self._value(self._powers(alt))
                if v is None:
                    continue
                if re.fullmatch(r"[01]{2,}", bare):
                    ambiguous.append((v, float(int(bare, 2))))
                else:
                    anchors.append(v)

        if len(anchors) + len(ambiguous) < 2:
            return True                      # nothing to compare
        if not anchors:
            anchors = [ambiguous[0][0]]
            ambiguous = ambiguous[1:]
        if any(abs(a - anchors[0]) > tol for a in anchors):
            return False
        return all(any(abs(r - anchors[0]) <= tol for r in readings)
                   for readings in ambiguous)

    def _rounding_slack(self, statement):
        """How far two sides may differ before they disagree.

        Saxon rounds all the time — "Round to 2 d.p." — so 45 / 2.7 = 16.7 is a
        correct line that an exact check calls broken. Demanding exactness does
        not make the lessons more correct; it makes rounded lines impossible to
        write in a checkable form, which is how the guard gets dodged.

        So: half a unit in the last place of the LEAST precise number written in
        the statement, which is exactly what rounding to that place promises. An
        all-integer statement gets no slack at all.
        """
        import re

        decimals = [len(m.group(1)) for m in re.finditer(r"\d+\.(\d+)", statement)]
        if not decimals:
            return 0.0
        return 0.5 * 10 ** (-min(decimals))

    def test_every_equation_in_lessons_71_and_72_balances(self):
        import re

        checked = 0
        for lesson in saxon_lesson_numbers():
            for line in self._math_lines(lesson):
                for statement in re.split(r"→|⇒", line):
                    if "=" not in statement:
                        continue
                    values = [v for v in self._sides(statement) if v is not None]
                    if len(values) < 2:
                        continue
                    checked += 1
                    slack = self._rounding_slack(statement)
                    self.assertTrue(
                        self._balances(statement, slack),
                        f"L{lesson}: {statement.strip()!r} does not balance")
        # If the parser silently stopped understanding the notation this test
        # would pass by checking nothing at all.
        self.assertGreaterEqual(checked, 8, f"only {checked} equations were checked")

    def test_lesson_71s_answers_follow_from_its_own_questions(self):
        """Recompute each answer from the numbers the question states.

        Both halves are pinned: change a number in the question and the expected
        inputs no longer match; change the answer and the arithmetic no longer
        matches.
        """
        import re

        from tutor.models import LessonBlock
        worked = {d["number"]: d for k, d in self._blocks(71)
                  if k == LessonBlock.KIND_WORKED}

        # 71.2 — oxygen : hydrogen by mass, over a stated TOTAL mass of water.
        d = worked["71.2"]
        nums = [int(n) for n in re.findall(r"\d+", d["question"])]
        self.assertEqual(nums, [8, 1, 270], "the 71.2 question changed")
        oxygen, hydrogen, total = nums
        self.assertEqual(f"{total * hydrogen // (oxygen + hydrogen)} grams of hydrogen",
                         d["answer"])

        # 71.3 — a percent, its complement, and the count of the OTHER part.
        d = worked["71.3"]
        nums = [int(n) for n in re.findall(r"\d+", d["question"])]
        self.assertEqual(nums, [20, 32], "the 71.3 question changed")
        apple_pct, oranges = nums
        self.assertEqual(f"{oranges * 100 // (100 - apple_pct)} pieces of fruit",
                         d["answer"])

    def test_every_worked_answer_appears_in_the_step_that_produces_it(self):
        """The steps and the answer must not tell her different numbers.

        A review mutated `H = 30` to `H = 35` in the steps while leaving the
        answer as "30 grams" — a lesson that contradicts itself mid-page, which
        is worse for a child than one that is plainly wrong.

        A block may carry several answers (72.3-72.4 works four problems and
        lists all four results). Where the counts line up, each answer is matched
        against ITS OWN step rather than all of them against the last one.
        """
        import re

        from tutor.models import LessonBlock

        def shows(haystack, needle):
            flat = " ".join(haystack.split())
            needle = " ".join(needle.split())
            if re.fullmatch(r"[\d.]+", needle):
                # A bare number must be the whole number, not a piece of a
                # bigger one: "30" must not be satisfied by "270".
                return re.search(rf"(?<![\d.]){re.escape(needle)}(?![\d.])", flat)
            return needle in flat

        checked = 0
        for lesson in saxon_lesson_numbers():
            for kind, data in self._blocks(lesson):
                if kind != LessonBlock.KIND_WORKED or not data.get("answer"):
                    continue
                steps = [st for st in data["steps"]
                         if isinstance(st, dict) and st.get("math")]
                if not steps:
                    continue
                chunks = [c.strip() for c in data["answer"].split("·") if c.strip()]
                # Strip a trailing unit phrase: "30 grams of hydrogen" -> "30".
                cores = [re.sub(r"(\s+[A-Za-z]+)+$", "", c).strip() for c in chunks]
                if len(cores) > 1 and len(cores) == len(steps):
                    pairs = list(zip(cores, steps))
                else:
                    pairs = [(cores[0], steps[-1])]
                for core, step in pairs:
                    if not core:
                        continue
                    checked += 1
                    self.assertTrue(
                        shows(step["math"], core),
                        f"{data['number']}: the answer says {core!r} but the step "
                        f"that should produce it says {step['math']!r}")
        self.assertGreaterEqual(checked, 6, f"only {checked} answers were checked")

    def test_every_proportion_lesson_71_solves_is_solved_correctly(self):
        """a/b = c/X  ->  X = n must actually have n = b*c/a.

        The balance test cannot see these: both sides hold the unknown, so it
        skips them. But solving a proportion IS Lesson 71, and its error block
        states the correct answer with full authority — a wrong number there
        teaches the very mistake the block exists to prevent.

        Only a line whose LAST segment is the bare statement "X = n" counts. The
        cross-multiply line ends "3 × T = 7 × 60", which states a step and not an
        answer; reading an answer out of it found 7 and called the lesson wrong.
        """
        import re

        setup = re.compile(r"(\d+)\s*/\s*(\d+)\s*=\s*(\d+)\s*/\s*([A-Za-z])")
        checked = 0
        for line in self._math_lines(71):
            found = setup.search(line)
            if not found:
                continue
            a, b, c, var = found.groups()
            last = re.split(r"->|→", line)[-1]
            answer = re.fullmatch(r"\s*" + re.escape(var) + r"\s*=\s*(\d+)\s*", last)
            if not answer:
                continue
            a, b, c = int(a), int(b), int(c)
            stated = int(answer.group(1))
            checked += 1
            self.assertEqual(
                stated, b * c // a,
                f"{line!r} says the answer is {stated}, but "
                f"{a}/{b} = {c}/{var} gives {b * c / a:g}")
        self.assertGreaterEqual(checked, 1, "no proportion was checked at all")

    def test_the_ratio_box_total_row_is_the_sum_of_its_parts(self):
        """The caption calls the total row 'the whole lesson'. It has to be right."""
        from tutor.models import LessonBlock
        table = next(d for k, d in self._blocks(71)
                     if k == LessonBlock.KIND_TABLE and d.get("headers") == ["", "Ratio", "Actual"])
        parts, total = [], None
        for row in table["rows"]:
            name, ratio = row["cells"][0], row["cells"][1]
            if name.upper() == "TOTAL":
                total = int(ratio)
            else:
                parts.append(int(ratio))
        self.assertIsNotNone(total, "the ratio box lost its total row")
        self.assertEqual(total, sum(parts),
                         f"the box says the total is {total}, but {parts} sum to "
                         f"{sum(parts)}")

    def test_lesson_71s_stepped_example_lands_on_the_right_total(self):
        import re

        from tutor.models import LessonBlock
        stepper = next(d for k, d in self._blocks(71) if k == LessonBlock.KIND_STEPPER)
        red, blue = 3, 4
        self.assertIn(f"{red} : {blue}", stepper["equation"])
        reds = int(re.search(r"(\d+)\s*reds", stepper["equation"]).group(1))
        total = reds * (red + blue) // red
        self.assertIn(f"{total} hats", stepper["steps"][-1]["math"])

    def test_lesson_72s_stated_answers_equal_their_own_questions(self):
        """Each worked answer, evaluated, must equal its question evaluated."""
        from tutor.models import LessonBlock
        checked = 0
        for kind, data in self._blocks(72):
            if kind != LessonBlock.KIND_WORKED or not data.get("answer"):
                continue
            want = self._value(self._powers(data["question"]))
            got = self._value(self._powers(data["answer"]))
            if want is None or got is None:
                continue
            checked += 1
            self.assertAlmostEqual(
                got, want, delta=abs(want) * 1e-9,
                msg=f"{data['number']}: {data['question']} != {data['answer']}")
        self.assertGreaterEqual(checked, 2, f"only {checked} answers were checked")


class SaxonBatchSeedCommandTests(TestCase):
    """The runner that makes deploying thirty lessons one command (HH-155)."""

    def test_it_understands_the_selection_forms(self):
        from tutor.management.commands.seed_saxon import parse_selection
        avail = [71, 72, 73, 74, 75]
        self.assertEqual(parse_selection("all", avail), avail)
        self.assertEqual(parse_selection("72-74", avail), [72, 73, 74])
        self.assertEqual(parse_selection("75,71", avail), [71, 75])
        self.assertEqual(parse_selection("73", avail), [73])
        # A range and a list together, deduplicated and ordered.
        self.assertEqual(parse_selection("71-73,72,75", avail), [71, 72, 73, 75])

    def test_asking_for_a_lesson_with_no_seeder_is_an_error(self):
        """Silently skipping it would leave a lesson missing from a deploy.

        The failure mode this prevents: 'seed_saxon --lesson 74-100' on a branch
        where half those files do not exist yet, reporting success.
        """
        from django.core.management.base import CommandError

        from tutor.management.commands.seed_saxon import parse_selection
        with self.assertRaises(CommandError) as ctx:
            parse_selection("71-80", [71, 72, 73])
        for missing in ("74", "75", "80"):
            self.assertIn(missing, str(ctx.exception))

    def test_it_rejects_nonsense_rather_than_seeding_nothing(self):
        from django.core.management.base import CommandError

        from tutor.management.commands.seed_saxon import parse_selection
        for bad in ("seventy-four", "80-74", "71..73"):
            with self.assertRaises(CommandError):
                parse_selection(bad, [71, 72, 73])

    def test_discovery_finds_the_lessons_that_exist(self):
        from tutor.management.commands.seed_saxon import available_lessons
        self.assertEqual(available_lessons(), saxon_lesson_numbers())

    def test_it_actually_seeds_the_range_it_was_given(self):
        from curricula.models import Curriculum
        from curricula.services import apply_blueprint, get_blueprint
        from tutor.models import Material

        parent = User.objects.create_user("sxb", "sxb@e.com", "pw")
        cur = Curriculum.objects.create(
            parent=parent, name="Saxon Pre-Algebra (DIVE)", subject="Math",
            grade_level="G07")
        apply_blueprint(cur, get_blueprint("saxon_prealgebra_dive"))

        out = StringIO()
        call_command("seed_saxon", "--curriculum", str(cur.pk),
                     "--lesson", "71,73", stdout=out)
        seeded = set(Material.objects
                     .filter(lesson__chapter__curriculum=cur)
                     .values_list("lesson__number", flat=True))
        self.assertEqual(seeded, {71, 73}, "the runner seeded the wrong lessons")
        self.assertIn("Seeded 2 lesson(s)", out.getvalue())


class LessonToolTemplateContractTests(TestCase):
    """Every widget must find the config the template hands it (HH-155).

    A new widget read `data-config` while the template has always emitted
    `data-config-id`. Nothing failed: the script simply found nothing and left an
    empty div, so the child would have got a blank space where the interactive
    part of her lesson should be. That is the exact failure the seed validator
    was built to prevent, arriving through a door it does not watch.
    """

    def _render(self, widget, config):
        from django.template.loader import render_to_string

        from curricula.models import Chapter, Curriculum, Lesson
        from tutor.models import LessonBlock, Material
        lesson = Lesson.objects.create(
            chapter=Chapter.objects.create(
                curriculum=Curriculum.objects.create(
                    parent=User.objects.create_user(
                        f"tc{widget}", f"tc{widget}@e.com", "pw"),
                    name="C", subject="Math", grade_level="G07"),
                number=1, title="One"),
            order=1, number=1, title="L")
        m = Material.objects.create(lesson=lesson, title="T",
                                    skill_type=Material.SKILL_LESSON,
                                    student_intro="i", student_content="i",
                                    parent_content="p")
        block = LessonBlock.objects.create(
            material=m, order=1, kind=LessonBlock.KIND_TOOL,
            data={"widget": widget, "config": config})
        html = render_to_string("portal/_lesson_blocks.html", {"blocks": [block]})
        return html, block

    def test_every_known_widget_is_handed_a_config_it_can_find(self):
        import re

        from tutor.management.commands._saxon_seed import KNOWN_WIDGETS

        for widget in sorted(KNOWN_WIDGETS):
            html, block = self._render(widget, {"probe": widget})
            self.assertIn(f'data-tool="{widget}"', html)
            # The id on the host must be the id of a script that is really there.
            m = re.search(r'data-config-id="([^"]+)"', html)
            self.assertIsNotNone(m, f"{widget}: no config id on the host element")
            self.assertIn(f'id="{m.group(1)}"', html,
                          f"{widget}: the host points at a config that is not on the page")
            self.assertEqual(m.group(1), block.config_dom_id)

    def test_the_scripts_read_the_attribute_the_template_writes(self):
        """Read the JS itself, because this is a cross-file contract.

        Nothing else in the suite can see it: the template test above proves the
        attribute is written, the node tests prove the maths, and neither one
        notices that the two halves disagree about the name.
        """
        import os
        import re

        from django.conf import settings

        js_dir = os.path.join(settings.BASE_DIR, "static", "js")
        checked = 0
        for name in sorted(os.listdir(js_dir)):
            if not re.fullmatch(r"portal-\w+\.js", name):
                continue
            with open(os.path.join(js_dir, name), encoding="utf-8") as fh:
                src = fh.read()
            # A LESSON widget is one that mounts on .lesson-tool[data-tool=...].
            # portal-markup.js has a [data-tool=undo] button and is not one.
            if ".lesson-tool[data-tool=" not in src:
                continue
            checked += 1
            self.assertIn("dataset.configId", src,
                          f"{name} does not read the id the template writes")
            self.assertNotIn('getAttribute("data-config")', src,
                             f"{name} reads an attribute the template never writes")
        self.assertGreaterEqual(checked, 5,
                                f"only {checked} widget modules were checked")


class SocialStudiesVioletSeedTests(TestCase):
    """Violet's Grade 3 Social Studies mission course: self-contained seed, renders
    on the portal, no AI. Mirrors the discovery-driven Saxon tests."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.parent = User.objects.create_user("ssviolet", email="ssv@e.com", password="pw")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03")

    def _seed(self):
        call_command("seed_ss_violet", stdout=StringIO())

    def test_seeds_curriculum_units_missions_and_approved_materials(self):
        from curricula.models import Chapter, CurriculumPlacement
        from tutor.models import LessonBlock, Material
        self._seed()
        curr = Curriculum.objects.get(name__startswith="Social Studies 3")
        self.assertEqual(curr.subject, "Social Studies")
        self.assertEqual(curr.grade_level, "G03")
        self.assertEqual(Chapter.objects.filter(curriculum=curr).count(), 6)   # 5 units + capstone
        self.assertEqual(Lesson.objects.filter(chapter__curriculum=curr).count(), 24)
        mats = Material.objects.filter(
            lesson__chapter__curriculum=curr, skill_type=Material.SKILL_LESSON)
        self.assertEqual(mats.count(), 24)
        self.assertTrue(all(m.status == Material.APPROVED for m in mats),
                        "missions must seed APPROVED so they're visible day one")
        # Every mission carries the uniform "do this" + completion blocks.
        for m in mats:
            kinds = list(m.blocks.order_by("order").values_list("kind", flat=True))
            self.assertIn(LessonBlock.KIND_STEPS, kinds, m.title)
            self.assertIn(LessonBlock.KIND_RECAP, kinds, m.title)
            self.assertIn("Parent check", m.parent_content, m.title)
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.violet, curriculum=curr).exists())

    def test_is_idempotent(self):
        from tutor.models import Material
        self._seed()
        self._seed()
        self.assertEqual(
            Material.objects.filter(skill_type=Material.SKILL_LESSON).count(), 24)

    def test_a_mission_renders_with_a_clickable_resource_link_and_completion(self):
        """The 'Watch/Read first' URL must render as a real link (markdownify), and
        the completion block must appear — proving the no-UI, in-app delivery works."""
        from django.template.loader import render_to_string
        from tutor.models import Material
        self._seed()
        m5 = Material.objects.get(title__startswith="Mission 5")
        html = render_to_string(
            "portal/_lesson_blocks.html", {"blocks": m5.blocks.order_by("order")})
        self.assertIn("Nisenan", html)                       # verbatim content preserved
        self.assertIn("factcards.califa.org", html)          # resource URL present (link + plain)
        self.assertIn("<a ", html)                            # rendered as a clickable link
        self.assertIn("Explorer's Log", html)                # RECAP now points to the journal

    def test_each_mission_has_an_explorers_log_journal(self):
        """The reflection the charter needs lives in a per-mission student journal —
        turning it in fires AI encouragement + a draft the parent stamps."""
        from tutor.models import Question, QuestionSet
        self._seed()
        curr = Curriculum.objects.get(name__startswith="Social Studies 3")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curr)
        self.assertEqual(sets.count(), 24)                    # one journal per mission
        self.assertTrue(all(s.status == QuestionSet.APPROVED for s in sets))
        self.assertTrue(all(s.mode == QuestionSet.MODE_STUDENT for s in sets))
        m1 = sets.get(title__startswith="Mission 1 ")
        prompts = " ".join(m1.questions.values_list("prompt", flat=True))
        self.assertIn("3 things I learned", prompts)          # the reflection moved here
        self.assertIn("log", prompts.lower())
        # + a short auto-check quiz on the mission's facts, in the same journal
        self.assertTrue(m1.questions.filter(
            response_type__in=[Question.TYPE_MATCHING, Question.TYPE_FILL_BLANK]).exists())


class WorldHistoryKaylinSeedTests(TestCase):
    """Kaylin's Grade 7 World History mission course: 32 missions across 10 units,
    each ending with dated timeline cards. Same in-app, no-AI pattern."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.parent = User.objects.create_user("whkaylin", email="whk@e.com", password="pw")
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07")

    def _seed(self):
        call_command("seed_ss_kaylin", stdout=StringIO())

    def test_seeds_ten_units_and_32_approved_missions(self):
        from curricula.models import Chapter, CurriculumPlacement
        from tutor.models import Material
        self._seed()
        curr = Curriculum.objects.get(name__startswith="World History 7")
        self.assertEqual(curr.grade_level, "G07")
        self.assertEqual(Chapter.objects.filter(curriculum=curr).count(), 10)
        self.assertEqual(Lesson.objects.filter(chapter__curriculum=curr).count(), 32)
        mats = Material.objects.filter(
            lesson__chapter__curriculum=curr, skill_type=Material.SKILL_LESSON)
        self.assertEqual(mats.count(), 32)
        self.assertTrue(all(m.status == Material.APPROVED for m in mats))
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.kaylin, curriculum=curr).exists())

    def test_missions_carry_dated_timeline_cards_in_completion(self):
        from tutor.models import LessonBlock, Material
        self._seed()
        m1 = Material.objects.get(title__startswith="Mission 1:")
        recap = m1.blocks.get(kind=LessonBlock.KIND_RECAP)
        joined = " ".join(recap.data["items"])
        self.assertIn("wall timeline", joined)               # the timeline-card completion step
        self.assertIn("476 CE", joined)                       # mission 1's dated card

    def test_a_mission_renders_verbatim(self):
        from django.template.loader import render_to_string
        from tutor.models import Material
        self._seed()
        m6 = Material.objects.get(title__startswith="Mission 6")
        html = render_to_string(
            "portal/_lesson_blocks.html", {"blocks": m6.blocks.order_by("order")})
        self.assertIn("House of Wisdom", html)               # verbatim content preserved
        self.assertIn("al-jabr", html)                        # the algebra tie-in

    def test_each_mission_has_a_history_log_journal(self):
        from tutor.models import Question, QuestionSet
        self._seed()
        curr = Curriculum.objects.get(name__startswith="World History 7")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curr)
        self.assertEqual(sets.count(), 32)                    # one journal per mission
        self.assertTrue(all(s.status == QuestionSet.APPROVED for s in sets))
        self.assertTrue(all(s.mode == QuestionSet.MODE_STUDENT for s in sets))
        m1 = sets.get(title__startswith="Mission 1 ")
        prompts = " ".join(m1.questions.values_list("prompt", flat=True))
        self.assertIn("Big Idea", prompts)                    # the reflection moved here
        self.assertIn("3 facts", prompts)
        self.assertTrue(m1.questions.filter(
            response_type__in=[Question.TYPE_MATCHING, Question.TYPE_FILL_BLANK]).exists())


class ScienceVioletSeedTests(TestCase):
    """Violet's Grade 3 Science mission course: household experiments, safety flags,
    no AI. Same in-app mission pattern (via _mission_seed)."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.parent = User.objects.create_user("sciviolet", email="sv@e.com", password="pw")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03")

    def _seed(self):
        call_command("seed_sci_violet", stdout=StringIO())

    def test_seeds_units_missions_and_approved_materials(self):
        from curricula.models import Chapter, CurriculumPlacement
        from tutor.models import Material
        self._seed()
        curr = Curriculum.objects.get(name__startswith="Science 3")
        self.assertEqual(curr.subject, "Science")
        self.assertEqual(Chapter.objects.filter(curriculum=curr).count(), 7)   # 6 units + capstone
        self.assertEqual(Lesson.objects.filter(chapter__curriculum=curr).count(), 26)
        mats = Material.objects.filter(
            lesson__chapter__curriculum=curr, skill_type=Material.SKILL_LESSON)
        self.assertEqual(mats.count(), 26)
        self.assertTrue(all(m.status == Material.APPROVED for m in mats))
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.violet, curriculum=curr).exists())

    def test_hot_water_mission_carries_the_adult_assist_and_safety_flags(self):
        from django.template.loader import render_to_string
        from tutor.models import Material
        self._seed()
        m22 = Material.objects.get(title__startswith="Mission 22")
        html = render_to_string(
            "portal/_lesson_blocks.html", {"blocks": m22.blocks.order_by("order")})
        self.assertIn("ADULT ASSIST", html)                  # the flagged safety banner
        self.assertIn("Safety", html)                         # standing safety rule on every card

    def test_a_mission_renders_verbatim(self):
        from django.template.loader import render_to_string
        from tutor.models import Material
        self._seed()
        m8 = Material.objects.get(title__startswith="Mission 8")
        html = render_to_string(
            "portal/_lesson_blocks.html", {"blocks": m8.blocks.order_by("order")})
        self.assertIn("compass", html.lower())               # verbatim content
        self.assertIn("Science Log", html)                    # RECAP now points to the journal

    def test_each_mission_has_a_science_log_journal(self):
        from tutor.models import Question, QuestionSet
        self._seed()
        curr = Curriculum.objects.get(name__startswith="Science 3")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curr)
        self.assertEqual(sets.count(), 26)                    # one journal per mission
        self.assertTrue(all(s.status == QuestionSet.APPROVED for s in sets))
        self.assertTrue(all(s.mode == QuestionSet.MODE_STUDENT for s in sets))
        m1 = sets.get(title__startswith="Mission 1 ")
        prompts = " ".join(m1.questions.values_list("prompt", flat=True))
        self.assertIn("3 things I learned", prompts)          # the reflection moved here
        self.assertIn("science log", prompts.lower())
        self.assertTrue(m1.questions.filter(
            response_type__in=[Question.TYPE_MATCHING, Question.TYPE_FILL_BLANK]).exists())

    def test_quiz_widgets_are_well_formed_and_self_checking(self):
        """A fill-blank blank splits on six underscores and every answer is in the
        word bank; a matching definition points at a real word — so the portal
        widgets render and self-check instead of silently degrading."""
        from tutor.models import Question
        self._seed()
        curr = Curriculum.objects.get(name__startswith="Science 3")
        fill = Question.objects.filter(
            question_set__lesson__chapter__curriculum=curr,
            response_type=Question.TYPE_FILL_BLANK).first()
        self.assertIsNotNone(fill)
        data = fill.vocab_data
        self.assertTrue(data.get("words"))
        self.assertTrue(data.get("sentences"))
        for s in data["sentences"]:
            self.assertIn("______", s["text"])               # widget splits the blank here
            self.assertIn(s["word"], data["words"])          # the answer is in the bank
        match = Question.objects.filter(
            question_set__lesson__chapter__curriculum=curr,
            response_type=Question.TYPE_MATCHING).first()
        self.assertIsNotNone(match)
        words = set(match.vocab_data["words"])
        self.assertTrue(words)
        for d in match.vocab_data["definitions"]:
            self.assertIn(d["word"], words)                  # each definition points at a real word


class ScienceKaylinSeedTests(TestCase):
    """Kaylin's Grade 7 Integrated Science: 30 missions, CER completion, PhET labs,
    adult-assist flags. Same in-app mission pattern."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.parent = User.objects.create_user("scikaylin", email="sk@e.com", password="pw")
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07")

    def _seed(self):
        call_command("seed_sci_kaylin", stdout=StringIO())

    def test_seeds_eight_units_and_30_approved_missions(self):
        from curricula.models import Chapter, CurriculumPlacement
        from tutor.models import Material
        self._seed()
        curr = Curriculum.objects.get(name__startswith="Science 7")
        self.assertEqual(curr.subject, "Science")
        self.assertEqual(curr.grade_level, "G07")
        self.assertEqual(Chapter.objects.filter(curriculum=curr).count(), 9)   # 8 units + capstone
        self.assertEqual(Lesson.objects.filter(chapter__curriculum=curr).count(), 30)
        mats = Material.objects.filter(
            lesson__chapter__curriculum=curr, skill_type=Material.SKILL_LESSON)
        self.assertEqual(mats.count(), 30)
        self.assertTrue(all(m.status == Material.APPROVED for m in mats))
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.kaylin, curriculum=curr).exists())

    def test_cer_completion_and_phet_digital_lab_render(self):
        from django.template.loader import render_to_string
        from tutor.models import Material
        self._seed()
        m1 = Material.objects.get(title__startswith="Mission 1:")
        html = render_to_string(
            "portal/_lesson_blocks.html", {"blocks": m1.blocks.order_by("order")})
        self.assertIn("Lab Notebook", html)                  # RECAP now points to the journal
        self.assertIn("phet.colorado.edu", html)              # PhET digital-lab link
        self.assertIn("<a ", html)                            # rendered as a clickable link
        self.assertIn('target="_blank"', html)                # external lab link opens in a new tab

    def test_each_mission_has_a_lab_notebook_journal(self):
        from tutor.models import Question, QuestionSet
        self._seed()
        curr = Curriculum.objects.get(name__startswith="Science 7")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curr)
        self.assertEqual(sets.count(), 30)                    # one journal per mission
        self.assertTrue(all(s.status == QuestionSet.APPROVED for s in sets))
        self.assertTrue(all(s.mode == QuestionSet.MODE_STUDENT for s in sets))
        m1 = sets.get(title__startswith="Mission 1 ")
        prompts = " ".join(m1.questions.values_list("prompt", flat=True))
        self.assertIn("I claim", prompts)                     # the CER frame moved here
        self.assertIn("3 facts", prompts)
        self.assertTrue(m1.questions.filter(
            response_type__in=[Question.TYPE_MATCHING, Question.TYPE_FILL_BLANK]).exists())

    def test_stove_mission_carries_the_adult_assist_flag(self):
        from django.template.loader import render_to_string
        from tutor.models import Material
        self._seed()
        m3 = Material.objects.get(title__startswith="Mission 3:")
        html = render_to_string(
            "portal/_lesson_blocks.html", {"blocks": m3.blocks.order_by("order")})
        self.assertIn("ADULT ASSIST", html)                  # the flagged stove safety banner


class LinkifySearchesTests(TestCase):
    """A "search X" hint becomes a clickable search link but keeps the phrase text
    visible as a fallback; existing links and "browse X" hints are left alone."""

    def _link(self, text):
        from tutor.management.commands._mission_seed import linkify_searches
        return linkify_searches(text)

    def test_search_phrase_becomes_a_link_that_keeps_the_text(self):
        out = self._link('Search "friction for kids video" (any short one).')
        self.assertIn("[friction for kids video]", out)      # phrase kept as the link label
        self.assertIn("youtube.com/results?search_query=friction+for+kids+video", out)
        self.assertIn("Search", out)                          # the instruction word stays

    def test_show_name_sharpens_the_query(self):
        out = self._link('**Crash Course World History #12 "Fall of the Roman Empire"** (YouTube).')
        self.assertIn("search_query=Crash+Course+World+History+Fall+of+the+Roman+Empire", out)

    def test_image_hint_uses_image_search(self):
        self.assertIn("tbm=isch", self._link('Search images: "Timbuktu manuscripts".'))

    def test_browse_section_on_a_linked_site_is_left_alone(self):
        raw = ('**NASA Climate Kids** — [climatekids.nasa.gov](https://climatekids.nasa.gov) '
               '(browse "Weather & Climate").')
        self.assertEqual(self._link(raw), raw)

    def test_plain_text_without_quotes_is_untouched(self):
        raw = "Nothing needed — the steps show the setup."
        self.assertEqual(self._link(raw), raw)


class FolkKeeperSeedTests(TestCase):
    """Kaylin's Blackbird 'The Folk Keeper' course: the guide's own four uneven
    sections plus a Glean week, discussion-heavy because Joyce leads it orally."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.parent = User.objects.create_user("fkmom", email="fk@e.com", password="pw")
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07")

    def _seed(self):
        call_command("seed_the_folk_keeper", "--for-user", "fkmom", stdout=StringIO())

    def test_seeds_the_guides_own_section_divisions(self):
        from curricula.models import Chapter, CurriculumPlacement
        self._seed()
        curr = Curriculum.objects.get(name__startswith="The Folk Keeper")
        self.assertEqual(curr.subject, "Literature")
        self.assertEqual(curr.grade_level, "G07")
        # Four reading sections + the Glean week; the reading sections are
        # deliberately uneven (4, 4, 3, 5 chapters) — that is the guide's split.
        chapters = list(Chapter.objects.filter(curriculum=curr).order_by("number"))
        self.assertEqual(len(chapters), 5)
        self.assertIn("1–4", chapters[0].title)
        self.assertIn("5–8", chapters[1].title)
        self.assertIn("9–11", chapters[2].title)
        self.assertIn("12–16", chapters[3].title)
        self.assertIn("Glean", chapters[4].title)
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.kaylin, curriculum=curr).exists())

    def test_every_section_carries_the_full_set_of_work(self):
        from tutor.models import QuestionSet
        self._seed()
        curr = Curriculum.objects.get(name__startswith="The Folk Keeper")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curr)
        # 4 x 6 + Glean + the hands-on Glean beside it.
        self.assertEqual(sets.count(), 26)
        for n in (1, 2, 3, 4):
            titles = set(sets.filter(lesson__chapter__number=n).values_list("title", flat=True))
            for kind in ("Journal", "Vocabulary", "Comprehension",
                         "Writing Exercise", "Discussion", "Socratic Seminar"):
                self.assertIn(f"Section {n} · {kind}", titles)
            # Six vocabulary words, then FIVE separate sentence boxes — the guide
            # prints five numbered lines, so the child gets five inputs, not one.
            vocab = sets.get(title=f"Section {n} · Vocabulary")
            self.assertEqual(vocab.questions.count(), 11)
            sentence_qs = vocab.questions.filter(prompt__contains="Sentence").order_by("order")
            self.assertEqual(sentence_qs.count(), 5)
            self.assertEqual(
                [q.prompt.split("**")[1] for q in sentence_qs],
                [f"Sentence {i} of 5" for i in range(1, 6)],
            )
            # Every one is its own plain typed box.
            self.assertTrue(all(q.response_type == Question.TYPE_TEXT for q in sentence_qs))
            # …and fourteen comprehension questions, every one answer-keyed.
            comp = sets.get(title=f"Section {n} · Comprehension")
            self.assertEqual(comp.questions.count(), 14)
            self.assertIn("answer key", comp.answer_key.lower())

    def test_discussion_and_seminar_are_oral_never_typed(self):
        """Joyce leads these with Kaylin — they must not land in the kid's portal
        as forms to fill in."""
        from tutor.models import QuestionSet
        self._seed()
        curr = Curriculum.objects.get(name__startswith="The Folk Keeper")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curr)
        oral = sets.filter(mode=QuestionSet.MODE_DISCUSSION)
        self.assertEqual(oral.count(), 8)                     # a Discussion + a Seminar per section
        for s in oral:
            self.assertTrue(
                s.title.endswith("Discussion") or s.title.endswith("Socratic Seminar"), s.title)
        # Everything else is the child's own work — 17, plus the hands-on final
        # project, which is hers to do alone and so is a student set too.
        self.assertEqual(sets.filter(mode=QuestionSet.MODE_STUDENT).count(), 18)

    def test_answer_key_content_matches_the_publishers_key(self):
        from tutor.models import QuestionSet
        self._seed()
        curr = Curriculum.objects.get(name__startswith="The Folk Keeper")
        s1 = QuestionSet.objects.get(
            lesson__chapter__curriculum=curr, title="Section 1 · Comprehension")
        self.assertIn("steal Matron's breakfast sausage", s1.answer_key)
        self.assertIn("cannot bear the light", s1.answer_key)
        s4 = QuestionSet.objects.get(
            lesson__chapter__curriculum=curr, title="Section 4 · Comprehension")
        self.assertIn("amber beads", s4.answer_key)           # Taffy's grave
        # Vocabulary keys carry the publisher's definitions, teacher-side only.
        v3 = QuestionSet.objects.get(
            lesson__chapter__curriculum=curr, title="Section 3 · Vocabulary")
        self.assertIn("unable to be placated", v3.answer_key)  # implacable
        self.assertIn("teacher reference only", v3.answer_key)

    def test_teacher_only_answer_key_link_is_attached(self):
        from curricula.models import CurriculumResource
        self._seed()
        curr = Curriculum.objects.get(name__startswith="The Folk Keeper")
        res = CurriculumResource.objects.get(curriculum=curr)
        self.assertTrue(res.teacher_only)
        self.assertIn("the-folk-keeper", res.url)

    def test_is_idempotent(self):
        from tutor.models import QuestionSet
        self._seed()
        self._seed()
        curr = Curriculum.objects.get(name__startswith="The Folk Keeper")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curr)
        # 25, plus the hands-on final project beside the guide's own.
        self.assertEqual(sets.count(), 26)
        self.assertEqual(sum(s.questions.count() for s in sets), 194)
        gleans = sets.filter(title__contains="Glean")
        self.assertEqual(gleans.count(), 2)
        self.assertTrue(gleans.filter(title__endswith="Final Project").exists(),
                        "the guide's own options must still be offered")


class EIWLessonTenTests(SimpleTestCase):
    """Lesson 10 (Pronouns and Antecedents) against the printed workbook, pp.35-41.

    Every exercise here used to seed as "Mark the sentences (n)", so the child
    opening her list could not tell underline-the-pronouns from
    circle-the-antecedents from rewrite-the-sentence — and two rewrite exercises
    handed her a drawing pen for a task the workbook asks her to write out.
    """

    @property
    def blocks(self):
        from tutor.management.commands._eiw_content import EXERCISES
        return EXERCISES[10]

    def test_every_workbook_page_is_present(self):
        """p.41 (Complete Assessment 4) was missing entirely, so the lesson
        stopped one exercise short of the book."""
        pages = [b["workbook_page"] for b in self.blocks]
        self.assertEqual(pages, [35, 35, 36, 37, 37, 38, 39, 40, 41])
        self.assertTrue(any(b["assessment"] for b in self.blocks))

    def test_each_exercise_names_the_action_it_wants(self):
        labels = [b["label"] for b in self.blocks]
        self.assertEqual(len(labels), len(set(labels)), "duplicate labels are the bug")
        for b in self.blocks:
            verb = b["instructions"].split()[0].strip("*").lower()
            self.assertIn(verb, {"underline", "circle", "rewrite", "read", "write"})
            # The label has to carry the action too — it is what she reads in the list.
            self.assertRegex(b["label"].lower(), r"underline|circle|rewrite|missing|write")

    def test_rewrite_exercises_are_typed_not_drawn(self):
        """A pen tool cannot rewrite a sentence."""
        for b in self.blocks:
            if b["instructions"].lower().startswith("rewrite"):
                self.assertNotEqual(b["kind"], "sentence-editing", b["label"])

    def test_marking_exercises_stay_drawable(self):
        for b in self.blocks:
            first = b["instructions"].split()[0].lower()
            if first in ("underline", "circle"):
                self.assertEqual(b["kind"], "sentence-editing", b["label"])

    def test_the_words_to_replace_are_marked(self):
        """The workbook underlines the nouns to swap out; without that the
        rewrite exercises are ambiguous."""
        for b in self.blocks:
            if "underlined" in b["instructions"]:
                for item in b["items"]:
                    self.assertIn("<u>", item, b["label"])

    def test_the_pronoun_chart_is_exactly_the_workbook_list(self):
        import re
        from tutor.management.commands._eiw_content import pronoun_list_html
        printed = "I me my you your he they them their our we us him his she her it its"
        shown = re.findall(r">([A-Za-z]+)</span>", pronoun_list_html())
        self.assertEqual(
            sorted({w.lower() for w in shown}),
            sorted({w.lower() for w in printed.split()}),
        )

    def test_the_worked_example_shows_both_marks(self):
        from tutor.management.commands._eiw_content import antecedent_model_html
        html = antecedent_model_html("Tyrone", "made a cake.", "He", "made a cake.")
        self.assertIn("border-radius:999px", html)   # circled antecedent
        self.assertIn("border-bottom", html)         # underlined pronoun
        self.assertIn("antecedent", html)
        self.assertIn("pronoun", html)

    def test_the_instruction_comes_first_in_what_she_reads(self):
        from tutor.management.commands.seed_eiw_violet import build_intro
        intro = build_intro(self.blocks[0], wants_pen_hint=True)
        self.assertTrue(intro.startswith("**Underline the pronouns.**"), intro[:80])
        self.assertLess(intro.index("Underline the pronouns"), intro.index("List of Pronouns"))


class MarkupSurfaceRecordedTests(SimpleTestCase):
    """BOTH drawing widgets must record the surface they were drawn on.

    There are two: portal-markup.js (draw on a printed sentence) and
    portal-writemarkup.js (type your own sentence, then draw on it). They have
    separate persist() functions, and teaching only one of them to record the
    surface is silent — the replay still renders, it just rebuilds the box at a
    guessed width, re-wraps the sentence, and puts her underline under a
    different word than the one she marked. Worse than showing nothing.
    """

    WIDGETS = ["static/js/portal-markup.js", "static/js/portal-writemarkup.js"]

    def test_both_widgets_record_the_surface_size(self):
        from django.contrib.staticfiles import finders
        for path in self.WIDGETS:
            src = open(finders.find(path.split("static/", 1)[1]), encoding="utf-8").read()
            self.assertIn("surface:", src, path)
            self.assertIn("getBoundingClientRect", src, path)
            # Width AND height — the width is what fixes the wrap, but the
            # height keeps the box the shape she drew in.
            self.assertRegex(src, r"w:\s*Math\.round", path)
            self.assertRegex(src, r"h:\s*Math\.round", path)

    def test_the_replay_treats_a_missing_surface_as_a_guess(self):
        """So that forgetting the JS half shows the caveat rather than passing a
        misaligned drawing off as exact."""
        from tutor.markup import replay_for
        from tutor.models import Question
        import json
        q = Question(response_type=Question.TYPE_WRITE_MARKUP, passage="")
        raw = json.dumps({"text": "My dog is soft.",
                          "strokes": [{"c": "#333333", "w": 3, "p": [[0.1, 0.5], [0.3, 0.5]]}]})
        self.assertFalse(replay_for(raw, q).exact)


class CharterReportMarkupTests(TestCase):
    """The charter report is the surface this feature exists for — the packet
    South Sutter is shown at the Learning Record Meeting. A work sample of a
    mark-the-sentence exercise has to carry the actual circles and underlines."""

    @classmethod
    def setUpTestData(cls):
        import json
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from core.models import Family, FamilyMembership
        from curricula.models import Chapter, Curriculum, Lesson
        from students.models import Student
        from tutor.models import Question, QuestionSet, ResponseSheet
        from worklog.models import WorkLogEntry
        from tutor.models import Question, QuestionSet, ResponseSheet

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="chp", email="chp@e.com", password="pw")
        cls.family = Family.objects.create(name="Charter Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cur = Curriculum.objects.create(
            parent=cls.parent, family=cls.family, name="Writing", subject="Writing")
        chap = Chapter.objects.create(curriculum=cur, number=1, title="Pronouns")
        lesson = Lesson.objects.create(chapter=chap, order=1, number=1, title="Pronouns")
        qset = QuestionSet.objects.create(
            lesson=lesson, title="Underline the pronouns", family=cls.family,
            status=QuestionSet.APPROVED)
        q = Question.objects.create(
            question_set=qset, order=1, category="editing",
            response_type=Question.TYPE_MARKUP,
            passage="Jim sang a song. It was so pretty!")
        entry = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.child, family=cls.family, curriculum=cur,
            subject="Writing", date=timezone.localdate(), description="Lesson 10")
        ResponseSheet.objects.create(
            question_set=qset, child=cls.child, work_entry=entry,
            submitted_at=timezone.now(),
            answers={str(q.pk): json.dumps({
                "strokes": [{"c": "#2b6cb0", "w": 3, "p": [[0.34, 0.73], [0.37, 0.73]]}],
                "marks": [{"word": "It", "kind": "underlined"}],
                "unread": 0,
                "surface": {"w": 702, "h": 74},
            })},
        )

    def test_the_report_carries_the_drawing(self):
        self.client.login(username="chp", password="pw")
        resp = self.client.get(reverse("worklog:charter_report"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<polyline")
        self.assertContains(resp, "#2b6cb0")
        self.assertContains(resp, "--mr-w:702px")
        self.assertContains(resp, "Read as:")

    def test_the_report_asks_for_its_own_print_scale(self):
        """Print gets a narrower column than the screen. One shared scale plus
        overflow:hidden is what silently cropped a quarter off every printed
        drawing, so the print size must reach the page separately."""
        self.client.login(username="chp", password="pw")
        resp = self.client.get(reverse("worklog:charter_report"))
        self.assertContains(resp, "--mr-print-scale:")
        self.assertContains(resp, "--mr-print-w:")
        self.assertContains(resp, "css/markup-replay.")

    def test_the_stylesheet_gives_print_its_own_rules(self):
        """Guards the two lines that make it print: the container override and
        the print-specific scale. Both are invisible on screen."""
        from django.contrib.staticfiles import finders
        css = open(finders.find("css/markup-replay.css"), encoding="utf-8").read()
        media = css[css.index("@media print"):]
        self.assertIn("max-width: 100%", media)          # Bootstrap .container in print
        self.assertIn("--mr-print-scale", media)
        self.assertNotIn("overflow: hidden", css)        # clipping is the bug


class MarkupReplayTests(SimpleTestCase):
    """Her drawn work has to survive out of the portal and onto a printed page.

    Reports used to show the sentence and a line of prose about it ("she
    underlined 'It'"). For a mark-the-sentence exercise the marks ARE the work,
    so a report without them isn't a report of that exercise.
    """

    def _q(self, passage="Jim sang a song. It was so pretty!", write=False):
        from tutor.models import Question
        return Question(
            response_type=Question.TYPE_WRITE_MARKUP if write else Question.TYPE_MARKUP,
            passage="" if write else passage,
        )

    def _answer(self, **over):
        data = {
            "strokes": [{"c": "#2b6cb0", "w": 3, "p": [[0.1, 0.5], [0.3, 0.5]]}],
            "marks": [{"word": "It", "kind": "underlined"}],
            "unread": 0,
        }
        data.update(over)
        return json.dumps(data)

    def test_the_strokes_reach_the_page_as_drawable_svg(self):
        from tutor.markup import replay_for
        r = replay_for(self._answer(), self._q())
        self.assertTrue(r.has_drawing)
        self.assertIn("<polyline", r.svg)
        self.assertIn("#2b6cb0", r.svg)
        # Normalized 0..1 scaled into the viewBox — 0.1 -> 100, 0.3 -> 300.
        self.assertIn("100.0,500.0 300.0,500.0", r.svg)
        self.assertIn('preserveAspectRatio="none"', r.svg)
        self.assertIn("non-scaling-stroke", r.svg)   # pen stays a pen when stretched

    def test_the_sentence_comes_back_word_by_word(self):
        from tutor.markup import replay_for
        r = replay_for(self._answer(), self._q())
        words = [w["text"] for line in r.lines for w in line]
        self.assertEqual(words[:4], ["Jim", "sang", "a", "song."])

    def test_a_typed_sentence_is_reproduced_exactly_as_she_typed_it(self):
        """She wrote it herself, so it lives in the answer, not the question —
        and it is mirrored into the portal's drawing surface verbatim under
        white-space:pre-wrap. Re-joining it on whitespace would shift every word
        after a double space out from under her marks."""
        from tutor.markup import replay_for
        typed = "My dog is soft.  He naps a lot."
        r = replay_for(self._answer(text=typed), self._q(write=True))
        self.assertTrue(r.typed)
        self.assertEqual(r.text, typed)          # both spaces survive
        self.assertEqual(r.lines, [])            # not rebuilt from words

    def test_a_printed_passage_is_rebuilt_from_its_words(self):
        from tutor.markup import replay_for
        r = replay_for(self._answer(), self._q())
        self.assertFalse(r.typed)
        self.assertIn("Jim", [w["text"] for line in r.lines for w in line])

    def test_nothing_drawn_means_nothing_to_replay(self):
        from tutor.markup import replay_for
        for raw in ("", "not json", "[]", json.dumps({"strokes": []}), json.dumps({})):
            self.assertIsNone(replay_for(raw, self._q()), raw)

    def test_pre_marks_answers_still_replay(self):
        """The oldest answers are a bare stroke list. The drawing is still hers."""
        from tutor.markup import replay_for
        raw = json.dumps([{"c": "#333333", "w": 3, "p": [[0.2, 0.4], [0.6, 0.4]]}])
        r = replay_for(raw, self._q())
        self.assertTrue(r.has_drawing)
        self.assertEqual(r.summary, "")      # nothing can be named, and it says so

    def test_a_single_tap_still_draws(self):
        from tutor.markup import replay_for
        raw = self._answer(strokes=[{"c": "#333333", "w": 3, "p": [[0.5, 0.5]]}])
        self.assertIn("<polyline", replay_for(raw, self._q()).svg)

    def test_the_reading_is_shown_next_to_the_drawing(self):
        from tutor.markup import replay_for
        raw = self._answer(marks=[{"word": "It", "kind": "underlined"},
                                  {"word": "Jim", "kind": "circled"}])
        s = replay_for(raw, self._q()).summary
        self.assertIn("underlined", s)
        self.assertIn("circled", s)
        self.assertIn("Jim", s)

    def test_unreadable_marks_are_declared_not_hidden(self):
        from tutor.markup import replay_for
        raw = self._answer(unread=2)
        self.assertIn("2 more mark", replay_for(raw, self._q()).summary)

    def test_a_hostile_colour_cannot_escape_into_the_page(self):
        """Answers are child-supplied JSON and the colour lands, via mark_safe,
        straight into an SVG attribute.

        The probes deliberately include values with a VALID hex prefix and
        trailing junk: drop the anchors on the colour pattern and those match,
        carrying the payload into the attribute. An oracle of "no <script>"
        would not notice, since an event handler needs no script tag — so this
        asserts the whole attribute instead."""
        from tutor.markup import replay_for
        hostile = [
            '"><script>alert(1)</script>',
            "url(javascript:alert(1))",
            "red; x",
            None,
            "#333 onmouseover=alert(document.cookie) x=",
            '#333333" onload="alert(1)',
            '#fff\n" onload="x',
            "&#106;avascript:alert(1)",
            "\uff03\uff46\uff46\uff46",
            "#333333;background:url(x)",
            ["#ff0000"],
            {"c": "#ff0000"},
            True,
            "#" + "f" * 5000,
        ]
        for bad in hostile:
            svg = replay_for(
                self._answer(strokes=[{"c": bad, "w": 3, "p": [[0, 0], [1, 1]]}]),
                self._q(),
            ).svg
            self.assertIn('stroke="#333333"', svg, repr(bad))
            for probe in ("script", "onload", "onmouseover", "javascript:", "&#"):
                self.assertNotIn(probe, svg.lower(), repr(bad))
            self.assertEqual(svg.count('stroke="'), 1, repr(bad))

    def test_a_valid_colour_is_kept_exactly(self):
        """The guard must not be a blanket rewrite — her pen colours are the work."""
        from tutor.markup import replay_for
        for good in ("#2b6cb0", "#d64545", "#1E7A50", "#333333", "#abc"):
            svg = replay_for(
                self._answer(strokes=[{"c": good, "w": 3, "p": [[0, 0], [1, 1]]}]),
                self._q(),
            ).svg
            self.assertIn('stroke="' + good + '"', svg)

    def test_a_width_cannot_blow_the_page_up(self):
        from tutor.markup import replay_for
        cases = [(9e9, "12.0"), (float("inf"), "12.0"), (-5, "1.0"),
                 ("1e400", "12.0"), (float("nan"), "3.0")]
        for bad, want in cases:
            raw = self._answer(strokes=[{"c": "#333333", "w": bad, "p": [[0, 0], [1, 1]]}])
            self.assertIn('stroke-width="' + want + '"',
                          replay_for(raw, self._q()).svg, repr(bad))

    def test_an_enormous_answer_cannot_produce_an_unopenable_page(self):
        """Autosave stores whatever the client posts, and one stored byte fans out
        into many bytes of SVG path text. The charter report loops over every
        entry, so an unbounded answer is an unopenable report, not a big drawing."""
        from tutor.markup import replay_for, MAX_STROKES, MAX_POINTS
        raw = self._answer(strokes=[
            {"c": "#333333", "w": 3, "p": [[i / 5000, 0.5] for i in range(5000)]}
            for _ in range(MAX_STROKES + 50)
        ])
        svg = replay_for(raw, self._q()).svg
        self.assertEqual(svg.count("<polyline"), MAX_STROKES)
        # Points are capped per stroke too, so one gigantic stroke cannot
        # sidestep the stroke cap.
        first = svg.split('points="')[1].split('"')[0]
        self.assertLessEqual(len(first.split()), MAX_POINTS)

    def test_infinite_and_giant_coordinates_never_reach_the_path(self):
        """inf formats as the literal "inf"; 1e300 as 300-odd digits."""
        from tutor.markup import replay_for
        raw = self._answer(strokes=[{"c": "#333333", "w": 3, "p": [
            [float("inf"), 0.5], [-float("inf"), 0.5], [1e300, 1e300], [0.5, 0.5],
        ]}])
        svg = replay_for(raw, self._q()).svg
        self.assertNotIn("inf", svg.lower())
        self.assertNotIn("e+", svg.lower())
        for chunk in svg.split('points="')[1].split('"')[0].split():
            for n in chunk.split(","):
                self.assertLess(len(n), 10, n)

    def test_garbage_points_are_skipped_not_fatal(self):
        from tutor.markup import replay_for
        raw = self._answer(strokes=[
            {"c": "#333333", "w": 3, "p": [["x", "y"], [0.2, 0.2], None, [0.4, 0.4]]},
        ])
        svg = replay_for(raw, self._q()).svg
        self.assertIn("200.0,200.0 400.0,400.0", svg)

    def test_junk_in_place_of_a_stroke_path_does_not_500_the_report(self):
        """`p` is child-supplied and stored verbatim by autosave. An int slices
        with TypeError and a dict with KeyError, and one poisoned row would take
        down the whole charter report for that date range."""
        from tutor.markup import replay_for
        for bad in (5, True, {"0": 1}, "x", None, 3.5):
            raw = self._answer(strokes=[{"c": "#333333", "w": 3, "p": bad}])
            self.assertIsNone(replay_for(raw, self._q()), repr(bad))
        # A good stroke beside a bad one still draws.
        raw = self._answer(strokes=[
            {"c": "#333333", "w": 3, "p": 5},
            {"c": "#333333", "w": 3, "p": [[0.1, 0.5], [0.3, 0.5]]},
        ])
        self.assertEqual(replay_for(raw, self._q()).svg.count("<polyline"), 1)

    def test_junk_in_place_of_marks_does_not_500_the_report(self):
        from tutor.markup import replay_for
        for bad in (5, True, "x", {"a": 1}):
            raw = self._answer(marks=bad)
            r = replay_for(raw, self._q())
            self.assertIsNotNone(r, repr(bad))
            self.assertEqual(r.summary, "", repr(bad))

    def test_unreadable_marks_are_reported_even_when_none_could_be_named(self):
        """Silence here reads as "she marked nothing", the opposite of the truth."""
        from tutor.markup import replay_for
        raw = self._answer(marks=[], unread=3)
        self.assertIn("3 mark", replay_for(raw, self._q()).summary)

    # Heights measured in Chrome against the real markup-replay.css at the
    # legacy width (700px), which is the only width this path ever uses. The
    # estimate must be >= actual: too short clips the sentence behind a
    # scrollbar on screen and prints it on top of the caption.
    HEIGHT_CASES = [
        ("lowercase", 168,
         "Callie and John are siblings. They are my friends, and they both play "
         "the piano. Callie likes to play rag music."),
        # A single average char width tuned to lowercase under-counts these by a
        # third: Georgia runs 5px (l) to 23px (W).
        ("uppercase", 168,
         "A BIG STORM BLEW THROUGH A SMALL TOWN AND THE WIND KNOCKED DOWN THREE "
         "OLD TREES ON THE MAIN ROAD NEAR THE SCHOOL"),
        ("child typing in caps", 168,
         "I WENT TO THE ZOO WITH MY MOM AND MY DAD AND WE SAW A BIG LION AND "
         "MANY BIRDS!"),
        ("widest glyphs", 120, "WWWWW MMMMM WWWWW MMMMM WWWWW MMMMM WWWWW MMMMM WWWWW MMMMM"),
        ("explicit newlines", 216, "One line.\nTwo line.\nThree line.\nFour line."),
        ("narrow glyphs", 72, "iiiii iiiii iiiii iiiii iiiii iiiii iiiii iiiii iiiii iiiii iiiii iiiii"),
        ("short", 72, "The cat sat."),
        # Breaks between characters rather than at spaces.
        ("emoji", 168, "\U0001F600" * 40),
        # Does not break mid-word; overflows on one line, as the portal does.
        ("unbreakable run", 72, "supercalifragilisticexpialidociousandthensome"),
    ]

    def test_a_legacy_box_is_tall_enough_for_its_text(self):
        from tutor.markup import replay_for
        for name, actual_px, text in self.HEIGHT_CASES:
            r = replay_for(self._answer(text=text), self._q(write=True))
            self.assertGreaterEqual(
                r.height, actual_px,
                f"{name}: box {r.height}px is shorter than the {actual_px}px the "
                f"browser needs — the sentence gets clipped",
            )
            # And not absurdly generous, or the page fills with empty boxes.
            self.assertLess(r.height, actual_px + 120, name)

    # Measured the same way as HEIGHT_CASES. None of these is reachable from
    # real content — the passages are seeded ASCII and a Tab keypress moves focus
    # rather than inserting a character — but the estimate has to be an upper
    # bound for every input, not only the plausible ones.
    HOSTILE_HEIGHT_CASES = [
        # Tab is a BREAK OPPORTUNITY, so splitting on spaces alone treated this
        # as one unbreakable run and under-counted it.
        ("tab separated", 120, "Word\there\tand\tmore\twords\tacross\tthe\tline\there"),
        # Leading whitespace still occupies width under pre-wrap.
        ("leading tabs", 120, "\t\t\t\t\t\t\t\tindented deeply after eight tabs on this line"),
        ("control chars", 216,
         "".join(chr(c) for c in range(1, 32)) + " visible text after controls"),
        ("nbsp joined", 120, "one\u00a0two\u00a0three\u00a0four\u00a0five\u00a0six\u00a0seven\u00a0eight\u00a0nine\u00a0ten"),
        ("combining accents", 72, "e\u0301" * 60),
        ("thai, no spaces", 72, "\u0e2a\u0e27\u0e31\u0e2a\u0e14\u0e35\u0e04\u0e23\u0e31\u0e1a\u0e19\u0e35\u0e48\u0e04\u0e37\u0e2d\u0e02\u0e49\u0e2d\u0e04\u0e27\u0e32\u0e21\u0e17\u0e14\u0e2a\u0e2d\u0e1a"),
        ("zwj family emoji", 264, "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466" * 10),
        ("skin tone emoji", 168, "\U0001F44D\U0001F3FD" * 25),
        ("very long", 1320, "the quick brown fox jumps over the lazy dog " * 30),
        ("many spaces", 120, "a" + "  " * 80 + "b"),
        ("double spaces", 120,
         "The  cat  sat  on  the  mat  and  then  the  dog  came  over  to  play  too"),
    ]

    def test_a_legacy_box_holds_hostile_text_too(self):
        from tutor.markup import replay_for
        for name, actual_px, text in self.HOSTILE_HEIGHT_CASES:
            r = replay_for(self._answer(text=text), self._q(write=True))
            self.assertGreaterEqual(
                r.height, actual_px,
                f"{name}: box {r.height}px is shorter than the {actual_px}px the "
                f"browser needs — the text gets clipped",
            )

    def test_the_line_estimate_beats_a_single_average_char_width(self):
        """Guards the specific regression: an average tuned to lowercase.

        Same word count, same character count — only the case differs. Any model
        using one width per character gives these the same height, and the
        upper-case one then clips."""
        from tutor.markup import replay_for
        lower = ("the quick brown fox jumps over the lazy dog while nine happy "
                 "children watch from the green hill")
        upper = lower.upper()
        low = replay_for(self._answer(text=lower), self._q(write=True)).height
        up = replay_for(self._answer(text=upper), self._q(write=True)).height
        self.assertEqual(len(lower), len(upper))
        self.assertGreater(up, low)

    def test_an_answer_with_no_recorded_size_is_not_pinned_to_a_guessed_box(self):
        """Every answer that predates surface recording takes this path. A pinned
        box that is too short hides the end of a long sentence on screen and
        prints it over the caption, so these size to their own text instead."""
        from tutor.markup import replay_for
        r = replay_for(self._answer(surface=None), self._q())
        self.assertFalse(r.exact)

    def test_the_surface_is_rebuilt_at_the_width_she_drew_on(self):
        """Normalized strokes only land right at the ORIGINAL pixel width.

        The type is sized in absolute pixels, so a box of the same aspect but a
        different width re-wraps the sentence and moves the words out from under
        her marks."""
        from tutor.markup import replay_for, SCREEN_TARGET, PRINT_TARGET
        r = replay_for(self._answer(surface={"w": 900, "h": 260}), self._q())
        self.assertTrue(r.exact)
        self.assertEqual((r.width, r.height), (900, 260))
        self.assertIn("--mr-w:900px;--mr-h:260px", r.style_vars)
        # Too wide for either column, so the whole surface scales down as a unit.
        self.assertAlmostEqual(r.scale, SCREEN_TARGET / 900, places=4)
        self.assertAlmostEqual(r.print_scale, PRINT_TARGET / 900, places=4)
        # Print gets its OWN scale, independent of the screen's: one shared
        # number is what cropped every printed drawing.
        self.assertNotEqual(r.print_scale, r.scale)
        # Both contexts reserve their post-scale footprint; a transform doesn't.
        self.assertIn(f"--mr-fit-h:{round(260 * r.scale)}px", r.style_vars)
        self.assertIn(f"--mr-print-h:{round(260 * r.print_scale)}px", r.style_vars)

    def test_a_small_drawing_is_never_blown_up(self):
        from tutor.markup import replay_for
        r = replay_for(self._answer(surface={"w": 320, "h": 110}), self._q())
        self.assertEqual(r.scale, 1.0)
        self.assertEqual(r.print_scale, 1.0)
        self.assertIn("--mr-scale:1.0000", r.style_vars)

    def test_answers_drawn_before_the_size_was_recorded_say_so(self):
        """Any width is a guess for these, and the page admits it rather than
        presenting a misaligned drawing as exact."""
        from tutor.markup import replay_for
        for surface in (None, {}, {"w": 0, "h": 0}, {"w": "wide", "h": 3}, {"w": 9e9, "h": 9e9}):
            r = replay_for(self._answer(surface=surface), self._q())
            self.assertFalse(r.exact, surface)
            self.assertTrue(r.width > 0 and r.height > 0)


class LexiconContentTests(SimpleTestCase):
    """Operation Lexicon against the printed guide.

    Every answer must be one of that week's ten words: the exercise is choosing
    between ten plausible traits, so an answer outside the list makes the
    question unanswerable rather than merely hard.
    """

    @property
    def weeks(self):
        from tutor.lexicon import WEEKS
        return WEEKS

    def test_ten_weeks_ten_words_ten_sentences(self):
        self.assertEqual(len(self.weeks), 10)
        for wk in self.weeks:
            self.assertEqual(len(wk["words"]), 10, wk["number"])
            self.assertEqual(len(wk["sentences"]), 10, wk["number"])

    def test_it_is_a_hundred_words(self):
        """The guide promises a hundred. It repeats "meticulous" across weeks 5
        and 9, which is the publisher's own doing — so 100 entries, 99 distinct.
        Asserting only the list length would hide a transcription slip that
        duplicated a word by accident."""
        from collections import Counter
        from tutor.lexicon import all_words
        counts = Counter(all_words())
        self.assertEqual(len(all_words()), 100)
        self.assertEqual(len(counts), 99)
        self.assertEqual([w for w, n in counts.items() if n > 1], ["meticulous"])

    def test_every_answer_is_one_of_that_weeks_words(self):
        for wk in self.weeks:
            words = {w for w, _d in wk["words"]}
            answers = {a for _t, a in wk["sentences"]}
            self.assertEqual(answers, words, f"week {wk['number']}")

    def test_no_word_is_used_for_two_sentences_in_a_week(self):
        """Ten words, ten sentences, one each — otherwise one word has no home."""
        for wk in self.weeks:
            answers = [a for _t, a in wk["sentences"]]
            self.assertEqual(len(answers), len(set(answers)), f"week {wk['number']}")

    def test_every_sentence_has_somewhere_to_write(self):
        for wk in self.weeks:
            for text, _a in wk["sentences"]:
                self.assertIn("_____", text, f"week {wk['number']}: {text[:40]}")

    def test_every_word_has_a_definition(self):
        for wk in self.weeks:
            for word, definition in wk["words"]:
                self.assertTrue(definition.strip(), f"{word} has no definition")
                self.assertTrue(definition.rstrip().endswith("."), word)

    def test_every_week_names_its_book(self):
        """The words are anchored to a story; without the book they're a list."""
        for wk in self.weeks:
            for field in ("person", "role", "book", "author"):
                self.assertTrue(wk[field].strip(), f"week {wk['number']} {field}")


class HandwritingTests(TestCase):
    """Writing by hand, not typing.

    A third grader practising writing should be forming letters. Typing these
    would swap the skill for keyboard hunting.
    """

    @classmethod
    def setUpTestData(cls):
        import json
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from curricula.models import Chapter, Curriculum, Lesson
        from students.models import Student
        from tutor.models import Question, QuestionSet, ResponseSheet

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="hw", email="hw@e.com", password="pw")
        cls.family = Family.objects.create(name="HW Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        from curricula.models import CurriculumPlacement

        cur = Curriculum.objects.create(
            parent=cls.parent, family=cls.family, name="Lexicon", subject="Language Arts")
        chap = Chapter.objects.create(curriculum=cur, number=1, title="Traits")
        # Shared (not child-pinned) work is only visible through a placement —
        # the portal's own gate, so the fixture has to place her.
        CurriculumPlacement.objects.create(child=cls.child, curriculum=cur)
        cls.lesson = Lesson.objects.create(chapter=chap, order=1, number=1, title="Erdős")
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="What amazed you?", family=cls.family,
            status=QuestionSet.APPROVED)
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="writing",
            response_type=Question.TYPE_HANDWRITING, prompt="Amazing thing #1")
        cls.answer = json.dumps({
            "strokes": [{"c": "#1d3557", "w": 3, "p": [[0.05, 0.2], [0.4, 0.22]]}],
            "surface": {"w": 702, "h": 192},
        })

    def test_a_handwritten_answer_is_not_reported_as_blank(self):
        """"(no answer)" against a full page of writing would mark her down for
        work she actually did."""
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.child,
            answers={str(self.q.pk): self.answer})
        display = sheet.answer_display(self.q)
        self.assertNotIn("no answer", display.lower())
        self.assertIn("handwritten", display.lower())

    def test_writing_nothing_still_reads_as_nothing(self):
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.child, answers={str(self.q.pk): ""})
        self.assertIn("nothing written", sheet.answer_display(self.q).lower())

    def test_her_handwriting_replays_for_the_parent(self):
        """The whole point: the parent and the charter report see the writing."""
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.child,
            answers={str(self.q.pk): self.answer})
        replay = sheet.answer_replay(self.q)
        self.assertIsNotNone(replay)
        self.assertTrue(replay.has_drawing)
        self.assertTrue(replay.exact)               # surface size was recorded
        self.assertEqual((replay.width, replay.height), (702, 192))
        self.assertIn("#1d3557", replay.svg)

    def test_the_portal_gives_her_a_pen_not_a_keyboard(self):
        from portal.tokens import make_portal_token
        token = make_portal_token(self.child)
        resp = self.client.get(
            reverse("portal:portal_questions", args=[token, self.qset.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "handwriting-canvas")
        self.assertContains(resp, "js/portal-handwriting.")
        # No typing box for THIS question — typing is the thing we're avoiding.
        # Asserting on the raw class string would pass even if a textarea were
        # rendered (the template emits it followed by a newline, not a space),
        # so count the widgets instead: one handwriting canvas, no answer boxes.
        html = resp.content.decode()
        self.assertEqual(html.count("handwriting-canvas"), 1)
        self.assertEqual(html.count("portal-answer"), 0)

    def test_an_emptied_drawing_is_not_read_back_as_her_answer(self):
        """_parse_markup accepts a bare array as a legacy stroke shape, so
        checking only the first character would hand "[]" or "null" to the
        grader and the report as if she had written that."""
        for payload in ("[]", "null", '{"strokes": [], "surface": null}'):
            with self.subTest(payload=payload):
                sheet = ResponseSheet.objects.create(
                    question_set=self.qset, child=self.child,
                    answers={str(self.q.pk): payload})
                self.assertEqual(sheet.answer_display(self.q),
                                 "(nothing written yet)")
                sheet.delete()

    def test_words_she_typed_before_the_switch_are_not_lost(self):
        """A question can change instrument under an answer she already gave —
        Lexicon's three boxes were typed for a few days. Reading her sentence
        back as "(nothing written yet)" would hide real work from the grader,
        the parent's work browser and the printed report."""
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.child,
            answers={str(self.q.pk): "I never knew Kandinsky could hear colours."})
        self.assertEqual(sheet.answer_display(self.q),
                         "I never knew Kandinsky could hear colours.")
        self.assertIsNone(sheet.answer_replay(self.q))   # there is nothing to draw

    def test_a_typed_question_is_untouched(self):
        typed = Question.objects.create(
            question_set=self.qset, order=2, category="writing",
            response_type=Question.TYPE_TEXT, prompt="Type this one")
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.child,
            answers={str(typed.pk): "I typed my answer."})
        self.assertEqual(sheet.answer_display(typed), "I typed my answer.")
        self.assertIsNone(sheet.answer_replay(typed))


class HandwritingGradingTests(HandwritingTests):
    """The AI must not score writing it cannot see.

    The rubric asks for complete sentences and a real thought. Handed
    "[handwritten answer — 2 pen stroke(s)]", a grader will confabulate a level
    for work it never read, and the child gets feedback on nothing.
    """

    def test_the_grader_is_told_it_cannot_read_the_answers(self):
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.child,
            answers={str(self.q.pk): self.answer})
        text = sheet.as_worklog_text()
        self.assertTrue(sheet.is_handwritten_only)
        self.assertIn("written BY HAND", text)
        self.assertIn("do not", text.lower())
        # The answers are still there for the record, just labelled unreadable.
        self.assertIn("handwritten answer", text)

    def test_a_mixed_sheet_names_which_answers_cannot_be_read(self):
        """A mixed sheet has something real to grade AND something unreadable.

        A Lexicon week is the case in point: ten typed sentences plus three
        written with the pen. Saying nothing lets the grader score the three it
        never saw; saying "this whole page is handwritten" would throw away the
        ten it can. So it names them.
        """
        typed = Question.objects.create(
            question_set=self.qset, order=2, category="writing",
            response_type=Question.TYPE_TEXT, prompt="Type this one")
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.child,
            answers={str(self.q.pk): self.answer,
                     str(typed.pk): "Paul Erdős amazed me."})
        self.assertFalse(sheet.is_handwritten_only)
        text = sheet.as_worklog_text()
        self.assertIn(f"Q{self.q.order} were written BY HAND", text)
        self.assertIn("Grade only the other questions", text)
        # The typed answer is still handed over in full.
        self.assertIn("Paul Erdős amazed me.", text)
        self.assertNotIn("every answer here was written BY HAND", text)

    def test_a_typed_only_sheet_is_untouched(self):
        from tutor.models import Question, QuestionSet, ResponseSheet
        typed_set = QuestionSet.objects.create(
            lesson=self.lesson, title="Typed", family=self.family,
            status=QuestionSet.APPROVED)
        q = Question.objects.create(
            question_set=typed_set, order=1, category="writing",
            response_type=Question.TYPE_TEXT, prompt="Write something")
        sheet = ResponseSheet.objects.create(
            question_set=typed_set, child=self.child,
            answers={str(q.pk): "Paul Erdős amazed me."})
        self.assertFalse(sheet.is_handwritten_only)
        self.assertNotIn("NOTE TO THE GRADER", sheet.as_worklog_text())
        self.assertIn("Paul Erdős amazed me.", sheet.as_worklog_text())


class LexiconPosterTests(TestCase):
    """The hundred-word poster.

    The paper guide has her colour in each week's words on a wall poster; this
    is that, except it fills itself from work she has actually turned in. It has
    to be REACHABLE from the unit — a poster nobody can find is not a reward.
    """

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
        from students.models import Student
        from portal.tokens import make_portal_token
        from tutor.lexicon import CURRICULUM_NAME, WEEKS
        from tutor.models import Question, QuestionSet

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="lx", email="lx@e.com", password="pw")
        cls.family = Family.objects.create(name="LX Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, family=cls.family, name=CURRICULUM_NAME,
            subject="Language Arts")
        chap = Chapter.objects.create(curriculum=cls.cur, number=1, title="Traits")
        CurriculumPlacement.objects.create(child=cls.child, curriculum=cls.cur)
        cls.sets = {}
        for week in WEEKS[:3]:
            lesson = Lesson.objects.create(
                chapter=chap, order=week["number"], number=week["number"],
                title=week["person"])
            qset = QuestionSet.objects.create(
                lesson=lesson, family=cls.family, status=QuestionSet.APPROVED,
                title=f"Week {week['number']} · {week['person']} — {week['role']}")
            Question.objects.create(
                question_set=qset, order=1, category="grammar",
                response_type=Question.TYPE_CLOZE, passage="_____ test.")
            cls.sets[week["number"]] = qset
        cls.token = make_portal_token(cls.child)

    def _url(self):
        return reverse("portal:lexicon_poster", args=[self.token])

    def _submit(self, week_number):
        from django.utils import timezone
        from tutor.models import ResponseSheet
        qset = self.sets[week_number]
        q = qset.questions.first()
        ResponseSheet.objects.create(
            question_set=qset, child=self.child,
            answers={str(q.pk): "focused"},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())

    def test_it_starts_empty_but_shows_what_is_coming(self):
        """Seeing the words she hasn't earned yet is the point of a poster."""
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["collected"], 0)
        self.assertEqual(resp.context["total"], 100)
        self.assertContains(resp, "inquisitive")     # week 1, not yet earned
        self.assertContains(resp, "environmentalist")  # week 10, far away

    def test_turning_in_a_week_colours_in_its_ten_words(self):
        self._submit(1)
        resp = self.client.get(self._url())
        self.assertEqual(resp.context["collected"], 10)
        self.assertEqual(resp.context["weeks_done"], 1)
        rows = {r["number"]: r for r in resp.context["rows"]}
        self.assertTrue(rows[1]["earned"])
        self.assertFalse(rows[2]["earned"])
        self.assertTrue(all(w["earned"] for w in rows[1]["words"]))

    def test_work_started_but_not_turned_in_earns_nothing(self):
        """The poster records work finished, not work opened — otherwise it
        colours itself in for a page she merely looked at."""
        from tutor.models import ResponseSheet
        qset = self.sets[1]
        ResponseSheet.objects.create(
            question_set=qset, child=self.child,
            answers={str(qset.questions.first().pk): "focused"})
        self.assertEqual(self.client.get(self._url()).context["collected"], 0)

    def test_the_bar_is_a_percentage_not_a_count(self):
        """It reads correctly only by accident while the total is exactly 100."""
        self._submit(1)
        self._submit(2)
        resp = self.client.get(self._url())
        self.assertEqual(resp.context["pct"], 20)

    def test_a_sibling_cannot_read_her_poster(self):
        from portal.tokens import make_portal_token
        from students.models import Student
        sibling = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07",
            family=self.family)
        self._submit(1)
        resp = self.client.get(
            reverse("portal:lexicon_poster", args=[make_portal_token(sibling)]))
        # Not placed in the unit, so there is no poster for her at all.
        self.assertEqual(resp.status_code, 404)

    def test_a_bad_token_gets_nothing(self):
        self.assertEqual(
            self.client.get(
                reverse("portal:lexicon_poster", args=["not-a-token"])).status_code, 404)

    def test_the_unit_page_links_to_the_poster(self):
        """Built-but-unreachable is not built. This has bitten twice."""
        resp = self.client.get(
            reverse("portal:portal_subject", args=[self.token, self.cur.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context["show_lexicon_poster"])
        self.assertContains(resp, self._url())

    def test_other_units_do_not_advertise_a_poster_they_lack(self):
        from curricula.models import Curriculum, CurriculumPlacement
        other = Curriculum.objects.create(
            parent=self.parent, family=self.family, name="Dimensions Math 3A",
            subject="Math")
        CurriculumPlacement.objects.create(child=self.child, curriculum=other)
        resp = self.client.get(
            reverse("portal:portal_subject", args=[self.token, other.pk]))
        self.assertFalse(resp.context["show_lexicon_poster"])
        self.assertNotContains(resp, self._url())


class LexiconOnePageTests(TestCase):
    """A week is ONE page, the way the printed guide lays it out.

    Splitting it into "meet the words" / "finish the sentences" / "what amazed
    you" made her navigate between parts of a single spread, which the book
    never asks of her.
    """

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from students.models import Student
        from portal.tokens import make_portal_token

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="op", email="op@e.com", password="pw")
        cls.family = Family.objects.create(name="OP Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_lexicon_violet", "--for-user", "op", stdout=StringIO())

    def test_each_week_is_a_single_page(self):
        from curricula.models import Curriculum, Lesson
        from tutor.lexicon import CURRICULUM_NAME
        from tutor.models import QuestionSet

        self._seed()
        cur = Curriculum.objects.get(name=CURRICULUM_NAME, parent=self.parent)
        lessons = Lesson.objects.filter(chapter__curriculum=cur)
        self.assertEqual(lessons.count(), 10)
        for lesson in lessons:
            sets = QuestionSet.objects.filter(lesson=lesson)
            self.assertEqual(sets.count(), 1, f"week {lesson.number}")
            self.assertEqual(sets.first().questions.count(), 13)

    def test_the_page_carries_words_sentences_and_writing_together(self):
        from tutor.models import Question, QuestionSet

        self._seed()
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__parent=self.parent).first()
        kinds = [q.response_type for q in qset.questions.order_by("order")]
        self.assertEqual(kinds.count(Question.TYPE_CLOZE), 10)
        self.assertEqual(kinds.count(Question.TYPE_HANDWRITING), 3)
        # Sentences first, writing last — the order the book uses.
        self.assertEqual(kinds[:10], [Question.TYPE_CLOZE] * 10)
        self.assertEqual(kinds[10:], [Question.TYPE_HANDWRITING] * 3)

        resp = self.client.get(
            reverse("portal:portal_questions", args=[self.token, qset.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Paul Erdős")           # who the week is about
        self.assertContains(resp, "The Boy Who Loved Math")  # the book to read
        self.assertContains(resp, "inquisitive")          # a word and its meaning
        self.assertContains(resp, "eager for knowledge")
        self.assertContains(resp, "lxa-hand")             # and the three writing boxes

    def test_the_word_list_never_reaches_her_as_raw_markdown(self):
        """It shipped once showing "## Week 1" and "**focused**" with the
        asterisks, because the content was dumped instead of rendered."""
        from tutor.models import QuestionSet

        self._seed()
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__parent=self.parent).first()
        html = self.client.get(
            reverse("portal:portal_questions", args=[self.token, qset.pk])
        ).content.decode()
        body = html[html.index("<body"):]
        self.assertNotIn("**", body)
        self.assertNotIn("## Week", body)
        # Rendered as cards instead.
        self.assertIn("lxw-card", body)

    def test_reseeding_retires_the_old_three_part_shape(self):
        from curricula.models import Lesson
        from tutor.models import Material, QuestionSet

        self._seed()
        lesson = Lesson.objects.get(
            number=1, chapter__curriculum__parent=self.parent)
        # Simulate the earlier shape sitting beside the new page.
        QuestionSet.objects.create(
            lesson=lesson, family=self.family, status=QuestionSet.APPROVED,
            title="Week 1 · Paul Erdős — finish the sentences")
        Material.objects.create(
            lesson=lesson, family=self.family, title="Week 1: meet the words",
            student_content="old", status=Material.APPROVED)
        self._seed()
        self.assertEqual(QuestionSet.objects.filter(lesson=lesson).count(), 1)
        self.assertEqual(Material.objects.filter(lesson=lesson).count(), 0)

    def test_a_stale_page_she_has_worked_in_is_kept(self):
        """Sweeping away the old shape must never take work with it."""
        from django.utils import timezone
        from curricula.models import Lesson
        from tutor.models import QuestionSet, ResponseSheet

        self._seed()
        lesson = Lesson.objects.get(
            number=1, chapter__curriculum__parent=self.parent)
        old = QuestionSet.objects.create(
            lesson=lesson, family=self.family, status=QuestionSet.APPROVED,
            title="Week 1 · Paul Erdős — finish the sentences")
        ResponseSheet.objects.create(
            question_set=old, child=self.child, answers={"1": "focused"},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        self._seed()
        self.assertTrue(QuestionSet.objects.filter(pk=old.pk).exists())

    def test_turning_in_the_week_earns_its_words_on_the_poster(self):
        """The poster keyed on a title string, which stopped earning anything
        the moment the page was renamed."""
        from django.utils import timezone
        from tutor.models import QuestionSet, ResponseSheet

        self._seed()
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__parent=self.parent).first()
        ResponseSheet.objects.create(
            question_set=qset, child=self.child, answers={"1": "focused"},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        resp = self.client.get(reverse("portal:lexicon_poster", args=[self.token]))
        self.assertEqual(resp.context["collected"], 10)


class LexiconWritingBoxTests(LexiconOnePageTests):
    """The three "what amazes you" boxes.

    This is the one place in the week she writes her own thought, and she writes
    it BY HAND with a stylus — so her sentences reach the parent's work browser
    and the printed charter report exactly as she formed them.
    """

    def _page(self):
        from tutor.models import QuestionSet

        self._seed()
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__parent=self.parent).first()
        return self.client.get(
            reverse("portal:portal_questions", args=[self.token, qset.pk])
        ).content.decode()

    def test_she_writes_these_three_with_the_pen(self):
        html = self._page()
        self.assertEqual(html.count("handwriting-canvas"), 3)
        self.assertNotIn("lxa-input", html)   # no typed box left behind

    def test_the_pen_sits_inside_the_designed_card(self):
        """The generic handwriting branch matches these questions too, so
        whichever branch the template tests first wins. When it was the generic
        one she lost the card, the medallion and the shared heading, and got the
        bare widget with its own "write by hand" hint three times over.
        """
        html = self._page()
        self.assertEqual(html.count('class="lxa-box'), 3)
        self.assertEqual(html.count("lxa-num"), 3)
        self.assertEqual(html.count("lxa-hand"), 3)
        self.assertNotIn("handwriting-hint", html)

    def test_the_page_never_hands_her_a_pen_the_database_disagrees_with(self):
        """The seed is a manual step after a deploy, so the template can be live
        while the rows still say "text". If the page decided on its own that
        these three are handwriting, her strokes would be stored against a text
        question: nothing would replay them, and the grader would be handed raw
        coordinate JSON as her sentence."""
        from tutor.models import Question, QuestionSet

        self._seed()
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__parent=self.parent).first()
        qset.questions.filter(order__gt=10).update(
            response_type=Question.TYPE_TEXT)   # the not-yet-re-seeded state
        html = self.client.get(
            reverse("portal:portal_questions", args=[self.token, qset.pk])
        ).content.decode()
        self.assertNotIn("handwriting-canvas", html)
        self.assertNotIn("lxa-box", html)
        # And she is not left staring at three unlabelled boxes either. The
        # question is asked in this state too — it appears nowhere else on the
        # page, and this is exactly the state prod is in between a deploy and
        # the re-seed.
        self.assertEqual(html.count("portal-qnum"), 13)
        self.assertIn("Amazing thing 1", html)
        self.assertEqual(html.count("What are three things that amaze you"), 1)
        self.assertIn("Paul Erdős", html)

    def test_an_older_set_is_left_alone(self):
        """The seed KEEPS the earlier three-part sets when a child has work in
        them, and those hold the same three writing questions at orders 1-3. The
        page used to number its cards `order - 10`, so it offered her medallions
        reading -9, -8, -7 — and, because the shared heading only renders above
        card 1, asked her no question at all."""
        from tutor.models import Question, QuestionSet

        self._seed()
        lesson = Lesson.objects.get(
            number=1, chapter__curriculum__parent=self.parent)
        old = QuestionSet.objects.create(
            lesson=lesson, family=self.family, status=QuestionSet.APPROVED,
            title="Week 1 · Paul Erdős — what amazed you?")
        for i in (1, 2, 3):
            Question.objects.create(
                question_set=old, order=i, category="writing",
                response_type=Question.TYPE_HANDWRITING,
                prompt=f"Amazing thing {i}")
        html = self.client.get(
            reverse("portal:portal_questions", args=[self.token, old.pk])
        ).content.decode()
        # Not a bare "-9": the portal token is base64 and contains that pair
        # about one page in a hundred, which would fail this for no reason.
        self.assertNotIn("Amazing thing -9", html)
        self.assertNotIn("lxa-box", html)
        # It falls back to the ordinary handwriting widget, which asks the
        # question in the prompt the way every other page does.
        self.assertEqual(html.count("handwriting-canvas"), 3)
        self.assertEqual(html.count("portal-qnum"), 3)
        self.assertIn("Amazing thing 1", html)

    def test_the_question_is_asked_once_above_the_boxes(self):
        """Asking it three times would read as three separate assignments."""
        html = self._page()
        self.assertEqual(html.count("What are three things that amaze you"), 1)
        self.assertIn("Paul Erdős", html)

    def test_each_box_keeps_its_number_and_visible_label(self):
        """The medallion and label are what tell her which of the three she is
        on — the surface itself carries no wording but "Write here…"."""
        html = self._page()
        self.assertEqual(html.count("Amazing thing 1"), 1)
        self.assertEqual(html.count('class="lxa-label"'), 3)
        # Nothing on these boxes leans on a placeholder attribute.
        start = html.index("lxa-box")
        self.assertNotIn("placeholder", html[start:html.index("Turn it in")])

    def test_the_pens_are_put_away_once_the_week_is_turned_in(self):
        """A submitted page must show her writing, not invite more of it."""
        from django.utils import timezone
        from tutor.models import QuestionSet, ResponseSheet

        self._seed()
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__parent=self.parent).first()
        ResponseSheet.objects.create(
            question_set=qset, child=self.child, answers={},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        html = self.client.get(
            reverse("portal:portal_questions", args=[self.token, qset.pk])
        ).content.decode()
        self.assertEqual(html.count("handwriting-canvas"), 3)
        self.assertEqual(html.count('data-readonly="1"'), 3)
        self.assertNotIn("lxa-pens", html)

    def test_the_grader_is_told_not_to_mark_the_handwriting(self):
        """Her strokes reach the AI as stroke JSON, which it would happily
        "read" and grade as gibberish. It must abstain and leave these to me."""
        from django.utils import timezone
        from tutor.models import QuestionSet, ResponseSheet

        self._seed()
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__parent=self.parent).first()
        sheet = ResponseSheet.objects.create(
            question_set=qset, child=self.child,
            answers={str(q.pk): "focused" for q in qset.questions.all()[:10]},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        for q in qset.questions.filter(order__gt=10):
            sheet.answers[str(q.pk)] = (
                '{"strokes":[{"c":"#1d3557","w":3,"p":[[0.1,0.1],[0.4,0.2]]}],'
                '"surface":{"w":600,"h":192}}')
        sheet.save()
        text = sheet.as_worklog_text()
        # Mixed sheet: it must name the three, not claim the whole page is
        # unreadable — the ten sentences are exactly what it should be grading.
        self.assertIn("Q11, Q12, Q13 were written BY HAND", text)
        self.assertIn("Grade only the other questions", text)
        self.assertNotIn("every answer here was written BY HAND", text)
        self.assertNotIn('"strokes"', text)
        # And it is told to keep that between itself and me. The highlights and
        # the encouragement are printed straight onto her feedback page, and
        # "a grown-up will have to read your writing" lands on a nine-year-old
        # as "what you did was no good".
        self.assertIn("never in the encouragement", text)
        self.assertIn("child-facing highlights", text)

    def test_the_generic_question_chrome_stands_down(self):
        """The medallion and label already say the number and the task; the
        badge, chip and prompt would say all three a second time."""
        html = self._page()
        self.assertEqual(html.count("own-chrome"), 3)
        self.assertEqual(html.count("portal-qnum"), 10)   # the ten cloze rows only

    def test_the_week_tint_reaches_the_boxes(self):
        """The medallions are coloured by the week; without the class on a
        common ancestor they fall back to teal on every week."""
        html = self._page()
        self.assertIn("lx-week-1", html)

    def test_turning_it_in_is_never_blocked_by_an_empty_box(self):
        """She works alone. A dead button with no explanation reads as broken,
        and punishes exactly the child who is already stuck."""
        html = self._page()
        button = html[html.index("Turn it in") - 400:html.index("Turn it in")]
        self.assertNotIn("disabled", button)


class DickinsonSeedTests(TestCase):
    """Kaylin's Operation Lexicon: Emily Dickinson.

    23 weeks, three days each, the way the guide numbers itself. The copying is
    done with a pen — that is the skill the guide is teaching.
    """

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from portal.tokens import make_portal_token

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="dk", email="dk@e.com", password="pw")
        cls.family = Family.objects.create(name="DK Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07",
            family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_lexicon_kaylin", "--for-user", "dk", stdout=StringIO())

    def _set(self, week, day):
        from tutor.dickinson import CURRICULUM_NAME
        from tutor.models import QuestionSet
        return QuestionSet.objects.get(
            lesson__number=week, title__endswith="Day %d" % day,
            lesson__chapter__curriculum__name=CURRICULUM_NAME,
            lesson__chapter__curriculum__parent=self.parent)

    def _page(self, week=1, day=1):
        return self.client.get(reverse(
            "portal:portal_questions", args=[self.token, self._set(week, day).pk])
        ).content.decode()

    def test_the_guide_is_laid_out_as_twenty_three_weeks_of_three_days(self):
        from curricula.models import Curriculum, Lesson
        from tutor.dickinson import CURRICULUM_NAME
        from tutor.models import QuestionSet

        self._seed()
        cur = Curriculum.objects.get(name=CURRICULUM_NAME, parent=self.parent)
        lessons = Lesson.objects.filter(chapter__curriculum=cur)
        self.assertEqual(lessons.count(), 23)
        for lesson in lessons:
            sets = QuestionSet.objects.filter(lesson=lesson)
            self.assertEqual(sets.count(), 3, "week %s" % lesson.number)
        # Two words a day, three steps each; day 3 is the word and the story.
        self.assertEqual(self._set(1, 1).questions.count(), 6)
        self.assertEqual(self._set(1, 2).questions.count(), 6)
        self.assertEqual(self._set(1, 3).questions.count(), 2)

    def test_the_copying_is_done_with_a_pen(self):
        """The guide teaches handwriting and 'contemplative attention to
        detail' through the copying. Typed, it practises neither."""
        from tutor.models import Question

        self._seed()
        for day in (1, 2):
            kinds = [q.response_type
                     for q in self._set(1, day).questions.order_by("order")]
            self.assertEqual(kinds, [Question.TYPE_HANDWRITING] * 6,
                             "day %d" % day)
        # Day 3 is a 150-word story that wants revising — that one is typed.
        self.assertEqual(
            [q.response_type for q in self._set(1, 3).questions.order_by("order")],
            [Question.TYPE_TEXT] * 2)

    def test_she_can_see_what_she_is_copying(self):
        """The words live in tutor.dickinson, not on the questions, so the page
        has to put them back. Without the card there is nothing to copy from —
        just an instruction to copy something invisible."""
        html = self._seed() or self._page(1, 1)
        self.assertEqual(html.count("dk-word"), 2)          # two words today
        self.assertIn("agate", html)
        self.assertIn("an ornamental stone", html)          # the definition
        self.assertIn("To joint this Agate were a work", html)   # her lines
        self.assertIn("1134 pg. 509", html)                 # the citation
        self.assertEqual(html.count("handwriting-canvas"), 6)

    def test_dickinsons_line_breaks_reach_the_page(self):
        """Her line breaks are the poem. Collapsed into a paragraph, Kaylin
        would copy out prose and the exercise would be pointless.

        This pins the breaks into the HTML; keeping them VISIBLE is
        `white-space: pre-wrap` on .dk-quote, which no request-level test can
        see — that half is checked by looking at the rendered page.
        """
        self._seed()
        html = self._page(1, 2)
        self.assertIn("But if they only stay\nAmpler to fly away", html)

    def test_the_guides_own_misspelling_is_flagged_where_she_will_copy_it(self):
        """Week 16 prints "perrenial". She is copying it out by hand, so the
        page says so rather than letting her learn it wrong."""
        self._seed()
        html = self._page(16, 1)
        self.assertIn("perrenial", html)      # as printed — she copies the book
        self.assertIn("dk-note", html)
        self.assertIn("perennial", html)      # and is told the real spelling

    def test_day_three_asks_for_the_story_and_offers_the_starters(self):
        self._seed()
        html = self._page(1, 3)
        self.assertIn("micro-story", html)
        self.assertIn("COURAGE is a lion", html)
        self.assertNotIn("handwriting-canvas", html)   # typed, for revising
        self.assertEqual(html.count("dk-word"), 0)     # no words to copy today

    def test_a_set_that_does_not_match_the_book_still_shows_the_words(self):
        """If a question is pruned, or the content is edited to a different
        number of words, the cards can no longer be matched one-to-one. Falling
        back to no words at all would leave her instructions to copy something
        that isn't on the page."""
        self._seed()
        qset = self._set(1, 1)
        # Delete the FIRST question, not the last. Removing the last one is the
        # single case where the unguarded path still happens to render correctly,
        # so a test built on it cannot tell the fallback from the bug.
        qset.questions.order_by("order").first().delete()
        html = self.client.get(reverse(
            "portal:portal_questions", args=[self.token, qset.pk])).content.decode()
        self.assertEqual(html.count("dk-word"), 2)
        self.assertIn("an ornamental stone", html)
        self.assertIn("a fine-grained, translucent form of gypsum", html)
        # Header mode puts BOTH words above ALL the questions. Paired mode
        # interleaves them. That position is the only thing in the HTML that
        # tells the two apart — the card markup itself is identical.
        self.assertLess(html.index("a fine-grained, translucent form of gypsum"),
                        html.index("— copy the word and the definition"))

    def test_reseeding_changes_nothing(self):
        from tutor.models import Question, QuestionSet

        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)


class DickinsonGuideTests(DickinsonSeedTests):
    """The parent guide — the booklet's front matter, which the app was
    otherwise swallowing."""

    def _guide(self):
        from curricula.models import Curriculum
        from tutor.dickinson import CURRICULUM_NAME

        self._seed()
        cur = Curriculum.objects.get(name=CURRICULUM_NAME, parent=self.parent)
        self.client.force_login(self.parent)
        return cur, self.client.get(reverse("tutor:dickinson_guide", args=[cur.pk]))

    def test_it_explains_the_method_and_lists_every_word(self):
        _cur, resp = self._guide()
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("How a week runs", html)
        self.assertIn("Copy the word and its definition", html)
        # All 92 words, with their definitions, at a glance.
        from tutor.dickinson import all_words
        for entry in all_words():
            self.assertIn(entry["word"], html)

    def test_it_says_which_portions_are_written_by_hand(self):
        """This is the guide's pedagogy, not a preference of ours, and the
        parent has no other way to find out which portions take the pen."""
        _cur, resp = self._guide()
        html = resp.content.decode()
        self.assertIn("Why the copying is done by hand", html)
        start = html.index("Why the copying is done by hand")
        block = html[start:start + 1400]
        self.assertEqual(block.count("written by hand"), 3)   # the three copy steps
        self.assertIn("typed", block)                          # day 3

    def test_it_carries_the_printed_guides_misspelling_forward(self):
        _cur, resp = self._guide()
        html = resp.content.decode()
        self.assertIn("perrenial", html)
        self.assertIn("perennial", html)

    def test_a_week_counts_as_done_only_when_all_three_days_are_in(self):
        """One day turned in is progress, not a finished week — counting it as
        one would tell the parent she is three times further along."""
        from django.utils import timezone
        from tutor.models import ResponseSheet

        self._seed()
        ResponseSheet.objects.create(
            question_set=self._set(1, 1), child=self.child, answers={},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        _cur, resp = self._guide()
        row = resp.context["children"][0]
        self.assertEqual(row["weeks_done"], 0)
        self.assertEqual(row["days_done"], 1)
        for day in (2, 3):
            ResponseSheet.objects.create(
                question_set=self._set(1, day), child=self.child, answers={},
                status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        _cur, resp = self._guide()
        row = resp.context["children"][0]
        self.assertEqual(row["weeks_done"], 1)
        self.assertEqual(row["words"], 4)
        self.assertEqual(row["next_week"]["number"], 2)

    def test_the_guide_is_not_reachable_for_other_curricula(self):
        """The URL takes any curriculum id; without the name check it would
        render Dickinson's front matter over somebody else's course."""
        from curricula.models import Curriculum

        self._seed()
        other = Curriculum.objects.create(
            parent=self.parent, name="Something Else", subject="Math",
            family=self.family)
        self.client.force_login(self.parent)
        resp = self.client.get(reverse("tutor:dickinson_guide", args=[other.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_the_link_shows_on_this_curriculum_and_not_on_others(self):
        from curricula.models import Curriculum

        cur, _resp = self._guide()
        detail = self.client.get(
            reverse("curricula:curriculum_detail", args=[cur.pk])).content.decode()
        self.assertIn("dickinson-guide", detail)
        other = Curriculum.objects.create(
            parent=self.parent, name="Something Else", subject="Math",
            family=self.family)
        detail = self.client.get(
            reverse("curricula:curriculum_detail", args=[other.pk])).content.decode()
        self.assertNotIn("dickinson-guide", detail)
        self.assertNotIn("lexicon-guide", detail)


class DickinsonSeamTests(DickinsonSeedTests):
    """The ways the page could show her the wrong thing to copy."""

    def _html(self, qset):
        return self.client.get(reverse(
            "portal:portal_questions", args=[self.token, qset.pk])).content.decode()

    def test_the_cards_and_the_answers_stay_in_step(self):
        """Positional pairing is only as good as its guard. A delete PLUS an
        insert leaves the count unchanged and shifts every word one slot, so
        she would be told to copy alabaster's definition while looking at
        agate's card — wrong, with nothing on the page to reveal it."""
        from tutor.models import Question

        self._seed()
        qset = self._set(1, 1)
        qset.questions.order_by("order").first().delete()
        Question.objects.create(
            question_set=qset, order=7, category="writing",
            response_type=Question.TYPE_HANDWRITING, prompt="an inserted extra")
        html = self._html(qset)
        # Count is back to six, but the prompts no longer match the words, so
        # the page falls back instead of pairing them wrongly.
        self.assertEqual(qset.questions.count(), 6)
        self.assertEqual(html.count("dk-word"), 2)
        # Both cards above all the questions = header mode. If the count-only
        # guard let this pair up, alabaster's card would sit BETWEEN them.
        self.assertLess(html.index("a fine-grained, translucent form of gypsum"),
                        html.index("— copy the lines from Dickinson"))

    def test_the_happy_path_really_does_pair_each_word_with_its_own_answers(self):
        """The whole seam. Without an ordering assertion, mispairing the words
        still renders two cards and passes every other test here."""
        self._seed()
        html = self._html(self._set(1, 1))
        agate_card = html.index("an ornamental stone")
        alabaster_card = html.index("a fine-grained, translucent form of gypsum")
        agate_q = html.index("agate — copy the word and the definition")
        alabaster_q = html.index("alabaster — copy the word and the definition")
        self.assertLess(agate_card, agate_q)
        self.assertLess(agate_q, alabaster_card)
        self.assertLess(alabaster_card, alabaster_q)

    def test_a_renamed_set_shows_the_whole_week_not_a_guessed_day(self):
        """Guessing the day from the set's position among its siblings put Day
        2's words above Day 1's prompts. Showing her the wrong words while
        telling her she is on the right day is worse than showing none."""
        self._seed()
        qset = self._set(1, 3)
        qset.title = "Week 1 · something else"
        qset.save(update_fields=["title"])
        html = self._html(qset)
        self.assertNotIn("Day 2", html)
        self.assertEqual(html.count("dk-word"), 4)   # the whole week
        for definition in ("an ornamental stone", "food or nourishment"):
            self.assertIn(definition, html)

    def test_a_dry_run_writes_nothing(self):
        """It created the curriculum, the chapter and all 23 lessons, then said
        "nothing written" — leaving a phantom course in the parent's list."""
        from io import StringIO
        from django.core.management import call_command
        from curricula.models import Chapter, Curriculum, Lesson

        out = StringIO()
        call_command("seed_lexicon_kaylin", "--for-user", "dk", "--dry-run",
                     stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)
        self.assertEqual(Chapter.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_reseeding_restores_a_question_that_was_tampered_with(self):
        """update_or_create has to actually refresh the row. The prod Lexicon
        deploy was already bitten once by a response_type left stale."""
        from tutor.models import Question

        self._seed()
        q = self._set(1, 1).questions.order_by("order").first()
        Question.objects.filter(pk=q.pk).update(
            response_type=Question.TYPE_TEXT, prompt="STALE")
        self._seed()
        q.refresh_from_db()
        self.assertEqual(q.response_type, Question.TYPE_HANDWRITING)
        self.assertTrue(q.prompt.startswith("agate"))

    def test_the_guides_own_confusions_are_flagged_on_her_card(self):
        """Two places where copying the guide exactly would teach her something
        false. She still copies what is printed — the card just says so."""
        self._seed()
        html = self._html(self._set(9, 1))
        self.assertIn("Debachee", html)          # as printed
        self.assertIn("Debauchee", html)         # and what the word really is
        html = self._html(self._set(17, 1))
        self.assertIn("Quenching—in Purple", html)
        self.assertIn("put a fire or a light OUT", html)


class OneTrueSentenceTests(TestCase):
    """Violet's One True Sentence: Tools of Style.

    Twenty weeks, each a lesson page and a practice page, the way the book is
    laid out. The copying and her own sentences are done with the pen.
    """

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from portal.tokens import make_portal_token

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="ot", email="ot@e.com", password="pw")
        cls.family = Family.objects.create(name="OT Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_onetrue_violet", "--for-user", "ot", stdout=StringIO())

    def _set(self, week, practice=False):
        from tutor.models import QuestionSet
        from tutor.onetrue import CURRICULUM_NAME
        qs = QuestionSet.objects.filter(
            lesson__number=week,
            lesson__chapter__curriculum__name=CURRICULUM_NAME,
            lesson__chapter__curriculum__parent=self.parent)
        return (qs.filter(title__endswith="now you try!").get() if practice
                else qs.exclude(title__endswith="now you try!").get())

    def _page(self, week=1, practice=False):
        return self.client.get(reverse(
            "portal:portal_questions",
            args=[self.token, self._set(week, practice).pk])).content.decode()

    def test_twenty_weeks_each_a_lesson_and_a_practice(self):
        from curricula.models import Curriculum, Lesson
        from tutor.models import QuestionSet
        from tutor.onetrue import CURRICULUM_NAME

        self._seed()
        cur = Curriculum.objects.get(name=CURRICULUM_NAME, parent=self.parent)
        lessons = Lesson.objects.filter(chapter__curriculum=cur)
        self.assertEqual(lessons.count(), 20)
        for lesson in lessons:
            self.assertEqual(
                QuestionSet.objects.filter(lesson=lesson).count(), 2,
                "week %s" % lesson.number)

    def test_the_copying_and_her_own_sentences_use_the_pen(self):
        """Copying a Caldecott sentence at a keyboard is transcription, not
        noticing how it is built. And she is nine — five sentences hunted out on
        a keyboard is an endurance test, not sentence craft."""
        from tutor.models import Question

        self._seed()
        lesson = list(self._set(1).questions.order_by("order"))
        self.assertEqual(lesson[0].response_type, Question.TYPE_HANDWRITING)
        self.assertTrue(lesson[0].prompt.startswith("Read and copy"))
        # The noticing questions are typed, so the grader can read them.
        self.assertTrue(all(q.response_type == Question.TYPE_TEXT
                            for q in lesson[1:]))
        practice = list(self._set(1, practice=True).questions.all())
        self.assertEqual([q.response_type for q in practice],
                         [Question.TYPE_HANDWRITING] * 5)

    def test_she_can_see_the_sentence_she_is_copying(self):
        self._seed()
        html = self._page(1)
        self.assertIn("Vivid and descriptive", html)          # the explanation
        self.assertIn("Wordsworth, Daffodils", html)          # its example
        self.assertIn("chuckleberry blossoms", html)          # Sentence 1
        self.assertIn("Margaret Wise Brown, The Little Island", html)
        self.assertIn("pastel hues", html)                    # Sentence 2
        self.assertIn("whispered tone", html)

    def test_the_practice_page_does_not_show_the_model_sentence(self):
        """She is composing there. Leaving the model sentence on screen invites
        copying it a second time instead of writing her own."""
        self._seed()
        html = self._page(1, practice=True)
        self.assertIn("Vivid and descriptive", html)     # the tool, still
        self.assertNotIn("chuckleberry blossoms", html)  # but not the model
        self.assertNotIn("Margaret Wise Brown", html)
        self.assertEqual(html.count("handwriting-canvas"), 5)

    def test_the_weeks_that_split_into_groups_ask_for_the_right_number(self):
        """The practice page is not always five. Week 3 splits into two groups
        of three, week 7 into three pairs, week 20 into two and two."""
        self._seed()
        for week, expected in ((1, 5), (3, 6), (7, 6), (18, 6), (20, 4)):
            self.assertEqual(
                self._set(week, practice=True).questions.count(), expected,
                "week %d" % week)
        prompts = " ".join(
            q.prompt for q in self._set(3, practice=True).questions.all())
        # "using you" is a substring of "using your", so asserting it proves
        # nothing — two "your" groups and no "you're" group would pass.
        self.assertIn("using you're", prompts)
        self.assertIn("using your", prompts)

    def test_the_paired_weeks_ask_for_both_halves(self):
        """Weeks 8 and 19 are craft-then-rewrite: a fragment then the whole
        sentence, a run-on then the split version. One box each would lose half
        the exercise."""
        self._seed()
        eight = list(self._set(8, practice=True).questions.order_by("order"))
        self.assertEqual(len(eight), 8)            # four items, two answers each
        self.assertTrue(eight[0].prompt.startswith("Fragment 1"))
        self.assertTrue(eight[1].prompt.startswith("Sentence 1"))
        nineteen = list(self._set(19, practice=True).questions.order_by("order"))
        self.assertEqual(len(nineteen), 6)         # three items, two answers each
        self.assertTrue(nineteen[0].prompt.startswith("Run-on 1"))
        self.assertTrue(nineteen[1].prompt.startswith("Rewritten 1"))

    def test_a_dry_run_writes_nothing(self):
        from io import StringIO
        from django.core.management import call_command
        from curricula.models import Curriculum, Lesson

        out = StringIO()
        call_command("seed_onetrue_violet", "--for-user", "ot", "--dry-run",
                     stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_reseeding_changes_nothing(self):
        from tutor.models import Question, QuestionSet

        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)


class OneTrueGuideTests(OneTrueSentenceTests):
    """The parent guide."""

    def _guide(self):
        from curricula.models import Curriculum
        from tutor.onetrue import CURRICULUM_NAME

        self._seed()
        cur = Curriculum.objects.get(name=CURRICULUM_NAME, parent=self.parent)
        self.client.force_login(self.parent)
        return cur, self.client.get(reverse("tutor:onetrue_guide", args=[cur.pk]))

    def test_it_carries_the_books_own_reference_material(self):
        from tutor.onetrue import WEEKS

        _cur, resp = self._guide()
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("Sentence construction basics", html)
        self.assertIn("Part 3: Phrases", html)          # the reference section
        self.assertIn("Because the sun was shining", html)
        # escape(): the apostrophe in "You're / Your" reaches the page as
        # &#x27; — asserting the raw topic would fail for reasons that have
        # nothing to do with whether the week is listed.
        from django.utils.html import escape
        for week in WEEKS:                              # every tool, in a table
            self.assertIn(escape(week["topic"]), html)

    def test_it_says_which_parts_she_writes_by_hand(self):
        _cur, resp = self._guide()
        html = resp.content.decode()
        start = html.index("Which parts she writes by hand")
        block = html[start:start + 1800]
        self.assertEqual(block.count("written by hand"), 2)   # copy + her own
        self.assertIn("typed", block)                          # the noticing qs

    def test_a_week_counts_as_done_only_when_both_pages_are_in(self):
        from django.utils import timezone
        from tutor.models import ResponseSheet

        self._seed()
        ResponseSheet.objects.create(
            question_set=self._set(1), child=self.child, answers={},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        _cur, resp = self._guide()
        self.assertEqual(resp.context["children"][0]["weeks_done"], 0)
        ResponseSheet.objects.create(
            question_set=self._set(1, practice=True), child=self.child,
            answers={}, status=ResponseSheet.SUBMITTED,
            submitted_at=timezone.now())
        _cur, resp = self._guide()
        row = resp.context["children"][0]
        self.assertEqual(row["weeks_done"], 1)
        self.assertEqual(row["next_week"]["number"], 2)

    def test_the_guide_is_not_reachable_for_other_curricula(self):
        from curricula.models import Curriculum

        self._seed()
        other = Curriculum.objects.create(
            parent=self.parent, name="Something Else", subject="Math",
            family=self.family)
        self.client.force_login(self.parent)
        self.assertEqual(
            self.client.get(
                reverse("tutor:onetrue_guide", args=[other.pk])).status_code, 404)

    def test_the_link_shows_only_on_this_curriculum(self):
        from curricula.models import Curriculum

        cur, _resp = self._guide()
        detail = self.client.get(
            reverse("curricula:curriculum_detail", args=[cur.pk])).content.decode()
        self.assertIn("onetrue-guide", detail)
        other = Curriculum.objects.create(
            parent=self.parent, name="Something Else", subject="Math",
            family=self.family)
        detail = self.client.get(
            reverse("curricula:curriculum_detail", args=[other.pk])).content.decode()
        self.assertNotIn("onetrue-guide", detail)


class OneTrueSeamTests(OneTrueSentenceTests):
    """Things the build could get wrong quietly."""

    def test_the_practice_prompts_lead_with_what_makes_them_different(self):
        """Week 8's instruction runs to four lines. Repeated in full above all
        eight boxes with the only difference at the very end, it is a wall of
        identical text to a nine-year-old."""
        self._seed()
        prompts = [q.prompt for q in
                   self._set(8, practice=True).questions.order_by("order")]
        self.assertTrue(prompts[0].startswith("Fragment 1 —"))
        self.assertTrue(prompts[1].startswith("Sentence 1"))
        self.assertTrue(prompts[2].startswith("Fragment 2"))
        # The long instruction appears once, not eight times.
        self.assertEqual(sum("rewrite each as a complete" in p for p in prompts), 1)
        self.assertEqual(sum("Across the deep, dark sky" in p for p in prompts), 1)

    def test_every_group_says_what_to_do_once(self):
        """A multi-group week must not leave a group with no instruction — she
        would reach box 4 of week 7 with nothing telling her it wants "their"."""
        self._seed()
        for week, groups in ((3, 2), (7, 3), (18, 3), (20, 2)):
            prompts = [q.prompt for q in
                       self._set(week, practice=True).questions.order_by("order")]
            leading = [p for p in prompts if " — " in p]
            self.assertEqual(len(leading), groups, "week %d" % week)

    def test_question_orders_are_contiguous_and_unique(self):
        """update_or_create is keyed on (set, order), and there is a unique
        constraint on the pair — a gap or a repeat is a silently dropped
        question or an IntegrityError."""
        from tutor.models import QuestionSet
        from tutor.onetrue import CURRICULUM_NAME

        self._seed()
        for qset in QuestionSet.objects.filter(
                lesson__chapter__curriculum__name=CURRICULUM_NAME,
                lesson__chapter__curriculum__parent=self.parent):
            orders = list(qset.questions.order_by("order")
                          .values_list("order", flat=True))
            self.assertEqual(orders, list(range(1, len(orders) + 1)), qset.title)

    def test_reseeding_restores_a_question_that_was_tampered_with(self):
        """The trap the prod Lexicon deploy already hit: update_or_create has to
        actually refresh the row, not just leave the old one in place."""
        from tutor.models import Question

        self._seed()
        q = self._set(1).questions.order_by("order").first()
        Question.objects.filter(pk=q.pk).update(
            response_type=Question.TYPE_TEXT, prompt="STALE")
        self._seed()
        q.refresh_from_db()
        self.assertEqual(q.response_type, Question.TYPE_HANDWRITING)
        self.assertTrue(q.prompt.startswith("Read and copy"))

    def test_the_guides_own_mistakes_are_flagged_where_she_meets_them(self):
        """Two places where the printed guide is wrong in a way she would copy
        or reason from. She still gets what is printed — the page just says so."""
        self._seed()
        html = self._page(17)
        self.assertIn("stone drunk", html)      # as printed, and she copies it
        self.assertIn("stone-", html)           # and what Steig actually wrote
        html = self._page(12)
        self.assertIn("Dorothy&#x27;s hand", html)
        self.assertIn("mistake in the guide", html)

    def test_the_page_never_tells_her_to_write_by_hand_over_a_keyboard(self):
        """The wording follows the seed's flag rather than restating it."""
        self._seed()
        self.assertIn("Write each one by hand", self._page(1, practice=True))


class RickshawGirlTests(TestCase):
    """Violet's Blackbird Level 3 guide for Rickshaw Girl."""

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from portal.tokens import make_portal_token

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="rg", email="rg@e.com", password="pw")
        cls.family = Family.objects.create(name="RG Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_rickshaw_girl", "--for-user", "rg", stdout=StringIO())

    def _set(self, title):
        from tutor.models import QuestionSet
        from tutor.rickshaw import CURRICULUM_NAME
        return QuestionSet.objects.get(
            title=title, lesson__chapter__curriculum__name=CURRICULUM_NAME,
            lesson__chapter__curriculum__parent=self.parent)

    def _page(self, title):
        return self.client.get(reverse(
            "portal:portal_questions", args=[self.token, self._set(title).pk])
        ).content.decode()

    def test_the_guides_five_sections_are_all_there(self):
        from curricula.models import Chapter, Lesson
        from tutor.models import Question, QuestionSet
        from tutor.rickshaw import CURRICULUM_NAME

        self._seed()
        lessons = Lesson.objects.filter(
            chapter__curriculum__name=CURRICULUM_NAME,
            chapter__curriculum__parent=self.parent)
        # The shared Blackbird blueprint: four sections of Read/Journal/Acquire/
        # Recollect/Explore, plus the final project — the same skeleton as
        # A Mouse Called Wolf, which is the same publisher, level and child.
        self.assertEqual(
            Chapter.objects.filter(curriculum__name=CURRICULUM_NAME,
                                   curriculum__parent=self.parent).count(), 5)
        self.assertEqual(lessons.count(), 21)
        sets = QuestionSet.objects.filter(lesson__in=lessons)
        # 4 x 5 + the final project + the hands-on final project beside it.
        self.assertEqual(sets.count(), 22)
        gleans = sets.filter(title__contains="Glean")
        self.assertEqual(gleans.count(), 2)
        self.assertTrue(gleans.filter(title__endswith="Final Project").exists(),
                        "the guide's own options must still be offered")
        self.assertTrue(gleans.filter(title__contains="hands-on").exists())
        # 82 for the four sections, plus the final project's three scaffolded
        # questions (pick → plan → reflect), plus the hands-on project's six.
        self.assertEqual(
            Question.objects.filter(question_set__in=sets).count(), 90)

    def test_vocabulary_keeps_the_guides_own_two_exercises(self):
        """Level 3 matches words to numbered definitions and fills blanks. Both
        widgets already existed, so the page keeps the guide's format instead of
        flattening it into text boxes."""
        import json
        from tutor.models import Question

        self._seed()
        match, fill = self._set("Section 1 · Vocabulary").questions.order_by("order")
        self.assertEqual(match.response_type, Question.TYPE_MATCHING)
        self.assertEqual(fill.response_type, Question.TYPE_FILL_BLANK)

        data = json.loads(match.passage)
        self.assertEqual(len(data["words"]), 6)
        self.assertEqual(len(data["definitions"]), 6)
        # Every definition carries the word it belongs to, and each word is used
        # exactly once — a mis-paired key is what this catches.
        self.assertEqual(sorted(d["word"] for d in data["definitions"]),
                         sorted(data["words"]))
        by_n = {d["n"]: d["word"] for d in data["definitions"]}
        self.assertEqual(by_n[3], "rickshaw")     # "a small, two-wheeled vehicle"
        self.assertEqual(by_n[1], "hut")          # "a small, roughly made shelter"

        blanks = json.loads(fill.passage)["sentences"]
        self.assertEqual(len(blanks), 6)
        for s in blanks:
            # The widget splits on six underscores; the content stores three.
            self.assertIn("______", s["text"])
            self.assertNotIn("___ ", s["text"].replace("______", ""))

    def test_every_blank_can_actually_be_answered(self):
        """THE one that matters. The dropdown is built from the bank, so a blank
        keyed to a word the bank doesn't carry can never be selected: she picks
        the only sensible option, is told she is wrong, and can never finish the
        page. Section 4 shipped exactly that — 'scolded' and 'labored' keyed
        against a bank printing 'scold' and 'labor'."""
        import json

        self._seed()
        for n in (1, 2, 3, 4):
            fill = self._set("Section %d · Vocabulary" % n).questions.order_by("order")[1]
            data = json.loads(fill.passage)
            bank = set(data["words"])
            for sentence in data["sentences"]:
                self.assertIn(sentence["word"], bank,
                              "section %d: %r is not selectable" % (n, sentence["word"]))

    def test_the_blanks_that_need_a_different_ending_offer_it(self):
        """Section 4 prints 'scold' and 'labor' in its word list, but its
        sentences want 'scolded' and 'labored'. The bank has to carry the form
        the sentence needs — the matching list keeps the printed one."""
        import json

        self._seed()
        match, fill = self._set("Section 4 · Vocabulary").questions.order_by("order")
        self.assertIn("scolded", json.loads(fill.passage)["words"])
        self.assertIn("labored", json.loads(fill.passage)["words"])
        # The matching exercise still uses the guide's printed base forms.
        self.assertIn("scold", json.loads(match.passage)["words"])
        self.assertNotIn("scolded", json.loads(match.passage)["words"])

    def test_the_dropdown_on_her_page_offers_every_answer(self):
        """The data being right is not enough — this is what she actually sees."""
        import re

        self._seed()
        html = self._page("Section 4 · Vocabulary")
        block = html[html.index("vocab-fillblank"):]
        options = set(re.findall(r'<option value="([^"]+)"', block))
        needed = set(re.findall(r"data-word=\"([^\"]+)\"", block))
        self.assertTrue(needed)
        self.assertTrue(needed <= options,
                        "unselectable: %s" % (needed - options))

    def test_the_journal_names_the_sections_own_characters(self):
        from tutor.models import Question

        self._seed()
        q = self._set("Section 1 · Journal").questions.order_by("order").first()
        self.assertEqual(q.response_type, Question.TYPE_CHARACTERS)
        self.assertEqual(q.character_names,
                         ["Naima", "Rashida", "Father", "Saleem"])
        # Section 4 swaps Rashida and Saleem for the widow.
        q4 = self._set("Section 4 · Journal").questions.order_by("order").first()
        self.assertIn("The Widow", q4.character_names)
        self.assertNotIn("Rashida", q4.character_names)

    def test_the_final_draft_is_recopied_by_hand(self):
        """The guide asks for it 'using your best penmanship'. The rough draft
        stays typed — it is meant to be revised."""
        from tutor.models import Question

        self._seed()
        rough, final = self._set(
            "Section 1 · Writing Exercise").questions.order_by("order")
        self.assertEqual(rough.response_type, Question.TYPE_PARAGRAPH)
        self.assertEqual(rough.paragraph_sections,
                         ["Introduction / Topic Sentence",
                          "Supporting Sentences", "Concluding Sentence"])
        self.assertEqual(final.response_type, Question.TYPE_HANDWRITING)
        self.assertIn("penmanship", final.prompt)

    def test_discussion_is_teacher_led_not_written(self):
        from tutor.models import QuestionSet

        self._seed()
        qset = self._set("Section 3 · Discussion")
        self.assertEqual(qset.mode, QuestionSet.MODE_DISCUSSION)
        self.assertEqual(qset.questions.count(), 8)

    def test_the_pages_render_for_her(self):
        self._seed()
        html = self._page("Section 1 · Vocabulary")
        self.assertIn("vocab-matching", html)
        self.assertIn("vocab-fillblank", html)
        self.assertIn("threshold", html)
        self.assertIn("the sill of a door", html)
        self.assertEqual(html.count("vocab-blank-select"), 6)
        html = self._page("Section 1 · Journal")
        self.assertEqual(html.count("character-field"), 4)

    def test_a_dry_run_writes_nothing(self):
        from io import StringIO
        from django.core.management import call_command
        from curricula.models import Curriculum, Lesson

        out = StringIO()
        call_command("seed_rickshaw_girl", "--for-user", "rg", "--dry-run",
                     stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_reseeding_restores_a_question_that_was_tampered_with(self):
        from tutor.models import Question

        self._seed()
        q = self._set("Section 1 · Vocabulary").questions.order_by("order").first()
        Question.objects.filter(pk=q.pk).update(
            response_type=Question.TYPE_TEXT, passage="", prompt="STALE")
        self._seed()
        q.refresh_from_db()
        self.assertEqual(q.response_type, Question.TYPE_MATCHING)
        self.assertIn("threshold", q.passage)

    def test_reseeding_changes_nothing(self):
        from tutor.models import Question, QuestionSet

        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)


class RickshawContentTests(TestCase):
    """Semantic spot-checks on the transcription.

    The bijection check in RickshawGirlTests cannot catch a mis-pairing: swap
    two definition numbers and it is still a bijection. These pin the meaning,
    across every section rather than only the first.
    """

    def test_each_word_means_what_its_definition_says(self):
        from tutor.rickshaw import SECTIONS, section_by_number

        # (section, word, a phrase that must appear in ITS definition)
        for n, word, phrase in [
            (1, "hut", "shelter"), (1, "rickshaw", "two-wheeled"),
            (1, "threshold", "sill"), (1, "grime", "dirt"),
            (2, "coiled", "wound circles"), (2, "recognize", "know and remember"),
            (2, "lotus", "flowering plant"), (2, "disguise", "change the usual appearance"),
            (3, "idle", "doing nothing"), (3, "numb", "unable to feel"),
            (3, "symmetry", "two sides or halves"), (3, "dim", "not bright"),
            (4, "decent", "polite, moral"), (4, "jubilant", "great joy"),
            (4, "fierce", "wild or threatening"), (4, "scold", "find fault"),
        ]:
            section = section_by_number(n)
            number = dict(section["vocab"])[word]
            definition = section["definitions"][number - 1]
            self.assertIn(phrase, definition,
                          "section %d: %r points at %r" % (n, word, definition))
        self.assertEqual(len(SECTIONS), 4)

    def test_each_blank_takes_the_word_that_fits_it(self):
        from tutor.rickshaw import section_by_number

        # (section, a phrase from the sentence, the word that belongs in it)
        for n, phrase, word in [
            (1, "toured part of the city", "rickshaw"),
            (1, "kitchen sink", "grime"),
            (1, "carried his bride across", "threshold"),
            (2, "rattlesnake", "coiled"),
            (2, "Hulk costume", "disguise"),
            (2, "sour milk", "grim"),
            (3, "sit around and be", "idle"),
            (3, "look in the mirror", "symmetry"),
            (3, "difficult to read", "dim"),
            (4, "barked wildly", "fierce"),
            (4, "at the wedding", "jubilant"),
            (4, "water buffalo", "labored"),
        ]:
            blanks = section_by_number(n)["blanks"]
            match = [(s, a) for s, a in blanks if phrase in s]
            self.assertEqual(len(match), 1,
                             "section %d: %r matched %d sentences" % (n, phrase, len(match)))
            self.assertEqual(match[0][1], word,
                             "section %d: %r wants %r" % (n, phrase, match[0][1]))

    def test_each_section_journals_its_own_characters(self):
        from tutor.rickshaw import section_by_number

        self.assertEqual(section_by_number(1)["characters"],
                         ["Naima", "Rashida", "Father", "Saleem"])
        self.assertEqual(section_by_number(4)["characters"],
                         ["Naima", "The Widow", "Mother", "Father"])
        for n in (1, 2, 3, 4):
            self.assertIn("Naima", section_by_number(n)["characters"])

    def test_the_writing_prompts_are_the_guides_own(self):
        from tutor.rickshaw import section_by_number

        for n, phrase in ((1, "alpanas on holidays"), (2, "costing her family"),
                          (3, "crazy idea"), (4, "microfinance")):
            self.assertIn(phrase, section_by_number(n)["writing_prompt"])


class RickshawChildFacingTests(RickshawGirlTests):
    """What a nine-year-old working alone actually meets on the page.

    A UI review of the first build found these missing or wrong; they are the
    difference between a page she can finish by herself and one she stalls on.
    """

    def test_she_can_open_a_nudge_on_the_work_she_does_alone(self):
        """The sibling course carries 31 of these. Shipping with none is the
        single thing that made the two feel like different products — and the
        hint is the mechanism a child alone uses to get unstuck."""
        from tutor.models import Question, QuestionSet
        from tutor.rickshaw import CURRICULUM_NAME

        self._seed()
        sets = QuestionSet.objects.filter(
            lesson__chapter__curriculum__name=CURRICULUM_NAME,
            mode=QuestionSet.MODE_STUDENT)
        for qset in sets:
            hinted = qset.questions.exclude(hint="").count()
            if "Comprehension" in qset.title:
                # Deliberately none. The only thing a nudge could say here is
                # already the intro directly above, and seven identical ones per
                # set teach her the 💡 is not worth tapping — which costs her on
                # the pages where the nudges genuinely help.
                self.assertEqual(hinted, 0, qset.title)
            else:
                self.assertEqual(hinted, qset.questions.count(),
                                 "%s has unhinted questions" % qset.title)
        self.assertGreater(
            Question.objects.filter(question_set__in=sets).exclude(hint="").count(),
            25)

    def test_the_journal_chips_name_the_three_different_boxes(self):
        """They read 'Character · Comprehension · Comprehension' — two adjacent
        chips repeating one word while the prompts under them said SETTING and
        PLOT. A child reads the chip as the box's label."""
        self._seed()
        for n in (1, 2, 3, 4):
            chips = [q.get_category_display() for q in
                     self._set("Section %d · Journal" % n).questions.order_by("order")]
            self.assertEqual(chips, ["Character", "Setting", "Plot"])

    def test_the_fill_in_never_claims_the_word_is_in_the_list_above(self):
        """Section 4's blanks want 'scolded' and 'labored' while the matching
        list prints 'scold' and 'labor'. Telling her to use a word 'from the
        list above' sends her hunting for one that isn't there."""
        self._seed()
        fill = self._set("Section 4 · Vocabulary").questions.order_by("order")[1]
        self.assertNotIn("from the vocabulary list above", fill.prompt)
        self.assertIn("ending", fill.prompt)

    def test_the_final_project_is_scaffolded_not_a_wall_of_prose(self):
        """It opened with five weeks of scheduling admin, then asked which
        option she chose BEFORE listing the options, in a 233-word prompt."""
        self._seed()
        qset = self._set("Section 5 · Glean: Final Project")
        self.assertEqual(qset.questions.count(), 3)
        longest = max(len(q.prompt.split()) for q in qset.questions.all())
        self.assertLess(longest, 30)
        # The options are shown up front, each with a short scannable name.
        self.assertIn("Build a diorama", qset.intro)
        self.assertIn("Tradition poster", qset.intro)
        self.assertNotIn("designed to be completed in five weeks", qset.intro)


class PoetrySmallFormsTests(TestCase):
    """Kaylin's Poetry: Small Forms — the grid, the attachments, the method."""

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from portal.tokens import make_portal_token

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="po", email="po@e.com", password="pw")
        cls.family = Family.objects.create(name="PO Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07",
            family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_poetry_kaylin", "--for-user", "po", stdout=StringIO())

    def _set(self, number):
        from tutor.models import QuestionSet
        from tutor.poetry import CURRICULUM_NAME
        return QuestionSet.objects.get(
            lesson__number=number,
            lesson__chapter__curriculum__name=CURRICULUM_NAME,
            lesson__chapter__curriculum__parent=self.parent)

    def _page(self, number):
        return self.client.get(reverse(
            "portal:portal_questions", args=[self.token, self._set(number).pk])
        ).content.decode()

    def test_twelve_sections_of_four_steps(self):
        from curricula.models import Lesson
        from tutor.models import Question, QuestionSet
        from tutor.poetry import CURRICULUM_NAME

        self._seed()
        lessons = Lesson.objects.filter(
            chapter__curriculum__name=CURRICULUM_NAME,
            chapter__curriculum__parent=self.parent)
        self.assertEqual(lessons.count(), 12)
        sets = QuestionSet.objects.filter(lesson__in=lessons)
        self.assertEqual(sets.count(), 12)
        self.assertEqual(
            Question.objects.filter(question_set__in=sets).count(), 48)
        for qset in sets:
            self.assertEqual(
                qset.questions.exclude(hint="").count(), 4, qset.title)

    def test_the_grid_matches_each_forms_own_pattern(self):
        """The whole point: nonet counts down 9..1, cinquain climbs 2-4-6-8-2.
        A wrong grid teaches her the wrong form."""
        self._seed()
        html = self._page(8)                       # nonet
        import re
        targets = re.findall(r'data-target="(\d*)"', html)
        self.assertEqual([t for t in targets if t],
                         ["9", "8", "7", "6", "5", "4", "3", "2", "1"])
        html = self._page(5)                       # cinquain
        targets = [t for t in re.findall(r'data-target="(\d*)"', html) if t]
        self.assertEqual(targets, ["2", "4", "6", "8", "2"])

    def test_tricube_breaks_into_three_stanzas(self):
        self._seed()
        html = self._page(7)
        self.assertEqual(html.count("po-grid-stanza"), 2)   # before lines 4 and 7

    def test_a_form_with_no_syllable_rule_gets_lines_not_targets(self):
        import re

        self._seed()
        html = self._page(10)                      # gogyohka
        self.assertEqual([t for t in re.findall(r'data-target="(\d*)"', html) if t], [])
        self.assertIn("no syllable rule", html)
        # five rows for five lines
        self.assertEqual(html.count('aria-label="Line '), 5)

    def test_the_original_pages_are_attached_and_exist_on_disk(self):
        """Her guide's worked examples are handwritten; she reads the real
        pages. Every section links its own pages, and every file exists."""
        import os
        from django.conf import settings
        from tutor.poetry import SECTIONS, page_images

        self._seed()
        for s in SECTIONS:
            for img in page_images(s):
                self.assertTrue(
                    os.path.exists(os.path.join(
                        settings.BASE_DIR, "static", img)),
                    "%s missing" % img)
        html = self._page(9)                       # shadorma
        self.assertIn("poetry/shadorma/p1", html)
        self.assertNotIn("poetry/haiku/p1", html)  # its own pages only

    def test_the_sevenling_grid_carries_the_guides_line_roles(self):
        self._seed()
        html = self._page(11)
        self.assertIn('placeholder="the twist"', html)
        self.assertEqual(html.count('placeholder="first of three"'), 2)

    def test_the_stored_answer_is_readable_plain_text(self):
        """The grid writes title-then-lines into the normal answer field, so
        the grader and the printed report need nothing new."""
        from tutor.models import ResponseSheet

        self._seed()
        qset = self._set(1)
        final = qset.questions.order_by("order").last()
        sheet = ResponseSheet.objects.create(
            question_set=qset, child=self.child,
            answers={str(final.pk):
                     "Backyard Morning\ncold dew on the grass\n"
                     "a sparrow lands and listens\nthe kettle whistles"})
        self.assertIn("sparrow", sheet.as_worklog_text())
        self.assertNotIn("strokes", sheet.as_worklog_text())

    def test_a_dry_run_writes_nothing(self):
        from io import StringIO
        from django.core.management import call_command
        from curricula.models import Curriculum, Lesson

        out = StringIO()
        call_command("seed_poetry_kaylin", "--for-user", "po", "--dry-run",
                     stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_reseeding_restores_a_tampered_question(self):
        from tutor.models import Question

        self._seed()
        q = self._set(1).questions.order_by("order").first()
        Question.objects.filter(pk=q.pk).update(prompt="STALE", hint="")
        self._seed()
        q.refresh_from_db()
        self.assertTrue(q.prompt.startswith("Craft a detailed sentence"))
        self.assertNotEqual(q.hint, "")

    def test_reseeding_changes_nothing(self):
        from tutor.models import Question, QuestionSet

        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)


class PoetryGuideTests(PoetrySmallFormsTests):
    """The parent guide."""

    def _guide(self):
        from curricula.models import Curriculum
        from tutor.poetry import CURRICULUM_NAME

        self._seed()
        cur = Curriculum.objects.get(name=CURRICULUM_NAME, parent=self.parent)
        self.client.force_login(self.parent)
        return cur, self.client.get(reverse("tutor:poetry_guide", args=[cur.pk]))

    def test_it_shows_all_twelve_forms_with_their_patterns(self):
        _cur, resp = self._guide()
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        for name in ("haiku", "tanka", "shadorma", "sevenling"):
            self.assertIn(name, html)
        self.assertIn("9-8-7-6-5-4-3-2-1", html)      # the nonet countdown
        self.assertIn("3-4-3-3-7-5", html)            # shadorma
        self.assertIn("no syllable rule", html)       # gogyohka and friends

    def test_progress_counts_submitted_sections(self):
        from django.utils import timezone
        from tutor.models import ResponseSheet

        self._seed()
        ResponseSheet.objects.create(
            question_set=self._set(1), child=self.child, answers={},
            status=ResponseSheet.SUBMITTED, submitted_at=timezone.now())
        _cur, resp = self._guide()
        row = resp.context["children"][0]
        self.assertEqual(row["sections_done"], 1)
        self.assertEqual(row["next_section"]["number"], 2)

    def test_the_guide_is_not_reachable_for_other_curricula(self):
        from curricula.models import Curriculum

        self._seed()
        other = Curriculum.objects.create(
            parent=self.parent, name="Something Else", subject="Math",
            family=self.family)
        self.client.force_login(self.parent)
        self.assertEqual(
            self.client.get(
                reverse("tutor:poetry_guide", args=[other.pk])).status_code, 404)

    def test_the_link_shows_only_on_this_curriculum(self):
        from curricula.models import Curriculum

        cur, _resp = self._guide()
        detail = self.client.get(
            reverse("curricula:curriculum_detail", args=[cur.pk])).content.decode()
        self.assertIn("poetry-guide", detail)
        other = Curriculum.objects.create(
            parent=self.parent, name="Something Else", subject="Math",
            family=self.family)
        detail = self.client.get(
            reverse("curricula:curriculum_detail", args=[other.pk])).content.decode()
        self.assertNotIn("poetry-guide", detail)


class MissAgnesTests(TestCase):
    """Violet's Blackbird Level 3 guide for The Year of Miss Agnes.

    The seed is Rickshaw Girl's builders pointed at this book's module, so the
    tests pin what actually differs: the chapter splits, the two-character
    journals, the discussion counts, and that no blank needs an inflected form.
    """

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from portal.tokens import make_portal_token

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="ag", email="ag@e.com", password="pw")
        cls.family = Family.objects.create(name="AG Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_year_of_miss_agnes", "--for-user", "ag",
                     stdout=StringIO())

    def _set(self, title):
        from tutor.agnes import CURRICULUM_NAME
        from tutor.models import QuestionSet
        return QuestionSet.objects.get(
            title=title, lesson__chapter__curriculum__name=CURRICULUM_NAME,
            lesson__chapter__curriculum__parent=self.parent)

    def test_the_books_own_shape(self):
        from curricula.models import Chapter, Lesson
        from tutor.agnes import CURRICULUM_NAME
        from tutor.models import Question, QuestionSet

        self._seed()
        self.assertEqual(Chapter.objects.filter(
            curriculum__name=CURRICULUM_NAME,
            curriculum__parent=self.parent).count(), 5)
        lessons = Lesson.objects.filter(
            chapter__curriculum__name=CURRICULUM_NAME,
            chapter__curriculum__parent=self.parent)
        self.assertEqual(lessons.count(), 21)
        sets = QuestionSet.objects.filter(lesson__in=lessons)
        # 4 x 5 + the final project + the hands-on one beside it.
        self.assertEqual(sets.count(), 22)
        gleans = sets.filter(title__contains="Glean")
        self.assertEqual(gleans.count(), 2)
        self.assertTrue(gleans.filter(title__endswith="Final Project").exists(),
                        "the guide's own options must still be offered")
        self.assertEqual(
            Question.objects.filter(question_set__in=sets).count(), 89)

    def test_journals_name_this_books_pairs_not_rickshaws_four(self):
        from tutor.models import Question

        self._seed()
        q = self._set("Section 1 · Journal").questions.order_by("order").first()
        self.assertEqual(q.response_type, Question.TYPE_CHARACTERS)
        self.assertEqual(len(q.character_names), 2)
        self.assertIn("Fred", q.character_names)
        q4 = self._set("Section 4 · Journal").questions.order_by("order").first()
        self.assertIn("Miss Agnes", q4.character_names)

    def test_every_blank_is_answerable_with_no_inflection_needed(self):
        """This guide, unlike Rickshaw §4, needs no inflected forms — so the
        bank must equal the printed word list and the "ending changed" sentence
        must NOT appear in any fill-in prompt."""
        import json

        self._seed()
        for n in (1, 2, 3, 4):
            fill = self._set("Section %d · Vocabulary" % n).questions.order_by("order")[1]
            data = json.loads(fill.passage)
            bank = set(data["words"])
            for s in data["sentences"]:
                self.assertIn(s["word"], bank, "section %d" % n)
            self.assertNotIn("ending changed", fill.prompt)

    def test_discussion_counts_follow_the_book(self):
        from tutor.models import QuestionSet

        self._seed()
        for n, count in ((1, 5), (2, 8), (3, 6), (4, 5)):
            qset = self._set("Section %d · Discussion" % n)
            self.assertEqual(qset.mode, QuestionSet.MODE_DISCUSSION)
            self.assertEqual(qset.questions.count(), count, "section %d" % n)

    def test_the_glean_page_offers_the_six_options(self):
        self._seed()
        qset = self._set("Section 5 · Glean: Final Project")
        self.assertEqual(qset.questions.count(), 3)   # pick / plan / reflect
        self.assertIn("Alaska", qset.intro)
        self.assertIn("Miss Agnes", qset.intro)

    def test_the_page_renders_for_her(self):
        self._seed()
        html = self.client.get(reverse(
            "portal:portal_questions",
            args=[self.token, self._set("Section 1 · Journal").pk])
        ).content.decode()
        self.assertEqual(html.count("character-field"), 2)
        self.assertIn("Need a nudge", html)

    def test_a_dry_run_writes_nothing(self):
        from io import StringIO
        from django.core.management import call_command
        from curricula.models import Curriculum, Lesson

        out = StringIO()
        call_command("seed_year_of_miss_agnes", "--for-user", "ag", "--dry-run",
                     stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_reseeding_changes_nothing(self):
        from tutor.models import Question, QuestionSet

        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)


class MissAgnesContentTests(TestCase):
    """Semantic spot-checks — a bijection survives swapping two numbers, so
    these pin the meaning, at least two words per section."""

    def test_each_word_means_what_its_definition_says(self):
        from tutor.agnes import section_by_number

        for n, word, phrase in [
            (1, "harness", "working animal"), (1, "quill", "feather"),
            (1, "moccasins", "soft leather"),
            (2, "holler", "shout"), (2, "geography", "earth"),
            (2, "hunker", "squat"),
            (3, "microscope", "small particles"), (3, "echo", "reflected"),
            (3, "brittle", "easily broken"),
            (4, "invent", "create"), (4, "gloomy", "dark"),
            (4, "brag", "highly of oneself"),
        ]:
            section = section_by_number(n)
            number = dict(section["vocab"])[word]
            definition = section["definitions"][number - 1]
            self.assertIn(phrase, definition,
                          "S%d: %r points at %r" % (n, word, definition))

    def test_each_section_journals_its_own_pair(self):
        from tutor.agnes import SECTIONS

        pairs = [set(s["characters"]) for s in SECTIONS]
        self.assertEqual(len(pairs), 4)
        for p in pairs:
            self.assertEqual(len(p), 2)
        self.assertIn("Miss Agnes", pairs[2] | pairs[3])


class OneTrue3Tests(TestCase):
    """Volume C3: twenty rhetorical devices.

    Its shape is NOT C1's — no Sentence 2, two copy tasks per lesson — so these
    pin the differences rather than re-testing the shared machinery.
    """

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from core.models import Family, FamilyMembership
        from portal.tokens import make_portal_token

        User = get_user_model()
        cls.parent = User.objects.create_user(
            username="o3", email="o3@e.com", password="pw")
        cls.family = Family.objects.create(name="O3 Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        # The publisher puts this volume at Grades 6-8, so it is Kaylin's.
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07",
            family=cls.family)
        # C1 is Violet's (Grades 4-5) and one test below seeds it, so she has
        # to exist here too.
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_onetrue3_kaylin", "--for-user", "o3", stdout=StringIO())

    def _set(self, week, practice=False):
        from tutor.models import QuestionSet
        from tutor.onetrue3 import CURRICULUM_NAME
        qs = QuestionSet.objects.filter(
            lesson__number=week,
            lesson__chapter__curriculum__name=CURRICULUM_NAME,
            lesson__chapter__curriculum__parent=self.parent)
        return (qs.filter(title__endswith="now you try!").get() if practice
                else qs.exclude(title__endswith="now you try!").get())

    def _page(self, week=1, practice=False):
        return self.client.get(reverse(
            "portal:portal_questions",
            args=[self.token, self._set(week, practice).pk])).content.decode()

    def test_twenty_weeks_each_a_lesson_and_a_practice(self):
        from curricula.models import Lesson
        from tutor.models import QuestionSet
        from tutor.onetrue3 import CURRICULUM_NAME

        self._seed()
        lessons = Lesson.objects.filter(
            chapter__curriculum__name=CURRICULUM_NAME,
            chapter__curriculum__parent=self.parent)
        self.assertEqual(lessons.count(), 20)
        for lesson in lessons:
            self.assertEqual(
                QuestionSet.objects.filter(lesson=lesson).count(), 2,
                "week %s" % lesson.number)

    def test_both_copy_tasks_take_the_pen_and_sit_where_the_book_prints_them(self):
        """Task 1 copies the EXPLANATION; the copy-the-example task is printed
        fourth, right after 'read it silently'. The transcription lifted the
        latter into its own field, so getting it back into position is the one
        thing this seed has to do carefully."""
        from tutor.models import Question

        self._seed()
        qs = list(self._set(1).questions.order_by("order"))
        self.assertTrue(qs[0].prompt.startswith("Read and copy the explanation"))
        self.assertEqual(qs[0].response_type, Question.TYPE_HANDWRITING)
        self.assertIn("silently", qs[2].prompt)
        self.assertEqual(qs[3].prompt, "Copy the example sentence.")
        self.assertEqual(qs[3].response_type, Question.TYPE_HANDWRITING)
        # Everything else is typed, so the grader can read it.
        for q in qs[1:3] + qs[4:]:
            self.assertEqual(q.response_type, Question.TYPE_TEXT, q.prompt[:40])
        # …and the POSITIONS hold in every week, not just the first. Counting
        # two pens per week would still pass if the copy task were inserted in
        # the wrong place, which is the mistake worth catching.
        for n in range(1, 21):
            week = list(self._set(n).questions.order_by("order"))
            pens = [i for i, q in enumerate(week)
                    if q.response_type == Question.TYPE_HANDWRITING]
            self.assertEqual(pens, [0, 3], "week %d" % n)
            self.assertTrue(week[0].prompt.startswith("Read and copy the explanation"),
                            "week %d" % n)
            self.assertEqual(week[3].prompt, "Copy the example sentence.",
                             "week %d" % n)

    def test_the_page_does_not_invent_a_sentence_two(self):
        """This volume has none — one Example box IS the model. C1's header
        would otherwise print an empty 'Sentence 2' chip."""
        self._seed()
        html = self._page(1)
        self.assertNotIn("Sentence 2", html)
        self.assertIn(">Example<", html)
        self.assertIn("Though the torrential downpour", html)

    def test_her_own_sentences_are_handwritten(self):
        from tutor.models import Question

        self._seed()
        practice = list(self._set(1, practice=True).questions.order_by("order"))
        self.assertEqual(len(practice), 5)
        self.assertEqual([q.response_type for q in practice],
                         [Question.TYPE_HANDWRITING] * 5)
        self.assertTrue(practice[0].prompt.startswith("Sentence 1 of 5 —"))
        self.assertTrue(practice[1].prompt.startswith("Sentence 2 of 5"))
        # The long instruction appears once, not five times.
        self.assertEqual(
            sum("antanagoge" in q.prompt.lower() for q in practice), 1)

    def test_the_printed_quirks_are_preserved(self):
        """Four weeks carry the guide's own oddities verbatim, with notes."""
        from tutor.onetrue3 import WEEKS

        noted = [w for w in WEEKS if w.get("note")]
        self.assertGreaterEqual(len(noted), 4)
        text = " ".join(q for w in WEEKS for q in w["questions_one"])
        self.assertIn("paranthesis", text)
        self.assertIn("elliminates", text)
        self.assertIn("Why?.", text)
        self.assertIn("write rewrite", text)

    def test_every_question_carries_a_nudge(self):
        self._seed()
        for n in (1, 10, 20):
            for practice in (False, True):
                qset = self._set(n, practice)
                self.assertEqual(qset.questions.exclude(hint="").count(),
                                 qset.questions.count(), qset.title)

    def test_a_dry_run_writes_nothing(self):
        from io import StringIO
        from django.core.management import call_command
        from curricula.models import Curriculum, Lesson

        out = StringIO()
        call_command("seed_onetrue3_kaylin", "--for-user", "o3", "--dry-run",
                     stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_reseeding_changes_nothing(self):
        from tutor.models import Question, QuestionSet

        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)

    def test_volume_c1_still_renders_its_own_shape(self):
        """The two volumes share a header; C3's changes must not strip C1's
        Sentence 2, which is live in production."""
        from io import StringIO
        from django.core.management import call_command
        from tutor.models import QuestionSet
        from tutor.onetrue import CURRICULUM_NAME as C1

        from portal.tokens import make_portal_token

        call_command("seed_onetrue_violet", "--for-user", "o3", stdout=StringIO())
        qset = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__name=C1,
            lesson__chapter__curriculum__parent=self.parent).exclude(
            title__endswith="now you try!").get()
        html = self.client.get(reverse(
            "portal:portal_questions",
            args=[make_portal_token(self.violet), qset.pk])).content.decode()
        self.assertIn("Sentence 2", html)
        self.assertIn("Margaret Wise Brown", html)
        self.assertIn(">Sentence 1<", html)
        # The read-aloud line: branching the template for C3 once hoisted "the"
        # outside the {% if %}, so all twenty of Violet's LIVE pages read
        # "Read the Sentence 1 silently". Checking only the chip missed it.
        import re
        flat = re.sub(r"\s+", " ", html)
        self.assertIn("Read Sentence 1 silently", flat)
        self.assertNotIn("Read the Sentence 1", flat)
        # …and her practice page is untouched too.
        practice = QuestionSet.objects.filter(
            lesson__number=1, lesson__chapter__curriculum__name=C1,
            lesson__chapter__curriculum__parent=self.parent,
            title__endswith="now you try!").get()
        phtml = self.client.get(reverse(
            "portal:portal_questions",
            args=[make_portal_token(self.violet), practice.pk])).content.decode()
        self.assertIn("Now you try", phtml)
        # The MODEL sentence is withheld on the practice page. ("Sentence 1"
        # itself still appears there — the practice prompts are numbered
        # "Sentence 1 of 5".)
        self.assertNotIn("chuckleberry blossoms", phtml)


class EssayVolume2Tests(TestCase):
    """Intro to Composition: The Essay, Volume 2 — Kaylin's ten weeks.

    The two halves of each lesson are different shapes, and most of what can go
    wrong here is one half quietly acquiring the other's furniture, so these
    pin the halves against each other rather than testing either alone.
    """

    @classmethod
    def setUpTestData(cls):
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(
            username="es", email="es@e.com", password="pw")
        cls.family = Family.objects.create(name="Essay Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07",
            family=cls.family)
        cls.token = make_portal_token(cls.child)

    def _seed(self):
        call_command("seed_essay_kaylin", "--for-user", "es", stdout=StringIO())

    def _set(self, week):
        from tutor.essay import CURRICULUM_NAME
        from tutor.models import QuestionSet
        return QuestionSet.objects.get(
            lesson__number=week,
            lesson__chapter__curriculum__name=CURRICULUM_NAME,
            lesson__chapter__curriculum__parent=self.parent)

    def _page(self, week):
        return self.client.get(reverse(
            "portal:portal_questions",
            args=[self.token, self._set(week).pk])).content.decode()

    # -- the book's own arithmetic -----------------------------------------

    def test_the_blueprint_adds_up_to_the_thirty_sentences_it_claims(self):
        """Every paragraph must list exactly as many lines as it says it has.

        The blueprint is the spine: it drives the rough-draft boxes, the
        thirty-item checklist AND the size of each box, so a paragraph whose
        line list and sentence count disagree corrupts three things at once.
        """
        from tutor import essay

        self.assertEqual(essay.blueprint_total(), 30)
        for para in essay.BLUEPRINT:
            self.assertEqual(len(para["lines"]), para["sentences"], para["tag"])
        self.assertEqual([p["sentences"] for p in essay.BLUEPRINT],
                         [3, 8, 8, 8, 3])

    def test_the_teacher_form_sections_sum_to_the_printed_fifty(self):
        from tutor import essay

        self.assertEqual(essay.TOTAL_POINTS, 50)
        self.assertEqual(sum(t for _, t, _ in essay.TEACHER_FORM), 50)
        for name, total, items in essay.TEACHER_FORM:
            self.assertEqual(sum(v for _, v in items), total, name)

    def test_the_rubric_keeps_all_five_bands_and_all_their_criteria(self):
        """The grader is handed these verbatim; a dropped bullet is a real loss."""
        from tutor import essay

        self.assertEqual([n for n, _ in essay.EVALUATION_RUBRIC],
                         ["ACCOMPLISHED", "PROFICIENT", "BASIC", "LIMITED", "POOR"])
        for name, criteria in essay.EVALUATION_RUBRIC:
            self.assertEqual(len(criteria), 6, name)

    # -- shape -------------------------------------------------------------

    def test_ten_weeks_five_essays_two_weeks_each(self):
        from tutor.essay import CURRICULUM_NAME

        self._seed()
        lessons = Lesson.objects.filter(
            chapter__curriculum__name=CURRICULUM_NAME,
            chapter__curriculum__parent=self.parent).order_by("number")
        self.assertEqual([x.number for x in lessons], list(range(1, 11)))
        self.assertEqual(Curriculum.objects.get(
            name=CURRICULUM_NAME, parent=self.parent).grade_level, "G07")

    def test_the_two_halves_of_a_lesson_are_different_shapes(self):
        """Odd week: the guide's pre-writing, typed. Even week: one essay.

        Pinned against each other because the failure mode is one half
        acquiring the other's furniture — a drafting week full of short-answer
        boxes, or a pre-writing week that hands her a paragraph widget.
        """
        self._seed()
        for start in (1, 3, 5, 7, 9):
            odd = list(self._set(start).questions.all())
            even = list(self._set(start + 1).questions.order_by("order"))

            self.assertGreater(len(odd), 15, "week %d" % start)
            self.assertNotIn(Question.TYPE_PARAGRAPH,
                             {q.response_type for q in odd},
                             "week %d must not draft" % start)

            self.assertEqual([q.response_type for q in even],
                             [Question.TYPE_PARAGRAPH, Question.TYPE_SELF_EVAL,
                              Question.TYPE_SELF_EVAL],
                             "week %d" % (start + 1))

    def test_the_rough_draft_boxes_are_the_blueprint_sized_to_its_paragraphs(self):
        """The three BODY paragraphs are eight sentences and need the room.

        The widget used to hardcode "the second box is the tall one" — right
        for a three-part paragraph, and it left two of the three body
        paragraphs of a five-paragraph essay with a two-row box.
        """
        from tutor import essay

        self._seed()
        draft = self._set(2).questions.order_by("order").first()
        self.assertEqual(draft.paragraph_sections, essay.PARAGRAPH_SECTIONS)
        self.assertEqual(draft.paragraph_section_rows, [3, 8, 8, 8, 3])
        self.assertEqual([b["rows"] for b in draft.paragraph_boxes], [3, 8, 8, 8, 3])
        self.assertEqual([b["label"] for b in draft.paragraph_boxes],
                         essay.PARAGRAPH_SECTIONS)

    def test_the_blueprint_checklist_has_one_box_per_sentence_and_names_it(self):
        """Thirty boxes, each saying which paragraph it belongs to.

        Flattened, "Opener" and "Clincher" each appear three times; without the
        paragraph tag she cannot tell which of the three she is ticking.
        """
        self._seed()
        checklist = self._set(2).questions.order_by("order")[1]
        items = checklist.self_eval_items
        self.assertEqual(len(items), 30)
        self.assertEqual(len(set(items)), 30, "every row distinct")
        self.assertTrue(items[0].startswith("P1"))
        self.assertTrue(items[-1].startswith("P5"))
        self.assertIn("Hook", items[0])
        self.assertIn("Twist", items[-1])
        self.assertEqual(sum(1 for i in items if "Opener" in i), 3)
        # A bare checkbox in the book: no "how would you improve this" line.
        self.assertFalse(checklist.self_eval_wants_notes)
        # Two options, because a checkbox has two states. Collapse this to one
        # and every row renders pre-decided, with nothing for her to say.
        self.assertEqual(checklist.self_eval_scale, ["In my draft", "Not yet"])

    def test_the_self_evaluation_is_the_guides_twelve_components(self):
        self._seed()
        form = self._set(2).questions.order_by("order")[2]
        self.assertEqual(len(form.self_eval_items), 12)
        self.assertEqual(form.self_eval_items[0], "Follows Essay Format")
        self.assertEqual(form.self_eval_items[-1], "Vocal Creativity")
        self.assertEqual(form.self_eval_scale,
                         ["Excellent", "Satisfactory", "Needs to Improve"])
        self.assertTrue(form.self_eval_wants_notes)

    def test_the_self_check_groups_only_ever_ask_questions(self):
        """"Now write the final pair of sentences and the clincher." is an
        instruction, and was briefly being offered to her as something to rate
        Yes / Not yet. Every self-check the book prints is a question."""
        from tutor.essay_lessons import LESSONS

        for lesson in LESSONS:
            for step in lesson["steps"]:
                for check in step.get("checks", []):
                    self.assertTrue(check.endswith("?"),
                                    "L%d: %r" % (lesson["number"], check))
        self._seed()
        for week in (1, 3, 5, 7, 9):
            for q in self._set(week).questions.filter(
                    response_type=Question.TYPE_SELF_EVAL):
                for item in q.self_eval_items:
                    self.assertTrue(item.endswith("?"),
                                    "week %d: %r" % (week, item))

    def test_the_three_sub_topics_get_three_boxes(self):
        """The page prints three numbered rules, not one three-line box —
        three of the five readers collapsed them, the second reader caught it."""
        from tutor.essay_lessons import LESSONS

        for lesson in LESSONS:
            slots = [p["text"] for step in lesson["steps"]
                     for p in step["prompts"] if "Sub-topic" in p["text"]]
            self.assertEqual(len(slots), 3, "L%d" % lesson["number"])
            self.assertIn("Choose three sub-topics", slots[0])
            self.assertTrue(slots[1].endswith("2 of 3"))

    # -- the printed guide's own mistakes ----------------------------------

    def test_the_guides_typos_are_preserved_and_explained(self):
        """Transcribed verbatim, warned about separately — never silently fixed.

        "complimentary" is the one that matters: the prompt orders her to go
        and research the word, and the word the guide prints is the wrong one.
        """
        from tutor.essay_lessons import LESSONS

        l1 = LESSONS[0]
        vangogh = [p["text"] for step in l1["steps"] for p in step["prompts"]
                   if "Van Gogh" in p["text"]]
        self.assertEqual(len(vangogh), 1)
        self.assertIn("complimentary colors", vangogh[0])
        self.assertNotIn("complementary colors", vangogh[0])
        self.assertIn("COMPLEMENTARY", " ".join(n["text"] for n in l1["notes"]))

        # PS» for P5» — in lessons 1, 3 and 5 only, which is how we know it is
        # the book's own slip and not somebody misreading a scan.
        for lesson in LESSONS:
            texts = " ".join(n["text"] for n in lesson.get("notes", []))
            self.assertEqual("PS»" in texts, lesson["number"] in (1, 3, 5),
                             "L%d" % lesson["number"])

    def test_a_note_appears_only_on_the_week_it_is_about(self):
        """The blueprint-checklist typo belongs to the drafting week; the
        research-the-wrong-word warning belongs to the week that asks."""
        self._seed()
        first, draft = self._page(1), self._page(2)
        self.assertIn("COMPLEMENTARY", first)
        self.assertNotIn("COMPLEMENTARY", draft)
        self.assertIn("PS»", draft)
        self.assertNotIn("PS»", first)

    def test_the_guides_own_pages_are_reachable_while_she_writes(self):
        from tutor import essay

        self._seed()
        html = self._page(2)
        for path, _title in essay.reference_images():
            self.assertIn(path.rsplit(".", 1)[0], html, path)
        self.assertIn("The Model - Descriptive Essay", html)

    # -- what the grader is told -------------------------------------------

    def test_a_self_evaluation_reaches_the_grader_as_her_judgement(self):
        """Not as answers to be marked. A grader handed a column of "Needs to
        Improve" would otherwise mark her down for the very honesty the
        exercise is asking for."""
        self._seed()
        qset = self._set(2)
        form = qset.questions.order_by("order")[2]
        sheet = ResponseSheet.objects.create(
            question_set=qset, child=self.child,
            answers={str(form.pk): json.dumps({
                "ratings": {"0": "Excellent", "2": "Needs to Improve"},
                "notes": {"2": "my hook is boring"}})})
        shown = sheet.answer_display(form)
        self.assertIn("her judgement", shown)
        self.assertIn("1. Follows Essay Format — Excellent", shown)
        self.assertIn("3. Hook Grabs Reader's Attention — Needs to Improve",
                      shown)
        self.assertIn("my hook is boring", shown)
        # Untouched rows stay out rather than reading as unrated failures.
        self.assertNotIn("2. Clearly Communicates", shown)

    def test_an_untouched_self_evaluation_is_not_an_answer(self):
        self._seed()
        qset = self._set(2)
        form = qset.questions.order_by("order")[2]
        sheet = ResponseSheet.objects.create(
            question_set=qset, child=self.child,
            answers={str(form.pk): json.dumps({"ratings": {}, "notes": {}})})
        self.assertEqual(sheet.answer_display(form), "(no answer)")

    def test_the_rubric_hands_over_the_guides_own_form(self):
        from tutor import essay

        self._seed()
        rubric = self._set(2).rubric
        for _name, _total, items in essay.TEACHER_FORM:
            for label, _pts in items:
                self.assertIn(label, rubric)
        self.assertIn("ACCOMPLISHED", rubric)
        self.assertIn("Grade the FINAL DRAFT", rubric)

    # -- the usual guards --------------------------------------------------

    def test_every_week_renders(self):
        self._seed()
        for week in range(1, 11):
            r = self.client.get(reverse(
                "portal:portal_questions", args=[self.token, self._set(week).pk]))
            self.assertEqual(r.status_code, 200, "week %d" % week)

    def test_every_question_carries_a_nudge(self):
        self._seed()
        for week in range(1, 11):
            qset = self._set(week)
            self.assertEqual(qset.questions.exclude(hint="").count(),
                             qset.questions.count(), qset.title)

    def test_a_dry_run_writes_nothing(self):
        out = StringIO()
        call_command("seed_essay_kaylin", "--for-user", "es", "--dry-run",
                     stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_reseeding_changes_nothing(self):
        from tutor.models import QuestionSet

        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)

    def test_the_auditor_catches_a_self_evaluation_with_nothing_to_judge(self):
        self._seed()
        form = self._set(2).questions.order_by("order")[2]
        form.passage = json.dumps({"items": [], "scale": ["Yes", "No"]})
        form.save(update_fields=["passage"])
        out = StringIO()
        # The command exits non-zero when it finds anything — that exit IS the
        # signal, so a clean run here would mean the auditor missed it.
        with self.assertRaises(SystemExit):
            call_command("audit_content", stdout=out)
        self.assertIn("self-evaluation lists no components", out.getvalue())

    def test_the_auditor_catches_a_scale_with_nothing_to_choose_between(self):
        """One option is not a rating — every row renders already decided."""
        self._seed()
        form = self._set(2).questions.order_by("order")[2]
        form.passage = json.dumps({"items": ["Follows Essay Format"],
                                   "scale": ["Excellent"]})
        form.save(update_fields=["passage"])
        out = StringIO()
        with self.assertRaises(SystemExit):
            call_command("audit_content", stdout=out)
        self.assertIn("nothing to choose between", out.getvalue())

    # -- guards the review found missing -----------------------------------

    def test_a_paragraph_question_without_row_sizes_renders_as_it_always_did(self):
        """The ONE line in this change that touches already-live pages.

        Every paragraph question in Rickshaw Girl, Miss Agnes and Essentials in
        Writing predates `section_rows` and must keep the exact shape the
        template used to hardcode: `{% if forloop.counter == 2 %}4{% else %}2`,
        i.e. the SECOND box tall and the rest short, whatever the section count.
        """
        from tutor.models import QuestionSet

        self._seed()
        qset = QuestionSet.objects.create(
            family=self.family, title="legacy", status=QuestionSet.APPROVED,
            lesson=Lesson.objects.filter(
                chapter__curriculum__parent=self.parent).first())
        for sections, expected in (
                (["Topic", "Support", "Conclusion"], [2, 4, 2]),
                (["A", "B"], [2, 4]),
                (["only"], [2]),
                (["a", "b", "c", "d", "e"], [2, 4, 2, 2, 2]),
        ):
            q = Question.objects.create(
                question_set=qset, order=1, prompt="p",
                response_type=Question.TYPE_PARAGRAPH,
                passage=json.dumps({"sections": sections}))
            self.assertEqual(q.paragraph_section_rows, expected, sections)
            self.assertEqual([b["rows"] for b in q.paragraph_boxes], expected)
            self.assertEqual([b["label"] for b in q.paragraph_boxes], sections)
            q.delete()

        # And a question with no passage at all still gets the default sections.
        bare = Question.objects.create(
            question_set=qset, order=2, prompt="p",
            response_type=Question.TYPE_PARAGRAPH)
        self.assertEqual(bare.paragraph_section_rows, [2, 4, 2])

    def test_the_self_evaluation_actually_renders_as_a_rating_widget(self):
        """Without this, deleting the template branch falls through to the
        generic textarea — which prints the stored JSON into a text box — and
        every test still passes, because they only check for a 200."""
        self._seed()
        html = self._page(2)
        self.assertIn("selfeval-widget", html)
        self.assertIn('class="se-rating"', html)
        self.assertIn("Needs to Improve", html)
        self.assertIn("Follows Essay Format", html)
        # The blueprint checklist's thirty rows are there and are radio inputs,
        # not a textarea holding raw JSON.
        self.assertIn("P1 · Introduction — Hook", html)
        self.assertNotIn('&quot;ratings&quot;', html)

    def test_the_widget_and_the_grader_agree_on_how_a_rating_is_keyed(self):
        """The widget writes ratings keyed by the component's INDEX and the
        formatter reads them back the same way. Shift one and every rating
        slides onto the wrong component with the last one silently lost —
        which no hand-built-JSON test can see."""
        import re

        self._seed()
        html = self._page(2)
        form = self._set(2).questions.order_by("order")[2]
        indexes = re.findall(r'class="se-item" data-index="(\d+)"', html)
        # Both self-evaluations on the page, each keyed 0..n-1 in printed order.
        self.assertEqual(indexes,
                         [str(i) for i in range(30)] + [str(i) for i in range(12)])

        # The last component must be reachable: key it the way the widget does
        # and the formatter must find it.
        last = len(form.self_eval_items) - 1
        sheet, _ = ResponseSheet.objects.update_or_create(
            question_set=self._set(2), child=self.child,
            defaults={"answers": {str(form.pk): json.dumps(
                {"ratings": {str(last): "Excellent"}, "notes": {}})}})
        self.assertIn("12. Vocal Creativity — Excellent",
                      sheet.answer_display(form))

    def test_every_reference_page_exists_on_disk(self):
        """Under ManifestStaticFilesStorage a missing static file does not
        degrade — it raises, and takes the drafting week down with it. The
        render test cannot catch a typo'd page number because it iterates the
        same list the template does."""
        from django.contrib.staticfiles import finders
        from tutor import essay

        for path, title in essay.reference_images():
            self.assertIsNotNone(finders.find(path), path)
            self.assertTrue(title.strip(), path)

    def test_the_labelled_model_essay_is_one_of_the_pages_offered(self):
        """The page tells her the model has "every part labelled in the
        margin". Folio 14 is the plain prose; folio 15 is the labelled one, and
        it was committed but left out of the list — so the promise pointed at
        an essay with nothing marked on it."""
        from tutor import essay

        folios = [p["folio"] for p in essay.REFERENCE_PAGES]
        self.assertIn(15, folios)
        self.assertEqual(folios, sorted(folios), "printed order")
        labelled = [p for p in essay.REFERENCE_PAGES if p["folio"] == 15][0]
        self.assertIn("labelled", labelled["title"])

    def test_the_drafting_week_is_the_even_one(self):
        """`is_draft_week` decides whether the blueprint opens expanded and
        whether the title says "(cont.)". It is computed separately from the
        note scoping, so the note test cannot catch it being inverted."""
        self._seed()
        for week in range(1, 11):
            html = self._page(week)
            self.assertEqual("(cont.)" in html, week % 2 == 0, "week %d" % week)

    def test_no_step_asks_the_same_thing_twice(self):
        """The body-paragraph warm-up prints six rules under three labels —
        "1a. FACTUAL (TELL): / 1b. SENSORY (SHOW): / 2a. …". With the book's
        numbering dropped, three lessons showed her "FACTUAL (TELL):" twice and
        "SENSORY (SHOW):" three times, with no way to tell the pairs apart."""
        from tutor.essay_lessons import LESSONS

        for lesson in LESSONS:
            for step in lesson["steps"]:
                texts = [p["text"] for p in step["prompts"]]
                self.assertEqual(len(set(texts)), len(texts),
                                 "L%d %s" % (lesson["number"], step["heading"]))
        self._seed()
        for week in (1, 3, 5, 7, 9):
            prompts = [q.prompt for q in self._set(week).questions.all()]
            self.assertEqual(len(set(prompts)), len(prompts), "week %d" % week)

    def test_no_transcription_scaffolding_reaches_her(self):
        """"[arrow callout]" is a reader describing the paper, not the guide
        speaking. It was landing in the hint she opens when she is stuck."""
        from tutor.essay_lessons import LESSONS

        for lesson in LESSONS:
            blob = json.dumps(lesson)
            for marker in ("[arrow callout]", "LINE CUT OFF", "[PAGE TRUNCATED",
                           "cannot be read reliably", "pdf_page"):
                self.assertNotIn(marker, blob,
                                 "L%d leaks %r" % (lesson["number"], marker))
        self._seed()
        for week in range(1, 11):
            for q in self._set(week).questions.all():
                self.assertNotIn("[arrow", q.prompt + q.hint)

    def test_every_lesson_that_sends_her_to_the_missing_section_says_so(self):
        """"Thinking In Threes" is referred to in all five lessons and exists
        in none of them. The warning was written for two."""
        from tutor.essay_lessons import LESSONS

        for lesson in LESSONS:
            mentions = any(
                "Thinking In Threes" in p["text"]
                for step in lesson["steps"] for p in step["prompts"])
            mentions = mentions or any(
                "thought in threes" in c.lower()
                for step in lesson["steps"] for c in step.get("checks", []))
            noted = any("Thinking In Threes" in n["text"]
                        for n in lesson.get("notes", []))
            self.assertEqual(noted, mentions, "L%d" % lesson["number"])
            self.assertTrue(mentions, "L%d should mention it" % lesson["number"])

    def test_the_lesson_module_is_what_the_generator_makes_of_the_pages(self):
        """The committed module must be exactly what the generator emits.

        `tutor/essay_lessons.py` is generated, and every rule about the guide's
        content — the numbering folded into the prompts, the transcription
        scaffolding stripped, which lessons get which warning — lives in
        `scripts/gen_essay_lessons.py`. Nothing else can see a change there:
        edit the generator, forget to regenerate, and the module keeps whatever
        it had while the rules say otherwise. Mutating the generator survived
        every other test in this class until this one existed.

        It also pins the provenance. The page transcriptions are the source of
        this curriculum; kept only in a scratch directory they would be swept
        up, and the generator would be unrunnable.
        """
        import subprocess
        import sys
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        gen = root / "scripts" / "gen_essay_lessons.py"
        pages = root / "tutor" / "data" / "essay_vol2_pages.json"
        committed = root / "tutor" / "essay_lessons.py"
        self.assertTrue(gen.exists(), gen)
        self.assertTrue(pages.exists(), pages)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "regenerated.py"
            proc = subprocess.run(
                [sys.executable, str(gen), str(pages), str(out)],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(
                out.read_text(encoding="utf-8"),
                committed.read_text(encoding="utf-8"),
                "tutor/essay_lessons.py is stale — re-run "
                "scripts/gen_essay_lessons.py tutor/data/essay_vol2_pages.json "
                "tutor/essay_lessons.py")

    def test_the_page_transcriptions_still_describe_this_guide(self):
        """A cheap sanity pin on the source data, so a truncated or swapped
        file is caught here rather than as a mystifying diff in the module."""
        import json as _json
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        pages = _json.loads(
            (root / "tutor" / "data" / "essay_vol2_pages.json").read_text(
                encoding="utf-8"))
        self.assertEqual([p["lesson_number"] for p in pages], [1, 2, 3, 4, 5])
        # Pages 18-72 of the scan, which is where the five lessons live.
        seen = sorted(pg["pdf_page"] for p in pages for pg in p["pages"])
        self.assertEqual(seen, list(range(18, 73)))

    # -- guards for what a second review found unpinned --------------------

    def test_the_dictionary_words_are_asked(self):
        """Four lessons open with "Use a dictionary to define:".

        Deleting that loop from the seed dropped twelve questions and every
        test still passed — the shape test only asserted "more than fifteen
        questions", and the weeks stay above fifteen without them.
        """
        from tutor.essay_lessons import LESSONS

        self._seed()
        expected = {L["weeks"][0]: L["vocabulary"] for L in LESSONS}
        self.assertEqual([len(v) for _w, v in sorted(expected.items())],
                         [0, 2, 3, 3, 4], "lesson 1 has no word list; the rest do")
        for week, words in expected.items():
            prompts = [q.prompt for q in self._set(week).questions.all()]
            for word in words:
                self.assertTrue(
                    any(word in p and "dictionary" in p for p in prompts),
                    "week %d never asks for %r" % (week, word))
            self.assertEqual(
                sum(1 for p in prompts if "Use a dictionary" in p), len(words),
                "week %d" % week)

    def test_every_week_asks_exactly_what_the_guide_prints(self):
        """A per-week count, so questions cannot quietly go missing.

        Derived from the lesson data rather than hardcoded, so it tracks a
        re-transcription — but it still fails the moment the seed stops
        emitting something the pages contain.
        """
        from tutor.essay_lessons import LESSONS

        self._seed()
        for lesson in LESSONS:
            odd, even = lesson["weeks"]
            expected = len(lesson["vocabulary"])
            for step in lesson["steps"]:
                expected += len(step["prompts"])
                if step.get("checks"):
                    expected += 1
            self.assertEqual(self._set(odd).questions.count(), expected,
                             "week %d" % odd)
            self.assertEqual(self._set(even).questions.count(), 3,
                             "week %d: draft + checklist + self-evaluation" % even)

    def test_the_drafting_prompt_names_the_essay_without_stuttering(self):
        """The titles are already imperative, so prefixing "Write" gave
        "Write write an orange" — on the one question of every drafting week,
        and in the text handed to the grader."""
        self._seed()
        for week in (2, 4, 6, 8, 10):
            prompt = self._set(week).questions.order_by("order").first().prompt
            self.assertNotIn("write write", prompt.lower())
            self.assertNotIn("Write **write", prompt)
        self.assertIn("Write an Orange",
                      self._set(2).questions.order_by("order").first().prompt)

    def test_the_guides_closing_direction_comes_after_the_week_s_work(self):
        """It tells her to begin crafting the essay from a hook and three
        sub-topics — which she writes ON that page. Printed above the
        questions it read as an instruction to start with none of them, and to
        hand-write on pages that do not exist in the app."""
        self._seed()
        html = self._page(1)
        self.assertIn("es-handover", html)
        # After the last question, not before the first.
        self.assertGreater(html.index("es-handover"), html.rindex("portal-answer"))
        # And it is honest about the app being typed.
        self.assertIn("you will type", html)
        # Not on the drafting week — that week's intro carries the order.
        self.assertNotIn("es-handover", self._page(2))

    def test_the_grader_is_told_not_to_punish_an_honest_self_evaluation(self):
        """This lives in the seeded rubric, a different file and a different
        sentence from the formatter's label — deleting it left every test
        green while the grader lost the only thing stopping it from marking
        her down for saying "Needs to Improve"."""
        self._seed()
        rubric = self._set(2).rubric
        self.assertIn("her own judgement of her own work", rubric)
        self.assertIn("never mark her down", rubric)
        self.assertIn("rough-draft sections are planning and are not marked",
                      rubric)

    def test_the_rubric_criteria_are_the_printed_words(self):
        """Counting six bullets per band catches a DROPPED one and nothing
        else — a corrupted or duplicated bullet passed. The grader is handed
        these verbatim."""
        from tutor import essay

        for name, criteria in essay.EVALUATION_RUBRIC:
            self.assertEqual(len(set(criteria)), len(criteria),
                             "%s repeats a criterion" % name)
        bands = dict(essay.EVALUATION_RUBRIC)
        self.assertEqual(bands["ACCOMPLISHED"][0], "Creatively focuses on the topic")
        self.assertEqual(bands["ACCOMPLISHED"][2], "Varies sentence structure")
        self.assertEqual(bands["POOR"][-1],
                         "Frequent errors in basic writing conventions")
        # The band-to-band wording the second reader flagged as the book's own
        # inconsistency: LIMITED says "Organization pattern", POOR says
        # "Organizational pattern". Both are printed; keep both.
        self.assertIn("Organization pattern is weak", bands["LIMITED"])
        self.assertIn("Organizational pattern is lacking", bands["POOR"])

    def test_the_teacher_form_line_items_are_the_printed_weights(self):
        """Section totals alone survive a compensating swap inside a section
        (Hook 1 → 2, Context 1 → 0)."""
        from tutor import essay

        items = {label: pts for _n, _t, rows in essay.TEACHER_FORM
                 for label, pts in rows}
        self.assertEqual(items["Hook"], 1)
        self.assertEqual(items["Context"], 1)
        self.assertEqual(items["Thesis Statement"], 1)
        self.assertEqual(items["Body Paragraphs on Topic"], 6)
        self.assertEqual(items["Supporting Facts & Details"], 6)
        self.assertEqual(items["Clear Sequence of Ideas"], 6)
        self.assertEqual(items["Weave"], 1)
        self.assertEqual(items["Echo"], 1)
        self.assertEqual(items["Twist"], 1)
        self.assertEqual(len(items), 22)

    def test_no_bracketed_reader_annotation_survives_anywhere(self):
        """Stronger than listing the markers we happened to see: a NEW reader
        annotation in a re-transcription would have shipped."""
        from tutor.essay_lessons import LESSONS

        for lesson in LESSONS:
            for step in lesson["steps"]:
                blob = " ".join(
                    [step["heading"], step.get("instruction", "")]
                    + [p["text"] for p in step["prompts"]]
                    + list(step.get("checks", [])))
                self.assertNotIn("[", blob, "L%d %s" % (lesson["number"],
                                                        step["heading"]))

    def test_she_is_told_the_page_numbers_are_the_paper_book_s(self):
        """"Choose one of your three sub-topics from page 32" — she typed those
        into this app a few questions earlier, and that printed page is blank."""
        from tutor.essay_lessons import LESSONS
        import re

        for lesson in LESSONS:
            refs = [m for step in lesson["steps"]
                    for m in re.findall(r"from page (\d+)",
                                        step.get("instruction", ""))]
            noted = any("page" in n["text"] and "paper book" in n["text"]
                        for n in lesson.get("notes", []))
            self.assertEqual(bool(refs), noted,
                             "L%d refs=%s noted=%s" % (lesson["number"], refs, noted))

    def test_the_sub_topic_lead_keeps_its_line_break(self):
        """textwrap turns a newline into a space unless told not to, which
        silently rewrote this prompt in the generated file."""
        from tutor.essay_lessons import LESSONS

        for lesson in LESSONS:
            leads = [p["text"] for step in lesson["steps"] for p in step["prompts"]
                     if "Choose three sub-topics" in p["text"]]
            self.assertEqual(len(leads), 1, "L%d" % lesson["number"])
            self.assertIn("\n\nSub-topic 1 of 3", leads[0],
                          "L%d lost the break" % lesson["number"])

    def test_every_reference_page_we_ship_is_actually_offered(self):
        """A page committed under static/essay/reference/ and left out of the
        list is invisible to her.

        That is exactly what happened twice: folio 15 (the LABELLED model essay,
        the page the template promises) and folio 17 (the course map) were both
        rendered, committed and never listed. Checking that the listed pages
        resolve cannot catch it — the list is the thing that was wrong.
        """
        from pathlib import Path

        from tutor import essay

        root = Path(__file__).resolve().parent.parent / "static" / "essay" / "reference"
        on_disk = {p.name for p in root.glob("*.jpg")}
        offered = {"p%02d.jpg" % p["pdf_page"] for p in essay.REFERENCE_PAGES}
        self.assertEqual(on_disk - offered, set(),
                         "committed but never shown to her")
        self.assertEqual(offered - on_disk, set(), "listed but not on disk")

    def test_the_rubric_bands_are_pinned_word_for_word(self):
        """All thirty bullets, not three.

        The grader is handed these verbatim, and a corrupted bullet reads as
        plausible guidance — "Transitions are creative and adequate" under
        PROFICIENT would quietly invert what the band means.
        """
        from tutor import essay

        expected = {
            "ACCOMPLISHED": [
                "Creatively focuses on the topic",
                "Uses logical progression of ideas to develop and supports topic with details",
                "Varies sentence structure",
                "Uses interesting transitions",
                "Makes strong word choice",
                "Mature understanding of writing conventions",
            ],
            "PROFICIENT": [
                "Focuses on topic and includes adequate support",
                "Uses logical progression of ideas to develop and loosely supports topic",
                "Some varied sentence structure",
                "Transitions are adequate but not creative",
                "Word choice is adequate but not creative",
                "General understanding of writing conventions",
            ],
            "BASIC": [
                "Topic is addressed, but unclear",
                "Lacks logical progression of ideas and support is weak",
                "Sentences are stagnant and uninteresting",
                "Lack of transitions",
                "Average word choice",
                "Partial understanding of writing conventions",
            ],
            "LIMITED": [
                "Topic may be mentioned, but not clearly addressed and loosely supported",
                "Organization pattern is weak",
                "Writing contains sentence fragments and run-ons",
                "Poor transitions",
                "Poor word choice",
                "Definite misunderstanding of writing conventions",
            ],
            "POOR": [
                "Topic is not addressed or clearly supported",
                "Organizational pattern is lacking",
                "Sentence structure is insufficient",
                "Non-existent transitions",
                "Weak word choice",
                "Frequent errors in basic writing conventions",
            ],
        }
        self.assertEqual(dict(essay.EVALUATION_RUBRIC), expected)

    def test_no_bracketed_annotation_anywhere_in_the_lesson_data(self):
        """Wider than the per-step blob: banners, word lists and checklist
        lead-ins are child-facing too.

        Walks the string VALUES — serialising the whole lesson and searching
        the JSON would flag its own array brackets and pass for the wrong
        reason forever after.
        """
        from tutor.essay_lessons import LESSONS

        def strings(value, path="L"):
            if isinstance(value, str):
                yield path, value
            elif isinstance(value, dict):
                for k, v in value.items():
                    yield from strings(v, "%s.%s" % (path, k))
            elif isinstance(value, (list, tuple)):
                for i, v in enumerate(value):
                    yield from strings(v, "%s[%d]" % (path, i))

        for lesson in LESSONS:
            for path, text in strings(lesson, "L%d" % lesson["number"]):
                self.assertNotIn("[", text, path)


class StudiesWeeklyTests(TestCase):
    """California Studies Weekly — one issue a week, per grade, for years.

    The point of the framework is that week 2 is a content file, not a build.
    These pin the parts that would silently rot: the answer key matching the
    teacher edition, the figures existing, and the level/grade pairing.
    """

    @classmethod
    def setUpTestData(cls):
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(
            username="sw", email="sw@e.com", password="pw")
        cls.fam = Family.objects.create(name="SW Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam, role="parent")
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.fam)
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.fam)
        cls.token = make_portal_token(cls.kaylin)

    def _seed(self, level=7, week=1):
        call_command("seed_weekly", "--level", str(level), "--week", str(week),
                     "--for-user", "sw", stdout=StringIO())

    def _set(self, week=1, level=7):
        return QuestionSet.objects.get(
            lesson__number=week,
            lesson__chapter__curriculum__parent=self.parent,
            lesson__chapter__curriculum__name__startswith=
                "Studies Weekly %d" % level)

    def _page(self, week=1, level=7, child=None):
        from portal.tokens import make_portal_token

        token = make_portal_token(child) if child is not None else self.token
        return self.client.get(reverse(
            "portal:portal_questions",
            args=[token, self._set(week, level).pk])).content.decode()

    # -- the issue's own answers -------------------------------------------

    def test_the_answer_key_is_the_teacher_editions(self):
        """Marked answers from pp. 1.13-1.14 of the issue. If a re-transcription
        ever drifts, a child gets told her right answer is wrong."""
        from tutor import weekly_l7w1 as w

        correct = [q.get("correct") for q in w.QUESTIONS if q["kind"] == "choice"]
        self.assertEqual(correct, [["c"], ["a", "b", "e"], ["d"], ["c"], ["b"],
                                   ["c"], ["a"]])
        pairs = [q for q in w.QUESTIONS if q["kind"] == "fill_two"]
        self.assertEqual(
            [(p["correct_a"], p["correct_b"]) for p in pairs],
            [("Physical geography", "human geography"), ("north", "west")])

    def test_only_one_question_takes_several_answers(self):
        """"Which ARE examples" is multi; every "which IS" is single. A child
        who can tick three boxes on a one-answer question has been told
        something untrue about the question."""
        from tutor import weekly_l7w1 as w

        multi = [q["prompt"] for q in w.QUESTIONS
                 if q["kind"] == "choice" and q["multi"]]
        self.assertEqual(len(multi), 1)
        self.assertIn("Which are examples", multi[0])

    def test_every_correct_answer_is_actually_on_offer(self):
        """An answer key naming an option that does not exist is a question she
        cannot get right — the same class of defect as an unwinnable blank."""
        from tutor import weekly_l7w1 as w

        for q in w.QUESTIONS:
            if q["kind"] == "choice":
                keys = {o["key"] for o in q["options"]}
                self.assertTrue(set(q["correct"]) <= keys, q["prompt"][:40])
            elif q["kind"] == "fill_two":
                self.assertIn(q["correct_a"], q["bank_a"])
                self.assertIn(q["correct_b"], q["bank_b"])

    def test_every_figure_and_page_exists_on_disk(self):
        """"Study the map" is unanswerable without the map, and under
        ManifestStaticFilesStorage a missing file raises rather than degrades."""
        from django.contrib.staticfiles import finders

        from tutor import weekly_l7w1 as w

        for q in w.QUESTIONS:
            for path in ([q.get("figure")] if q.get("figure") else []) + \
                        [o["image"] for o in q.get("options", []) if o.get("image")]:
                self.assertIsNotNone(finders.find(path), path)
        for path in w.PAGES:
            self.assertIsNotNone(finders.find(path), path)

    # -- what gets built ---------------------------------------------------

    def test_a_two_blank_sentence_becomes_two_questions(self):
        """The printed page gives each blank its own bank, so half-right is a
        real outcome — one combined answer could not record it."""
        self._seed()
        prompts = [q.prompt for q in self._set().questions.order_by("order")]
        self.assertIn("two branches of geography", prompts[0])
        self.assertIn("Blank A", prompts[0])
        self.assertEqual(prompts[1], "**Blank B**")

    def test_the_figure_rides_with_the_first_blank_only(self):
        """Printing the same map twice pushes the second blank off the screen."""
        self._seed()
        qs = list(self._set().questions.order_by("order"))
        pair = [q for q in qs if "Physical Map" in q.figure_caption]
        self.assertEqual(len(pair), 1)
        self.assertIn("Blank A", pair[0].prompt)

    def test_the_written_question_offers_the_answer_mode_picker(self):
        self._seed()
        written = [q for q in self._set().questions.all()
                   if q.response_type == Question.TYPE_TEXT]
        self.assertEqual(len(written), 1)
        self.assertTrue(written[0].offers_answer_mode)
        html = self._page()
        self.assertIn('data-mode="write"', html)
        self.assertIn('data-mode-pane="write"', html)
        self.assertIn("handwriting-canvas", html)

    def test_the_page_renders_every_question(self):
        self._seed()
        html = self._page()
        self.assertIn("choice-widget", html)
        self.assertIn("choice-options--pictures", html)   # the five photographs
        self.assertIn("q-figure", html)                    # the maps
        self.assertIn("Biomes of North America", html)

    # -- self-marking ------------------------------------------------------

    def test_a_choice_answer_is_marked_without_the_ai(self):
        """Ten recall questions should not cost a model call."""
        self._seed()
        q = [x for x in self._set().questions.all()
             if x.response_type == Question.TYPE_CHOICE and not x.choice_is_multi][0]
        right = sorted(q.choice_correct)[0]
        wrong = next(o["key"] for o in q.choice_options if o["key"] != right)
        sheet = ResponseSheet(question_set=self._set())

        sheet.answers = {str(q.pk): json.dumps({"picked": [right]})}
        self.assertIn("correct", sheet.answer_display(q))
        sheet.answers = {str(q.pk): json.dumps({"picked": [wrong]})}
        self.assertIn("not correct", sheet.answer_display(q))

    def test_a_multi_answer_needs_every_one_of_them(self):
        self._seed()
        q = [x for x in self._set().questions.all()
             if x.response_type == Question.TYPE_CHOICE and x.choice_is_multi][0]
        sheet = ResponseSheet(question_set=self._set())
        sheet.answers = {str(q.pk): json.dumps({"picked": ["a", "b"]})}
        self.assertIn("not correct", sheet.answer_display(q),
                      "two of the three is not the answer")
        sheet.answers = {str(q.pk): json.dumps({"picked": ["a", "b", "e"]})}
        self.assertIn("correct", sheet.answer_display(q))

    def test_the_grader_is_shown_the_words_not_the_letters(self):
        """"a, c" makes the grader go and look them up."""
        self._seed()
        q = [x for x in self._set().questions.all()
             if x.response_type == Question.TYPE_CHOICE
             and "human-environment" in x.prompt][0]
        sheet = ResponseSheet(question_set=self._set())
        sheet.answers = {str(q.pk): json.dumps({"picked": ["c"]})}
        self.assertIn("Hoover Dam", sheet.answer_display(q))

    def test_writing_by_hand_on_a_typed_question_still_reads_as_handwriting(self):
        """The answer-mode picker lets her write on a question authored for
        typing. The stored shape is the only thing that can tell us, and the
        reports must show the marks rather than the JSON."""
        self._seed()
        q = [x for x in self._set().questions.all()
             if x.response_type == Question.TYPE_TEXT][0]
        sheet = ResponseSheet(question_set=self._set())
        sheet.answers = {str(q.pk): json.dumps({
            "strokes": [{"c": "#1d3557", "w": 3, "p": [[0.1, 0.5], [0.6, 0.5]]}],
            "surface": {"w": 662, "h": 192}})}
        shown = sheet.answer_display(q)
        self.assertIn("handwritten", shown)
        self.assertNotIn("strokes", shown)
        self.assertIsNotNone(sheet.answer_replay(q))

        sheet.answers = {str(q.pk): "Maps show where things are."}
        self.assertEqual(sheet.answer_display(q), "Maps show where things are.")
        self.assertIsNone(sheet.answer_replay(q))

    # -- the framework -----------------------------------------------------

    def test_a_level_is_a_grade_and_the_seed_refuses_a_mismatch(self):
        """Level 7 is Grades 6-8 material. Seeding it for a third-grader is a
        typo worth stopping, not a curriculum decision."""
        with self.assertRaises(CommandError) as caught:
            call_command("seed_weekly", "--level", "7", "--week", "1",
                         "--for-user", "sw", "--child-name", "Violet",
                         stdout=StringIO())
        self.assertIn("G03", str(caught.exception))

    def test_a_missing_week_says_what_to_write(self):
        with self.assertRaises(ModuleNotFoundError) as caught:
            call_command("seed_weekly", "--level", "7", "--week", "99",
                         "--for-user", "sw", stdout=StringIO())
        self.assertIn("weekly_l7w99", str(caught.exception))

    def test_a_dry_run_writes_nothing(self):
        out = StringIO()
        call_command("seed_weekly", "--level", "7", "--week", "1",
                     "--for-user", "sw", "--dry-run", stdout=out)
        self.assertIn("nothing written", out.getvalue())
        self.assertEqual(Curriculum.objects.count(), 0)

    def test_reseeding_changes_nothing(self):
        self._seed()
        before = (QuestionSet.objects.count(), Question.objects.count())
        self._seed()
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)

    def test_the_issue_is_attached_as_the_week_s_reading(self):
        """She reads the real newspaper page — the layout IS the lesson."""
        from tutor.models import Material

        self._seed()
        m = Material.objects.get(lesson__number=1)
        self.assertEqual(m.status, Material.DRAFT)      # a parent approves it
        self.assertIn("Geography and Map Skills", m.title)
        self.assertIn("Framework", m.parent_content)    # the standards table


class StudiesWeeklyLevel3Tests(TestCase):
    """Violet's Level 3 — a different shape on the same framework.

    Kaylin's week is one article and a map-heavy check. Violet's is five short
    articles and a check about the method itself, and it brought two things the
    framework did not have: a sorting question, and a matching column that has
    to be shuffled. These pin both, and pin that one child's week cannot put
    words in the other's mouth.
    """

    @classmethod
    def setUpTestData(cls):
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(
            username="sw3", email="sw3@e.com", password="pw")
        cls.fam = Family.objects.create(name="SW3 Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam,
                                        role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.fam)
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07",
            family=cls.fam)
        cls.token = make_portal_token(cls.violet)

    def _seed(self, week=1):
        call_command("seed_weekly", "--level", "3", "--week", str(week),
                     "--for-user", "sw3", stdout=StringIO())

    def _set(self, week=1):
        return QuestionSet.objects.get(
            lesson__number=week,
            lesson__chapter__curriculum__parent=self.parent)

    def _page(self, week=1):
        return self.client.get(reverse(
            "portal:portal_questions",
            args=[self.token, self._set(week).pk])).content.decode()

    # -- the issue's own answers -------------------------------------------

    def test_the_answer_key_is_the_teacher_editions(self):
        """Marked answers from 1.8-1.9. A drifted key tells a nine-year-old her
        right answer is wrong, which is the worst thing this file can do."""
        from tutor import weekly_l3w1 as w

        self.assertEqual([q["correct"] for q in w.QUESTIONS if q["kind"] == "choice"],
                         [["b"], ["c"], ["a"], ["b"], ["a"]])
        blanks = [q for q in w.QUESTIONS if q["kind"] == "fill_two"]
        self.assertEqual([(q["correct_a"], q["correct_b"]) for q in blanks],
                         [("compelling", "supporting")])
        pairs = dict(next(q for q in w.QUESTIONS if q["kind"] == "matching")["pairs"])
        self.assertEqual(pairs["economist"], "How do people make money?")
        self.assertEqual(pairs["geographer"], "Where is it?")
        self.assertEqual(pairs["political scientist"], "How are laws created?")

    def test_the_claim_stays_at_step_two(self):
        """The article numbers "make a claim" SECOND, before the research, and
        the key agrees. It reads like a mistake and is not one — question 8 is
        built on it. Anyone "fixing" this marks her right answer wrong."""
        from tutor import weekly_l3w1 as w

        sort = next(q for q in w.QUESTIONS if q["kind"] == "order")
        self.assertEqual(sort["correct"][0], "Ask a compelling question")
        self.assertEqual(sort["correct"][1], "Make a claim")
        self.assertEqual(sort["correct"][-1], "Present your conclusions")

    def test_nothing_is_in_its_answer_position_before_she_starts(self):
        """A scrambled question printed unscrambled is free marks. Both the
        sorting steps and the matching column must actually move."""
        from tutor import weekly_l3w1 as w

        sort = next(q for q in w.QUESTIONS if q["kind"] == "order")
        self.assertNotEqual(sort["steps"], sort["correct"])
        for i, (printed, right) in enumerate(zip(sort["steps"], sort["correct"])):
            self.assertNotEqual(printed, right, "step %d is already placed" % (i + 1))

        self._seed()
        q = [x for x in self._set().questions.all() if x.is_matching][0]
        words = q.vocab_data["words"]
        for i, d in enumerate(q.vocab_data["definitions"]):
            self.assertNotEqual(
                d["word"], words[i],
                "row %d matches itself — she can draw straight lines" % (i + 1))

    def test_the_shared_word_bank_serves_both_blanks(self):
        """The page prints ONE bank of four for question 3 and uses it twice, so
        both blanks must offer all four words — and land on different ones."""
        self._seed()
        blanks = [q for q in self._set().questions.order_by("order")
                  if "guides inquiry" in q.prompt or q.prompt == "**Blank B**"]
        self.assertEqual(len(blanks), 2)
        texts = [sorted(o["text"] for o in q.choice_options) for q in blanks]
        self.assertEqual(texts[0], texts[1])
        self.assertEqual(texts[0], ["compelling", "mystery", "research", "supporting"])
        self.assertNotEqual(blanks[0].choice_correct, blanks[1].choice_correct)
        self.assertEqual(
            [next(o["text"] for o in q.choice_options
                  if o["key"] in q.choice_correct) for q in blanks],
            ["compelling", "supporting"])

    def test_every_correct_answer_is_actually_on_offer(self):
        from tutor import weekly_l3w1 as w

        for q in w.QUESTIONS:
            if q["kind"] == "choice":
                self.assertTrue(set(q["correct"]) <= {o["key"] for o in q["options"]},
                                q["prompt"][:40])
            elif q["kind"] == "fill_two":
                self.assertIn(q["correct_a"], q["bank_a"])
                self.assertIn(q["correct_b"], q["bank_b"])

    def test_every_figure_and_page_exists_on_disk(self):
        """A question about "this image" is unanswerable without the image, and
        under ManifestStaticFilesStorage a missing file raises in production
        rather than degrading to a broken picture."""
        from django.contrib.staticfiles import finders

        from tutor import weekly_l3w1 as w

        for q in w.QUESTIONS:
            if q.get("figure"):
                self.assertIsNotNone(finders.find(q["figure"]), q["figure"])
        self.assertEqual(len(w.PAGES), 4)
        for path in w.PAGES:
            self.assertIsNotNone(finders.find(path), path)

    def test_she_can_actually_reach_the_pages_she_is_told_to_read(self):
        """The intro says "read all 4 pages below". For a while nothing rendered
        them: PAGES fed the sentence and the dry-run and nothing else, so every
        question was a reading question about text that was never on screen.

        Checking the files exist could not catch that — nothing passed them to
        {% static %}, so a missing one could not have raised either. This
        fetches the page a child actually opens.
        """
        from tutor import weekly_l3w1 as w
        from tutor.models import Material

        self._seed()
        material = Material.objects.get(lesson__number=1)
        material.status = Material.APPROVED       # a parent approves it first
        material.save(update_fields=["status"])

        from django.templatetags.static import static

        html = self.client.get(reverse(
            "portal:portal_material",
            args=[self.token, material.pk])).content.decode()
        self.assertIn("read all 4 pages below", html.lower())
        for path in w.PAGES:
            self.assertIn(static(path), html, path)
        # Each one links out full size — a newspaper page is unreadable inline.
        self.assertEqual(html.count('class="lesson-page"'), 4)
        # {# #} is SINGLE-LINE ONLY. A multi-line one renders its own text onto
        # her screen, and it has shipped that way four times — including once
        # into this very block. Rendering the real page is the only way to see
        # it, because the template compiles either way.
        body = html.split("<body")[1]
        for marker in ("{#", "#}", "{% comment %}", "{% endcomment %}"):
            self.assertNotIn(marker, body, "a template comment leaked onto the page")

    def test_a_reseed_does_not_un_approve_a_week_already_approved(self):
        """The portal only shows APPROVED materials. Reseeding to fix a question
        used to force the Material back to DRAFT, which would take the reading
        off the child's page mid-week without anyone touching it."""
        from tutor.models import Material

        self._seed()
        material = Material.objects.get(lesson__number=1)
        self.assertEqual(material.status, Material.DRAFT)   # new ones are drafts
        material.status = Material.APPROVED
        material.save(update_fields=["status"])

        self._seed()
        material.refresh_from_db()
        self.assertEqual(material.status, Material.APPROVED)

    # -- what gets built ---------------------------------------------------

    def test_the_page_renders_the_sorting_widget(self):
        self._seed()
        html = self._page()
        self.assertIn("order-widget", html)
        self.assertIn("order-pick", html)
        self.assertIn("Search for answers / Experiment", html)

    def test_a_sorted_answer_is_marked_without_the_ai(self):
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_order][0]
        sheet = ResponseSheet(question_set=self._set())

        sheet.answers = {str(q.pk): json.dumps({"order": q.order_correct})}
        shown = sheet.answer_display(q)
        self.assertIn("[correct]", shown)
        self.assertIn("1. Ask a compelling question", shown)

        swapped = list(q.order_correct)
        swapped[1], swapped[2] = swapped[2], swapped[1]
        sheet.answers = {str(q.pk): json.dumps({"order": swapped})}
        shown = sheet.answer_display(q)
        self.assertIn("not correct", shown)
        self.assertIn("Ask a compelling question → Make a claim", shown,
                      "a wrong order should show her the right one")

    def test_a_half_filled_order_is_not_called_correct(self):
        """She numbers one of five and walks away. Whatever the record says,
        it must not say she got it right — in either shape a partial can take.

        The nulls are the shape the widget used to save when its array was left
        sparse: JSON.stringify turns a hole into null, and str(None) is the
        truthy string "None", so the parent's report printed "1. None". The
        widget no longer writes it, but answers already stored do.
        """
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_order][0]
        sheet = ResponseSheet(question_set=self._set())
        for partial in (["Ask a compelling question", "", "", "", ""],
                        [None, None, None, None, "Present your conclusions"]):
            sheet.answers = {str(q.pk): json.dumps({"order": partial})}
            shown = sheet.answer_display(q)
            self.assertNotIn("[correct]", shown)
            self.assertNotIn("None", shown,
                             "a blank slot must not print as the word None")

    def test_a_part_numbered_sort_is_not_counted_as_answered(self):
        """The count renders as "N of M answered" on the line directly above a
        "Turn it in" button she cannot undo, so it must not call a sort with one
        number in it finished. An ordering answer says so itself: one slot per
        step, "" where she has not placed one.

        Everything else keeps the plain not-empty rule — changing that would
        move the number under children who are part-way through a page.
        """
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_order][0]
        sheet = ResponseSheet(question_set=self._set())

        sheet.answers = {str(q.pk): json.dumps(
            {"order": ["", "", "", "", "Present your conclusions"]})}
        self.assertEqual(sheet.answered_count, 0, "one number is not an answer")

        sheet.answers = {str(q.pk): json.dumps({"order": q.order_correct})}
        self.assertEqual(sheet.answered_count, 1)

        # A wrong-but-complete order is still an answer she gave.
        backwards = list(reversed(q.order_correct))
        sheet.answers = {str(q.pk): json.dumps({"order": backwards})}
        self.assertEqual(sheet.answered_count, 1)

        # And nothing else changed: a typed answer counts by being non-empty.
        written = [x for x in self._set().questions.all()
                   if x.response_type == Question.TYPE_TEXT][0]
        sheet.answers = {str(written.pk): "I wonder how rivers start."}
        self.assertEqual(sheet.answered_count, 1)
        sheet.answers = {str(written.pk): "   "}
        self.assertEqual(sheet.answered_count, 0)

    def test_the_written_task_offers_the_answer_mode_picker(self):
        """It is the only thing she writes this week, and she may want to write
        it with the stylus."""
        self._seed()
        written = [q for q in self._set().questions.all()
                   if q.response_type == Question.TYPE_TEXT]
        self.assertEqual(len(written), 1)
        self.assertTrue(written[0].offers_answer_mode)
        html = self._page()
        self.assertIn('data-mode="write"', html)
        self.assertIn("handwriting-canvas", html)

    # -- one week cannot speak for another ---------------------------------

    def test_her_week_says_nothing_about_kaylins_maps(self):
        """The seeder used to hard-code Level 7's prose — "read the maps",
        "questions 6, 8 and 9" — into every week it built. Violet's issue has no
        maps and eight questions, so that guidance was simply untrue for her."""
        self._seed()
        qset = self._set()
        guide = Material.objects.get(lesson__number=1).parent_content
        for text in (qset.rubric, guide, qset.intro):
            self.assertNotIn("6, 8 and 9", text)
            self.assertNotIn("read the maps", text.lower())
            self.assertNotIn("sit with her and the map", text.lower())
        for text in (qset.rubric, qset.intro):
            self.assertNotIn("map", text.lower())
        self.assertIn("make a claim", guide.lower())
        self.assertIn("compelling question", qset.rubric.lower())

    def test_the_standards_are_the_teacher_editions_own(self):
        """"Meets California standards" has to mean the codes the publisher
        prints, not a framework name I picked."""
        from tutor import weekly_l3w1 as w

        self._seed()
        guide = Material.objects.get(lesson__number=1).parent_content
        self.assertIn("RI.3.1", guide)
        self.assertIn("W.3.2", guide)
        self.assertTrue(w.REFLECTION["standard"].startswith("W.3.2"),
                        "the writing task is the W standard, not the reading one")
        self.assertTrue(all(q["standard"].startswith("RI.3.1")
                            for q in w.QUESTIONS))

    def test_a_level_is_a_grade_and_the_seed_refuses_a_mismatch(self):
        with self.assertRaises(CommandError) as caught:
            call_command("seed_weekly", "--level", "3", "--week", "1",
                         "--for-user", "sw3", "--child-name", "Kaylin",
                         stdout=StringIO())
        self.assertIn("G07", str(caught.exception))

    def test_a_missing_week_says_what_to_write(self):
        with self.assertRaises(ModuleNotFoundError) as caught:
            call_command("seed_weekly", "--level", "3", "--week", "99",
                         "--for-user", "sw3", stdout=StringIO())
        self.assertIn("weekly_l3w99", str(caught.exception))

    def test_the_issue_is_attached_as_the_week_s_reading(self):
        self._seed()
        m = Material.objects.get(lesson__number=1)
        self.assertEqual(m.status, Material.DRAFT)      # a parent approves it
        self.assertIn("Developing Inquiries", m.title)
        self.assertIn("all 4 pages", m.student_intro)


class StudiesWeeklyBuilderTests(SimpleTestCase):
    """The two builders that can quietly author an unanswerable question."""

    def test_a_step_that_cannot_be_placed_is_refused(self):
        from tutor.weekly import order

        with self.assertRaises(ValueError):
            order("Put these in order.",
                  steps=["one", "two", "three"],
                  correct=["one", "two", "THREE"])

    def test_a_matching_column_missing_an_answer_is_refused(self):
        """A word in the answer but not in the column is a pair she can never
        make; a word in the column but not in the answer never matches
        anything."""
        from tutor.weekly import matching

        pairs = [("a", "1"), ("b", "2")]
        with self.assertRaises(ValueError):
            matching("Match them.", pairs, word_order=["1", "3"])
        with self.assertRaises(ValueError):
            matching("Match them.", pairs, word_order=["1"])
        self.assertEqual(matching("Match them.", pairs,
                                  word_order=["2", "1"])["word_order"],
                         ["2", "1"])

    def test_a_page_that_does_not_scramble_is_still_allowed(self):
        """Some pages print the column straight. The builder should not force a
        shuffle it was not asked for — it should only refuse a wrong one."""
        from tutor.weekly import matching

        self.assertIsNone(matching("Match them.", [("a", "1")])["word_order"])

    def test_two_steps_that_read_the_same_are_refused(self):
        """The widget keys a step on its TEXT: two identical steps hydrate to
        the same number, so there is no ordering she could enter that would be
        marked correct. Set equality alone would let this through — both lists
        hold the same strings."""
        from tutor.weekly import order

        with self.assertRaises(ValueError) as caught:
            order("Put these in order.",
                  steps=["read it", "read it", "write it"],
                  correct=["write it", "read it", "read it"])
        self.assertIn("read the same", str(caught.exception))

    def test_two_questions_sharing_an_answer_are_refused(self):
        """Same reason on the other widget: one button cannot be matched to two
        questions, so the second is uncompletable."""
        from tutor.weekly import matching

        with self.assertRaises(ValueError) as caught:
            matching("Match them.",
                     [("Who?", "a person"), ("Whom?", "a person")])
        self.assertIn("share an answer", str(caught.exception))


class LessonBlockKindRegistryTests(SimpleTestCase):
    """Every block kind must render, and every kind must be checkable.

    A kind the template does not know renders as blank space on a child's page,
    and a kind missing from REQUIRED_KEYS is one `audit_content` waves through
    without looking — `REQUIRED_KEYS.get(kind, ())` checks nothing at all. Both
    failures are silent, which is why they are pinned rather than remembered.
    """

    def test_every_kind_has_a_branch_in_the_template(self):
        import os

        from django.conf import settings

        from tutor.models import LessonBlock

        path = os.path.join(settings.BASE_DIR, "templates", "portal",
                            "_lesson_blocks.html")
        with open(path, encoding="utf-8") as fh:
            markup = fh.read()
        for kind, _label in LessonBlock.KIND_CHOICES:
            self.assertIn('b.kind == "%s"' % kind, markup,
                          "%s would render as nothing at all" % kind)

    def test_every_kind_is_checked_by_the_auditor(self):
        from tutor.management.commands._saxon_seed import REQUIRED_KEYS
        from tutor.models import LessonBlock

        for kind, _label in LessonBlock.KIND_CHOICES:
            self.assertIn(kind, REQUIRED_KEYS,
                          "%s slips past audit_content unchecked" % kind)
            self.assertTrue(REQUIRED_KEYS[kind], kind)


class HandsOnGleanTests(TestCase):
    """Violet's sixth Glean option for "A Mouse Called Wolf".

    The guide's five final projects all end in "write a paragraph". She read the
    book, liked it, and wanted none of them — so this option covers the same
    ground with her hands. The thing these guard is the promise the page makes
    her on its first line: **there is nothing to write.**
    """

    @classmethod
    def setUpTestData(cls):
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(
            username="wolf", email="wolf@e.com", password="pw")
        cls.fam = Family.objects.create(name="Wolf Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam,
                                        role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.fam)
        cls.token = make_portal_token(cls.violet)

    def _seed(self):
        call_command("seed_a_mouse_called_wolf", "--for-user", "wolf",
                     stdout=StringIO())

    def _set(self):
        return QuestionSet.objects.get(title__contains="Wolf's Big Concert")

    # -- the promise on the first line --------------------------------------

    def test_not_one_question_asks_her_to_write(self):
        """The whole reason this option exists. A typed-answer question here
        would put back exactly the thing she said no to."""
        self._seed()
        types = {q.response_type for q in self._set().questions.all()}
        self.assertNotIn(Question.TYPE_TEXT, types)
        self.assertNotIn(Question.TYPE_PARAGRAPH, types)
        self.assertNotIn(Question.TYPE_HANDWRITING, types)
        self.assertNotIn(Question.TYPE_CLOZE, types)
        self.assertEqual(types, {Question.TYPE_DRAWING, Question.TYPE_CHOICE,
                                 Question.TYPE_MATCHING, Question.TYPE_SELF_EVAL})

    def test_the_self_check_does_not_ask_for_notes(self):
        """A self-evaluation normally offers a "how would you strengthen this?"
        line per item. Six of those is six paragraphs by another name."""
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_self_eval][0]
        self.assertFalse(q.self_eval_wants_notes)
        self.assertEqual(len(q.self_eval_items), 6)
        self.assertEqual(q.self_eval_scale, ["Not yet", "Nearly", "Yes!"])

    def test_most_of_it_is_drawing(self):
        """"More drawing" was the request, not "one drawing at the end"."""
        self._seed()
        drawings = [q for q in self._set().questions.all() if q.is_drawing]
        self.assertGreaterEqual(len(drawings), 6)
        # The poster and the piano need more paper than a listening doodle.
        heights = sorted(q.drawing_height for q in drawings)
        self.assertGreater(heights[-1], heights[0])

    # -- it covers the guide's ground ---------------------------------------

    def test_it_does_the_work_of_the_guide_s_written_options(self):
        """This is what makes it a legitimate alternative rather than a lighter
        one: between them the steps cover four of the printed five."""
        self._seed()
        questions = list(self._set().questions.all())
        prompts = " ".join(q.prompt for q in questions).lower()

        # Option 1, composer compare: one listening step EACH, or there is
        # nothing to compare.
        for composer in ("mozart", "beethoven", "schubert"):
            self.assertEqual(
                len([q for q in questions
                     if composer in q.prompt.lower() and q.is_drawing]), 1,
                "one listening drawing for %s" % composer)

        # Option 3, grand piano: the tapping game AND the drawing.
        self.assertTrue(any("grand piano" in q.prompt.lower() and q.is_drawing
                            for q in questions))
        self.assertTrue(any("piano" in q.prompt.lower() and q.is_matching
                            for q in questions))

        # Option 4, her name. Matching "name" anywhere in the prompts passed
        # even with this step deleted — the piano step says she may write the
        # parts' NAMES on her drawing. The step itself is what is being pinned.
        shield = [q for q in questions if "shield" in q.prompt.lower()]
        self.assertEqual(len(shield), 1)
        self.assertTrue(shield[0].is_drawing)
        self.assertIn("ask your mum and dad", shield[0].prompt.lower(),
                      "the interview is the point of this one, and it happens "
                      "out loud")

        terms = [w for q in self._set().questions.all() if q.is_matching
                 for w in q.vocab_data["words"]]
        for term in ("ballad", "bass", "carol", "composer", "discordant", "key",
                     "measure", "melody", "opus", "reprise", "rhythm", "scales",
                     "solo", "sonata"):                        # option 5, all 14
            self.assertIn(term, terms, "the guide lists %r" % term)

    def test_the_guide_s_own_five_options_are_still_there(self):
        """It is an extra option, not a substitution. The record has to show the
        purchased guide followed."""
        self._seed()
        printed = QuestionSet.objects.get(title__endswith="Glean: Final Project")
        self.assertIn("Composer compare", printed.intro)
        self.assertIn("Musical terms", printed.intro)
        self.assertEqual(printed.questions.count(), 3)

    def test_nothing_she_taps_can_be_marked_wrong_on_the_favourite(self):
        """"Which composer did you like best" has no right answer, and marking
        one would be telling a nine-year-old her taste is incorrect."""
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_choice][0]
        self.assertEqual(q.choice_correct, set())
        sheet = ResponseSheet(question_set=self._set())
        for key in ("a", "b", "c"):
            sheet.answers = {str(q.pk): json.dumps({"picked": [key]})}
            shown = sheet.answer_display(q)
            self.assertNotIn("not correct", shown)
            self.assertNotIn("[correct", shown)

    def test_the_word_games_still_mark_themselves(self):
        """They are the guide's option 5. If they did not mark, a parent would
        be checking fourteen definitions by hand."""
        self._seed()
        for q in [x for x in self._set().questions.all() if x.is_matching]:
            for d in q.vocab_data["definitions"]:
                self.assertIn(d["word"], q.vocab_data["words"])
            self.assertEqual(len(q.vocab_data["words"]),
                             len(q.vocab_data["definitions"]))

    def test_no_word_game_matches_itself_row_for_row(self):
        """Straight down the list is free marks — she can pair them by position
        without reading a single meaning."""
        self._seed()
        for q in [x for x in self._set().questions.all() if x.is_matching]:
            words = q.vocab_data["words"]
            for i, d in enumerate(q.vocab_data["definitions"]):
                self.assertNotEqual(d["word"], words[i],
                                    "%s: row %d pairs itself" % (q.prompt[:24], i + 1))

    # -- what the grown-ups see ---------------------------------------------

    def test_a_drawing_reaches_the_report_as_a_picture_not_as_json(self):
        """The stored answer is a stroke array. Left unformatted it reached the
        grader, the parent's work browser and the printed report as raw JSON,
        which reads as if she had answered in gibberish."""
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_drawing][0]
        sheet = ResponseSheet(question_set=self._set())
        sheet.answers = {str(q.pk): json.dumps({
            "strokes": [{"c": "#D64545", "w": 3, "p": [[0.1, 0.2], [0.6, 0.7]]},
                        {"c": "#2B6CB0", "w": 3, "p": [[0.2, 0.4], [0.8, 0.5]]}],
            "surface": {"w": 662, "h": 420}})}

        shown = sheet.answer_display(q)
        self.assertNotIn("strokes", shown)
        self.assertNotIn("#D64545", shown)
        self.assertIn("2 pen stroke", shown)
        # ...and the marks themselves are replayed, not just described.
        self.assertIsNotNone(sheet.answer_replay(q))

        sheet.answers = {str(q.pk): ""}
        self.assertEqual(sheet.answer_display(q), "(nothing drawn yet)")
        self.assertIsNone(sheet.answer_replay(q))

    def test_her_picture_does_not_print_with_its_own_config_across_it(self):
        """The replay draws her ink over the question's `passage` as the
        sentence she marked up. A drawing has no sentence — and its `passage`
        holds the widget's config — so this printed {"height": 560} in Georgia
        across her concert poster, on the report that goes to the charter
        school.
        """
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_drawing][-1]
        self.assertIn("height", q.passage, "the config really does live there")

        sheet = ResponseSheet(question_set=self._set())
        sheet.answers = {str(q.pk): json.dumps({
            "strokes": [{"c": "#D64545", "w": 3, "p": [[0.1, 0.2], [0.6, 0.7]]}],
            "surface": {"w": 662, "h": 560}})}
        replay = sheet.answer_replay(sheet.question_set.questions.get(pk=q.pk))
        self.assertIsNotNone(replay)
        self.assertEqual(replay.text, "", "blank paper stays blank")
        self.assertNotIn("height", str(replay.text))

    def test_a_typed_answer_left_behind_by_a_type_change_is_not_swallowed(self):
        """If a question is ever switched to drawing over an answer she already
        typed, her words are still in the sheet. Reporting "nothing drawn"
        would hide work she did from the grader and from her report."""
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_drawing][0]
        sheet = ResponseSheet(question_set=self._set())
        sheet.answers = {str(q.pk): "I drew the music going up and down."}
        self.assertEqual(sheet.answer_display(q),
                         "I drew the music going up and down.")

    def test_a_broken_height_does_not_take_the_page_down(self):
        """`int(inf)` raises OverflowError, which is not ValueError — the same
        trap `_parse_markup` already guards. A 500 here is her whole page."""
        self._seed()
        q = [x for x in self._set().questions.all() if x.is_drawing][0]
        for broken in ('{"height": 1e400}', '{"height": "tall"}', "{}",
                       "not json at all", '{"height": null}', "[]"):
            q.passage = broken
            self.assertEqual(q.drawing_height, 420, broken)
        q.passage = '{"height": 99999}'
        self.assertEqual(q.drawing_height, 900)     # bounded, not unbounded
        q.passage = '{"height": 1}'
        self.assertEqual(q.drawing_height, 200)

    def test_the_teacher_note_tells_the_grader_not_to_ask_for_prose(self):
        """An AI grader handed a rubric about paragraphs would mark a project
        with no paragraphs down for not having any."""
        self._seed()
        rubric = self._set().rubric.lower()
        self.assertIn("20 points", rubric)
        self.assertIn("not the spelling", rubric)
        self.assertIn("no prose here to mark", rubric)

    # -- the page she opens -------------------------------------------------

    def test_the_page_gives_her_paper_and_a_box_of_colours(self):
        self._seed()
        html = self.client.get(reverse(
            "portal:portal_questions",
            args=[self.token, self._set().pk])).content.decode()
        self.assertIn("drawing-widget", html)
        self.assertIn("drawing-surface", html)
        self.assertIn("Draw here", html)
        # Nine pencils, not the three greys a handwriting box gets.
        self.assertGreaterEqual(html.count('class="handwriting-pen'), 9)
        self.assertIn("vocab-matching", html)
        self.assertIn("choice-widget", html)
        # And no typing box anywhere on it.
        self.assertNotIn("portal-answer", html)

    def test_the_selected_pencil_is_the_one_that_draws(self):
        """The template rings the first colour; the stroke engine used to start
        on a navy of its own regardless. A child who picks black and gets navy
        has been told something untrue by her own page."""
        import os

        from django.conf import settings

        self._seed()
        html = self.client.get(reverse(
            "portal:portal_questions",
            args=[self.token, self._set().pk])).content.decode()
        first = html.split('class="handwriting-pen is-active"')[1]
        self.assertIn('data-color="#222222"', first.split(">")[0])

        js = os.path.join(settings.BASE_DIR, "static", "js",
                          "portal-handwriting.js")
        with open(js, encoding="utf-8") as fh:
            source = fh.read()
        self.assertIn(".handwriting-pen.is-active", source,
                      "the engine must read its starting colour off the page")

    def test_the_writing_surfaces_still_start_on_the_ink_they_always_did(self):
        """The stroke engine is SHARED. Making it read its colour off the page
        was right for a nine-colour palette, but it also means a careless edit
        to any other toolbar silently changes the ink Kaylin's handwriting and
        the Lexicon boxes have always used.
        """
        import os
        import re

        from django.conf import settings

        path = os.path.join(settings.BASE_DIR, "templates", "portal",
                            "portal_questions.html")
        with open(path, encoding="utf-8") as fh:
            markup = fh.read()
        selected = re.findall(
            r'class="handwriting-pen is-active"[^>]*data-color="([^"]+)"', markup)
        # Every writing surface (Lexicon box, handwriting question, the
        # answer-mode pane) opens on the navy pencil; only the drawing palette
        # differs, and it opens on black.
        self.assertEqual(sorted(set(selected)), ["#1d3557"])
        self.assertGreaterEqual(len(selected), 3)
        # The drawing palette is the model's, not the template's, and it opens
        # on black — which is the whole reason the engine had to stop assuming.
        self._seed()
        drawing = [q for q in self._set().questions.all() if q.is_drawing][0]
        self.assertEqual(drawing.drawing_colours[0]["hex"], "#222222")


class RubricReadabilityTests(TestCase):
    """The page a parent is on when they decide a mastery level.

    Rubrics are authored in Markdown — headings, bold, the standards table —
    because every other surface renders them. This one dumped the source, so a
    parent finalising an assessment read "### What she was asked to do" and
    "**Essential question:**" as literal text.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="rr", email="rr@e.com", password="pw")
        cls.family = Family.objects.create(name="RR Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family,
                                        role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.entry = WorkLogEntry.objects.create(
            parent=cls.parent, child=cls.child, subject="Social Studies",
            family=cls.family, description="Studies Weekly Week 1")

    def _assessment(self, rubric, answers="Q1 [reading]: Blank B\nA: b) compelling"):
        return MasteryAssessment.objects.create(
            work_entry=self.entry, rubric=rubric, answers=answers,
            ai_level="developing", status=MasteryAssessment.DRAFT)

    def _page(self, assessment):
        self.client.login(username="rr", password="pw")
        return self.client.get(
            reverse("tutor:assess_detail", kwargs={"pk": assessment.pk})
        ).content.decode()

    def test_the_rubric_is_rendered_not_dumped(self):
        a = self._assessment(
            "## Week 1: Developing Inquiries\n\n"
            "**Essential question:** What is inquiry?\n\n"
            "### What this week assesses\n"
            "| Framework | Questions |\n|---|---|\n| RI.3.1 | 1, 2, 3 |\n")
        html = self._page(a)

        body = html.split('class="assess-rubric"')[1].split("</div>")[0]
        self.assertIn("<h2>", body)
        self.assertIn("<h3>", body)
        self.assertIn("<strong>Essential question:</strong>", body)
        self.assertIn("<table>", body)
        # ...and none of the source markers survive as text.
        for marker in ("## Week 1", "### What this week", "**Essential",
                       "|---|"):
            self.assertNotIn(marker, body, "the Markdown source leaked through")

    def test_a_typed_rubric_cannot_carry_script_onto_a_reviewer_s_page(self):
        """A rubric is NOT seeder-only. `AssessmentRequestForm.rubric` is a
        textarea any editor posts to, and the finished assessment is read by
        every view role — including `teacher`, the charter-oversight account,
        which can hold memberships across several families. Rendering it with
        the raw-HTML-allowing filter would let an editor in one family run
        script in an overseer's session.
        """
        a = self._assessment(
            "## Real heading\n\n"
            "<script>alert(document.cookie)</script>\n\n"
            "<img src=x onerror=alert(1)>")
        html = self._page(a)
        body = html.split('class="assess-rubric"')[1].split("</div>")[0]

        # The words survive as escaped TEXT — that is the point — so assert on
        # the tags, which are what a browser would act on.
        self.assertNotIn("<script", body)
        self.assertNotIn("<img", body)
        self.assertIn("&lt;script&gt;", body, "shown as the text someone typed")
        self.assertIn("&lt;img", body)
        # ...and the formatting a rubric actually needs still works.
        self.assertIn("<h2>Real heading</h2>", body)

    def test_a_rubric_with_no_markdown_still_reads_normally(self):
        """Most rubrics are a plain sentence. Rendering must not mangle them."""
        a = self._assessment("Bonds to 100. Reward showing the working.")
        body = self._page(a).split('class="assess-rubric"')[1].split("</div>")[0]
        self.assertIn("Bonds to 100. Reward showing the working.", body)

    def test_the_child_s_own_words_are_never_rendered_as_markup(self):
        """The rubric is ours; her answers are hers. Rendering her text as
        Markdown would let anything she typed become markup on a parent's
        page — and would run her Q/A lines together into paragraphs."""
        a = self._assessment(
            "Plain rubric.",
            answers="Q1: Name a lens\nA: <script>alert(1)</script> **not bold**")
        html = self._page(a)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("**not bold**", html, "her asterisks are hers, kept as-is")


class WorklogTranscriptTests(TestCase):
    """The plain-text Q&A that reaches the work log, the grader and the
    parent's mastery page."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="wt", email="wt@e.com", password="pw")
        cls.family = Family.objects.create(name="WT Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family,
                                        role="parent")

    def test_a_prompt_s_markdown_does_not_leak_into_the_transcript(self):
        """Prompts are Markdown because the child's page renders them. This
        transcript is plain text, so "**Blank A**" arrived at the grader — and
        at a parent deciding a mastery level — with its asterisks on."""
        self.assertEqual(ResponseSheet._plain("**Blank B**"), "Blank B")
        self.assertEqual(ResponseSheet._plain("## Let's write. Pick a lens."),
                         "Let's write. Pick a lens.")
        self.assertEqual(
            ResponseSheet._plain("**Listen and draw.** Play **Eine kleine "
                                 "Nachtmusik**."),
            "Listen and draw. Play Eine kleine Nachtmusik.")

    def test_a_printed_blank_is_not_mistaken_for_emphasis(self):
        """`___A___` is the blank the child fills in, not underscore-bold.
        Stripping it gives "A _A_ question guides inquiry" — a different
        question from the one she was asked."""
        self.assertEqual(
            ResponseSheet._plain("A ___A___ question guides inquiry. "
                                 "___B___ questions look at smaller parts."),
            "A ___A___ question guides inquiry. ___B___ questions look at "
            "smaller parts.")

    def test_the_transcript_itself_is_clean_not_just_the_helper(self):
        """The helper was tested; the CALL was not. Reverting `as_worklog_text`
        to interpolating the raw prompt left the whole suite green, which means
        nothing was actually guarding the thing a parent reads."""
        from curricula.models import Chapter, Curriculum, Lesson

        child = Student.objects.create(
            parent=self.parent, first_name="Violet", grade_level="G03",
            family=self.family)
        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Transcript Fixture", subject="Social Studies",
            grade_level="G03", family=self.family)
        chapter = Chapter.objects.create(curriculum=curriculum, number=1, title="U1")
        lesson = Lesson.objects.create(chapter=chapter, number=1, order=1, title="L1")
        qset = QuestionSet.objects.create(
            lesson=lesson, title="Check", family=self.family,
            status=QuestionSet.APPROVED)
        q = Question.objects.create(
            question_set=qset, order=1, category="reading",
            prompt="**Blank A**", response_type=Question.TYPE_TEXT)
        blank = Question.objects.create(
            question_set=qset, order=2, category="reading",
            prompt="A ___A___ question guides inquiry.",
            response_type=Question.TYPE_TEXT)

        sheet = ResponseSheet.objects.create(question_set=qset, child=child)
        sheet.answers = {str(q.pk): "compelling", str(blank.pk): "compelling"}
        text = sheet.as_worklog_text()

        self.assertIn("Blank A", text)
        self.assertNotIn("**", text, "the prompt's Markdown reached the parent")
        self.assertIn("___A___", text, "the printed blank is not emphasis")

    def test_it_never_drops_the_words_themselves(self):
        """A stripper that eats content is worse than the markers it removes."""
        for prompt in ("What is 3 * 4?", "See #3 on the list.",
                       "Rate this 5 * out of 5", "a_b_c", "plain question"):
            self.assertEqual(ResponseSheet._plain(prompt), prompt)
        self.assertEqual(ResponseSheet._plain(""), "")
        self.assertEqual(ResponseSheet._plain(None), "")


class WeeklyRoutineTests(StudiesWeeklyLevel3Tests):
    """The teaching sequence, on the page a parent already opens.

    The publisher prescribes a real weekly routine — a question stimulus before
    anything else, a learning intention said out loud, two discussion questions
    — and prints it in a teacher edition. That is to say: somewhere other than
    where the teaching happens. Splitting attention between a PDF and the app is
    the reliable way for the spoken half of a lesson to stop happening.
    """

    def _guide(self):
        self._seed()
        return Material.objects.get(lesson__number=1).parent_content

    def test_the_spoken_steps_are_in_the_guide_at_all(self):
        """None of these existed anywhere in the app before. They are the half
        of the week that needs a grown-up, and they were invisible."""
        guide = self._guide()
        self.assertIn("This week, in order", guide)
        self.assertIn("The question is just as important as the answer", guide)
        self.assertIn("I am learning the parts of the inquiry process", guide)
        self.assertIn("looking at a problem with different lenses", guide)
        self.assertIn("help you understand others", guide)

    def test_every_step_says_where_it_happens(self):
        """The distinction the table exists for: what needs you, and what runs
        on her screen without you."""
        from tutor import weekly_l3w1 as w

        wheres = {s["where"] for s in w.ROUTINE["steps"]}
        self.assertEqual(wheres, {"out loud", "her screen"})
        guide = self._guide()
        rows = [line for line in guide.splitlines()
                if line.startswith("| ") and ("out loud" in line or "her screen" in line)]
        self.assertEqual(len(rows), len(w.ROUTINE["steps"]))

    def test_the_publisher_s_own_sequence_is_kept_in_order(self):
        """The pre-assessment comes FIRST — a question-generating exercise is
        worthless once she has read the answers. Reordering it to sit with the
        other discussion questions would quietly destroy it."""
        from tutor import weekly_l3w1 as w

        steps = [s["do"] for s in w.ROUTINE["steps"]]
        self.assertIn("just as important as the answer", steps[0])
        self.assertLess([i for i, s in enumerate(steps) if "Read the issue" in s][0],
                        [i for i, s in enumerate(steps) if "check" in s][0])
        self.assertIn("lens paragraph", steps[-1])

    def test_the_bad_day_version_is_there_and_is_shorter(self):
        """Rigid schedules fail on the first disrupted day, and a parent who has
        run out of afternoon drops something whether the guide says so or not.
        Saying WHICH, in advance, is the whole value."""
        from tutor import weekly_l3w1 as w

        self.assertTrue(w.ROUTINE["short"])
        self.assertLess(len(w.ROUTINE["short"]), len(w.ROUTINE["steps"]))
        guide = self._guide()
        self.assertIn("If today is a write-off", guide)
        # It keeps the opening question — dropping that keeps the week's shape
        # while losing the thing the unit is actually teaching.
        self.assertIn("The opening question", guide)

    def test_no_invented_timings_anywhere(self):
        """The publisher gives pacing for some weeks and marks others N/A. A
        number I made up would read as theirs."""
        guide = self._guide()
        table = guide[guide.find("This week, in order"):
                      guide.find("What this week assesses")]
        for invented in ("min", "minutes", "mins"):
            self.assertNotIn(invented, table.lower())

    def test_a_week_without_a_routine_simply_has_no_table(self):
        """Kaylin's week carries no ROUTINE yet. The guide must come out whole
        and unremarkable, not with an empty heading over an empty table."""
        call_command("seed_weekly", "--level", "7", "--week", "1",
                     "--for-user", "sw3", "--child-name", "Kaylin",
                     stdout=StringIO())
        guide = Material.objects.get(
            lesson__chapter__curriculum__name__startswith="Studies Weekly 7"
        ).parent_content
        self.assertNotIn("This week, in order", guide)
        self.assertNotIn("If today is a write-off", guide)
        self.assertIn("What this week assesses", guide)


class AssessedWorkTests(TestCase):
    """The parent judging a mastery level should be looking at the work.

    `MasteryAssessment.answers` is a plain-text snapshot taken at grading time —
    the right thing to send a model, the wrong thing to show a person. A drawing
    arrives in it as "[a drawing - 4 pen stroke(s)]" and a marked-up sentence as
    a sentence about marks, so the page asked a parent to grade work they could
    not see.
    """

    def setUp(self):
        from core.models import Family, FamilyMembership
        from curricula.models import Chapter, Curriculum, Lesson
        from students.models import Student
        from worklog.models import WorkLogEntry

        self.parent = User.objects.create_user(
            username="aw", email="aw@e.com", password="pw")
        self.family = Family.objects.create(name="AW Fam")
        FamilyMembership.objects.create(user=self.parent, family=self.family,
                                        role="parent")
        self.child = Student.objects.create(
            parent=self.parent, first_name="Violet", grade_level="G03",
            family=self.family)
        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Wolf", subject="Reading",
            grade_level="G03", family=self.family)
        chapter = Chapter.objects.create(curriculum=curriculum, number=1, title="U")
        self.lesson = Lesson.objects.create(chapter=chapter, number=1, order=1,
                                            title="L")
        self.entry = WorkLogEntry.objects.create(
            parent=self.parent, child=self.child, family=self.family,
            subject="Reading", description="a text snapshot")

    def _assessment_with_work(self):
        import json

        from tutor.models import (MasteryAssessment, Question, QuestionSet,
                                  ResponseSheet)

        qset = QuestionSet.objects.create(
            lesson=self.lesson, title="Wolf's Big Concert", family=self.family,
            status=QuestionSet.APPROVED)
        drawing = Question.objects.create(
            question_set=qset, order=1, category="application",
            prompt="Draw a grand piano.",
            response_type=Question.TYPE_DRAWING,
            passage=json.dumps({"height": 480}))
        typed = Question.objects.create(
            question_set=qset, order=2, category="writing",
            prompt="Which composer would Wolf sing?",
            response_type=Question.TYPE_TEXT)

        sheet = ResponseSheet.objects.create(
            question_set=qset, child=self.child, work_entry=self.entry,
            answers={
                str(drawing.pk): json.dumps({
                    "strokes": [{"c": "#D64545", "w": 3,
                                 "p": [[0.1, 0.2], [0.7, 0.6]]}],
                    "surface": {"w": 662, "h": 480}}),
                str(typed.pk): "Mozart, because Wolf is named after him.",
            })
        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, rubric="Grade the pictures, not the spelling.",
            answers=sheet.as_worklog_text(), ai_level="proficient",
            status=MasteryAssessment.DRAFT)
        return assessment, sheet, drawing, typed

    def _page(self, assessment):
        self.client.login(username="aw", password="pw")
        return self.client.get(
            reverse("tutor:assess_detail", kwargs={"pk": assessment.pk}))

    def test_a_drawing_is_shown_as_the_drawing(self):
        """The picture IS the answer. Describing it in words and asking for a
        mastery level is asking somebody to grade what they cannot see."""
        assessment, _sheet, _drawing, _typed = self._assessment_with_work()
        html = self._page(assessment).content.decode()

        # The strokes, replayed — the same rendering the work browser uses.
        self.assertIn("markup-replay", html)
        self.assertIn("Violet drew this", html)
        # ...and not the prose stand-in that the stored snapshot carries.
        self.assertNotIn("pen stroke(s)", html)

    def test_her_typed_answer_is_shown_next_to_its_question(self):
        assessment, _sheet, _drawing, _typed = self._assessment_with_work()
        html = self._page(assessment).content.decode()
        self.assertIn("Which composer would Wolf sing?", html)
        self.assertIn("Mozart, because Wolf is named after him.", html)

    def test_no_prompt_markdown_reaches_the_page_as_asterisks(self):
        """The snapshot was taken before prompts were cleaned, so old rows still
        carry "**Blank A**". Rendering the LIVE questions sidesteps that
        entirely — the page reads the work, not the transcript of it."""
        import json

        from tutor.models import MasteryAssessment, Question, QuestionSet, ResponseSheet

        qset = QuestionSet.objects.create(
            lesson=self.lesson, title="Check", family=self.family,
            status=QuestionSet.APPROVED)
        q = Question.objects.create(
            question_set=qset, order=1, category="reading",
            prompt="**Blank A**", response_type=Question.TYPE_TEXT)
        ResponseSheet.objects.create(
            question_set=qset, child=self.child, work_entry=self.entry,
            answers={str(q.pk): "compelling"})
        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, rubric="r",
            answers="Q1 [reading]: **Blank A**\nA: compelling",   # the old snapshot
            ai_level="proficient", status=MasteryAssessment.DRAFT)

        html = self._page(assessment).content.decode()
        self.assertIn("Blank A", html)
        self.assertNotIn("**Blank A**", html)

    def test_paper_work_is_shown_not_just_mentioned(self):
        """She did it on paper and photographed it in. The photo is the work."""
        from django.utils import timezone

        from tutor.models import MasteryAssessment, Question, QuestionSet, ResponseSheet

        qset = QuestionSet.objects.create(
            lesson=self.lesson, title="Project", family=self.family,
            status=QuestionSet.APPROVED)
        Question.objects.create(question_set=qset, order=1, category="application",
                                prompt="Make the poster.")
        sheet = ResponseSheet.objects.create(
            question_set=qset, child=self.child, work_entry=self.entry,
            answers={})
        # As a real paper submission looks: uploaded AND marked on paper.
        sheet.attachment = "uploads/poster.jpg"
        sheet.completion_mode = ResponseSheet.ON_PAPER
        sheet.approved_at = timezone.now()
        sheet.approved_by = self.parent
        sheet.save()

        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, rubric="r", answers="(on paper)",
            ai_level="proficient", status=MasteryAssessment.DRAFT)
        html = self._page(assessment).content.decode()
        self.assertIn("Turned in on paper", html)
        self.assertIn("poster.jpg", html)

    def test_on_screen_work_carrying_an_old_upload_is_not_called_paper_work(self):
        """Submitting on screen deliberately KEEPS an earlier upload attached,
        so gating the label on the attachment alone told a parent she had
        turned in on paper when she had typed her answers."""
        from django.utils import timezone

        from tutor.models import MasteryAssessment, Question, QuestionSet, ResponseSheet

        qset = QuestionSet.objects.create(
            lesson=self.lesson, title="Typed", family=self.family,
            status=QuestionSet.APPROVED)
        q = Question.objects.create(question_set=qset, order=1,
                                    category="writing", prompt="Write it.")
        sheet = ResponseSheet.objects.create(
            question_set=qset, child=self.child, work_entry=self.entry,
            answers={str(q.pk): "She typed this."})
        sheet.attachment = "uploads/earlier.jpg"          # still attached
        sheet.completion_mode = ResponseSheet.ON_SCREEN   # but typed
        sheet.save()

        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, rubric="r", answers="x",
            ai_level="proficient", status=MasteryAssessment.DRAFT)
        html = self._page(assessment).content.decode()
        self.assertIn("She typed this.", html)
        self.assertNotIn("Turned in on paper", html)

    def test_a_typed_rubric_with_no_sheet_still_shows_its_snapshot(self):
        """A rubric typed straight into the manual grading form has no questions
        behind it. The snapshot is all there is, and it must not vanish."""
        from tutor.models import MasteryAssessment

        assessment = MasteryAssessment.objects.create(
            work_entry=self.entry, rubric="Bonds to 100.",
            answers="98 + 2 = 100, shown with a number bond.",
            ai_level="proficient", status=MasteryAssessment.DRAFT)
        html = self._page(assessment).content.decode()
        self.assertIn("98 + 2 = 100, shown with a number bond.", html)


class HandsOnGleanEveryBookTests(TestCase):
    """Every Blackbird book gets a final project she can draw.

    Every one of I Am David's six printed options ends in writing, and four of
    The Folk Keeper's do. She read both books; she did not want to write about
    them a seventh time.

    What these guard is that the alternative is a real Grade 7 project and not a
    lighter one — each drawing carries an argument that needs the book.
    """

    @classmethod
    def setUpTestData(cls):
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(
            username="kg", email="kg@e.com", password="pw")
        cls.fam = Family.objects.create(name="KG Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.fam,
                                        role="parent")
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07",
            family=cls.fam)
        cls.token = make_portal_token(cls.kaylin)
        call_command("seed_i_am_david", "--for-user", "kg", stdout=StringIO())
        call_command("seed_the_folk_keeper", "--for-user", "kg", stdout=StringIO())

    def _set(self, contains):
        return QuestionSet.objects.get(title__contains=contains)

    BOOKS = ["What David Saw", "The Cellar and the Sea"]

    # -- it is an EXTRA option, not a replacement ---------------------------

    def test_the_guide_s_own_options_are_untouched(self):
        """The record has to show the purchased guide followed. She picks."""
        for book, marker in (("I Am David", "Epilogue"),
                             ("Folk Keeper", "Sealfolk research")):
            printed = QuestionSet.objects.get(
                lesson__chapter__curriculum__name__contains=book,
                title__endswith="Glean: Final Project")
            self.assertIn(marker, printed.intro)
            self.assertEqual(printed.questions.count(), 3)

    def test_each_book_now_offers_both(self):
        for book in ("I Am David", "Folk Keeper"):
            gleans = QuestionSet.objects.filter(
                lesson__chapter__curriculum__name__contains=book,
                title__contains="Glean")
            self.assertEqual(gleans.count(), 2, book)

    # -- and it is genuinely hands-on ---------------------------------------

    def test_it_is_drawing_with_exactly_one_thing_to_write(self):
        """The complaint was that ALL of it was writing, not that any of it
        was. One paragraph is right for a twelve-year-old; six is not."""
        for title in self.BOOKS:
            questions = list(self._set(title).questions.order_by("order"))
            drawings = [q for q in questions if q.is_drawing]
            written = [q for q in questions
                       if q.response_type == Question.TYPE_TEXT]
            self.assertEqual(len(drawings), 5, title)
            self.assertEqual(len(written), 1, title)
            self.assertTrue(written[0].offers_answer_mode,
                            "she can type it or write it by hand")
            self.assertTrue(questions[-1].is_self_eval)

    def test_the_big_pieces_get_more_paper(self):
        """A cover and a map need more room than an inventory sketch."""
        for title in self.BOOKS:
            heights = [q.drawing_height
                       for q in self._set(title).questions.all() if q.is_drawing]
            self.assertGreater(max(heights), min(heights), title)
            self.assertGreaterEqual(min(heights), 480, title)

    def test_the_self_check_asks_for_no_writing(self):
        for title in self.BOOKS:
            check = [q for q in self._set(title).questions.all() if q.is_self_eval][0]
            self.assertFalse(check.self_eval_wants_notes)
            self.assertEqual(check.self_eval_scale, ["Not yet", "Nearly", "Yes!"])

    # -- it is Grade 7, not Grade 3 -----------------------------------------

    def test_the_drawings_send_her_back_to_the_book(self):
        """This is what makes it a comprehension check rather than an art
        period: several of these cannot be done without re-reading."""
        david = " ".join(q.prompt + q.hint
                         for q in self._set("What David Saw").questions.all())
        self.assertIn("go back to the book", david.lower())
        self.assertIn("the same face, twice", david.lower())

        folk = " ".join(q.prompt + q.hint
                        for q in self._set("The Cellar and the Sea").questions.all())
        self.assertIn("defensible from the text", folk.lower())

    def test_no_prompt_asserts_a_plot_detail_i_could_have_got_wrong(self):
        """The prompts ask HER to find the details rather than supplying them —
        a list I invented would be wrong in a way she would trust."""
        david = self._set("What David Saw")
        bundle = david.questions.get(order=1)
        self.assertIn("get the list right", bundle.prompt)
        self.assertNotIn("soap", bundle.prompt.lower())
        journey = david.questions.get(order=3)
        self.assertIn("against the book", journey.hint)

    def test_the_teacher_note_says_it_is_not_the_easier_option(self):
        for title in self.BOOKS:
            rubric = self._set(title).rubric
            self.assertIn("20 points", rubric)
            self.assertIn("not the easier option", rubric)
            self.assertIn("on paper", rubric.lower())

    # -- the page she opens --------------------------------------------------

    def test_the_page_gives_her_paper_and_no_typing_box_but_one(self):
        for title in self.BOOKS:
            html = self.client.get(reverse(
                "portal:portal_questions",
                args=[self.token, self._set(title).pk])).content.decode()
            self.assertIn("drawing-widget", html)
            self.assertIn("Draw here", html)
            # The single written answer offers the pen as well as the keyboard.
            self.assertIn('data-mode="write"', html)
            self.assertIn("handwriting-canvas", html)

    def test_reseeding_changes_nothing(self):
        before = (QuestionSet.objects.count(), Question.objects.count())
        call_command("seed_i_am_david", "--for-user", "kg", stdout=StringIO())
        call_command("seed_the_folk_keeper", "--for-user", "kg", stdout=StringIO())
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)


class HandsOnGleanContentTests(SimpleTestCase):
    """The same promise, checked for EVERY book at once.

    Six books now carry one of these. A per-book test that only covered two of
    them would let the next one ship with five paragraphs and a drawing.
    """

    def _books(self):
        from tutor import glean_handson

        return glean_handson.BOOKS

    def test_every_book_has_one(self):
        """Six Blackbird guides, six hands-on options."""
        self.assertEqual(len(self._books()), 5)   # Wolf's lives in glean_wolf
        for key, book in self._books().items():
            self.assertTrue(book["title"], key)
            self.assertTrue(book["steps"], key)

    def test_every_one_of_them_is_drawing_with_one_thing_to_write(self):
        """The complaint was never that there was ANY writing — it was that
        there was nothing else. One short piece is right; six is not."""
        from tutor.models import Question

        for key, book in self._books().items():
            types = [extra["response_type"] for _c, _p, _h, extra in book["steps"]]
            self.assertGreaterEqual(types.count(Question.TYPE_DRAWING), 4, key)
            self.assertEqual(types.count(Question.TYPE_TEXT), 1, key)
            self.assertEqual(types[-1], Question.TYPE_SELF_EVAL, key)

    def test_the_one_written_step_lets_her_use_a_pen(self):
        for key, book in self._books().items():
            written = [extra for _c, _p, _h, extra in book["steps"]
                       if extra["response_type"] == "text"]
            self.assertTrue(written[0]["passage"].get("answer_mode"), key)

    def test_every_teacher_note_says_it_is_not_the_lighter_option(self):
        """A parent glancing at five drawings and one paragraph could
        reasonably assume it is the soft choice. It is not, and the note says
        so — along with the fact that paper is fine."""
        for key, book in self._books().items():
            rubric = book["rubric"]
            self.assertIn("20 points", rubric, key)
            self.assertIn("not the easier option", rubric.lower(), key)
            self.assertIn("on paper", rubric.lower(), key)

    def test_every_book_sends_her_back_to_its_own_text(self):
        """These are comprehension checks wearing different clothes. A project
        that could be done without opening the book is just an art period."""
        for key, book in self._books().items():
            words = " ".join(p + h for _c, p, h, _e in book["steps"]).lower()
            self.assertTrue(
                any(phrase in words for phrase in
                    ("go back to the book", "back to the book", "in the book",
                     "from the text", "against the book", "find the moment",
                     "find where", "look at the")),
                f"{key}: nothing sends her to the text")

    def test_the_self_check_never_asks_for_writing(self):
        for key, book in self._books().items():
            check = book["steps"][-1][3]["passage"]
            self.assertFalse(check.get("notes", True), key)
            self.assertGreaterEqual(len(check["items"]), 4, key)


class HandsOnGleanShapeTests(SimpleTestCase):
    """HH-199: these projects exist BECAUSE every printed option ends in writing.

    The father asked twice for no writing and got writing twice. These assert the
    properties that make them what they are, so a later edit cannot quietly undo
    the point of the file.
    """

    def _books(self):
        from tutor import glean_handson

        return glean_handson.BOOKS

    def test_no_project_contains_any_writing(self):
        from tutor.models import Question

        writing = {Question.TYPE_TEXT, Question.TYPE_PARAGRAPH,
                   Question.TYPE_WRITE_MARKUP, Question.TYPE_HANDWRITING}
        for key, book in self._books().items():
            for _cat, prompt, _hint, extra in book["steps"]:
                self.assertNotIn(
                    extra["response_type"], writing,
                    "%s asks her to write: %r" % (key, prompt[:60]))

    def test_each_project_is_mostly_making_not_drawing(self):
        """One drawing step at most. Five drawing prompts in a row is exactly
        what these replaced."""
        from tutor.models import Question

        for key, book in self._books().items():
            kinds = [e["response_type"] for _c, _p, _h, e in book["steps"]]
            self.assertLessEqual(kinds.count(Question.TYPE_DRAWING), 1, key)
            self.assertGreaterEqual(kinds.count(Question.TYPE_PHOTO), 4, key)

    def test_every_project_ends_in_a_tap_a_face_check(self):
        from tutor.models import Question

        for key, book in self._books().items():
            last = book["steps"][-1]
            self.assertEqual(last[3]["response_type"], Question.TYPE_SELF_EVAL, key)
            self.assertFalse(last[3]["passage"].get("notes"),
                             "%s reintroduces writing via self-eval notes" % key)

    def test_no_prompt_asserts_a_count_the_book_must_supply(self):
        """"Find three things he was given" is an unverified claim about how
        often the book does something. A child who hunts for three and finds one
        concludes she read badly. The hundred dresses is the one allowed number,
        because Wanda says it out loud."""
        import re

        # Only the dangerous form: a number that QUANTIFIES what she must find in
        # the text. "Draw it as six panels" counts her own work and is fine, as
        # is "take as many as you can find; do not stop before four" — open with
        # a floor cannot strand her. "Find three things he was given" can.
        banned = re.compile(
            r"\b(find|there are|there were)\s+(at least\s+|about\s+)?"
            r"(two|three|four|five|six|seven|eight|nine|ten|\d+)\b", re.I)
        # A hundred is Wanda's own number, said aloud in the text.
        allowed = {"hundred_dresses"}
        for key, book in self._books().items():
            if key in allowed:
                continue
            for _cat, prompt, hint, _extra in book["steps"]:
                for text in (prompt, hint):
                    self.assertIsNone(
                        banned.search(text),
                        "%s states a count the book must supply: %r" % (key, text[:90]))

    def test_every_project_has_teacher_notes_worth_the_same_marks(self):
        for key, book in self._books().items():
            self.assertIn("20 points", book["rubric"], key)
            self.assertTrue(book["title"], key)
            self.assertIn("##", book["intro"], key)


class RetireSupersededGleanTests(TestCase):
    """HH-199: renaming a project must not leave the retired one beside it.

    The seeders upsert on (lesson, title), so "What David Saw" becoming "The
    David Museum" created a second set and left the first — offering the child
    both the writing-based project and the making-based one that replaced it.
    """

    def setUp(self):
        from core.models import Family
        from curricula.models import Chapter, Curriculum, Lesson

        self.user = User.objects.create_user(username="rs", email="rs@e.com", password="pw")
        self.family = Family.objects.create(name="RS")
        self.curriculum = Curriculum.objects.create(
            parent=self.user, name="Blackbird", subject="Reading", family=self.family)
        chapter = Chapter.objects.create(curriculum=self.curriculum, number=5, title="Glean")
        self.lesson = Lesson.objects.create(chapter=chapter, order=1, number=1, title="Final")
        self.child = Student.objects.create(
            parent=self.user, first_name="Kaylin", grade_level="G07", family=self.family)

    def _set(self, title):
        return QuestionSet.objects.create(
            lesson=self.lesson, title=title, family=self.family,
            status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)

    def test_an_untouched_old_project_is_renamed_so_its_row_is_reused(self):
        from tutor import glean_handson

        old = self._set("Section 5 · Glean: What David Saw (hands-on)")
        glean_handson.retire_superseded(
            self.lesson, "Section 5 · Glean: The David Museum (hands-on)")
        old.refresh_from_db()
        self.assertEqual(old.title, "Section 5 · Glean: The David Museum (hands-on)")
        self.assertEqual(QuestionSet.objects.filter(
            lesson=self.lesson, title__endswith="(hands-on)").count(), 1)

    def test_an_old_project_is_removed_when_the_new_one_already_exists(self):
        """Renaming into an occupied title would leave two rows sharing it, and
        the next upsert would die with MultipleObjectsReturned."""
        from tutor import glean_handson

        self._set("Section 5 · Glean: What David Saw (hands-on)")
        self._set("Section 5 · Glean: The David Museum (hands-on)")
        glean_handson.retire_superseded(
            self.lesson, "Section 5 · Glean: The David Museum (hands-on)")
        titles = list(QuestionSet.objects.filter(
            lesson=self.lesson, title__endswith="(hands-on)").values_list("title", flat=True))
        self.assertEqual(titles, ["Section 5 · Glean: The David Museum (hands-on)"])

    def test_a_project_she_has_worked_on_is_never_binned(self):
        """Silently deleting a finished project is worse than a duplicate a
        parent can see and resolve."""
        from tutor import glean_handson

        old = self._set("Section 5 · Glean: What David Saw (hands-on)")
        ResponseSheet.objects.create(question_set=old, child=self.child)
        self._set("Section 5 · Glean: The David Museum (hands-on)")
        stranded = glean_handson.retire_superseded(
            self.lesson, "Section 5 · Glean: The David Museum (hands-on)")
        self.assertTrue(QuestionSet.objects.filter(pk=old.pk).exists())
        self.assertIn("Section 5 · Glean: What David Saw (hands-on)", stranded)

    def test_the_guides_own_printed_sets_are_never_touched(self):
        from tutor import glean_handson

        printed = self._set("Section 5 · Glean: Final Project")
        glean_handson.retire_superseded(
            self.lesson, "Section 5 · Glean: The David Museum (hands-on)")
        printed.refresh_from_db()
        self.assertEqual(printed.title, "Section 5 · Glean: Final Project")

    def test_it_does_nothing_when_there_is_nothing_to_retire(self):
        from tutor import glean_handson

        self.assertEqual(glean_handson.retire_superseded(
            self.lesson, "Section 5 · Glean: The David Museum (hands-on)"), [])
