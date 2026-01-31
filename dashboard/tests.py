from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from assignments.models import Assignment
from curricula.models import Curriculum
from students.models import Student


class DashboardViewTests(TestCase):
    """Tests for the parent progress dashboard."""

    @classmethod
    def setUpTestData(cls):
        # ── Users ──
        cls.parent = CustomUser.objects.create_user(
            username="parent1",
            email="parent1@test.com",
            password="testpass123",
        )
        cls.other_parent = CustomUser.objects.create_user(
            username="parent2",
            email="parent2@test.com",
            password="testpass123",
        )

        # ── Students ──
        cls.child_a = Student.objects.create(
            parent=cls.parent,
            first_name="Alice",
            grade_level="G03",
        )
        cls.child_b = Student.objects.create(
            parent=cls.parent,
            first_name="Bob",
            grade_level="G05",
        )
        cls.other_child = Student.objects.create(
            parent=cls.other_parent,
            first_name="Other",
            grade_level="G01",
        )

        # ── Curricula ──
        cls.math = Curriculum.objects.create(
            parent=cls.parent,
            name="Math 3A",
            subject="Math",
        )
        cls.science = Curriculum.objects.create(
            parent=cls.parent,
            name="Science 5",
            subject="Science",
        )
        cls.other_curriculum = Curriculum.objects.create(
            parent=cls.other_parent,
            name="Other Curr",
            subject="Art",
        )

        today = date.today()

        # ── Assignments for parent ──
        # Completed assignment (Alice, Math, past due)
        cls.a1 = Assignment.objects.create(
            parent=cls.parent,
            child=cls.child_a,
            curriculum=cls.math,
            title="Completed Math HW",
            due_date=today - timedelta(days=3),
            status=Assignment.COMPLETE,
        )
        # Overdue assignment (Alice, Science, past due, not complete)
        cls.a2 = Assignment.objects.create(
            parent=cls.parent,
            child=cls.child_a,
            curriculum=cls.science,
            title="Overdue Science HW",
            due_date=today - timedelta(days=1),
            status=Assignment.PENDING,
        )
        # Pending assignment (Bob, Math, future due)
        cls.a3 = Assignment.objects.create(
            parent=cls.parent,
            child=cls.child_b,
            curriculum=cls.math,
            title="Future Math HW",
            due_date=today + timedelta(days=7),
            status=Assignment.PENDING,
        )
        # In-progress assignment (Bob, Science, future due)
        cls.a4 = Assignment.objects.create(
            parent=cls.parent,
            child=cls.child_b,
            curriculum=cls.science,
            title="InProgress Science HW",
            due_date=today + timedelta(days=14),
            status=Assignment.IN_PROGRESS,
        )

        # ── Assignment for OTHER parent (should never appear) ──
        cls.other_assignment = Assignment.objects.create(
            parent=cls.other_parent,
            child=cls.other_child,
            curriculum=cls.other_curriculum,
            title="Other Parent HW",
            due_date=today,
            status=Assignment.PENDING,
        )

        cls.url = reverse("dashboard:dashboard")

    # ── 1. Requires login ─────────────────────────────────────────────────

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    # ── 2. Only shows logged-in user's data ───────────────────────────────

    def test_only_own_assignments_shown(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Summary should reflect parent1's 4 assignments
        self.assertEqual(response.context["summary"]["total"], 4)
        self.assertEqual(response.context["summary"]["completed"], 1)
        self.assertEqual(response.context["summary"]["not_completed"], 3)
        self.assertEqual(response.context["summary"]["overdue"], 1)

        # Other parent's assignment title must not appear in HTML
        self.assertNotContains(response, "Other Parent HW")

    # ── 3. Filter by child_id ─────────────────────────────────────────────

    def test_filter_by_child(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(self.url, {"child_id": self.child_a.id})
        self.assertEqual(response.status_code, 200)

        # Alice has 2 assignments (a1 complete, a2 overdue)
        self.assertEqual(response.context["summary"]["total"], 2)
        self.assertEqual(response.context["summary"]["completed"], 1)
        self.assertEqual(response.context["summary"]["overdue"], 1)

    # ── 4. Filter by curriculum_id ────────────────────────────────────────

    def test_filter_by_curriculum(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            self.url, {"curriculum_id": self.math.id}
        )
        self.assertEqual(response.status_code, 200)

        # Math has 2 assignments (a1 complete, a3 pending future)
        self.assertEqual(response.context["summary"]["total"], 2)
        self.assertEqual(response.context["summary"]["completed"], 1)
        self.assertEqual(response.context["summary"]["overdue"], 0)

    # ── 5. Date range filter ──────────────────────────────────────────────

    def test_date_range_filter(self):
        self.client.login(username="parent1", password="testpass123")
        today = date.today()
        # Range that only includes a2 (overdue, yesterday) and a1 (3 days ago)
        start = (today - timedelta(days=5)).isoformat()
        end = (today - timedelta(days=1)).isoformat()
        response = self.client.get(
            self.url, {"start_date": start, "end_date": end}
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["summary"]["total"], 2)
        self.assertEqual(response.context["summary"]["completed"], 1)
        self.assertEqual(response.context["summary"]["overdue"], 1)

    # ── 6. Overdue logic correct ──────────────────────────────────────────

    def test_overdue_logic(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(self.url)

        # Only a2 is overdue (past due + not complete)
        self.assertEqual(response.context["summary"]["overdue"], 1)

        # a1 is past due but COMPLETE, so not overdue
        # a3, a4 are future, so not overdue
        assignments = list(response.context["assignments"])
        overdue_assignments = [a for a in assignments if a.is_overdue]
        self.assertEqual(len(overdue_assignments), 1)
        self.assertEqual(overdue_assignments[0].title, "Overdue Science HW")

    # ── 7. Assignment detail links in rendered HTML ───────────────────────

    def test_assignment_detail_links(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Each of parent1's assignments should have a detail link
        for assignment in [self.a1, self.a2, self.a3, self.a4]:
            detail_url = reverse(
                "assignments:assignment_detail", args=[assignment.pk]
            )
            self.assertContains(response, detail_url)

    # ── 8. Other user filter IDs produce empty results (no crash) ─────────

    def test_filter_other_users_child_returns_empty(self):
        self.client.login(username="parent1", password="testpass123")
        response = self.client.get(
            self.url, {"child_id": self.other_child.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"]["total"], 0)


class TeacherDashboardViewTests(TestCase):
    """Tests that teachers can view the dashboard for their family."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent_user = CustomUser.objects.create_user(
            username="td_parent", email="td_parent@test.com", password="testpass123",
        )
        cls.teacher_user = CustomUser.objects.create_user(
            username="td_teacher", email="td_teacher@test.com", password="testpass123",
        )
        cls.family = Family.objects.create(name="Teacher Dash Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.teacher_user, family=cls.family, role="teacher",
        )
        cls.child = Student.objects.create(
            parent=cls.parent_user, first_name="DashChild", grade_level="G03",
            family=cls.family,
        )
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent_user, name="Dash Math", subject="Math",
            family=cls.family,
        )
        cls.assignment = Assignment.objects.create(
            parent=cls.parent_user,
            child=cls.child,
            curriculum=cls.curriculum,
            title="Dash Assignment",
            due_date=date.today(),
            family=cls.family,
        )
        cls.url = reverse("dashboard:dashboard")

    def test_teacher_can_view_dashboard(self):
        self.client.login(username="td_teacher", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_teacher_sees_family_assignments(self):
        self.client.login(username="td_teacher", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["summary"]["total"], 1)
        self.assertContains(response, "Dash Assignment")


class FamilySwitcherDashboardTests(TestCase):
    """Tests for family-scoped dashboard with family switching."""

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership

        cls.parent_user = CustomUser.objects.create_user(
            username="sw_parent", email="sw_parent@test.com", password="testpass123",
        )
        cls.family_a = Family.objects.create(name="Switcher A Family")
        cls.family_b = Family.objects.create(name="Switcher B Family")
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family_a, role="parent",
        )
        FamilyMembership.objects.create(
            user=cls.parent_user, family=cls.family_b, role="parent",
        )

        # Data in family A
        cls.child_a = Student.objects.create(
            parent=cls.parent_user, first_name="ChildA", grade_level="G03",
            family=cls.family_a,
        )
        cls.curr_a = Curriculum.objects.create(
            parent=cls.parent_user, name="Math A", subject="Math",
            family=cls.family_a,
        )
        cls.assign_a = Assignment.objects.create(
            parent=cls.parent_user, child=cls.child_a, curriculum=cls.curr_a,
            title="Assignment A", due_date=date.today(), family=cls.family_a,
        )

        # Data in family B
        cls.child_b = Student.objects.create(
            parent=cls.parent_user, first_name="ChildB", grade_level="G05",
            family=cls.family_b,
        )
        cls.curr_b = Curriculum.objects.create(
            parent=cls.parent_user, name="Math B", subject="Math",
            family=cls.family_b,
        )
        cls.assign_b = Assignment.objects.create(
            parent=cls.parent_user, child=cls.child_b, curriculum=cls.curr_b,
            title="Assignment B", due_date=date.today(), family=cls.family_b,
        )

        cls.url = reverse("dashboard:dashboard")

    def test_default_shows_first_family(self):
        self.client.login(username="sw_parent", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"]["total"], 1)
        self.assertContains(response, "Assignment A")
        self.assertNotContains(response, "Assignment B")

    def test_switch_family_shows_other_data(self):
        self.client.login(username="sw_parent", password="testpass123")
        response = self.client.get(self.url, {"family_id": self.family_b.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"]["total"], 1)
        self.assertContains(response, "Assignment B")
        self.assertNotContains(response, "Assignment A")

    def test_session_persists_family_selection(self):
        self.client.login(username="sw_parent", password="testpass123")
        # First request: switch to family B
        self.client.get(self.url, {"family_id": self.family_b.id})
        # Second request: no family_id param
        response = self.client.get(self.url)
        self.assertEqual(response.context["summary"]["total"], 1)
        self.assertContains(response, "Assignment B")

    def test_filter_dropdowns_scoped_to_selected_family(self):
        self.client.login(username="sw_parent", password="testpass123")
        # Default: family A selected
        response = self.client.get(self.url)
        children = list(response.context["children"])
        curricula_list = list(response.context["curricula"])
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].first_name, "ChildA")
        self.assertEqual(len(curricula_list), 1)
        self.assertEqual(curricula_list[0].name, "Math A")
