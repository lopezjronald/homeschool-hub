"""Spelling OS behaviour.

The two things worth guarding are the ones a child would feel: a word she got
wrong must come straight back, and the app must never hand her the same activity
twice or skip one she hasn't done.
"""

import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Family, FamilyMembership
from portal.tokens import make_portal_token
from students.models import Student

from . import services
from .models import (
    SpellingCard, SpellingPlacement, SpellingSession, SpellingWeek, SpellingWord,
)

User = get_user_model()


class SpellingBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="sp", email="sp@e.com", password="pw")
        cls.family = Family.objects.create(name="Spell Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.week = SpellingWeek.objects.create(
            number=1, unit="Foundation Repair", pattern="short a / short i",
            rule="One vowel between two consonants says its short sound.",
            sort_buckets=["short a", "short i"])
        for order, (w, s, b) in enumerate([
            ("cat", "The cat sat on my lap.", 0),
            ("map", "Dad has a big map.", 0),
            ("pig", "The pig is in the mud.", 1),
        ]):
            SpellingWord.objects.create(
                week=cls.week, word=w, sentence=s, sort_bucket=b, order=order)
        SpellingWord.objects.create(
            week=cls.week, word="said", sentence="She said hello to me.",
            is_heart=True, tricky_part="ai says short e")
        cls.token = make_portal_token(cls.child)


class LeitnerTests(SpellingBase):
    def test_a_miss_brings_the_word_straight_back(self):
        """The whole point of the box system: a wrong answer is due again today,
        not next week. Getting it wrong is not a penalty, it's a signal."""
        card = SpellingCard.objects.create(
            child=self.child, word=self.week.words.first(), box=4)
        card.record(correct=False)
        self.assertEqual(card.box, 1)
        self.assertEqual(card.due, timezone.localdate())
        self.assertEqual(card.misses, 1)

    def test_mastery_takes_four_spaced_correct_answers(self):
        """Not one lucky Friday. Four rights, each pushing the interval out."""
        card = SpellingCard.objects.create(child=self.child, word=self.week.words.first())
        intervals = []
        for _ in range(4):
            newly = card.record(correct=True)
            intervals.append((card.due - timezone.localdate()).days)
        self.assertEqual(card.box, SpellingCard.MAX_BOX)
        self.assertTrue(newly)                        # the 4th one masters it
        self.assertEqual(intervals, sorted(intervals))  # gaps only widen
        self.assertTrue(card.is_mastered)

    def test_mastering_is_reported_once(self):
        card = SpellingCard.objects.create(child=self.child, word=self.week.words.first())
        results = [card.record(correct=True) for _ in range(5)]
        self.assertEqual(results.count(True), 1, "should celebrate mastery once")

    def test_a_word_missed_three_times_is_flagged_for_the_parent(self):
        card = SpellingCard.objects.create(child=self.child, word=self.week.words.first())
        for _ in range(2):
            card.record(correct=False)
        self.assertFalse(card.is_trouble)
        card.record(correct=False)
        self.assertTrue(card.is_trouble)


class RouterTests(SpellingBase):
    def test_the_flow_runs_in_order_and_never_repeats(self):
        seen = []
        for _ in range(4):
            kind, week = services.next_activity(self.child)
            seen.append(kind)
            SpellingSession.objects.create(child=self.child, week=week, kind=kind)
        self.assertEqual(seen, services.WEEK_FLOW)

    def test_all_done_is_a_real_answer(self):
        """With the week finished and nothing due, she gets 'all done', not a
        fifth activity invented to fill the day."""
        for kind in services.WEEK_FLOW:
            SpellingSession.objects.create(child=self.child, week=self.week, kind=kind)
        SpellingCard.objects.filter(child=self.child).update(
            due=timezone.localdate() + timedelta(days=5))
        kind, _ = services.next_activity(self.child)
        self.assertIsNone(kind)

    def test_a_missed_day_does_not_lock_her_out(self):
        """Skipping Tuesday should offer the sort, not skip it — the flow is
        what she has left, not what day it is."""
        SpellingSession.objects.create(
            child=self.child, week=self.week, kind=SpellingSession.LEARN)
        kind, _ = services.next_activity(self.child)
        self.assertEqual(kind, SpellingSession.SORT)

    def test_last_weeks_sessions_do_not_count_as_this_weeks(self):
        last_week = services.week_start() - timedelta(days=3)
        for kind in services.WEEK_FLOW:
            SpellingSession.objects.create(
                child=self.child, week=self.week, kind=kind, on_date=last_week)
        kind, _ = services.next_activity(self.child)
        self.assertEqual(kind, SpellingSession.LEARN)


class AdvanceTests(SpellingBase):
    def setUp(self):
        SpellingWeek.objects.create(
            number=2, unit="Foundation Repair", pattern="short o",
            rule="Short o as in dog.", sort_buckets=["short o"])
        services.ensure_cards(self.child, self.week)
        for kind in services.WEEK_FLOW:
            SpellingSession.objects.create(child=self.child, week=self.week, kind=kind)

    def test_a_week_she_has_learned_advances(self):
        SpellingCard.objects.filter(child=self.child).update(box=3)
        week = services.advance_if_ready(self.child)
        self.assertEqual(week.number, 2)

    def test_a_week_she_has_not_learned_repeats_and_tells_the_parent(self):
        """More than 40% still in box 1 means moving on would bury the gap."""
        SpellingCard.objects.filter(child=self.child).update(box=1)
        week = services.advance_if_ready(self.child)
        self.assertEqual(week.number, 1)
        self.assertIsNotNone(
            SpellingPlacement.objects.get(child=self.child).repeat_flagged_on)

    def test_an_unfinished_week_never_advances(self):
        SpellingSession.objects.filter(child=self.child).delete()
        SpellingCard.objects.filter(child=self.child).update(box=5)
        self.assertEqual(services.advance_if_ready(self.child).number, 1)


class DueSelectionTests(SpellingBase):
    def test_review_words_ride_along_with_this_weeks(self):
        """Words don't vanish after their week — that's the difference between
        this and a Friday test."""
        old_week = SpellingWeek.objects.create(
            number=0, unit="prior", pattern="old", rule="r", sort_buckets=[])
        old = SpellingWord.objects.create(
            week=old_week, word="ship", sentence="The ship is at sea.")
        SpellingCard.objects.create(
            child=self.child, word=old, box=2, due=timezone.localdate() - timedelta(days=3))
        services.ensure_cards(self.child, self.week)
        words = [c.word.word for c in services.due_cards(self.child, self.week)]
        self.assertIn("ship", words)

    def test_a_session_stays_short(self):
        for n in range(40):
            w = SpellingWord.objects.create(
                week=self.week, word=f"word{n}", sentence=f"This is word{n}.")
            SpellingCard.objects.create(child=self.child, word=w)
        self.assertLessEqual(
            len(services.due_cards(self.child, self.week)), services.QUIZ_CAP)

    def test_mastered_words_stop_crowding_the_review(self):
        old_week = SpellingWeek.objects.create(
            number=0, unit="prior", pattern="old", rule="r", sort_buckets=[])
        done = SpellingWord.objects.create(
            week=old_week, word="ship", sentence="The ship is at sea.")
        SpellingCard.objects.create(
            child=self.child, word=done, box=SpellingCard.MAX_BOX,
            due=timezone.localdate() - timedelta(days=99))
        words = [c.word.word for c in services.due_cards(self.child, self.week)]
        self.assertNotIn("ship", words)


class KidSurfaceTests(SpellingBase):
    def setUp(self):
        services.placement_for(self.child)

    def test_the_home_screen_offers_exactly_one_thing(self):
        resp = self.client.get(reverse("spelling:home", args=[self.token]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["kind"], SpellingSession.LEARN)
        self.assertIn("/learn/", resp.context["next_url"])

    def test_the_quiz_ships_the_words_and_their_sentences(self):
        resp = self.client.get(reverse("spelling:quiz", args=[self.token]))
        self.assertEqual(resp.status_code, 200)
        items = json.loads(resp.context["items_json"])
        self.assertTrue(items)
        self.assertEqual(
            set(items[0]), {"card", "word", "sentence", "heart", "tricky"})

    def test_an_answer_moves_the_card(self):
        services.ensure_cards(self.child, self.week)
        card = SpellingCard.objects.filter(child=self.child).first()
        resp = self.client.post(
            reverse("spelling:answer", args=[self.token]),
            data=json.dumps({"card": card.pk, "correct": True}),
            content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        card.refresh_from_db()
        self.assertEqual(card.box, 2)

    def test_a_child_cannot_touch_another_childs_card(self):
        """The card id comes from the client, so it has to be scoped."""
        sibling = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07", family=self.family)
        theirs = SpellingCard.objects.create(
            child=sibling, word=self.week.words.first())
        resp = self.client.post(
            reverse("spelling:answer", args=[self.token]),
            data=json.dumps({"card": theirs.pk, "correct": True}),
            content_type="application/json")
        self.assertEqual(resp.status_code, 404)
        theirs.refresh_from_db()
        self.assertEqual(theirs.box, 1)

    def test_a_bad_token_gets_nothing(self):
        for url in ("home", "learn", "quiz", "sort", "dictation"):
            self.assertEqual(
                self.client.get(reverse(f"spelling:{url}", args=["not-a-token"])).status_code,
                404, url)

    def test_switching_spelling_off_hides_it_from_her_entirely(self):
        SpellingPlacement.objects.filter(child=self.child).update(is_active=False)
        self.assertEqual(
            self.client.get(reverse("spelling:home", args=[self.token])).status_code, 404)

    def test_finishing_logs_the_session(self):
        resp = self.client.post(
            reverse("spelling:finish", args=[self.token]),
            data=json.dumps({"kind": "quiz", "asked": 5, "right": 4, "missed": ["cat"]}),
            content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        session = SpellingSession.objects.get(child=self.child)
        self.assertEqual((session.asked, session.right), (5, 4))
        self.assertEqual(session.missed_words, ["cat"])

    def test_a_made_up_activity_is_refused(self):
        resp = self.client.post(
            reverse("spelling:finish", args=[self.token]),
            data=json.dumps({"kind": "nonsense", "asked": 1, "right": 1}),
            content_type="application/json")
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(SpellingSession.objects.exists())

    def test_the_kid_surfaces_are_post_only_where_they_write(self):
        for name in ("answer", "finish"):
            self.assertEqual(
                self.client.get(reverse(f"spelling:{name}", args=[self.token])).status_code,
                405, name)


class ParentDashboardTests(SpellingBase):
    def test_the_parent_sees_where_she_is_and_what_is_stuck(self):
        services.ensure_cards(self.child, self.week)
        card = SpellingCard.objects.filter(child=self.child).first()
        for _ in range(3):
            card.record(correct=False)
        self.client.login(username="sp", password="pw")
        resp = self.client.get(reverse("spelling:parent_dashboard", args=[self.child.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(card, resp.context["trouble"])
        self.assertContains(resp, card.word.word)

    def test_another_family_cannot_read_her_progress(self):
        other = User.objects.create_user(
            username="other", email="o@e.com", password="pw")
        fam = Family.objects.create(name="Other")
        FamilyMembership.objects.create(user=other, family=fam, role="parent")
        self.client.login(username="other", password="pw")
        self.assertEqual(
            self.client.get(
                reverse("spelling:parent_dashboard", args=[self.child.pk])).status_code,
            404)

    def test_it_needs_a_login(self):
        resp = self.client.get(reverse("spelling:parent_dashboard", args=[self.child.pk]))
        self.assertEqual(resp.status_code, 302)


class SeedTests(TestCase):
    def test_the_seed_is_idempotent_and_matches_the_scope(self):
        from django.core.management import call_command
        from io import StringIO
        for _ in range(2):
            call_command("seed_spelling", stdout=StringIO())
        self.assertEqual(SpellingWeek.objects.count(), 4)
        self.assertEqual(SpellingWord.objects.count(), 67)
        for week in SpellingWeek.objects.all():
            self.assertTrue(12 <= week.pattern_words.count() <= 15, week.number)
            self.assertTrue(2 <= week.heart_words.count() <= 3, week.number)

    def test_every_dictation_sentence_contains_its_word(self):
        """A sentence that doesn't use the word can't dictate it."""
        from django.core.management import call_command
        from io import StringIO
        call_command("seed_spelling", stdout=StringIO())
        for word in SpellingWord.objects.all():
            self.assertIn(word.word.lower(), word.sentence.lower(), word.word)

    def test_every_pattern_word_lands_in_a_real_bucket(self):
        """A word pointing past the end of its columns is unsortable."""
        from django.core.management import call_command
        from io import StringIO
        call_command("seed_spelling", stdout=StringIO())
        for word in SpellingWord.objects.filter(is_heart=False):
            self.assertLess(word.sort_bucket, len(word.week.sort_buckets), word.word)


class CsrfTests(SpellingBase):
    """The kid endpoints write to the database, so they need a CSRF token.

    The default test client disables CSRF, which is exactly why the first
    version of the quiz shipped a fetch() with no token: 29 tests passed while
    every answer 403'd in a real browser and the JS swallowed it.
    """

    def setUp(self):
        from django.test import Client
        self.strict = Client(enforce_csrf_checks=True)
        services.ensure_cards(self.child, self.week)

    def _page_token(self, url):
        resp = self.strict.get(url)
        self.assertEqual(resp.status_code, 200)
        return resp.cookies["csrftoken"].value if "csrftoken" in resp.cookies else \
            resp.context["csrf_token"]

    def test_a_post_without_a_token_is_refused(self):
        card = SpellingCard.objects.filter(child=self.child).first()
        resp = self.strict.post(
            reverse("spelling:answer", args=[self.token]),
            data=json.dumps({"card": card.pk, "correct": True}),
            content_type="application/json")
        self.assertEqual(resp.status_code, 403)

    def test_a_post_with_the_page_token_succeeds(self):
        """What the browser actually does: read the token the page rendered,
        send it back in the X-CSRFToken header."""
        token = self._page_token(reverse("spelling:quiz", args=[self.token]))
        card = SpellingCard.objects.filter(child=self.child).first()
        resp = self.strict.post(
            reverse("spelling:answer", args=[self.token]),
            data=json.dumps({"card": card.pk, "correct": True}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token)
        self.assertEqual(resp.status_code, 200)
        card.refresh_from_db()
        self.assertEqual(card.box, 2)

    def test_every_writing_page_renders_a_token_for_its_script(self):
        for name in ("quiz", "learn", "sort", "dictation"):
            resp = self.client.get(reverse(f"spelling:{name}", args=[self.token]))
            self.assertContains(resp, "csrfmiddlewaretoken", msg_prefix=name)
            # Hash-suffixed by manifest storage, so match the stem.
            self.assertContains(resp, "js/spelling-post.", msg_prefix=name)
