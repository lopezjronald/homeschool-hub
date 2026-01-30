from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Curriculum

User = get_user_model()


class CurriculumModelTest(TestCase):
    """Tests for the Curriculum model."""

    def setUp(self):
        self.parent = User.objects.create_user(
            username="parent1",
            email="parent1@example.com",
            password="testpass123",
            is_active=True,
        )

    def test_create_curriculum(self):
        """Curriculum can be created with required fields."""
        curriculum = Curriculum.objects.create(
            parent=self.parent,
            name="Singapore Math 5A",
            subject="Math",
        )
        self.assertEqual(curriculum.name, "Singapore Math 5A")
        self.assertEqual(curriculum.parent, self.parent)
        self.assertEqual(str(curriculum), "Singapore Math 5A")

    def test_curriculum_with_grade_level(self):
        """Curriculum can have optional grade level."""
        curriculum = Curriculum.objects.create(
            parent=self.parent,
            name="History for 5th Grade",
            subject="History",
            grade_level="G05",
        )
        self.assertEqual(curriculum.grade_level, "G05")
        self.assertEqual(curriculum.get_grade_level_display(), "5th Grade")

    def test_related_assignments_count_no_assignments(self):
        """get_related_assignments_count returns 0 when no assignments exist."""
        curriculum = Curriculum.objects.create(
            parent=self.parent,
            name="Test Curriculum",
            subject="Test",
        )
        self.assertEqual(curriculum.get_related_assignments_count(), 0)


class CurriculumViewsTest(TestCase):
    """Tests for curriculum CRUD views."""

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
        self.curriculum1 = Curriculum.objects.create(
            parent=self.parent1,
            name="Math Curriculum",
            subject="Math",
        )
        self.curriculum2 = Curriculum.objects.create(
            parent=self.parent2,
            name="Science Curriculum",
            subject="Science",
        )

    def test_list_requires_login(self):
        """Curriculum list redirects to login if not authenticated."""
        response = self.client.get(reverse("curricula:curriculum_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_list_shows_only_own_curricula(self):
        """Parent sees only their own curricula in the list."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Math Curriculum")
        self.assertNotContains(response, "Science Curriculum")

    def test_detail_requires_login(self):
        """Curriculum detail redirects to login if not authenticated."""
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum1.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_detail_returns_404_for_non_owner(self):
        """Parent cannot view another parent's curriculum (404)."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum2.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_shows_own_curriculum(self):
        """Parent can view their own curriculum's details."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Math Curriculum")

    def test_update_returns_404_for_non_owner(self):
        """Parent cannot edit another parent's curriculum (404)."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_update", kwargs={"pk": self.curriculum2.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_returns_404_for_non_owner(self):
        """Parent cannot delete another parent's curriculum (404)."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_delete", kwargs={"pk": self.curriculum2.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_create_requires_login(self):
        """Create view redirects to login if not authenticated."""
        response = self.client.get(reverse("curricula:curriculum_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_curriculum_success(self):
        """Parent can create a new curriculum."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("curricula:curriculum_create"),
            data={
                "name": "New Curriculum",
                "subject": "Reading",
                "grade_level": "G03",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Curriculum.objects.filter(name="New Curriculum", parent=self.parent1).exists()
        )

    def test_create_sets_parent_automatically(self):
        """Parent is set automatically from logged-in user."""
        self.client.login(username="parent1", password="testpass123")
        self.client.post(
            reverse("curricula:curriculum_create"),
            data={
                "name": "Auto Parent Curriculum",
                "subject": "Art",
            },
        )
        curriculum = Curriculum.objects.get(name="Auto Parent Curriculum")
        self.assertEqual(curriculum.parent, self.parent1)

    def test_update_curriculum_success(self):
        """Parent can update their own curriculum."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("curricula:curriculum_update", kwargs={"pk": self.curriculum1.pk}),
            data={
                "name": "Updated Math",
                "subject": "Mathematics",
                "grade_level": "G05",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.curriculum1.refresh_from_db()
        self.assertEqual(self.curriculum1.name, "Updated Math")

    def test_delete_curriculum_success(self):
        """Parent can delete their own curriculum."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("curricula:curriculum_delete", kwargs={"pk": self.curriculum1.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Curriculum.objects.filter(pk=self.curriculum1.pk).exists())


class TeacherCurriculumViewTests(TestCase):
    """Tests that teachers can view but not create/edit/delete curricula."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent_user = User.objects.create_user(
            username="tc_parent", email="tc_parent@test.com", password="testpass123",
        )
        cls.teacher_user = User.objects.create_user(
            username="tc_teacher", email="tc_teacher@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Teacher Curr Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent_user, name="Family Math", subject="Math",
            family=cls.family,
        )

    def test_teacher_can_list_curricula(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Family Math")

    def test_teacher_can_view_curriculum_detail(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_teacher_cannot_create_curriculum(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_create"))
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_update_curriculum(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_update", kwargs={"pk": self.curriculum.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_delete_curriculum(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_delete", kwargs={"pk": self.curriculum.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_list_hides_edit_buttons(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_list"))
        self.assertNotContains(response, "Add Curriculum")
        self.assertNotContains(response, "btn-outline-danger")

    def test_teacher_detail_hides_edit_buttons(self):
        self.client.login(username="tc_teacher", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum.pk})
        )
        self.assertNotContains(response, "btn-primary\">Edit")
        self.assertNotContains(response, "btn-danger\">Delete")
