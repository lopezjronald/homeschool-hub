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
    FLUENCY_THRESHOLD_MS, MASTERY_STREAK, Attempt, Fact, GameSession, Level,
    Operation, PersonalRecord, RecordType, StudentFactState,
)
from . import scheduling


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
        zero = Fact.objects.get(factor_a=0, factor_b=5)
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
        self.assertTrue(scheduling.is_fluent(True, FLUENCY_THRESHOLD_MS - 1))

    def test_right_but_slow_is_not_fluent(self):
        self.assertFalse(scheduling.is_fluent(True, FLUENCY_THRESHOLD_MS + 1))

    def test_fast_but_wrong_is_not_fluent(self):
        self.assertFalse(scheduling.is_fluent(False, 200))

    def test_a_fluent_answer_promotes_a_box_and_pushes_the_review_out(self):
        state = self._state()
        before = state.due_at
        scheduling.apply_attempt(state, is_correct=True, response_ms=900)
        self.assertEqual(state.leitner_box, 2)
        self.assertEqual(state.consecutive_fluent, 1)
        self.assertGreater(state.due_at, before)

    def test_right_but_slow_HOLDS_the_box(self):
        """The rule the whole design rests on. A correct answer after five
        seconds was derived, not recalled — promoting it would push a slow fact
        out to a long interval and quietly stop practising it."""
        state = self._state()
        scheduling.apply_attempt(state, is_correct=True, response_ms=900)
        self.assertEqual(state.leitner_box, 2)
        scheduling.apply_attempt(state, is_correct=True, response_ms=5000)
        self.assertEqual(state.leitner_box, 2, "a slow answer must not promote")
        self.assertEqual(state.consecutive_fluent, 0, "and it breaks the streak")

    def test_a_slow_answer_brings_the_fact_back_soon(self):
        state = self._state()
        scheduling.apply_attempt(state, is_correct=True, response_ms=5000)
        self.assertLess(state.due_at, timezone.now() + timedelta(hours=1))

    def test_a_wrong_answer_drops_to_box_one_and_is_due_at_once(self):
        state = self._state()
        for _ in range(3):
            scheduling.apply_attempt(state, is_correct=True, response_ms=800)
        self.assertGreater(state.leitner_box, 1)
        scheduling.apply_attempt(state, is_correct=False, response_ms=800)
        self.assertEqual(state.leitner_box, 1)
        self.assertFalse(state.is_mastered)
        self.assertLessEqual(state.due_at, timezone.now())

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
        from .models import NEW_FACTS_PER_ROUND

        questions = scheduling.build_round(self.child, self.fives)
        self.assertTrue(questions)
        distinct = {(q["fact_id"], q["operation"]) for q in questions}
        self.assertLessEqual(len(distinct), NEW_FACTS_PER_ROUND)

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
        zero = Fact.objects.get(factor_a=0, factor_b=5)
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
        from .models import NEW_FACTS_PER_ROUND

        questions = scheduling.build_round(
            self.child, Level.objects.get(slug="fives"))
        distinct = {(q["fact_id"], q["operation"]) for q in questions}
        self.assertLessEqual(len(distinct), NEW_FACTS_PER_ROUND)

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
        html = self._home(self.mathy)
        self.assertIn("Fact Dash", html)
        self.assertIn(reverse("factfluency:home", args=[make_portal_token(self.mathy)]),
                      html)

    def test_a_child_with_no_maths_does_not(self):
        """A times-tables game on the portal of a child who does no maths here
        is clutter, the same reason spelling only shows on a placement."""
        self.assertNotIn("Fact Dash", self._home(self.readery))

    def test_the_tile_names_the_level_she_is_on(self):
        html = self._home(self.mathy)
        self.assertIn("Ones &amp; Twos", html)
        self.assertIn("facts nailed", html)

    def test_the_tile_advances_when_she_beats_a_level(self):
        ones = Level.objects.get(slug="ones-twos")
        for state in scheduling.ensure_states(
                self.mathy, scheduling._forms_for_level(ones)).values():
            state.is_mastered = True
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
                                 is_correct=True, response_ms=5000, session_id=1)
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
