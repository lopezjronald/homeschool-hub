import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.models import Family, FamilyMembership
from students.models import Student

from .models import (
    Chapter, Curriculum, CurriculumDocument, CurriculumPlacement, CurriculumResource, Lesson,
)
from .services import apply_blueprint, get_blueprint

User = get_user_model()

MEDIA = tempfile.mkdtemp()


class FuzzySearchTests(TestCase):
    """Misspelling-tolerant curricula search (trigram on Postgres, icontains fallback)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="fz", email="fz@e.com", password="pw")
        cls.family = Family.objects.create(name="Fz Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        Curriculum.objects.create(parent=cls.parent, family=cls.family,
                                  name="Dimensions Math 3A", subject="Math")
        Curriculum.objects.create(parent=cls.parent, family=cls.family,
                                  name="Essentials in Writing 3", subject="Writing")

    def _search(self, q):
        self.client.login(username="fz", password="pw")
        resp = self.client.get(reverse("curricula:curriculum_list"), {"q": q})
        self.assertEqual(resp.status_code, 200)
        return [c.name for c in resp.context["curricula"]]

    def test_exact_substring_matches_on_any_backend(self):
        self.assertEqual(self._search("Dimensions"), ["Dimensions Math 3A"])
        self.assertEqual(self._search("writ"), ["Essentials in Writing 3"])

    def test_no_results_state_does_not_crash(self):
        self.assertEqual(self._search("zzzzz"), [])

    def test_misspelling_still_matches_on_postgres(self):
        from django.db import connection
        from unittest import skipUnless  # noqa: F401  (documented guard below)

        if connection.vendor != "postgresql":
            self.skipTest("trigram similarity requires PostgreSQL (runs on prod)")
        self.assertIn("Dimensions Math 3A", self._search("Dimensios Math"))
        self.assertIn("Essentials in Writing 3", self._search("Essentails"))


class CurriculumResourceTests(TestCase):
    """External resource links (answer keys, videos, …) attached to a curriculum."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="rp", email="rp@e.com", password="pw")
        cls.family = Family.objects.create(name="Res Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.teacher = User.objects.create_user(username="rt", email="rt@e.com", password="pw")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Res Course", subject="Literature", family=cls.family,
        )

    def _add_url(self):
        return reverse("curricula:curriculum_resource_add", kwargs={"pk": self.cur.pk})

    def test_editor_adds_resource_and_it_renders_safely(self):
        self.client.login(username="rp", password="pw")
        resp = self.client.post(self._add_url(), data={
            "label": "Answer Key", "url": "https://example.com/key",
            "resource_type": "answer_key", "teacher_only": "on", "notes": "",
        })
        self.assertEqual(resp.status_code, 302)
        r = CurriculumResource.objects.get(curriculum=self.cur)
        self.assertTrue(r.teacher_only)
        page = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.cur.pk})
        ).content.decode()
        self.assertIn("Answer Key", page)
        self.assertIn('rel="noopener noreferrer"', page)   # safe external link
        self.assertIn("Teacher only", page)

    def test_teacher_role_cannot_add(self):
        self.client.login(username="rt", password="pw")
        resp = self.client.post(self._add_url(), data={
            "label": "X", "url": "https://example.com/x", "resource_type": "other",
        })
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(CurriculumResource.objects.filter(curriculum=self.cur).exists())

    def test_editor_deletes_resource(self):
        r = CurriculumResource.objects.create(
            curriculum=self.cur, label="Vid", url="https://e.com/v", resource_type="video",
        )
        self.client.login(username="rp", password="pw")
        resp = self.client.post(reverse("curricula:curriculum_resource_delete", kwargs={
            "pk": self.cur.pk, "resource_pk": r.pk,
        }))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(CurriculumResource.objects.filter(pk=r.pk).exists())

    def test_rejects_non_http_url(self):
        self.client.login(username="rp", password="pw")
        self.client.post(self._add_url(), data={
            "label": "Bad", "url": "javascript:alert(1)", "resource_type": "other",
        })
        self.assertFalse(CurriculumResource.objects.filter(curriculum=self.cur).exists())


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


class CurriculumWebsiteUrlTests(TestCase):
    """Tests for HH-72: optional curriculum website URL."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="wu_parent", email="wu@test.com", password="testpass123",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.user, name="WU Math", subject="Math",
        )

    # -- Form validation --

    def test_blank_website_url_allowed(self):
        from .forms import CurriculumForm
        form = CurriculumForm(data={
            "name": "Test", "subject": "Math", "grade_level": "", "website_url": "",
        })
        self.assertTrue(form.is_valid())

    def test_valid_https_url_accepted(self):
        from .forms import CurriculumForm
        form = CurriculumForm(data={
            "name": "Test", "subject": "Math", "grade_level": "",
            "website_url": "https://khanacademy.org",
        })
        self.assertTrue(form.is_valid())

    def test_valid_http_url_accepted(self):
        from .forms import CurriculumForm
        form = CurriculumForm(data={
            "name": "Test", "subject": "Math", "grade_level": "",
            "website_url": "http://example.com",
        })
        self.assertTrue(form.is_valid())

    def test_ftp_url_rejected(self):
        from .forms import CurriculumForm
        form = CurriculumForm(data={
            "name": "Test", "subject": "Math", "grade_level": "",
            "website_url": "ftp://files.example.com",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("website_url", form.errors)

    def test_javascript_url_rejected(self):
        from .forms import CurriculumForm
        form = CurriculumForm(data={
            "name": "Test", "subject": "Math", "grade_level": "",
            "website_url": "javascript:alert(1)",
        })
        self.assertFalse(form.is_valid())

    # -- Template rendering --

    def test_detail_shows_launch_button_when_url_set(self):
        self.curriculum.website_url = "https://khanacademy.org"
        self.curriculum.save()
        self.client.login(username="wu_parent", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum.pk})
        )
        self.assertContains(response, "Launch curriculum")
        self.assertContains(response, "https://khanacademy.org")

    def test_detail_hides_launch_button_when_url_blank(self):
        self.client.login(username="wu_parent", password="testpass123")
        response = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum.pk})
        )
        self.assertNotContains(response, "Launch curriculum")

    def test_list_shows_launch_link_when_url_set(self):
        self.curriculum.website_url = "https://khanacademy.org"
        self.curriculum.save()
        self.client.login(username="wu_parent", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_list"))
        self.assertContains(response, "https://khanacademy.org")
        self.assertContains(response, "Launch")

    def test_list_hides_launch_link_when_url_blank(self):
        self.client.login(username="wu_parent", password="testpass123")
        response = self.client.get(reverse("curricula:curriculum_list"))
        self.assertNotContains(response, "Launch ↗")


class BlueprintTests(TestCase):
    """HH-82: Dimensions Math 3A blueprint + Chapter/Lesson structure."""

    def setUp(self):
        self.parent = User.objects.create_user(
            username="bp", email="bp@example.com", password="pw",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.parent, name="Dimensions Math 3A", subject="Math", grade_level="G03",
        )

    def test_apply_blueprint_creates_full_structure(self):
        bp = get_blueprint("dimensions_math_3a")
        chapters, lessons = apply_blueprint(self.curriculum, bp)
        self.assertEqual(chapters, 7)
        self.assertEqual(lessons, 70)
        self.assertEqual(Chapter.objects.filter(curriculum=self.curriculum).count(), 7)
        self.assertEqual(Lesson.objects.filter(chapter__curriculum=self.curriculum).count(), 70)

    def test_apply_blueprint_is_idempotent(self):
        bp = get_blueprint("dimensions_math_3a")
        apply_blueprint(self.curriculum, bp)
        apply_blueprint(self.curriculum, bp)  # second run must not duplicate
        self.assertEqual(Chapter.objects.filter(curriculum=self.curriculum).count(), 7)
        self.assertEqual(Lesson.objects.filter(chapter__curriculum=self.curriculum).count(), 70)

    def test_lesson_code_and_objectives(self):
        apply_blueprint(self.curriculum, get_blueprint("dimensions_math_3a"))
        lesson = Lesson.objects.get(chapter__curriculum=self.curriculum, chapter__number=2, number=6)
        self.assertEqual(lesson.code, "Ch 2, L6")
        self.assertEqual(lesson.title, "Strategies for Numbers Close to Hundreds")
        self.assertTrue(lesson.objectives)
        opener = Lesson.objects.get(
            chapter__curriculum=self.curriculum, chapter__number=1, lesson_type=Lesson.TYPE_OPENER,
        )
        self.assertEqual(opener.code, "Ch 1 Opener")

    def test_apply_blueprint_view_requires_editor(self):
        # teacher (view-only) cannot apply
        teacher = User.objects.create_user(username="bt", email="bt@e.com", password="pw")
        fam = Family.objects.create(name="BP Fam")
        FamilyMembership.objects.create(user=self.parent, family=fam, role="parent")
        FamilyMembership.objects.create(user=teacher, family=fam, role="teacher")
        self.curriculum.family = fam
        self.curriculum.save()
        self.client.login(username="bt", password="pw")
        resp = self.client.post(
            reverse("curricula:curriculum_apply_blueprint", kwargs={"pk": self.curriculum.pk}),
            data={"blueprint": "dimensions_math_3a"},
        )
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(Chapter.objects.filter(curriculum=self.curriculum).exists())

    def test_apply_blueprint_view_editor_success(self):
        self.client.login(username="bp", password="pw")
        resp = self.client.post(
            reverse("curricula:curriculum_apply_blueprint", kwargs={"pk": self.curriculum.pk}),
            data={"blueprint": "dimensions_math_3a"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Chapter.objects.filter(curriculum=self.curriculum).count(), 7)

    def test_detail_renders_structure(self):
        apply_blueprint(self.curriculum, get_blueprint("dimensions_math_3a"))
        self.client.login(username="bp", password="pw")
        resp = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum.pk})
        )
        self.assertContains(resp, "Addition and Subtraction - Part 1")
        self.assertContains(resp, "Strategies for Numbers Close to Hundreds")


@override_settings(MEDIA_ROOT=MEDIA)
class CurriculumDocumentTests(TestCase):
    """HH-82: source document upload/download/delete."""

    def setUp(self):
        self.parent = User.objects.create_user(
            username="doc", email="doc@example.com", password="pw",
        )
        self.curriculum = Curriculum.objects.create(
            parent=self.parent, name="Dimensions Math 3A", subject="Math",
        )

    def test_editor_can_upload_document(self):
        self.client.login(username="doc", password="pw")
        pdf = SimpleUploadedFile("guide.pdf", b"%PDF-1.4 fake", content_type="application/pdf")
        resp = self.client.post(
            reverse("curricula:curriculum_document_add", kwargs={"pk": self.curriculum.pk}),
            data={"title": "Instructor Guide 3A", "doc_type": "instructor_guide", "file": pdf},
        )
        self.assertEqual(resp.status_code, 302)
        doc = CurriculumDocument.objects.get(curriculum=self.curriculum)
        self.assertEqual(doc.title, "Instructor Guide 3A")
        self.assertEqual(doc.uploaded_by, self.parent)

    def test_editor_can_delete_document(self):
        doc = CurriculumDocument.objects.create(
            curriculum=self.curriculum, title="Temp", doc_type="other",
            file=SimpleUploadedFile("t.pdf", b"x"),
        )
        self.client.login(username="doc", password="pw")
        resp = self.client.post(
            reverse("curricula:curriculum_document_delete",
                    kwargs={"pk": self.curriculum.pk, "doc_pk": doc.pk}),
        )
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(CurriculumDocument.objects.filter(pk=doc.pk).exists())


class PlacementTests(TestCase):
    """HH-83: per-child lesson placement + progress."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="pl", email="pl@e.com", password="pw")
        cls.family = Family.objects.create(name="Placement Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family,
        )
        apply_blueprint(cls.curriculum, get_blueprint("dimensions_math_3a"))
        cls.ch2_l6 = Lesson.objects.get(
            chapter__curriculum=cls.curriculum, chapter__number=2, number=6,
        )

    def test_progress_and_next_lesson(self):
        placement = CurriculumPlacement.objects.create(
            child=self.child, curriculum=self.curriculum, current_lesson=self.ch2_l6,
        )
        prog = placement.progress()
        # Ch1 has 11 non-opener lessons; Ch2 L1-L5 = 5 before L6 → 16 done.
        self.assertEqual(prog["done"], 16)
        self.assertTrue(0 < prog["pct"] < 100)
        nxt = placement.next_lesson()
        self.assertEqual(nxt.number, 7)  # Ch2 L7 Practice A

    def test_editor_can_set_placement(self):
        self.client.login(username="pl", password="pw")
        resp = self.client.post(
            reverse("curricula:curriculum_set_placement",
                    kwargs={"pk": self.curriculum.pk, "child_pk": self.child.pk}),
            data={"current_lesson": self.ch2_l6.pk},
        )
        self.assertEqual(resp.status_code, 302)
        placement = CurriculumPlacement.objects.get(child=self.child, curriculum=self.curriculum)
        self.assertEqual(placement.current_lesson, self.ch2_l6)

    def test_teacher_cannot_set_placement(self):
        teacher = User.objects.create_user(username="plt", email="plt@e.com", password="pw")
        FamilyMembership.objects.create(user=teacher, family=self.family, role="teacher")
        self.client.login(username="plt", password="pw")
        resp = self.client.post(
            reverse("curricula:curriculum_set_placement",
                    kwargs={"pk": self.curriculum.pk, "child_pk": self.child.pk}),
            data={"current_lesson": self.ch2_l6.pk},
        )
        self.assertEqual(resp.status_code, 404)

    def test_progress_bar_shown_on_detail(self):
        CurriculumPlacement.objects.create(
            child=self.child, curriculum=self.curriculum, current_lesson=self.ch2_l6,
        )
        self.client.login(username="pl", password="pw")
        resp = self.client.get(
            reverse("curricula:curriculum_detail", kwargs={"pk": self.curriculum.pk})
        )
        self.assertContains(resp, "Violet")
        self.assertContains(resp, "progress-bar")


class CurriculumBrowserTests(TestCase):
    """HH-91: filter / search / tiled curricula browser."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="cb", email="cb@e.com", password="pw")
        cls.family = Family.objects.create(name="Browse Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        Curriculum.objects.create(parent=cls.parent, family=cls.family, name="Dimensions Math 3A", subject="Math", grade_level="G03")
        Curriculum.objects.create(parent=cls.parent, family=cls.family, name="Essentials in Writing 3", subject="Writing", grade_level="G03")
        Curriculum.objects.create(parent=cls.parent, family=cls.family, name="I Am David", subject="Literature", grade_level="G07")

    def setUp(self):
        self.client.login(username="cb", password="pw")

    def test_lists_all_with_facets(self):
        resp = self.client.get(reverse("curricula:curriculum_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Dimensions Math 3A")
        self.assertContains(resp, "Essentials in Writing 3")
        self.assertContains(resp, "I Am David")
        # subject + grade facets available
        self.assertContains(resp, ">Math<")
        self.assertContains(resp, ">Literature<")

    def test_filter_by_subject(self):
        resp = self.client.get(reverse("curricula:curriculum_list"), {"subject": "Math"})
        self.assertContains(resp, "Dimensions Math 3A")
        self.assertNotContains(resp, "I Am David")

    def test_filter_by_grade(self):
        resp = self.client.get(reverse("curricula:curriculum_list"), {"grade": "G07"})
        self.assertContains(resp, "I Am David")
        self.assertNotContains(resp, "Dimensions Math 3A")

    def test_search_query(self):
        resp = self.client.get(reverse("curricula:curriculum_list"), {"q": "writing"})
        self.assertContains(resp, "Essentials in Writing 3")
        self.assertNotContains(resp, "I Am David")

    def test_no_results_state(self):
        resp = self.client.get(reverse("curricula:curriculum_list"), {"q": "zzzznope"})
        self.assertContains(resp, "No curricula match")

    def test_scoped_to_family(self):
        other = User.objects.create_user(username="cb2", email="cb2@e.com", password="pw")
        fam2 = Family.objects.create(name="Other")
        FamilyMembership.objects.create(user=other, family=fam2, role="parent")
        Curriculum.objects.create(parent=other, family=fam2, name="Secret Course", subject="Math")
        resp = self.client.get(reverse("curricula:curriculum_list"))
        self.assertNotContains(resp, "Secret Course")
