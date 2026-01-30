from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import Client, TestCase
from django.urls import reverse

from curricula.models import Curriculum
from students.models import Student

from .forms import AssignmentForm, AssignmentStatusForm, ResourceLinkForm
from .models import Assignment, AssignmentResourceLink

User = get_user_model()


class AssignmentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="testpass123"
        )
        self.child = Student.objects.create(
            parent=self.user,
            first_name="Alice",
            grade_level="G03",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user,
            name="Math 3A",
            subject="Math",
        )

    def test_assignment_str(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Chapter 1 Review",
            due_date=date.today(),
        )
        self.assertEqual(str(assignment), "Chapter 1 Review")

    def test_is_overdue_true_when_past_and_not_complete(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Old Assignment",
            due_date=date.today() - timedelta(days=1),
            status=Assignment.PENDING,
        )
        self.assertTrue(assignment.is_overdue)

    def test_is_overdue_false_when_complete(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Done Assignment",
            due_date=date.today() - timedelta(days=1),
            status=Assignment.COMPLETE,
        )
        self.assertFalse(assignment.is_overdue)

    def test_is_overdue_false_when_future(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Future Assignment",
            due_date=date.today() + timedelta(days=1),
            status=Assignment.PENDING,
        )
        self.assertFalse(assignment.is_overdue)

    def test_default_status_is_pending(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="New Assignment",
            due_date=date.today(),
        )
        self.assertEqual(assignment.status, Assignment.PENDING)

    def test_get_student_status_token(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
        )
        token = assignment.get_student_status_token()
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_get_from_student_token_valid(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
        )
        token = assignment.get_student_status_token()
        retrieved = Assignment.get_from_student_token(token)
        self.assertEqual(retrieved, assignment)

    def test_get_from_student_token_invalid(self):
        retrieved = Assignment.get_from_student_token("invalid-token")
        self.assertIsNone(retrieved)

    def test_get_from_student_token_expired(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
        )
        token = assignment.get_student_status_token()
        # Test with max_age=0 to simulate expiration
        retrieved = Assignment.get_from_student_token(token, max_age=0)
        self.assertIsNone(retrieved)

    def test_get_student_status_url(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
        )
        url = assignment.get_student_status_url()
        self.assertIn("/assignments/s/", url)


class AssignmentFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="parent2", email="parent2@test.com", password="testpass123"
        )
        self.child = Student.objects.create(
            parent=self.user,
            first_name="Alice",
            grade_level="G03",
        )
        self.other_child = Student.objects.create(
            parent=self.other_user,
            first_name="Bob",
            grade_level="G04",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user,
            name="Math 3A",
            subject="Math",
        )
        self.other_curriculum = Curriculum.objects.create(
            parent=self.other_user,
            name="Science 4",
            subject="Science",
        )

    def test_dropdown_filters_children_to_user(self):
        form = AssignmentForm(user=self.user)
        child_queryset = form.fields["child"].queryset
        self.assertIn(self.child, child_queryset)
        self.assertNotIn(self.other_child, child_queryset)

    def test_dropdown_filters_curricula_to_user(self):
        form = AssignmentForm(user=self.user)
        curriculum_queryset = form.fields["curriculum"].queryset
        self.assertIn(self.curriculum, curriculum_queryset)
        self.assertNotIn(self.other_curriculum, curriculum_queryset)

    def test_due_date_cannot_be_past_on_create(self):
        form = AssignmentForm(
            data={
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Test",
                "due_date": date.today() - timedelta(days=1),
                "status": Assignment.PENDING,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)

    def test_due_date_can_be_past_on_update(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Existing",
            due_date=date.today() - timedelta(days=5),
            status=Assignment.PENDING,
        )
        form = AssignmentForm(
            data={
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Updated",
                "due_date": date.today() - timedelta(days=3),
                "status": Assignment.IN_PROGRESS,
            },
            instance=assignment,
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_rejects_other_users_child(self):
        form = AssignmentForm(
            data={
                "child": self.other_child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Test",
                "due_date": date.today(),
                "status": Assignment.PENDING,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("child", form.errors)

    def test_rejects_other_users_curriculum(self):
        form = AssignmentForm(
            data={
                "child": self.child.pk,
                "curriculum": self.other_curriculum.pk,
                "title": "Test",
                "due_date": date.today(),
                "status": Assignment.PENDING,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("curriculum", form.errors)


class AssignmentStatusFormTests(TestCase):
    def test_valid_status_choices(self):
        for status, _ in Assignment.STATUS_CHOICES:
            form = AssignmentStatusForm(data={"status": status})
            self.assertTrue(form.is_valid())

    def test_invalid_status(self):
        form = AssignmentStatusForm(data={"status": "invalid"})
        self.assertFalse(form.is_valid())


class AssignmentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="parent2", email="parent2@test.com", password="testpass123"
        )
        self.child = Student.objects.create(
            parent=self.user,
            first_name="Alice",
            grade_level="G03",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user,
            name="Math 3A",
            subject="Math",
        )
        self.assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_list_shows_only_users_assignments(self):
        other_child = Student.objects.create(
            parent=self.other_user,
            first_name="Bob",
            grade_level="G04",
        )
        other_curriculum = Curriculum.objects.create(
            parent=self.other_user,
            name="Science",
            subject="Science",
        )
        other_assignment = Assignment.objects.create(
            parent=self.other_user,
            child=other_child,
            curriculum=other_curriculum,
            title="Other Assignment",
            due_date=date.today(),
        )

        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Assignment")
        self.assertNotContains(response, "Other Assignment")

    def test_detail_returns_404_for_other_user(self):
        self.client.login(username="parent2", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_update_returns_404_for_other_user(self):
        self.client.login(username="parent2", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_update", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_returns_404_for_other_user(self):
        self.client.login(username="parent2", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_delete", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_create_shows_empty_state_without_children(self):
        user_no_children = User.objects.create_user(
            username="parent3", email="parent3@test.com", password="testpass123"
        )
        Curriculum.objects.create(
            parent=user_no_children,
            name="Curriculum",
            subject="Subject",
        )
        self.client.login(username="parent3", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "add a child first")

    def test_create_shows_empty_state_without_curricula(self):
        user_no_curricula = User.objects.create_user(
            username="parent4", email="parent4@test.com", password="testpass123"
        )
        Student.objects.create(
            parent=user_no_curricula,
            first_name="Child",
            grade_level="G01",
        )
        self.client.login(username="parent4", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "add a curriculum first")

    def test_create_assignment_success(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_create"),
            {
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "New Assignment",
                "due_date": date.today(),
                "status": Assignment.PENDING,
            },
        )
        self.assertRedirects(response, reverse("assignments:assignment_list"))
        self.assertTrue(Assignment.objects.filter(title="New Assignment").exists())

    def test_update_assignment_success(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_update", args=[self.assignment.pk]),
            {
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Updated Title",
                "due_date": date.today(),
                "status": Assignment.IN_PROGRESS,
            },
        )
        self.assertRedirects(response, reverse("assignments:assignment_list"))
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.title, "Updated Title")
        self.assertEqual(self.assignment.status, Assignment.IN_PROGRESS)

    def test_delete_assignment_success(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_delete", args=[self.assignment.pk])
        )
        self.assertRedirects(response, reverse("assignments:assignment_list"))
        self.assertFalse(Assignment.objects.filter(pk=self.assignment.pk).exists())

    def test_detail_shows_student_link(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Update Link")
        self.assertContains(response, "/assignments/s/")


class StudentUpdateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="testpass123"
        )
        self.child = Student.objects.create(
            parent=self.user,
            first_name="Alice",
            grade_level="G03",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user,
            name="Math 3A",
            subject="Math",
        )
        self.assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
            status=Assignment.PENDING,
        )

    def test_student_update_no_login_required(self):
        token = self.assignment.get_student_status_token()
        url = reverse("assignments:assignment_student_update", args=[token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Assignment")

    def test_student_update_shows_form(self):
        token = self.assignment.get_student_status_token()
        url = reverse("assignments:assignment_student_update", args=[token])
        response = self.client.get(url)
        self.assertContains(response, "Update Status")

    def test_student_update_post_success(self):
        token = self.assignment.get_student_status_token()
        url = reverse("assignments:assignment_student_update", args=[token])
        response = self.client.post(url, {"status": Assignment.SUBMITTED})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status Updated")
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, Assignment.SUBMITTED)

    def test_student_update_invalid_token(self):
        url = reverse("assignments:assignment_student_update", args=["invalid-token"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "invalid or has expired")

    def test_student_update_all_statuses(self):
        token = self.assignment.get_student_status_token()
        url = reverse("assignments:assignment_student_update", args=[token])

        for status, _ in Assignment.STATUS_CHOICES:
            response = self.client.post(url, {"status": status})
            self.assertEqual(response.status_code, 200)
            self.assignment.refresh_from_db()
            self.assertEqual(self.assignment.status, status)


class CurriculumAssignmentCountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="testpass123"
        )
        self.child = Student.objects.create(
            parent=self.user,
            first_name="Alice",
            grade_level="G03",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user,
            name="Math 3A",
            subject="Math",
        )

    def test_curriculum_assignment_count(self):
        self.assertEqual(self.curriculum.get_related_assignments_count(), 0)

        Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Assignment 1",
            due_date=date.today(),
        )
        Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Assignment 2",
            due_date=date.today(),
        )

        self.assertEqual(self.curriculum.get_related_assignments_count(), 2)


class AssignmentResourceLinkModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="testpass123"
        )
        self.child = Student.objects.create(
            parent=self.user,
            first_name="Alice",
            grade_level="G03",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user,
            name="Math 3A",
            subject="Math",
        )
        self.assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
        )

    def test_str_with_label(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
            label="Example Site",
        )
        self.assertEqual(str(link), "Example Site")

    def test_str_without_label(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
        )
        self.assertEqual(str(link), "https://example.com")

    def test_display_label_with_label(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
            label="Example Site",
        )
        self.assertEqual(link.display_label, "Example Site")

    def test_display_label_without_label(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
        )
        self.assertEqual(link.display_label, "https://example.com")

    def test_cascade_delete(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
        )
        link_pk = link.pk
        self.assignment.delete()
        self.assertFalse(AssignmentResourceLink.objects.filter(pk=link_pk).exists())


class ResourceLinkFormTests(TestCase):
    def test_valid_https_url(self):
        form = ResourceLinkForm(data={"url": "https://example.com", "label": "Test"})
        self.assertTrue(form.is_valid())

    def test_valid_http_url(self):
        form = ResourceLinkForm(data={"url": "http://example.com", "label": ""})
        self.assertTrue(form.is_valid())

    def test_invalid_ftp_url(self):
        form = ResourceLinkForm(data={"url": "ftp://example.com", "label": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("url", form.errors)

    def test_invalid_javascript_url(self):
        form = ResourceLinkForm(data={"url": "javascript:alert(1)", "label": ""})
        self.assertFalse(form.is_valid())

    def test_label_optional(self):
        form = ResourceLinkForm(data={"url": "https://example.com"})
        self.assertTrue(form.is_valid())


class ResourceLinkViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="parent1", email="parent1@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="parent2", email="parent2@test.com", password="testpass123"
        )
        self.child = Student.objects.create(
            parent=self.user,
            first_name="Alice",
            grade_level="G03",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user,
            name="Math 3A",
            subject="Math",
        )
        self.assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Test Assignment",
            due_date=date.today(),
        )

    def test_add_resource_link_success(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_add", args=[self.assignment.pk]),
            {"url": "https://youtube.com/watch?v=123", "label": "Math Video"},
        )
        self.assertRedirects(
            response,
            reverse("assignments:assignment_detail", args=[self.assignment.pk]),
        )
        self.assertTrue(
            AssignmentResourceLink.objects.filter(
                assignment=self.assignment, label="Math Video"
            ).exists()
        )

    def test_add_resource_link_requires_login(self):
        response = self.client.post(
            reverse("assignments:resource_link_add", args=[self.assignment.pk]),
            {"url": "https://example.com", "label": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_add_resource_link_returns_404_for_other_user(self):
        self.client.login(username="parent2", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_add", args=[self.assignment.pk]),
            {"url": "https://example.com", "label": ""},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_resource_link_success(self):
        self.client.login(username="parent1", password="testpass123")
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
            label="Test",
        )
        response = self.client.post(
            reverse("assignments:resource_link_delete", args=[link.pk])
        )
        self.assertRedirects(
            response,
            reverse("assignments:assignment_detail", args=[self.assignment.pk]),
        )
        self.assertFalse(AssignmentResourceLink.objects.filter(pk=link.pk).exists())

    def test_delete_resource_link_returns_404_for_other_user(self):
        self.client.login(username="parent2", password="testpass123")
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
            label="Test",
        )
        response = self.client.post(
            reverse("assignments:resource_link_delete", args=[link.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_shows_resources(self):
        self.client.login(username="parent1", password="testpass123")
        AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://youtube.com/video",
            label="Video Tutorial",
        )
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Video Tutorial")
        self.assertContains(response, "https://youtube.com/video")

    def test_student_view_shows_resources(self):
        AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://youtube.com/video",
            label="Video Tutorial",
        )
        token = self.assignment.get_student_status_token()
        url = reverse("assignments:assignment_student_update", args=[token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Video Tutorial")
        self.assertContains(response, "https://youtube.com/video")


class TeacherAssignmentViewTests(TestCase):
    """Tests that teachers can view but not create/edit/delete assignments."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent_user = User.objects.create_user(
            username="ta_parent", email="ta_parent@test.com", password="testpass123",
        )
        cls.teacher_user = User.objects.create_user(
            username="ta_teacher", email="ta_teacher@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Teacher Assign Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        cls.child = Student.objects.create(
            parent=cls.parent_user, first_name="FamChild", grade_level="G03",
            family=cls.family,
        )
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent_user, name="Family Math", subject="Math",
            family=cls.family,
        )
        cls.assignment = Assignment.objects.create(
            parent=cls.parent_user,
            child=cls.child,
            curriculum=cls.curriculum,
            title="Family Assignment",
            due_date=date.today(),
            family=cls.family,
        )

    def test_teacher_can_list_assignments(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Family Assignment")

    def test_teacher_can_view_assignment_detail(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_teacher_cannot_create_assignment(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_create"))
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_update_assignment(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_update", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_assignment(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_delete", args=[self.assignment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_add_resource_link(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_add", args=[self.assignment.pk]),
            {"url": "https://example.com", "label": "Test"},
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_resource_link(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.assignment,
            url="https://example.com",
            label="Test",
        )
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_delete", args=[link.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_list_hides_edit_buttons(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertNotContains(response, "Add Assignment")
        self.assertNotContains(response, "btn-outline-danger")

    def test_teacher_detail_hides_edit_controls(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment.pk])
        )
        self.assertNotContains(response, "Student Update Link")
        self.assertNotContains(response, "btn-danger\">Delete")
