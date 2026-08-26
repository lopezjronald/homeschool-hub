import re
import shutil
import subprocess
from datetime import date, time
from pathlib import Path

from django.test import SimpleTestCase

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Family, FamilyMembership
from students.models import Student

from .models import CalendarEvent

User = get_user_model()


class RecurrenceTests(TestCase):
    """occurrences() is the heart of the model — exact date-list assertions."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="cp", email="cp@e.com", password="pw")

    def _event(self, **kw):
        base = {"parent": self.parent, "title": "Jiu-jitsu",
                "event_type": CalendarEvent.TYPE_ACTIVITY, "date": date(2026, 8, 11)}
        base.update(kw)
        return CalendarEvent.objects.create(**base)

    def test_single_event_only_inside_window(self):
        e = self._event()
        self.assertEqual(e.occurrences(date(2026, 8, 1), date(2026, 8, 31)), [date(2026, 8, 11)])
        self.assertEqual(e.occurrences(date(2026, 9, 1), date(2026, 9, 30)), [])
        # Inclusive boundaries — the event ON the window edge counts.
        self.assertEqual(e.occurrences(date(2026, 8, 11), date(2026, 8, 11)), [date(2026, 8, 11)])

    def test_weekly_series_exact_dates_with_skip_and_until(self):
        # Anchor Tue Aug 11 2026; repeats Tue+Thu until Thu Aug 27 (inclusive);
        # Tue Aug 18 cancelled. Expected: 11, 13, 20, 25, 27.
        e = self._event(
            repeats_weekly=True, repeat_weekdays=[1, 3],
            repeat_until=date(2026, 8, 27), skip_dates=["2026-08-18"],
        )
        self.assertEqual(
            e.occurrences(date(2026, 8, 1), date(2026, 9, 30)),
            [date(2026, 8, 11), date(2026, 8, 13), date(2026, 8, 20),
             date(2026, 8, 25), date(2026, 8, 27)],
        )

    def test_empty_weekday_list_falls_back_to_anchor_weekday(self):
        # Anchor is a Tuesday; with no weekday list the series is every Tuesday.
        e = self._event(repeats_weekly=True, repeat_until=date(2026, 8, 31))
        self.assertEqual(
            e.occurrences(date(2026, 8, 1), date(2026, 9, 30)),
            [date(2026, 8, 11), date(2026, 8, 18), date(2026, 8, 25)],
        )

    def test_series_never_starts_before_its_anchor(self):
        e = self._event(repeats_weekly=True, repeat_until=date(2026, 8, 31))
        occ = e.occurrences(date(2026, 7, 1), date(2026, 8, 31))
        self.assertEqual(occ[0], date(2026, 8, 11))          # not Aug 4

    def test_open_ended_series_is_bounded_by_the_window(self):
        e = self._event(repeats_weekly=True)                  # no repeat_until
        occ = e.occurrences(date(2026, 8, 11), date(2027, 8, 11))
        self.assertEqual(len(occ), 53)                        # one per week, window-bounded

    def test_bad_json_shapes_are_tolerated(self):
        e = self._event(repeats_weekly=True, repeat_weekdays=["x", 9, 1],
                        skip_dates=[None, "2026-08-11"], repeat_until=date(2026, 8, 18))
        # Invalid weekday entries drop out (leaving Tue), the None skip is ignored,
        # and the valid skip removes the anchor date.
        self.assertEqual(e.occurrences(date(2026, 8, 1), date(2026, 8, 31)),
                         [date(2026, 8, 18)])


class FeedTests(TestCase):
    """The parent feed: scoping is the whole security story."""

    @classmethod
    def setUpTestData(cls):
        cls.parent_a = User.objects.create_user(username="fa", email="fa@e.com", password="pw")
        cls.family_a = Family.objects.create(name="Fam A")
        FamilyMembership.objects.create(user=cls.parent_a, family=cls.family_a, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent_a, first_name="Violet", grade_level="G03", family=cls.family_a)
        cls.kaylin = Student.objects.create(
            parent=cls.parent_a, first_name="Kaylin", grade_level="G07", family=cls.family_a)

        cls.parent_b = User.objects.create_user(username="fb", email="fb@e.com", password="pw")
        cls.family_b = Family.objects.create(name="Fam B")
        FamilyMembership.objects.create(user=cls.parent_b, family=cls.family_b, role="parent")
        cls.other_kid = Student.objects.create(
            parent=cls.parent_b, first_name="Zed", grade_level="G05", family=cls.family_b)

        cls.jj = CalendarEvent.objects.create(
            parent=cls.parent_a, family=cls.family_a, child=cls.violet,
            title="Jiu-jitsu", event_type=CalendarEvent.TYPE_ACTIVITY,
            date=date(2026, 9, 1),
        )
        cls.family_wide = CalendarEvent.objects.create(
            parent=cls.parent_a, family=cls.family_a, child=None,
            title="Zoo trip", event_type=CalendarEvent.TYPE_OTHER, date=date(2026, 9, 2),
        )
        cls.foreign = CalendarEvent.objects.create(
            parent=cls.parent_b, family=cls.family_b, child=cls.other_kid,
            title="Secret B thing", event_type=CalendarEvent.TYPE_OTHER, date=date(2026, 9, 1),
        )

    def _feed(self, **params):
        base = {"start": "2026-09-01", "end": "2026-09-30"}
        base.update(params)
        return self.client.get(reverse("family_calendar:feed"), base)

    def test_feed_is_family_isolated_both_directions(self):
        self.client.login(username="fa", password="pw")
        titles = [e["title"] for e in self._feed().json()]
        self.assertTrue(any("Jiu-jitsu" in t for t in titles))
        self.assertTrue(any("Zoo trip" in t for t in titles))
        self.assertFalse(any("Secret B thing" in t for t in titles))

        self.client.login(username="fb", password="pw")
        titles = [e["title"] for e in self._feed().json()]
        self.assertTrue(any("Secret B thing" in t for t in titles))
        self.assertFalse(any("Jiu-jitsu" in t for t in titles))

    def test_children_filter_narrows_but_family_wide_stays(self):
        self.client.login(username="fa", password="pw")
        titles = [e["title"] for e in self._feed(children=str(self.kaylin.pk)).json()]
        self.assertFalse(any("Jiu-jitsu" in t for t in titles))   # Violet's filtered out
        self.assertTrue(any("Zoo trip" in t for t in titles))     # family-wide always shows

    def test_foreign_child_id_in_filter_is_dropped(self):
        # Filtering by another family's child must not leak their events — and,
        # because the foreign id is discarded, the wanted-set is empty so only
        # family-wide events remain.
        self.client.login(username="fa", password="pw")
        titles = [e["title"] for e in self._feed(children=str(self.other_kid.pk)).json()]
        self.assertFalse(any("Secret B thing" in t for t in titles))
        self.assertFalse(any("Jiu-jitsu" in t for t in titles))
        self.assertTrue(any("Zoo trip" in t for t in titles))

    def test_garbage_window_returns_defaults_not_500(self):
        self.client.login(username="fa", password="pw")
        resp = self._feed(start="not-a-date", end="2026-99-99")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_giant_window_is_clamped(self):
        weekly = CalendarEvent.objects.create(
            parent=self.parent_a, family=self.family_a, title="Forever",
            event_type=CalendarEvent.TYPE_ACTIVITY, date=date(2026, 9, 7),
            repeats_weekly=True,                                  # open-ended
        )
        self.client.login(username="fa", password="pw")
        payload = self._feed(start="2026-09-01", end="2036-09-01").json()
        forever = [e for e in payload if "Forever" in e["title"]]
        # 400-day clamp => at most ~58 weekly occurrences, never ~520.
        self.assertLessEqual(len(forever), 58)
        self.assertGreater(len(forever), 50)

    def test_feed_requires_login(self):
        resp = self._feed()
        self.assertEqual(resp.status_code, 302)                  # → login

    def test_spanish_is_one_family_chip_per_day_not_one_per_child(self):
        # Two kids: the parent view must NOT get a pair of identical daily chips
        # (they drowned the month grid — UI review finding 1).
        from datetime import date, timedelta
        from django.utils import timezone

        today = timezone.localdate()
        self.client.login(username="fa", password="pw")
        payload = self._feed(start=today.isoformat(),
                             end=(today + timedelta(days=6)).isoformat()).json()
        spanish = [e for e in payload if e["extendedProps"]["layer"] == "spanish"]
        weekdays = sum(1 for i in range(7) if (today + timedelta(days=i)).weekday() < 5)
        self.assertEqual(len(spanish), weekdays)              # one per day, not ×2
        self.assertTrue(all(e["title"] == "📖 Español" for e in spanish))
        # Every layer chip carries a sort priority so real events win the row.
        self.assertTrue(all("prio" in e["extendedProps"] for e in spanish))

    def test_all_day_vs_timed_shapes(self):
        from datetime import time
        CalendarEvent.objects.create(
            parent=self.parent_a, family=self.family_a, child=self.violet,
            title="Timed", event_type=CalendarEvent.TYPE_APPOINTMENT,
            date=date(2026, 9, 3), start_time=time(16, 30), end_time=time(17, 30),
        )
        self.client.login(username="fa", password="pw")
        by_title = {e["title"]: e for e in self._feed().json()}
        timed = next(v for k, v in by_title.items() if "Timed" in k)
        self.assertEqual(timed["start"], "2026-09-03T16:30:00")
        self.assertEqual(timed["end"], "2026-09-03T17:30:00")
        self.assertFalse(timed["allDay"])
        zoo = next(v for k, v in by_title.items() if "Zoo trip" in k)
        self.assertEqual(zoo["start"], "2026-09-02")
        self.assertTrue(zoo["allDay"])


class CrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="cr", email="cr@e.com", password="pw")
        cls.family = Family.objects.create(name="Crud Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.viewer = User.objects.create_user(username="tv", email="tv@e.com", password="pw")
        FamilyMembership.objects.create(user=cls.viewer, family=cls.family, role="teacher")

    def test_day_click_prefills_the_add_form(self):
        self.client.login(username="cr", password="pw")
        resp = self.client.get(reverse("family_calendar:event_create"), {"date": "2026-09-15"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'value="2026-09-15"')

    def test_create_and_calendar_page(self):
        self.client.login(username="cr", password="pw")
        resp = self.client.post(reverse("family_calendar:event_create"), {
            "title": "LRM with Mrs. Lee", "event_type": "charter",
            "date": "2026-09-10", "start_time": "10:00", "end_time": "11:00",
            "child": "", "location": "Zoom", "repeat_weekdays": [], "notes": "",
        })
        self.assertEqual(resp.status_code, 302)
        event = CalendarEvent.objects.get(title="LRM with Mrs. Lee")
        self.assertEqual(event.family, self.family)
        self.assertEqual(event.event_type, CalendarEvent.TYPE_CHARTER)
        page = self.client.get(reverse("family_calendar:calendar"))
        self.assertContains(page, "Violet")                      # legend
        self.assertContains(page, "fullcalendar@")               # pinned CDN tag

    def test_break_event_forces_all_day(self):
        self.client.login(username="cr", password="pw")
        self.client.post(reverse("family_calendar:event_create"), {
            "title": "Spring break", "event_type": "break",
            "date": "2026-09-21", "start_time": "09:00", "end_time": "10:00",
            "child": "", "location": "", "repeat_weekdays": [], "notes": "",
        })
        event = CalendarEvent.objects.get(title="Spring break")
        self.assertIsNone(event.start_time)                      # times cleared
        self.assertIsNone(event.end_time)

    def test_occurrence_skip_removes_exactly_that_date(self):
        event = CalendarEvent.objects.create(
            parent=self.parent, family=self.family, child=self.violet,
            title="Jiu-jitsu", event_type=CalendarEvent.TYPE_ACTIVITY,
            date=date(2026, 9, 1), repeats_weekly=True,
            repeat_weekdays=[1], repeat_until=date(2026, 9, 30),
        )
        self.client.login(username="cr", password="pw")
        resp = self.client.post(
            reverse("family_calendar:occurrence_skip", args=[event.pk]),
            {"date": "2026-09-08"},
        )
        self.assertEqual(resp.status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.skip_dates, ["2026-09-08"])
        occ = event.occurrences(date(2026, 9, 1), date(2026, 9, 30))
        self.assertNotIn(date(2026, 9, 8), occ)
        self.assertIn(date(2026, 9, 1), occ)                     # siblings intact
        self.assertIn(date(2026, 9, 15), occ)
        # Restore brings it back.
        self.client.post(
            reverse("family_calendar:occurrence_skip", args=[event.pk]),
            {"date": "2026-09-08", "action": "restore"},
        )
        event.refresh_from_db()
        self.assertEqual(event.skip_dates, [])

    def test_viewer_role_cannot_write(self):
        self.client.login(username="tv", password="pw")
        self.assertEqual(
            self.client.get(reverse("family_calendar:event_create")).status_code, 404)
        event = CalendarEvent.objects.create(
            parent=self.parent, family=self.family, title="X",
            event_type=CalendarEvent.TYPE_OTHER, date=date(2026, 9, 1))
        self.assertEqual(
            self.client.get(reverse("family_calendar:event_update", args=[event.pk])).status_code, 404)
        self.assertEqual(
            self.client.post(reverse("family_calendar:event_delete", args=[event.pk])).status_code, 404)
        # But the viewer CAN see the calendar (read is allowed).
        self.assertEqual(
            self.client.get(reverse("family_calendar:calendar")).status_code, 200)

    def test_home_hub_tile_previews_the_next_event(self):
        from datetime import timedelta
        from django.utils import timezone
        CalendarEvent.objects.create(
            parent=self.parent, family=self.family, child=self.violet,
            title="Tumbling", event_type=CalendarEvent.TYPE_ACTIVITY,
            date=timezone.localdate() + timedelta(days=2),
        )
        self.client.login(username="cr", password="pw")
        resp = self.client.get("/")
        self.assertContains(resp, "Family Calendar")
        self.assertContains(resp, "Tumbling")
        self.assertContains(resp, reverse("family_calendar:calendar"))


class PortalCalendarTests(TestCase):
    """The kid's calendar: token-scoped, read-only, sibling-tight."""

    @classmethod
    def setUpTestData(cls):
        from datetime import time, timedelta
        from django.utils import timezone
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(username="pc", email="pc@e.com", password="pw")
        cls.family = Family.objects.create(name="Portal Cal Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)
        cls.token = make_portal_token(cls.violet)

        cls.today = timezone.localdate()
        cls.hers = CalendarEvent.objects.create(
            parent=cls.parent, family=cls.family, child=cls.violet,
            title="Jiu-jitsu", event_type=CalendarEvent.TYPE_ACTIVITY,
            date=cls.today, start_time=time(16, 30),
        )
        cls.siblings = CalendarEvent.objects.create(
            parent=cls.parent, family=cls.family, child=cls.kaylin,
            title="Volleyball", event_type=CalendarEvent.TYPE_ACTIVITY,
            date=cls.today,
        )
        cls.family_wide = CalendarEvent.objects.create(
            parent=cls.parent, family=cls.family, child=None,
            title="Zoo trip", event_type=CalendarEvent.TYPE_OTHER,
            date=cls.today + timedelta(days=3),
        )

    def _url(self, name):
        return reverse(f"portal:{name}", kwargs={"token": self.token})

    def test_page_agenda_shows_hers_and_family_but_never_siblings(self):
        resp = self.client.get(self._url("portal_calendar"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Jiu-jitsu")
        self.assertContains(resp, "4:30 PM")                 # timed agenda line
        self.assertContains(resp, "Zoo trip")                # family-wide included
        self.assertNotContains(resp, "Volleyball")           # sibling's event NEVER
        self.assertContains(resp, "⭐ Today")

    def test_feed_is_token_scoped_and_carries_no_edit_urls(self):
        resp = self.client.get(self._url("portal_calendar_feed"),
                               {"start": self.today.isoformat(),
                                "end": (self.today.replace(year=self.today.year + 1)).isoformat()})
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        titles = [e["title"] for e in payload]
        self.assertTrue(any("Jiu-jitsu" in t for t in titles))
        self.assertTrue(any("Zoo trip" in t for t in titles))
        self.assertFalse(any("Volleyball" in t for t in titles))
        # Read-only: any url must stay inside HER portal (token-authed) — never a
        # parent-app edit or students path.
        for e in payload:
            url = e.get("url", "")
            if url:
                self.assertIn(self.token, url)
                self.assertNotIn("/calendar/", url.replace(f"/portal/{self.token}/calendar/", ""))
                self.assertNotIn("/students/", url)

    def test_feed_and_page_reject_posts(self):
        self.assertEqual(self.client.post(self._url("portal_calendar_feed")).status_code, 405)

    def test_garbage_token_404s(self):
        for name in ("portal_calendar", "portal_calendar_feed"):
            resp = self.client.get(
                reverse(f"portal:{name}", kwargs={"token": "not-a-token"}))
            self.assertEqual(resp.status_code, 404)

    def test_portal_home_shows_the_my_week_card(self):
        resp = self.client.get(reverse("portal:portal_home", kwargs={"token": self.token}))
        self.assertContains(resp, "My Week")
        self.assertContains(resp, self._url("portal_calendar"))
        self.assertContains(resp, "Jiu-jitsu")               # today's event previewed


class MissionLayerTests(TestCase):
    """Auto-paced mission due dates in both feeds — projected live, never stored."""

    @classmethod
    def setUpTestData(cls):
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(username="ml", email="ml@e.com", password="pw")
        cls.family = Family.objects.create(name="Mission Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.token = make_portal_token(cls.violet)

        cls.cur = Curriculum.objects.create(
            parent=cls.parent, family=cls.family, name="Science 3 — Test", subject="Science")
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="U1")
        cls.lessons = [
            Lesson.objects.create(chapter=ch, order=i, number=i, title=f"Mission {i} fun")
            for i in range(1, 5)
        ]
        cls.placement = CurriculumPlacement.objects.create(
            child=cls.violet, curriculum=cls.cur, weekly_pace=5)

    def _parent_feed(self):
        self.client.login(username="ml", password="pw")
        from datetime import timedelta
        from django.utils import timezone
        today = timezone.localdate()
        return self.client.get(reverse("family_calendar:feed"), {
            "start": today.isoformat(),
            "end": (today + timedelta(days=60)).isoformat(),
        }).json()

    def _portal_feed(self):
        from datetime import timedelta
        from django.utils import timezone
        today = timezone.localdate()
        return self.client.get(
            reverse("portal:portal_calendar_feed", kwargs={"token": self.token}),
            {"start": today.isoformat(), "end": (today + timedelta(days=60)).isoformat()},
        ).json()

    def test_parent_feed_projects_missions_with_child_label_and_lessons_url(self):
        missions = [e for e in self._parent_feed()
                    if e["extendedProps"]["layer"] == "missions"]
        self.assertEqual(len(missions), 4)                    # all remaining, in order
        self.assertIn("Violet", missions[0]["title"])
        self.assertIn("Mission 1 fun", missions[0]["title"])
        self.assertIn(f"/students/{self.violet.pk}/lessons/{self.cur.pk}/", missions[0]["url"])
        self.assertTrue(all(m["allDay"] for m in missions))
        # Dates ascend and never land on a weekend.
        from datetime import date
        dates = [date.fromisoformat(m["start"]) for m in missions]
        self.assertEqual(dates, sorted(dates))
        self.assertTrue(all(d.weekday() < 5 for d in dates))

    def test_completing_a_lesson_moves_the_projection_live(self):
        from curricula.models import LessonProgress
        first = self._parent_feed()
        first_missions = [e for e in first if e["extendedProps"]["layer"] == "missions"]
        self.assertIn("Mission 1 fun", first_missions[0]["title"])

        LessonProgress.objects.create(
            child=self.violet, lesson=self.lessons[0],
            status=LessonProgress.COMPLETED, marked_by=self.parent)
        second = self._parent_feed()
        second_missions = [e for e in second if e["extendedProps"]["layer"] == "missions"]
        self.assertEqual(len(second_missions), 3)             # one fewer
        self.assertIn("Mission 2 fun", second_missions[0]["title"])  # next one leads

    def test_pace_none_projects_nothing(self):
        self.placement.weekly_pace = None
        self.placement.save()
        missions = [e for e in self._parent_feed()
                    if e["extendedProps"]["layer"] == "missions"]
        self.assertEqual(missions, [])

    def test_portal_feed_mission_urls_carry_the_token_and_no_parent_urls(self):
        missions = [e for e in self._portal_feed()
                    if e["extendedProps"]["layer"] == "missions"]
        self.assertEqual(len(missions), 4)
        for m in missions:
            self.assertIn(self.token, m["url"])               # kid's own subject page
            self.assertNotIn("/students/", m["url"])          # never a parent URL
        self.assertNotIn("Violet", missions[0]["title"])      # no child prefix for the kid

    def test_family_break_pushes_the_due_dates(self):
        from datetime import timedelta
        from django.utils import timezone
        today = timezone.localdate()
        # Block the next 10 weekdays for the whole family; every projection must
        # land after the break ends.
        CalendarEvent.objects.create(
            parent=self.parent, family=self.family, title="Break",
            event_type=CalendarEvent.TYPE_BREAK, date=today,
            repeats_weekly=True, repeat_weekdays=[0, 1, 2, 3, 4],
            repeat_until=today + timedelta(days=13),
        )
        from datetime import date
        missions = [e for e in self._parent_feed()
                    if e["extendedProps"]["layer"] == "missions"]
        self.assertTrue(missions)
        for m in missions:
            self.assertGreater(
                date.fromisoformat(m["start"]), today + timedelta(days=13))

    def test_portal_page_shows_countdown_chips(self):
        resp = self.client.get(
            reverse("portal:portal_calendar", kwargs={"token": self.token}))
        self.assertContains(resp, "🎯")
        self.assertContains(resp, "Mission 1 fun")
        self.assertContains(resp, "due")                      # today/tomorrow/in N days

    def test_history_layer_shows_done_days_and_stays_in_the_past(self):
        from datetime import timedelta
        from django.utils import timezone
        from worklog.models import WorkLogEntry

        today = timezone.localdate()
        WorkLogEntry.objects.create(
            parent=self.parent, family=self.family, child=self.violet,
            subject="Science", description="Ramp races", date=today - timedelta(days=2))
        WorkLogEntry.objects.create(  # today's work must NOT appear as history
            parent=self.parent, family=self.family, child=self.violet,
            subject="Math", description="today", date=today)
        self.client.login(username="ml", password="pw")
        payload = self.client.get(reverse("family_calendar:feed"), {
            "start": (today - timedelta(days=10)).isoformat(),
            "end": (today + timedelta(days=10)).isoformat(),
        }).json()
        history = [e for e in payload if e["extendedProps"]["layer"] == "history"]
        self.assertEqual(len(history), 1)
        self.assertIn("✓ Violet", history[0]["title"])
        self.assertIn("science", history[0]["title"])
        self.assertEqual(history[0]["start"], (today - timedelta(days=2)).isoformat())

    def test_layers_param_can_switch_history_off(self):
        from datetime import timedelta
        from django.utils import timezone
        from worklog.models import WorkLogEntry

        today = timezone.localdate()
        WorkLogEntry.objects.create(
            parent=self.parent, family=self.family, child=self.violet,
            subject="Science", description="x", date=today - timedelta(days=1))
        self.client.login(username="ml", password="pw")
        payload = self.client.get(reverse("family_calendar:feed"), {
            "start": (today - timedelta(days=5)).isoformat(),
            "end": today.isoformat(),
            "layers": "events,missions",
        }).json()
        self.assertFalse([e for e in payload if e["extendedProps"]["layer"] == "history"])

    def test_birthdays_appear_for_every_family_kid_on_both_surfaces(self):
        from datetime import date, timedelta
        from django.utils import timezone

        today = timezone.localdate()
        upcoming = today + timedelta(days=10)
        self.violet.date_of_birth = date(upcoming.year - 9, upcoming.month, upcoming.day)
        self.violet.save()
        self.client.login(username="ml", password="pw")
        window = {"start": today.isoformat(),
                  "end": (today + timedelta(days=30)).isoformat()}
        payload = self.client.get(reverse("family_calendar:feed"), window).json()
        bdays = [e for e in payload if e["extendedProps"]["layer"] == "birthdays"]
        self.assertEqual(len(bdays), 1)
        self.assertEqual(bdays[0]["title"], "🎂 Violet turns 9")
        self.assertEqual(bdays[0]["start"], upcoming.isoformat())
        # And on the kid's own feed too.
        portal = self.client.get(
            reverse("portal:portal_calendar_feed", kwargs={"token": self.token}),
            window).json()
        self.assertTrue(
            [e for e in portal if e["extendedProps"]["layer"] == "birthdays"])

    def test_lrm_callout_appears_within_a_week_only(self):
        from datetime import timedelta
        from django.utils import timezone

        today = timezone.localdate()
        self.client.login(username="ml", password="pw")
        lrm = CalendarEvent.objects.create(
            parent=self.parent, family=self.family, title="LRM with Mrs. Lee",
            event_type=CalendarEvent.TYPE_CHARTER, date=today + timedelta(days=9))
        page = self.client.get(reverse("family_calendar:calendar"))
        self.assertNotContains(page, "walk in with the record ready")   # 9 days out: quiet
        lrm.date = today + timedelta(days=6)
        lrm.save()
        page = self.client.get(reverse("family_calendar:calendar"))
        self.assertContains(page, "walk in with the record ready")
        self.assertContains(page, reverse("worklog:charter_report"))

    def test_spanish_layer_daily_on_weekdays_and_toggleable(self):
        from datetime import date, timedelta
        from django.utils import timezone

        today = timezone.localdate()
        self.client.login(username="ml", password="pw")
        window = {"start": today.isoformat(),
                  "end": (today + timedelta(days=13)).isoformat()}
        payload = self.client.get(reverse("family_calendar:feed"), window).json()
        spanish = [e for e in payload if e["extendedProps"]["layer"] == "spanish"]
        self.assertEqual(len(spanish), sum(
            1 for i in range(14) if (today + timedelta(days=i)).weekday() < 5))
        self.assertTrue(all("Español" in e["title"] for e in spanish))
        self.assertTrue(all(
            date.fromisoformat(e["start"]).weekday() < 5 for e in spanish))
        # And the toggle removes it.
        window["layers"] = "events,missions"
        payload = self.client.get(reverse("family_calendar:feed"), window).json()
        self.assertFalse([e for e in payload if e["extendedProps"]["layer"] == "spanish"])

    def test_portal_spanish_links_into_her_camino(self):
        from datetime import timedelta
        from django.utils import timezone

        today = timezone.localdate()
        payload = self.client.get(
            reverse("portal:portal_calendar_feed", kwargs={"token": self.token}),
            {"start": today.isoformat(), "end": (today + timedelta(days=6)).isoformat()},
        ).json()
        spanish = [e for e in payload if e["extendedProps"]["layer"] == "spanish"]
        self.assertTrue(spanish)
        self.assertTrue(all(self.token in e["url"] for e in spanish))
        self.assertTrue(all("/lingua/" in e["url"] for e in spanish))
        # One kid on her own calendar: no name prefix.
        self.assertEqual(spanish[0]["title"], "📖 Español")

    def test_unscheduled_activity_gets_a_schedule_it_chip_and_prefill(self):
        from activities.models import ExternalActivity

        guitar = ExternalActivity.objects.create(
            parent=self.parent, family=self.family, student=self.violet,
            title="Guitar", provider="School of Rock",
            url="https://sor.example/", emoji="🎸",
        )
        self.client.login(username="ml", password="pw")
        page = self.client.get(reverse("family_calendar:calendar"))
        self.assertContains(page, "Guitar — schedule it")
        self.assertContains(page, f"?activity={guitar.pk}")

        form_page = self.client.get(
            reverse("family_calendar:event_create"), {"activity": guitar.pk})
        self.assertContains(form_page, 'value="Guitar"')      # title prefilled
        self.assertContains(form_page, "checked")             # repeats_weekly on
        # Once an event links the activity, the chip disappears.
        from django.utils import timezone
        CalendarEvent.objects.create(
            parent=self.parent, family=self.family, child=self.violet,
            activity=guitar, title="Guitar",
            event_type=CalendarEvent.TYPE_ACTIVITY, date=timezone.localdate())
        page = self.client.get(reverse("family_calendar:calendar"))
        self.assertNotContains(page, "Guitar — schedule it")

    def test_pacing_panel_sets_and_clears_pace(self):
        self.client.login(username="ml", password="pw")
        page = self.client.get(reverse("family_calendar:calendar"))
        self.assertContains(page, "Pacing")
        self.assertContains(page, "Science 3 — Test")
        resp = self.client.post(
            reverse("family_calendar:set_pace", args=[self.placement.pk]),
            {"weekly_pace": "2"})
        self.assertEqual(resp.status_code, 302)
        self.placement.refresh_from_db()
        self.assertEqual(self.placement.weekly_pace, 2)
        self.client.post(
            reverse("family_calendar:set_pace", args=[self.placement.pk]),
            {"weekly_pace": "0"})
        self.placement.refresh_from_db()
        self.assertIsNone(self.placement.weekly_pace)


class DuplicateEventTests(FeedTests):
    """Right-click → Duplicate.

    The case it exists for: several LRM meetings that differ only by date.
    Everything is copied and the copy opens for editing, so the one field that
    actually changes is the only one she touches.
    """

    def test_duplicating_copies_everything_and_opens_the_copy(self):
        self.client.login(username="fa", password="pw")
        self.jj.location = "South Sutter"
        self.jj.notes = "bring the folder"
        self.jj.start_time = time(14, 30)
        self.jj.end_time = time(15, 30)
        self.jj.save()

        resp = self.client.post(
            reverse("family_calendar:event_duplicate", args=[self.jj.pk]))
        copy = CalendarEvent.objects.exclude(pk=self.jj.pk).get(title="Jiu-jitsu")
        self.assertRedirects(
            resp, reverse("family_calendar:event_update", args=[copy.pk]))
        for field in ("title", "event_type", "location", "notes", "date",
                      "start_time", "end_time", "child_id", "family_id"):
            self.assertEqual(getattr(copy, field), getattr(self.jj, field), field)
        self.jj.refresh_from_db()
        self.assertEqual(self.jj.title, "Jiu-jitsu")   # original untouched

    def test_a_copy_does_not_inherit_the_originals_skipped_days(self):
        """Skips are exceptions to the ORIGINAL's schedule. Carried onto a copy
        that will sit on a different date, they would silently blank days she
        never chose to skip."""
        self.client.login(username="fa", password="pw")
        self.jj.repeats_weekly = True
        self.jj.skip_dates = ["2026-09-08"]
        self.jj.save()
        self.client.post(
            reverse("family_calendar:event_duplicate", args=[self.jj.pk]))
        copy = CalendarEvent.objects.exclude(pk=self.jj.pk).get(title="Jiu-jitsu")
        self.assertEqual(copy.skip_dates, [])
        self.assertTrue(copy.repeats_weekly)          # the pattern IS copied

    def test_it_can_land_the_copy_on_a_given_date(self):
        self.client.login(username="fa", password="pw")
        self.client.post(
            reverse("family_calendar:event_duplicate", args=[self.jj.pk]),
            {"date": "2026-10-15"})
        copy = CalendarEvent.objects.exclude(pk=self.jj.pk).get(title="Jiu-jitsu")
        self.assertEqual(copy.date, date(2026, 10, 15))

    def test_a_junk_date_falls_back_to_the_originals(self):
        self.client.login(username="fa", password="pw")
        self.client.post(
            reverse("family_calendar:event_duplicate", args=[self.jj.pk]),
            {"date": "not-a-date"})
        copy = CalendarEvent.objects.exclude(pk=self.jj.pk).get(title="Jiu-jitsu")
        self.assertEqual(copy.date, self.jj.date)

    def test_another_family_cannot_duplicate_your_event(self):
        """The whole security story: a pk in a URL must not reach across
        families, or one parent could clone another's calendar into their own."""
        self.client.login(username="fb", password="pw")
        resp = self.client.post(
            reverse("family_calendar:event_duplicate", args=[self.jj.pk]))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(CalendarEvent.objects.filter(title="Jiu-jitsu").count(), 1)

    def test_get_does_not_duplicate(self):
        self.client.login(username="fa", password="pw")
        resp = self.client.get(
            reverse("family_calendar:event_duplicate", args=[self.jj.pk]))
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(CalendarEvent.objects.filter(title="Jiu-jitsu").count(), 1)

    def test_the_feed_marks_which_chips_can_be_acted_on(self):
        """The menu keys on pk: real rows get one, generated layers must not,
        because there is no row behind a birthday to delete."""
        self.client.login(username="fa", password="pw")
        # Without a birthday the generated layer emits nothing, and the
        # negative loop below iterates over an empty list — passing while
        # proving nothing. Give her one so there is a generated chip to check.
        self.violet.date_of_birth = date(2016, 9, 15)
        self.violet.save(update_fields=["date_of_birth"])
        events = self._feed(layers="events,birthdays").json()
        real = [e for e in events if e["extendedProps"]["layer"] == "events"]
        generated = [e for e in events if e["extendedProps"]["layer"] != "events"]
        self.assertTrue(real)
        self.assertTrue(generated, "no generated chips — the check below is vacuous")
        for e in real:
            self.assertTrue(e["extendedProps"].get("pk"))
        for e in generated:
            self.assertIsNone(e["extendedProps"].get("pk"))

    def test_a_viewer_cannot_duplicate(self):
        """The gate on this view is its own; nothing else covered it."""
        from core.models import FamilyMembership

        viewer = User.objects.create_user(
            username="viewer", email="v@e.com", password="pw")
        FamilyMembership.objects.create(
            user=viewer, family=self.family_a, role="viewer")
        self.client.login(username="viewer", password="pw")
        resp = self.client.post(
            reverse("family_calendar:event_duplicate", args=[self.jj.pk]))
        self.assertIn(resp.status_code, (403, 404))
        self.assertEqual(CalendarEvent.objects.filter(title="Jiu-jitsu").count(), 1)


class StaticJavaScriptParsesTests(SimpleTestCase):
    """Every shipped .js file must actually parse.

    This exists because a "\\n\\n" escape got flattened into a real newline
    inside a double-quoted string in calendar-menu.js. In JavaScript that is an
    unterminated string literal, so the whole file failed to parse, the IIFE
    never ran, and `window.calendarMenuAttach` was never defined. The calendar's
    `eventDidMount` guards with `if (window.calendarMenuAttach)`, so it skipped
    silently — and right-clicking an event fell through to the browser's own
    context menu. Edit, Duplicate and Delete were all dead in production, with
    nothing in the server logs and every Python test passing.

    Nothing here checked that a script we ship is even syntactically valid.
    """

    JS_DIR = Path(__file__).resolve().parent.parent / "static" / "js"

    def _files(self):
        files = sorted(self.JS_DIR.glob("*.js"))
        self.assertGreater(len(files), 10, "expected the portal's scripts here")
        return files

    def test_every_static_script_parses(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not on PATH")
        broken = []
        for path in self._files():
            proc = subprocess.run([node, "--check", str(path)],
                                  capture_output=True, text=True)
            if proc.returncode != 0:
                first = (proc.stderr or "").strip().splitlines()
                broken.append("%s: %s" % (path.name, first[-1] if first else "?"))
        self.assertEqual(broken, [], "these scripts do not parse:\n" + "\n".join(broken))


# ---- HH-168: Google Calendar push ------------------------------------------

import json
import time as _time
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import override_settings


class _FakeResponse:
    """Just enough of requests.Response for these tests."""

    def __init__(self, status_code=200, payload=None, text="", content=b"x"):
        self.status_code = status_code
        self._payload = {} if payload is None else payload
        self.text = text
        self.content = content

    def json(self):
        return self._payload


def _reset_token_cache():
    from family_calendar import google_api

    google_api._cached_token = None
    google_api._cached_until = 0.0


# A syntactically complete service-account key. The private_key is deliberately
# nonsense: every test that would need a real signature mocks jwt.encode, so a
# real key would only be a liability sitting in the repo.
FAKE_SA = json.dumps({
    "type": "service_account",
    "project_id": "steadfast-scholars-calendar",
    "client_email": "calendar-push@steadfast-scholars-calendar.iam.gserviceaccount.com",
    "private_key": "-----BEGIN PRIVATE KEY-----\nnot-a-real-key\n-----END PRIVATE KEY-----\n",
    "token_uri": "https://oauth2.googleapis.com/token",
})

BOTH_CALENDARS = ("mom.dad.homeschool@gmail.com,"
                  "family12229112883802399559@group.calendar.google.com")


@override_settings(GOOGLE_CALENDAR_SA_JSON=FAKE_SA, GOOGLE_CALENDAR_IDS=BOTH_CALENDARS)
class GoogleApiConfigTests(TestCase):
    """HH-168: the module is inert unless BOTH halves of the config exist."""

    def setUp(self):
        _reset_token_cache()

    def test_both_halves_are_required(self):
        from family_calendar import google_api

        self.assertTrue(google_api.is_configured())
        with override_settings(GOOGLE_CALENDAR_SA_JSON=""):
            self.assertFalse(google_api.is_configured())   # key but nowhere to write
        with override_settings(GOOGLE_CALENDAR_IDS=""):
            self.assertFalse(google_api.is_configured())   # destination, no key

    def test_calendar_ids_are_split_and_trimmed(self):
        from family_calendar import google_api

        with override_settings(GOOGLE_CALENDAR_IDS=" a@x.com , , b@y.com "):
            self.assertEqual(google_api.calendar_ids(), ["a@x.com", "b@y.com"])

    def test_the_two_real_calendars_parse(self):
        from family_calendar import google_api

        self.assertEqual(google_api.calendar_ids(), [
            "mom.dad.homeschool@gmail.com",
            "family12229112883802399559@group.calendar.google.com",
        ])

    def test_a_broken_key_shouts_rather_than_switching_off_quietly(self):
        from family_calendar import google_api

        with override_settings(GOOGLE_CALENDAR_SA_JSON="{not json"):
            with self.assertRaises(google_api.GoogleCalendarError):
                google_api.service_account()

    def test_a_key_missing_its_private_key_is_rejected(self):
        from family_calendar import google_api

        partial = json.dumps({"client_email": "a@b.com",
                              "token_uri": "https://oauth2.googleapis.com/token"})
        with override_settings(GOOGLE_CALENDAR_SA_JSON=partial):
            with self.assertRaises(google_api.GoogleCalendarError):
                google_api.service_account()

    def test_no_key_at_all_is_simply_off(self):
        from family_calendar import google_api

        with override_settings(GOOGLE_CALENDAR_SA_JSON=""):
            self.assertIsNone(google_api.service_account())


@override_settings(GOOGLE_CALENDAR_SA_JSON=FAKE_SA, GOOGLE_CALENDAR_IDS=BOTH_CALENDARS)
class GoogleApiTokenTests(TestCase):
    """The token is minted once and reused — a fresh JWT per API call would be
    three round trips to Google for every event we push."""

    def setUp(self):
        _reset_token_cache()

    def test_the_token_is_cached_between_calls(self):
        from family_calendar import google_api

        with mock.patch.object(google_api.jwt, "encode", return_value="signed"), \
             mock.patch.object(google_api.requests, "post") as post:
            post.return_value = _FakeResponse(
                200, {"access_token": "tok-1", "expires_in": 3600})
            self.assertEqual(google_api.access_token(), "tok-1")
            self.assertEqual(google_api.access_token(), "tok-1")
            self.assertEqual(post.call_count, 1)          # minted once, not twice

    def test_an_expired_token_is_reminted(self):
        from family_calendar import google_api

        with mock.patch.object(google_api.jwt, "encode", return_value="signed"), \
             mock.patch.object(google_api.requests, "post") as post:
            post.return_value = _FakeResponse(
                200, {"access_token": "tok-1", "expires_in": 3600})
            google_api.access_token()
            google_api._cached_until = _time.time() - 1     # pretend an hour passed
            post.return_value = _FakeResponse(
                200, {"access_token": "tok-2", "expires_in": 3600})
            self.assertEqual(google_api.access_token(), "tok-2")
            self.assertEqual(post.call_count, 2)

    def test_a_rejected_key_reports_googles_own_reason(self):
        from family_calendar import google_api

        with mock.patch.object(google_api.jwt, "encode", return_value="signed"), \
             mock.patch.object(google_api.requests, "post") as post:
            post.return_value = _FakeResponse(
                400, text='{"error":"invalid_grant"}')
            with self.assertRaises(google_api.GoogleCalendarError) as caught:
                google_api.access_token()
        # Google's diagnosis must survive to the operator — "invalid_grant" is
        # the difference between a revoked key and a clock problem.
        self.assertIn("invalid_grant", str(caught.exception))
        self.assertEqual(caught.exception.status, 400)

    def test_the_signed_claims_name_the_service_account_and_scope(self):
        from family_calendar import google_api

        with mock.patch.object(google_api.jwt, "encode", return_value="signed") as enc, \
             mock.patch.object(google_api.requests, "post") as post:
            post.return_value = _FakeResponse(
                200, {"access_token": "tok", "expires_in": 3600})
            google_api.access_token()
        claims = enc.call_args[0][0]
        self.assertEqual(claims["iss"],
                         "calendar-push@steadfast-scholars-calendar.iam.gserviceaccount.com")
        self.assertEqual(claims["aud"], "https://oauth2.googleapis.com/token")
        self.assertEqual(claims["scope"], google_api.SCOPE)
        self.assertGreater(claims["exp"], claims["iat"])
        self.assertEqual(enc.call_args[1]["algorithm"], "RS256")


@override_settings(GOOGLE_CALENDAR_SA_JSON=FAKE_SA, GOOGLE_CALENDAR_IDS=BOTH_CALENDARS)
class GoogleApiRequestTests(TestCase):
    """A revoked token looks exactly like an expired one until Google says 401."""

    def setUp(self):
        _reset_token_cache()

    def test_a_401_is_retried_once_with_a_fresh_token(self):
        from family_calendar import google_api

        with mock.patch.object(google_api.jwt, "encode", return_value="signed"), \
             mock.patch.object(google_api.requests, "post",
                               return_value=_FakeResponse(
                                   200, {"access_token": "tok", "expires_in": 3600})), \
             mock.patch.object(google_api.requests, "request") as req:
            req.side_effect = [
                _FakeResponse(401, text="expired"),
                _FakeResponse(200, {"ok": True}),
            ]
            self.assertEqual(google_api.request("GET", "/x"), {"ok": True})
            self.assertEqual(req.call_count, 2)

    def test_a_second_401_gives_up_rather_than_looping(self):
        from family_calendar import google_api

        with mock.patch.object(google_api.jwt, "encode", return_value="signed"), \
             mock.patch.object(google_api.requests, "post",
                               return_value=_FakeResponse(
                                   200, {"access_token": "tok", "expires_in": 3600})), \
             mock.patch.object(google_api.requests, "request") as req:
            req.return_value = _FakeResponse(401, text="nope")
            with self.assertRaises(google_api.GoogleCalendarError):
                google_api.request("GET", "/x")
            self.assertEqual(req.call_count, 2)      # two attempts, then stop

    def test_a_403_is_not_retried(self):
        from family_calendar import google_api

        with mock.patch.object(google_api.jwt, "encode", return_value="signed"), \
             mock.patch.object(google_api.requests, "post",
                               return_value=_FakeResponse(
                                   200, {"access_token": "tok", "expires_in": 3600})), \
             mock.patch.object(google_api.requests, "request") as req:
            req.return_value = _FakeResponse(403, text="forbidden")
            with self.assertRaises(google_api.GoogleCalendarError) as caught:
                google_api.request("GET", "/x")
            self.assertEqual(req.call_count, 1)      # a permission problem is final
        self.assertEqual(caught.exception.status, 403)


@override_settings(GOOGLE_CALENDAR_SA_JSON=FAKE_SA, GOOGLE_CALENDAR_IDS=BOTH_CALENDARS)
class AccessRoleTests(TestCase):
    """Google renamed the sharing levels on 2026-07-07 and added
    writerWithoutPrivateAccess directly above the one we need. It writes
    non-private events fine, so accepting it would look like success and then
    misbehave later."""

    def setUp(self):
        _reset_token_cache()

    def test_writer_without_private_access_is_not_treated_as_writable(self):
        from family_calendar import google_api

        self.assertIn(google_api.ROLE_WRITER, google_api.WRITABLE_ROLES)
        self.assertIn(google_api.ROLE_OWNER, google_api.WRITABLE_ROLES)
        self.assertNotIn(google_api.ROLE_PARTIAL, google_api.WRITABLE_ROLES)

    def test_a_calendar_already_in_the_list_is_read_not_re_added(self):
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api.requests, "request") as req:
            req.return_value = _FakeResponse(200, {"accessRole": "writer"})
            self.assertEqual(google_api.access_role("a@b.com"), "writer")
            self.assertEqual(req.call_args[0][0], "GET")   # never POSTs when present

    def test_an_unaccepted_share_is_picked_up_then_read(self):
        """A calendar shared with a service account never appears on its own —
        nobody accepts an invitation on a robot's behalf."""
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api.requests, "request") as req:
            req.side_effect = [
                _FakeResponse(404, text="not found"),
                _FakeResponse(200, {"accessRole": "writer"}),
            ]
            self.assertEqual(google_api.access_role("a@b.com"), "writer")
            self.assertEqual(req.call_count, 2)
            self.assertEqual(req.call_args[0][0], "POST")  # calendarList.insert

    def test_a_403_is_not_mistaken_for_an_unaccepted_share(self):
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api.requests, "request") as req:
            req.return_value = _FakeResponse(403, text="forbidden")
            with self.assertRaises(google_api.GoogleCalendarError):
                google_api.access_role("a@b.com")
            self.assertEqual(req.call_count, 1)   # must NOT try to insert


@override_settings(GOOGLE_CALENDAR_SA_JSON=FAKE_SA, GOOGLE_CALENDAR_IDS=BOTH_CALENDARS)
class CheckCommandTests(TestCase):
    """The command exists to answer one question truthfully, including when the
    answer is 'nearly'."""

    def setUp(self):
        _reset_token_cache()

    def _run(self):
        out = StringIO()
        err = StringIO()
        call_command("check_google_calendar", stdout=out, stderr=err)
        return out.getvalue() + err.getvalue()

    def test_two_writable_calendars_reads_as_done(self):
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api, "access_role", return_value="writer"):
            output = self._run()
        self.assertIn("handshake is done", output)
        self.assertNotIn("Not ready", output)

    def test_the_near_miss_role_is_called_out_by_name(self):
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api, "access_role",
                               return_value=google_api.ROLE_PARTIAL):
            output = self._run()
        self.assertIn("Not ready", output)
        self.assertIn("Make changes and see event details", output)  # the fix, verbatim

    def test_a_read_only_share_is_reported_as_read_only(self):
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api, "access_role", return_value="reader"):
            output = self._run()
        self.assertIn("Not ready", output)
        self.assertIn("Read-only", output)

    def test_one_good_one_bad_still_reports_not_ready(self):
        """Both calendars must work. Reporting success on a partial setup would
        mean events silently landing on only one of them."""
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api, "access_role",
                               side_effect=["writer", "reader"]):
            output = self._run()
        self.assertIn("Not ready", output)

    def test_a_missing_calendar_says_so_rather_than_crashing(self):
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token", return_value="tok"), \
             mock.patch.object(google_api, "access_role",
                               side_effect=google_api.GoogleCalendarError(
                                   "gone", status=404)):
            output = self._run()
        self.assertIn("never shared", output)
        self.assertIn("Not ready", output)

    def test_a_rejected_key_stops_before_touching_any_calendar(self):
        from family_calendar import google_api

        with mock.patch.object(google_api, "access_token",
                               side_effect=google_api.GoogleCalendarError(
                                   "invalid_grant", status=400)), \
             mock.patch.object(google_api, "access_role") as role:
            output = self._run()
        self.assertIn("invalid_grant", output)
        role.assert_not_called()      # no point asking about calendars

    def test_no_config_reports_switched_off_not_an_error(self):
        with override_settings(GOOGLE_CALENDAR_SA_JSON=""):
            output = self._run()
        self.assertIn("switched off", output)
