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
        form = ResourceLinkForm(data={
            "url": "https://example.com", "label": "Test", "link_type": "resource",
        })
        self.assertTrue(form.is_valid())

    def test_valid_http_url(self):
        form = ResourceLinkForm(data={
            "url": "http://example.com", "label": "Test", "link_type": "resource",
        })
        self.assertTrue(form.is_valid())

    def test_invalid_ftp_url(self):
        form = ResourceLinkForm(data={
            "url": "ftp://example.com", "label": "Test", "link_type": "resource",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("url", form.errors)

    def test_invalid_javascript_url(self):
        form = ResourceLinkForm(data={
            "url": "javascript:alert(1)", "label": "Test", "link_type": "resource",
        })
        self.assertFalse(form.is_valid())

    def test_label_required(self):
        form = ResourceLinkForm(data={
            "url": "https://example.com", "label": "", "link_type": "resource",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("label", form.errors)


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
            {"url": "https://youtube.com/watch?v=123", "label": "Math Video", "link_type": "resource"},
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

    def test_teacher_can_access_create_page(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_create"))
        self.assertEqual(response.status_code, 200)

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

    def test_teacher_list_shows_create_but_hides_row_actions(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertContains(response, "Add Assignment")
        # Parent-created row: no Edit or Delete
        self.assertNotContains(response, "btn-outline-secondary")
        self.assertNotContains(response, "btn-outline-danger")

    def test_teacher_detail_hides_edit_controls(self):
        self.client.login(username="ta_teacher", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.assignment.pk])
        )
        self.assertNotContains(response, "Student Update Link")
        self.assertNotContains(response, "btn-danger\">Delete")


class TeacherAssignmentCreationTests(TestCase):
    """Tests for HH-70: teacher assignment creation, editing, and audit."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent_user = User.objects.create_user(
            username="tc_parent", email="tc_parent@test.com", password="testpass123",
        )
        cls.teacher_user = User.objects.create_user(
            username="tc_teacher", email="tc_teacher@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="TC Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        cls.child = Student.objects.create(
            parent=cls.parent_user, first_name="TCChild", grade_level="G03",
            family=cls.family,
        )
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent_user, name="TC Math", subject="Math",
            family=cls.family,
        )
        cls.parent_assignment = Assignment.objects.create(
            parent=cls.parent_user,
            child=cls.child,
            curriculum=cls.curriculum,
            title="Parent Assignment",
            due_date=date.today(),
            family=cls.family,
            source=Assignment.SOURCE_PARENT,
            created_by=cls.parent_user,
        )

    def test_teacher_can_create_assignment_for_assigned_family(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_create"),
            {
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Teacher Created",
                "due_date": date.today().isoformat(),
                "status": Assignment.PENDING,
            },
        )
        self.assertRedirects(response, reverse("assignments:assignment_list"))
        assignment = Assignment.objects.get(title="Teacher Created")
        self.assertEqual(assignment.source, Assignment.SOURCE_TEACHER)
        self.assertEqual(assignment.created_by, self.teacher_user)
        self.assertEqual(assignment.family, self.family)
        self.assertEqual(assignment.parent, self.parent_user)

    def test_teacher_cannot_create_for_unassigned_family(self):
        from core.models import Family, FamilyMembership

        other_parent = User.objects.create_user(
            username="tc_other_parent", email="tc_other@test.com",
            password="testpass123",
        )
        other_family = Family.objects.create(name="Other TC Family")
        FamilyMembership.objects.create(
            user=other_parent, family=other_family, role="parent",
        )
        other_child = Student.objects.create(
            parent=other_parent, first_name="OtherChild", grade_level="G02",
            family=other_family,
        )
        other_curriculum = Curriculum.objects.create(
            parent=other_parent, name="Other Math", subject="Math",
            family=other_family,
        )
        # Teacher tries to force-select unassigned family via GET param
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_create")
            + f"?family={other_family.pk}",
            {
                "child": other_child.pk,
                "curriculum": other_curriculum.pk,
                "title": "Sneaky Assignment",
                "due_date": date.today().isoformat(),
                "status": Assignment.PENDING,
            },
        )
        # Form rejects — child/curriculum not in teacher's allowed querysets
        self.assertEqual(response.status_code, 200)  # re-renders form
        self.assertFalse(
            Assignment.objects.filter(title="Sneaky Assignment").exists()
        )

    def test_teacher_can_edit_own_assignment(self):
        teacher_assignment = Assignment.objects.create(
            parent=self.parent_user,
            child=self.child,
            curriculum=self.curriculum,
            title="Teacher Editable",
            due_date=date.today(),
            family=self.family,
            source=Assignment.SOURCE_TEACHER,
            created_by=self.teacher_user,
        )
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:assignment_update", args=[teacher_assignment.pk]),
            {
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Teacher Updated",
                "due_date": date.today().isoformat(),
                "status": Assignment.IN_PROGRESS,
            },
        )
        self.assertRedirects(response, reverse("assignments:assignment_list"))
        teacher_assignment.refresh_from_db()
        self.assertEqual(teacher_assignment.title, "Teacher Updated")

    def test_teacher_cannot_edit_parent_created_assignment(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_update", args=[self.parent_assignment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_any_assignment(self):
        teacher_assignment = Assignment.objects.create(
            parent=self.parent_user,
            child=self.child,
            curriculum=self.curriculum,
            title="Teacher No Delete",
            due_date=date.today(),
            family=self.family,
            source=Assignment.SOURCE_TEACHER,
            created_by=self.teacher_user,
        )
        self.client.login(username="tc_teacher", password="testpass123")
        # Cannot delete own teacher-created assignment
        response = self.client.get(
            reverse("assignments:assignment_delete", args=[teacher_assignment.pk])
        )
        self.assertEqual(response.status_code, 404)
        # Cannot delete parent-created assignment
        response = self.client.get(
            reverse("assignments:assignment_delete", args=[self.parent_assignment.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_parent_can_still_edit_and_delete(self):
        deletable = Assignment.objects.create(
            parent=self.parent_user,
            child=self.child,
            curriculum=self.curriculum,
            title="Parent Deletable",
            due_date=date.today(),
            family=self.family,
            source=Assignment.SOURCE_PARENT,
            created_by=self.parent_user,
        )
        self.client.login(username="tc_parent", password="testpass123")
        # Parent can edit
        response = self.client.post(
            reverse("assignments:assignment_update", args=[deletable.pk]),
            {
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Parent Updated",
                "due_date": date.today().isoformat(),
                "status": Assignment.PENDING,
            },
        )
        self.assertRedirects(response, reverse("assignments:assignment_list"))
        deletable.refresh_from_db()
        self.assertEqual(deletable.title, "Parent Updated")
        # Parent can delete
        response = self.client.post(
            reverse("assignments:assignment_delete", args=[deletable.pk])
        )
        self.assertRedirects(response, reverse("assignments:assignment_list"))
        self.assertFalse(
            Assignment.objects.filter(pk=deletable.pk).exists()
        )

    def test_assignment_shows_correct_source_and_created_by(self):
        self.client.login(username="tc_teacher", password="testpass123")
        self.client.post(
            reverse("assignments:assignment_create"),
            {
                "child": self.child.pk,
                "curriculum": self.curriculum.pk,
                "title": "Audit Trail Test",
                "due_date": date.today().isoformat(),
                "status": Assignment.PENDING,
            },
        )
        assignment = Assignment.objects.get(title="Audit Trail Test")
        self.assertEqual(assignment.source, Assignment.SOURCE_TEACHER)
        self.assertEqual(assignment.created_by, self.teacher_user)
        # Detail page shows teacher attribution
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[assignment.pk])
        )
        self.assertContains(response, "(Teacher)")


class AssessmentLinkTests(TestCase):
    """Tests for HH-71: assessment links with typed links, labels, and windows."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent_user = User.objects.create_user(
            username="al_parent", email="al_parent@test.com", password="testpass123",
        )
        cls.teacher_user = User.objects.create_user(
            username="al_teacher", email="al_teacher@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="AL Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        cls.child = Student.objects.create(
            parent=cls.parent_user, first_name="ALChild", grade_level="G03",
            family=cls.family,
        )
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent_user, name="AL Math", subject="Math",
            family=cls.family,
        )
        cls.parent_assignment = Assignment.objects.create(
            parent=cls.parent_user,
            child=cls.child,
            curriculum=cls.curriculum,
            title="Parent Assign",
            due_date=date.today(),
            family=cls.family,
            source=Assignment.SOURCE_PARENT,
            created_by=cls.parent_user,
        )
        cls.teacher_assignment = Assignment.objects.create(
            parent=cls.parent_user,
            child=cls.child,
            curriculum=cls.curriculum,
            title="Teacher Assign",
            due_date=date.today(),
            family=cls.family,
            source=Assignment.SOURCE_TEACHER,
            created_by=cls.teacher_user,
        )

    # -- Model tests --

    def test_link_type_default_is_resource(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.parent_assignment,
            url="https://example.com",
            label="Test",
        )
        self.assertEqual(link.link_type, AssignmentResourceLink.TYPE_RESOURCE)

    def test_window_display_both_dates(self):
        link = AssignmentResourceLink(
            window_start=date(2026, 3, 1), window_end=date(2026, 3, 15),
        )
        self.assertIn("2026-03-01", link.window_display)
        self.assertIn("2026-03-15", link.window_display)
        self.assertTrue(link.window_display.startswith("Window:"))

    def test_window_display_start_only(self):
        link = AssignmentResourceLink(window_start=date(2026, 3, 1))
        self.assertEqual(link.window_display, "Window starts: 2026-03-01")

    def test_window_display_end_only(self):
        link = AssignmentResourceLink(window_end=date(2026, 3, 15))
        self.assertEqual(link.window_display, "Window ends: 2026-03-15")

    def test_window_display_no_dates(self):
        link = AssignmentResourceLink()
        self.assertEqual(link.window_display, "")

    # -- Form tests --

    def test_form_rejects_whitespace_only_label(self):
        form = ResourceLinkForm(data={
            "url": "https://example.com", "label": "   ", "link_type": "resource",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("label", form.errors)

    def test_form_rejects_invalid_link_type(self):
        form = ResourceLinkForm(data={
            "url": "https://example.com", "label": "Test", "link_type": "invalid",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("link_type", form.errors)

    def test_form_window_start_after_end_rejected(self):
        form = ResourceLinkForm(data={
            "url": "https://example.com",
            "label": "Test",
            "link_type": "assessment",
            "window_start": "2026-03-15",
            "window_end": "2026-03-01",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_window_dates_individually_optional(self):
        # Only start date
        form = ResourceLinkForm(data={
            "url": "https://example.com",
            "label": "Test",
            "link_type": "assessment",
            "window_start": "2026-03-01",
        })
        self.assertTrue(form.is_valid())
        # Only end date
        form = ResourceLinkForm(data={
            "url": "https://example.com",
            "label": "Test",
            "link_type": "assessment",
            "window_end": "2026-03-15",
        })
        self.assertTrue(form.is_valid())

    def test_form_window_both_dates_valid(self):
        form = ResourceLinkForm(data={
            "url": "https://example.com",
            "label": "Test",
            "link_type": "assessment",
            "window_start": "2026-03-01",
            "window_end": "2026-03-15",
        })
        self.assertTrue(form.is_valid())

    # -- View / permission tests --

    def test_add_assessment_link_success(self):
        self.client.login(username="al_parent", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_add", args=[self.parent_assignment.pk]),
            {
                "url": "https://caaspp.cde.ca.gov",
                "label": "CAASPP ELA",
                "link_type": "assessment",
                "window_start": "2026-03-01",
                "window_end": "2026-03-15",
            },
        )
        self.assertRedirects(
            response,
            reverse("assignments:assignment_detail", args=[self.parent_assignment.pk]),
        )
        link = AssignmentResourceLink.objects.get(label="CAASPP ELA")
        self.assertEqual(link.link_type, AssignmentResourceLink.TYPE_ASSESSMENT)
        self.assertEqual(link.window_start, date(2026, 3, 1))
        self.assertEqual(link.window_end, date(2026, 3, 15))

    def test_teacher_can_add_link_to_own_assignment(self):
        self.client.login(username="al_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_add", args=[self.teacher_assignment.pk]),
            {
                "url": "https://i-ready.com/test",
                "label": "i-Ready Diagnostic",
                "link_type": "assessment",
            },
        )
        self.assertRedirects(
            response,
            reverse("assignments:assignment_detail", args=[self.teacher_assignment.pk]),
        )
        self.assertTrue(
            AssignmentResourceLink.objects.filter(
                assignment=self.teacher_assignment, label="i-Ready Diagnostic",
            ).exists()
        )

    def test_teacher_cannot_add_link_to_parent_assignment(self):
        self.client.login(username="al_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_add", args=[self.parent_assignment.pk]),
            {
                "url": "https://example.com",
                "label": "Sneaky",
                "link_type": "resource",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_can_delete_link_on_own_assignment(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.teacher_assignment,
            url="https://example.com",
            label="Deletable",
            link_type=AssignmentResourceLink.TYPE_RESOURCE,
        )
        self.client.login(username="al_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_delete", args=[link.pk])
        )
        self.assertRedirects(
            response,
            reverse("assignments:assignment_detail", args=[self.teacher_assignment.pk]),
        )
        self.assertFalse(AssignmentResourceLink.objects.filter(pk=link.pk).exists())

    def test_teacher_cannot_delete_link_on_parent_assignment(self):
        link = AssignmentResourceLink.objects.create(
            assignment=self.parent_assignment,
            url="https://example.com",
            label="Protected",
            link_type=AssignmentResourceLink.TYPE_RESOURCE,
        )
        self.client.login(username="al_teacher", password="testpass123")
        response = self.client.post(
            reverse("assignments:resource_link_delete", args=[link.pk])
        )
        self.assertEqual(response.status_code, 404)

    # -- Template tests --

    def test_detail_groups_assessments_and_resources(self):
        AssignmentResourceLink.objects.create(
            assignment=self.parent_assignment,
            url="https://caaspp.cde.ca.gov",
            label="CAASPP",
            link_type=AssignmentResourceLink.TYPE_ASSESSMENT,
        )
        AssignmentResourceLink.objects.create(
            assignment=self.parent_assignment,
            url="https://youtube.com/math",
            label="Math Video",
            link_type=AssignmentResourceLink.TYPE_RESOURCE,
        )
        self.client.login(username="al_parent", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.parent_assignment.pk])
        )
        content = response.content.decode()
        # Assessments section appears before Resources section
        assess_pos = content.index("Take Test: CAASPP")
        resource_pos = content.index("Math Video")
        self.assertLess(assess_pos, resource_pos)
        # Assessment uses button style
        self.assertContains(response, "Take Test: CAASPP")
        self.assertContains(response, "btn-outline-primary")

    def test_student_page_groups_links(self):
        AssignmentResourceLink.objects.create(
            assignment=self.parent_assignment,
            url="https://caaspp.cde.ca.gov",
            label="CAASPP",
            link_type=AssignmentResourceLink.TYPE_ASSESSMENT,
        )
        AssignmentResourceLink.objects.create(
            assignment=self.parent_assignment,
            url="https://youtube.com/math",
            label="Math Video",
            link_type=AssignmentResourceLink.TYPE_RESOURCE,
        )
        token = self.parent_assignment.get_student_status_token()
        url = reverse("assignments:assignment_student_update", args=[token])
        response = self.client.get(url)
        self.assertContains(response, "Assessments")
        self.assertContains(response, "Take Test: CAASPP")
        self.assertContains(response, "Resources")
        self.assertContains(response, "Math Video")

    def test_assessment_shows_window_dates(self):
        AssignmentResourceLink.objects.create(
            assignment=self.parent_assignment,
            url="https://caaspp.cde.ca.gov",
            label="CAASPP",
            link_type=AssignmentResourceLink.TYPE_ASSESSMENT,
            window_start=date(2026, 3, 1),
            window_end=date(2026, 3, 15),
        )
        self.client.login(username="al_parent", password="testpass123")
        response = self.client.get(
            reverse("assignments:assignment_detail", args=[self.parent_assignment.pk])
        )
        self.assertContains(response, "Window:")
        self.assertContains(response, "2026-03-01")
        self.assertContains(response, "2026-03-15")
