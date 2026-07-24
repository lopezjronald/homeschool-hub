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

    def test_detail_shows_curricula_and_progress(self):
        """The detail page lists the curricula the child is currently doing."""
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson

        curriculum = Curriculum.objects.create(
            parent=self.parent1, name="Dimensions Math 3A", subject="Math",
        )
        chapter = Chapter.objects.create(curriculum=curriculum, number=1, title="Numbers")
        Lesson.objects.create(chapter=chapter, order=1, number=1, title="Counting")
        lesson2 = Lesson.objects.create(chapter=chapter, order=2, number=2, title="Place Value")
        CurriculumPlacement.objects.create(
            child=self.student1, curriculum=curriculum, current_lesson=lesson2,
        )

        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student1.pk})
        )
        self.assertContains(response, "Curricula")
        self.assertContains(response, "Dimensions Math 3A")
        self.assertContains(response, "Ch 1, L2")  # current lesson code

    def test_detail_empty_state_when_no_curricula(self):
        """A child with no placement shows a friendly empty message."""
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            reverse("students:student_detail", kwargs={"pk": self.student1.pk})
        )
        self.assertContains(response, "Not placed in a subject yet")

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

    def test_delete_student_with_worklog_is_graceful(self):
        """LGA-20: a child with work-log history can't be hard-deleted (worklog
        PROTECTs). The view must degrade gracefully, not 500 (was unguarded)."""
        from worklog.models import WorkLogEntry
        WorkLogEntry.objects.create(
            parent=self.parent1, child=self.student1, subject="Math",
        )
        self.client.login(username="parent1", password="testpass123")
        response = self.client.post(
            reverse("students:student_delete", kwargs={"pk": self.student1.pk}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)  # graceful, not a 500
        self.assertTrue(Student.objects.filter(pk=self.student1.pk).exists())  # preserved
        msgs = [str(m) for m in response.context["messages"]]
        self.assertTrue(any("work-log history" in m for m in msgs))


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


class EnterPortalTests(TestCase):
    """Parent taps a child -> lands in the child's portal, signed out."""

    def setUp(self):
        from core.models import Family, FamilyMembership
        self.parent = User.objects.create_user(
            username="kp", email="kp@example.com", password="pw", is_active=True,
        )
        self.other = User.objects.create_user(
            username="kp2", email="kp2@example.com", password="pw", is_active=True,
        )
        fam = Family.objects.create(name="Kiosk Fam")
        FamilyMembership.objects.create(user=self.parent, family=fam, role="parent")
        self.child = Student.objects.create(
            parent=self.parent, first_name="Violet", grade_level="G03", family=fam,
        )

    def test_enter_portal_logs_out_and_redirects_to_portal(self):
        self.client.login(username="kp", password="pw")
        resp = self.client.post(reverse("students:enter_portal", kwargs={"pk": self.child.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/portal/", resp.url)
        # the parent session is gone — a login-required page now redirects to login
        self.assertNotIn("_auth_user_id", self.client.session)
        after = self.client.get(reverse("students:student_list"))
        self.assertEqual(after.status_code, 302)
        self.assertIn("/accounts/login/", after.url)

    def test_enter_portal_requires_post(self):
        self.client.login(username="kp", password="pw")
        resp = self.client.get(reverse("students:enter_portal", kwargs={"pk": self.child.pk}))
        self.assertEqual(resp.status_code, 405)

    def test_cannot_enter_another_familys_child_portal(self):
        self.client.login(username="kp2", password="pw")
        resp = self.client.post(reverse("students:enter_portal", kwargs={"pk": self.child.pk}))
        self.assertEqual(resp.status_code, 404)


class StudentWorkBrowserTests(TestCase):
    """Parents can browse into a child's actual answers."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
        from tutor.models import Question, QuestionSet, ResponseSheet

        cls.parent = User.objects.create_user(username="wb", email="wb@e.com", password="pw")
        cls.family = Family.objects.create(name="WB Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="WB Course", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="Chapters 1-3")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Section 1 · Comprehension", family=cls.family,
            status=QuestionSet.APPROVED,
        )
        cls.q1 = Question.objects.create(question_set=cls.qset, order=1, category="comprehension",
                                         prompt="Why is Wolf brave?")
        cls.q2 = Question.objects.create(question_set=cls.qset, order=2, category="comprehension",
                                         prompt="Where does he live?")
        cls.discussion = QuestionSet.objects.create(
            lesson=cls.lesson, title="Section 1 · Discussion", family=cls.family,
            status=QuestionSet.APPROVED, mode=QuestionSet.MODE_DISCUSSION,
        )
        cls.sheet = ResponseSheet.objects.create(
            question_set=cls.qset, child=cls.violet,
            answers={str(cls.q1.pk): "He sings for help even though he is small."},
        )
        # another family (must not be reachable)
        cls.other = User.objects.create_user(username="wb2", email="wb2@e.com", password="pw")
        fam2 = Family.objects.create(name="Other WB")
        FamilyMembership.objects.create(user=cls.other, family=fam2, role="parent")

    def test_work_list_shows_student_sets_not_discussion(self):
        self.client.login(username="wb", password="pw")
        resp = self.client.get(reverse("students:student_work", kwargs={
            "pk": self.violet.pk, "curriculum_id": self.cur.pk,
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Section 1 · Comprehension")
        self.assertNotContains(resp, "Section 1 · Discussion")   # teacher-led, no child answers
        self.assertContains(resp, "In progress")                 # 1 of 2 answered

    def test_work_set_shows_the_childs_answer(self):
        self.client.login(username="wb", password="pw")
        resp = self.client.get(reverse("students:student_work_set", kwargs={
            "pk": self.violet.pk, "set_pk": self.qset.pk,
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "sings for help even though he is small")
        self.assertContains(resp, "No answer")                   # q2 unanswered

    def test_detail_page_links_to_work(self):
        self.client.login(username="wb", password="pw")
        resp = self.client.get(reverse("students:student_detail", kwargs={"pk": self.violet.pk}))
        self.assertContains(resp, reverse("students:student_work", kwargs={
            "pk": self.violet.pk, "curriculum_id": self.cur.pk,
        }))

    def test_other_family_cannot_browse(self):
        self.client.login(username="wb2", password="pw")
        r1 = self.client.get(reverse("students:student_work", kwargs={
            "pk": self.violet.pk, "curriculum_id": self.cur.pk,
        }))
        r2 = self.client.get(reverse("students:student_work_set", kwargs={
            "pk": self.violet.pk, "set_pk": self.qset.pk,
        }))
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 404)

    def test_sibling_pinned_set_hidden_from_other_child(self):
        # A set pinned to a sibling isn't this child's work (mirrors the portal).
        from tutor.models import QuestionSet
        kaylin = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07", family=self.family,
        )
        pinned = QuestionSet.objects.create(
            lesson=self.lesson, title="Kaylin-only set", family=self.family,
            status=QuestionSet.APPROVED, child=kaylin,
        )
        self.client.login(username="wb", password="pw")
        listing = self.client.get(reverse("students:student_work", kwargs={
            "pk": self.violet.pk, "curriculum_id": self.cur.pk,
        }))
        self.assertNotContains(listing, "Kaylin-only set")               # not in Violet's list
        direct = self.client.get(reverse("students:student_work_set", kwargs={
            "pk": self.violet.pk, "set_pk": pinned.pk,
        }))
        self.assertEqual(direct.status_code, 404)                        # nor reachable directly

    def test_survives_deleted_work_entry_without_500(self):
        # Submitting creates a WorkLogEntry; deleting it must not crash the page.
        from tutor.models import Question, QuestionSet
        q = Question.objects.create(question_set=self.qset, order=3, category="comprehension",
                                    prompt="One more?")
        self.client.login(username="wb", password="pw")
        # (violet's sheet already exists; give it a submitted state via the portal path)
        from portal.tokens import make_portal_token
        token = make_portal_token(self.violet)
        self.client.post(reverse("portal:portal_questions", kwargs={"token": token, "set_pk": self.qset.pk}),
                         data={f"answer_{q.pk}": "Yes."})
        sheet = self.qset.responses.get(child=self.violet)
        self.assertTrue(sheet.is_submitted)
        sheet.work_entry.delete()   # parent deletes the work-log entry later
        self.client.login(username="wb", password="pw")
        resp = self.client.get(reverse("students:student_work_set", kwargs={
            "pk": self.violet.pk, "set_pk": self.qset.pk,
        }))
        self.assertEqual(resp.status_code, 200)                          # no NoReverseMatch 500

    def test_empty_structured_answer_reads_as_no_answer(self):
        # Only-wrong matching attempts store JSON but display as "(no answer)".
        import json
        from tutor.models import Question, QuestionSet, ResponseSheet
        mset = QuestionSet.objects.create(
            lesson=self.lesson, title="Vocab match", family=self.family, status=QuestionSet.APPROVED,
        )
        mq = Question.objects.create(
            question_set=mset, order=1, category="vocabulary",
            response_type=Question.TYPE_MATCHING,
            passage=json.dumps({"words": ["a"], "definitions": [{"n": 1, "text": "first", "word": "a"}]}),
        )
        ResponseSheet.objects.create(
            question_set=mset, child=self.violet,
            answers={str(mq.pk): json.dumps({"matches": {}, "tries": 3})},
        )
        self.client.login(username="wb", password="pw")
        resp = self.client.get(reverse("students:student_work_set", kwargs={
            "pk": self.violet.pk, "set_pk": mset.pk,
        }))
        self.assertContains(resp, "No answer")             # clean empty state
        self.assertNotContains(resp, "ss-answer-block")    # not a filled green card


class ActivityFormRenderTests(TestCase):
    """The redesigned add-activity form has real Bootstrap controls + emoji picker."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent = User.objects.create_user(username="af", email="af@e.com", password="pw")
        cls.family = Family.objects.create(name="AF Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        Student.objects.create(parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)

    def test_form_has_styled_controls_and_emoji_picker(self):
        self.client.login(username="af", password="pw")
        resp = self.client.get(reverse("activities:activity_create"))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("activity-emoji-picker", html)
        self.assertIn("activity-emoji-choice", html)
        self.assertIn('class="form-control form-control-lg"', html)   # title styled
        self.assertIn("form-select", html)                            # child/cadence dropdowns
        self.assertIn("form-switch", html)                            # active toggle
        self.assertNotIn("btn-primary", html)                         # AURORA amber, not stock blue
