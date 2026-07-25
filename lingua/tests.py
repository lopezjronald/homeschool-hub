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
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import models as dj_models
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from students.models import Student

from django.core.files.storage import InMemoryStorage, storages

from . import advancement, assets, audio, cognates, comprehension, leveling, profiles, services
from . import storage as lingua_storage
from .integrations import directory
from .models import (
    AuditEvent, ComprehensionCheck, KnownWord, Learner, LearnerProfile, MilestoneAward,
    ReadingSession, Story, StoryAudio, Theme,
)
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

    def test_token_flags_aligns_to_tokens(self):
        flags = cognates.token_flags(["El", "animal", "está", "librería.", "..."])
        self.assertTrue(flags[1]["cognate"])                       # animal
        self.assertIsNone(flags[1]["false_friend"])
        self.assertEqual(flags[3]["false_friend"], ("library", "bookstore"))  # librería.
        self.assertFalse(flags[3]["cognate"])                     # false friend ≠ cognate
        self.assertFalse(flags[0]["cognate"])                     # El
        self.assertIsNone(flags[4]["false_friend"])              # punctuation-only token


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


class ContentHashTests(TestCase):
    """LGA-37 / N-04: content-addressed keys — an edit busts the cache."""

    def _h(self, text, provider="polly", voice="Mia", engine="neural"):
        return assets.content_hash(text, provider=provider, voice=voice, engine=engine)

    def test_stable_and_sensitive(self):
        base = self._h("Hola")
        self.assertEqual(base, self._h("Hola"))                       # deterministic
        self.assertNotEqual(base, self._h("Hola."))                   # text edit
        self.assertNotEqual(base, self._h("Hola", voice="Lupe"))      # voice
        self.assertNotEqual(base, self._h("Hola", engine="standard"))  # engine
        self.assertNotEqual(base, self._h("Hola", provider="edge"))   # provider

    def test_whitespace_change_busts_cache(self):
        # whitespace shifts char offsets → timings would mis-align → must be a new key
        self.assertNotEqual(self._h("un gato"), self._h("un  gato"))

    def test_separator_prevents_field_collision(self):
        # ("ab","c") must not hash the same as ("a","bc")
        self.assertNotEqual(
            assets.content_hash("t", provider="ab", voice="c", engine="e"),
            assets.content_hash("t", provider="a", voice="bc", engine="e"),
        )

    def test_asset_keys_derive_from_hash(self):
        keys = assets.asset_keys("deadbeef")
        self.assertEqual(keys["audio"], "lingua/readalong/deadbeef.mp3")
        self.assertEqual(keys["timings"], "lingua/readalong/deadbeef.json")


class StoryAudioModelTests(TestCase):
    """LGA-37: StoryAudio staleness detection, uniqueness, cascade."""

    @classmethod
    def setUpTestData(cls):
        cls.story = Story.objects.create(title="El gato", body="Hay un gato.", level="L1")

    def _bake(self, story=None, voice="Mia", engine="neural", provider="polly"):
        story = story or self.story
        digest = story.audio_hash(voice, engine, provider=provider)
        return StoryAudio.objects.create(
            story=story, voice=voice, engine=engine, provider=provider,
            content_hash=digest, audio_key=assets.asset_keys(digest)["audio"],
            timings={"words": []},
        )

    def test_audio_hash_matches_assets_module(self):
        self.assertEqual(
            self.story.audio_hash("Mia", "neural"),
            assets.content_hash(self.story.body, provider="polly", voice="Mia", engine="neural"),
        )

    def test_is_current_true_then_stale_after_text_edit(self):
        sa = self._bake()
        self.assertTrue(sa.is_current)
        self.story.body = "Hay dos gatos."
        self.story.save(update_fields=["body"])
        sa = StoryAudio.objects.get(pk=sa.pk)  # fresh fetch (story text changed)
        self.assertFalse(sa.is_current)

    def test_current_audio_fresh_missing_and_stale(self):
        self.assertIsNone(self.story.current_audio("Mia", "neural"))   # missing
        sa = self._bake()
        self.assertEqual(self.story.current_audio("Mia", "neural"), sa)  # fresh
        self.story.body = "Otro texto distinto."
        self.story.save(update_fields=["body"])
        self.assertIsNone(self.story.current_audio("Mia", "neural"))   # stale → None

    def test_unique_per_story_voice_engine_provider(self):
        from django.db import IntegrityError, transaction
        self._bake()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._bake()  # same (story, voice, engine, provider)

    def test_same_story_different_voice_coexists(self):
        self._bake(voice="Mia")
        self._bake(voice="Lupe")
        self.assertEqual(self.story.audios.count(), 2)

    def test_same_voice_different_provider_coexists(self):
        # provider is part of the identity, so a future edge-tts asset can sit
        # alongside the Polly one for the same (story, voice, engine).
        self._bake(provider="polly")
        self._bake(provider="edge")
        self.assertEqual(self.story.audios.count(), 2)

    def test_cascade_delete_with_story(self):
        s = Story.objects.create(title="x", body="y", level="L1")
        self._bake(story=s)
        sid = s.pk  # capture BEFORE delete — s.delete() sets s.pk = None
        self.assertTrue(StoryAudio.objects.filter(story_id=sid).exists())
        s.delete()
        self.assertFalse(StoryAudio.objects.filter(story_id=sid).exists())


_INMEM_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    "lingua_readalong": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
        "OPTIONS": {"base_url": "https://cdn.test/"},
    },
}


class ReadalongStorageTests(TestCase):
    """LGA-36 / N-03: public, immutably-cached read-along asset path."""

    def test_cache_control_is_public_immutable_long(self):
        self.assertEqual(lingua_storage.IMMUTABLE_CACHE_CONTROL,
                         "public, max-age=31536000, immutable")

    def test_alias_configured_and_distinct_from_default(self):
        from django.conf import settings as dj_settings
        self.assertIn("lingua_readalong", dj_settings.STORAGES)
        # the public read-along path is a SEPARATE entry from the private-media default
        self.assertIsNot(dj_settings.STORAGES["lingua_readalong"],
                         dj_settings.STORAGES["default"])

    @override_settings(STORAGES=_INMEM_STORAGES)
    def test_save_audio_stable_url_and_skips_reupload(self):
        key = "lingua/readalong/abc123.mp3"
        url1 = lingua_storage.save_audio(key, b"first-bytes")
        self.assertEqual(url1, "https://cdn.test/lingua/readalong/abc123.mp3")
        # content-addressed: a second save of the SAME key must be a no-op (skip),
        # NOT overwrite or write a suffixed duplicate. Feed different bytes to prove
        # the guard: the original survives and no second object is created.
        url2 = lingua_storage.save_audio(key, b"DIFFERENT-bytes")
        self.assertEqual(url1, url2)  # stable URL
        store = lingua_storage.readalong_storage()
        with store.open(key) as fh:
            self.assertEqual(fh.read(), b"first-bytes")  # original untouched
        _dirs, files = store.listdir("lingua/readalong")
        self.assertEqual(len(files), 1)  # no suffixed duplicate written
        self.assertEqual(lingua_storage.public_url(key), url1)

    @override_settings(STORAGES=_INMEM_STORAGES)
    def test_readalong_storage_resolves_the_alias(self):
        self.assertIsInstance(lingua_storage.readalong_storage(), InMemoryStorage)

    def test_public_capable_guard(self):
        from types import SimpleNamespace
        cap = lingua_storage._public_capable
        # unsigned backend with no custom_domain would 403 → not capable
        self.assertFalse(cap(SimpleNamespace(querystring_auth=False, custom_domain=None)))
        # unsigned + a public domain → capable
        self.assertTrue(cap(SimpleNamespace(querystring_auth=False, custom_domain="cdn.example")))
        # signed backend (default media) → capable
        self.assertTrue(cap(SimpleNamespace(querystring_auth=True, custom_domain=None)))
        # non-S3 backend (no querystring_auth attr, e.g. filesystem) → capable
        self.assertTrue(cap(InMemoryStorage()))

    def test_falls_back_to_default_when_alias_missing(self):
        no_alias = {
            "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
        }
        with override_settings(STORAGES=no_alias):
            self.assertIs(lingua_storage.readalong_storage(), storages["default"])


@override_settings(STORAGES=_INMEM_STORAGES)
class TtsBuildCommandTests(TestCase):
    """LGA-38: tts_build bakes/links StoryAudio rows; idempotent; --link-only skips Polly."""

    @classmethod
    def setUpTestData(cls):
        cls.story = Story.objects.create(
            title="El gato", body="Hay un gato pequeño en la casa.",
            level="L1", status=Story.APPROVED,
        )

    def _run(self, *args, polly=True, **kwargs):
        from django.core.management import call_command
        out, err = io.StringIO(), io.StringIO()
        ctx = (mock.patch("lingua.audio._polly_client",
                          return_value=_FakePolly(_simulate_polly_marks(self.story.body)))
               if polly else mock.patch("lingua.audio._polly_client",
                                        side_effect=AssertionError("Polly must not be called")))
        with ctx:
            call_command("tts_build", *args, stdout=out, stderr=err, **kwargs)
        return out.getvalue(), err.getvalue()

    def test_bake_creates_row_and_uploads_assets(self):
        out, _ = self._run(str(self.story.pk))
        sa = self.story.current_audio("Mia", "neural")
        self.assertIsNotNone(sa)
        self.assertTrue(sa.timings["words"])
        self.assertEqual(sa.audio_key, assets.asset_keys(sa.content_hash)["audio"])
        self.assertIn("[baked]", out)  # per-story action tag, not the summary's "N baked"
        store = lingua_storage.readalong_storage()
        self.assertTrue(store.exists(assets.asset_keys(sa.content_hash)["audio"]))
        self.assertTrue(store.exists(assets.asset_keys(sa.content_hash)["timings"]))

    def test_bake_is_idempotent(self):
        self._run(str(self.story.pk))
        # 2nd pass must SKIP: polly=False makes any re-synthesis blow up, and the
        # bracketed tag (not the summary's "N skipped") proves the skip path ran.
        out, _ = self._run(str(self.story.pk), polly=False)
        self.assertIn("[skipped]", out)
        self.assertEqual(self.story.audios.count(), 1)

    def test_force_rebakes_in_place(self):
        self._run(str(self.story.pk))
        out, _ = self._run(str(self.story.pk), "--force")
        self.assertIn("[baked]", out)  # action tag: fails if --force is ignored (would be [skipped])
        self.assertEqual(self.story.audios.count(), 1)  # update_or_create, not a dupe

    def test_link_only_rebuilds_without_polly(self):
        self._run(str(self.story.pk))              # full bake uploads mp3 + timings
        self.story.audios.all().delete()           # simulate a fresh prod DB
        # --link-only must NOT call Polly (patched to blow up if it does)
        out, _ = self._run(str(self.story.pk), "--link-only", polly=False)
        self.assertIn("[linked]", out)
        sa = self.story.current_audio("Mia", "neural")
        self.assertIsNotNone(sa)                    # link path succeeded (Polly never called)
        self.assertTrue(sa.timings["words"])       # rebuilt from the stored timings

    def test_link_only_without_assets_fails_gracefully(self):
        # A never-baked story (unique body -> unique hash -> no timings in the store)
        # must fail cleanly on --link-only, not crash. (Unique body avoids the
        # in-memory store leaking a prior test's assets across methods.)
        from django.core.management import call_command
        s = Story.objects.create(title="Nunca", body="Texto jamás sintetizado todavía.",
                                 level="L1", status=Story.APPROVED)
        out, err = io.StringIO(), io.StringIO()
        call_command("tts_build", str(s.pk), "--link-only", stdout=out, stderr=err)
        # the per-story stderr line "story N failed:" (colon) is discriminating —
        # the summary's "0 failed." (period) would match a bare "failed" tautologically.
        self.assertIn("failed:", err.getvalue())
        self.assertIsNone(s.current_audio("Mia", "neural"))

    def test_digits_in_body_warn(self):
        s = Story.objects.create(title="Números", body="Hay 5 gatos.",
                                 level="L1", status=Story.APPROVED)
        from django.core.management import call_command
        err = io.StringIO()
        with mock.patch("lingua.audio._polly_client",
                        return_value=_FakePolly(_simulate_polly_marks(s.body))):
            call_command("tts_build", str(s.pk), stdout=io.StringIO(), stderr=err)
        self.assertIn("digits", err.getvalue())

    def test_all_approved_targets_only_approved(self):
        draft = Story.objects.create(title="Draft", body="Un perro corre.",
                                     level="L1", status=Story.DRAFT)
        self._run("--all-approved")
        self.assertIsNotNone(self.story.current_audio("Mia", "neural"))
        self.assertIsNone(draft.current_audio("Mia", "neural"))

    def test_no_target_raises(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command("tts_build", stdout=io.StringIO())


class ReaderViewTests(TestCase):
    """LGA-47 / LGA-54: read-along reader page + graceful degradation."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("reader_parent", password="pw")
        cls.story = Story.objects.create(
            title="El gato", body="Hay un gato feliz.", level="L1", status=Story.APPROVED,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def _url(self, story):
        return reverse("lingua:read", args=[story.pk])

    def _add_audio(self, story):
        digest = story.audio_hash("Mia", "neural")
        return StoryAudio.objects.create(
            story=story, voice="Mia", engine="neural", provider="polly",
            content_hash=digest, audio_key=assets.asset_keys(digest)["audio"],
            timings={
                "tokens": ["Hay", "un", "gato", "feliz."],
                "token_spans": [[0, 3], [4, 6], [7, 11], [12, 18]],
                "words": [{"i": 0, "s_ms": 0, "e_ms": 300, "cs": 0, "ce": 3},
                          {"i": 2, "s_ms": 300, "e_ms": 600, "cs": 7, "ce": 11}],
            },
            duration_ms=600,
        )

    def test_requires_login(self):
        self.client.logout()
        self.assertIn(self.client.get(self._url(self.story)).status_code, (301, 302))

    def test_only_approved_is_servable(self):
        draft = Story.objects.create(title="d", body="x y", level="L1", status=Story.DRAFT)
        self.assertEqual(self.client.get(self._url(draft)).status_code, 404)  # D-49

    def test_degrades_to_text_without_audio(self):
        html = self.client.get(self._url(self.story)).content.decode()
        self.assertNotIn("<audio", html)                 # no player element
        self.assertNotIn("lingua-timings", html)         # no timing block (hash-stable marker)
        self.assertNotIn("<script", html)                # no player script emitted at all
        self.assertIn('data-i="0"', html)                # words still rendered as spans
        self.assertIn("Audio is being prepared", html)   # degradation note (LGA-54)

    @override_settings(STORAGES=_INMEM_STORAGES)
    def test_renders_player_with_audio(self):
        self._add_audio(self.story)
        html = self.client.get(self._url(self.story)).content.decode()
        self.assertIn("<audio", html)
        self.assertIn('id="lingua-timings"', html)       # json_script data block (not static-hashed)
        self.assertIn("readalong", html)                 # player script (matches hashed name too)
        self.assertIn('data-i="0"', html)

    def test_degrades_when_public_url_raises(self):
        # A present StoryAudio whose public_url() blows up must still render text,
        # not 500 — the reading loop never hard-depends on the asset store (LGA-54).
        self._add_audio(self.story)
        with mock.patch("lingua.storage.public_url", side_effect=RuntimeError("R2 down")):
            r = self.client.get(self._url(self.story))
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        self.assertNotIn("<audio", html)
        self.assertIn("Audio is being prepared", html)

    @override_settings(STORAGES=_INMEM_STORAGES)
    def test_csp_widened_to_audio_host(self):
        self._add_audio(self.story)                       # InMem base_url is https://cdn.test/
        csp = self.client.get(self._url(self.story)).headers.get("Content-Security-Policy", "")
        self.assertIn("media-src", csp)
        self.assertIn("cdn.test", csp)                   # widened to the cross-origin R2 host

    def test_csp_is_strict(self):
        csp = self.client.get(self._url(self.story)).headers.get("Content-Security-Policy", "")
        self.assertIn("default-src", csp)
        self.assertNotIn("unsafe-inline", csp)           # strict kid-page policy (D-13)

    def test_reader_disables_browser_translation(self):
        # The whole point is to READ Spanish — Chrome must not auto-translate it.
        html = self.client.get(self._url(self.story)).content.decode()
        self.assertIn('translate="no"', html)
        self.assertIn("notranslate", html)

    def test_multiparagraph_story_renders_separate_paragraphs(self):
        s = Story.objects.create(title="P", body="Primero uno.\n\nSegundo dos.",
                                 level="L1", status=Story.APPROVED)
        html = self.client.get(self._url(s)).content.decode()
        self.assertEqual(html.count('<p class="story">'), 2)   # not a run-on wall

    def test_audio_row_without_tokens_degrades_to_text(self):
        # A StoryAudio with words but no tokens (hand-edited/corrupt) must degrade to
        # readable text, not render an empty story under a player.
        s = Story.objects.create(title="T", body="Hola mundo", level="L1", status=Story.APPROVED)
        StoryAudio.objects.create(
            story=s, voice="Mia", engine="neural", provider="polly",
            content_hash=s.audio_hash("Mia", "neural"), audio_key="k",
            timings={"words": [{"i": 0, "s_ms": 0, "e_ms": 100}]}, duration_ms=100)
        html = self.client.get(self._url(s)).content.decode()
        self.assertNotIn("<audio", html)        # no player
        self.assertIn('data-i="0"', html)       # body text still shown
        self.assertIn("Hola", html)

    def test_cognate_and_false_friend_treatments(self):
        s = Story.objects.create(title="Biblioteca", body="El animal está en la librería.",
                                 level="L1", status=Story.APPROVED)
        html = self.client.get(self._url(s)).content.decode()
        # Assert the WORD-SPAN treatment (class "w cognate"/"w false-friend"), NOT the
        # legend chips ("chip cognate"/"chip false-friend") which would match a bare
        # "cognate"/"false-friend" substring even if the span treatment were removed.
        self.assertIn('class="w cognate"', html)        # "animal" span treated
        self.assertIn('class="w false-friend"', html)   # "librería" span flagged
        self.assertIn("significa", html)                # false-friend warning (title text)
        self.assertIn("bookstore", html)                # the true meaning surfaced
        self.assertIn("cognado", html)                  # legend shown when flags exist

    def test_no_legend_without_flags(self):
        # a plain story (no cognates/false-friends) shows no legend
        html = self.client.get(self._url(self.story)).content.decode()
        self.assertNotIn("cognado", html)


class ReadingMetricTests(TestCase):
    """LGA-53 / D-60-61: reading-volume + known-words hero metric."""

    @classmethod
    def setUpTestData(cls):
        cls.learner = Learner.create_for_host_student(501, profiles.KIDS_EARLY)
        cls.s1 = Story.objects.create(title="A", body="uno dos tres", level="L1")  # 3 words
        cls.s2 = Story.objects.create(title="B", body="cuatro cinco", level="L1")  # 2 words

    def test_record_reading_counts_words_and_time(self):
        sess = services.record_reading(self.learner, self.s1, seconds=90)
        self.assertEqual(sess.words, 3)
        self.assertEqual(sess.seconds, 90)
        self.assertEqual(sess.learner, self.learner)

    def test_reading_totals_aggregate(self):
        services.record_reading(self.learner, self.s1, seconds=90)  # 3 words
        services.record_reading(self.learner, self.s2, seconds=30)  # 2 words
        services.record_reading(self.learner, self.s1, seconds=60)  # reread s1, +3
        t = services.reading_totals(self.learner)
        self.assertEqual(t["words_read"], 8)   # 3 + 2 + 3
        self.assertEqual(t["minutes"], 3)      # (90+30+60)/60
        self.assertEqual(t["stories"], 2)      # distinct s1, s2 (reread not double-counted)
        self.assertEqual(t["known_words"], 0)

    def test_credit_known_word_dedups_and_normalizes(self):
        _, c1 = services.credit_known_word(self.learner, "Gato")
        _, c2 = services.credit_known_word(self.learner, "gato")    # same normalized form
        _, c3 = services.credit_known_word(self.learner, "gató")    # diacritic-stripped → gato
        _, c4 = services.credit_known_word(self.learner, "¡Gato!")  # punctuation stripped → gato
        self.assertTrue(c1)
        self.assertFalse(c2)
        self.assertFalse(c3)
        self.assertFalse(c4)
        self.assertEqual(self.learner.known_words.count(), 1)  # all four collapse to one
        for junk in ("   ", "!!!", "123", "..."):              # blank / punctuation / digits
            obj, created = services.credit_known_word(self.learner, junk)
            self.assertIsNone(obj, junk)
            self.assertFalse(created, junk)
        self.assertEqual(self.learner.known_words.count(), 1)  # no junk stored
        self.assertEqual(services.reading_totals(self.learner)["known_words"], 1)

    def test_overlong_known_word_is_capped(self):
        obj, _ = services.credit_known_word(self.learner, "a" * 200)
        self.assertLessEqual(len(obj.word), 64)  # capped to the field width (no DataError)

    def test_seconds_clamped_nonnegative(self):
        self.assertEqual(services.record_reading(self.learner, self.s1, seconds=-5).seconds, 0)

    def test_seconds_clamped_to_one_day(self):
        # a hostile/garbage huge value must not overflow int4 on Postgres → 500
        self.assertEqual(services.record_reading(self.learner, self.s1, seconds=9_999_999_999).seconds, 86_400)

    def test_cascade_delete_learner(self):
        services.record_reading(self.learner, self.s1)
        services.credit_known_word(self.learner, "gato")
        lid = self.learner.pk  # capture BEFORE delete
        self.learner.delete()
        self.assertFalse(ReadingSession.objects.filter(learner_id=lid).exists())
        self.assertFalse(KnownWord.objects.filter(learner_id=lid).exists())

    def test_story_delete_preserves_session_history(self):
        sess = services.record_reading(self.learner, self.s1, seconds=60)
        sid = sess.pk
        self.s1.delete()  # SET_NULL — you don't un-read a story
        sess = ReadingSession.objects.get(pk=sid)  # still exists
        self.assertIsNone(sess.story)
        self.assertEqual(sess.words, 3)  # words already read are retained

    def test_credit_known_word_unique_constraint(self):
        from django.db import IntegrityError, transaction
        KnownWord.objects.create(learner=self.learner, word="perro")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                KnownWord.objects.create(learner=self.learner, word="perro")


class RereadSchedulerTests(TestCase):
    """LGA-66 / N-01: reread-first scheduler — per-story cap + least-recently rotation."""

    @classmethod
    def setUpTestData(cls):
        cls.learner = Learner.create_for_host_student(601, profiles.KIDS_EARLY)
        cls.s1 = Story.objects.create(title="s1", body="uno dos", level="L1", status=Story.APPROVED)
        cls.s2 = Story.objects.create(title="s2", body="tres cuatro", level="L1", status=Story.APPROVED)

    def _read(self, story, days_ago=0):
        sess = services.record_reading(self.learner, story)
        if days_ago:
            from datetime import timedelta

            from django.utils import timezone
            # auto_now_add blocks a create kwarg, so backdate via update()
            ReadingSession.objects.filter(pk=sess.pk).update(
                created_at=timezone.now() - timedelta(days=days_ago))
        return sess

    def test_none_when_no_reads(self):
        self.assertIsNone(services.pick_reread(self.learner))

    def test_returns_previously_read(self):
        self._read(self.s1)
        self.assertEqual(services.pick_reread(self.learner), self.s1)

    def test_respects_cap(self):
        for _ in range(3):
            self._read(self.s1)                                   # 3 reads
        self.assertIsNone(services.pick_reread(self.learner, cap=3))       # at cap
        self.assertEqual(services.pick_reread(self.learner, cap=4), self.s1)  # room again

    def test_rotation_picks_least_recently_read(self):
        self._read(self.s1, days_ago=1)                          # read yesterday
        self._read(self.s2, days_ago=5)                          # read 5 days ago (older)
        self.assertEqual(services.pick_reread(self.learner), self.s2)  # least-recent first

    def test_exclude(self):
        self._read(self.s1, days_ago=0)
        self._read(self.s2, days_ago=2)                          # older → picked first...
        self.assertEqual(                                        # ...unless excluded
            services.pick_reread(self.learner, exclude_story_ids=[self.s2.pk]), self.s1)

    def test_only_approved_resurfaced(self):
        self._read(self.s1)
        self.s1.status = Story.DRAFT
        self.s1.save(update_fields=["status"])
        self.assertIsNone(services.pick_reread(self.learner))

    def test_deleted_story_not_resurfaced(self):
        self._read(self.s1)
        self.s1.delete()                                         # SET_NULL → story is None
        self.assertIsNone(services.pick_reread(self.learner))


class DailyPlanTests(TestCase):
    """LGA-65 / F-06 / D-66 / N-01: daily plan — hard cap, reread-first, ceiling, choice."""

    def _learner(self, hsid, ceiling="L2", support=None):
        overrides = {"content_ceiling": ceiling}
        if support:
            overrides["support_level"] = support
        return Learner.create_for_host_student(hsid, profiles.KIDS_EARLY, **overrides)

    def _story(self, title, level="L2", words=40, theme=None, status=Story.APPROVED):
        return Story.objects.create(
            title=title, body=" ".join(["x"] * words), level=level, status=status, theme=theme)

    def test_session_cap_is_a_hard_limit(self):
        # PARENT_MEDIATED cap = 10 min. Two 400-word stories = 10 min each @ 40 wpm.
        learner = self._learner(701, ceiling="L2")
        a = self._story("A", words=400)
        self._story("B", words=400)
        services.record_reading(learner, a)          # A becomes the reread
        plan = services.build_daily_plan(learner)
        self.assertEqual(plan["cap_minutes"], 10)
        self.assertEqual(plan["estimated_minutes"], 10)   # NOT 20 — harder content ≠ more time
        self.assertEqual(len(plan["items"]), 1)           # only the reread fits; new excluded
        self.assertEqual(plan["items"][0]["kind"], "reread")

    def test_short_stories_both_fit_under_cap(self):
        learner = self._learner(702, ceiling="L2")
        a = self._story("A", words=40)               # 1 min each
        self._story("B", words=40)
        services.record_reading(learner, a)
        plan = services.build_daily_plan(learner)
        self.assertEqual([i["kind"] for i in plan["items"]], ["reread", "new"])
        self.assertEqual(plan["estimated_minutes"], 2)

    def test_reread_first_when_due(self):
        learner = self._learner(703, ceiling="L2")
        old = self._story("old", words=40)
        self._story("fresh", words=40)
        services.record_reading(learner, old)
        plan = services.build_daily_plan(learner)
        self.assertEqual(plan["items"][0]["kind"], "reread")
        self.assertEqual(plan["items"][0]["story"], old)

    def test_new_story_respects_ceiling(self):
        learner = self._learner(704, ceiling="L2")
        too_hard = self._story("too-hard", level="L3", words=40)   # above ceiling
        at = self._story("at-ceiling", level="L2", words=40)
        plan = services.build_daily_plan(learner)
        served = [i["story"] for i in plan["items"]] + plan["choices"]
        self.assertIn(at, served)
        self.assertNotIn(too_hard, served)          # above the ceiling is never served

    def test_bounded_choice_at_most_three(self):
        learner = self._learner(705, ceiling="L2")
        for i in range(6):
            self._story(f"s{i}", level="L1", words=40)
        plan = services.build_daily_plan(learner)
        self.assertLessEqual(len(plan["choices"]), 3)
        self.assertTrue(all(s.status == Story.APPROVED for s in plan["choices"]))
        picked = {i["story"].pk for i in plan["items"]}
        self.assertFalse(picked & {s.pk for s in plan["choices"]})  # no overlap with items

    def test_empty_plan_when_no_content(self):
        plan = services.build_daily_plan(self._learner(706, ceiling="L2"))
        self.assertEqual(plan["items"], [])
        self.assertEqual(plan["choices"], [])

    def test_engaged_learner_not_dead_ended(self):
        # Read the only story past the reread cap: the plan must still offer a reread
        # (fallback), never an empty plan + false "no stories yet" message.
        learner = self._learner(709, ceiling="L1")
        s = self._story("only", level="L1", words=40)
        for _ in range(5):                       # well past pick_reread's cap of 3
            services.record_reading(learner, s)
        plan = services.build_daily_plan(learner)
        self.assertEqual(len(plan["items"]), 1)
        self.assertEqual(plan["items"][0]["kind"], "reread")
        self.assertEqual(plan["items"][0]["story"], s)

    def test_oversized_first_story_is_still_offered(self):
        # A lone story longer than the cap must still be offered — the cap governs how
        # MANY items, never whether the child gets one (never an empty session, D-66).
        learner = self._learner(708, ceiling="L2")
        big = self._story("big", words=800)   # 20 min > 10-min cap, and no reread exists
        plan = services.build_daily_plan(learner)
        self.assertEqual(len(plan["items"]), 1)
        self.assertEqual(plan["items"][0]["story"], big)
        self.assertEqual(plan["estimated_minutes"], 20)   # the single item, even over cap

    def test_story_minutes_prefers_audio_duration(self):
        s = self._story("with-audio", words=4000)   # word-based = 100 min
        StoryAudio.objects.create(
            story=s, voice="Mia", engine="neural", provider="polly",
            content_hash="h", audio_key="k", timings={}, duration_ms=120000)
        self.assertEqual(services._story_minutes(s), 2)  # 120000ms → 2 min, not 100

    def test_narrow_reading_prefers_reread_theme(self):
        t = Theme.objects.create(slug="t", name="T", age_band=profiles.KIDS_EARLY)
        learner = self._learner(707, ceiling="L2")
        old = self._story("old", words=40, theme=t)
        same = self._story("same-theme", words=40, theme=t)
        self._story("other", words=40, theme=None)   # newer, no theme
        services.record_reading(learner, old)
        plan = services.build_daily_plan(learner)
        new_item = next(i for i in plan["items"] if i["kind"] == "new")
        self.assertEqual(new_item["story"], same)    # same theme as the reread (continuity)


class AdvancementTests(TestCase):
    """LGA-67 / D-64 / D-67: transparent advancement rule + parent 'testing above' nudge."""

    @classmethod
    def setUpTestData(cls):
        cls.story = Story.objects.create(title="s", body="El gato.", level="L1", status=Story.APPROVED)

    def _learner(self, hsid, ceiling="L1"):
        return Learner.create_for_host_student(hsid, profiles.KIDS_EARLY, content_ceiling=ceiling)

    def _check(self, learner, result, days_ago=0):
        c = services.record_comprehension(learner, self.story, comprehension.PICTURE_MATCH, result=result)
        if days_ago:
            from datetime import timedelta

            from django.utils import timezone
            ComprehensionCheck.objects.filter(pk=c.pk).update(
                created_at=timezone.now() - timedelta(days=days_ago))
        return c

    # --- pure evaluate: the threshold matrix (DB-free) ---
    def test_evaluate_promote(self):
        recent = [comprehension.PROFICIENT] * 4 + [comprehension.BEGINNING]
        self.assertEqual(
            advancement.evaluate(recent, n_graded=5, weeks_active=3, level_rank=0, top_rank=7),
            advancement.PROMOTE)

    def test_evaluate_holds_when_too_few_hits(self):
        recent = [comprehension.PROFICIENT] * 3 + [comprehension.BEGINNING] * 2
        self.assertEqual(
            advancement.evaluate(recent, n_graded=5, weeks_active=3, level_rank=0, top_rank=7),
            advancement.HOLD)

    def test_evaluate_holds_before_two_weeks(self):
        recent = [comprehension.STRONG] * 5
        self.assertEqual(
            advancement.evaluate(recent, n_graded=5, weeks_active=1, level_rank=0, top_rank=7),
            advancement.HOLD)

    def test_evaluate_no_promote_at_top(self):
        recent = [comprehension.STRONG] * 5
        self.assertEqual(
            advancement.evaluate(recent, n_graded=5, weeks_active=4, level_rank=7, top_rank=7),
            advancement.HOLD)

    def test_evaluate_demote_on_three_beginning(self):
        recent = [comprehension.BEGINNING] * 3 + [comprehension.DEVELOPING]
        self.assertEqual(
            advancement.evaluate(recent, n_graded=4, weeks_active=4, level_rank=3, top_rank=7),
            advancement.DEMOTE)

    def test_evaluate_no_demote_at_floor_or_short_streak(self):
        self.assertEqual(  # at floor
            advancement.evaluate([comprehension.BEGINNING] * 3, n_graded=3, weeks_active=4, level_rank=0, top_rank=7),
            advancement.HOLD)
        self.assertEqual(  # only 2 in a row
            advancement.evaluate([comprehension.BEGINNING, comprehension.BEGINNING, comprehension.PROFICIENT],
                                 n_graded=3, weeks_active=4, level_rank=3, top_rank=7),
            advancement.HOLD)

    def test_evaluate_deadband_holds(self):
        recent = [comprehension.PROFICIENT, comprehension.PROFICIENT, comprehension.BEGINNING,
                  comprehension.BEGINNING, comprehension.DEVELOPING]
        self.assertEqual(
            advancement.evaluate(recent, n_graded=5, weeks_active=4, level_rank=3, top_rank=7),
            advancement.HOLD)

    # --- service: gathers signals + proposes a level ---
    def test_recommendation_promote_to_next_level(self):
        l = self._learner(1001, ceiling="L1")
        self._check(l, comprehension.PROFICIENT, days_ago=20)       # oldest → >2 weeks
        for _ in range(3):
            self._check(l, comprehension.PROFICIENT, days_ago=1)
        self._check(l, comprehension.BEGINNING)                     # 5 total, 4 proficient
        rec = services.advancement_recommendation(l)
        self.assertEqual(rec["action"], "promote")
        self.assertEqual((rec["from_level"], rec["to_level"]), ("L1", "L2"))

    def test_recommendation_hold_when_new(self):
        l = self._learner(1006, ceiling="L1")
        for _ in range(5):
            self._check(l, comprehension.PROFICIENT)                # all today → <2 weeks
        self.assertEqual(services.advancement_recommendation(l)["action"], "hold")

    def test_apply_advancement_sets_ceiling_and_audits(self):
        l = self._learner(1002, ceiling="L1")
        services.apply_advancement(l, "L2", host_user_id=7)
        l.profile.refresh_from_db()
        self.assertEqual(l.profile.content_ceiling, "L2")
        self.assertTrue(AuditEvent.objects.filter(action="learner.advanced", target_id=l.pk).exists())

    def test_apply_advancement_rejects_bad_level(self):
        with self.assertRaises(ValueError):
            services.apply_advancement(self._learner(1003), "L99", host_user_id=7)

    def test_nudge_fires_on_consistent_strong_then_debounces(self):
        l = self._learner(1004, ceiling="L1")
        for _ in range(5):
            self._check(l, comprehension.STRONG)
        self.assertTrue(services.nudge_testing_above_defaults(l))    # consistently strong
        services.mark_nudge_shown(l)
        self.assertFalse(services.nudge_testing_above_defaults(l))   # just shown → debounced
        for _ in range(5):
            services.record_reading(l, self.story)                  # 5 more sessions
        self.assertTrue(services.nudge_testing_above_defaults(l))    # debounce elapsed

    def test_no_nudge_unless_all_strong(self):
        l = self._learner(1005, ceiling="L1")
        for _ in range(4):
            self._check(l, comprehension.STRONG)
        self._check(l, comprehension.PROFICIENT)                    # not all strong
        self.assertFalse(services.nudge_testing_above_defaults(l))


class ComprehensionTests(TestCase):
    """LGA-52 / F-01: after-reading comprehension checks → signals for advancement."""

    @classmethod
    def setUpTestData(cls):
        cls.learner = Learner.create_for_host_student(901, profiles.KIDS_EARLY)
        cls.story = Story.objects.create(title="s", body="El gato.", level="L1", status=Story.APPROVED)

    def test_check_kind_varies_by_band(self):
        self.assertEqual(comprehension.check_kind_for(profiles.KIDS_EARLY), comprehension.PICTURE_MATCH)
        self.assertEqual(comprehension.check_kind_for(profiles.KIDS_OLDER), comprehension.RETELL)
        self.assertEqual(comprehension.check_kind_for(profiles.TEEN), comprehension.SHORT_ANSWER)
        self.assertEqual(comprehension.check_kind_for(profiles.ADULT), comprehension.SHORT_ANSWER)

    def test_scale_helpers(self):
        self.assertTrue(comprehension.meets_bar(comprehension.PROFICIENT))
        self.assertTrue(comprehension.meets_bar(comprehension.STRONG))
        self.assertFalse(comprehension.meets_bar(comprehension.DEVELOPING))
        self.assertFalse(comprehension.is_signal(comprehension.PENDING))
        self.assertTrue(comprehension.is_signal(comprehension.BEGINNING))

    def test_recognition_autogrades_open_is_pending(self):
        auto = services.record_comprehension(
            self.learner, self.story, comprehension.PICTURE_MATCH, result=comprehension.PROFICIENT)
        self.assertEqual(auto.result, comprehension.PROFICIENT)     # recognition auto-graded
        openc = services.record_comprehension(self.learner, self.story, comprehension.RETELL)
        self.assertEqual(openc.result, comprehension.PENDING)       # open → awaits review

    def test_record_rejects_unknown_result(self):
        with self.assertRaises(ValueError):
            services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH, result="genius")

    def test_open_kind_ignores_result_and_awaits_review(self):
        # an open kind can NEVER skip parent review, even if a result is passed (D-53/F-01)
        c = services.record_comprehension(
            self.learner, self.story, comprehension.RETELL, result=comprehension.STRONG)
        self.assertEqual(c.result, comprehension.PENDING)
        self.assertIsNone(c.reviewed_by)

    def test_auto_graded_kind_requires_result(self):
        with self.assertRaises(ValueError):  # recognition must produce a grade
            services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH)

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            services.record_comprehension(self.learner, self.story, "essay", result=comprehension.STRONG)

    def test_field_default_is_pending(self):
        c = ComprehensionCheck.objects.create(learner=self.learner, kind=comprehension.RETELL)
        self.assertEqual(c.result, comprehension.PENDING)   # model/DB default

    def test_grade_open_check(self):
        c = services.record_comprehension(self.learner, self.story, comprehension.RETELL)
        services.grade_comprehension(c, comprehension.DEVELOPING, reviewed_by=7)
        c.refresh_from_db()
        self.assertEqual(c.result, comprehension.DEVELOPING)
        self.assertEqual(c.reviewed_by, 7)

    def test_recent_comprehension_is_the_advancement_window(self):
        # newest-first, graded-only (PENDING excluded), capped at n
        services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH, result=comprehension.BEGINNING)
        services.record_comprehension(self.learner, self.story, comprehension.RETELL)  # PENDING, excluded
        services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH, result=comprehension.PROFICIENT)
        recent = services.recent_comprehension(self.learner, n=5)
        self.assertEqual(recent, [comprehension.PROFICIENT, comprehension.BEGINNING])  # newest first, no PENDING

    def test_cascade_and_set_null(self):
        c = services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH, result=comprehension.STRONG)
        cid = c.pk
        self.story.delete()                                        # SET_NULL keeps the signal
        c.refresh_from_db()
        self.assertIsNone(c.story)
        self.assertEqual(c.result, comprehension.STRONG)
        self.learner.delete()                                      # CASCADE
        self.assertFalse(ComprehensionCheck.objects.filter(pk=cid).exists())


class MilestoneTests(TestCase):
    """LGA-68 / D-60-61: warm milestone celebrations — volume/known-words, no streaks."""

    @classmethod
    def setUpTestData(cls):
        cls.learner = Learner.create_for_host_student(801, profiles.KIDS_EARLY)

    def _read(self, words):
        s = Story.objects.create(title="s", body=" ".join(["x"] * words),
                                 level="L1", status=Story.APPROVED)
        services.record_reading(self.learner, s)

    def test_awards_words_milestone_on_crossing(self):
        self._read(120)
        awarded = services.award_milestones(self.learner)
        self.assertEqual([(a.kind, a.threshold) for a in awarded], [("words", 100)])

    def test_below_threshold_no_award(self):
        self._read(50)
        self.assertEqual(services.award_milestones(self.learner), [])

    def test_idempotent_no_reaward(self):
        self._read(120)
        services.award_milestones(self.learner)
        self.assertEqual(services.award_milestones(self.learner), [])   # nothing new
        self.assertEqual(self.learner.milestones.count(), 1)

    def test_crossing_multiple_at_once_most_significant_first(self):
        self._read(600)
        awarded = services.award_milestones(self.learner)
        self.assertEqual([a.threshold for a in awarded], [500, 100])    # sorted desc

    def test_known_words_milestone(self):
        # 10 DISTINCT words (digits are stripped by canonicalization, so "w0".."w9"
        # would collapse to one — use real distinct words).
        for w in ["uno", "dos", "tres", "cuatro", "cinco",
                  "seis", "siete", "ocho", "nueve", "diez"]:
            services.credit_known_word(self.learner, w)
        self.assertEqual(self.learner.known_words.count(), 10)
        awarded = services.award_milestones(self.learner)
        self.assertIn(("known", 10), [(a.kind, a.threshold) for a in awarded])

    def test_no_streak_or_accuracy_kind(self):
        # celebrations are volume/known only — never streaks/accuracy (D-61)
        self.assertEqual({k for k, _ in MilestoneAward.KIND_CHOICES}, {"words", "known"})

    def test_unique_per_learner_kind_threshold(self):
        from django.db import IntegrityError, transaction
        MilestoneAward.objects.create(learner=self.learner, kind="words", threshold=100)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MilestoneAward.objects.create(learner=self.learner, kind="words", threshold=100)


class KidPortalTests(TestCase):
    """E-08: tokenless kid portal — daily plan, reader, session logging, auto-provision."""

    @classmethod
    def setUpTestData(cls):
        from portal.tokens import make_portal_token
        cls.parent = User.objects.create_user("kp_parent", password="pw")
        cls.student = Student.objects.create(parent=cls.parent, first_name="Ana")
        cls.token = make_portal_token(cls.student)
        cls.story = Story.objects.create(
            title="El sol", body="El sol brilla.", level="L1", status=Story.APPROVED)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_plan_auto_provisions_learner_and_renders(self):
        self.assertFalse(Learner.objects.filter(host_student_id=self.student.pk).exists())
        r = self.client.get(self._url("lingua_plan"))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Learner.objects.filter(host_student_id=self.student.pk).exists())
        self.assertContains(r, "El sol")                 # the approved story is in the plan
        self.assertContains(r, "palabras leídas")        # the hero metric renders

    def test_plan_provision_is_idempotent(self):
        self.client.get(self._url("lingua_plan"))
        self.client.get(self._url("lingua_plan"))
        self.assertEqual(Learner.objects.filter(host_student_id=self.student.pk).count(), 1)

    def test_invalid_token_404(self):
        r = self.client.get(reverse("portal:lingua_plan", kwargs={"token": "bogus.tampered"}))
        self.assertEqual(r.status_code, 404)

    def test_reader_serves_tokenless_with_csp(self):
        r = self.client.get(self._url("lingua_read", story_id=self.story.pk))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "El sol")
        self.assertContains(r, 'id="lingua-finish"')     # finish form present
        # render_reader sets the strict CSP even though served by a host portal view
        self.assertIn("default-src", r.headers.get("Content-Security-Policy", ""))

    def test_reader_non_approved_404(self):
        draft = Story.objects.create(title="d", body="x", level="L1", status=Story.DRAFT)
        r = self.client.get(self._url("lingua_read", story_id=draft.pk))
        self.assertEqual(r.status_code, 404)             # D-49 servable gate

    def test_reader_has_no_raw_template_comment(self):
        # A multi-line {# #} comment would render as literal text (the bug the user
        # caught). The kid reader (finish_url set) must not leak any comment.
        html = self.client.get(self._url("lingua_read", story_id=self.story.pk)).content.decode()
        self.assertNotIn("CSP-clean finish", html)
        self.assertNotIn("{#", html)

    def test_finish_logs_reading_session(self):
        r = self.client.post(self._url("lingua_finish", story_id=self.story.pk), {"seconds": "45"})
        self.assertEqual(r.status_code, 302)             # PRG back to the plan
        learner = Learner.objects.get(host_student_id=self.student.pk)
        sess = learner.reading_sessions.get()
        self.assertEqual(sess.story, self.story)
        self.assertEqual(sess.seconds, 45)
        self.assertEqual(sess.words, 3)                  # "El sol brilla." → 3 words

    def test_finish_rejects_get(self):
        r = self.client.get(self._url("lingua_finish", story_id=self.story.pk))
        self.assertEqual(r.status_code, 405)             # require_POST

    def test_reader_shows_self_check(self):
        html = self.client.get(self._url("lingua_read", story_id=self.story.pk)).content.decode()
        self.assertIn('name="felt"', html)               # the 3-emoji comprehension check
        self.assertIn("¿Cómo te fue?", html)

    def test_finish_records_self_check(self):
        r = self.client.post(self._url("lingua_finish", story_id=self.story.pk),
                             {"seconds": "20", "felt": "great"})
        self.assertEqual(r.status_code, 302)
        learner = Learner.objects.get(host_student_id=self.student.pk)
        check = learner.comprehension_checks.get()
        self.assertEqual(check.kind, comprehension.SELF_CHECK)
        self.assertEqual(check.result, comprehension.PROFICIENT)   # "great" → proficient
        self.assertEqual(learner.reading_sessions.count(), 1)      # read logged too

    def test_finish_without_felt_skips_check(self):
        self.client.post(self._url("lingua_finish", story_id=self.story.pk), {"seconds": "5"})
        learner = Learner.objects.get(host_student_id=self.student.pk)
        self.assertEqual(learner.comprehension_checks.count(), 0)  # no check, no crash
        self.assertEqual(learner.reading_sessions.count(), 1)      # read still logged

    def test_finish_celebrates_crossed_milestone(self):
        big = Story.objects.create(title="big", body=" ".join(["x"] * 120),
                                   level="L1", status=Story.APPROVED)
        r = self.client.post(self._url("lingua_finish", story_id=big.pk), {"seconds": "10"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("celebrate=100", r["Location"])    # crossed the 100-word milestone
        plan = self.client.get(r["Location"])
        self.assertContains(plan, "100 palabras leídas")  # banner renders on the plan

    def test_finish_tolerates_bad_seconds(self):
        r = self.client.post(self._url("lingua_finish", story_id=self.story.pk), {"seconds": "junk"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Learner.objects.get(host_student_id=self.student.pk)
                         .reading_sessions.get().seconds, 0)

    def test_band_inferred_from_dob(self):
        from datetime import date

        from portal.views import _infer_band
        y = date.today().year
        young = Student.objects.create(parent=self.parent, first_name="Bo",
                                       date_of_birth=date(y - 8, 1, 1))
        old = Student.objects.create(parent=self.parent, first_name="Cy",
                                     date_of_birth=date(y - 12, 1, 1))
        self.assertEqual(_infer_band(young), profiles.KIDS_EARLY)
        self.assertEqual(_infer_band(old), profiles.KIDS_OLDER)

    def test_band_boundary_is_calendar_exact(self):
        # A child whose 10th birthday is TOMORROW is still 9 → KIDS_EARLY. The old
        # //365 math would drift to 10 (KIDS_OLDER) after ~2-3 leap days.
        from datetime import date, timedelta

        from portal.views import _infer_band
        today = date.today()
        try:
            tenth_bday = today.replace(year=today.year - 10)
        except ValueError:      # today is Feb 29
            tenth_bday = today.replace(year=today.year - 10, day=28)
        almost = Student.objects.create(
            parent=self.parent, first_name="N", date_of_birth=tenth_bday + timedelta(days=1))
        self.assertEqual(_infer_band(almost), profiles.KIDS_EARLY)

    def test_get_or_create_learner_recovers_from_race(self):
        # Simulate a concurrent first-entry: we saw no learner, tried to create, but a
        # racing request already inserted it (IntegrityError) → recover, don't 500.
        from django.db import IntegrityError
        winner = Learner.create_for_host_student(self.student.pk, profiles.KIDS_EARLY)
        with mock.patch.object(Learner.objects, "filter") as m_filter:
            m_filter.return_value.first.return_value = None      # our read saw nothing
            with mock.patch.object(Learner, "create_for_host_student",
                                   side_effect=IntegrityError):  # the racing insert won
                got = services.get_or_create_learner(self.student.pk, profiles.KIDS_EARLY)
        self.assertEqual(got, winner)                            # recovered the existing row


class ProgressViewTests(TestCase):
    """LGA-53/67: parent progress + advancement page (editors only)."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership
        cls.parent = User.objects.create_user("prog_parent", email="prog@e.com", password="pw")
        cls.family = Family.objects.create(name="Prog Family")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.student = Student.objects.create(parent=cls.parent, family=cls.family, first_name="Nia")
        cls.learner = Learner.create_for_host_student(
            cls.student.pk, profiles.KIDS_EARLY, content_ceiling="L1")
        cls.story = Story.objects.create(title="s", body="uno dos tres", level="L1", status=Story.APPROVED)

    def setUp(self):
        self.client.force_login(self.parent)
        session = self.client.session
        session["selected_family_id"] = self.family.id
        session.save()

    def _url(self):
        return reverse("lingua:progress")

    def _make_promotable(self):
        from datetime import timedelta

        from django.utils import timezone
        c = services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH,
                                          result=comprehension.PROFICIENT)
        ComprehensionCheck.objects.filter(pk=c.pk).update(created_at=timezone.now() - timedelta(days=20))
        for _ in range(3):
            services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH,
                                          result=comprehension.PROFICIENT)
        services.record_comprehension(self.learner, self.story, comprehension.PICTURE_MATCH,
                                      result=comprehension.BEGINNING)

    def test_requires_login(self):
        self.client.logout()
        self.assertIn(self.client.get(self._url()).status_code, (301, 302))

    def test_non_editor_gets_404(self):
        from core.models import Family, FamilyMembership
        viewer = User.objects.create_user("gp_only", email="gp@e.com", password="pw")
        FamilyMembership.objects.create(
            user=viewer, family=Family.objects.create(name="V"), role="grandparent")  # non-edit
        self.client.force_login(viewer)
        self.assertEqual(self.client.get(self._url()).status_code, 404)

    def test_navbar_links_to_spanish(self):
        # discoverable: the site navbar (base.html) links to the Lingua progress page
        html = self.client.get(reverse("students:student_list")).content.decode()
        self.assertIn(reverse("lingua:progress"), html)

    def test_renders_family_learner_with_metric(self):
        services.record_reading(self.learner, self.story)
        r = self.client.get(self._url())
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        self.assertIn("Nia", html)
        self.assertIn("palabras leídas", html)

    def test_shows_and_confirms_promotion(self):
        self._make_promotable()
        self.assertIn("L1 → L2", self.client.get(self._url()).content.decode())
        r = self.client.post(self._url(), {"host_student_id": self.student.pk,
                                           "action": "advance", "to_level": "L2"})
        self.assertEqual(r.status_code, 302)
        self.learner.profile.refresh_from_db()
        self.assertEqual(self.learner.profile.content_ceiling, "L2")
        self.assertTrue(AuditEvent.objects.filter(
            action="learner.advanced", target_id=self.learner.pk).exists())

    def test_rejects_non_recommended_level(self):
        self._make_promotable()   # recommends L2 only
        self.client.post(self._url(), {"host_student_id": self.student.pk,
                                       "action": "advance", "to_level": "L8"})
        self.learner.profile.refresh_from_db()
        self.assertEqual(self.learner.profile.content_ceiling, "L1")   # arbitrary jump refused

    def test_cannot_act_on_learner_outside_family(self):
        Learner.create_for_host_student(99999, profiles.KIDS_EARLY)    # not in this family
        r = self.client.post(self._url(), {"host_student_id": 99999,
                                           "action": "advance", "to_level": "L2"})
        self.assertEqual(r.status_code, 404)

    def test_view_only_member_of_selected_family_cannot_act(self):
        # Parent-in-own-family but only a VIEW-only grandparent in family A: selecting A
        # must not let them mutate A's learners (per-family edit gate, not global).
        from core.models import Family, FamilyMembership
        fam_a = Family.objects.create(name="A-other")
        a_parent = User.objects.create_user("a_par", email="apar@e.com", password="pw")
        FamilyMembership.objects.create(user=a_parent, family=fam_a, role="parent")
        a_student = Student.objects.create(parent=a_parent, family=fam_a, first_name="Ari")
        a_learner = Learner.create_for_host_student(a_student.pk, profiles.KIDS_EARLY, content_ceiling="L1")
        FamilyMembership.objects.create(user=self.parent, family=fam_a, role="grandparent")  # view-only
        session = self.client.session
        session["selected_family_id"] = fam_a.id
        session.save()
        r = self.client.post(self._url(), {"host_student_id": a_student.pk,
                                           "action": "advance", "to_level": "L2"})
        self.assertEqual(r.status_code, 404)
        a_learner.profile.refresh_from_db()
        self.assertEqual(a_learner.profile.content_ceiling, "L1")   # unchanged


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
