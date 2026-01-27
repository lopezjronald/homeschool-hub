from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from curricula.models import Curriculum
from students.models import Student

from .forms import AssignmentForm
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

    def test_is_overdue_true_when_past_and_not_completed(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Old Assignment",
            due_date=date.today() - timedelta(days=1),
            status=Assignment.NOT_STARTED,
        )
        self.assertTrue(assignment.is_overdue)

    def test_is_overdue_false_when_completed(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Done Assignment",
            due_date=date.today() - timedelta(days=1),
            status=Assignment.COMPLETED,
        )
        self.assertFalse(assignment.is_overdue)

    def test_is_overdue_false_when_future(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="Future Assignment",
            due_date=date.today() + timedelta(days=1),
            status=Assignment.NOT_STARTED,
        )
        self.assertFalse(assignment.is_overdue)

    def test_default_status_is_not_started(self):
        assignment = Assignment.objects.create(
            parent=self.user,
            child=self.child,
            curriculum=self.curriculum,
            title="New Assignment",
            due_date=date.today(),
        )
        self.assertEqual(assignment.status, Assignment.NOT_STARTED)


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
                "status": Assignment.NOT_STARTED,
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
            status=Assignment.NOT_STARTED,
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
                "status": Assignment.NOT_STARTED,
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
                "status": Assignment.NOT_STARTED,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("curriculum", form.errors)


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
                "status": Assignment.NOT_STARTED,
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
