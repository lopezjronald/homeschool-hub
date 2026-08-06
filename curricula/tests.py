import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from core.models import Family, FamilyMembership
from students.models import Student

from .models import (
    Chapter, Curriculum, CurriculumDocument, CurriculumPlacement, CurriculumResource, Lesson,
    LessonProgress,
)
from .services import apply_blueprint, get_blueprint

User = get_user_model()

MEDIA = tempfile.mkdtemp()


class SubjectCanonicalTests(SimpleTestCase):
    """canonical() is the grouping key every cross-subject feature keys on (F1)."""

    def test_case_and_whitespace_are_folded(self):
        from curricula.subjects import canonical
        self.assertEqual(canonical("  Math  "), "math")
        self.assertEqual(canonical("MATHEMATICS"), "math")
        # collapses runs of internal whitespace, not just the ends
        self.assertEqual(canonical("Language   Arts"), "writing")

    def test_the_lingua_mirror_subject_folds_into_spanish(self):
        """The load-bearing alias: the book mirror files rows under 'Spanish
        reading', which must group with the child's Spanish, not a 2nd subject.
        Assert the exact slug so a mutant that drops the alias (leaving
        'spanish-reading') fails."""
        from curricula.subjects import canonical
        self.assertEqual(canonical("Spanish reading"), "spanish")
        self.assertEqual(canonical("Spanish"), "spanish")
        self.assertEqual(canonical("Spanish reading"), canonical("Español"))

    def test_known_synonyms_fold_together(self):
        from curricula.subjects import canonical
        self.assertEqual(canonical("English"), "writing")
        self.assertEqual(canonical("Social Studies"), "history")
        self.assertEqual(canonical("Geography"), "history")

    def test_an_unknown_subject_keeps_its_own_slug_not_a_catch_all(self):
        """A genuinely new subject must never be silently merged into another —
        it falls through to its OWN hyphenated slug. Kills a mutant that returns
        '' or a shared bucket for anything unrecognized."""
        from curricula.subjects import canonical
        self.assertEqual(canonical("Underwater Basket Weaving"),
                         "underwater-basket-weaving")
        self.assertNotEqual(canonical("Underwater Basket Weaving"), "")

    def test_distinct_subjects_stay_distinct(self):
        """Guards against over-merging: reading and literature are different
        subjects, and math must not collapse into writing."""
        from curricula.subjects import canonical
        self.assertNotEqual(canonical("Reading"), canonical("Literature"))
        self.assertNotEqual(canonical("Math"), canonical("Writing"))

    def test_empty_and_none_are_empty_string(self):
        from curricula.subjects import canonical
        self.assertEqual(canonical(""), "")
        self.assertEqual(canonical(None), "")
        self.assertEqual(canonical("   "), "")

    def test_canonical_is_idempotent(self):
        """Feeding a slug back through yields itself — so grouping on canonical()
        is stable no matter how many times it is applied."""
        from curricula.subjects import canonical
        for raw in ("Mathematics", "Spanish reading", "Underwater Basket Weaving"):
            once = canonical(raw)
            self.assertEqual(canonical(once), once, raw)


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

    def test_no_teaching_lesson_in_any_blueprint_is_graded_blind(self):
        # Objectives are not decoration: tutor.views._entry_objectives feeds them to
        # the AI grader as concept context, so a lesson with none is graded blind.
        # Openers, practices and reviews carry none by design — they introduce no
        # objective of their own.
        from curricula.blueprints import BLUEPRINTS
        blind = []
        for slug, bp in BLUEPRINTS.items():
            for ch in bp["chapters"]:
                for lsn in ch["lessons"]:
                    if lsn["type"] != Lesson.TYPE_LESSON:
                        continue
                    if not (lsn["objectives"] or "").strip():
                        blind.append(f"{slug} Ch{ch['number']} {lsn['title']}")
        self.assertEqual(blind, [], f"lessons the grader would judge blind: {blind}")

    def test_objectives_survive_being_applied_to_a_curriculum(self):
        # The blueprint having them is only half of it — apply_blueprint has to
        # carry them onto the Lesson rows the grader actually reads.
        apply_blueprint(self.curriculum, get_blueprint("dimensions_math_3a"))
        blind = [
            f"Ch{L.chapter.number} L{L.number} {L.title}"
            for L in Lesson.objects.filter(
                chapter__curriculum=self.curriculum,
                lesson_type=Lesson.TYPE_LESSON,
            ).select_related("chapter")
            if not (L.objectives or "").strip()
        ]
        self.assertEqual(blind, [], f"lessons the grader would judge blind: {blind}")

    def test_re_applying_the_blueprint_backfills_objectives_in_place(self):
        # How Ch3's objectives reach a curriculum that was created before they were
        # written: apply_blueprint updates rather than skipping existing lessons.
        apply_blueprint(self.curriculum, get_blueprint("dimensions_math_3a"))
        lesson = Lesson.objects.get(
            chapter__curriculum=self.curriculum, chapter__number=3, number=4)
        Lesson.objects.filter(pk=lesson.pk).update(objectives="")

        apply_blueprint(self.curriculum, get_blueprint("dimensions_math_3a"))

        lesson.refresh_from_db()
        self.assertIn("estimate", lesson.objectives.lower())

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

    def test_progress_counts_submitted_work_even_when_pointer_stuck(self):
        # Regression (HH): current_lesson never auto-advances, so a child who has
        # completed lessons showed "0 of N". Progress must follow the work she
        # actually turns in — with the pointer kept only as a floor.
        from tutor.models import QuestionSet, ResponseSheet

        first_lesson = (
            Lesson.objects.filter(chapter__curriculum=self.curriculum)
            .exclude(lesson_type=Lesson.TYPE_OPENER)
            .order_by("chapter__number", "order")
            .first()
        )
        placement = CurriculumPlacement.objects.create(
            child=self.child, curriculum=self.curriculum, current_lesson=first_lesson,
        )
        self.assertEqual(placement.progress()["done"], 0)   # pointer at lesson 1, nothing turned in

        for lesson in (first_lesson, self.ch2_l6):
            qs = QuestionSet.objects.create(
                lesson=lesson, title=f"Set {lesson.pk}", family=self.family,
                status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT,
            )
            ResponseSheet.objects.create(
                question_set=qs, child=self.child, status=ResponseSheet.SUBMITTED,
            )

        self.assertEqual(placement.progress()["done"], 2)   # two lessons turned in now count

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


class CurriculumDeleteProtectedTests(TestCase):
    """Regression: deleting a curriculum with a linked (PROTECTED) assignment must
    redirect gracefully, not raise ProtectedError → 500."""

    @classmethod
    def setUpTestData(cls):
        import datetime

        from assignments.models import Assignment
        cls.parent = User.objects.create_user(username="cdp", email="cdp@e.com", password="pw")
        cls.family = Family.objects.create(name="F")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.curriculum = Curriculum.objects.create(parent=cls.parent, family=cls.family, name="Math")
        cls.child = Student.objects.create(parent=cls.parent, family=cls.family, first_name="Kid")
        Assignment.objects.create(
            parent=cls.parent, family=cls.family, child=cls.child, curriculum=cls.curriculum,
            title="A1", due_date=datetime.date.today(), created_by=cls.parent,
        )

    def test_delete_with_assignment_is_graceful(self):
        self.client.login(username="cdp", password="pw")
        r = self.client.post(reverse("curricula:curriculum_delete", kwargs={"pk": self.curriculum.pk}))
        self.assertEqual(r.status_code, 302)                                  # not a 500
        self.assertTrue(Curriculum.objects.filter(pk=self.curriculum.pk).exists())  # still there


class LessonProgressTests(TestCase):
    """HH-141: per-child lesson complete/skip tracking (Violet's math)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="lp", email="lp@e.com", password="pw")
        cls.teacher = User.objects.create_user(username="lt", email="lt@e.com", password="pw")
        cls.family = Family.objects.create(name="LP Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family)
        apply_blueprint(cls.curriculum, get_blueprint("dimensions_math_3a"))
        cls.lessons = list(
            Lesson.objects.filter(chapter__curriculum=cls.curriculum)
            .exclude(lesson_type=Lesson.TYPE_OPENER).order_by("chapter__number", "order"))

    def _placement(self):
        p, _ = CurriculumPlacement.objects.get_or_create(
            child=self.child, curriculum=self.curriculum)
        return p

    def _mark(self, lesson, status):
        return LessonProgress.objects.update_or_create(
            child=self.child, lesson=lesson, defaults={"status": status})[0]

    def test_completing_a_lesson_advances_current_and_progress(self):
        p = self._placement()
        first = self.lessons[0]
        self.assertEqual(p.current_actionable_lesson(), first)   # nothing done → first
        self.assertEqual(p.progress()["done"], 0)
        self._mark(first, LessonProgress.COMPLETED)
        self.assertEqual(p.current_actionable_lesson(), self.lessons[1])  # moved on
        self.assertEqual(p.progress()["done"], 1)

    def test_skipped_lesson_is_passed_over_and_counted(self):
        p = self._placement()
        self._mark(self.lessons[0], LessonProgress.SKIPPED)
        # a skip resolves the lesson: it's not "next", and the bar advances past it
        self.assertEqual(p.current_actionable_lesson(), self.lessons[1])
        prog = p.progress()
        self.assertEqual(prog["done"], 1)
        self.assertEqual(prog["skipped"], 1)

    def test_reset_restores_not_started(self):
        p = self._placement()
        self._mark(self.lessons[0], LessonProgress.COMPLETED)
        LessonProgress.objects.filter(child=self.child, lesson=self.lessons[0]).delete()
        self.assertEqual(p.current_actionable_lesson(), self.lessons[0])   # back to first
        self.assertEqual(p.progress()["done"], 0)

    def test_submitted_work_still_counts_when_no_marks(self):
        # Regression guard: the legacy inferred signal must survive the union rewrite.
        from tutor.models import QuestionSet, ResponseSheet
        qs = QuestionSet.objects.create(
            lesson=self.lessons[0], title="Set", family=self.family,
            status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)
        ResponseSheet.objects.create(question_set=qs, child=self.child,
                                     status=ResponseSheet.SUBMITTED)
        self.assertEqual(self._placement().progress()["done"], 1)

    def test_editor_can_mark_and_teacher_cannot(self):
        url = reverse("students:lesson_mark",
                      kwargs={"pk": self.child.pk, "curriculum_id": self.curriculum.pk})
        c = Client()
        c.login(username="lt", password="pw")
        self.assertEqual(c.post(url, {"lesson": self.lessons[0].pk, "action": "completed"}).status_code, 404)
        self.assertFalse(LessonProgress.objects.exists())          # view-only blocked
        c.login(username="lp", password="pw")
        r = c.post(url, {"lesson": self.lessons[0].pk, "action": "completed"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(LessonProgress.objects.get().status, LessonProgress.COMPLETED)
        # "Where the child is now" is DERIVED, not a rewritten pointer: marking lesson 1
        # complete makes lesson 2 the next actionable one, while the parent's own
        # placement pointer is left alone (rewriting it broke Undo — see
        # LessonProgressReviewFixTests).
        self.assertEqual(self._placement().current_actionable_lesson(), self.lessons[1])

    def test_skip_all_remaining_practice(self):
        c = Client()
        c.login(username="lp", password="pw")
        url = reverse("students:lessons_skip_practice",
                      kwargs={"pk": self.child.pk, "curriculum_id": self.curriculum.pk})
        r = c.post(url)
        self.assertEqual(r.status_code, 302)
        practice = [l for l in self.lessons if l.lesson_type == Lesson.TYPE_PRACTICE]
        self.assertGreater(len(practice), 0)                       # blueprint has practice lessons
        skipped = set(LessonProgress.objects.filter(
            status=LessonProgress.SKIPPED).values_list("lesson_id", flat=True))
        self.assertEqual(skipped, {l.pk for l in practice})        # exactly the practice ones
        # and the next actionable lesson is NOT a practice lesson
        nxt = self._placement().current_actionable_lesson()
        self.assertNotEqual(nxt.lesson_type, Lesson.TYPE_PRACTICE)

    def test_lessons_page_renders_with_controls(self):
        c = Client()
        c.login(username="lp", password="pw")
        url = reverse("students:student_lessons",
                      kwargs={"pk": self.child.pk, "curriculum_id": self.curriculum.pk})
        html = c.get(url).content.decode()
        self.assertIn("Dimensions Math 3A", html)                   # the checklist page
        self.assertIn('name="done"', html)                          # a real checkbox per lesson
        self.assertIn('name="skip"', html)                          # per-lesson skip checkbox
        self.assertIn("Save changes", html)                         # explicit save (works w/o JS)
        self.assertIn("Skip all remaining practice", html)          # bulk practice skip
        self.assertIn("lessons-badge", html)                        # practice badge


class LessonProgressReviewFixTests(TestCase):
    """HH-141 review fixes: Undo actually undoes, the parent's placement pointer is
    never auto-rewritten, cross-family writes are refused, hostile input 404s."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="rf", email="rf@e.com", password="pw")
        cls.family = Family.objects.create(name="RF Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family)
        apply_blueprint(cls.curriculum, get_blueprint("dimensions_math_3a"))
        cls.lessons = list(
            Lesson.objects.filter(chapter__curriculum=cls.curriculum)
            .exclude(lesson_type=Lesson.TYPE_OPENER).order_by("chapter__number", "order"))
        cls.opener = Lesson.objects.filter(
            chapter__curriculum=cls.curriculum, lesson_type=Lesson.TYPE_OPENER).first()

    def _c(self):
        c = Client(); c.login(username="rf", password="pw"); return c

    def _mark_url(self):
        return reverse("students:lesson_mark",
                       kwargs={"pk": self.child.pk, "curriculum_id": self.curriculum.pk})

    def test_undo_actually_undoes_a_completed_lesson(self):
        # Regression: auto-advancing the placement pointer made the floor re-resolve
        # the un-done lesson, so Undo was a permanent no-op.
        c, first = self._c(), self.lessons[0]
        c.post(self._mark_url(), {"lesson": first.pk, "action": "completed"})
        p = CurriculumPlacement.objects.get(child=self.child, curriculum=self.curriculum)
        self.assertEqual(p.progress()["done"], 1)
        c.post(self._mark_url(), {"lesson": first.pk, "action": "reset"})
        p.refresh_from_db()
        self.assertEqual(p.progress()["done"], 0)                  # truly undone
        self.assertEqual(p.current_actionable_lesson(), first)      # back to lesson 1

    def test_marking_never_rewrites_the_parents_placement(self):
        # An opener placement (or any parent-set pointer) must survive a mark.
        p = CurriculumPlacement.objects.create(
            child=self.child, curriculum=self.curriculum, current_lesson=self.opener)
        self._c().post(self._mark_url(), {"lesson": self.lessons[0].pk, "action": "completed"})
        p.refresh_from_db()
        self.assertEqual(p.current_lesson, self.opener)             # untouched

    def test_finishing_every_lesson_reads_as_finished_not_not_started(self):
        c = self._c()
        for lesson in self.lessons:
            c.post(self._mark_url(), {"lesson": lesson.pk, "action": "completed"})
        p = CurriculumPlacement.objects.get(child=self.child, curriculum=self.curriculum)
        self.assertIsNone(p.current_actionable_lesson())            # nothing left
        self.assertEqual(p.progress()["pct"], 100)
        html = c.get(reverse("students:student_lessons", kwargs={
            "pk": self.child.pk, "curriculum_id": self.curriculum.pk})).content.decode()
        self.assertIn("Finished", html)
        self.assertNotIn("Not started yet", html)

    def test_unknown_action_and_bad_lesson_pk_are_refused(self):
        c = self._c()
        self.assertEqual(c.post(self._mark_url(),
                                {"lesson": self.lessons[0].pk, "action": "bogus"}).status_code, 404)
        self.assertEqual(c.post(self._mark_url(),
                                {"lesson": "abc", "action": "completed"}).status_code, 404)
        self.assertFalse(LessonProgress.objects.exists())           # nothing written

    def test_cannot_bind_a_child_to_another_familys_curriculum(self):
        other_family = Family.objects.create(name="Other Fam")
        FamilyMembership.objects.create(user=self.parent, family=other_family, role="parent")
        other_cur = Curriculum.objects.create(
            parent=self.parent, name="Other Math", subject="Math", family=other_family)
        ch = Chapter.objects.create(curriculum=other_cur, number=1, title="C1")
        other_lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        r = self._c().post(
            reverse("students:lesson_mark",
                    kwargs={"pk": self.child.pk, "curriculum_id": other_cur.pk}),
            {"lesson": other_lesson.pk, "action": "completed"})
        self.assertEqual(r.status_code, 404)                        # cross-family refused
        self.assertFalse(LessonProgress.objects.exists())

    def test_progress_does_not_issue_a_redundant_skipped_query(self):
        LessonProgress.objects.create(child=self.child, lesson=self.lessons[0],
                                      status=LessonProgress.SKIPPED)
        p = CurriculumPlacement.objects.create(child=self.child, curriculum=self.curriculum)
        with self.assertNumQueries(3):        # lesson ids + marks + submitted work
            prog = p.progress()
        self.assertEqual(prog["skipped"], 1)


class LessonChecklistSaveTests(TestCase):
    """HH-142: the lesson page is a CHECKLIST — tick what's done, Save, un-tick to undo."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ck", email="ck@e.com", password="pw")
        cls.teacher = User.objects.create_user(username="ckt", email="ckt@e.com", password="pw")
        cls.family = Family.objects.create(name="CK Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        FamilyMembership.objects.create(user=cls.teacher, family=cls.family, role="teacher")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family)
        apply_blueprint(cls.curriculum, get_blueprint("dimensions_math_3a"))
        cls.lessons = list(
            Lesson.objects.filter(chapter__curriculum=cls.curriculum)
            .exclude(lesson_type=Lesson.TYPE_OPENER).order_by("chapter__number", "order"))
        cls.opener = Lesson.objects.filter(
            chapter__curriculum=cls.curriculum, lesson_type=Lesson.TYPE_OPENER).first()

    def _c(self, who="ck"):
        c = Client(); c.login(username=who, password="pw"); return c

    def _url(self):
        return reverse("students:lessons_save",
                       kwargs={"pk": self.child.pk, "curriculum_id": self.curriculum.pk})

    def test_ticking_lessons_marks_them_done(self):
        ids = [self.lessons[0].pk, self.lessons[1].pk]
        r = self._c().post(self._url(), {"done": [str(i) for i in ids]})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(
            set(LessonProgress.objects.filter(status=LessonProgress.COMPLETED)
                .values_list("lesson_id", flat=True)), set(ids))
        p = CurriculumPlacement.objects.get(child=self.child, curriculum=self.curriculum)
        self.assertEqual(p.progress()["done"], 2)

    def test_unticking_undoes(self):
        c = self._c()
        c.post(self._url(), {"done": [str(self.lessons[0].pk), str(self.lessons[1].pk)]})
        c.post(self._url(), {"done": [str(self.lessons[0].pk)]})   # untick the second
        done = set(LessonProgress.objects.filter(status=LessonProgress.COMPLETED)
                   .values_list("lesson_id", flat=True))
        self.assertEqual(done, {self.lessons[0].pk})
        c.post(self._url(), {})                                     # untick everything
        self.assertFalse(LessonProgress.objects.exists())

    def test_skip_column_marks_skipped_and_done_wins(self):
        c = self._c()
        c.post(self._url(), {"skip": [str(self.lessons[2].pk)]})
        self.assertEqual(LessonProgress.objects.get(lesson=self.lessons[2]).status,
                         LessonProgress.SKIPPED)
        # ticking BOTH done and skip for the same lesson resolves to done
        c.post(self._url(), {"done": [str(self.lessons[2].pk)], "skip": [str(self.lessons[2].pk)]})
        self.assertEqual(LessonProgress.objects.get(lesson=self.lessons[2]).status,
                         LessonProgress.COMPLETED)

    def test_hostile_and_foreign_ids_are_ignored(self):
        other_cur = Curriculum.objects.create(
            parent=self.parent, name="Other", subject="Math", family=self.family)
        ch = Chapter.objects.create(curriculum=other_cur, number=1, title="C")
        foreign = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        r = self._c().post(self._url(), {
            "done": ["abc", "٧", "999999", str(foreign.pk), str(self.lessons[0].pk)]})
        self.assertEqual(r.status_code, 302)                        # no 500
        self.assertEqual(list(LessonProgress.objects.values_list("lesson_id", flat=True)),
                         [self.lessons[0].pk])                      # only the valid own-lesson

    def test_openers_cannot_be_ticked(self):
        self._c().post(self._url(), {"done": [str(self.opener.pk)]})
        self.assertFalse(LessonProgress.objects.exists())           # openers aren't checklist items

    def test_view_only_teacher_cannot_save(self):
        r = self._c("ckt").post(self._url(), {"done": [str(self.lessons[0].pk)]})
        self.assertEqual(r.status_code, 404)
        self.assertFalse(LessonProgress.objects.exists())

    def test_checklist_renders_current_state(self):
        c = self._c()
        c.post(self._url(), {"done": [str(self.lessons[0].pk)],
                             "skip": [str(self.lessons[1].pk)]})
        html = c.get(reverse("students:student_lessons", kwargs={
            "pk": self.child.pk, "curriculum_id": self.curriculum.pk})).content.decode()
        self.assertIn(f'name="done" value="{self.lessons[0].pk}"\n                     checked', html.replace("\r", ""))
        self.assertIn("is-skipped", html)                           # skipped row styled


class LessonChecklistFloorTests(TestCase):
    """HH-142: lessons already counted done by the placement floor must render TICKED,
    so the progress number and the checkboxes never disagree."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="fl", email="fl@e.com", password="pw")
        cls.family = Family.objects.create(name="FL Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family)
        apply_blueprint(cls.curriculum, get_blueprint("dimensions_math_3a"))
        cls.lessons = list(
            Lesson.objects.filter(chapter__curriculum=cls.curriculum)
            .exclude(lesson_type=Lesson.TYPE_OPENER).order_by("chapter__number", "order"))

    def test_lessons_below_the_pointer_render_checked(self):
        # Parent placed the child mid-curriculum: everything before the pointer is done.
        pointer = self.lessons[5]
        p = CurriculumPlacement.objects.create(
            child=self.child, curriculum=self.curriculum, current_lesson=pointer)
        self.assertEqual(p.progress()["done"], 5)

        c = Client(); c.login(username="fl", password="pw")
        html = c.get(reverse("students:student_lessons", kwargs={
            "pk": self.child.pk, "curriculum_id": self.curriculum.pk})).content.decode()
        flat = " ".join(html.split())
        # the 5 lessons before the pointer are ticked...
        for lesson in self.lessons[:5]:
            self.assertIn(f'name="done" value="{lesson.pk}" checked', flat,
                          f"{lesson.code} should render checked (below the floor)")
        # ...and the pointer lesson itself is NOT ticked (it's the one still to do)
        self.assertNotIn(f'name="done" value="{pointer.pk}" checked', flat)
        self.assertIn(f'name="done" value="{pointer.pk}"', flat)   # but it is on the page


class SaxonPreAlgebraBlueprintTests(TestCase):
    """The Saxon course is a flat run of numbered lessons grouped into synthetic
    chapters of ten (HH-155)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user("sx", "sx@e.com", "pw")
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Saxon Pre-Algebra (DIVE)", subject="Math",
            grade_level="G07",
        )

    def test_chapters_are_numbered_so_earlier_lessons_can_be_added_later(self):
        # chapter = (lesson - 1) // 10 + 1, so 71-80 is Ch8. If lessons 1-70 are
        # ever added they become Ch1-7 with no renumbering and no collision with
        # unique_chapter_number_per_curriculum.
        bp = get_blueprint("saxon_prealgebra_dive")
        by_number = {ch["number"]: ch for ch in bp["chapters"]}
        self.assertEqual(sorted(by_number), [8, 9, 10])
        self.assertEqual([l["number"] for l in by_number[8]["lessons"]],
                         list(range(71, 81)))
        self.assertEqual([l["number"] for l in by_number[10]["lessons"]],
                         list(range(91, 101)))

    def test_lesson_code_shows_the_printed_saxon_number(self):
        apply_blueprint(self.cur, get_blueprint("saxon_prealgebra_dive"))
        lesson = Lesson.objects.get(chapter__curriculum=self.cur, number=71)
        self.assertEqual(lesson.chapter.number, 8)
        self.assertEqual(lesson.order, 1)          # first within its ten
        self.assertEqual(lesson.code, "Ch 8, L71")

    def test_every_lesson_has_an_objective(self):
        # tutor.views._entry_objectives feeds these to the AI grader, so a lesson
        # without one is graded blind.
        bp = get_blueprint("saxon_prealgebra_dive")
        blind = [l["title"] for ch in bp["chapters"] for l in ch["lessons"]
                 if not (l["objectives"] or "").strip()]
        self.assertEqual(blind, [])

    def test_there_are_no_chapter_openers(self):
        # Saxon has no opener pages, and openers are excluded from progress.
        bp = get_blueprint("saxon_prealgebra_dive")
        kinds = {l["type"] for ch in bp["chapters"] for l in ch["lessons"]}
        self.assertEqual(kinds, {Lesson.TYPE_LESSON})

    def test_applying_it_is_idempotent(self):
        bp = get_blueprint("saxon_prealgebra_dive")
        apply_blueprint(self.cur, bp)
        before = Lesson.objects.filter(chapter__curriculum=self.cur).count()
        apply_blueprint(self.cur, bp)
        self.assertEqual(Lesson.objects.filter(chapter__curriculum=self.cur).count(), before)
        self.assertEqual(before, 30)

    def test_a_later_lesson_can_be_added_without_disturbing_the_others(self):
        # The course grows as the PDFs arrive: adding a row and re-running must
        # not renumber or delete anything already there.
        from curricula.blueprints import _SAXON_LESSONS, _saxon_chapters
        apply_blueprint(self.cur, get_blueprint("saxon_prealgebra_dive"))
        first = Lesson.objects.get(chapter__curriculum=self.cur, number=71)

        _SAXON_LESSONS[101] = ("A Later Lesson", "Do a later thing.")
        try:
            grown = dict(get_blueprint("saxon_prealgebra_dive"))
            grown["chapters"] = _saxon_chapters()
            apply_blueprint(self.cur, grown)
        finally:
            del _SAXON_LESSONS[101]

        self.assertEqual(Lesson.objects.filter(chapter__curriculum=self.cur).count(), 31)
        first.refresh_from_db()
        self.assertEqual((first.chapter.number, first.order), (8, 1))
        self.assertTrue(Lesson.objects.filter(
            chapter__curriculum=self.cur, chapter__number=11, number=101).exists())
