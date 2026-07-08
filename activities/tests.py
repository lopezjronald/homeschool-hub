from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Family, FamilyMembership
from students.models import Student

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
