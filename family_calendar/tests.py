from datetime import date

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
        self.assertFalse(any(e.get("url") for e in payload))  # read-only: no links out

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
