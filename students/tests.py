from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Student

User = get_user_model()


class StudentModelTest(TestCase):
    """Tests for the Student model."""

    def setUp(self):
        self.parent = User.objects.create_user(
            username="parent1",
            email="parent1@example.com",
            password="testpass123",
            is_active=True,
        )

    def test_create_student(self):
        """Student can be created with required fields."""
        student = Student.objects.create(
            parent=self.parent,
            first_name="Alice",
            grade_level="G03",
        )
        self.assertEqual(student.first_name, "Alice")
        self.assertEqual(student.parent, self.parent)
        self.assertEqual(str(student), "Alice")

    def test_student_full_name(self):
        """get_full_name returns first + last name."""
        student = Student.objects.create(
            parent=self.parent,
            first_name="Bob",
            last_name="Smith",
            grade_level="G05",
        )
        self.assertEqual(student.get_full_name(), "Bob Smith")
        self.assertEqual(str(student), "Bob Smith")


class StudentViewsTest(TestCase):
    """Tests for student CRUD views."""

    def setUp(self):
        self.client = Client()
        self.parent1 = User.objects.create_user(
            username="parent1",
            email="parent1@example.com",
            password="testpass123",
            is_active=True,
        )
        self.parent2 = User.objects.create_user(
            username="parent2",
            email="parent2@example.com",
            password="testpass456",
            is_active=True,
        )
        self.student1 = Student.objects.create(
            parent=self.parent1,
            first_name="Child1",
            grade_level="G01",
        )
        self.student2 = Student.objects.create(
            parent=self.parent2,
            first_name="Child2",
            grade_level="G02",
        )

    def test_list_requires_login(self):
        """Student list redirects to login if not authenticated."""
        response = self.client.get(reverse("students:student_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_list_shows_only_own_children(self):
        """Parent sees only their own children in the list."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(reverse("students:student_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Child1")
        self.assertNotContains(response, "Child2")

    def test_detail_requires_login(self):
        """Student detail redirects to login if not authenticated."""
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student1.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_detail_returns_404_for_non_owner(self):
        """Parent cannot view another parent's child (404)."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student2.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_shows_own_child(self):
        """Parent can view their own child's details."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Child1")

    def test_update_returns_404_for_non_owner(self):
        """Parent cannot edit another parent's child (404)."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("students:student_update", kwargs={"pk": self.student2.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_returns_404_for_non_owner(self):
        """Parent cannot delete another parent's child (404)."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("students:student_delete", kwargs={"pk": self.student2.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_create_requires_login(self):
        """Create view redirects to login if not authenticated."""
        response = self.client.get(reverse("students:student_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_student_success(self):
        """Parent can create a new child."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("students:student_create"),
            data={
                "first_name": "NewChild",
                "last_name": "",
                "grade_level": "K",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Student.objects.filter(first_name="NewChild", parent=self.parent1).exists()
        )

    def test_update_student_success(self):
        """Parent can update their own child."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("students:student_update", kwargs={"pk": self.student1.pk}),
            data={
                "first_name": "UpdatedName",
                "last_name": "",
                "grade_level": "G03",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.first_name, "UpdatedName")

    def test_delete_student_success(self):
        """Parent can delete their own child."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("students:student_delete", kwargs={"pk": self.student1.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Student.objects.filter(pk=self.student1.pk).exists())


class StudentFormValidationTest(TestCase):
    """Tests for student form validation."""

    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(
            username="parent",
            email="parent@example.com",
            password="testpass123",
            is_active=True,
        )

    def test_future_date_of_birth_rejected(self):
        """Date of birth in the future is rejected."""
        self.client.login(username="parent", password="testpass123")
        response = self.client.post(
            reverse("students:student_create"),
            data={
                "first_name": "FutureChild",
                "grade_level": "K",
                "date_of_birth": "2099-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)  # Form re-rendered with errors
        self.assertContains(response, "cannot be in the future")


class TeacherStudentViewTests(TestCase):
    """Tests that teachers can view but not create/edit/delete students."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent_user = User.objects.create_user(
            username="t_parent", email="t_parent@test.com", password="testpass123",
        )
        cls.teacher_user = User.objects.create_user(
            username="t_teacher", email="t_teacher@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Teacher Test Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        cls.student = Student.objects.create(
            parent=cls.parent_user, first_name="FamChild", grade_level="G03",
            family=cls.family,
        )

    def test_teacher_can_list_students(self):
        self.client.login(username="t_teacher", password="testpass123")
        response = self.client.get(reverse("students:student_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FamChild")

    def test_teacher_can_view_student_detail(self):
        self.client.login(username="t_teacher", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_teacher_cannot_create_student(self):
        self.client.login(username="t_teacher", password="testpass123")
        response = self.client.get(reverse("students:student_create"))
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_update_student(self):
        self.client.login(username="t_teacher", password="testpass123")
        response = self.client.get(
            reverse("students:student_update", kwargs={"pk": self.student.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_student(self):
        self.client.login(username="t_teacher", password="testpass123")
        response = self.client.get(
            reverse("students:student_delete", kwargs={"pk": self.student.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_list_hides_edit_buttons(self):
        self.client.login(username="t_teacher", password="testpass123")
        response = self.client.get(reverse("students:student_list"))
        self.assertNotContains(response, "Add Child")
        self.assertNotContains(response, "btn-outline-danger")

    def test_teacher_detail_hides_edit_buttons(self):
        self.client.login(username="t_teacher", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student.pk})
        )
        self.assertNotContains(response, "btn-primary\">Edit")
        self.assertNotContains(response, "btn-danger\">Delete")
