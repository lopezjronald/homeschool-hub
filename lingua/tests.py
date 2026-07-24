"""Foundation tests: profile constants, the no-FK learner seam, the host-identity
directory, and the AIClient port/adapter — plus AST guards that ENFORCE the D-03/D-04
extractability rules (the module's whole reason to exist).

Repo convention: django.test.TestCase + setUpTestData, no pytest.
Run: `python manage.py collectstatic --noinput && python manage.py test lingua`.
"""
import ast
import inspect
import io
import json
import pathlib
import re

from django.contrib.auth import get_user_model
from django.db import models as dj_models
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from students.models import Student

from . import audio, cognates, leveling, profiles, services
from .integrations import directory
from .models import AuditEvent, Learner, LearnerProfile, Story, Theme
from .ports import AIClient, AIResult

User = get_user_model()


def _import_roots(source):
    """Top-level package name of every import in a Python source string."""
    roots = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:  # absolute only
            roots.add((node.module or "").split(".")[0])
    return roots


class ProfileConstantsTests(TestCase):
    def test_all_four_tracks_defined(self):
        for track in (profiles.KIDS_EARLY, profiles.KIDS_OLDER,
                      profiles.TEEN, profiles.ADULT):
            self.assertIn(track, profiles.PROFILES)

    def test_v1_active_is_the_two_kid_tracks(self):
        self.assertEqual(profiles.V1_ACTIVE,
                         {profiles.KIDS_EARLY, profiles.KIDS_OLDER})

    def test_kids_early_defaults(self):
        d = profiles.defaults_for(profiles.KIDS_EARLY)
        self.assertEqual(d["scheduler"], "leitner")
        self.assertEqual(d["support_level"], profiles.PARENT_MEDIATED)
        self.assertTrue(d["picture_first"])
        self.assertEqual(d["grader"], "parent")

    def test_session_cap_by_support_level_not_track(self):
        # D-66: the cap is a function of support_level.
        self.assertEqual(profiles.session_minutes_for(profiles.PARENT_MEDIATED), 10)
        self.assertEqual(profiles.session_minutes_for(profiles.GUIDED), 18)
        self.assertEqual(profiles.session_minutes_for(profiles.INDEPENDENT), 25)

    def test_ladder_is_l1_to_l8(self):
        self.assertEqual(profiles.LADDER[0], "L1")
        self.assertEqual(profiles.LADDER[-1], "L8")
        self.assertEqual(len(profiles.LADDER), 8)
        self.assertLess(profiles.level_rank("L1"), profiles.level_rank("L8"))


class LearnerSeamTests(TestCase):
    def test_host_reference_is_not_a_foreign_key(self):
        """D-03: the load-bearing rule. host_student_id must be a plain integer,
        never a relation to a host model."""
        field = Learner._meta.get_field("host_student_id")
        self.assertIsInstance(field, dj_models.IntegerField)
        self.assertFalse(field.is_relation)

    def test_no_lingua_model_fks_out_to_a_host_app(self):
        """No FK from ANY lingua model points outside the lingua app label (D-03).
        Iterates every current + future lingua model, not a hardcoded list."""
        from django.apps import apps
        for model in apps.get_app_config("lingua").get_models():
            for f in model._meta.get_fields():
                if isinstance(f, (dj_models.ForeignKey, dj_models.OneToOneField)):
                    self.assertEqual(
                        f.related_model._meta.app_label, "lingua",
                        f"{model.__name__}.{f.name} FKs out of lingua -> "
                        f"{f.related_model._meta.label} (violates D-03)",
                    )


class LearnerCreationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.early = Learner.create_for_host_student(101, profiles.KIDS_EARLY)
        cls.older = Learner.create_for_host_student(102, profiles.KIDS_OLDER)

    def test_creates_learner_and_seeded_profile(self):
        self.assertEqual(self.early.profile.track_profile, profiles.KIDS_EARLY)
        self.assertEqual(self.early.profile.support_level, profiles.PARENT_MEDIATED)
        self.assertEqual(self.early.profile.content_ceiling, "L1")
        self.assertEqual(self.early.language, "es")
        self.assertEqual(self.early.variant, "es-MX")

    def test_two_axes_are_independent(self):
        # D-65: a PARENT_MEDIATED learner may have an unrestricted ceiling.
        bright = Learner.create_for_host_student(
            103, profiles.KIDS_EARLY, content_ceiling="L8",
        )
        self.assertEqual(bright.profile.support_level, profiles.PARENT_MEDIATED)
        self.assertEqual(bright.profile.content_ceiling, "L8")

    def test_harder_content_does_not_lengthen_session(self):
        # D-66: session cap tracks support_level, not the ceiling.
        bright = Learner.create_for_host_student(
            104, profiles.KIDS_EARLY, content_ceiling="L8",
        )
        self.assertEqual(bright.profile.session_minutes, 10)  # same as any PARENT_MEDIATED

    def test_unknown_override_raises(self):
        # Guards typos (e.g. content_ceilng) before the service layer.
        with self.assertRaises(ValueError):
            Learner.create_for_host_student(
                105, profiles.KIDS_EARLY, content_ceilng="L8",
            )

    def test_host_student_id_is_unique(self):
        from django.db import IntegrityError, transaction
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Learner.objects.create(host_student_id=101)


class UserDirectoryTests(TestCase):
    """The single host-identity coupling point (D-04)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="p1", email="p1@example.com", password="x", is_active=True,
        )
        cls.student = Student.objects.create(
            parent=cls.parent, first_name="Ada", last_name="Lopez", grade_level="G03",
        )

    def test_learner_exists(self):
        self.assertTrue(directory.learner_exists(self.student.pk))
        self.assertFalse(directory.learner_exists(999999))

    def test_get_learner_display_resolves_name_and_level(self):
        info = directory.get_learner_display(self.student.pk)
        self.assertEqual(info, {"name": "Ada Lopez", "grade_level": "G03"})

    def test_get_learner_display_missing_returns_none(self):
        self.assertIsNone(directory.get_learner_display(999999))

    def test_list_for_family_scopes_by_family(self):
        # The student has no family set, so no family id lists it.
        self.assertEqual(directory.list_for_family(999999), [])

    def test_existing_student_ids_returns_only_real_ids(self):
        self.assertEqual(
            directory.existing_student_ids([self.student.pk, 999999]),
            {self.student.pk},
        )


class PortsAndAdapterTests(TestCase):
    """The AIClient port + host adapter seam (D-04)."""

    def test_ports_module_has_no_django_or_host_imports(self):
        """ports.py must IMPORT no Django/host coupling — AST-checked (prose may mention them)."""
        from lingua import ports as ports_mod
        roots = _import_roots(inspect.getsource(ports_mod))
        for forbidden in ("django", "tutor", "students", "homeschool_hub"):
            self.assertNotIn(forbidden, roots)

    def test_no_lingua_module_imports_host_except_directory(self):
        """D-04, generalized: across ALL of lingua/, only integrations/directory.py
        may import `students`, and NOTHING may import `tutor` or the host adapter.
        This is the enforcement the whole extractable-module design rests on."""
        root = pathlib.Path(inspect.getfile(services)).parent
        offenders = []
        for py in root.rglob("*.py"):
            rel = py.relative_to(root).as_posix()
            if rel == "tests.py" or rel.startswith("spikes/"):
                continue
            roots = _import_roots(py.read_text(encoding="utf-8"))
            if "tutor" in roots:
                offenders.append(f"{rel} imports tutor")
            if "homeschool_hub" in roots:
                offenders.append(f"{rel} imports the host (homeschool_hub)")
            if "students" in roots and rel != "integrations/directory.py":
                offenders.append(f"{rel} imports students")
        self.assertEqual(offenders, [], f"D-04 boundary violations: {offenders}")

    def test_factory_returns_an_aiclient(self):
        self.assertIsInstance(services.get_ai_client(), AIClient)

    @override_settings(ANTHROPIC_API_KEY="")
    def test_factory_adapter_reports_unconfigured_without_key(self):
        self.assertFalse(services.get_ai_client().is_configured())

    def test_fake_client_satisfies_the_contract(self):
        class _FakeAIClient(AIClient):
            def is_configured(self):
                return True

            def generate(self, *, system, user, max_tokens=1024, timeout=None, meta=None):
                return AIResult(text="hola", usage={"input_tokens": 1, "output_tokens": 1},
                                model="fake")

        r = _FakeAIClient().generate(system="s", user="u")
        self.assertIsInstance(r, AIResult)
        self.assertEqual(r.text, "hola")
        self.assertEqual(r.model, "fake")

    def test_adapter_raises_on_empty_text(self):
        """A text-less model reply must raise, not return a silent empty success."""
        from types import SimpleNamespace
        from unittest import mock

        from homeschool_hub.adapters.lingua_ai import TutorAIClient
        from tutor import ai

        fake_client = mock.Mock()
        fake_client.messages.create.return_value = SimpleNamespace(content=[], usage=None)
        with mock.patch("tutor.ai.is_configured", return_value=True), \
                mock.patch("tutor.ai._make_client", return_value=fake_client):
            with self.assertRaises(ai.GraderError):
                TutorAIClient().generate(system="s", user="u")


class OrphanCleanupTests(TestCase):
    """LGA-20: purge lingua rows when a host Student is deleted (D-03 = no cascade)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="op", email="op@example.com", password="x", is_active=True,
        )
        cls.student = Student.objects.create(
            parent=cls.parent, first_name="Bo", grade_level="G04",
        )
        cls.learner = Learner.create_for_host_student(cls.student.pk, profiles.KIDS_EARLY)

    def test_delete_learner_for_student_is_idempotent(self):
        n = services.delete_learner_for_student(self.student.pk)
        self.assertGreaterEqual(n, 1)  # learner + its profile
        self.assertFalse(Learner.objects.filter(host_student_id=self.student.pk).exists())
        # second call is a safe no-op
        self.assertEqual(services.delete_learner_for_student(self.student.pk), 0)

    def test_prune_orphans_deletes_orphans_keeps_valid(self):
        from io import StringIO

        from django.core.management import call_command

        Learner.create_for_host_student(999999, profiles.KIDS_OLDER)  # orphan: no host student
        call_command("lingua_prune_orphans", stdout=StringIO())
        self.assertFalse(Learner.objects.filter(host_student_id=999999).exists())
        self.assertTrue(Learner.objects.filter(host_student_id=self.student.pk).exists())

    def test_prune_orphans_dry_run_deletes_nothing(self):
        from io import StringIO

        from django.core.management import call_command

        Learner.create_for_host_student(999998, profiles.KIDS_OLDER)
        call_command("lingua_prune_orphans", "--dry-run", stdout=StringIO())
        self.assertTrue(Learner.objects.filter(host_student_id=999998).exists())


class CspScopingTests(TestCase):
    """D-13: CSP is scoped per-response to lingua views; no site-wide header."""

    def _through_middleware(self, view):
        from django.middleware.csp import ContentSecurityPolicyMiddleware
        return ContentSecurityPolicyMiddleware(view)(RequestFactory().get("/x"))

    def test_decorator_sets_a_strict_clean_policy(self):
        from django.http import HttpResponse
        from django.utils.csp import CSP

        from lingua.csp import lingua_csp

        @lingua_csp
        def view(request):
            return HttpResponse("ok")

        cfg = view(RequestFactory().get("/x"))._csp_config
        self.assertEqual(cfg["default-src"], [CSP.SELF])
        self.assertEqual(cfg["object-src"], [CSP.NONE])
        # CSP-clean: never 'unsafe-inline' in script/style.
        self.assertNotIn(CSP.UNSAFE_INLINE, cfg["script-src"])
        self.assertNotIn(CSP.UNSAFE_INLINE, cfg["style-src"])

    def test_middleware_emits_header_for_a_lingua_view(self):
        from django.http import HttpResponse

        from lingua.csp import lingua_csp

        @lingua_csp
        def view(request):
            return HttpResponse("ok")

        resp = self._through_middleware(view)
        self.assertIn("Content-Security-Policy", resp.headers)
        self.assertIn("default-src 'self'", resp.headers["Content-Security-Policy"])

    @override_settings(SECURE_CSP={}, SECURE_CSP_REPORT_ONLY={})
    def test_no_site_wide_header_for_an_undecorated_view(self):
        from django.http import HttpResponse

        def plain(request):
            return HttpResponse("ok")

        resp = self._through_middleware(plain)
        self.assertNotIn("Content-Security-Policy", resp.headers)

    def test_csp_middleware_and_context_processor_are_wired(self):
        from django.conf import settings
        self.assertIn(
            "django.middleware.csp.ContentSecurityPolicyMiddleware",
            settings.MIDDLEWARE,
        )

    def test_legacy_page_gets_no_csp_header(self):
        # The anti-leak guarantee, full-stack through the real middleware chain:
        # a non-lingua page must carry no CSP header (enforce or report-only).
        resp = self.client.get("/accounts/login/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("Content-Security-Policy", resp.headers)
        self.assertNotIn("Content-Security-Policy-Report-Only", resp.headers)


class LinguaTablePrefixTests(TestCase):
    """D-07 (replaced): every lingua table is lingua_-prefixed, so
    `pg_dump --table='lingua_*'` is a complete extraction (see EXTRACTION.md)."""

    def test_all_lingua_tables_are_prefixed(self):
        from django.apps import apps
        for model in apps.get_app_config("lingua").get_models():
            self.assertTrue(
                model._meta.db_table.startswith("lingua_"),
                f"{model._meta.label} table {model._meta.db_table!r} not lingua_-prefixed",
            )


class AuditEventTests(TestCase):
    """D-57: audit logs decisions/events, never payloads; closed action vocab."""

    def test_record_writes_a_structured_event(self):
        e = AuditEvent.record(
            "ai.generate_completed", actor_type=AuditEvent.AI,
            target_type="Story", target_id=5, summary="generated 1 story",
            metadata={"model": "x", "output_tokens": 10},
        )
        self.assertEqual(e.action, "ai.generate_completed")
        self.assertEqual(e.actor_type, AuditEvent.AI)
        self.assertEqual(e.metadata["output_tokens"], 10)

    def test_record_rejects_unknown_action(self):
        with self.assertRaises(ValueError):
            AuditEvent.record("ai.exfiltrate")

    def test_record_truncates_summary(self):
        e = AuditEvent.record("data.exported", summary="x" * 500)
        self.assertLessEqual(len(e.summary), 200)

    def test_audit_has_no_free_text_payload_field(self):
        # D-57: never store prompts/answers/child text in the audit trail.
        names = {f.name for f in AuditEvent._meta.get_fields()}
        for banned in ("prompt", "answer", "text", "body", "content", "output"):
            self.assertNotIn(banned, names)

    def test_record_rejects_payload_smuggled_in_metadata(self):
        # D-57 teeth: a long string value in metadata (a smuggled prompt/answer)
        # is rejected — metadata is for structured facts only.
        with self.assertRaises(ValueError):
            AuditEvent.record("ai.generate_completed", metadata={"prompt": "x" * 500})
        # short structured values are fine
        e = AuditEvent.record("ai.generate_completed", metadata={"model": "haiku", "output_tokens": 12})
        self.assertEqual(e.metadata["model"], "haiku")


class StoryContentTests(TestCase):
    """D-48/49/50: content lifecycle draft -> approve; only approved is servable."""

    def test_story_defaults_and_language(self):
        s = Story.objects.create(title="El gato", body="Hay un gato.", level="L1")
        self.assertEqual(s.status, Story.DRAFT)
        self.assertEqual(s.language, "es")   # D-02
        self.assertEqual(s.variant, "es-MX")
        self.assertFalse(s.is_servable)

    def test_approve_marks_servable_and_audits(self):
        s = Story.objects.create(title="El perro", body="Hay un perro.", level="L2",
                                 status=Story.PENDING)
        s.approve(host_user_id=7)
        s.refresh_from_db()
        self.assertEqual(s.status, Story.APPROVED)
        self.assertEqual(s.approved_by, 7)
        self.assertIsNotNone(s.approved_at)
        self.assertTrue(s.is_servable)
        # approval wrote an audit event (D-57), reusing the LGA-27 seed
        evs = AuditEvent.objects.filter(action="content.approved", target_id=s.pk)
        self.assertEqual(evs.count(), 1)  # exactly one audit event
        self.assertEqual(evs.first().actor_id, 7)

    def test_reject_is_not_servable_and_audits(self):
        s = Story.objects.create(title="x", body="y", level="L1", status=Story.PENDING)
        s.reject(host_user_id=7)
        s.refresh_from_db()
        self.assertEqual(s.status, Story.REJECTED)
        self.assertFalse(s.is_servable)
        self.assertTrue(
            AuditEvent.objects.filter(action="content.rejected", target_id=s.pk).exists()
        )

    def test_theme_age_band(self):
        t = Theme.objects.create(slug="animals", name="Animals",
                                 age_band=profiles.KIDS_EARLY)
        s = Story.objects.create(title="El gato", body="...", level="L1", theme=t)
        self.assertEqual(s.theme.name, "Animals")
        self.assertEqual(t.stories.count(), 1)

    def test_deleting_theme_keeps_story(self):
        # SET_NULL: an expensively-approved story must survive losing its theme.
        t = Theme.objects.create(slug="space", name="Space",
                                 age_band=profiles.KIDS_OLDER)
        s = Story.objects.create(title="La luna", body="...", level="L2", theme=t)
        t.delete()
        s.refresh_from_db()
        self.assertIsNone(s.theme)


class _ScriptedAIClient(AIClient):
    """Fake AIClient: returns critic JSON when handed the critic system prompt,
    otherwise the story JSON. Counts calls."""

    def __init__(self, story_json, critic_json):
        self._story, self._critic = story_json, critic_json
        self.calls = 0

    def is_configured(self):
        return True

    def generate(self, *, system, user, max_tokens=1024, timeout=None, meta=None):
        from lingua.prompts import CRITIC_SYSTEM
        self.calls += 1
        payload = self._critic if system == CRITIC_SYSTEM else self._story
        return AIResult(text=payload, usage={"input_tokens": 5, "output_tokens": 10},
                        model="fake")


class GenerationTests(TestCase):
    """D-48/49: generate -> LLM-critic -> persist a Story draft."""

    @classmethod
    def setUpTestData(cls):
        cls.theme = Theme.objects.create(slug="animals", name="Animals",
                                         age_band=profiles.KIDS_EARLY)

    def test_passed_draft_lands_pending(self):
        fake = _ScriptedAIClient('{"title":"El gato","body":"Hay un gato pequeño."}',
                                 '{"passed":true,"flags":[]}')
        s = services.create_story_draft(theme=self.theme, level="L1", ai_client=fake)
        self.assertEqual(s.status, Story.PENDING)
        self.assertTrue(s.critic_passed)
        self.assertEqual(s.title, "El gato")
        self.assertEqual(s.theme, self.theme)
        self.assertEqual(s.source, Story.SOURCE_GENERATED)
        self.assertEqual(fake.calls, 2)  # generate + critic

    def test_flagged_draft_lands_draft_with_flags(self):
        fake = _ScriptedAIClient('{"title":"x","body":"y"}',
                                 '{"passed":false,"flags":["gender error: la problema"]}')
        s = services.create_story_draft(theme=self.theme, level="L2", ai_client=fake)
        self.assertEqual(s.status, Story.DRAFT)
        self.assertFalse(s.critic_passed)
        self.assertIn("gender error: la problema", s.critic_flags)
        self.assertFalse(s.is_servable)

    def test_tolerates_markdown_json_fences(self):
        fake = _ScriptedAIClient('```json\n{"title":"T","body":"B"}\n```',
                                 '```\n{"passed":true,"flags":[]}\n```')
        s = services.create_story_draft(theme=self.theme, level="L1", ai_client=fake)
        self.assertEqual(s.title, "T")
        self.assertEqual(s.body, "B")

    def test_generation_writes_one_audit_event_with_tokens(self):
        fake = _ScriptedAIClient('{"title":"T","body":"B"}', '{"passed":true,"flags":[]}')
        s = services.create_story_draft(theme=self.theme, level="L1", ai_client=fake)
        evs = AuditEvent.objects.filter(action="ai.generate_completed", target_id=s.pk)
        self.assertEqual(evs.count(), 1)
        self.assertEqual(evs.first().actor_type, AuditEvent.AI)
        self.assertTrue(evs.first().metadata["critic_passed"])
        # summed tokens across generate + critic (15 each) feed the cost ceiling
        self.assertEqual(evs.first().metadata["tokens"], 30)

    def test_empty_title_falls_back(self):
        fake = _ScriptedAIClient('{"title":"","body":"Hay un gato."}',
                                 '{"passed":true,"flags":[]}')
        s = services.create_story_draft(theme=self.theme, level="L1", ai_client=fake)
        self.assertEqual(s.title, "(sin título)")

    def test_generation_failure_audits_and_raises_no_partial(self):
        # A malformed model reply -> ai.generate_failed recorded, exception raised,
        # and NO Story / no generate_completed left behind.
        fake = _ScriptedAIClient("this is not json", '{"passed":true,"flags":[]}')
        with self.assertRaises(Exception):
            services.create_story_draft(theme=self.theme, level="L1", ai_client=fake)
        self.assertTrue(
            AuditEvent.objects.filter(action="ai.generate_failed",
                                      target_id=self.theme.pk).exists()
        )
        self.assertFalse(Story.objects.exists())
        self.assertFalse(AuditEvent.objects.filter(action="ai.generate_completed").exists())

    def test_command_rejects_bad_level_and_missing_theme(self):
        from django.core.management import CommandError, call_command
        from io import StringIO
        with self.assertRaises(CommandError):
            call_command("generate_stories", "animals", "--level", "L99", stderr=StringIO())
        with self.assertRaises(CommandError):
            call_command("generate_stories", "nope", "--level", "L1", stderr=StringIO())

    def test_generation_populates_leveling_signal(self):
        fake = _ScriptedAIClient('{"title":"El gato","body":"Hay un gato pequeño."}',
                                 '{"passed":true,"flags":[]}')
        s = services.create_story_draft(theme=self.theme, level="L1", ai_client=fake)
        self.assertEqual(s.suggested_level, "L1")     # simple text reads easy
        self.assertIsInstance(s.flagged_words, list)  # soft signal populated

    def test_leveling_failure_does_not_abort_generation(self):
        # A soft signal must never lose a paid-for story: leveling errors degrade.
        from unittest import mock
        fake = _ScriptedAIClient('{"title":"T","body":"B"}', '{"passed":true,"flags":[]}')
        with mock.patch("lingua.services.leveling.analyze",
                        side_effect=RuntimeError("boom")):
            s = services.create_story_draft(theme=self.theme, level="L1", ai_client=fake)
        self.assertEqual(s.status, Story.PENDING)     # story still created
        self.assertEqual(s.suggested_level, "")       # degraded signal
        self.assertTrue(
            AuditEvent.objects.filter(action="ai.generate_completed", target_id=s.pk).exists()
        )


class ApprovalUITests(TestCase):
    """D-50: parent batch-approves pending drafts; editors only."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="ap", email="ap@example.com", password="pw", is_active=True,
        )
        cls.theme = Theme.objects.create(slug="a", name="A", age_band=profiles.KIDS_EARLY)

    def _pending(self, title="T"):
        return Story.objects.create(title=title, body="Hay un gato.", level="L1",
                                    theme=self.theme, status=Story.PENDING)

    def test_editor_sees_pending_drafts(self):
        self._pending("El gato pendiente")
        self.client.force_login(self.parent)
        resp = self.client.get(reverse("lingua:approvals"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "El gato pendiente")

    def test_approve_selected_flips_status_multi_and_audits(self):
        s1, s2 = self._pending("uno"), self._pending("dos")
        self.client.force_login(self.parent)
        resp = self.client.post(
            reverse("lingua:approvals"),
            {"action": "approve", "story_ids": [s1.pk, s2.pk]}, follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        for s in (s1, s2):
            s.refresh_from_db()
            self.assertEqual(s.status, Story.APPROVED)
            self.assertTrue(s.is_servable)
        self.assertContains(resp, "2 stories approved")
        self.assertEqual(AuditEvent.objects.filter(action="content.approved").count(), 2)

    def test_non_pending_id_is_a_noop(self):
        # The status=PENDING filter is the replay/forgery guard: re-POSTing an
        # already-approved id must not re-approve or alter it.
        s = Story.objects.create(title="done", body="x", level="L1",
                                 theme=self.theme, status=Story.APPROVED)
        self.client.force_login(self.parent)
        resp = self.client.post(
            reverse("lingua:approvals"),
            {"action": "approve", "story_ids": [s.pk]}, follow=True,
        )
        s.refresh_from_db()
        self.assertEqual(s.status, Story.APPROVED)
        self.assertContains(resp, "No stories selected")
        self.assertFalse(AuditEvent.objects.filter(action="content.approved").exists())

    def test_forged_junk_ids_do_not_500(self):
        self.client.force_login(self.parent)
        resp = self.client.post(
            reverse("lingua:approvals"),
            {"action": "approve", "story_ids": ["abc", "1x", "99999999999999999999"]},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)

    def test_reject_selected(self):
        s = self._pending()
        self.client.force_login(self.parent)
        self.client.post(reverse("lingua:approvals"),
                         {"action": "reject", "story_ids": [s.pk]})
        s.refresh_from_db()
        self.assertEqual(s.status, Story.REJECTED)

    def test_requires_login(self):
        resp = self.client.get(reverse("lingua:approvals"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login", resp.url)

    def test_non_editor_gets_404(self):
        from core.models import Family, FamilyMembership
        teacher = User.objects.create_user(
            username="tt", email="tt@example.com", password="pw", is_active=True,
        )
        fam = Family.objects.create(name="F")
        FamilyMembership.objects.create(user=teacher, family=fam, role="teacher")
        self.client.force_login(teacher)
        resp = self.client.get(reverse("lingua:approvals"))
        self.assertEqual(resp.status_code, 404)


class LevelingTests(TestCase):
    """D-25/LGA-44: frequency-band leveling as a soft signal (from SPIKE-03)."""

    def test_simple_text_scores_low(self):
        r = leveling.analyze("Hay un gato pequeño. El niño ve el gato.")
        self.assertEqual(r["suggested_level"], "L1")
        self.assertLess(r["out_of_band_pct"], 6)

    def test_rich_text_scores_higher_and_flags_words(self):
        r = leveling.analyze(
            "El felino acechaba sigilosamente entre la espesura contemplando el ocaso."
        )
        self.assertGreater(profiles.level_rank(r["suggested_level"]),
                           profiles.level_rank("L1"))
        self.assertIn("felino", r["out_of_band_words"])

    def test_empty_text(self):
        r = leveling.analyze("")
        self.assertIsNone(r["suggested_level"])
        self.assertEqual(r["out_of_band_words"], [])

    def test_level_for_boundaries(self):
        self.assertEqual(leveling._level_for(0), "L1")
        self.assertEqual(leveling._level_for(6), "L1")
        self.assertEqual(leveling._level_for(6.01), "L2")
        self.assertEqual(leveling._level_for(70), "L7")
        self.assertEqual(leveling._level_for(70.1), "L8")


class CognateTests(TestCase):
    """pedagogy-8 / D-28: cognate detection + the false-friend safety net."""

    def test_dice_similarity(self):
        self.assertEqual(cognates.dice_similarity("animal", "animal"), 1.0)
        self.assertGreater(cognates.dice_similarity("información", "information"), 0.6)
        self.assertLess(cognates.dice_similarity("perro", "dog"), 0.3)  # clearly non-cognate

    def test_normalize_strips_diacritics(self):
        self.assertEqual(cognates.normalize("Ñoño"), "nono")
        self.assertEqual(cognates.normalize("ÉXITO"), "exito")

    def test_false_friend_detection(self):
        self.assertTrue(cognates.is_false_friend("embarazada"))
        self.assertTrue(cognates.is_false_friend("Librería"))  # accent + case insensitive
        self.assertEqual(cognates.false_friend_note("sopa"), ("soap", "soup"))
        self.assertIsNone(cognates.false_friend_note("gato"))

    def test_cognate_detection_excludes_false_friends(self):
        self.assertTrue(cognates.is_cognate("animal"))
        self.assertTrue(cognates.is_cognate("hospital"))
        self.assertFalse(cognates.is_cognate("gato"))          # not a cognate
        self.assertFalse(cognates.is_cognate("embarazada"))    # false friend, never a cognate

    def test_looks_cognate_respects_false_friends(self):
        self.assertTrue(cognates.looks_cognate("información", "information"))
        # a false friend is never a cognate even if orthographically similar
        self.assertFalse(cognates.looks_cognate("embarazada", "embarrassed"))

    def test_dice_edge_cases(self):
        self.assertEqual(cognates.dice_similarity("", ""), 1.0)
        self.assertEqual(cognates.dice_similarity("", "x"), 0.0)
        self.assertEqual(cognates.dice_similarity("a", "a"), 1.0)

    def test_analyze_text(self):
        r = cognates.analyze_text(
            "El animal está en el hospital. La librería es grande. El gato duerme."
        )
        self.assertIn("animal", r["cognates"])
        self.assertIn("hospital", r["cognates"])
        self.assertIn("librería", r["false_friends"])
        # safety net at the text level: a false friend never lands in cognates,
        # and a plain non-cognate word appears in neither.
        self.assertNotIn("librería", r["cognates"])
        self.assertNotIn("gato", r["cognates"])
        self.assertNotIn("gato", r["false_friends"])


class ThemeRotationTests(TestCase):
    """LGA-46 / D-51 / N-01: age-banded theme rotation + bounded choice."""

    @classmethod
    def setUpTestData(cls):
        cls.early = [
            Theme.objects.create(slug=f"e{i}", name=f"Early {i}",
                                 age_band=profiles.KIDS_EARLY)
            for i in range(4)
        ]
        cls.older = Theme.objects.create(slug="o1", name="Older 1",
                                         age_band=profiles.KIDS_OLDER)

    def _approve(self, theme, n):
        for i in range(n):
            Story.objects.create(title=f"t{i}", body="...", level="L1",
                                 theme=theme, status=Story.APPROVED)

    def test_rotate_is_bounded_and_band_scoped(self):
        picks = services.rotate_themes(profiles.KIDS_EARLY, count=3)
        self.assertEqual(len(picks), 3)                     # capped at count
        self.assertTrue(all(t.age_band == profiles.KIDS_EARLY for t in picks))

    def test_rotate_orders_least_covered_first(self):
        # Give the alphabetically-first theme the MOST approved stories, so a
        # naive name-only sort would surface it first — coverage ordering must not.
        self._approve(self.early[0], 5)   # "Early 0"
        self._approve(self.early[1], 1)   # "Early 1"
        picks = services.rotate_themes(profiles.KIDS_EARLY, count=4)
        # Two untouched themes (0 approved) come first, then the 1-story, then 5.
        self.assertEqual(picks[0].n_approved, 0)
        self.assertEqual([t.slug for t in picks[-2:]], ["e1", "e0"])

    def test_only_approved_stories_count_toward_coverage(self):
        # Pending/draft/rejected drafts are not servable, so they must NOT sink a
        # theme's rotation priority (else a theme of unapproved drafts starves).
        for status in (Story.PENDING, Story.DRAFT, Story.REJECTED):
            Story.objects.create(title="x", body="...", level="L1",
                                 theme=self.early[0], status=status)
        picks = services.rotate_themes(profiles.KIDS_EARLY, count=4)
        self.assertTrue(all(t.n_approved == 0 for t in picks))

    def test_rotate_excludes_inactive(self):
        self.early[0].active = False
        self.early[0].save(update_fields=["active"])
        slugs = {t.slug for t in services.rotate_themes(profiles.KIDS_EARLY, count=9)}
        self.assertNotIn("e0", slugs)
        self.assertEqual(len(slugs), 3)   # 4 seeded − 1 inactive

    def test_rotate_nonpositive_count_is_empty(self):
        self.assertEqual(services.rotate_themes(profiles.KIDS_EARLY, count=0), [])

    def test_next_theme_picks_thinnest_or_none(self):
        self._approve(self.early[0], 2)
        pick = services.next_theme(profiles.KIDS_EARLY)
        self.assertEqual(pick.n_approved, 0)              # thinnest, not e0
        self.assertIsNone(services.next_theme(profiles.TEEN))  # empty band

    def test_seed_themes_is_idempotent(self):
        from io import StringIO

        from django.core.management import call_command

        # Start clean so the seed count is deterministic regardless of setUpTestData.
        Theme.objects.all().delete()
        call_command("seed_themes", stdout=StringIO())
        first = Theme.objects.count()
        self.assertGreater(first, 0)
        self.assertTrue(Theme.objects.filter(age_band=profiles.KIDS_EARLY).exists())
        self.assertTrue(Theme.objects.filter(age_band=profiles.KIDS_OLDER).exists())
        call_command("seed_themes", stdout=StringIO())     # re-run
        self.assertEqual(Theme.objects.count(), first)     # no duplicates

    def test_seed_themes_band_filter(self):
        from io import StringIO

        from django.core.management import call_command

        Theme.objects.all().delete()
        call_command("seed_themes", "--band", profiles.KIDS_OLDER, stdout=StringIO())
        self.assertFalse(Theme.objects.filter(age_band=profiles.KIDS_EARLY).exists())
        self.assertTrue(Theme.objects.filter(age_band=profiles.KIDS_OLDER).exists())


class _FakePolly:
    """Fake boto3 Polly client: mp3 bytes for OutputFormat=mp3, JSON-Lines word
    marks for OutputFormat=json. Records calls so tests can assert the API contract."""

    def __init__(self, marks, audio_bytes=b"ID3\x03fake-mp3", raises=None):
        self._marks = marks
        self._audio = audio_bytes
        self._raises = raises
        self.calls = []

    def synthesize_speech(self, **kw):
        self.calls.append(kw)
        if self._raises:
            raise self._raises
        if kw["OutputFormat"] == "mp3":
            return {"AudioStream": io.BytesIO(self._audio)}
        lines = "\n".join(json.dumps(m) for m in self._marks)
        return {"AudioStream": io.BytesIO(lines.encode("utf-8"))}


def _simulate_polly_marks(text):
    """Simulate Polly word marks for ``text``: for each whitespace token, mark the
    leading word-character run (Polly reports the word, not trailing punctuation),
    with UTF-8 BYTE offsets — exactly the hazard build_timings must undo."""
    marks = []
    for k, tok in enumerate(re.finditer(r"\S+", text)):
        wm = re.search(r"[^\W]+", tok.group(), re.UNICODE)  # word run inside the token
        if not wm:
            continue
        cs = tok.start() + wm.start()
        ce = tok.start() + wm.end()
        marks.append({
            "time": k * 300, "type": "word",
            "start": len(text[:cs].encode("utf-8")),
            "end": len(text[:ce].encode("utf-8")),
            "value": wm.group(),
        })
    return marks


# Accents (á é í ó ú ñ) + inverted punctuation (¿ ¡) — the 2-byte hazard.
_ACCENT_STORY = "¿Dónde está el pájaro? ¡Ñoño corre rápido!"


class AudioSynthTests(TestCase):
    """LGA-34: Polly synthesis boundary (D-17/D-18). Client injected, no AWS."""

    def test_returns_audio_and_word_marks(self):
        marks = _simulate_polly_marks(_ACCENT_STORY)
        client = _FakePolly(marks)
        out = audio.synthesize(_ACCENT_STORY, client=client)
        self.assertEqual(out["audio"], b"ID3\x03fake-mp3")
        # one word mark per word token (all tokens here have word chars)
        self.assertEqual(len(out["marks"]), len(marks))
        self.assertTrue(all(m["type"] == "word" for m in out["marks"]))
        # two calls: mp3 then json marks, both plain text
        self.assertEqual([c["OutputFormat"] for c in client.calls], ["mp3", "json"])
        self.assertEqual(client.calls[1]["SpeechMarkTypes"], ["word"])
        self.assertTrue(all(c["TextType"] == "text" for c in client.calls))

    def test_filters_non_word_marks(self):
        marks = [{"time": 0, "type": "sentence", "start": 0, "end": 5, "value": "x"},
                 {"time": 10, "type": "word", "start": 0, "end": 5, "value": "Hola"}]
        out = audio.synthesize("Hola", client=_FakePolly(marks))
        self.assertEqual(len(out["marks"]), 1)
        self.assertEqual(out["marks"][0]["value"], "Hola")

    def test_reads_voice_engine_from_settings(self):
        # Override with values DISTINCT from the hardcoded .get() fallbacks so this
        # actually exercises the settings->synthesize wiring (not the fallback).
        from django.conf import settings as dj_settings
        cfg = {**dj_settings.LINGUA, "TTS_VOICE": "Lupe", "TTS_ENGINE": "standard"}
        with override_settings(LINGUA=cfg):
            client = _FakePolly(_simulate_polly_marks("Hola mundo"))
            out = audio.synthesize("Hola mundo", client=client)
        self.assertEqual((out["voice"], out["engine"]), ("Lupe", "standard"))
        self.assertEqual(client.calls[0]["VoiceId"], "Lupe")
        self.assertEqual(client.calls[0]["Engine"], "standard")

    def test_explicit_args_override_settings(self):
        client = _FakePolly(_simulate_polly_marks("Hola"))
        audio.synthesize("Hola", voice="Andres", engine="standard", client=client)
        self.assertEqual(client.calls[0]["VoiceId"], "Andres")
        self.assertEqual(client.calls[0]["Engine"], "standard")

    def test_empty_text_raises(self):
        with self.assertRaises(audio.TTSError):
            audio.synthesize("   ", client=_FakePolly([]))

    def test_client_error_is_wrapped(self):
        client = _FakePolly([], raises=RuntimeError("boom"))
        with self.assertRaises(audio.TTSError):
            audio.synthesize("Hola", client=client)

    def test_malformed_marks_line_is_wrapped_as_ttserror(self):
        # A truncated/garbage marks line must surface as TTSError (so tts_build skips
        # one story), NOT a raw JSONDecodeError that aborts the whole batch run.
        class _BadMarksPolly:
            def __init__(self):
                self.calls = []

            def synthesize_speech(self, **kw):
                self.calls.append(kw)
                if kw["OutputFormat"] == "mp3":
                    return {"AudioStream": io.BytesIO(b"ID3\x03mp3")}
                return {"AudioStream": io.BytesIO(b'{"time":0,"type":"wo')}  # truncated
        with self.assertRaises(audio.TTSError):
            audio.synthesize("Hola", client=_BadMarksPolly())


class AudioTimingTests(TestCase):
    """LGA-35 / D-21: byte→char mapping + flat char-offset timing JSON."""

    def test_byte_to_char_map_recovers_accented_words(self):
        text = _ACCENT_STORY
        b2c = audio.byte_to_char_map(text)
        # naive byte-as-char slicing is wrong; the map recovers the true word.
        for m in re.finditer(r"[^\W]+", text, re.UNICODE):
            bstart = len(text[:m.start()].encode("utf-8"))
            bend = len(text[:m.end()].encode("utf-8"))
            self.assertEqual(text[b2c[bstart]:b2c[bend]], m.group())

    def test_char_offsets_correct_across_accents(self):
        marks = _simulate_polly_marks(_ACCENT_STORY)
        t = audio.build_timings(_ACCENT_STORY, marks)
        self.assertEqual(len(t["words"]), len(marks))
        for w, m in zip(t["words"], marks):
            # cs/ce are CHARACTER offsets that slice the true word out of the source
            self.assertEqual(_ACCENT_STORY[w["cs"]:w["ce"]], m["value"])
            self.assertNotIn("start", w)  # no byte offsets exposed (D-21)
            self.assertNotIn("end", w)

    def test_words_are_monotonic_and_end_chains_to_next(self):
        marks = _simulate_polly_marks(_ACCENT_STORY)
        words = audio.build_timings(_ACCENT_STORY, marks, tail_ms=400)["words"]
        starts = [w["s_ms"] for w in words]
        self.assertEqual(starts, sorted(starts))  # binary-searchable
        for i in range(len(words) - 1):
            self.assertEqual(words[i]["e_ms"], words[i + 1]["s_ms"])
        self.assertEqual(words[-1]["e_ms"], words[-1]["s_ms"] + 400)  # tail

    def test_word_maps_to_containing_display_token(self):
        t = audio.build_timings(_ACCENT_STORY, _simulate_polly_marks(_ACCENT_STORY))
        # first word "Dónde" sits inside display token 0 "¿Dónde"
        self.assertEqual(t["tokens"][0], "¿Dónde")
        self.assertEqual(t["words"][0]["i"], 0)
        # every word's token index is valid and its char span lies within that token
        for w in t["words"]:
            cs_lo, cs_hi = t["token_spans"][w["i"]]
            self.assertTrue(cs_lo <= w["cs"] < cs_hi)

    def test_skips_offset_that_misses_a_char_boundary(self):
        # A mark starting mid-accent (byte offset lands inside a 2-byte char) must be
        # dropped, not crash or corrupt the array.
        good = _simulate_polly_marks("Dónde")[0]
        bad = dict(good, start=good["start"] + 2)  # +2 bytes = inside "ó"
        t = audio.build_timings("Dónde", [good, bad])
        self.assertEqual(len(t["words"]), 1)

    def test_empty_marks_yields_empty_words_with_tokens(self):
        t = audio.build_timings("Hola mundo", [])
        self.assertEqual(t["words"], [])
        self.assertEqual(t["tokens"], ["Hola", "mundo"])

    def test_synthesize_story_combines_audio_and_timings(self):
        client = _FakePolly(_simulate_polly_marks(_ACCENT_STORY))
        out = audio.synthesize_story(_ACCENT_STORY, client=client)
        self.assertEqual(out["audio"], b"ID3\x03fake-mp3")
        self.assertTrue(out["timings"]["words"])
        self.assertEqual(out["voice"], "Mia")


class PurgeStaleTests(TestCase):
    """D-56: retention is enforced, not indefinite."""

    def _backdate(self, event, days):
        from datetime import timedelta

        from django.utils import timezone
        # auto_now_add blocks a create kwarg, so update() past the window.
        AuditEvent.objects.filter(pk=event.pk).update(
            ts=timezone.now() - timedelta(days=days)
        )

    def test_purges_past_retention_keeps_recent(self):
        from io import StringIO

        from django.core.management import call_command

        recent = AuditEvent.record("data.exported", summary="recent")
        old = AuditEvent.record("data.exported", summary="old")
        self._backdate(old, 1000)
        call_command("purge_stale", stdout=StringIO())
        self.assertFalse(AuditEvent.objects.filter(pk=old.pk).exists())
        self.assertTrue(AuditEvent.objects.filter(pk=recent.pk).exists())

    def test_dry_run_purges_nothing(self):
        from io import StringIO

        from django.core.management import call_command

        old = AuditEvent.record("data.exported")
        self._backdate(old, 1000)
        call_command("purge_stale", "--dry-run", stdout=StringIO())
        self.assertTrue(AuditEvent.objects.filter(pk=old.pk).exists())
