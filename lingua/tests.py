"""Foundation tests: profile constants + the no-FK learner seam.

Repo convention (see recon): django.test.TestCase + setUpTestData, no pytest.
Run: `python manage.py collectstatic --noinput && python manage.py test lingua`.
"""
from django.db import models as dj_models
from django.test import TestCase

from . import profiles
from .models import Learner, LearnerProfile


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
