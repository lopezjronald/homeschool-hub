from datetime import date, timedelta

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser
from assignments.models import Assignment
from django.test import RequestFactory

from core.forms import TeacherInviteForm
from core.models import Family, FamilyMembership, Invitation
from core.utils import get_active_family, get_selected_family
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


class PermissionHelperTests(TestCase):
    """Tests for core.permissions module."""

    @classmethod
    def setUpTestData(cls):
        from core.permissions import (
            viewable_queryset, editable_queryset, user_can_edit,
        )

        cls.parent_user = CustomUser.objects.create_user(
            username="perm_owner", email="perm_owner@test.com", password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="perm_teacher", email="perm_teacher@test.com", password="testpass123",
        )
        cls.outsider = CustomUser.objects.create_user(
            username="perm_outsider", email="perm_outsider@test.com", password="testpass123",
        )
        cls.legacy_user = CustomUser.objects.create_user(
            username="perm_legacy", email="perm_legacy@test.com", password="testpass123",
        )

        cls.family = Family.objects.create(name="Perm Test Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        # outsider gets a membership in a DIFFERENT family (teacher-only)
        cls.other_family = Family.objects.create(name="Other Perm Family")
        FamilyMembership.objects.create(
            user=cls.outsider, family=cls.other_family, role="teacher",
        )

        # Family-owned student
        cls.student_family = Student.objects.create(
            parent=cls.parent_user, first_name="FamChild", grade_level="G03",
            family=cls.family,
        )
        # Legacy student (no family)
        cls.student_legacy = Student.objects.create(
            parent=cls.legacy_user, first_name="LegacyChild", grade_level="G01",
        )

    # ── user_can_edit ──────────────────────────────────────────────────────

    def test_user_can_edit_parent(self):
        from core.permissions import user_can_edit
        self.assertTrue(user_can_edit(self.parent_user))

    def test_user_can_edit_teacher_only(self):
        from core.permissions import user_can_edit
        self.assertFalse(user_can_edit(self.teacher_user))

    def test_user_can_edit_legacy_no_membership(self):
        from core.permissions import user_can_edit
        self.assertTrue(user_can_edit(self.legacy_user))

    def test_user_can_edit_outsider_teacher_only(self):
        from core.permissions import user_can_edit
        self.assertFalse(user_can_edit(self.outsider))

    # ── viewable_queryset ──────────────────────────────────────────────────

    def test_viewable_parent_sees_family_records(self):
        from core.permissions import viewable_queryset
        qs = viewable_queryset(Student.objects.all(), self.parent_user)
        self.assertIn(self.student_family, qs)

    def test_viewable_teacher_sees_family_records(self):
        from core.permissions import viewable_queryset
        qs = viewable_queryset(Student.objects.all(), self.teacher_user)
        self.assertIn(self.student_family, qs)

    def test_viewable_outsider_sees_nothing_in_family(self):
        from core.permissions import viewable_queryset
        qs = viewable_queryset(Student.objects.all(), self.outsider)
        self.assertNotIn(self.student_family, qs)
        self.assertNotIn(self.student_legacy, qs)

    def test_viewable_legacy_fallback(self):
        from core.permissions import viewable_queryset
        qs = viewable_queryset(Student.objects.all(), self.legacy_user)
        self.assertIn(self.student_legacy, qs)
        self.assertNotIn(self.student_family, qs)

    # ── editable_queryset ──────────────────────────────────────────────────

    def test_editable_parent_can_edit_family_records(self):
        from core.permissions import editable_queryset
        qs = editable_queryset(Student.objects.all(), self.parent_user)
        self.assertIn(self.student_family, qs)

    def test_editable_teacher_cannot_edit_family_records(self):
        from core.permissions import editable_queryset
        qs = editable_queryset(Student.objects.all(), self.teacher_user)
        self.assertNotIn(self.student_family, qs)

    def test_editable_legacy_fallback(self):
        from core.permissions import editable_queryset
        qs = editable_queryset(Student.objects.all(), self.legacy_user)
        self.assertIn(self.student_legacy, qs)


# ===========================================================================
# Invitation Model Tests
# ===========================================================================


class InvitationModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="inv_parent", email="inv_parent@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Invite Family")
        FamilyMembership.objects.create(
            user=cls.user, family=cls.family, role="parent",
        )

    def test_str(self):
        invite = Invitation.objects.create(
            email="teacher@test.com", family=self.family,
            invited_by=self.user, role="teacher",
        )
        self.assertIn("teacher@test.com", str(invite))
        self.assertIn("Invite Family", str(invite))

    def test_default_status_is_pending(self):
        invite = Invitation.objects.create(
            email="teacher@test.com", family=self.family,
            invited_by=self.user,
        )
        self.assertEqual(invite.status, Invitation.PENDING)

    def test_is_expired_false_when_recent(self):
        invite = Invitation.objects.create(
            email="teacher@test.com", family=self.family,
            invited_by=self.user,
        )
        self.assertFalse(invite.is_expired)

    def test_is_expired_true_when_old(self):
        invite = Invitation.objects.create(
            email="teacher@test.com", family=self.family,
            invited_by=self.user,
        )
        # Backdate created_at beyond expiry
        Invitation.objects.filter(pk=invite.pk).update(
            created_at=timezone.now() - timedelta(days=8),
        )
        invite.refresh_from_db()
        self.assertTrue(invite.is_expired)


# ===========================================================================
# Teacher Invite Form Tests
# ===========================================================================


class TeacherInviteFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="form_parent", email="form_parent@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Form Family")
        FamilyMembership.objects.create(
            user=cls.user, family=cls.family, role="parent",
        )

    def test_valid_email(self):
        form = TeacherInviteForm(
            data={"email": "newteacher@example.com"}, family=self.family,
        )
        self.assertTrue(form.is_valid())

    def test_duplicate_pending_rejected(self):
        Invitation.objects.create(
            email="dup@example.com", family=self.family,
            invited_by=self.user,
        )
        form = TeacherInviteForm(
            data={"email": "dup@example.com"}, family=self.family,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_reinvite_after_accepted_ok(self):
        Invitation.objects.create(
            email="accepted@example.com", family=self.family,
            invited_by=self.user, status=Invitation.ACCEPTED,
        )
        form = TeacherInviteForm(
            data={"email": "accepted@example.com"}, family=self.family,
        )
        self.assertTrue(form.is_valid())


# ===========================================================================
# Invite Teacher View Tests
# ===========================================================================


class InviteTeacherViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent_user = CustomUser.objects.create_user(
            username="view_parent", email="view_parent@test.com", password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="view_teacher", email="view_teacher@test.com", password="testpass123",
        )
        cls.no_family_user = CustomUser.objects.create_user(
            username="view_nofam", email="view_nofam@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="View Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        cls.url = reverse("core:invite_teacher")

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_parent_can_access(self):
        self.client.login(username="view_parent", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invite a Teacher")

    def test_teacher_cannot_access(self):
        self.client.login(username="view_teacher", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_no_family_shows_message(self):
        self.client.login(username="view_nofam", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Family Found")

    def test_creates_invitation_and_sends_email(self):
        self.client.login(username="view_parent", password="testpass123")
        response = self.client.post(
            self.url, {"email": "newteacher@example.com"},
        )
        self.assertRedirects(response, self.url)
        self.assertTrue(
            Invitation.objects.filter(
                email="newteacher@example.com", family=self.family,
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("newteacher@example.com", mail.outbox[0].to)
        self.assertIn("invited", mail.outbox[0].subject.lower())

    def test_shows_pending_invites(self):
        Invitation.objects.create(
            email="pending@example.com", family=self.family,
            invited_by=self.parent_user,
        )
        self.client.login(username="view_parent", password="testpass123")
        response = self.client.get(self.url)
        self.assertContains(response, "pending@example.com")


# ===========================================================================
# Accept Invite View Tests
# ===========================================================================


class AcceptInviteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent_user = CustomUser.objects.create_user(
            username="acc_parent", email="acc_parent@test.com", password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="acc_teacher", email="acc_teacher@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Accept Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )

    def _create_invite(self, **kwargs):
        defaults = {
            "email": "acc_teacher@test.com",
            "family": self.family,
            "invited_by": self.parent_user,
            "role": "teacher",
        }
        defaults.update(kwargs)
        return Invitation.objects.create(**defaults)

    def test_not_logged_in_redirects_to_login(self):
        invite = self._create_invite()
        url = reverse("core:accept_invite", kwargs={"invite_id": invite.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
        self.assertIn(str(invite.id), response.url)

    def test_valid_invite_creates_membership(self):
        invite = self._create_invite()
        self.client.login(username="acc_teacher", password="testpass123")
        url = reverse("core:accept_invite", kwargs={"invite_id": invite.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("dashboard:dashboard"))

        # Membership created
        self.assertTrue(
            FamilyMembership.objects.filter(
                user=self.teacher_user, family=self.family, role="teacher",
            ).exists()
        )
        # Invite marked accepted
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invitation.ACCEPTED)
        self.assertIsNotNone(invite.accepted_at)

    def test_already_accepted_shows_error(self):
        invite = self._create_invite(status=Invitation.ACCEPTED)
        self.client.login(username="acc_teacher", password="testpass123")
        url = reverse("core:accept_invite", kwargs={"invite_id": invite.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already been accepted")

    def test_expired_invite_shows_error(self):
        invite = self._create_invite()
        # Backdate past expiry
        Invitation.objects.filter(pk=invite.pk).update(
            created_at=timezone.now() - timedelta(days=8),
        )
        self.client.login(username="acc_teacher", password="testpass123")
        url = reverse("core:accept_invite", kwargs={"invite_id": invite.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "expired")

        # Status should be updated to expired
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invitation.EXPIRED)

    def test_idempotent_accept(self):
        """Accepting when membership already exists doesn't fail or duplicate."""
        invite = self._create_invite()
        # Pre-create the membership
        FamilyMembership.objects.create(
            user=self.teacher_user, family=self.family, role="teacher",
        )
        self.client.login(username="acc_teacher", password="testpass123")
        url = reverse("core:accept_invite", kwargs={"invite_id": invite.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("dashboard:dashboard"))

        # Still only one membership
        self.assertEqual(
            FamilyMembership.objects.filter(
                user=self.teacher_user, family=self.family,
            ).count(),
            1,
        )

    def test_invalid_uuid_returns_404(self):
        self.client.login(username="acc_teacher", password="testpass123")
        url = reverse(
            "core:accept_invite",
            kwargs={"invite_id": "00000000-0000-0000-0000-000000000000"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


# ===========================================================================
# Get Selected Family Tests
# ===========================================================================


class GetSelectedFamilyTests(TestCase):
    """Tests for core.utils.get_selected_family."""

    @classmethod
    def setUpTestData(cls):
        cls.parent_user = CustomUser.objects.create_user(
            username="sel_parent", email="sel_parent@test.com", password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="sel_teacher", email="sel_teacher@test.com", password="testpass123",
        )
        cls.legacy_user = CustomUser.objects.create_user(
            username="sel_legacy", email="sel_legacy@test.com", password="testpass123",
        )
        cls.family_a = Family.objects.create(name="Select A Family")
        cls.family_b = Family.objects.create(name="Select B Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family_a, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family_b, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family_a, role="teacher",
        )

    def _make_request(self, user, get_params=None, session=None):
        factory = RequestFactory()
        request = factory.get("/", get_params or {})
        request.user = user
        request.session = session if session is not None else {}
        return request

    def test_fallback_to_first_parent_family(self):
        request = self._make_request(self.parent_user)
        result = get_selected_family(request)
        self.assertEqual(result, self.family_a)

    def test_fallback_teacher_to_first_any_family(self):
        request = self._make_request(self.teacher_user)
        result = get_selected_family(request)
        self.assertEqual(result, self.family_a)

    def test_legacy_user_returns_none(self):
        request = self._make_request(self.legacy_user)
        result = get_selected_family(request)
        self.assertIsNone(result)

    def test_get_param_overrides_fallback(self):
        request = self._make_request(
            self.parent_user, get_params={"family_id": str(self.family_b.id)},
        )
        result = get_selected_family(request)
        self.assertEqual(result, self.family_b)

    def test_session_persists_selection(self):
        session = {}
        # First request: select family_b via GET param
        request1 = self._make_request(
            self.parent_user, get_params={"family_id": str(self.family_b.id)},
            session=session,
        )
        get_selected_family(request1)

        # Second request: no GET param, same session
        request2 = self._make_request(self.parent_user, session=session)
        result = get_selected_family(request2)
        self.assertEqual(result, self.family_b)

    def test_invalid_family_id_ignored(self):
        request = self._make_request(
            self.parent_user, get_params={"family_id": "99999"},
        )
        result = get_selected_family(request)
        self.assertEqual(result, self.family_a)  # Fallback

    def test_teacher_cannot_select_unauthorized_family(self):
        request = self._make_request(
            self.teacher_user, get_params={"family_id": str(self.family_b.id)},
        )
        result = get_selected_family(request)
        self.assertEqual(result, self.family_a)  # Falls back to their family

    def test_cached_on_request(self):
        request = self._make_request(self.parent_user)
        result1 = get_selected_family(request)
        result2 = get_selected_family(request)
        self.assertIs(result1, result2)


# ===========================================================================
# Scoped Queryset Tests
# ===========================================================================


class ScopedQuerysetTests(TestCase):
    """Tests for core.permissions.scoped_queryset."""

    @classmethod
    def setUpTestData(cls):
        cls.parent_user = CustomUser.objects.create_user(
            username="scoped_parent", email="scoped_parent@test.com", password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="scoped_teacher", email="scoped_teacher@test.com", password="testpass123",
        )
        cls.legacy_user = CustomUser.objects.create_user(
            username="scoped_legacy", email="scoped_legacy@test.com", password="testpass123",
        )

        cls.family = Family.objects.create(name="Scoped Family")
        cls.other_family = Family.objects.create(name="Other Scoped Family")

        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )

        # Family-owned student
        cls.student_in_family = Student.objects.create(
            parent=cls.parent_user, first_name="FamChild", grade_level="G03",
            family=cls.family,
        )
        # Student in different family
        cls.student_other_family = Student.objects.create(
            parent=cls.parent_user, first_name="OtherFamChild", grade_level="G03",
            family=cls.other_family,
        )
        # Legacy student (no family) owned by parent_user
        cls.student_legacy = Student.objects.create(
            parent=cls.parent_user, first_name="LegacyChild", grade_level="G01",
        )
        # Legacy student owned by legacy_user
        cls.student_legacy_other = Student.objects.create(
            parent=cls.legacy_user, first_name="OtherLegacy", grade_level="G01",
        )

    def test_parent_sees_family_and_legacy_records(self):
        from core.permissions import scoped_queryset
        qs = scoped_queryset(Student.objects.all(), self.parent_user, self.family)
        self.assertIn(self.student_in_family, qs)
        self.assertIn(self.student_legacy, qs)
        self.assertNotIn(self.student_other_family, qs)
        self.assertNotIn(self.student_legacy_other, qs)

    def test_teacher_sees_only_family_records(self):
        from core.permissions import scoped_queryset
        qs = scoped_queryset(Student.objects.all(), self.teacher_user, self.family)
        self.assertIn(self.student_in_family, qs)
        self.assertNotIn(self.student_legacy, qs)
        self.assertNotIn(self.student_other_family, qs)
        self.assertNotIn(self.student_legacy_other, qs)

    def test_legacy_user_no_family_sees_own_null_records(self):
        from core.permissions import scoped_queryset
        qs = scoped_queryset(Student.objects.all(), self.legacy_user, None)
        self.assertIn(self.student_legacy_other, qs)
        self.assertNotIn(self.student_in_family, qs)
        self.assertNotIn(self.student_legacy, qs)

    def test_scoped_excludes_other_family_records(self):
        from core.permissions import scoped_queryset
        qs = scoped_queryset(Student.objects.all(), self.parent_user, self.family)
        self.assertNotIn(self.student_other_family, qs)
