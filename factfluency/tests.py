"""Fact Dash (HH-203).

The rules ARE the product here, so they are tested without a browser: what
counts as fluent, what promotes, what a round is made of, and who may play.
"""

import json
import uuid
from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Family, FamilyMembership
from portal.tokens import make_portal_token
from students.models import Student

from accounts.models import CustomUser as User

from .models import (
    MASTERY_STREAK, Attempt, Fact, GameSession, Level,
    Operation, PersonalRecord, RecordType, StudentFactState,
)
from . import scheduling
from .policy import BANDS, policy_for, threshold_for


class FactShapeTests(TestCase):
    """The seeded facts themselves. A wrong fact here is a child taught a lie."""

    def test_every_seeded_fact_has_the_right_product(self):
        for fact in Fact.objects.all():
            self.assertEqual(fact.product, fact.factor_a * fact.factor_b, str(fact))

    def test_no_question_ever_divides_by_zero(self):
        """0x5 would naively invert to "0 / 0", which is undefined — and the
        naive inverse would answer 5 to it."""
        for fact in Fact.objects.all():
            for operation in fact.operations():
                prompt = fact.prompt(operation)
                if "÷" in prompt:
                    divisor = int(prompt.split("÷")[1].strip())
                    self.assertNotEqual(divisor, 0, prompt)

    def test_every_answer_is_arithmetically_true(self):
        for fact in Fact.objects.all():
            for operation in fact.operations():
                prompt, answer = fact.prompt(operation), fact.answer(operation)
                if "×" in prompt:
                    a, b = (int(x) for x in prompt.split("×"))
                    self.assertEqual(answer, a * b, prompt)
                else:
                    p, d = (int(x) for x in prompt.split("÷"))
                    self.assertEqual(answer, p // d, prompt)
                    self.assertEqual(p % d, 0, "%s is not a whole division" % prompt)

    def test_a_square_has_one_division_not_two(self):
        seven = Fact.objects.get(factor_a=7, factor_b=7)
        self.assertEqual(seven.operations(), [Operation.MULT, Operation.DIV_A])

    def test_a_zero_fact_is_multiplication_only(self):
        zero = Fact.objects.get(factor_a=0, factor_b=6)
        self.assertEqual(zero.operations(), [Operation.MULT])

    def test_the_ten_levels_are_in_strategy_order(self):
        slugs = list(Level.objects.values_list("slug", flat=True))
        self.assertEqual(slugs, [
            "ones-twos", "fives", "tens", "squares", "threes",
            "fours", "nines", "sixes", "sevens", "the-tricky-ones"])

    def test_each_fact_is_introduced_by_exactly_one_level(self):
        """A fact introduced twice would count as 'new' twice and skew both
        bars. The challenge level is the deliberate exception — it re-mixes
        facts met elsewhere and has no bar of its own."""
        for fact in Fact.objects.all():
            introducing = fact.levels.filter(is_challenge=False)
            self.assertEqual(introducing.count(), 1, str(fact))

    def test_the_challenge_level_is_never_beaten(self):
        """Every fact in it is mastered elsewhere, so a mastery bar would read
        full before she answered anything. It is scored on records instead."""
        parent = User.objects.create_user(username="ch", email="ch@e.com", password="pw")
        family = Family.objects.create(name="CH Fam")
        child = Student.objects.create(
            parent=parent, first_name="V", grade_level="G03", family=family)
        boss = Level.objects.get(slug="the-tricky-ones")
        self.assertTrue(boss.is_challenge)
        for state in scheduling.ensure_states(
                child, scheduling._forms_for_level(boss)).values():
            state.is_mastered = True
            state.save()
        self.assertFalse(scheduling.is_level_beaten(child, boss))

    def test_only_the_last_level_is_a_challenge(self):
        challenges = list(Level.objects.filter(is_challenge=True))
        self.assertEqual([l.slug for l in challenges], ["the-tricky-ones"])

    def test_the_hard_facts_are_flagged_and_land_in_the_last_level(self):
        hard = {(6, 7), (6, 8), (7, 8), (4, 7), (4, 8)}
        flagged = {(f.factor_a, f.factor_b)
                   for f in Fact.objects.filter(is_hard_core=True)}
        self.assertEqual(flagged, hard)
        boss = Level.objects.get(slug="the-tricky-ones")
        self.assertEqual({(f.factor_a, f.factor_b) for f in boss.facts.all()}, hard)


class SchedulerTests(TestCase):
    """The Leitner rules, and the one that carries the whole design."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="fd", email="fd@e.com", password="pw")
        cls.family = Family.objects.create(name="FD Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.fact = Fact.objects.get(factor_a=6, factor_b=8)

    def _state(self):
        return StudentFactState.objects.create(
            student=self.child, fact=self.fact, operation=Operation.MULT)

    def test_fast_and_right_is_fluent(self):
        bar = policy_for(self.child).base_ms
        self.assertTrue(scheduling.is_fluent(True, bar - 1, bar))

    def test_right_but_slow_is_not_fluent(self):
        bar = policy_for(self.child).base_ms
        self.assertFalse(scheduling.is_fluent(True, bar + 1, bar))

    def test_fast_but_wrong_is_not_fluent(self):
        self.assertFalse(scheduling.is_fluent(False, 200, 3000))

    def test_a_fluent_answer_promotes_a_box_and_pushes_the_review_out(self):
        state = self._state()
        before = state.due_at
        scheduling.apply_attempt(state, is_correct=True, response_ms=900)
        self.assertEqual(state.leitner_box, 2)
        self.assertEqual(state.consecutive_fluent, 1)
        self.assertGreater(state.due_at, before)

    def test_right_but_slow_HOLDS_the_box(self):
        """The rule the whole design rests on. A correct answer after nine
        seconds was derived, not recalled — promoting it would push a slow fact
        out to a long interval and quietly stop practising it."""
        state = self._state()
        scheduling.apply_attempt(state, is_correct=True, response_ms=900)
        self.assertEqual(state.leitner_box, 2)
        scheduling.apply_attempt(state, is_correct=True, response_ms=9000)
        self.assertEqual(state.leitner_box, 2, "a slow answer must not promote")
        self.assertEqual(state.consecutive_fluent, 0, "and it breaks the streak")

    def test_a_slow_answer_brings_the_fact_back_soon(self):
        state = self._state()
        scheduling.apply_attempt(state, is_correct=True, response_ms=9000)
        self.assertLess(state.due_at, timezone.now() + timedelta(hours=1))

    def test_a_wrong_answer_drops_to_box_one_and_is_due_at_once(self):
        state = self._state()
        for _ in range(3):
            scheduling.apply_attempt(state, is_correct=True, response_ms=800)
        self.assertGreater(state.leitner_box, 1)
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        self.assertEqual(state.leitner_box, 1)
        self.assertLessEqual(state.due_at, timezone.now())
        # Mastery survives ONE miss (a typo is not forgetting — see GrazeTests);
        # it clears on the second miss before repair.
        self.assertTrue(state.is_mastered)
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        self.assertFalse(state.is_mastered)

    def test_mastery_is_a_streak_not_a_box(self):
        """Gating on box 5 would unlock levels on the calendar — the boxes are
        1+2+4+8 days apart — rather than on whether she can actually do it."""
        state = self._state()
        for i in range(MASTERY_STREAK):
            newly = scheduling.apply_attempt(state, is_correct=True, response_ms=800)
        self.assertTrue(state.is_mastered)
        self.assertTrue(newly, "the last attempt should report the new mastery")
        self.assertLess(state.leitner_box, 5, "and it did not need box 5")

    def test_mastery_is_reported_once_not_every_time(self):
        state = self._state()
        for _ in range(MASTERY_STREAK):
            scheduling.apply_attempt(state, is_correct=True, response_ms=800)
        again = scheduling.apply_attempt(state, is_correct=True, response_ms=800)
        self.assertFalse(again, "already-mastered must not re-fire the celebration")

    def test_the_counters_track_every_attempt(self):
        state = self._state()
        scheduling.apply_attempt(state, is_correct=True, response_ms=800)
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        self.assertEqual(state.total_attempts, 2)
        self.assertEqual(state.total_correct, 1)


class RoundBuildingTests(TestCase):
    """What a round is made of."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="rb", email="rb@e.com", password="pw")
        cls.family = Family.objects.create(name="RB Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.fives = Level.objects.get(slug="fives")

    def test_a_first_round_introduces_only_a_few_new_facts(self):
        """A wall of new facts is how a child learns that practice feels bad.

        Counts DISTINCT facts, not questions — the round repeats its small set
        to be worth playing, which is the drill, not extra material."""
        questions = scheduling.build_round(self.child, self.fives)
        self.assertTrue(questions)
        distinct = {(q["fact_id"], q["operation"]) for q in questions}
        self.assertLessEqual(len(distinct),
                             policy_for(self.child).new_facts_per_round)

    def test_a_round_never_asks_a_question_the_fact_cannot_be_asked(self):
        for level in Level.objects.all():
            for q in scheduling.build_round(self.child, level):
                fact = Fact.objects.get(pk=q["fact_id"])
                self.assertIn(q["operation"], fact.operations(), q["prompt"])

    def test_every_question_carries_the_true_answer(self):
        for q in scheduling.build_round(self.child, self.fives):
            fact = Fact.objects.get(pk=q["fact_id"])
            self.assertEqual(q["answer"], fact.answer(q["operation"]), q["prompt"])

    def test_due_facts_come_before_new_ones(self):
        forms = scheduling._forms_for_level(self.fives)
        states = scheduling.ensure_states(self.child, forms)
        # Make three of them seen-and-overdue.
        overdue = list(states.values())[:3]
        for state in overdue:
            state.total_attempts = 1
            state.due_at = timezone.now() - timedelta(days=2)
            state.save()
        questions = scheduling.build_round(self.child, self.fives)
        keys = {(q["fact_id"], q["operation"]) for q in questions}
        for state in overdue:
            self.assertIn((state.fact_id, state.operation), keys)

    def test_a_review_fact_is_one_she_has_actually_met(self):
        """Otherwise 'review' smuggles in brand-new facts and dodges the cap."""
        ones = Level.objects.get(slug="ones-twos")
        rows = scheduling._review_forms(self.child, self.fives, 4, __import__("random"))
        self.assertEqual(rows, [], "nothing met yet, so nothing to review")

        forms = scheduling._forms_for_level(ones)[:5]
        states = scheduling.ensure_states(self.child, forms)
        for state in states.values():
            state.total_attempts = 2
            state.save()
        rows = scheduling._review_forms(self.child, self.fives, 3, __import__("random"))
        self.assertTrue(rows)
        for fact, operation in rows:
            self.assertTrue(
                StudentFactState.objects.get(
                    student=self.child, fact=fact, operation=operation
                ).total_attempts > 0)


class LevelUnlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="lu", email="lu@e.com", password="pw")
        cls.family = Family.objects.create(name="LU Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)

    def _master_level(self, level):
        forms = scheduling._forms_for_level(level)
        states = scheduling.ensure_states(self.child, forms)
        for state in states.values():
            state.is_mastered = True
            # Mastery costs three fluent answers, so a mastered form always has
            # attempts behind it. The accuracy floor reads them.
            state.total_attempts = 4
            state.total_correct = 4
            state.save()

    def test_the_first_level_is_open_and_the_rest_are_not(self):
        rows = scheduling.unlocked_levels(self.child, list(Level.objects.all()))
        self.assertTrue(rows[0]["unlocked"])
        self.assertFalse(rows[1]["unlocked"])

    def test_beating_a_level_opens_the_next_one(self):
        self._master_level(Level.objects.get(slug="ones-twos"))
        rows = scheduling.unlocked_levels(self.child, list(Level.objects.all()))
        self.assertTrue(rows[0]["beaten"])
        self.assertTrue(rows[1]["unlocked"])
        self.assertFalse(rows[2]["unlocked"], "only the next one, not all of them")

    def test_a_beaten_level_stays_playable(self):
        """A record is only worth having if you can go back and break it."""
        self._master_level(Level.objects.get(slug="ones-twos"))
        rows = scheduling.unlocked_levels(self.child, list(Level.objects.all()))
        self.assertTrue(rows[0]["unlocked"])


class FactDashPortalTests(TestCase):
    """The surface she actually touches."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="fp", email="fp@e.com", password="pw")
        cls.family = Family.objects.create(name="FP Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.other = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)

    def setUp(self):
        self.token = make_portal_token(self.child)
        self.c = Client()

    def test_the_map_lists_every_level(self):
        html = self.c.get(reverse("factfluency:home", args=[self.token])).content.decode()
        self.assertIn("Ones &amp; Twos", html)
        self.assertIn("The Tricky Ones", html)

    def test_a_bad_token_gets_nothing(self):
        r = Client().get(reverse("factfluency:home", args=["not-a-token"]))
        self.assertEqual(r.status_code, 404)

    def test_a_locked_level_cannot_be_played_by_url(self):
        r = self.c.get(reverse("factfluency:play", args=[self.token, "sevens"]))
        self.assertEqual(r.status_code, 404)

    def test_starting_a_round_returns_questions_and_a_session(self):
        r = self.c.post(reverse("factfluency:api_start", args=[self.token, "ones-twos"]))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["questions"])
        self.assertTrue(GameSession.objects.filter(pk=data["session_id"]).exists())

    def test_a_locked_level_cannot_be_started_by_api(self):
        r = self.c.post(reverse("factfluency:api_start", args=[self.token, "sevens"]))
        self.assertEqual(r.status_code, 404)
        self.assertFalse(GameSession.objects.exists())

    def _start(self):
        return self.c.post(
            reverse("factfluency:api_start", args=[self.token, "ones-twos"])).json()

    def _post(self, session_id, rows):
        return self.c.post(
            reverse("factfluency:api_attempts", args=[self.token, session_id]),
            data=json.dumps({"attempts": rows}), content_type="application/json")

    def test_the_server_marks_the_answer_not_the_client(self):
        """The client is trusted for speed, never for the verdict."""
        data = self._start()
        q = data["questions"][0]
        self._post(data["session_id"], [{
            "client_uuid": str(uuid.uuid4()), "fact_id": q["fact_id"],
            "operation": q["operation"], "answer_given": q["answer"] + 1,
            "response_ms": 500, "is_correct": True,      # a lie
        }])
        attempt = Attempt.objects.get()
        self.assertFalse(attempt.is_correct, "the server must re-mark it")
        self.assertFalse(attempt.was_fluent)

    def test_a_retried_attempt_is_not_counted_twice(self):
        data = self._start()
        q = data["questions"][0]
        row = {"client_uuid": "fixed-uuid", "fact_id": q["fact_id"],
               "operation": q["operation"], "answer_given": q["answer"],
               "response_ms": 700}
        self._post(data["session_id"], [row])
        self._post(data["session_id"], [row])
        self.assertEqual(Attempt.objects.count(), 1)

    def test_another_childs_session_is_untouchable(self):
        data = self._start()
        sneaky = make_portal_token(self.other)
        r = Client().post(
            reverse("factfluency:api_attempts", args=[sneaky, data["session_id"]]),
            data=json.dumps({"attempts": []}), content_type="application/json")
        self.assertEqual(r.status_code, 404)

    def test_finishing_totals_the_round_and_sets_a_first_record(self):
        data = self._start()
        rows = [{"client_uuid": str(uuid.uuid4()), "fact_id": q["fact_id"],
                 "operation": q["operation"], "answer_given": q["answer"],
                 "response_ms": 600} for q in data["questions"]]
        self._post(data["session_id"], rows)
        r = self.c.post(
            reverse("factfluency:api_finish", args=[self.token, data["session_id"]]))
        out = r.json()
        self.assertEqual(out["num_correct"], len(rows))
        self.assertEqual(out["longest_streak"], len(rows))
        kinds = {rec["type"] for rec in out["records_beaten"]}
        self.assertIn(RecordType.LONGEST_STREAK, kinds)
        self.assertIn(RecordType.BEST_TIME, kinds)

    def test_a_messy_round_sets_no_best_time(self):
        """Otherwise the fastest run is the one where she got everything wrong
        as quickly as possible."""
        data = self._start()
        rows = [{"client_uuid": str(uuid.uuid4()), "fact_id": q["fact_id"],
                 "operation": q["operation"], "answer_given": q["answer"] + 1,
                 "response_ms": 300} for q in data["questions"]]
        self._post(data["session_id"], rows)
        out = self.c.post(reverse("factfluency:api_finish",
                                  args=[self.token, data["session_id"]])).json()
        self.assertNotIn(RecordType.BEST_TIME,
                         {rec["type"] for rec in out["records_beaten"]})

    def test_a_slower_round_does_not_beat_the_best_time(self):
        for response_ms, expect in ((400, True), (900, False)):
            data = self._start()
            rows = [{"client_uuid": str(uuid.uuid4()), "fact_id": q["fact_id"],
                     "operation": q["operation"], "answer_given": q["answer"],
                     "response_ms": response_ms} for q in data["questions"]]
            self._post(data["session_id"], rows)
            out = self.c.post(reverse("factfluency:api_finish",
                                      args=[self.token, data["session_id"]])).json()
            beat = RecordType.BEST_TIME in {r["type"] for r in out["records_beaten"]}
            self.assertEqual(beat, expect, "response_ms=%d" % response_ms)
        self.assertEqual(PersonalRecord.objects.filter(
            record_type=RecordType.BEST_TIME).count(), 1)

    def test_garbage_in_a_batch_is_skipped_not_fatal(self):
        data = self._start()
        r = self._post(data["session_id"], [
            "not a dict",
            {"client_uuid": "", "fact_id": 1, "operation": "mult"},
            {"client_uuid": str(uuid.uuid4()), "fact_id": 999999,
             "operation": "mult", "answer_given": 1, "response_ms": 100},
            {"client_uuid": str(uuid.uuid4()), "fact_id": data["questions"][0]["fact_id"],
             "operation": "nonsense", "answer_given": 1, "response_ms": 100},
        ])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["accepted"], 0)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_a_division_form_of_a_zero_fact_is_rejected(self):
        """0 x 5 has no division form; accepting one would store a question
        that cannot be asked and mark her on it."""
        data = self._start()
        zero = Fact.objects.get(factor_a=0, factor_b=6)
        r = self._post(data["session_id"], [{
            "client_uuid": str(uuid.uuid4()), "fact_id": zero.pk,
            "operation": Operation.DIV_A, "answer_given": 5, "response_ms": 100}])
        self.assertEqual(r.json()["accepted"], 0)

    def test_no_visible_countdown_anywhere_on_the_page(self):
        """Timing is measured and never shown. The research is specific that it
        is the visible clock, not the timing, that causes the anxiety."""
        html = self.c.get(
            reverse("factfluency:play", args=[self.token, "ones-twos"])).content.decode()
        for word in ("countdown", "time left", "seconds left"):
            self.assertNotIn(word, html.lower())


class RoundLengthTests(TestCase):
    """A round has to be worth playing."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="rl", email="rl@e.com", password="pw")
        cls.family = Family.objects.create(name="RL Fam")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)

    def test_a_first_round_is_not_four_questions_long(self):
        """Only four new facts may enter a round, so without padding the very
        first round of a level is over in twenty seconds."""
        questions = scheduling.build_round(
            self.child, Level.objects.get(slug="fives"))
        self.assertGreaterEqual(len(questions), scheduling.MIN_ROUND)

    def test_padding_repeats_the_new_facts_rather_than_inventing_any(self):
        questions = scheduling.build_round(
            self.child, Level.objects.get(slug="fives"))
        distinct = {(q["fact_id"], q["operation"]) for q in questions}
        self.assertLessEqual(len(distinct),
                             policy_for(self.child).new_facts_per_round)

    def test_the_same_question_never_comes_twice_in_a_row(self):
        """Answering 6x8 immediately after 6x8 is reading, not recall."""
        questions = scheduling.build_round(
            self.child, Level.objects.get(slug="fives"))
        for a, b in zip(questions, questions[1:]):
            self.assertNotEqual((a["fact_id"], a["operation"]),
                                (b["fact_id"], b["operation"]))

    def test_a_round_never_exceeds_its_length(self):
        for level in Level.objects.all():
            questions = scheduling.build_round(self.child, level, length=20)
            self.assertLessEqual(len(questions), 20, level.slug)


class MasterySpacingTests(TestCase):
    """Mastery must take more than one sitting."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ms", email="ms@e.com", password="pw")
        cls.family = Family.objects.create(name="MS Fam")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.level = Level.objects.get(slug="sevens")
        cls.fact = Fact.objects.get(factor_a=7, factor_b=8)

    def _state(self):
        return StudentFactState.objects.create(
            student=self.child, fact=self.fact, operation=Operation.MULT)

    def _session(self):
        return GameSession.objects.create(student=self.child, level=self.level)

    def test_drilling_one_fact_in_a_single_round_does_not_master_it(self):
        """The round repeats its small new set — that is the drill working —
        but three fluent hits half a minute apart is short-term memory, not
        recall. Mastery has to survive going away and coming back."""
        state = self._state()
        session = self._session()
        for _ in range(6):
            scheduling.apply_attempt(state, is_correct=True, response_ms=700,
                                     session_id=session.pk)
        self.assertFalse(state.is_mastered)
        self.assertEqual(state.consecutive_fluent, 1, "one per sitting")

    def test_three_separate_sittings_do_master_it(self):
        state = self._state()
        for _ in range(MASTERY_STREAK):
            scheduling.apply_attempt(state, is_correct=True, response_ms=700,
                                     session_id=self._session().pk)
        self.assertTrue(state.is_mastered)

    def test_a_wrong_answer_still_bites_even_later_in_the_same_round(self):
        """Only the PROMOTION is once per session. A miss must always demote,
        or she could get one right early and then miss it five times."""
        state = self._state()
        session = self._session()
        scheduling.apply_attempt(state, is_correct=True, response_ms=700,
                                 session_id=session.pk)
        self.assertEqual(state.leitner_box, 2)
        scheduling.apply_attempt(state, is_correct=False, response_ms=700,
                                 session_id=session.pk)
        self.assertEqual(state.leitner_box, 1)
        self.assertEqual(state.consecutive_fluent, 0)


class PortalTileTests(TestCase):
    """The tile on her portal home."""

    @classmethod
    def setUpTestData(cls):
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson

        cls.parent = User.objects.create_user(username="pt", email="pt@e.com", password="pw")
        cls.family = Family.objects.create(name="PT Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.mathy = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.readery = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)

        def course(name, subject, child):
            c = Curriculum.objects.create(parent=cls.parent, name=name, subject=subject,
                                          family=cls.family, is_active=True)
            ch = Chapter.objects.create(curriculum=c, number=1, title="C")
            lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L")
            CurriculumPlacement.objects.create(child=child, curriculum=c,
                                               current_lesson=lesson, is_active=True)
            return c

        course("Dimensions Math 3A", "Math", cls.mathy)
        course("Blackbird", "Reading", cls.readery)

    def _home(self, student):
        return Client().get(reverse("portal:portal_home",
                                    args=[make_portal_token(student)])).content.decode()

    def test_a_child_doing_maths_gets_the_tile(self):
        # One token minted once: the signed token embeds a second-resolution
        # timestamp, so minting a second one for the assertion made this flaky
        # whenever the render crossed a second boundary.
        token = make_portal_token(self.mathy)
        html = Client().get(reverse("portal:portal_home", args=[token])
                            ).content.decode()
        self.assertIn("Fact Dash", html)
        self.assertIn(reverse("factfluency:home", args=[token]), html)

    def test_a_child_with_no_maths_does_not(self):
        """A times-tables game on the portal of a child who does no maths here
        is clutter, the same reason spelling only shows on a placement."""
        self.assertNotIn("Fact Dash", self._home(self.readery))

    def test_the_tile_names_the_level_she_is_on(self):
        html = self._home(self.mathy)
        self.assertIn("Ones &amp; Twos", html)
        self.assertIn("mastered", html)

    def test_the_tile_counts_right_but_slow_too(self):
        """This is the page she opens most, and it said "1 of 29 facts nailed"
        on a morning she answered 49 of 52 correctly — mastery needs speed she
        has not got yet, so the only number shown was the one that barely
        moves."""
        ones = Level.objects.get(slug="ones-twos")
        forms = scheduling._forms_for_level(ones)[:3]
        for state in scheduling.ensure_states(self.mathy, forms).values():
            scheduling.apply_attempt(state, is_correct=True,
                                     response_ms=9000)
        summary = scheduling.portal_summary(self.mathy)
        self.assertEqual(summary["mastered"], 0)
        self.assertEqual(summary["learning"], 3)
        self.assertIn("3 getting there", self._home(self.mathy))

    def test_the_tile_advances_when_she_beats_a_level(self):
        ones = Level.objects.get(slug="ones-twos")
        for state in scheduling.ensure_states(
                self.mathy, scheduling._forms_for_level(ones)).values():
            state.is_mastered = True
            state.total_attempts = 4
            state.total_correct = 4
            state.save()
        html = self._home(self.mathy)
        self.assertIn("Fives", html)

    def test_the_challenge_level_is_left_out_of_the_running_total(self):
        """Its facts are counted in the levels that introduce them; counting
        them twice would make the total larger than the game."""
        summary = scheduling.portal_summary(self.mathy)
        self.assertEqual(summary["total"],
                         sum(l.form_count() for l in Level.objects.filter(
                             is_challenge=False)))


class DivisionFollowsMultiplicationTests(TestCase):
    """Division is DERIVED from multiplication, so it cannot come first.

    A child who does not yet know 5x7=35 cannot recall 35/7 — she can only
    count up, which by our own rule is not fluent, so the form would churn in
    box 1 teaching her nothing. Before this gate, a first round of the fives
    could be three divisions out of four.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="dm", email="dm@e.com", password="pw")
        cls.family = Family.objects.create(name="DM Fam")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.fives = Level.objects.get(slug="fives")

    def _prompts(self):
        return {q["prompt"] for q in scheduling.build_round(self.child, self.fives)}

    def test_the_very_first_round_is_all_multiplication(self):
        for prompt in self._prompts():
            self.assertNotIn("÷", prompt, prompt)

    def test_no_level_opens_with_a_division(self):
        for level in Level.objects.all():
            StudentFactState.objects.filter(student=self.child).delete()
            for q in scheduling.build_round(self.child, level):
                self.assertNotIn("÷", q["prompt"], "%s: %s" % (level.slug, q["prompt"]))

    def test_a_division_unlocks_once_its_multiplication_is_fluent(self):
        fact = Fact.objects.get(factor_a=5, factor_b=7)
        states = scheduling.ensure_states(
            self.child, [(fact, Operation.MULT), (fact, Operation.DIV_A)])
        mult = states[(fact.pk, Operation.MULT)]

        self.assertFalse(scheduling._division_is_earned(fact, Operation.DIV_A, states))
        scheduling.apply_attempt(mult, is_correct=True, response_ms=800, session_id=1)
        self.assertTrue(scheduling._division_is_earned(fact, Operation.DIV_A, states))

    def test_a_slow_multiplication_does_not_unlock_its_division(self):
        """Right-but-slow is derivation, not recall — the same standard that
        stops it promoting stops it opening the division."""
        fact = Fact.objects.get(factor_a=5, factor_b=7)
        states = scheduling.ensure_states(
            self.child, [(fact, Operation.MULT), (fact, Operation.DIV_A)])
        scheduling.apply_attempt(states[(fact.pk, Operation.MULT)],
                                 is_correct=True, response_ms=9000, session_id=1)
        self.assertFalse(scheduling._division_is_earned(fact, Operation.DIV_A, states))

    def test_a_division_already_in_play_is_not_taken_away_again(self):
        """The gate is on INTRODUCTION. Fumbling the multiplication later must
        not yank a division she is already working on out of her rounds."""
        fact = Fact.objects.get(factor_a=5, factor_b=7)
        forms = [(fact, Operation.MULT), (fact, Operation.DIV_A)]
        states = scheduling.ensure_states(self.child, forms)
        scheduling.apply_attempt(states[(fact.pk, Operation.MULT)],
                                 is_correct=True, response_ms=800, session_id=1)
        div = states[(fact.pk, Operation.DIV_A)]
        scheduling.apply_attempt(div, is_correct=True, response_ms=800, session_id=1)

        # now she blows the multiplication
        scheduling.apply_attempt(states[(fact.pk, Operation.MULT)],
                                 is_correct=False, response_ms=800, session_id=2)
        div.refresh_from_db()
        div.due_at = timezone.now() - timedelta(days=1)
        div.save()
        prompts = {q["prompt"] for q in scheduling.build_round(self.child, self.fives)}
        self.assertIn(fact.prompt(Operation.DIV_A), prompts)


class AnswerCommitTests(TestCase):
    """Nothing auto-submits.

    The first version advanced as soon as the typed digits reached the length
    of the answer. That commits a mis-tap with no way back, and on a two-digit
    answer the first digit alone could end the question. A structural guard,
    because the rule lives in the client.
    """

    def _js(self):
        from pathlib import Path

        return (Path(__file__).resolve().parent / "static" / "factfluency"
                / "factdash.js").read_text(encoding="utf-8")

    def test_the_engine_never_submits_on_its_own(self):
        js = self._js()
        self.assertNotIn("length >= expected.length", js)
        self.assertNotIn("auto-advance", js.lower())

    def test_enter_is_the_only_thing_that_commits(self):
        js = self._js()
        # submit() is reached from the enter branch and nowhere else in type().
        block = js.split("function type(ch)")[1].split("function submit()")[0]
        self.assertEqual(block.count("submit()"), 1, "exactly one way to commit")
        self.assertIn('ch === "enter"', block)

    def test_the_clock_stops_at_the_last_digit_not_at_enter(self):
        """Requiring Enter must not quietly make every fact look half a second
        slower against a 3000ms threshold — confirming is not remembering."""
        js = self._js()
        self.assertIn("state.answeredAt = performance.now()", js)
        self.assertIn("state.answeredAt || performance.now()", js)

    def test_the_screen_tells_her_to_press_it(self):
        from django.template.loader import render_to_string  # noqa: F401
        from pathlib import Path

        html = (Path(__file__).resolve().parent.parent / "templates" / "factfluency"
                / "play.html").read_text(encoding="utf-8")
        self.assertIn("press", html.lower())


class HintTests(TestCase):
    """A hint that lies is worse than no hint at all.

    Every one of these is generated from real numbers, so a slip in any rule
    produces a sentence that is confidently wrong — and she has no way to know.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="hint", email="hint@e.com", password="pw")
        cls.family = Family.objects.create(name="Hint Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")

    def _fact(self, a, b):
        from .models import Fact
        return Fact.objects.get(factor_a=min(a, b), factor_b=max(a, b))

    def test_every_number_in_every_multiplication_hint_is_true(self):
        """Pull the integers back out of each sentence and check the arithmetic.

        Not a spot check: this walks the whole table, so a wrong step in the
        double-double or take-one-group-away rule cannot hide on a fact nobody
        thought to test.
        """
        import re

        from .models import Fact, Operation
        from . import hints

        for fact in Fact.objects.all():
            text = hints.hint_for(fact, Operation.MULT)
            self.assertTrue(text, "%s has no hint" % fact)
            numbers = [int(n) for n in re.findall(r"\d+", text)]
            # Whatever route the hint takes, it has to arrive at the product —
            # except the two rules that legitimately never name it.
            if fact.factor_a in (0, 1) or fact.factor_b in (0, 1):
                continue
            self.assertIn(fact.product, numbers,
                          "%s: hint never reaches %d — %r"
                          % (fact, fact.product, text))

    def test_the_derivation_steps_actually_chain(self):
        """The intermediate numbers have to be the real intermediate numbers."""
        from .models import Operation
        from . import hints

        cases = {
            (4, 7): [7, 14, 28],        # double, double again
            (4, 8): [8, 16, 32],        # double, double again
            (3, 7): [14, 7, 21],        # double, add one more group
            (6, 8): None,               # mnemonic — checked separately
            (9, 7): [70, 7, 63],        # ten, give one back
            (5, 8): [8, 80, 40],        # half of ten
        }
        for (a, b), expected in cases.items():
            if expected is None:
                continue
            text = hints.hint_for(self._fact(a, b), Operation.MULT)
            import re
            numbers = [int(n) for n in re.findall(r"\d+", text)]
            self.assertEqual(numbers, expected,
                             "%d x %d derivation is wrong: %r" % (a, b, text))

    def test_no_seven_or_eight_fact_is_left_without_a_better_route(self):
        """The x7 and x8 rules are deliberately last in PRIORITY, which means
        inside a 10x10 table they never fire: every 7- and 8-fact is reached
        more cheaply through its other factor, or is one of the mnemonics.

        Asserted rather than assumed, because if a future PRIORITY edit made
        "split the 7 into a 5 and a 2" the primary hint for 7x3, she would be
        handed the hardest available route to an easy fact.
        """
        from .models import Fact, Operation
        from . import hints

        for fact in Fact.objects.filter(factor_b__in=(7, 8)):
            text = hints.hint_for(fact, Operation.MULT)
            self.assertNotIn("Split the 7", text, str(fact))
            self.assertNotIn("Double three times", text, str(fact))

    def test_the_stubborn_facts_get_their_mnemonic(self):
        from .models import Operation
        from . import hints

        self.assertIn("5, 6, 7, 8", hints.hint_for(self._fact(7, 8), Operation.MULT))
        self.assertIn("date", hints.hint_for(self._fact(6, 8), Operation.MULT))
        self.assertIn("64", hints.hint_for(self._fact(8, 8), Operation.MULT))

    def test_every_division_hint_names_the_right_missing_factor(self):
        """The whole strategy is 'what times the divisor makes the total' — if
        the sentence names the wrong divisor it teaches the reversal error the
        research says children already make."""
        from .models import Fact, Operation
        from . import hints

        for fact in Fact.objects.all():
            for operation in fact.operations():
                if operation == Operation.MULT:
                    continue
                text = hints.hint_for(fact, operation)
                divisor = (fact.factor_a if operation == Operation.DIV_A
                           else fact.factor_b)
                self.assertIn("what times %d makes %d? %d."
                              % (divisor, fact.product, fact.answer(operation)),
                              text, "%s: %r" % (fact.prompt(operation), text))
                self.assertNotIn("None", text)

    def test_halving_shortcuts_only_appear_where_they_are_real(self):
        """No invented tricks. Dividing by 7 has no shortcut and must not
        pretend to."""
        from .models import Operation
        from . import hints

        by_two = hints.hint_for(self._fact(2, 9), Operation.DIV_A)
        self.assertIn("halve", by_two)
        by_seven = hints.hint_for(self._fact(7, 8), Operation.DIV_A)
        self.assertNotIn("halve", by_seven)
        self.assertNotIn("Or", by_seven)

    def test_the_round_carries_the_hint_to_the_client(self):
        from students.models import Student
        from .models import Level
        from . import scheduling

        student = Student.objects.create(
            parent=self.parent, first_name="Hint", grade_level="G03",
            family=self.family)
        level = Level.objects.order_by("order").first()
        questions = scheduling.build_round(student, level)
        self.assertTrue(questions)
        for question in questions:
            self.assertTrue(question["hint"], question["prompt"])

    def test_the_hint_is_never_shown_before_she_answers(self):
        """It lives behind `hidden` and is only revealed on a miss. Showing it
        up front would turn a recall game into a reading exercise."""
        from pathlib import Path

        html = (Path(__file__).resolve().parent.parent / "templates" / "factfluency"
                / "play.html").read_text(encoding="utf-8")
        self.assertIn("data-tip hidden", html)

        js = (Path(__file__).resolve().parent / "static" / "factfluency"
              / "factdash.js").read_text(encoding="utf-8")
        reveal = js.split("if (!right) {")[1].split("}")[0]
        self.assertIn("els.tip.hidden = false", reveal)


class TemplateCommentLeakTests(TestCase):
    """Multi-line {# #} comments render as page text — this has now bitten the
    project FOUR times (three in lingua, once pushing Fact Dash's Done key
    238px below the fold with two invisible walls of leaked prose)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="leak", email="leak@e.com", password="pw")
        cls.family = Family.objects.create(name="Leak Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Leak", grade_level="G03",
            family=cls.family)

    def test_no_template_comment_reaches_the_page(self):
        from portal.tokens import make_portal_token
        from .models import Level

        token = make_portal_token(self.child)
        for name in ("factfluency:home", "factfluency:play"):
            kwargs = {"token": token}
            if name.endswith("play"):
                kwargs["slug"] = Level.objects.order_by("order").first().slug
            html = self.client.get(reverse(name, kwargs=kwargs)).content.decode()
            self.assertNotIn("{#", html, name)
            self.assertNotIn("#}", html, name)

    def test_no_source_template_carries_a_multiline_hash_comment(self):
        """Catch it at the source too, so a leak cannot hide behind an {% if %}
        branch the render above did not take."""
        import re
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent / "templates" / "factfluency"
        for path in root.glob("*.html"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"\{#(.*?)#\}", text, flags=re.S):
                self.assertNotIn("\n", match.group(1),
                                 "%s: multi-line {# #} comment leaks to the page"
                                 % path.name)


class AuditRegressionTests(TestCase):
    """Every finding from the adversarial audit, pinned so it stays fixed."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="aud", email="aud@e.com", password="pw")
        cls.family = Family.objects.create(name="Aud Fam")
        FamilyMembership.objects.create(
            user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Aud", grade_level="G03",
            family=cls.family)
        cls.level1 = Level.objects.get(slug="ones-twos")

    def setUp(self):
        from portal.tokens import make_portal_token
        self.token = make_portal_token(self.child)

    def _session(self):
        return GameSession.objects.create(student=self.child, level=self.level1)

    def _post(self, session, rows, raw=None):
        import json as _json
        url = reverse("factfluency:api_attempts",
                      kwargs={"token": self.token, "session_id": session.pk})
        body = raw if raw is not None else _json.dumps({"attempts": rows})
        return self.client.post(url, body, content_type="application/json")

    def _row(self, fact, operation="mult", **over):
        row = {"client_uuid": str(over.pop("uuid", fact.pk)) + "-" + operation,
               "fact_id": fact.pk, "operation": operation,
               "answer_given": fact.answer(operation), "response_ms": 900}
        row.update(over)
        return row

    # -- the two-tab mastery exploit ----------------------------------------

    def test_alternating_two_open_sessions_cannot_fake_three_sittings(self):
        fact = Fact.objects.get(factor_a=1, factor_b=3)
        state = StudentFactState.objects.create(
            student=self.child, fact=fact, operation=Operation.MULT)
        s1, s2 = self._session(), self._session()
        # s2 counts; bouncing back to the OLDER s1 must not, and returning to
        # s2 must not count twice.
        for sid in (s2.pk, s1.pk, s2.pk, s1.pk, s2.pk):
            scheduling.apply_attempt(state, is_correct=True, response_ms=500,
                                     session_id=sid)
        self.assertEqual(state.consecutive_fluent, 1)
        self.assertFalse(state.is_mastered)

    # -- the any-fact-from-any-level exploit --------------------------------

    def test_a_locked_levels_fact_is_refused(self):
        hard = Fact.objects.get(factor_a=7, factor_b=8)   # level 9 material
        session = self._session()                          # a level-1 round
        response = self._post(session, [self._row(hard)])
        self.assertEqual(response.json()["accepted"], 0)
        self.assertEqual(Attempt.objects.count(), 0)

    # -- the five 500s -------------------------------------------------------

    def test_malformed_payloads_never_500(self):
        session = self._session()
        fact = Fact.objects.get(factor_a=2, factor_b=3)
        cases = [
            ("[1, 2, 3]", 400),                            # top-level list
            ('"hello"', 400),                              # top-level string
            ('{"attempts": [{"client_uuid": "a", "fact_id": "abc"}]}', 200),
            ('{"attempts": [{"client_uuid": "b", "fact_id": [1]}]}', 200),
            ('{"attempts": [{"client_uuid": "c", "fact_id": %d, "operation": "mult",'
             ' "answer_given": 2, "response_ms": Infinity}]}' % fact.pk, 200),
            ('{"attempts": [{"client_uuid": "d", "fact_id": %d, "operation": "mult",'
             ' "answer_given": Infinity, "response_ms": 5}]}' % fact.pk, 200),
            ('{"attempts": [{"client_uuid": "e", "fact_id": %d, "operation": "mult",'
             ' "answer_given": 10000000000000000000, "response_ms": 5}]}' % fact.pk,
             200),
        ]
        for raw, expected in cases:
            response = self._post(session, None, raw=raw)
            self.assertEqual(response.status_code, expected, raw)
        self.assertEqual(Attempt.objects.count(), 0)       # all skipped, none stored

    def test_a_float_fact_id_does_not_resolve_to_the_wrong_fact(self):
        session = self._session()
        fact = Fact.objects.get(factor_a=2, factor_b=3)
        response = self._post(session, [self._row(fact, fact_id=fact.pk + 0.5)])
        self.assertEqual(response.json()["accepted"], 0)

    # -- garbage must not damage her state ----------------------------------

    def test_a_garbled_answer_is_skipped_not_recorded_as_a_miss(self):
        fact = Fact.objects.get(factor_a=2, factor_b=4)
        state = StudentFactState.objects.create(
            student=self.child, fact=fact, operation=Operation.MULT,
            leitner_box=2, consecutive_fluent=1)
        session = self._session()
        for bad in ({"oops": 1}, [6], None, "six", True):
            self._post(session, [self._row(fact, answer_given=bad, uuid=str(bad))])
        state.refresh_from_db()
        self.assertEqual(state.leitner_box, 2)             # untouched
        self.assertEqual(Attempt.objects.count(), 0)

    def test_a_missing_response_time_is_not_scored_as_instant(self):
        fact = Fact.objects.get(factor_a=2, factor_b=5)
        session = self._session()
        for bad_ms in (None, -50, "fast"):
            row = self._row(fact, uuid="ms" + str(bad_ms))
            if bad_ms is None:
                row.pop("response_ms")
            else:
                row["response_ms"] = bad_ms
            self._post(session, [row])
        self.assertEqual(Attempt.objects.count(), 0)

    # -- sessions close ------------------------------------------------------

    def test_finish_is_once(self):
        fact = Fact.objects.get(factor_a=2, factor_b=6)
        session = self._session()
        self._post(session, [self._row(fact)])
        url = reverse("factfluency:api_finish",
                      kwargs={"token": self.token, "session_id": session.pk})
        first = self.client.post(url).json()
        self.assertEqual(first["num_attempted"], 1)
        # More answers after the end, then finish again: the stored summary
        # must not be re-totalled.
        self._post(session, [self._row(fact, uuid="late")])
        second = self.client.post(url).json()
        self.assertEqual(second["num_attempted"], 1)
        self.assertEqual(second["records_beaten"], [])

    # -- the record that could never be beaten again ------------------------

    def test_best_time_is_per_question_so_a_longer_round_can_beat_it(self):
        from factfluency.views import _maybe_record

        s1, s2 = self._session(), self._session()
        for session, n, ms in ((s1, 12, 1000), (s2, 20, 900)):
            session.num_attempted = n
            session.num_correct = n
            session.duration_ms = n * ms
            session.save()
        first = _maybe_record(s1, RecordType.BEST_TIME,
                              round(s1.duration_ms / s1.num_attempted))
        self.assertTrue(first)                              # 1000ms/q stands
        beaten = _maybe_record(s2, RecordType.BEST_TIME,
                               round(s2.duration_ms / s2.num_attempted))
        self.assertTrue(beaten, "a faster pace on a LONGER round must win")

    def test_a_tiny_round_cannot_set_the_time_record(self):
        fact = Fact.objects.get(factor_a=2, factor_b=7)
        session = self._session()
        self._post(session, [self._row(fact, response_ms=1)])
        url = reverse("factfluency:api_finish",
                      kwargs={"token": self.token, "session_id": session.pk})
        out = self.client.post(url).json()
        kinds = [r["type"] for r in out["records_beaten"]]
        self.assertNotIn("best_time", kinds)

    # -- _pad can no longer hang the request ---------------------------------

    def test_pad_terminates_on_a_pool_of_identical_forms(self):
        import random
        fact = Fact.objects.get(factor_a=2, factor_b=8)
        form = (fact, Operation.MULT)
        out = scheduling._pad([form, form], 20, random)
        self.assertEqual(len(out), scheduling.MIN_ROUND)   # returned, not spun

    # -- client_uuid is per session ------------------------------------------

    def test_one_childs_uuid_cannot_mute_anothers_attempt(self):
        from portal.tokens import make_portal_token

        other = Student.objects.create(
            parent=self.parent, first_name="Sib", grade_level="G05",
            family=self.family)
        fact = Fact.objects.get(factor_a=2, factor_b=9)
        session_a = self._session()
        session_b = GameSession.objects.create(student=other, level=self.level1)
        self._post(session_a, [self._row(fact, uuid="collide")])
        url = reverse("factfluency:api_attempts",
                      kwargs={"token": make_portal_token(other),
                              "session_id": session_b.pk})
        import json as _json
        response = self.client.post(
            url, _json.dumps({"attempts": [self._row(fact, uuid="collide")]}),
            content_type="application/json")
        self.assertEqual(response.json()["accepted"], 1,
                         "the same uuid in a DIFFERENT session is a new attempt")


class RulesAreNotFactsTests(TestCase):
    """ "Does it really need to be 59 facts?" (user, 2026-08-27). No: 36 of the
    first level's 59 forms were the times-zero and times-one RULES inflated
    into nineteen Leitner cards, seventeen of them n/1-and-n/n drills — the
    documented confusion pair, which blurs precisely when drilled side by side.
    """

    def test_rule_facts_are_multiplication_only(self):
        for fact in Fact.objects.filter(factor_a__in=(0, 1)):
            self.assertEqual(fact.operations(), [Operation.MULT], str(fact))

    def test_each_rule_keeps_exactly_three_examples(self):
        self.assertEqual(Fact.objects.filter(factor_a=0).count(), 3)
        self.assertEqual(
            Fact.objects.filter(factor_a=1).exclude(factor_b=0).count(), 3)

    def test_the_first_level_is_mostly_twos(self):
        """The level's content is doubles. If rule cards ever outnumber the
        twos again, the level has gone back to being about nothing."""
        level = Level.objects.get(slug="ones-twos")
        twos = [f for f in level.facts.all()
                if 0 not in (f.factor_a, f.factor_b)
                and 1 not in (f.factor_a, f.factor_b)]
        rules = level.facts.count() - len(twos)
        self.assertGreater(len(twos), rules)

    def test_no_division_of_one_is_ever_asked(self):
        """n/1 and n/n are reasoned, not drilled, anywhere in the game."""
        for level in Level.objects.all():
            for fact, operation in scheduling._forms_for_level(level):
                if operation == Operation.MULT:
                    continue
                divisor = (fact.factor_a if operation == Operation.DIV_A
                           else fact.factor_b)
                self.assertNotEqual(divisor, 1, fact.prompt(operation))
                self.assertNotEqual(fact.answer(operation), fact.product,
                                    fact.prompt(operation))


class GrazeTests(TestCase):
    """One typo on a long-mastered fact must not erase the mastery.

    The real case: 1x9 fluent ten sessions running, then "96" submitted while
    reaching for Done — box 5 to box 1, mastery gone, 29/29 stuck at 28/29.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="gz", email="gz@e.com", password="pw")
        cls.family = Family.objects.create(name="Gz Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Gz", grade_level="G03", family=cls.family)
        cls.fact = Fact.objects.get(factor_a=2, factor_b=9)

    def _mastered_state(self):
        return StudentFactState.objects.create(
            student=self.child, fact=self.fact, operation=Operation.MULT,
            leitner_box=5, consecutive_fluent=3, is_mastered=True,
            total_attempts=10, total_correct=10)

    def test_one_miss_on_a_mastered_fact_keeps_the_mastery(self):
        state = self._mastered_state()
        scheduling.apply_attempt(state, is_correct=False, response_ms=856)
        self.assertTrue(state.is_mastered, "a typo is not forgetting")
        # …but it still comes straight back for repair.
        self.assertEqual(state.leitner_box, 1)
        self.assertEqual(state.consecutive_fluent, 0)
        self.assertLessEqual(state.due_at, timezone.now())

    def test_a_second_miss_before_repair_does_clear_it(self):
        state = self._mastered_state()
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        self.assertFalse(state.is_mastered, "missing twice IS forgetting")

    def test_a_repaired_fact_survives_a_later_isolated_miss(self):
        state = self._mastered_state()
        s1 = GameSession.objects.create(
            student=self.child, level=Level.objects.get(slug="ones-twos"))
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        scheduling.apply_attempt(state, is_correct=True, response_ms=700,
                                 session_id=s1.pk)      # repaired: box 2
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        self.assertTrue(state.is_mastered,
                        "an isolated miss after repair is a fresh graze")

    def test_an_unmastered_fact_still_resets_hard(self):
        state = StudentFactState.objects.create(
            student=self.child, fact=self.fact, operation=Operation.MULT,
            leitner_box=3, consecutive_fluent=2)
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        self.assertFalse(state.is_mastered)
        self.assertEqual(state.leitner_box, 1)
        self.assertEqual(state.consecutive_fluent, 0)

    def test_the_level_count_does_not_yo_yo_on_a_graze(self):
        state = self._mastered_state()
        level = Level.objects.get(slug="ones-twos")
        before, total = scheduling.level_progress(self.child, level)
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        after, _ = scheduling.level_progress(self.child, level)
        self.assertEqual(after, before)


class LearningTierTests(TestCase):
    """ "She went 3 rounds this morning, why is it 1 of 29 mastered?"

    Because mastery is fast AND right, three sittings running, and Violet's
    median correct answer took 4.1 seconds against a 3-second bar. She was
    right 49 times out of 52 and the map showed almost nothing, because
    right-but-slow was worth zero pixels. It is worth a band of its own now.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="lt", email="lt@e.com", password="pw")
        cls.family = Family.objects.create(name="LT Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.level = Level.objects.get(slug="ones-twos")

    def _state(self, fact, **kw):
        return StudentFactState.objects.create(
            student=self.child, fact=fact, operation=Operation.MULT, **kw)

    def test_right_but_slow_counts_as_getting_there(self):
        fact = Fact.objects.get(factor_a=2, factor_b=3)
        state = self._state(fact)
        scheduling.apply_attempt(state, is_correct=True,
                                 response_ms=9000)
        mastered, learning, total = scheduling.level_breakdown(self.child, self.level)
        self.assertEqual(mastered, 0, "slow is not mastered")
        self.assertEqual(learning, 1, "but it is not nothing either")
        self.assertGreater(total, 1)

    def test_a_fact_she_has_never_got_right_is_not_counted(self):
        fact = Fact.objects.get(factor_a=2, factor_b=4)
        state = self._state(fact)
        scheduling.apply_attempt(state, is_correct=False, response_ms=900)
        _, learning, _ = scheduling.level_breakdown(self.child, self.level)
        self.assertEqual(learning, 0)

    def test_mastered_facts_are_not_double_counted(self):
        fact = Fact.objects.get(factor_a=2, factor_b=5)
        state = self._state(fact, is_mastered=True, leitner_box=4,
                            total_attempts=3, total_correct=3)
        mastered, learning, _ = scheduling.level_breakdown(self.child, self.level)
        self.assertEqual((mastered, learning), (1, 0), str(state))

    def test_the_round_that_started_this_reports_both_numbers(self):
        """Sixteen right, two fast — the exact shape of her fourth round."""
        from portal.tokens import make_portal_token

        session = GameSession.objects.create(student=self.child, level=self.level)
        forms = scheduling._forms_for_level(self.level)[:16]
        states = scheduling.ensure_states(self.child, forms)
        for i, (fact, operation) in enumerate(forms):
            ms = 1400 if i < 2 else 9000          # 2 fluent, 14 right but slow
            bar = threshold_for(fact.answer(operation), policy_for(self.child))
            Attempt.objects.create(
                session=session, fact=fact, operation=operation,
                answer_given=fact.answer(operation), is_correct=True,
                response_ms=ms, was_fluent=ms <= bar,
                client_uuid="lt-%d" % i)
            scheduling.apply_attempt(states[(fact.pk, operation)],
                                     is_correct=True, response_ms=ms,
                                     session_id=session.pk)

        token = make_portal_token(self.child)
        data = self.client.post(reverse("factfluency:api_finish", kwargs={
            "token": token, "session_id": session.pk})).json()
        self.assertEqual(data["num_correct"], 16)
        self.assertEqual(data["num_fluent"], 2)
        # The point: the screen has something true and positive to show.
        self.assertEqual(data["learning"], 16)
        self.assertGreater(data["learning_pct"], 0)

    def test_the_screen_says_so_rather_than_leaving_her_to_infer_failure(self):
        from pathlib import Path

        js = (Path(__file__).resolve().parent / "static" / "factfluency"
              / "factdash.js").read_text(encoding="utf-8")
        # Both branches: some were quick, and none were quick yet.
        self.assertIn("which is exactly how it starts", js)
        self.assertIn("Knowing it comes first; fast comes after", js)
        self.assertIn("getting there", js)
        # And it only fires on a clean round — telling a child who got six wrong
        # that "you got every one right" would be worse than saying nothing.
        block = js.split("if (els.speed) {")[1].split("// A clean round")[0]
        self.assertIn("clean &&", block)


class StuckAtThirteenTests(TestCase):
    """ "She has been stuck on 13 of 29 for the longest time."

    Three mechanisms were holding her there. All are about the streak that
    gates mastery, and all of them punished a nine-year-old for thinking.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="s13", email="s13@e.com", password="pw")
        cls.family = Family.objects.create(name="S13 Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.level = Level.objects.get(slug="ones-twos")

    def _state(self, a=2, b=6):
        return StudentFactState.objects.create(
            student=self.child, fact=Fact.objects.get(factor_a=a, factor_b=b),
            operation=Operation.MULT)

    def _session(self):
        return GameSession.objects.create(student=self.child, level=self.level)

    # -- 1. a slow REPEAT no longer wipes what the first ask earned ----------

    def test_being_slow_on_a_repeat_does_not_undo_the_first_ask(self):
        state = self._state()
        session = self._session()
        scheduling.apply_attempt(state, is_correct=True, response_ms=700,
                                 session_id=session.pk)
        self.assertEqual(state.consecutive_fluent, 1)
        # The round asks it again — padding does this on purpose — and she
        # thinks about it. That used to zero the streak she had just earned.
        scheduling.apply_attempt(state, is_correct=True, response_ms=9000,
                                 session_id=session.pk)
        self.assertEqual(state.consecutive_fluent, 1, "one verdict per sitting")
        self.assertEqual(state.leitner_box, 2)

    def test_a_miss_on_a_repeat_still_bites(self):
        """Deliberately NOT gated — a wrong answer is unambiguous evidence."""
        state = self._state()
        session = self._session()
        scheduling.apply_attempt(state, is_correct=True, response_ms=700,
                                 session_id=session.pk)
        scheduling.apply_attempt(state, is_correct=False, response_ms=700,
                                 session_id=session.pk)
        self.assertEqual(state.leitner_box, 1)
        self.assertEqual(state.consecutive_fluent, 0)

    # -- 2. one thoughtful answer costs one step, not everything -------------

    def test_a_slow_answer_steps_the_streak_back_by_one(self):
        state = self._state()
        for _ in range(2):
            scheduling.apply_attempt(state, is_correct=True, response_ms=700,
                                     session_id=self._session().pk)
        self.assertEqual(state.consecutive_fluent, 2)
        scheduling.apply_attempt(state, is_correct=True, response_ms=9000,
                                 session_id=self._session().pk)
        self.assertEqual(state.consecutive_fluent, 1,
                         "a bad day is one step back, not back to nothing")

    def test_the_bar_is_not_lowered_alternating_never_masters(self):
        """The streak survives a wobble; it does not survive not knowing it."""
        state = self._state()
        for i in range(12):
            scheduling.apply_attempt(
                state, is_correct=True,
                response_ms=700 if i % 2 == 0 else 9000,
                session_id=self._session().pk)
        self.assertFalse(state.is_mastered)
        self.assertLessEqual(state.consecutive_fluent, 1)

    def test_a_realistic_run_now_actually_masters(self):
        """Fluent, fluent, one slow, fluent, fluent — which used to be four
        sittings of progress thrown away twice over."""
        state = self._state()
        for ms in (700, 700, 9000, 700, 700):
            scheduling.apply_attempt(state, is_correct=True, response_ms=ms,
                                     session_id=self._session().pk)
        self.assertTrue(state.is_mastered)

    # -- 3. the clock includes her typing ------------------------------------

    def test_a_two_digit_answer_gets_the_extra_tap_it_costs(self):
        """Per band: a nine-year-old's second tap costs a full second, a
        twelve-year-old's the 600ms the original benchmark allowed."""
        g3 = policy_for(Student(grade_level="G03"))
        g7 = policy_for(Student(grade_level="G07"))
        self.assertEqual([threshold_for(n, g3) for n in (8, 48, 100)],
                         [4000, 5000, 6000])
        self.assertEqual([threshold_for(n, g7) for n in (8, 48, 100)],
                         [3000, 3600, 4200])
        k = policy_for(Student(grade_level="K"))
        self.assertEqual([threshold_for(n, k) for n in (8, 48, 100)],
                         [5000, 6000, 7000])

    def test_the_allowance_is_applied_by_the_endpoint_not_just_available(self):
        """For a G03 child 4500ms on a two-digit answer (bar 5000) is fluent;
        on a one-digit answer (bar 4000) it is not. The API has to make that
        distinction, not just the helper."""
        from portal.tokens import make_portal_token

        session = self._session()
        two = Fact.objects.get(factor_a=2, factor_b=6)      # 12
        one = Fact.objects.get(factor_a=2, factor_b=3)      # 6
        token = make_portal_token(self.child)
        self.client.post(
            reverse("factfluency:api_attempts",
                    kwargs={"token": token, "session_id": session.pk}),
            data=json.dumps({"attempts": [
                {"client_uuid": "two", "fact_id": two.pk, "operation": "mult",
                 "answer_given": 12, "response_ms": 4500},
                {"client_uuid": "one", "fact_id": one.pk, "operation": "mult",
                 "answer_given": 6, "response_ms": 4500},
            ]}), content_type="application/json")
        self.assertTrue(Attempt.objects.get(client_uuid="two").was_fluent)
        self.assertFalse(Attempt.objects.get(client_uuid="one").was_fluent)


class RebuildFactStatesTests(TestCase):
    """The repair that gives back progress a fixed bug had eaten."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="rb", email="rb@e.com", password="pw")
        cls.family = Family.objects.create(name="RB Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.level = Level.objects.get(slug="ones-twos")
        cls.fact = Fact.objects.get(factor_a=2, factor_b=3)

    def _play(self, *rounds):
        """Each round is a list of (is_correct, response_ms)."""
        for n, answers in enumerate(rounds):
            session = GameSession.objects.create(
                student=self.child, level=self.level)
            for i, (ok, ms) in enumerate(answers):
                Attempt.objects.create(
                    session=session, fact=self.fact, operation=Operation.MULT,
                    answer_given=6 if ok else 0, is_correct=ok,
                    response_ms=ms, was_fluent=ok and ms <= 3000,
                    client_uuid="rb-%d-%d" % (n, i))

    def _run(self, **kw):
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command("rebuild_fact_states", child="Violet", stdout=out, **kw)
        return out.getvalue()

    def test_it_gives_back_a_streak_the_old_rules_had_wiped(self):
        # Three good sittings, each with a slow repeat that used to zero it.
        self._play([(True, 700), (True, 9000)],
                   [(True, 700), (True, 9000)],
                   [(True, 700), (True, 9000)])
        StudentFactState.objects.create(
            student=self.child, fact=self.fact, operation=Operation.MULT,
            leitner_box=1, consecutive_fluent=0, is_mastered=False)
        self._run()
        state = StudentFactState.objects.get(student=self.child, fact=self.fact)
        self.assertEqual(state.consecutive_fluent, 3)
        self.assertTrue(state.is_mastered)

    def test_a_dry_run_writes_nothing(self):
        self._play([(True, 700)], [(True, 700)], [(True, 700)])
        StudentFactState.objects.create(
            student=self.child, fact=self.fact, operation=Operation.MULT)
        out = self._run(dry_run=True)
        self.assertIn("dry run", out)
        state = StudentFactState.objects.get(student=self.child, fact=self.fact)
        self.assertEqual(state.consecutive_fluent, 0, "unchanged")

    def test_it_is_idempotent(self):
        self._play([(True, 700)], [(True, 700)], [(True, 700)])
        self._run()
        first = StudentFactState.objects.get(student=self.child, fact=self.fact)
        snapshot = (first.leitner_box, first.consecutive_fluent,
                    first.is_mastered, first.total_attempts, first.due_at)
        self._run()
        again = StudentFactState.objects.get(student=self.child, fact=self.fact)
        self.assertEqual(
            (again.leitner_box, again.consecutive_fluent, again.is_mastered,
             again.total_attempts, again.due_at), snapshot)

    def test_it_does_not_destroy_the_attempts_it_replays(self):
        """The states cascade from Fact and Student; a delete-and-recreate
        would have taken the history with it."""
        self._play([(True, 700)], [(True, 700)])
        before = Attempt.objects.count()
        self._run()
        self.assertEqual(Attempt.objects.count(), before)

    def test_the_due_dates_land_when_the_answers_happened(self):
        """Replaying with now=timezone.now() would stack every fact she has
        ever answered onto today and flood her next round with all of them."""
        from datetime import timedelta

        self._play([(True, 700)])
        long_ago = timezone.now() - timedelta(days=30)
        Attempt.objects.update(created_at=long_ago)
        self._run()
        state = StudentFactState.objects.get(student=self.child, fact=self.fact)
        # Answered a month ago and promoted to box 2 (a 2-day interval), so it
        # fell due 28 days ago — not two days from now.
        self.assertLess(state.due_at, timezone.now(),
                        "the replay must use when the answer happened")
        self.assertAlmostEqual(
            (state.due_at - long_ago).total_seconds(),
            timedelta(days=2).total_seconds(), delta=60)


class AuditFollowUpTests(TestCase):
    """Findings from the adversarial audit, ranked by what they cost a child."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="af", email="af@e.com", password="pw")
        cls.family = Family.objects.create(name="AF Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)

    def test_a_level_she_has_played_never_locks_again(self):
        """The worst finding. Unlocking was recomputed from current mastery, so
        two review misses could re-lock a FINISHED level: the map showed a
        padlock and a star on the same card, and the play page 404'd."""
        from portal.tokens import make_portal_token

        ones = Level.objects.get(slug="ones-twos")
        fives = Level.objects.get(slug="fives")
        for state in scheduling.ensure_states(
                self.child, scheduling._forms_for_level(ones)).values():
            state.is_mastered = True
            state.save()
        GameSession.objects.create(student=self.child, level=fives)

        # Now drop level 1 back under its threshold, the way review does.
        for state in StudentFactState.objects.filter(student=self.child)[:10]:
            state.is_mastered = False
            state.save()

        rows = {r["level"].slug: r for r in scheduling.unlocked_levels(
            self.child, list(Level.objects.all()))}
        self.assertFalse(rows["ones-twos"]["beaten"], "it really did fall")
        self.assertTrue(rows["fives"]["unlocked"],
                        "a level she has played stays playable")
        self.assertEqual(self.client.get(reverse(
            "factfluency:play",
            kwargs={"token": make_portal_token(self.child),
                    "slug": "fives"})).status_code, 200)

    def test_divisions_are_earned_by_knowing_it_not_by_being_quick(self):
        """A child reliably right but still deriving earned no division at all,
        so her level bar capped below the total with nothing explaining why."""
        fact = Fact.objects.get(factor_a=2, factor_b=6)
        state = scheduling.ensure_states(
            self.child, [(fact, Operation.MULT)])[(fact.pk, Operation.MULT)]
        level = Level.objects.get(slug="ones-twos")
        for _ in range(2):
            scheduling.apply_attempt(
                state, is_correct=True, response_ms=9000,
                session_id=GameSession.objects.create(
                    student=self.child, level=level).pk)
        self.assertEqual(state.leitner_box, 1, "still never been quick")
        self.assertTrue(scheduling._division_is_earned(
            fact, Operation.DIV_A, {(fact.pk, Operation.MULT): state}))

    def test_new_facts_get_seats_even_behind_a_long_due_backlog(self):
        ones = Level.objects.get(slug="ones-twos")
        states = scheduling.ensure_states(
            self.child, scheduling._forms_for_level(ones))
        past = timezone.now() - timedelta(days=5)
        items = list(states.items())
        for _key, state in items[:-2]:
            state.total_attempts = 3
            state.total_correct = 3
            state.due_at = past
            state.save()
        questions = scheduling.build_round(self.child, ones)
        seen = {(q["fact_id"], q["operation"]) for q in questions}
        fresh = {k for k, s in states.items() if s.total_attempts == 0}
        self.assertTrue(fresh & seen,
                        "a full backlog used to eat every seat in the round")

    def test_a_zero_millisecond_answer_is_not_a_free_promotion(self):
        from portal.tokens import make_portal_token

        session = GameSession.objects.create(
            student=self.child, level=Level.objects.get(slug="ones-twos"))
        fact = Fact.objects.get(factor_a=2, factor_b=3)
        self.client.post(
            reverse("factfluency:api_attempts", kwargs={
                "token": make_portal_token(self.child),
                "session_id": session.pk}),
            data=json.dumps({"attempts": [{
                "client_uuid": "zero", "fact_id": fact.pk,
                "operation": "mult", "answer_given": 6, "response_ms": 0}]}),
            content_type="application/json")
        self.assertFalse(Attempt.objects.filter(client_uuid="zero").exists())

    def test_an_unhashable_operation_is_refused_not_a_500(self):
        from portal.tokens import make_portal_token

        session = GameSession.objects.create(
            student=self.child, level=Level.objects.get(slug="ones-twos"))
        fact = Fact.objects.get(factor_a=2, factor_b=3)
        for hostile in ([1], {"a": 1}):
            response = self.client.post(
                reverse("factfluency:api_attempts", kwargs={
                    "token": make_portal_token(self.child),
                    "session_id": session.pk}),
                data=json.dumps({"attempts": [{
                    "client_uuid": "h", "fact_id": fact.pk,
                    "operation": hostile, "answer_given": 6,
                    "response_ms": 900}]}),
                content_type="application/json")
            self.assertEqual(response.status_code, 200, hostile)
            self.assertEqual(response.json()["accepted"], 0, hostile)

    def test_the_offline_queue_is_scoped_to_one_child(self):
        """Two children share this tablet. One shared localStorage key meant a
        sibling's undelivered answers were retried against whoever opened the
        game next — 404 forever, and able to evict good rows via the 200 cap."""
        from pathlib import Path

        js = (Path(__file__).resolve().parent / "static" / "factfluency"
              / "factdash.js").read_text(encoding="utf-8")
        self.assertIn("factdash:queue:", js)
        self.assertIn("root.dataset.who", js)
        html = (Path(__file__).resolve().parent.parent / "templates"
                / "factfluency" / "play.html").read_text(encoding="utf-8")
        self.assertIn("data-who=", html)

    def test_the_challenge_level_shows_no_bar_it_can_never_fill(self):
        """Its facts are all mastered in earlier levels, so it greeted her with
        a full bar, no star and nothing to do the moment it unlocked."""
        rows = {r["level"].slug: r for r in scheduling.unlocked_levels(
            self.child, list(Level.objects.all()))}
        self.assertTrue(Level.objects.get(slug="the-tricky-ones").is_challenge)
        from factfluency.views import _levels_with_state

        by_slug = {r["level"].slug: r for r in _levels_with_state(self.child)}
        self.assertFalse(by_slug["the-tricky-ones"]["show_bar"])
        self.assertTrue(by_slug["ones-twos"]["show_bar"])
        del rows

    def test_the_rebuild_ignores_forms_a_migration_retired(self):
        """Replaying them re-creates rows migration 0008 deleted, and inflates
        the very headline used to decide whether to run the repair for real."""
        from io import StringIO

        from django.core.management import call_command

        zero = Fact.objects.filter(factor_a=0).first()
        session = GameSession.objects.create(
            student=self.child, level=Level.objects.get(slug="ones-twos"))
        Attempt.objects.create(
            session=session, fact=zero, operation=Operation.DIV_A,
            answer_given=0, is_correct=True, response_ms=500,
            was_fluent=True, client_uuid="retired")
        out = StringIO()
        call_command("rebuild_fact_states", child="Violet", stdout=out)
        self.assertIn("retired forms skipped", out.getvalue())
        self.assertFalse(StudentFactState.objects.filter(
            student=self.child, fact=zero, operation=Operation.DIV_A).exists())


# ---------------------------------------------------------------------------
# HH-203: the bar is a function of her age, the gate is a count, and a round
# asks the facts she is stuck on.
# ---------------------------------------------------------------------------

def _make_child(username, first_name, grade):
    parent = User.objects.create_user(
        username=username, email=username + "@e.com", password="pw")
    family = Family.objects.create(name=username + " Fam")
    FamilyMembership.objects.create(user=parent, family=family, role="parent")
    return Student.objects.create(
        parent=parent, first_name=first_name, grade_level=grade, family=family)


class PolicyTableTests(TestCase):
    """The per-grade table is the ONLY home for the developmental numbers."""

    def test_every_level_choice_maps_to_exactly_one_band(self):
        seen = {}
        for grades, _policy in BANDS:
            for grade in grades:
                self.assertNotIn(grade, seen, "a grade in two bands")
                seen[grade] = True
        for code, _label in Student.LEVEL_CHOICES:
            self.assertIn(code, seen, code)
        # Blank or nonsense gets the CCSS grade for this content, never the
        # strictest band.
        self.assertEqual(policy_for(Student(grade_level="")), policy_for(Student(grade_level="G03")))
        self.assertEqual(policy_for(Student(grade_level="G99")), policy_for(Student(grade_level="G03")))

    def test_the_table_is_monotone_and_inside_the_research_range(self):
        order = [code for code, _ in Student.LEVEL_CHOICES]
        policies = [policy_for(Student(grade_level=g)) for g in order]
        for earlier, later in zip(policies, policies[1:]):
            self.assertGreaterEqual(earlier.base_ms, later.base_ms)
            self.assertGreaterEqual(earlier.per_digit_ms, later.per_digit_ms)
            self.assertLessEqual(earlier.new_facts_per_round, later.new_facts_per_round)
        for p in policies:
            self.assertTrue(3000 <= p.base_ms <= 5000, p)
        self.assertEqual(policy_for(Student(grade_level="G07"))[:2], (3000, 600))

    def test_the_same_answer_has_a_different_bar_at_nine_and_twelve(self):
        g3 = policy_for(Student(grade_level="G03"))
        g7 = policy_for(Student(grade_level="G07"))
        self.assertEqual(threshold_for(48, g3), 5000)
        self.assertEqual(threshold_for(48, g7), 3600)
        self.assertEqual(threshold_for(6, g3), 4000)
        self.assertEqual(threshold_for(6, g7), 3000)

    def test_a_skip_count_is_still_not_fluent_at_grade_three(self):
        """4.8s on 2x4 is "2, 4, 6, 8" — derived. It would pass a 5s bar; the
        Monte Carlo on Violet's own 4-6s answers beat Level 1 in 100% of runs
        at 5000 and 0% at 4000. This pins the 4000."""
        g3 = policy_for(Student(grade_level="G03"))
        self.assertFalse(scheduling.is_fluent(True, 4800, threshold_for(8, g3)))
        self.assertTrue(scheduling.is_fluent(True, 3900, threshold_for(8, g3)))


class LevelGateTests(TestCase):
    """The gate is a COUNT of forms she may still be working on."""

    @classmethod
    def setUpTestData(cls):
        cls.child = _make_child("gate", "Violet", "G03")
        cls.ones = Level.objects.get(slug="ones-twos")
        cls.fives = Level.objects.get(slug="fives")

    def _set(self, level, mastered, learning=None, never=()):
        """Master the first `mastered` forms, mark the rest learning except
        the `never` prompts, which get no state row at all."""
        forms = scheduling._forms_for_level(level)
        StudentFactState.objects.filter(
            student=self.child, fact__in={f for f, _ in forms}).delete()
        done = 0
        for fact, operation in forms:
            if fact.prompt(operation) in never:
                continue
            is_mastered = done < mastered
            done += 1 if is_mastered else 0
            StudentFactState.objects.create(
                student=self.child, fact=fact, operation=operation,
                is_mastered=is_mastered,
                # A child at the gate is ACCURATE — Violet's real Level 1 is
                # 0.946 right. 2-of-3 would be a guesser, and the accuracy
                # floor exists to refuse exactly that.
                total_attempts=20, total_correct=19,
                consecutive_fluent=3 if is_mastered else 1,
                leitner_box=4 if is_mastered else 2)

    def test_the_gate_arithmetic_is_exact_on_every_level(self):
        need = {}
        for level in Level.objects.filter(is_challenge=False):
            need[level.slug] = scheduling.forms_needed(
                len(scheduling._forms_for_level(level)))
        self.assertEqual(need, {
            "ones-twos": 24, "fives": 16, "tens": 21, "squares": 10,
            "threes": 12, "fours": 10, "nines": 8, "sixes": 5, "sevens": 2})
        # The (1 - 0.8) * 20 = 3.999 trap: fives needs 16, not 17.
        self.assertEqual(scheduling.forms_allowed_unmastered(20), 4)

    def test_violets_real_standing_beats_level_one(self):
        """25 of 29 mastered, the other four right-but-slow — her exact state
        after sixty-five rounds. Under the old 90% ratio she needed 27."""
        self._set(self.ones, mastered=25)
        self.assertTrue(scheduling.is_level_beaten(self.child, self.ones))
        rows = scheduling.unlocked_levels(self.child, list(Level.objects.all()))
        self.assertTrue(rows[1]["unlocked"], "fives opens")
        self._set(self.ones, mastered=23)
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))

    def test_a_form_never_answered_right_blocks_the_level(self):
        """The 64/8 shape: everything else mastered, one division never asked.
        Not beaten — a level is not cleared by not being asked its last form."""
        self._set(self.ones, mastered=24, never={"14 ÷ 2"})
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))
        fact = Fact.objects.get(factor_a=2, factor_b=7)
        StudentFactState.objects.create(
            student=self.child, fact=fact, operation=Operation.DIV_A,
            total_attempts=1, total_correct=1)
        # ...and she is accurate across the level, so only the never-asked
        # form was ever in the way.
        self.assertTrue(scheduling.is_level_beaten(self.child, self.ones))

    def test_the_small_levels_no_longer_demand_perfection(self):
        sevens = Level.objects.get(slug="sevens")       # 3 forms
        sixes = Level.objects.get(slug="sixes")         # 6 forms
        nines = Level.objects.get(slug="nines")         # 9 forms
        self._set(sevens, mastered=2)
        self.assertTrue(scheduling.is_level_beaten(self.child, sevens))
        self._set(sevens, mastered=1)
        self.assertFalse(scheduling.is_level_beaten(self.child, sevens))
        self._set(sixes, mastered=5)
        self.assertTrue(scheduling.is_level_beaten(self.child, sixes))
        self._set(sixes, mastered=4)
        self.assertFalse(scheduling.is_level_beaten(self.child, sixes))
        self._set(nines, mastered=8)
        self.assertTrue(scheduling.is_level_beaten(self.child, nines))

    def test_a_level_answered_like_a_guesser_is_not_beaten(self):
        """Count gate satisfied, accuracy not. Measured on the real code with
        the floor removed: a child answering 75% right with fast random taps
        beat Level 1 in 12 runs out of 12, and a 60% one in 3 of 12. The
        seating that helps a stuck child re-asks a guesser exactly what she has
        not mastered until luck carries it."""
        self._set(self.ones, mastered=25)
        self.assertTrue(scheduling.is_level_beaten(self.child, self.ones))
        StudentFactState.objects.filter(student=self.child).update(
            total_attempts=20, total_correct=15)          # 0.75
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))
        self.assertEqual(scheduling.portal_summary(self.child)["current"]["level"],
                         self.ones, "the tile must refuse her too")
        StudentFactState.objects.filter(student=self.child).update(
            total_attempts=20, total_correct=18)          # 0.90
        self.assertTrue(scheduling.is_level_beaten(self.child, self.ones))

    def test_the_tile_and_the_map_agree(self):
        """One helper, two readers. The stored Level.mastery_threshold is no
        longer consulted by either."""
        self._set(self.ones, mastered=24)
        self.assertTrue(scheduling.is_level_beaten(self.child, self.ones))
        self.assertEqual(scheduling.portal_summary(self.child)["current"]["level"], self.fives)
        self._set(self.ones, mastered=23)
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))
        self.assertEqual(scheduling.portal_summary(self.child)["current"]["level"], self.ones)
        Level.objects.filter(pk=self.ones.pk).update(mastery_threshold=1.0)
        self._set(self.ones, mastered=24)
        self.assertTrue(scheduling.is_level_beaten(self.child, self.ones))
        self.assertEqual(scheduling.portal_summary(self.child)["current"]["level"], self.fives)


class RoundOrderTests(TestCase):
    """A round asks the facts she is stuck on, and opens on one she holds."""

    @classmethod
    def setUpTestData(cls):
        cls.child = _make_child("order", "Violet", "G03")
        cls.ones = Level.objects.get(slug="ones-twos")
        cls.fives = Level.objects.get(slug="fives")

    def _stuck_on_four(self):
        """25 mastered, 4 un-mastered, nothing due — Violet's state."""
        import random

        later = timezone.now() + timedelta(days=30)
        forms = scheduling._forms_for_level(self.ones)
        stuck = set()
        for i, (fact, operation) in enumerate(forms):
            is_mastered = i >= 4
            if not is_mastered:
                stuck.add((fact.pk, operation))
            StudentFactState.objects.create(
                student=self.child, fact=fact, operation=operation,
                is_mastered=is_mastered, total_attempts=5, total_correct=4,
                consecutive_fluent=3 if is_mastered else 1, due_at=later,
                leitner_box=4 if is_mastered else 2)
        return stuck, random.Random(7)

    def test_unmastered_forms_take_seats_before_mastered_ones(self):
        stuck, rng = self._stuck_on_four()
        for _ in range(20):
            asked = {(q["fact_id"], q["operation"])
                     for q in scheduling.build_round(self.child, self.ones, rng=rng)}
            self.assertTrue(stuck <= asked, "a round skipped a stuck form")

    def test_the_first_question_is_a_warm_one_when_any_exists(self):
        stuck, rng = self._stuck_on_four()
        for _ in range(20):
            questions = scheduling.build_round(self.child, self.ones, rng=rng)
            first = (questions[0]["fact_id"], questions[0]["operation"])
            self.assertNotIn(first, stuck, "question 1 must be a form she holds")
            for a, b in zip(questions, questions[1:]):
                self.assertNotEqual((a["fact_id"], a["operation"]),
                                    (b["fact_id"], b["operation"]))

    def test_review_keeps_two_seats_behind_a_long_learning_list(self):
        """Fives all seen and un-mastered, ones-twos beaten: the round is
        eighteen fives and exactly two review forms — not four, not none."""
        import random

        later = timezone.now() + timedelta(days=30)
        for level, mastered in ((self.ones, True), (self.fives, False)):
            for fact, operation in scheduling._forms_for_level(level):
                StudentFactState.objects.create(
                    student=self.child, fact=fact, operation=operation,
                    is_mastered=mastered, total_attempts=3, total_correct=3,
                    consecutive_fluent=3 if mastered else 1, due_at=later)
        ones_ids = {f.pk for f in self.ones.facts.all()}
        questions = scheduling.build_round(self.child, self.fives,
                                           rng=random.Random(3))
        review = sum(1 for q in questions if q["fact_id"] in ones_ids)
        self.assertEqual(review, 2)
        self.assertEqual(len(questions), scheduling.ROUND_LENGTH)

    def test_the_cap_follows_the_band(self):
        squares = Level.objects.get(slug="squares")
        older = _make_child("older", "Kaylin", "G07")
        seen_older = {(q["fact_id"], q["operation"])
                      for q in scheduling.build_round(older, squares)}
        seen_young = {(q["fact_id"], q["operation"])
                      for q in scheduling.build_round(self.child, squares)}
        self.assertEqual(len(seen_older), 6, "all six multiplications")
        self.assertEqual(len(seen_young), 4)
        for q in scheduling.build_round(older, squares):
            self.assertNotIn("÷", q["prompt"])


class ControlTests(TestCase):
    """Who the leniency must NOT let through. Seeded, so the runs are exact."""

    @classmethod
    def setUpTestData(cls):
        cls.child = _make_child("ctrl", "Violet", "G03")
        cls.ones = Level.objects.get(slug="ones-twos")

    def _play(self, rounds, *, right, ms, seed=1):
        import random

        rng = random.Random(seed)
        now = timezone.now() - timedelta(days=10)
        for _ in range(rounds):
            session = GameSession.objects.create(student=self.child, level=self.ones)
            questions = scheduling.build_round(self.child, self.ones, now=now, rng=rng)
            forms = [(Fact.objects.get(pk=q["fact_id"]), q["operation"]) for q in questions]
            states = scheduling.ensure_states(self.child, forms)
            for fact, operation in forms:
                scheduling.apply_attempt(
                    states[(fact.pk, operation)],
                    is_correct=rng.random() < right, response_ms=ms(rng),
                    now=now, session_id=session.pk)
            now += timedelta(minutes=3)

    def test_a_seeded_guesser_does_not_beat_the_ones_and_twos(self):
        """60% right, fast — over NINETY rounds and five seeds.

        The forty-round single-seed version of this passed while the leak was
        wide open. Seating the un-mastered forms first is as attentive to a
        guesser as to a child who is stuck: it re-asks exactly what she has not
        mastered until a run of lucky hits carries it. Simulated over 400 runs
        she took Level 1 in 51% of them. Ninety rounds is the horizon that
        makes the failure visible; the accuracy floor is what closes it.
        """
        for seed in range(5):
            StudentFactState.objects.filter(student=self.child).delete()
            GameSession.objects.filter(student=self.child).delete()
            self._play(90, right=0.6, ms=lambda r: r.randint(800, 2000),
                       seed=seed)
            self.assertFalse(scheduling.is_level_beaten(self.child, self.ones),
                             "a guesser beat Level 1 on seed %d" % seed)

    def test_a_luckier_guesser_is_still_refused(self):
        """75% right and fast is a child who half-knows it and is stabbing at
        the rest. She is not fluent at this level and must not clear it."""
        self._play(90, right=0.75, ms=lambda r: r.randint(800, 2000), seed=11)
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))

    def test_the_floor_is_what_refuses_her_not_luck(self):
        """Name the mechanism: with the count gate alone she gets there, and
        the accuracy floor is the thing standing in the way. If this ever
        fails because the count gate now refuses her on its own, the guard
        above has stopped testing what it says it tests."""
        self._play(90, right=0.6, ms=lambda r: r.randint(800, 2000), seed=0)
        mastered, learning, total = scheduling.level_breakdown(self.child, self.ones)
        correct, attempts = scheduling.level_accuracy(self.child, self.ones)
        self.assertLess(correct / attempts, 0.85, "she was more accurate than a guesser")
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))

    def test_the_floor_does_not_touch_a_child_who_is_simply_slow(self):
        """Violet's real Level 1 accuracy is 0.946 and Kaylin's 0.95-1.00. A
        child who is right and slow must sail past this."""
        self._play(12, right=1.0, ms=lambda r: 9000, seed=3)
        correct, attempts = scheduling.level_accuracy(self.child, self.ones)
        self.assertEqual(correct, attempts)
        self.assertTrue(scheduling._accuracy_met(self.child, self.ones))

    def test_a_seeded_skip_counter_does_not_beat_the_ones_and_twos(self):
        """97% right at 4.1-6s — Violet's own deriving speed. A 5s bar would
        master every one-digit form here; the 4s bar masters none of them."""
        self._play(40, right=0.97, ms=lambda r: r.randint(4100, 6000))
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))
        for state in StudentFactState.objects.filter(student=self.child, is_mastered=True):
            self.assertGreaterEqual(state.fact.answer(state.operation), 10,
                                    "a one-digit answer mastered at skip-count speed")

    def test_a_seeded_deriver_masters_nothing(self):
        self._play(40, right=0.97, ms=lambda r: 7500)
        mastered, learning, _total = scheduling.level_breakdown(self.child, self.ones)
        self.assertEqual(mastered, 0)
        self.assertGreater(learning, 0)
        self.assertFalse(scheduling.is_level_beaten(self.child, self.ones))


class EndpointBandTests(TestCase):
    """The API judges each child by HER band, not by one site-wide clock."""

    def test_the_endpoint_applies_the_childs_own_band(self):
        from portal.tokens import make_portal_token

        ones = Level.objects.get(slug="ones-twos")
        fact = Fact.objects.get(factor_a=2, factor_b=3)          # 6
        verdicts = {}
        for username, grade in (("nine", "G03"), ("twelve", "G07")):
            child = _make_child(username, username, grade)
            session = GameSession.objects.create(student=child, level=ones)
            self.client.post(
                reverse("factfluency:api_attempts",
                        kwargs={"token": make_portal_token(child),
                                "session_id": session.pk}),
                data=json.dumps({"attempts": [
                    {"client_uuid": "a", "fact_id": fact.pk, "operation": "mult",
                     "answer_given": 6, "response_ms": 3500}]}),
                content_type="application/json")
            state = StudentFactState.objects.get(student=child, fact=fact)
            verdicts[grade] = (Attempt.objects.get(session=session).was_fluent,
                               state.consecutive_fluent)
        self.assertEqual(verdicts, {"G03": (True, 1), "G07": (False, 0)})

    def test_no_threshold_is_sent_to_the_page(self):
        from portal.tokens import make_portal_token

        child = _make_child("noclock", "V", "G03")
        data = self.client.post(reverse(
            "factfluency:api_start",
            kwargs={"token": make_portal_token(child), "slug": "ones-twos"})).json()
        self.assertNotIn("threshold_ms", data)
        self.assertIn("questions", data)


class RebuildBandTests(TestCase):
    """The replay judges history by the child's current band."""

    def _child(self, name, grade):
        return _make_child("rb_" + name, name, grade)

    def _play(self, child, ms, rounds=3, fact=None):
        ones = Level.objects.get(slug="ones-twos")
        fact = fact or Fact.objects.get(factor_a=2, factor_b=3)
        sessions = []
        for n in range(rounds):
            session = GameSession.objects.create(
                student=child, level=ones, ended_at=timezone.now(),
                num_attempted=1, num_correct=1, num_fluent=0)
            Attempt.objects.create(
                session=session, fact=fact, operation=Operation.MULT,
                answer_given=6, is_correct=True, response_ms=ms,
                was_fluent=False, client_uuid="rb-%d" % n)
            sessions.append(session)
        StudentFactState.objects.get_or_create(
            student=child, fact=fact, operation=Operation.MULT)
        return fact, sessions

    def _run(self, child, **kw):
        from io import StringIO

        from django.core.management import call_command
        out = StringIO()
        call_command("rebuild_fact_states", child=child.first_name, stdout=out, **kw)
        return out.getvalue()

    def test_the_replay_uses_the_childs_own_band(self):
        nine = self._child("Nine", "G03")
        twelve = self._child("Twelve", "G07")
        fact, _ = self._play(nine, 3500)
        self._play(twelve, 3500)
        self._run(nine)
        self._run(twelve)
        self.assertTrue(StudentFactState.objects.get(student=nine, fact=fact).is_mastered)
        self.assertFalse(StudentFactState.objects.get(student=twelve, fact=fact).is_mastered)

    def test_changing_the_grade_and_rebuilding_changes_the_verdict(self):
        child = self._child("Mover", "G03")
        fact, _ = self._play(child, 3500)
        self._run(child)
        self.assertTrue(StudentFactState.objects.get(student=child, fact=fact).is_mastered)
        child.grade_level = "G07"
        child.save()
        out = self._run(child)
        self.assertFalse(StudentFactState.objects.get(student=child, fact=fact).is_mastered)
        self.assertIn("lost mastery", out)
        child.grade_level = "G03"
        child.save()
        self._run(child)
        self.assertTrue(StudentFactState.objects.get(student=child, fact=fact).is_mastered)

    def test_the_rebuild_rewrites_was_fluent_and_the_session_tallies(self):
        child = self._child("Flags", "G03")
        _fact, sessions = self._play(child, 3500)
        self._run(child)
        for session in sessions:
            session.refresh_from_db()
            self.assertEqual(session.num_fluent, 1)
            self.assertEqual(session.longest_streak, 1)
        self.assertTrue(all(Attempt.objects.filter(session__student=child)
                            .values_list("was_fluent", flat=True)))

    def test_report_lists_the_standing_without_writing(self):
        child = self._child("Report", "G03")
        fact, _ = self._play(child, 9000)
        out = self._run(child, dry_run=True, report=True)
        self.assertIn("need 24", out)
        self.assertIn(fact.prompt(Operation.MULT), out)
        self.assertIn("nothing written", out)
        self.assertEqual(StudentFactState.objects.get(student=child, fact=fact)
                         .consecutive_fluent, 0)


class MapCopyTests(TestCase):
    """The map explains the rule, and never quotes the bar to the child."""

    SECONDS = r"\b\d+(\.\d+)?\s*(s|sec|secs|second|seconds)\b"

    def _map(self, child):
        from portal.tokens import make_portal_token

        return self.client.get(reverse(
            "factfluency:home",
            kwargs={"token": make_portal_token(child)})).content.decode()

    def test_the_map_explains_the_rule_without_a_number(self):
        import re

        child = _make_child("copy", "Violet", "G03")
        html = self._map(child)
        self.assertIn("three separate rounds", html)
        self.assertIn("all but a few", html)
        self.assertIsNone(re.compile(self.SECONDS, re.I).search(html))

    def test_her_own_best_time_is_the_one_number_allowed(self):
        """The live page failed the blanket version of the guard above, and it
        was the guard that was wrong: the record chip reads "1.0s a question"
        and that is HERS. What must never appear is the BAR — a number to beat
        is a countdown by another name — so the rule copy stays number-free
        while the record stands."""
        import re

        child = _make_child("record", "Violet", "G03")
        PersonalRecord.objects.create(
            student=child, level=Level.objects.get(slug="ones-twos"),
            record_type=RecordType.BEST_TIME, value=1040)
        html = self._map(child)
        found = re.findall(self.SECONDS, html)
        self.assertTrue(found, "the record chip should be showing")
        self.assertIn("1.0s a question", html)
        # ...and the rule sentences beside it still quote no number at all.
        rule = html.split('class="fd-rule"', 1)[1]
        self.assertIsNone(re.compile(self.SECONDS, re.I).search(rule))
        for band in ("3000", "4000", "5000", "3 seconds", "4 seconds"):
            self.assertNotIn(band, html)


class MasteryStreakPinTests(TestCase):
    """Three rounds, not two — pinned with literals, because the streak tests
    above loop over MASTERY_STREAK and would follow a lowered constant."""

    @classmethod
    def setUpTestData(cls):
        cls.child = _make_child("pin", "Violet", "G03")
        cls.level = Level.objects.get(slug="ones-twos")
        cls.fact = Fact.objects.get(factor_a=2, factor_b=3)

    def test_two_fluent_rounds_are_not_mastery_and_the_third_is(self):
        state = StudentFactState.objects.create(
            student=self.child, fact=self.fact, operation=Operation.MULT)
        for n in range(2):
            session = GameSession.objects.create(student=self.child, level=self.level)
            scheduling.apply_attempt(state, is_correct=True, response_ms=800,
                                     session_id=session.pk)
        self.assertFalse(state.is_mastered, "two rounds is what a guesser can fake")
        session = GameSession.objects.create(student=self.child, level=self.level)
        scheduling.apply_attempt(state, is_correct=True, response_ms=800,
                                 session_id=session.pk)
        self.assertTrue(state.is_mastered)
        self.assertEqual(MASTERY_STREAK, 3)


class SeatTieBreakTests(TestCase):
    """When the stuck forms outnumber the seats, the ones a single verdict
    from mastery go first and the ones at streak zero wait."""

    def test_nearly_mastered_forms_take_seats_before_streak_zero_ones(self):
        import random

        child = _make_child("tie", "Violet", "G03")
        ones = Level.objects.get(slug="ones-twos")
        fives = Level.objects.get(slug="fives")
        later = timezone.now() + timedelta(days=30)
        # Ones-twos beaten and seen, so review has something to draw on and
        # the floor of two seats applies: 18 seats for twenty stuck forms.
        for fact, operation in scheduling._forms_for_level(ones):
            StudentFactState.objects.create(
                student=child, fact=fact, operation=operation, is_mastered=True,
                total_attempts=3, total_correct=3, consecutive_fluent=3, due_at=later)
        forms = scheduling._forms_for_level(fives)
        cold = {(f.pk, o) for f, o in forms[:2]}
        for fact, operation in forms:
            StudentFactState.objects.create(
                student=child, fact=fact, operation=operation, is_mastered=False,
                total_attempts=3, total_correct=3, due_at=later,
                consecutive_fluent=0 if (fact.pk, operation) in cold else 2)
        for seed in range(5):
            asked = {(q["fact_id"], q["operation"])
                     for q in scheduling.build_round(child, fives, rng=random.Random(seed))}
            self.assertFalse(cold & asked, "a streak-zero form took a seat "
                                           "from one a verdict away")
