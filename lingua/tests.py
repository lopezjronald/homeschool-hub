"""Foundation tests: profile constants, the no-FK learner seam, the host-identity
directory, and the AIClient port/adapter — plus AST guards that ENFORCE the D-03/D-04
extractability rules (the module's whole reason to exist).

Repo convention: django.test.TestCase + setUpTestData, no pytest.
Run: `python manage.py collectstatic --noinput && python manage.py test lingua`.
"""
import ast
import inspect
import pathlib

from django.contrib.auth import get_user_model
from django.db import models as dj_models
from django.test import RequestFactory, TestCase, override_settings

from students.models import Student

from . import profiles, services
from .integrations import directory
from .models import Learner, LearnerProfile
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
        """No FK from any lingua model points outside the lingua app label."""
        for model in (Learner, LearnerProfile):
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
