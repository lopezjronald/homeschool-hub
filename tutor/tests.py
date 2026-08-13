import json
import os
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
        self.assertEqual(sets.count(), 25)                    # 4 x 6 + Glean
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
        # Everything else is the child's own written work.
        self.assertEqual(sets.filter(mode=QuestionSet.MODE_STUDENT).count(), 17)

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
        self.assertEqual(sets.count(), 25)
        self.assertEqual(sum(s.questions.count() for s in sets), 187)


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
        # Print gets its OWN scale: the report column is narrower on paper, and
        # one shared number is what cropped every printed drawing.
        self.assertLess(r.print_scale, r.scale)
        # Both contexts reserve their post-scale footprint; a transform doesn't.
        self.assertIn("--mr-fit-h:179px", r.style_vars)
        self.assertIn("--mr-print-h:173px", r.style_vars)

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
