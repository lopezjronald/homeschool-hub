from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import Client, TestCase
from django.urls import reverse

from curricula.models import Curriculum
from students.models import Student

from .forms import AssignmentForm, AssignmentStatusForm
from .models import Assignment

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
