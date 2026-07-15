from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Family, FamilyMembership
from students.models import Student
from worklog.models import WorkLogEntry

from .models import ExternalActivity

User = get_user_model()


class ExternalActivityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ap", email="ap@e.com", password="pw")
        cls.family = Family.objects.create(name="Act Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.kaylin = Student.objects.create(parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)

        cls.v_guitar = ExternalActivity.objects.create(
            parent=cls.parent, family=cls.family, student=cls.violet, title="Guitar",
            provider="School of Rock", url="https://sor.example/", emoji="🎸",
        )
        cls.k_drums = ExternalActivity.objects.create(
            parent=cls.parent, family=cls.family, student=cls.kaylin, title="Drums",
            provider="School of Rock", url="https://sor.example/", emoji="🥁",
        )
        cls.coding = ExternalActivity.objects.create(
            parent=cls.parent, family=cls.family, student=None, title="Coding",
            provider="CodaKid", url="https://codakid.example/", emoji="💻",
        )

    def test_parent_list_shows_all_family_activities(self):
        self.client.login(username="ap", password="pw")
        resp = self.client.get(reverse("activities:activity_list"))
        self.assertEqual(resp.status_code, 200)
        for label in ("Guitar", "Drums", "Coding", "School of Rock", "CodaKid"):
            self.assertContains(resp, label)

    def test_portal_scopes_activities_per_child(self):
        from portal.views import _visible_activities

        v = set(_visible_activities(self.violet).values_list("pk", flat=True))
        self.assertEqual(v, {self.v_guitar.pk, self.coding.pk})   # her guitar + family coding
        self.assertNotIn(self.k_drums.pk, v)                      # NOT Kaylin's drums
        k = set(_visible_activities(self.kaylin).values_list("pk", flat=True))
        self.assertEqual(k, {self.k_drums.pk, self.coding.pk})

    def test_inactive_hidden_from_portal(self):
        from portal.views import _visible_activities

        self.coding.is_active = False
        self.coding.save()
        self.assertNotIn(self.coding.pk, set(_visible_activities(self.violet).values_list("pk", flat=True)))

    def test_cross_family_not_visible(self):
        other = User.objects.create_user(username="ap2", email="ap2@e.com", password="pw")
        fam2 = Family.objects.create(name="Other")
        FamilyMembership.objects.create(user=other, family=fam2, role="parent")
        ExternalActivity.objects.create(parent=other, family=fam2, title="Secret", url="https://x.example/")
        self.client.login(username="ap", password="pw")
        resp = self.client.get(reverse("activities:activity_list"))
        self.assertNotContains(resp, "Secret")

    def test_create_requires_editor(self):
        self.client.login(username="ap", password="pw")
        resp = self.client.post(reverse("activities:activity_create"), data={
            "title": "Piano", "provider": "Local", "url": "https://p.example/",
            "emoji": "🎹", "cadence": "weekly",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ExternalActivity.objects.filter(title="Piano", parent=self.parent).exists())

    def test_is_due_logic(self):
        today = timezone.localdate()
        a = ExternalActivity.objects.create(
            parent=self.parent, family=self.family, title="Weekly", url="https://w.example/",
            cadence=ExternalActivity.CADENCE_WEEKLY,
        )
        self.assertTrue(a.is_due)                                  # never logged → due
        a.last_logged_at = today
        self.assertFalse(a.is_due)                                 # just logged
        a.last_logged_at = today - timedelta(days=8)
        self.assertTrue(a.is_due)                                  # a week+ ago
        a.snoozed_until = today + timedelta(days=1)
        self.assertFalse(a.is_due)                                 # snoozed
        a.snoozed_until = None
        a.is_muted = True
        self.assertFalse(a.is_due)                                 # muted

    def test_seed_activities_command(self):
        call_command("seed_activities", "--for-user", "ap")
        # guitar+drums per child (2x2) + CodaKid family-wide, on top of the 3 in setUp
        self.assertTrue(ExternalActivity.objects.filter(provider="CodaKid").exists())
        self.assertTrue(
            ExternalActivity.objects.filter(provider="School of Rock", title="Guitar", student=self.violet).exists()
        )


class ActivityCheckinTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="cp", email="cp@e.com", password="pw")
        cls.family = Family.objects.create(name="Checkin Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.kaylin = Student.objects.create(parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)

    def _activity(self, **kw):
        defaults = dict(
            parent=self.parent, family=self.family, title="Guitar",
            provider="School of Rock", url="https://sor.example/",
            cadence=ExternalActivity.CADENCE_WEEKLY,
        )
        defaults.update(kw)
        return ExternalActivity.objects.create(**defaults)

    def test_home_surfaces_due_activity_for_parent(self):
        self._activity(student=self.violet)
        self.client.login(username="cp", password="pw")
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Quick check-in")
        self.assertContains(resp, "Did Violet do Guitar")

    def test_log_creates_worklog_and_stamps_activity(self):
        from worklog.models import WorkLogEntry

        activity = self._activity(student=self.violet)
        self.client.login(username="cp", password="pw")
        resp = self.client.post(
            reverse("activities:activity_checkin", args=[activity.pk]), data={"action": "log"},
        )
        self.assertEqual(resp.status_code, 302)
        activity.refresh_from_db()
        self.assertEqual(activity.last_logged_at, timezone.localdate())
        self.assertFalse(activity.is_due)                          # logged → not due
        entries = WorkLogEntry.objects.filter(child=self.violet, subject="Guitar")
        self.assertEqual(entries.count(), 1)

    def test_log_family_wide_creates_entry_per_child(self):
        from worklog.models import WorkLogEntry

        activity = self._activity(student=None, title="Coding", provider="CodaKid")
        self.client.login(username="cp", password="pw")
        self.client.post(reverse("activities:activity_checkin", args=[activity.pk]), data={"action": "log"})
        # one WorkLogEntry for each child in the family
        self.assertEqual(WorkLogEntry.objects.filter(subject="Coding").count(), 2)

    def test_snooze_hides_until_tomorrow(self):
        activity = self._activity(student=self.violet)
        self.client.login(username="cp", password="pw")
        self.client.post(reverse("activities:activity_checkin", args=[activity.pk]), data={"action": "snooze"})
        activity.refresh_from_db()
        self.assertEqual(activity.snoozed_until, timezone.localdate() + timedelta(days=1))
        self.assertFalse(activity.is_due)

    def test_mute_stops_prompting(self):
        activity = self._activity(student=self.violet)
        self.client.login(username="cp", password="pw")
        self.client.post(reverse("activities:activity_checkin", args=[activity.pk]), data={"action": "mute"})
        activity.refresh_from_db()
        self.assertTrue(activity.is_muted)
        self.assertFalse(activity.is_due)

    def test_checkin_requires_login(self):
        activity = self._activity(student=self.violet)
        resp = self.client.post(reverse("activities:activity_checkin", args=[activity.pk]), data={"action": "log"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login", resp["Location"])

    def test_checkin_get_not_allowed(self):
        activity = self._activity(student=self.violet)
        self.client.login(username="cp", password="pw")
        resp = self.client.get(reverse("activities:activity_checkin", args=[activity.pk]))
        self.assertEqual(resp.status_code, 405)

    def test_cannot_checkin_other_family_activity(self):
        other = User.objects.create_user(username="cp2", email="cp2@e.com", password="pw")
        fam2 = Family.objects.create(name="Other")
        FamilyMembership.objects.create(user=other, family=fam2, role="parent")
        theirs = ExternalActivity.objects.create(
            parent=other, family=fam2, title="Secret", url="https://x.example/",
        )
        self.client.login(username="cp", password="pw")
        resp = self.client.post(
            reverse("activities:activity_checkin", args=[theirs.pk]), data={"action": "mute"},
        )
        self.assertEqual(resp.status_code, 404)
        theirs.refresh_from_db()
        self.assertFalse(theirs.is_muted)

    def test_log_is_idempotent_for_the_day(self):
        from worklog.models import WorkLogEntry

        activity = self._activity(student=self.violet)
        self.client.login(username="cp", password="pw")
        url = reverse("activities:activity_checkin", args=[activity.pk])
        self.client.post(url, data={"action": "log"})
        self.client.post(url, data={"action": "log"})   # double-click
        self.assertEqual(WorkLogEntry.objects.filter(child=self.violet, subject="Guitar").count(), 1)

    def test_log_truncates_long_title_to_worklog_subject(self):
        from worklog.models import WorkLogEntry

        long_title = "G" * 150
        activity = self._activity(student=self.violet, title=long_title)
        self.client.login(username="cp", password="pw")
        self.client.post(reverse("activities:activity_checkin", args=[activity.pk]), data={"action": "log"})
        entry = WorkLogEntry.objects.get(child=self.violet)
        self.assertLessEqual(len(entry.subject), 100)   # WorkLogEntry.subject max_length

    def test_log_ignores_supplied_next_redirect(self):
        activity = self._activity(student=self.violet)
        self.client.login(username="cp", password="pw")
        resp = self.client.post(
            reverse("activities:activity_checkin", args=[activity.pk]),
            data={"action": "snooze", "next": "https://evil.example/"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn("evil.example", resp["Location"])


class NullFamilyCheckinTests(TestCase):
    """A legacy/no-membership user's null-family activity must never fan out
    into another user's records (adversarial-review findings #1 and #3)."""

    @classmethod
    def setUpTestData(cls):
        # Two legacy users with NO family memberships → get_active_family == None.
        cls.a = User.objects.create_user(username="lega", email="a@e.com", password="pw")
        cls.b = User.objects.create_user(username="legb", email="b@e.com", password="pw")
        cls.a_kid = Student.objects.create(parent=cls.a, first_name="Amy", grade_level="G03")
        cls.b_kid = Student.objects.create(parent=cls.b, first_name="Bo", grade_level="G03")
        # A whole-family (student=None) activity owned by A, with no family.
        cls.a_activity = ExternalActivity.objects.create(
            parent=cls.a, family=None, student=None, title="Coding",
            provider="CodaKid", url="https://c.example/",
            cadence=ExternalActivity.CADENCE_WEEKLY,
        )
        # B's own null-family whole-family activity.
        cls.b_activity = ExternalActivity.objects.create(
            parent=cls.b, family=None, student=None, title="Piano",
            url="https://p.example/",
        )

    def test_log_does_not_reach_other_users_children(self):
        from worklog.models import WorkLogEntry

        self.client.login(username="lega", password="pw")
        self.client.post(reverse("activities:activity_checkin", args=[self.a_activity.pk]), data={"action": "log"})
        # Only A's null-family child gets an entry; B's child is untouched.
        self.assertTrue(WorkLogEntry.objects.filter(child=self.a_kid, subject="Coding").exists())
        self.assertFalse(WorkLogEntry.objects.filter(child=self.b_kid).exists())

    def test_portal_null_family_does_not_leak_other_users_activities(self):
        from portal.views import _visible_activities

        visible = set(_visible_activities(self.a_kid).values_list("pk", flat=True))
        self.assertIn(self.a_activity.pk, visible)       # A's own whole-family activity
        self.assertNotIn(self.b_activity.pk, visible)    # NOT B's null-family activity


class ActivityLogTests(TestCase):
    """Log a session for multiple chosen children on a chosen (back-dateable) date."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="lp", email="lp@e.com", password="pw")
        cls.family = Family.objects.create(name="Log Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.kaylin = Student.objects.create(parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)
        cls.jj = ExternalActivity.objects.create(
            parent=cls.parent, family=cls.family, student=None, title="Jiu Jitsu",
            provider="Dojo", url="https://dojo.example/", emoji="🥋",
        )
        cls.today = timezone.localdate()

    def _url(self):
        return reverse("activities:activity_log", kwargs={"pk": self.jj.pk})

    def test_form_renders_children_and_date(self):
        self.client.login(username="lp", password="pw")
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Violet")
        self.assertContains(resp, "Kaylin")
        self.assertContains(resp, 'type="date"')

    def test_logs_one_entry_per_child_on_chosen_date(self):
        self.client.login(username="lp", password="pw")
        when = self.today - timedelta(days=3)   # a forgotten day
        resp = self.client.post(self._url(), {
            "children": [self.violet.pk, self.kaylin.pk], "date": when.isoformat(),
        })
        self.assertEqual(resp.status_code, 302)
        entries = WorkLogEntry.objects.filter(subject="Jiu Jitsu", date=when)
        self.assertEqual(entries.count(), 2)
        self.assertEqual({e.child_id for e in entries}, {self.violet.pk, self.kaylin.pk})

    def test_can_log_a_single_child(self):
        self.client.login(username="lp", password="pw")
        self.client.post(self._url(), {"children": [self.kaylin.pk], "date": self.today.isoformat()})
        self.assertEqual(WorkLogEntry.objects.filter(child=self.kaylin, subject="Jiu Jitsu").count(), 1)
        self.assertEqual(WorkLogEntry.objects.filter(child=self.violet, subject="Jiu Jitsu").count(), 0)

    def test_relogging_same_day_is_deduped(self):
        self.client.login(username="lp", password="pw")
        data = {"children": [self.violet.pk], "date": self.today.isoformat()}
        self.client.post(self._url(), data)
        self.client.post(self._url(), data)
        self.assertEqual(
            WorkLogEntry.objects.filter(child=self.violet, subject="Jiu Jitsu", date=self.today).count(), 1)

    def test_future_date_rejected(self):
        self.client.login(username="lp", password="pw")
        resp = self.client.post(self._url(), {
            "children": [self.violet.pk], "date": (self.today + timedelta(days=2)).isoformat(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "future")
        self.assertEqual(WorkLogEntry.objects.filter(subject="Jiu Jitsu").count(), 0)

    def test_no_children_selected_errors(self):
        self.client.login(username="lp", password="pw")
        resp = self.client.post(self._url(), {"children": [], "date": self.today.isoformat()})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(WorkLogEntry.objects.count(), 0)

    def test_viewer_cannot_log(self):
        teacher = User.objects.create_user(username="lt", email="lt@e.com", password="pw")
        FamilyMembership.objects.create(user=teacher, family=self.family, role="teacher")
        self.client.login(username="lt", password="pw")
        self.assertEqual(self.client.get(self._url()).status_code, 404)
