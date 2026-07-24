"""Foundation tests: profile constants + the no-FK learner seam.

Repo convention (see recon): django.test.TestCase + setUpTestData, no pytest.
Run: `python manage.py collectstatic --noinput && python manage.py test lingua`.
"""
import inspect

from django.contrib.auth import get_user_model
from django.db import models as dj_models
from django.test import TestCase

from students.models import Student

from . import profiles, services
from .integrations import directory
from .models import Learner, LearnerProfile
from .ports import AIClient, AIResult

User = get_user_model()


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
                if isinstance(f, dj_models.ForeignKey) or isinstance(f, dj_models.OneToOneField):
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


class PortsAndAdapterTests(TestCase):
    """The AIClient port + host adapter seam (D-04)."""

    def test_ports_module_has_no_django_or_host_imports(self):
        """ports.py must IMPORT no Django/host coupling — enforced, not just documented.
        Checks actual import statements via AST (docstring prose may mention them)."""
        import ast

        from lingua import ports as ports_mod
        tree = ast.parse(inspect.getsource(ports_mod))
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                roots.add((node.module or "").split(".")[0])
        self.assertNotIn("django", roots)
        self.assertNotIn("tutor", roots)
        self.assertNotIn("students", roots)

    def test_factory_returns_an_aiclient(self):
        client = services.get_ai_client()
        self.assertIsInstance(client, AIClient)

    def test_factory_adapter_reports_unconfigured_without_key(self):
        # Test env has no ANTHROPIC_API_KEY -> adapter degrades, no crash.
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
