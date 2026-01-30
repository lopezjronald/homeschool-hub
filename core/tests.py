from datetime import date

from django.test import TestCase

from accounts.models import CustomUser
from assignments.models import Assignment
from core.models import Family, FamilyMembership
from core.utils import get_active_family
from curricula.models import Curriculum
from students.models import Student


class FamilyBackfillMixin:
    """Shared helper to create a parent user with child data."""

    def create_parent_with_data(self, username="parent1", email="p1@example.com"):
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password="testpass123",
            last_name="Smith",
            role="parent",
        )
        student = Student.objects.create(
            parent=user,
            first_name="Alice",
            grade_level="G03",
        )
        curriculum = Curriculum.objects.create(
            parent=user,
            name="Math 3A",
            subject="Math",
        )
        assignment = Assignment.objects.create(
            parent=user,
            child=student,
            curriculum=curriculum,
            title="Chapter 1",
            due_date=date(2026, 6, 1),
        )
        return user, student, curriculum, assignment


class BackfillCreatesFamily(FamilyBackfillMixin, TestCase):
    """Migration creates a Family + Membership for a user with existing data."""

    def test_family_created_for_parent_with_students(self):
        user, student, curriculum, assignment = self.create_parent_with_data()

        # Clear family FKs to simulate pre-backfill state
        Student.objects.filter(pk=student.pk).update(family=None)
        Curriculum.objects.filter(pk=curriculum.pk).update(family=None)
        Assignment.objects.filter(pk=assignment.pk).update(family=None)

        # Run backfill logic directly
        from core.utils import backfill_families
        from django.apps import apps

        backfill_families(apps, None)

        # Family and membership should exist
        self.assertEqual(Family.objects.count(), 1)
        family = Family.objects.first()
        self.assertEqual(family.name, "Smith Family")

        self.assertEqual(FamilyMembership.objects.count(), 1)
        mem = FamilyMembership.objects.first()
        self.assertEqual(mem.user, user)
        self.assertEqual(mem.family, family)
        self.assertEqual(mem.role, "parent")

    def test_backfill_sets_family_on_all_resources(self):
        user, student, curriculum, assignment = self.create_parent_with_data()

        # Clear family FKs
        Student.objects.filter(pk=student.pk).update(family=None)
        Curriculum.objects.filter(pk=curriculum.pk).update(family=None)
        Assignment.objects.filter(pk=assignment.pk).update(family=None)

        from core.utils import backfill_families
        from django.apps import apps

        backfill_families(apps, None)

        student.refresh_from_db()
        curriculum.refresh_from_db()
        assignment.refresh_from_db()

        family = Family.objects.first()
        self.assertEqual(student.family, family)
        self.assertEqual(curriculum.family, family)
        self.assertEqual(assignment.family, family)


class BackfillNoOverwrite(FamilyBackfillMixin, TestCase):
    """If family is already set, migration does not overwrite."""

    def test_existing_family_not_overwritten(self):
        user, student, curriculum, assignment = self.create_parent_with_data()

        # Create a pre-existing family and assign it
        existing_family = Family.objects.create(name="Existing Family")
        FamilyMembership.objects.create(
            user=user,
            family=existing_family,
            role="parent",
        )
        Student.objects.filter(pk=student.pk).update(family=existing_family)
        Curriculum.objects.filter(pk=curriculum.pk).update(family=existing_family)
        # Leave assignment family as None to test partial backfill
        Assignment.objects.filter(pk=assignment.pk).update(family=None)

        from core.utils import backfill_families
        from django.apps import apps

        backfill_families(apps, None)

        student.refresh_from_db()
        curriculum.refresh_from_db()
        assignment.refresh_from_db()

        # Student and curriculum keep existing family (not overwritten)
        self.assertEqual(student.family, existing_family)
        self.assertEqual(curriculum.family, existing_family)
        # Assignment was null, so it gets the existing family
        self.assertEqual(assignment.family, existing_family)


class BackfillIdempotent(FamilyBackfillMixin, TestCase):
    """Running migration twice doesn't create extra Families/Memberships."""

    def test_idempotent_run(self):
        user, student, curriculum, assignment = self.create_parent_with_data()

        # Clear family FKs
        Student.objects.filter(pk=student.pk).update(family=None)
        Curriculum.objects.filter(pk=curriculum.pk).update(family=None)
        Assignment.objects.filter(pk=assignment.pk).update(family=None)

        from core.utils import backfill_families
        from django.apps import apps

        # Run twice
        backfill_families(apps, None)
        family_count_after_first = Family.objects.count()
        membership_count_after_first = FamilyMembership.objects.count()

        backfill_families(apps, None)
        family_count_after_second = Family.objects.count()
        membership_count_after_second = FamilyMembership.objects.count()

        self.assertEqual(family_count_after_first, family_count_after_second)
        self.assertEqual(membership_count_after_first, membership_count_after_second)

        # Values on resources should remain unchanged
        student.refresh_from_db()
        family = Family.objects.first()
        self.assertEqual(student.family, family)


class BackfillFamilyNaming(TestCase):
    """Test family naming logic for different user configurations."""

    def test_family_name_from_last_name(self):
        user = CustomUser.objects.create_user(
            username="withname",
            email="name@example.com",
            password="testpass123",
            last_name="Johnson",
        )
        Student.objects.create(parent=user, first_name="Bob", grade_level="G01")
        Student.objects.filter(parent=user).update(family=None)

        from core.utils import backfill_families
        from django.apps import apps

        backfill_families(apps, None)

        family = Family.objects.first()
        self.assertEqual(family.name, "Johnson Family")

    def test_family_name_from_email_when_no_last_name(self):
        user = CustomUser.objects.create_user(
            username="noname",
            email="noname@example.com",
            password="testpass123",
            last_name="",
        )
        Student.objects.create(parent=user, first_name="Carol", grade_level="G02")
        Student.objects.filter(parent=user).update(family=None)

        from core.utils import backfill_families
        from django.apps import apps

        backfill_families(apps, None)

        family = Family.objects.first()
        self.assertEqual(family.name, "noname@example.com Family")


class GetActiveFamilyTests(FamilyBackfillMixin, TestCase):
    """Tests for core.utils.get_active_family."""

    def test_returns_family_for_parent_member(self):
        user, _, _, _ = self.create_parent_with_data()

        # Clear and re-backfill so family exists
        Student.objects.filter(parent=user).update(family=None)
        Curriculum.objects.filter(parent=user).update(family=None)
        Assignment.objects.filter(parent=user).update(family=None)

        from core.utils import backfill_families
        from django.apps import apps

        backfill_families(apps, None)

        family = get_active_family(user)
        self.assertIsNotNone(family)
        self.assertEqual(family.name, "Smith Family")

    def test_returns_none_when_no_membership(self):
        user = CustomUser.objects.create_user(
            username="lonely",
            email="lonely@example.com",
            password="testpass123",
        )
        self.assertIsNone(get_active_family(user))

    def test_returns_first_parent_family_by_id(self):
        user = CustomUser.objects.create_user(
            username="multi",
            email="multi@example.com",
            password="testpass123",
        )
        family_a = Family.objects.create(name="A Family")
        family_b = Family.objects.create(name="B Family")

        # Create memberships: family_a first (lower id)
        FamilyMembership.objects.create(user=user, family=family_a, role="parent")
        FamilyMembership.objects.create(user=user, family=family_b, role="parent")

        result = get_active_family(user)
        self.assertEqual(result, family_a)

    def test_ignores_teacher_role(self):
        user = CustomUser.objects.create_user(
            username="teacher",
            email="teacher@example.com",
            password="testpass123",
        )
        family = Family.objects.create(name="Other Family")
        FamilyMembership.objects.create(user=user, family=family, role="teacher")

        self.assertIsNone(get_active_family(user))
