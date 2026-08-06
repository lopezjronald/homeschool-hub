from datetime import date, timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from io import StringIO

from django.core.management import call_command

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

    # ── can_edit_family_or_global (per-object edit gate, closes cross-family leak) ──

    def test_or_global_editor_of_that_family(self):
        from core.permissions import can_edit_family_or_global
        self.assertTrue(can_edit_family_or_global(self.parent_user, self.family))

    def test_or_global_editor_ELSEWHERE_cannot_edit_this_family(self):
        # The leak fix: a user who is an editor in ANOTHER family but only a viewer of
        # THIS family must NOT get edit rights here. The old global user_can_edit
        # returned True for such a user (they can edit somewhere) — this is the case
        # that regressed portal-URL exposure. Mutation guard vs reverting to user_can_edit.
        cross = CustomUser.objects.create_user(
            username="cross", email="cross@test.com", password="testpass123")
        FamilyMembership.objects.create(user=cross, family=self.other_family, role="parent")
        FamilyMembership.objects.create(user=cross, family=self.family, role="teacher")
        from core.permissions import user_can_edit, can_edit_family_or_global
        self.assertTrue(user_can_edit(cross))                                # editor somewhere
        self.assertFalse(can_edit_family_or_global(cross, self.family))      # but NOT here

    def test_or_global_falls_back_to_global_right_for_family_less_content(self):
        from core.permissions import can_edit_family_or_global
        # Global/shared content (family=None): editors keep editing; legacy standalone
        # users (no memberships) keep their edit right — no regression.
        self.assertTrue(can_edit_family_or_global(self.parent_user, None))
        self.assertTrue(can_edit_family_or_global(self.legacy_user, None))
        self.assertFalse(can_edit_family_or_global(self.outsider, None))     # editor nowhere

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
# Invite people View Tests
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
        self.assertContains(response, "Invite someone")

    def test_teacher_cannot_access(self):
        self.client.login(username="view_teacher", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_no_family_shows_message(self):
        self.client.login(username="view_nofam", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No family yet")

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

    def test_not_logged_in_shows_signup_form(self):
        # Anonymous users can now create an account via the invite link.
        invite = self._create_invite()
        url = reverse("core:accept_invite", kwargs={"invite_id": invite.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create account")

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


# ===========================================================================
# Invite people Nav Link Tests (HH-73)
# ===========================================================================


class InviteTeacherNavTests(TestCase):
    """Tests for HH-73: 'Invite people' link visibility in navbar."""

    @classmethod
    def setUpTestData(cls):
        cls.parent_user = CustomUser.objects.create_user(
            username="nav_parent", email="nav_parent@test.com", password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="nav_teacher", email="nav_teacher@test.com", password="testpass123",
        )
        cls.no_family_user = CustomUser.objects.create_user(
            username="nav_nofam", email="nav_nofam@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Nav Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )

    def test_parent_sees_invite_teacher_link(self):
        self.client.login(username="nav_parent", password="testpass123")
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertContains(response, "Invite people")
        self.assertContains(response, reverse("core:invite_teacher"))

    def test_teacher_does_not_see_invite_teacher_link(self):
        self.client.login(username="nav_teacher", password="testpass123")
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertNotContains(response, "Invite people")

    def test_no_family_user_does_not_see_invite_teacher_link(self):
        self.client.login(username="nav_nofam", password="testpass123")
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertNotContains(response, "Invite people")


# ===========================================================================
# Resend Invite View Tests (HH-74)
# ===========================================================================


class ResendInviteViewTests(TestCase):
    """Tests for HH-74: resend pending invitations."""

    @classmethod
    def setUpTestData(cls):
        cls.parent_user = CustomUser.objects.create_user(
            username="resend_parent", email="resend_parent@test.com",
            password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="resend_teacher", email="resend_teacher@test.com",
            password="testpass123",
        )
        cls.family = Family.objects.create(name="Resend Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )

    def _create_invite(self, **kwargs):
        defaults = {
            "email": "invited@example.com",
            "family": self.family,
            "invited_by": self.parent_user,
            "role": "teacher",
        }
        defaults.update(kwargs)
        return Invitation.objects.create(**defaults)

    def test_parent_can_resend_pending_invite(self):
        invite = self._create_invite()
        self.client.login(username="resend_parent", password="testpass123")
        url = reverse("core:resend_invite", kwargs={"invite_id": invite.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("core:invite_teacher"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("invited@example.com", mail.outbox[0].to)
        invite.refresh_from_db()
        self.assertIsNotNone(invite.resent_at)

    def test_parent_cannot_resend_expired_invite(self):
        invite = self._create_invite()
        # Backdate past expiry
        Invitation.objects.filter(pk=invite.pk).update(
            created_at=timezone.now() - timedelta(days=8),
        )
        self.client.login(username="resend_parent", password="testpass123")
        url = reverse("core:resend_invite", kwargs={"invite_id": invite.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("core:invite_teacher"))
        self.assertEqual(len(mail.outbox), 0)

    def test_teacher_cannot_access_resend(self):
        invite = self._create_invite()
        self.client.login(username="resend_teacher", password="testpass123")
        url = reverse("core:resend_invite", kwargs={"invite_id": invite.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_copy_link_only_for_resendable_invites(self):
        """Resend + Copy Link buttons appear only for pending + not-expired."""
        pending_invite = self._create_invite()
        expired_invite = self._create_invite(email="expired@example.com")
        Invitation.objects.filter(pk=expired_invite.pk).update(
            created_at=timezone.now() - timedelta(days=8),
        )

        self.client.login(username="resend_parent", password="testpass123")
        response = self.client.get(reverse("core:invite_teacher"))

        # Pending invite shows Resend and Copy Link buttons
        self.assertContains(response, "Resend")
        self.assertContains(response, "Copy link")

        # Expired invite shows badge instead
        self.assertContains(response, "Expired")


# ===========================================================================
# HH-23: Cross-Family Access Control Regression Tests
# ===========================================================================


class CrossFamilyAccessControlTests(TestCase):
    """
    Security regression tests for HH-23: Verify family data isolation.

    These tests ensure:
    - Parent cannot access another family's students/curricula/assignments
    - Teacher cannot access families they're not assigned to
    - Teacher cannot access create/update/delete endpoints
    - Dashboard/dropdowns do not leak cross-family data
    """

    @classmethod
    def setUpTestData(cls):
        # ── Family A (parent_a owns it, teacher_a is assigned) ──
        cls.parent_a = CustomUser.objects.create_user(
            username="xf_parent_a", email="xf_parent_a@test.com", password="testpass123",
        )
        cls.teacher_a = CustomUser.objects.create_user(
            username="xf_teacher_a", email="xf_teacher_a@test.com", password="testpass123",
        )
        cls.family_a = Family.objects.create(name="Cross Family A")
        FamilyMembership.objects.create(
            user=cls.parent_a, family=cls.family_a, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_a, family=cls.family_a, role="teacher",
        )
        cls.student_a = Student.objects.create(
            parent=cls.parent_a, first_name="ChildA", grade_level="G03",
            family=cls.family_a,
        )
        cls.curriculum_a = Curriculum.objects.create(
            parent=cls.parent_a, name="Math A", subject="Math",
            family=cls.family_a,
        )
        cls.assignment_a = Assignment.objects.create(
            parent=cls.parent_a, child=cls.student_a, curriculum=cls.curriculum_a,
            title="Assignment A", due_date=date.today(), family=cls.family_a,
        )

        # ── Family B (parent_b owns it, teacher_b is assigned) ──
        cls.parent_b = CustomUser.objects.create_user(
            username="xf_parent_b", email="xf_parent_b@test.com", password="testpass123",
        )
        cls.teacher_b = CustomUser.objects.create_user(
            username="xf_teacher_b", email="xf_teacher_b@test.com", password="testpass123",
        )
        cls.family_b = Family.objects.create(name="Cross Family B")
        FamilyMembership.objects.create(
            user=cls.parent_b, family=cls.family_b, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_b, family=cls.family_b, role="teacher",
        )
        cls.student_b = Student.objects.create(
            parent=cls.parent_b, first_name="ChildB", grade_level="G05",
            family=cls.family_b,
        )
        cls.curriculum_b = Curriculum.objects.create(
            parent=cls.parent_b, name="Math B", subject="Math",
            family=cls.family_b,
        )
        cls.assignment_b = Assignment.objects.create(
            parent=cls.parent_b, child=cls.student_b, curriculum=cls.curriculum_b,
            title="Assignment B", due_date=date.today(), family=cls.family_b,
        )

    # ── Parent A cannot access Family B's data ────────────────────────────

    def test_parent_cannot_view_other_family_student_detail(self):
        """Parent A cannot view Family B's student detail."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_edit_other_family_student(self):
        """Parent A cannot edit Family B's student."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(
            reverse("students:student_update", kwargs={"pk": self.student_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_delete_other_family_student(self):
        """Parent A cannot delete Family B's student."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.post(
            reverse("students:student_delete", kwargs={"pk": self.student_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_view_other_family_curriculum_detail(self):
        """Parent A cannot view Family B's curriculum detail."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_edit_other_family_curriculum(self):
        """Parent A cannot edit Family B's curriculum."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_update", kwargs={"pk": self.curriculum_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_delete_other_family_curriculum(self):
        """Parent A cannot delete Family B's curriculum."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.post(
            reverse("curricula:curriculum_delete", kwargs={"pk": self.curriculum_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_view_other_family_assignment_detail(self):
        """Parent A cannot view Family B's assignment detail."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment_b.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_edit_other_family_assignment(self):
        """Parent A cannot edit Family B's assignment."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_update", args=[self.assignment_b.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_cannot_delete_other_family_assignment(self):
        """Parent A cannot delete Family B's assignment."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_delete", args=[self.assignment_b.pk])
        )
        self.assertEqual(response.status_code, 404)

    # ── Teacher A cannot access Family B's data ───────────────────────────

    def test_teacher_cannot_view_unassigned_family_student(self):
        """Teacher A (assigned to Family A) cannot view Family B's student."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_view_unassigned_family_curriculum(self):
        """Teacher A cannot view Family B's curriculum."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum_b.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_view_unassigned_family_assignment(self):
        """Teacher A cannot view Family B's assignment."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment_b.pk])
        )
        self.assertEqual(response.status_code, 404)

    # ── Teacher cannot access create/update/delete for students/curricula ─

    def test_teacher_cannot_create_student(self):
        """Teacher (even in assigned family) cannot create students."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(reverse("students:student_create"))
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_update_student(self):
        """Teacher cannot update students."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(
            reverse("students:student_update", kwargs={"pk": self.student_a.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_student(self):
        """Teacher cannot delete students."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.post(
            reverse("students:student_delete", kwargs={"pk": self.student_a.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_create_curriculum(self):
        """Teacher cannot create curricula."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_create"))
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_update_curriculum(self):
        """Teacher cannot update curricula."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_update", kwargs={"pk": self.curriculum_a.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_curriculum(self):
        """Teacher cannot delete curricula."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.post(
            reverse("curricula:curriculum_delete", kwargs={"pk": self.curriculum_a.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_assignment(self):
        """Teacher cannot delete assignments (even their own)."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_delete", args=[self.assignment_a.pk])
        )
        self.assertEqual(response.status_code, 404)

    # ── Dashboard/list views do not leak cross-family data ────────────────

    def test_student_list_does_not_leak_other_family(self):
        """Student list only shows current family's students."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(reverse("students:student_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ChildA")
        self.assertNotContains(response, "ChildB")

    def test_curriculum_list_does_not_leak_other_family(self):
        """Curriculum list only shows current family's curricula."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Math A")
        self.assertNotContains(response, "Math B")

    def test_assignment_list_does_not_leak_other_family(self):
        """Assignment list only shows current family's assignments."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Assignment A")
        self.assertNotContains(response, "Assignment B")

    def test_dashboard_does_not_leak_other_family(self):
        """Progress dashboard only shows the current family's children."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ChildA")
        self.assertNotContains(response, "ChildB")
        # Verify the child dropdown only contains Family A's child
        children = list(response.context["children"])
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].first_name, "ChildA")

    def test_dashboard_filter_dropdown_scoped_to_family(self):
        """Dashboard child dropdown only contains the current family's children."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(reverse("dashboard:dashboard"))
        children = list(response.context["children"])
        self.assertEqual([c.first_name for c in children], ["ChildA"])
        self.assertNotContains(response, "ChildB")

    # ── URL manipulation cannot bypass family scope ──────────────────────

    def test_parent_cannot_force_switch_to_unowned_family(self):
        """Parent A cannot access Family B data via family_id URL param."""
        self.client.login(username="xf_parent_a", password="testpass123")
        response = self.client.get(
            reverse("dashboard:dashboard"), {"family_id": self.family_b.id}
        )
        self.assertEqual(response.status_code, 200)
        # Should still show Family A data (fallback to owned family)
        self.assertContains(response, "ChildA")
        self.assertNotContains(response, "ChildB")

    def test_teacher_cannot_force_switch_to_unassigned_family(self):
        """Teacher A cannot access Family B data via family_id URL param."""
        self.client.login(username="xf_teacher_a", password="testpass123")
        response = self.client.get(
            reverse("dashboard:dashboard"), {"family_id": self.family_b.id}
        )
        self.assertEqual(response.status_code, 200)
        # Should still show Family A data (fallback to assigned family)
        self.assertContains(response, "ChildA")
        self.assertNotContains(response, "ChildB")


class CoParentInviteTests(TestCase):
    """HH-88: invite co-parent/guardian/grandparent; new users sign up via the link."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = CustomUser.objects.create_user(username="owner", email="owner@e.com", password="pw")
        cls.family = Family.objects.create(name="Invite Home")
        FamilyMembership.objects.create(user=cls.owner, family=cls.family, role="parent")

    def test_invite_records_chosen_role(self):
        self.client.login(username="owner", password="pw")
        self.client.post(reverse("core:invite_teacher"), {"email": "cp@e.com", "role": "parent"})
        inv = Invitation.objects.get(email="cp@e.com")
        self.assertEqual(inv.role, "parent")
        self.assertEqual(inv.role_display, "Co-parent")
        self.client.post(reverse("core:invite_teacher"), {"email": "gma@e.com", "role": "grandparent"})
        self.assertEqual(Invitation.objects.get(email="gma@e.com").role, "grandparent")

    def test_new_user_signs_up_via_link_and_joins(self):
        inv = Invitation.objects.create(
            email="newco@e.com", family=self.family, invited_by=self.owner, role="parent",
        )
        url = reverse("core:accept_invite", kwargs={"invite_id": inv.id})
        self.assertEqual(self.client.get(url).status_code, 200)  # anon sees signup form
        resp = self.client.post(url, {
            "username": "coparent", "email": "newco@e.com",
            "password1": "Str0ngPass!23", "password2": "Str0ngPass!23",
        })
        self.assertEqual(resp.status_code, 302)
        user = CustomUser.objects.get(username="coparent")
        self.assertTrue(user.is_active)
        self.assertTrue(
            FamilyMembership.objects.filter(user=user, family=self.family, role="parent").exists()
        )
        inv.refresh_from_db()
        self.assertEqual(inv.status, Invitation.ACCEPTED)
        self.assertIn("_auth_user_id", self.client.session)  # logged in

    def test_signup_password_mismatch_creates_no_user(self):
        inv = Invitation.objects.create(
            email="x@e.com", family=self.family, invited_by=self.owner, role="teacher",
        )
        url = reverse("core:accept_invite", kwargs={"invite_id": inv.id})
        resp = self.client.post(url, {
            "username": "xx", "email": "x@e.com",
            "password1": "Str0ngPass!23", "password2": "different",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username="xx").exists())

    def test_guardian_edits_grandparent_views_only(self):
        from core.permissions import user_can_edit

        guardian = CustomUser.objects.create_user(username="guard", email="g@e.com", password="pw")
        grandparent = CustomUser.objects.create_user(username="gp", email="gp@e.com", password="pw")
        FamilyMembership.objects.create(user=guardian, family=self.family, role="guardian")
        FamilyMembership.objects.create(user=grandparent, family=self.family, role="grandparent")
        self.assertTrue(user_can_edit(guardian))
        self.assertFalse(user_can_edit(grandparent))


class HubNavTests(TestCase):
    """HH-90: tiled parent hub + slimmed nav + Account dropdown."""

    def setUp(self):
        self.parent = CustomUser.objects.create_user(
            username="hubparent", email="hub@e.com", password="pw",
        )
        fam = Family.objects.create(name="Hub Family")
        FamilyMembership.objects.create(user=self.parent, family=fam, role="parent")

    def test_home_is_a_hub_for_signed_in_parent(self):
        self.client.login(username="hubparent", password="pw")
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "hub-tile")
        self.assertContains(resp, "Welcome back")
        self.assertContains(resp, "Work Log &amp; Report")
        self.assertContains(resp, ">Progress<")
        # The Spanish area must be reachable from the hub in one click, and the
        # tile must NAME writing — the parent could not find the writing track
        # because the only entry was a navbar link labelled "Spanish" landing on
        # a "Progress" page (HH-156). A hub tile that says "writing" fixes the
        # mental model regardless of which sub-page it lands on.
        self.assertContains(resp, reverse("lingua:progress"))
        self.assertContains(resp, ">Spanish<")
        self.assertContains(resp, "writing")

    def test_nav_drops_assignments_and_has_account_dropdown(self):
        self.client.login(username="hubparent", password="pw")
        resp = self.client.get(reverse("home"))
        self.assertNotContains(resp, reverse("assignments:assignment_list"))
        self.assertContains(resp, "accountMenu")           # Account dropdown
        self.assertContains(resp, "Log out")               # logout lives inside it

    def test_logged_out_home_shows_marketing(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "hub-tile")
        self.assertContains(resp, "Create account")


# ===========================================================================
# HH-47: Remove Family Member View Tests
# ===========================================================================


class RemoveMemberViewTests(TestCase):
    """HH-47: parents revoke family members; the primary parent is protected."""

    @classmethod
    def setUpTestData(cls):
        cls.family = Family.objects.create(name="Remove Family")

        # Primary parent = earliest parent-role membership (created first).
        cls.primary_parent = CustomUser.objects.create_user(
            username="rm_primary", email="rm_primary@test.com", password="testpass123",
        )
        cls.primary_membership = FamilyMembership.objects.create(
            user=cls.primary_parent, family=cls.family, role="parent",
        )
        # A second, non-primary parent.
        cls.second_parent = CustomUser.objects.create_user(
            username="rm_second", email="rm_second@test.com", password="testpass123",
        )
        cls.second_membership = FamilyMembership.objects.create(
            user=cls.second_parent, family=cls.family, role="parent",
        )
        # A grandparent member (removable).
        cls.grandparent = CustomUser.objects.create_user(
            username="rm_grandparent", email="rm_gp@test.com", password="testpass123",
        )
        cls.grandparent_membership = FamilyMembership.objects.create(
            user=cls.grandparent, family=cls.family, role="grandparent",
        )
        # A teacher (non-parent → no active family).
        cls.teacher = CustomUser.objects.create_user(
            username="rm_teacher", email="rm_teacher@test.com", password="testpass123",
        )
        cls.teacher_membership = FamilyMembership.objects.create(
            user=cls.teacher, family=cls.family, role="teacher",
        )

        # A separate family with its own member.
        cls.other_family = Family.objects.create(name="Other Remove Family")
        cls.other_parent = CustomUser.objects.create_user(
            username="rm_other_parent", email="rm_other@test.com", password="testpass123",
        )
        FamilyMembership.objects.create(
            user=cls.other_parent, family=cls.other_family, role="parent",
        )
        cls.other_member = CustomUser.objects.create_user(
            username="rm_other_member", email="rm_other_m@test.com", password="testpass123",
        )
        cls.other_membership = FamilyMembership.objects.create(
            user=cls.other_member, family=cls.other_family, role="grandparent",
        )

    def _url(self, membership_id):
        return reverse("core:remove_member", kwargs={"membership_id": membership_id})

    def test_primary_parent_removes_non_primary_member(self):
        self.client.login(username="rm_primary", password="testpass123")
        response = self.client.post(self._url(self.grandparent_membership.pk))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            FamilyMembership.objects.filter(pk=self.grandparent_membership.pk).exists()
        )

    def test_removing_primary_parent_is_blocked(self):
        self.client.login(username="rm_primary", password="testpass123")
        response = self.client.post(self._url(self.primary_membership.pk), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            FamilyMembership.objects.filter(pk=self.primary_membership.pk).exists()
        )
        self.assertContains(response, "be removed from the family")

    def test_teacher_post_returns_404(self):
        self.client.login(username="rm_teacher", password="testpass123")
        response = self.client.post(self._url(self.grandparent_membership.pk))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            FamilyMembership.objects.filter(pk=self.grandparent_membership.pk).exists()
        )

    def test_get_returns_405(self):
        self.client.login(username="rm_primary", password="testpass123")
        response = self.client.get(self._url(self.grandparent_membership.pk))
        self.assertEqual(response.status_code, 405)

    def test_member_in_another_family_returns_404(self):
        self.client.login(username="rm_primary", password="testpass123")
        response = self.client.post(self._url(self.other_membership.pk))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            FamilyMembership.objects.filter(pk=self.other_membership.pk).exists()
        )

    def test_non_primary_parent_can_leave(self):
        self.client.login(username="rm_second", password="testpass123")
        response = self.client.post(self._url(self.second_membership.pk))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            FamilyMembership.objects.filter(pk=self.second_membership.pk).exists()
        )


class SetupProgressTests(TestCase):
    """Onboarding setup-checklist service + surfaces (HH-102)."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(
            username="newparent", email="new@example.com", password="testpass123",
        )

    def _progress(self):
        from core.services import get_setup_progress

        request = self.factory.get("/")
        request.user = self.user
        return get_setup_progress(request, None)

    def test_new_parent_all_steps_incomplete(self):
        p = self._progress()
        self.assertEqual(p["total"], 4)
        self.assertEqual(p["done_count"], 0)
        self.assertEqual(p["percent"], 0)
        self.assertFalse(p["complete"])
        self.assertTrue(p["steps"][0]["is_next"])   # first action foregrounded
        self.assertFalse(p["steps"][0]["done"])

    def test_child_and_subject_advance_the_checklist(self):
        Student.objects.create(parent=self.user, first_name="Vi", grade_level="G03")
        Curriculum.objects.create(parent=self.user, name="Lit 3", subject="Literature")
        p = self._progress()
        self.assertTrue(p["steps"][0]["done"])      # child
        self.assertTrue(p["steps"][1]["done"])      # subject
        self.assertEqual(p["done_count"], 2)
        self.assertFalse(p["complete"])
        self.assertEqual(p["steps"][2]["key"], "portal")
        self.assertTrue(p["steps"][2]["is_next"])   # next action is the portal

    def test_read_only_reviewer_sees_no_checklist(self):
        # A user whose only membership is a read-only role never gets the card.
        family = Family.objects.create(name="Read-Only Fam")
        FamilyMembership.objects.create(user=self.user, family=family, role="grandparent")
        from core.services import get_setup_progress

        request = self.factory.get("/")
        request.user = self.user
        p = get_setup_progress(request, family)
        self.assertTrue(p["complete"])
        self.assertEqual(p["steps"], [])

    def test_hub_renders_checklist_for_new_user(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("home"))
        self.assertContains(resp, "Get set up")

    def test_student_list_shows_guided_empty_state(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("students:student_list"))
        self.assertContains(resp, "Add your first child")

    def test_sample_report_is_public(self):
        resp = self.client.get(reverse("worklog:sample_report"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "sample report")


class FamilyRenameTests(TestCase):
    """Renaming the household is editor-only."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = CustomUser.objects.create_user(username="frp", email="frp@e.com", password="pw")
        cls.teacher = CustomUser.objects.create_user(username="frt", email="frt@e.com", password="pw")
        cls.family = Family.objects.create(name="Old Name")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.url = reverse("core:family_settings")

    def test_editor_can_rename(self):
        self.client.login(username="frp", password="pw")
        resp = self.client.post(self.url, {"name": "New Name"})
        self.assertRedirects(resp, self.url)
        self.family.refresh_from_db()
        self.assertEqual(self.family.name, "New Name")

    def test_teacher_gets_404(self):
        self.client.login(username="frt", password="pw")
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_requires_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)


class InviteFamilySelectionTests(TestCase):
    """A multi-family parent's member-management acts on the SELECTED family, not
    their primary/active family (the cross-family write bug)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="multiparent", email="mp@e.com", password="testpass123")
        cls.fam_a = Family.objects.create(name="Alpha")   # lower id -> the "active" family
        cls.fam_b = Family.objects.create(name="Beta")
        FamilyMembership.objects.create(user=cls.user, family=cls.fam_a, role="parent")
        FamilyMembership.objects.create(user=cls.user, family=cls.fam_b, role="parent")

    def setUp(self):
        self.client.force_login(self.user)

    def test_invite_created_against_selected_family(self):
        # Viewing family B (?family_id=B), the invitation must be filed under B — not
        # A (the primary/active family that get_active_family would have returned).
        resp = self.client.post(
            reverse("core:invite_teacher") + f"?family_id={self.fam_b.pk}",
            {"email": "grandma@e.com", "role": "teacher"},
        )
        self.assertEqual(resp.status_code, 302)
        inv = Invitation.objects.get(email="grandma@e.com")
        self.assertEqual(inv.family, self.fam_b)          # selected, not active (fam_a)

    def test_rename_hits_selected_family(self):
        resp = self.client.post(
            reverse("core:family_settings") + f"?family_id={self.fam_b.pk}",
            {"name": "Beta Renamed"},
        )
        self.assertEqual(resp.status_code, 302)
        self.fam_a.refresh_from_db(); self.fam_b.refresh_from_db()
        self.assertEqual(self.fam_b.name, "Beta Renamed")  # selected renamed
        self.assertEqual(self.fam_a.name, "Alpha")         # active untouched

    def test_viewer_of_selected_family_cannot_invite(self):
        # A user who is only a VIEWER of the selected family gets a 404, not a silent
        # fallback to inviting into a family they can edit.
        viewer = CustomUser.objects.create_user(
            username="vieweronly", email="vo@e.com", password="testpass123")
        editable = Family.objects.create(name="Editable")
        FamilyMembership.objects.create(user=viewer, family=editable, role="parent")
        FamilyMembership.objects.create(user=viewer, family=self.fam_a, role="teacher")
        self.client.force_login(viewer)
        resp = self.client.post(
            reverse("core:invite_teacher") + f"?family_id={self.fam_a.pk}",
            {"email": "x@e.com", "role": "teacher"},
        )
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(Invitation.objects.filter(email="x@e.com").exists())


class TestEnvironmentDetectionTests(TestCase):
    """settings.TESTING decides the password hasher, whether grading runs inline,
    whether the API key is blanked, and (since HH-143) SECURE_SSL_REDIRECT.

    If the detector ever stops matching, none of that fails — the suite just gets
    slower, starts racing SQLite on daemon threads, and a developer whose .env
    carries an ANTHROPIC_API_KEY starts making live billed calls from `manage.py
    test`. So assert it directly; nothing else in 1200-odd tests does."""

    def test_the_runner_is_detected(self):
        from django.conf import settings
        self.assertTrue(
            settings.TESTING,
            "settings.TESTING is False under the test runner: the MD5 hasher, "
            "inline grading and the ANTHROPIC_API_KEY blanking are all off.",
        )

    def test_the_api_key_is_blanked_so_the_suite_cannot_bill(self):
        from django.conf import settings
        self.assertEqual(settings.ANTHROPIC_API_KEY, "")


class AuditContentCommandTests(TestCase):
    """`audit_content` is the repeatable version of clicking through every page.

    Its value is entirely in what it CATCHES, so each test breaks something the
    way it actually broke in production and asserts the audit says so.
    """

    @classmethod
    def setUpTestData(cls):
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
        from students.models import Student
        cls.parent = CustomUser.objects.create_user(
            username="auditor", email="a@e.com", password="pw")
        cls.child = Student.objects.create(parent=cls.parent, first_name="Nia")
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Audit Math", subject="Math", grade_level="G03")
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(
            child=cls.child, curriculum=cls.cur, current_lesson=cls.lesson)

    def _run(self):
        out, err = StringIO(), StringIO()
        try:
            call_command("audit_content", stdout=out, stderr=err)
        except SystemExit:
            pass
        return out.getvalue() + err.getvalue()

    def test_a_clean_setup_reports_no_problems(self):
        self.assertIn("No problems", self._run())

    def test_a_deactivated_placement_is_not_audited(self):
        """The audit must walk what the child can REACH, not what rows exist.

        A deactivated placement on a sibling's curriculum made the audit open
        that sibling's material, get the 404 the permission check is supposed to
        produce, and report it as breakage — turning a correct refusal into a
        red PROBLEM on every run. portal/views.py has filtered is_active since
        HH-149; this walk has to filter it the same way.
        """
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
        from students.models import Student
        from tutor.models import Material

        sibling = Student.objects.create(parent=self.parent, first_name="Rae")
        other = Curriculum.objects.create(
            parent=self.parent, name="Rae Only", subject="Math", grade_level="G07")
        ch = Chapter.objects.create(curriculum=other, number=1, title="One")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=sibling, curriculum=other)
        from tutor.models import LessonBlock
        m = Material.objects.create(
            lesson=lesson, child=sibling, title="Rae's own material",
            skill_type=Material.SKILL_LESSON, status=Material.APPROVED,
            student_intro="hi", student_content="hi", parent_content="hi")
        LessonBlock.objects.create(material=m, order=1,
                                   kind=LessonBlock.KIND_MASTHEAD,
                                   data={"title": "Rae's masthead"})

        # Rae reaches her own material; that page is hers and must still be walked.
        self.assertIn("Rae (#2)         6/6 pages OK", self._run())

        # Now give Nia a DEACTIVATED placement pointing at Rae's curriculum. It
        # must change nothing: Nia's page count stays put and the 404 the
        # permission check would raise is never provoked.
        CurriculumPlacement.objects.create(
            child=self.child, curriculum=other, is_active=False)

        out = self._run()
        self.assertIn("Nia (#1)         5/5 pages OK", out,
                      "the audit opened a page the child cannot reach")
        self.assertIn("No problems", out)

    def test_it_exits_nonzero_when_something_is_broken(self):
        from tutor.models import QuestionSet
        QuestionSet.objects.create(
            lesson=self.lesson, title="Empty set", intro="i", rubric="r")
        with self.assertRaises(SystemExit):
            call_command("audit_content", stdout=StringIO(), stderr=StringIO())

    def test_it_catches_an_answer_choice_posing_as_a_question(self):
        # The EIW Lesson 7 bug: a lettered option from an answer bank standing
        # alone as a question, with nothing for the child to answer.
        from tutor.models import Question, QuestionSet
        qs = QuestionSet.objects.create(
            lesson=self.lesson, title="Choices", intro="i", rubric="r")
        Question.objects.create(question_set=qs, order=1, category="grammar",
                                response_type=Question.TYPE_TEXT,
                                prompt="A. Question Mark (?)")
        self.assertIn("answer CHOICE posing as a question", self._run())

    def test_it_catches_a_question_that_renders_blank(self):
        from tutor.models import Question, QuestionSet
        qs = QuestionSet.objects.create(
            lesson=self.lesson, title="Blank", intro="i", rubric="r")
        Question.objects.create(question_set=qs, order=1, category="grammar",
                                response_type=Question.TYPE_TEXT, prompt="", passage="")
        self.assertIn("renders blank", self._run())

    def test_it_catches_a_matching_answer_the_child_cannot_pick(self):
        # Unwinnable: the correct answer isn't in the pool she taps from.
        import json
        from tutor.models import Question, QuestionSet
        qs = QuestionSet.objects.create(
            lesson=self.lesson, title="Match", intro="i", rubric="r")
        Question.objects.create(
            question_set=qs, order=1, category="grammar",
            response_type=Question.TYPE_MATCHING,
            passage=json.dumps({
                "words": ["Period (.)"],
                "definitions": [{"n": 1, "text": "Interrogative", "word": "Question Mark (?)"}],
            }),
        )
        self.assertIn("expects answers that are not in the pool", self._run())

    def test_it_catches_manga_art_that_is_not_deployed(self):
        from tutor.models import MangaPanel, Material
        m = Material.objects.create(
            lesson=self.lesson, title="Manga", skill_type=Material.SKILL_MANGA,
            student_content="x", parent_content="y", status=Material.APPROVED)
        MangaPanel.objects.create(material=m, order=1, alt="a", caption="c",
                                  image_path="manga/does-not-exist/p1.jpg")
        self.assertIn("not in the deployed static files", self._run())

    def test_it_catches_a_child_with_nowhere_to_go(self):
        from students.models import Student
        Student.objects.create(parent=self.parent, first_name="Stranded")
        self.assertIn("no curriculum placements", self._run())

    def test_a_draft_is_a_note_not_a_problem(self):
        # The approval workflow is not a defect: a parent has simply not approved
        # it yet. Flagging drafts as breakage would make the audit cry wolf and
        # stop being read.
        from tutor.models import MangaPanel, Material
        m = Material.objects.create(
            lesson=self.lesson, title="Pending", skill_type=Material.SKILL_MANGA,
            student_content="x", parent_content="y", status=Material.DRAFT)
        MangaPanel.objects.create(material=m, order=1, alt="a", caption="c", image_path="")
        out = self._run()
        self.assertIn("NOTE", out)
        self.assertIn("has to approve it", out)


class CrossAppActivityTests(TestCase):
    """core.activity.aggregate_activity + current_streak — the foundation (F2) the
    whole-school streak, hours report, and trophy case all read."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = CustomUser.objects.create_user(
            username="act", email="act@e.com", password="pw")
        cls.family = Family.objects.create(name="Act Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, family=cls.family, first_name="Vi", grade_level="G03")

    def _entry(self, subject, day, minutes=None):
        from worklog.models import WorkLogEntry
        return WorkLogEntry.objects.create(
            parent=self.parent, family=self.family, child=self.child,
            subject=subject, date=day, minutes=minutes)

    def test_a_day_shared_across_subjects_counts_once_but_keeps_both_minutes(self):
        from core.activity import aggregate_activity
        today = timezone.localdate()
        self._entry("Math", today, minutes=30)
        self._entry("Reading", today, minutes=15)
        agg = aggregate_activity(self.child, today, today)
        self.assertEqual(agg["days_count"], 1)                 # one distinct day of instruction
        self.assertEqual(agg["total_minutes"], 45)             # but both subjects' minutes
        self.assertEqual(agg["by_subject"]["math"]["minutes"], 30)
        self.assertEqual(agg["by_subject"]["reading"]["minutes"], 15)

    def test_the_spanish_mirror_and_a_lingua_session_never_double_count(self):
        """The load-bearing invariant. The lingua book mirror writes a 'Spanish
        reading' Work Log row (no minutes); the SAME day the child logs listening
        minutes inside lingua. Days must union to one, and Spanish minutes must come
        only from lingua — a mutant that summed the providers' days, or let the
        mirror contribute minutes, fails here."""
        from core.activity import aggregate_activity
        from lingua import profiles
        from lingua.models import Learner, ListeningSession
        today = timezone.localdate()
        self._entry("Math", today, minutes=30)
        self._entry("Spanish reading", today)                  # mirror row, minutes NULL
        learner = Learner.create_for_host_student(self.child.pk, profiles.KIDS_EARLY)
        ListeningSession.objects.create(learner=learner, minutes=15)  # created today
        agg = aggregate_activity(self.child, today, today)
        self.assertEqual(agg["days_count"], 1)                 # math + mirror + listening = 1 day
        self.assertEqual(agg["by_subject"]["spanish"]["minutes"], 15)   # not 0, not 30, not doubled
        self.assertEqual(agg["by_subject"]["spanish"]["days"], {today})
        self.assertEqual(agg["total_minutes"], 45)             # 30 math + 15 spanish; mirror adds 0

    def test_streak_counts_yesterday_when_today_is_empty(self):
        from core.activity import current_streak
        today = timezone.localdate()
        for back in (1, 2, 3):
            self._entry("Math", today - timedelta(days=back), minutes=10)
        self.assertEqual(current_streak(self.child, on=today), 3)   # yesterday still counts
        self._entry("Math", today, minutes=10)
        self.assertEqual(current_streak(self.child, on=today), 4)

    def test_streak_breaks_on_a_gap(self):
        from core.activity import current_streak
        today = timezone.localdate()
        self._entry("Math", today, minutes=10)
        self._entry("Math", today - timedelta(days=1), minutes=10)
        self._entry("Math", today - timedelta(days=3), minutes=10)   # gap at day-2
        self.assertEqual(current_streak(self.child, on=today), 2)

    def test_a_completed_lesson_is_activity_but_a_skip_is_not(self):
        from core.activity import aggregate_activity
        from curricula.models import Chapter, Lesson, LessonProgress
        curr = Curriculum.objects.create(
            parent=self.parent, family=self.family, name="Math 3A", subject="Math")
        ch = Chapter.objects.create(curriculum=curr, number=1, title="One")
        done = Lesson.objects.create(chapter=ch, order=1, title="L1")
        skipped = Lesson.objects.create(chapter=ch, order=2, title="L2")
        LessonProgress.objects.create(
            child=self.child, lesson=done, status=LessonProgress.COMPLETED)
        sk = LessonProgress.objects.create(
            child=self.child, lesson=skipped, status=LessonProgress.SKIPPED)
        # Backdate the skip to a DIFFERENT day. Both rows share today via auto_now_add,
        # so counting the skip would only show as a SECOND day if it lands elsewhere —
        # otherwise the exclusion can't be observed and the test can't kill the mutant.
        LessonProgress.objects.filter(pk=sk.pk).update(
            created_at=sk.created_at - timedelta(days=1))
        agg = aggregate_activity(self.child)                   # unbounded
        # Only today (the completed lesson). A mutant that counts skips would add
        # yesterday, making this set — and days_count — 2.
        self.assertEqual(agg["by_subject"]["math"]["days"], {timezone.localdate()})
        self.assertEqual(agg["days_count"], 1)

    def test_aggregating_never_provisions_a_lingua_learner(self):
        """Read-only invariant: reporting on a child who has never done Spanish must
        not create a Learner row (a provisioning getter would)."""
        from core.activity import aggregate_activity
        from lingua.models import Learner
        self._entry("Math", timezone.localdate(), minutes=20)
        aggregate_activity(self.child)
        self.assertEqual(Learner.objects.filter(host_student_id=self.child.pk).count(), 0)

    @override_settings(ACTIVITY_SIGNAL_PROVIDERS=[
        "worklog.activity.WorkLogSignals",
        "does.not.Exist",                                      # bogus path must be skipped
    ])
    def test_runs_without_lingua_and_survives_a_bad_provider(self):
        """Extractability + resilience: with the lingua provider absent and a bogus
        dotted path in the list, the aggregator still returns the host signals and
        does NOT reach into lingua."""
        from core.activity import aggregate_activity
        from lingua import profiles
        from lingua.models import Learner, ListeningSession
        today = timezone.localdate()
        self._entry("Math", today, minutes=30)
        learner = Learner.create_for_host_student(self.child.pk, profiles.KIDS_EARLY)
        ListeningSession.objects.create(learner=learner, minutes=99)
        agg = aggregate_activity(self.child, today, today)
        self.assertEqual(agg["by_subject"]["math"]["minutes"], 30)   # host signal present
        self.assertNotIn("spanish", agg["by_subject"])               # lingua not consulted
