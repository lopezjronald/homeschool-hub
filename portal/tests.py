import json
from datetime import date
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Family, FamilyMembership
from curricula.models import Chapter, Curriculum, CurriculumPlacement, CurriculumResource, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.models import AnswerPhoto, Question, QuestionSet, ResponseSheet
from worklog.models import WorkLogEntry

from .tokens import make_portal_token, student_from_token

User = get_user_model()


class PortalTokenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="pp", email="pp@e.com", password="pw")
        cls.family = Family.objects.create(name="Portal Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.kid = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )

    def test_round_trip(self):
        token = make_portal_token(self.kid)
        self.assertEqual(student_from_token(token), self.kid)

    def test_bad_token_returns_none_and_404(self):
        self.assertIsNone(student_from_token("garbage"))
        resp = self.client.get(reverse("portal:portal_home", kwargs={"token": "garbage"}))
        self.assertEqual(resp.status_code, 404)

    def test_rotating_key_revokes_link(self):
        from students.models import _new_portal_key

        token = make_portal_token(self.kid)
        self.assertEqual(student_from_token(token), self.kid)
        self.kid.portal_key = _new_portal_key()
        self.kid.save(update_fields=["portal_key"])
        # old token no longer resolves; a fresh one does
        self.assertIsNone(student_from_token(token))
        self.assertEqual(student_from_token(make_portal_token(self.kid)), self.kid)


class PortalCourseTests(TestCase):
    """The full Kaylin flow: seeded course -> portal -> autosave -> submit."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="dad", email="dad@e.com", password="pw")
        cls.family = Family.objects.create(name="Course Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        call_command("seed_i_am_david", "--for-user", "dad", stdout=StringIO())
        cls.token = make_portal_token(cls.kaylin)
        cls.first_set = QuestionSet.objects.order_by("pk").first()
        # The Journal's Q1 is now a per-character question; text-answer flow
        # tests target a plain typed question instead.
        cls.first_text_q = cls.first_set.questions.filter(
            response_type=Question.TYPE_TEXT,
        ).order_by("order").first()

    def _url(self, name, **kwargs):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kwargs})

    def test_seed_created_full_course(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        self.assertEqual(curriculum.grade_level, "G07")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        # 6/section x 4 + Glean + the hands-on Glean + seminar + toolbox
        self.assertEqual(sets.count(), 28)
        gleans = sets.filter(title__contains="Glean")
        self.assertEqual(gleans.count(), 2)
        self.assertTrue(gleans.filter(title__endswith="Final Project").exists(),
                        "the guide's own options must still be offered")
        self.assertEqual(
            Question.objects.filter(question_set__in=sets).count(), 239,
        )
        # Acquire keeps the Level 7 guide's own format (look it up and write it),
        # with the official Blackbird definitions attached as a TEACHER key.
        vocab = sets.get(title="Section 1 · Vocabulary")
        vq = vocab.questions.order_by("order").first()
        self.assertEqual(vq.response_type, Question.TYPE_TEXT)
        self.assertIn("Define:", vq.prompt)
        self.assertIn("Official Blackbird definitions", vocab.answer_key)
        self.assertIn("catastrophe —", vocab.answer_key)
        # comprehension sets carry the answer key (grader reference, never shown)
        self.assertTrue(sets.filter(title__contains="Comprehension").exclude(answer_key="").exists())
        # the reusable literature standard sets exist (teacher-led)
        self.assertTrue(
            sets.filter(title__contains="Story-Grammar", mode=QuestionSet.MODE_DISCUSSION).exists()
        )
        self.assertTrue(
            sets.filter(title__contains="Literary Toolbox", mode=QuestionSet.MODE_DISCUSSION).exists()
        )
        # Socratic sets exist per section with story-grammar categories
        socratic = sets.filter(title__contains="Socratic")
        self.assertEqual(socratic.count(), 4)
        cats = set(
            Question.objects.filter(question_set__in=socratic).values_list("category", flat=True)
        )
        for expected in ("setting", "character", "conflict", "plot", "theme"):
            self.assertIn(expected, cats)
        # Kaylin is placed
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.kaylin, curriculum=curriculum).exists()
        )

    def test_seed_is_idempotent(self):
        call_command("seed_i_am_david", "--for-user", "dad", stdout=StringIO())
        self.assertEqual(QuestionSet.objects.count(), 28)
        self.assertEqual(Question.objects.count(), 239)

    def test_portal_home_shows_one_calm_subject_card(self):
        # The "What's Next" home shows a subject CARD (curriculum name), not the
        # old wall of 27 set titles / section headings — those move to the drill-in.
        resp = self.client.get(self._url("portal_home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Kaylin")
        self.assertContains(resp, "I Am David")                 # the subject card
        self.assertContains(resp, "portal-subject-card")
        self.assertNotContains(resp, "Section 1: Chapters 1–2")  # no chapter dump on home
        self.assertNotContains(resp, "Comprehension")            # no set titles on home

    def test_portal_subject_drilldown_groups_by_chapter(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        resp = self.client.get(self._url("portal_subject", curriculum_id=curriculum.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Section 1: Chapters 1–2")     # chapter heading here
        self.assertContains(resp, "Comprehension")               # set titles here
        # the current chapter is expanded on load
        self.assertContains(resp, 'class="collapse show"')
        # and a big Continue points at the next unstarted set
        self.assertContains(resp, "Continue")

    def test_seeded_journal_uses_per_character_boxes(self):
        from tutor.models import Question

        journal = QuestionSet.objects.filter(title__endswith="Journal").first()
        char_q = journal.questions.get(order=1)
        self.assertEqual(char_q.response_type, Question.TYPE_CHARACTERS)
        self.assertIn("David", char_q.character_names)          # names live in passage now
        self.assertGreaterEqual(len(char_q.character_names), 2)  # a box per character
        self.assertNotIn("·", char_q.prompt)                    # names no longer crammed in the prompt

    def test_portal_subject_rejects_sibling(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        violet_token = make_portal_token(self.violet)
        resp = self.client.get(reverse("portal:portal_subject", kwargs={
            "token": violet_token, "curriculum_id": curriculum.pk,
        }))
        self.assertEqual(resp.status_code, 404)

    def test_next_set_advances_after_submit(self):
        from portal.views import _subject_cards

        first_next = _subject_cards(self.kaylin)[0]["next_set"]
        self.assertIsNotNone(first_next)
        # turn in the first set
        q = first_next.questions.first()
        data = {f"answer_{q.pk}": "done."} if q else {}
        self.client.post(self._url("portal_questions", set_pk=first_next.pk), data=data)
        second_next = _subject_cards(self.kaylin)[0]["next_set"]
        self.assertIsNotNone(second_next)
        self.assertNotEqual(second_next.pk, first_next.pk)       # skips the submitted one

    def test_discussion_sets_hidden_from_student_portal(self):
        # Socratic + Discussion are teacher-led — never shown to the child.
        resp = self.client.get(self._url("portal_home"))
        self.assertNotContains(resp, "Socratic Seminar")
        socratic = QuestionSet.objects.filter(title__contains="Socratic").first()
        opened = self.client.get(self._url("portal_questions", set_pk=socratic.pk))
        self.assertEqual(opened.status_code, 404)  # not openable as a student form

    def test_discussion_guide_shows_socratic_to_parent(self):
        curriculum = Curriculum.objects.get(name__contains="I Am David")
        self.client.login(username="dad", password="pw")
        resp = self.client.get(reverse("tutor:discussion_guide", kwargs={"curriculum_pk": curriculum.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Socratic Seminar")
        self.assertContains(resp, "Discussion")
        self.assertContains(resp, "lead")  # facilitation guidance

    def test_typed_fields_offer_spelling_help_but_no_autocorrect(self):
        # It's not a spelling class — the browser flags misspellings (spellcheck),
        # but autocorrect stays off so nothing silently rewrites the child's words.
        resp = self.client.get(self._url("portal_questions", set_pk=self.first_set.pk))
        self.assertContains(resp, 'spellcheck="true"')
        self.assertNotContains(resp, 'spellcheck="false"')
        self.assertContains(resp, 'autocorrect="off"')
        self.assertContains(resp, 'data-gramm="false"')
        self.assertContains(resp, "portal-autosave")  # hashed filename under manifest storage

    def test_autosave_saves_and_scopes(self):
        q = self.first_set.questions.first()
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.first_set.pk),
            data=json.dumps({"answers": {str(q.pk): "My notes on David.", "99999": "evil"}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["ok"])
        sheet = ResponseSheet.objects.get(question_set=self.first_set, child=self.kaylin)
        self.assertEqual(sheet.answers[str(q.pk)], "My notes on David.")
        self.assertNotIn("99999", sheet.answers)

    def test_submit_creates_worklog_entry_and_locks(self):
        q = self.first_text_q
        resp = self.client.post(
            self._url("portal_questions", set_pk=self.first_set.pk),
            data={f"answer_{q.pk}": "David escapes bravely."},
        )
        self.assertEqual(resp.status_code, 302)
        sheet = ResponseSheet.objects.get(question_set=self.first_set, child=self.kaylin)
        self.assertTrue(sheet.is_submitted)
        self.assertIsNotNone(sheet.work_entry)
        self.assertEqual(sheet.work_entry.child, self.kaylin)
        self.assertIn("David escapes bravely.", sheet.work_entry.description)
        # further autosaves are rejected
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.first_set.pk),
            data=json.dumps({"answers": {str(q.pk): "sneaky edit"}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)
        # and the page renders read-only celebration
        resp = self.client.get(self._url("portal_questions", set_pk=self.first_set.pk))
        self.assertContains(resp, "Turned in!")
        self.assertContains(resp, "readonly")

    def test_double_submit_creates_one_worklog_entry(self):
        q = self.first_text_q
        url = self._url("portal_questions", set_pk=self.first_set.pk)
        self.client.post(url, data={f"answer_{q.pk}": "First submit."})
        # a second POST (double-click / stale tab) must NOT create a 2nd entry
        self.client.post(url, data={f"answer_{q.pk}": "Second submit changes nothing."})
        sheets = ResponseSheet.objects.filter(question_set=self.first_set, child=self.kaylin)
        self.assertEqual(sheets.count(), 1)
        self.assertEqual(
            WorkLogEntry.objects.filter(child=self.kaylin, description__contains="Section 1").count(),
            1,
        )
        self.assertIn("First submit.", sheets.first().work_entry.description)

    def test_autosave_rejects_non_object_payload(self):
        for bad in ("[]", '"hi"', "5", "null"):
            resp = self.client.post(
                self._url("portal_autosave", set_pk=self.first_set.pk),
                data=bad, content_type="application/json",
            )
            self.assertEqual(resp.status_code, 400, bad)

    def test_sibling_cannot_open_other_childs_course(self):
        violet_token = make_portal_token(self.violet)
        resp = self.client.get(
            reverse("portal:portal_questions", kwargs={
                "token": violet_token, "set_pk": self.first_set.pk,
            })
        )
        self.assertEqual(resp.status_code, 404)
        home = self.client.get(reverse("portal:portal_home", kwargs={"token": violet_token}))
        self.assertNotContains(home, "I Am David")

    def test_draft_sets_hidden(self):
        QuestionSet.objects.all().update(status=QuestionSet.DRAFT)
        resp = self.client.get(self._url("portal_home"))
        self.assertNotContains(resp, "Socratic Seminar")

    def test_parent_sees_portal_link_on_student_page(self):
        self.client.login(username="dad", password="pw")
        resp = self.client.get(reverse("students:student_detail", kwargs={"pk": self.kaylin.pk}))
        self.assertContains(resp, "portal")
        self.assertContains(resp, "Copy link")

    def test_assess_form_prefills_blackbird_rubric(self):
        q = self.first_text_q
        self.client.post(
            self._url("portal_questions", set_pk=self.first_set.pk),
            data={f"answer_{q.pk}": "My journal notes."},
        )
        sheet = ResponseSheet.objects.get(question_set=self.first_set, child=self.kaylin)
        self.client.login(username="dad", password="pw")
        resp = self.client.get(
            reverse("tutor:assess_create", kwargs={"entry_pk": sheet.work_entry.pk})
        )
        self.assertContains(resp, "Blackbird grading")     # rubric prefilled
        self.assertContains(resp, "My journal notes.")     # answers prefilled


class MarkupTests(TestCase):
    """Draw-on-the-sentence markup questions (Essentials in Writing)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="mup", email="mup@e.com", password="pw")
        cls.family = Family.objects.create(name="Markup Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Essentials in Writing 3", subject="Writing", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="Writing Sentences")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Mark it", family=cls.family,
            status=QuestionSet.APPROVED, intro="Underline the subject.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="editing",
            response_type=Question.TYPE_MARKUP, passage="The dog ran.", prompt="",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_markup_renders_canvas_and_passage(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.qset.pk))
        self.assertContains(resp, "markup-widget")
        self.assertContains(resp, "markup-canvas")
        self.assertContains(resp, "portal-markup")
        # Every word carries its own box so the strokes drawn over it can be read
        # back by name. Without this the passage is one blob and a stroke is
        # coordinates over nothing.
        for i, word in enumerate(["The", "dog", "ran."]):
            self.assertContains(
                resp, f'<span class="markup-word" data-word="{i}">{word}</span>', html=False)

    def test_the_whole_sentence_is_still_readable_on_the_page(self):
        # Splitting into spans must not change what the child sees: the words
        # still read as a sentence, separated by spaces.
        resp = self.client.get(self._url("portal_questions", set_pk=self.qset.pk))
        import re
        html = resp.content.decode()
        passage = re.search(r'<div class="markup-passage">(.*?)</div>', html, re.S).group(1)
        self.assertEqual(re.sub(r"<[^>]+>", "", passage).strip(), "The dog ran.")

    def test_markup_strokes_autosave_and_submit(self):
        strokes = '[{"c":"#333333","w":3,"p":[[0.1,0.5],[0.4,0.5]]}]'
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.qset.pk),
            data=json.dumps({"answers": {str(self.q.pk): strokes}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertEqual(sheet.answers[str(self.q.pk)], strokes)

        self.client.post(
            self._url("portal_questions", set_pk=self.qset.pk),
            data={f"answer_{self.q.pk}": strokes},
        )
        sheet.refresh_from_db()
        self.assertTrue(sheet.is_submitted)
        # A pre-marks answer (a bare stroke array) can only report that she drew —
        # the word positions it was drawn over are gone — but it must say so in a
        # way that does not read to the grader as a wrong answer.
        desc = sheet.work_entry.description
        self.assertIn('she drew 1 mark(s) on "The dog ran."', desc)
        self.assertIn("none were machine-readable", desc)

    def test_a_marked_up_sentence_reaches_the_grader_as_words(self):
        # The point of the whole feature: the grader has to learn WHAT she marked,
        # not merely that she drew something.
        answer = json.dumps({
            "strokes": [{"c": "#333", "w": 3, "p": [[0.1, 0.8], [0.3, 0.8]]}],
            "marks": [{"i": 0, "word": "The", "kind": "underlined"},
                      {"i": 1, "word": "dog", "kind": "underlined"}],
            "unread": 0,
        })
        self.client.post(
            self._url("portal_questions", set_pk=self.qset.pk),
            data={f"answer_{self.q.pk}": answer},
        )
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        desc = sheet.work_entry.description
        self.assertIn('underlined "The", "dog"', desc)
        self.assertNotIn("could not be read", desc)

    def test_eiw_seed_builds_markup_forms(self):
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        markup = Question.objects.filter(response_type=Question.TYPE_MARKUP)
        self.assertGreater(markup.count(), 100)
        self.assertTrue(markup.exclude(passage="").exists())
        # re-running is idempotent (no duplicate sets)
        before = QuestionSet.objects.count()
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        self.assertEqual(QuestionSet.objects.count(), before)

    def test_eiw_matching_exercise_is_one_question_not_one_per_row(self):
        # Lesson 7 is a MATCHING grid: four sentence types beside a lettered answer
        # bank. Seeded as separate questions, the four ANSWER CHOICES became four
        # questions of their own, each with its own empty answer box, and the four
        # sentence types had nothing to choose from.
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        qs = QuestionSet.objects.get(
            lesson__number=7, title__endswith="Match them up")
        self.assertEqual(qs.questions.count(), 1)
        q = qs.questions.get()
        self.assertEqual(q.response_type, Question.TYPE_MATCHING)
        data = json.loads(q.passage)
        self.assertEqual(
            {d["text"]: d["word"] for d in data["definitions"]},
            {
                "Declarative": "Period (.)",
                "Interrogative": "Question Mark (?)",
                "Exclamatory": "Exclamation Point (!)",
                # A command takes a period, or an exclamation point if forceful.
                "Imperative": "Period (.) OR Exclamation Point (!)",
            },
        )
        # Every answer the child can pick has to be in the pool she picks from.
        self.assertEqual(
            sorted(data["words"]),
            sorted(d["word"] for d in data["definitions"]),
        )
        # ...and the pool keeps the workbook's printed A-D order, so a child
        # working alongside the book sees the same four choices in the same order.
        self.assertEqual(data["words"], [
            "Question Mark (?)",                    # A
            "Period (.) OR Exclamation Point (!)",  # B
            "Period (.)",                           # C
            "Exclamation Point (!)",                # D
        ])

    def test_no_eiw_question_is_really_an_answer_choice(self):
        # The general shape of the Lesson 7 bug: a lettered option from an answer
        # bank standing on its own as a question. There is nothing to answer.
        import re
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        offenders = [
            f"{q.question_set.title} Q{q.order}: {q.prompt!r}"
            for q in Question.objects.exclude(prompt="").select_related("question_set")
            if re.match(r"^[A-D]\.\s", q.prompt.strip())
        ]
        self.assertEqual(offenders, [], f"answer choices seeded as questions: {offenders}")

    def _lesson7(self):
        return QuestionSet.objects.filter(lesson__number=7).first().lesson

    def _superseded_set(self, **sheet_kwargs):
        """A set this seeder no longer produces, optionally with a sheet on it."""
        lesson = self._lesson7()
        old = QuestionSet.objects.create(
            lesson=lesson, family=self.family, status=QuestionSet.APPROVED,
            title="Lesson 7 · Types of Sentences and Punctuation Marks — Choose the answer",
            intro="i", rubric="r",
        )
        for i, item in enumerate(
            ["______ Declarative", "______ Interrogative", "______ Exclamatory",
             "______ Imperative", "A. Question Mark (?)",
             "B. Period (.) OR Exclamation Point (!)", "C. Period (.)",
             "D. Exclamation Point (!)"], start=1,
        ):
            Question.objects.create(
                question_set=old, order=i, category="grammar",
                response_type=Question.TYPE_TEXT, prompt=item,
            )
        if sheet_kwargs is not None:
            ResponseSheet.objects.create(
                question_set=old, child=self.violet, **sheet_kwargs)
        return old

    def test_the_superseded_broken_set_is_actually_removed(self):
        # Sets are keyed on title, so retitling leaves the superseded one beside
        # the new one — and the superseded one is the BROKEN one. Recreate the
        # real prod state (8 text questions + an untouched draft sheet) and prove
        # the seeder removes it, rather than asserting the absence of something a
        # fresh test DB never created.
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        old = self._superseded_set(answers={})

        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())

        self.assertFalse(QuestionSet.objects.filter(pk=old.pk).exists())
        self.assertTrue(QuestionSet.objects.filter(
            lesson__number=7, title__endswith="Match them up").exists())

    def test_a_superseded_set_with_saved_answers_is_kept(self):
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        old = self._superseded_set(answers={"1": "her work"})
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        self.assertTrue(QuestionSet.objects.filter(pk=old.pk).exists())

    def test_a_superseded_set_that_was_SUBMITTED_is_kept_even_if_blank(self):
        # The dangerous case: four of the broken set's eight questions were
        # unanswerable answer-choices, so a blank submit is exactly what a child
        # does with it. Lesson completion counts submitted sheets, so deleting one
        # rolls the lesson back to not-done and moves "What's Next" backwards.
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        old = self._superseded_set(answers={}, status=ResponseSheet.SUBMITTED)
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        self.assertTrue(QuestionSet.objects.filter(pk=old.pk).exists())

    def test_a_teacher_discussion_set_is_never_swept_up(self):
        # Discussion sets are excluded from the child's portal, so they can never
        # have a ResponseSheet to protect them — an unscoped sweep would delete
        # them on every single run.
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        keeper = QuestionSet.objects.create(
            lesson=self._lesson7(), family=self.family,
            title="Lesson 7 · Literary Toolbox", intro="i", rubric="r",
            mode=QuestionSet.MODE_DISCUSSION,
        )
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        self.assertTrue(QuestionSet.objects.filter(pk=keeper.pk).exists())

    def test_dry_run_reports_the_removal_without_doing_it(self):
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        old = self._superseded_set(answers={})
        out = StringIO()
        call_command("seed_eiw_violet", "--for-user", "mup", "--dry-run", stdout=out)
        self.assertIn("Removed superseded set", out.getvalue())
        self.assertTrue(QuestionSet.objects.filter(pk=old.pk).exists())

    def test_eiw_seed_builds_write_markup_forms(self):
        # "Write sentences… circle/underline X" exercises become write-then-markup
        # boxes: she types the sentence, then draws on it. They keep the writing
        # prompt and have no fixed passage (she supplies the sentence).
        call_command("seed_eiw_violet", "--for-user", "mup", stdout=StringIO())
        wm = Question.objects.filter(response_type=Question.TYPE_WRITE_MARKUP)
        self.assertGreater(wm.count(), 0)
        q = wm.first()
        self.assertTrue(q.prompt)
        self.assertEqual(q.passage, "")
        self.assertRegex(q.question_set.intro.lower(), r"circle|underline")


class JournalThemeTests(TestCase):
    """Mission-course journals get a themed skin — an Explorer's Log (parchment)
    for Social Studies, a Lab Notebook (graph paper) for Science. Other subjects
    (writing/literature/math) stay unthemed."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="jth", email="jth@e.com", password="pw")
        cls.family = Family.objects.create(name="Journal Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.token = make_portal_token(cls.violet)

    def _set(self, subject, title):
        cur = Curriculum.objects.create(
            parent=self.parent, name=f"{subject} course", subject=subject, family=self.family)
        ch = Chapter.objects.create(curriculum=cur, number=1, title="U1")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="M1")
        CurriculumPlacement.objects.create(child=self.violet, curriculum=cur, current_lesson=lesson)
        qs = QuestionSet.objects.create(
            lesson=lesson, title=title, family=self.family, status=QuestionSet.APPROVED)
        Question.objects.create(question_set=qs, order=1, category="application", prompt="Reflect.")
        return qs

    def _url(self, set_pk):
        return reverse("portal:portal_questions", kwargs={"token": self.token, "set_pk": set_pk})

    def test_social_studies_journal_gets_the_explorer_skin(self):
        qs = self._set("Social Studies", "Mission 1 · Explorer's Log")
        resp = self.client.get(self._url(qs.pk))
        self.assertContains(resp, "journal-explorer")
        self.assertContains(resp, "journal-banner")
        # banner-scoped so the always-rendered card-header title can't satisfy it
        self.assertContains(resp, 'journal-banner-kicker">Explorer')
        self.assertContains(resp, "🧭")              # emoji mapped from the log name
        self.assertNotContains(resp, "journal-lab")

    def test_science_journal_gets_the_lab_skin(self):
        qs = self._set("Science", "Mission 1 · Lab Notebook")
        resp = self.client.get(self._url(qs.pk))
        self.assertContains(resp, "journal-lab")
        self.assertContains(resp, 'journal-banner-kicker">Lab Notebook</div>')
        self.assertContains(resp, "🔬")
        self.assertNotContains(resp, "journal-explorer")

    def test_other_subjects_are_not_themed(self):
        qs = self._set("Writing", "Paragraph practice")
        resp = self.client.get(self._url(qs.pk))
        self.assertNotContains(resp, "journal-themed")
        self.assertNotContains(resp, "journal-banner")


class SubmitKicksGradeTests(TestCase):
    """Turning work in starts grading immediately — not only when the feedback
    page's JS fires — so a submission can't sit ungraded."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="skg", email="skg@e.com", password="pw")
        cls.family = Family.objects.create(name="Kick Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cur = Curriculum.objects.create(
            parent=cls.parent, name="Writing", subject="Writing", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cur, number=1, title="U1")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cur, current_lesson=lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=lesson, title="Q", family=cls.family, status=QuestionSet.APPROVED,
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="editing", prompt="Why?",
        )
        cls.token = make_portal_token(cls.violet)

    def test_submit_starts_background_grade(self):
        url = reverse("portal:portal_questions", kwargs={"token": self.token, "set_pk": self.qset.pk})
        with mock.patch("tutor.grading.start_background_grade") as kick:
            resp = self.client.post(url, data={f"answer_{self.q.pk}": "Because it is true."})
        self.assertEqual(resp.status_code, 302)  # off to the feedback page
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertTrue(sheet.is_submitted)
        kick.assert_called_once_with(sheet.pk)


class ParagraphWritingTests(TestCase):
    """The paragraph writing exercise: rough-draft sections → final draft."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="pwr", email="pwr@e.com", password="pw")
        cls.family = Family.objects.create(name="Para Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cur = Curriculum.objects.create(
            parent=cls.parent, name="A Mouse Called Wolf", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cur, number=1, title="Section 1")
        lesson = Lesson.objects.create(chapter=ch, order=5, number=5, title="Writing")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cur, current_lesson=lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=lesson, title="Section 1 · Writing", family=cls.family, status=QuestionSet.APPROVED,
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="writing",
            response_type=Question.TYPE_PARAGRAPH,
            prompt="Write a paragraph about Wolfgang Amadeus Mouse.",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_renders_rough_sections_final_and_pull(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.qset.pk))
        self.assertContains(resp, "paragraph-widget")
        self.assertContains(resp, "Introduction / Topic Sentence")
        self.assertContains(resp, "Supporting Sentences")
        self.assertContains(resp, "Concluding Sentence")
        self.assertContains(resp, "para-final-box")
        self.assertContains(resp, "Pull in my rough draft")
        self.assertContains(resp, "portal-paragraph")  # hashed filename under manifest storage
        # Coach-the-rough: a paragraph question always shows the coach.
        self.assertContains(resp, "Get feedback on my rough draft")

    def test_custom_sections_via_passage_json(self):
        self.q.passage = '{"sections": ["Beginning", "Middle", "End"]}'
        self.q.save()
        resp = self.client.get(self._url("portal_questions", set_pk=self.qset.pk))
        self.assertContains(resp, "Beginning")
        self.assertContains(resp, "Middle")
        self.assertContains(resp, "End")
        self.assertNotContains(resp, "Concluding Sentence")

    @override_settings(ANTHROPIC_API_KEY="test-key")
    @mock.patch("tutor.ai.review_draft",
                return_value={"praise": "Nice topic sentence!", "suggestions": ["Add one detail."]})
    def test_coach_does_not_clobber_structured_answer(self, _rev):
        # Pre-save a structured paragraph answer, then ask the coach for feedback on
        # the rough draft — the structured answer (with her final draft) must survive.
        sheet = ResponseSheet.objects.create(question_set=self.qset, child=self.violet)
        structured = json.dumps({"rough": ["Wolf is brave.", "", ""], "final": "Wolf is a brave mouse."})
        sheet.answers = {str(self.q.pk): structured}
        sheet.save()
        resp = self.client.post(
            self._url("portal_draft_feedback", set_pk=self.qset.pk),
            data=json.dumps({
                "question": str(self.q.pk),
                "text": "Wolf is a very brave little mouse who loves to sing.",
            }),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["ok"])
        sheet.refresh_from_db()
        self.assertEqual(sheet.answers[str(self.q.pk)], structured)  # untouched
        self.assertIn(str(self.q.pk), sheet.draft_feedback)          # feedback saved


class SpellcheckAndWordHelpTests(TestCase):
    """Red-squiggle spellcheck + 'better words' helper on writing curricula,
    both switched OFF on spelling curricula."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="wh", email="wh@e.com", password="pw")
        cls.family = Family.objects.create(name="WordHelp Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.writing_set = cls._make_set("Blackbird Writing", "Writing")
        cls.spelling_set = cls._make_set("Spelling Week 1", "Spelling")
        cls.token = make_portal_token(cls.violet)

    @classmethod
    def _make_set(cls, name, subject):
        cur = Curriculum.objects.create(
            parent=cls.parent, name=name, subject=subject, family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cur, number=1, title="Unit 1")
        lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cur, current_lesson=lesson)
        qset = QuestionSet.objects.create(
            lesson=lesson, title=name, family=cls.family, status=QuestionSet.APPROVED,
        )
        Question.objects.create(
            question_set=qset, order=1, category="editing",
            response_type=Question.TYPE_TEXT, prompt="Write about it.",
        )
        return qset

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_writing_curriculum_enables_spellcheck_and_wordhelp(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.writing_set.pk))
        self.assertContains(resp, 'spellcheck="true"')
        self.assertContains(resp, "wordhelp-hint")
        self.assertContains(resp, "data-wordhelp-url")
        self.assertContains(resp, "data-spellcheck-url")

    def test_write_markup_question_renders_the_widget(self):
        # A "write a sentence, then circle/underline it" question renders the
        # write-then-markup widget: a typing box + a drawing canvas + the script.
        Question.objects.create(
            question_set=self.writing_set, order=3, category="grammar",
            response_type=Question.TYPE_WRITE_MARKUP,
            prompt="Write a sentence, then circle the verb.",
        )
        resp = self.client.get(self._url("portal_questions", set_pk=self.writing_set.pk))
        self.assertContains(resp, "writemark-widget")
        self.assertContains(resp, "writemark-input")
        self.assertContains(resp, "markup-canvas")
        self.assertContains(resp, "portal-writemarkup")  # the widget's script is loaded

    def test_cloze_blank_gets_native_spellcheck_on_writing(self):
        # A fill-in-the-blank (cloze) box is a place the child types her own words,
        # so it carries native spellcheck; the JS then attaches the AI helpers to
        # it too (verified with jsdom) — grammar drills aren't a spelling blind spot.
        Question.objects.create(
            question_set=self.writing_set, order=2, category="grammar",
            response_type=Question.TYPE_CLOZE, passage="The ___ ran fast.",
        )
        resp = self.client.get(self._url("portal_questions", set_pk=self.writing_set.pk))
        self.assertContains(resp, "cloze-input")
        self.assertRegex(resp.content.decode(), r'cloze-input[^>]*spellcheck="true"')

    def test_spelling_curriculum_disables_spellcheck_and_wordhelp(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.spelling_set.pk))
        self.assertContains(resp, 'spellcheck="false"')
        self.assertNotContains(resp, 'spellcheck="true"')
        self.assertNotContains(resp, "wordhelp-hint")
        self.assertNotContains(resp, "data-wordhelp-url")
        self.assertNotContains(resp, "data-spellcheck-url")

    @mock.patch("tutor.ai.check_spelling", return_value=[
        {"wrong": "speshel", "fixes": ["special"]},
        {"wrong": "becuse", "fixes": ["because"]},
    ])
    def test_spellcheck_endpoint_returns_misspellings(self, _chk):
        resp = self.client.post(
            self._url("portal_spellcheck", set_pk=self.writing_set.pk),
            data=json.dumps({"text": "He was little and speshel becuse of it."}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        wrongs = [m["wrong"] for m in data["misspelled"]]
        self.assertEqual(wrongs, ["speshel", "becuse"])

    @mock.patch("tutor.ai.check_spelling", return_value=[{"wrong": "cat", "fixes": ["cat"]}])
    def test_spellcheck_disabled_on_spelling_curricula(self, chk):
        resp = self.client.post(
            self._url("portal_spellcheck", set_pk=self.spelling_set.pk),
            data=json.dumps({"text": "kat"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["misspelled"], [])
        chk.assert_not_called()

    @mock.patch("portal.thesaurus.synonyms", return_value=["glad", "joyful", "cheerful"])
    def test_word_help_returns_suggestions(self, _syn):
        resp = self.client.post(
            self._url("portal_word_help", set_pk=self.writing_set.pk),
            data=json.dumps({"word": "happy"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["words"], ["glad", "joyful", "cheerful"])

    @mock.patch("portal.thesaurus.synonyms", return_value=["glad"])
    def test_word_help_is_disabled_on_spelling_curricula(self, syn):
        resp = self.client.post(
            self._url("portal_word_help", set_pk=self.spelling_set.pk),
            data=json.dumps({"word": "happy"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["words"], [])
        syn.assert_not_called()


class SocraticStandardTests(TestCase):
    """The reusable CenterForLit question ladder scales by the reader's level."""

    def test_questions_scale_by_level(self):
        from tutor import socratic

        g3 = socratic.questions_for("G03")
        g7 = socratic.questions_for("G07")
        self.assertGreater(len(g7), len(g3))  # older readers get more/deeper questions
        # every element is represented at the top band
        cats = {c for c, _t, _h in g7}
        for expected in ("context", "setting", "character", "conflict", "plot", "theme", "style"):
            self.assertIn(expected, cats)

    def test_band_mapping(self):
        from tutor import socratic

        self.assertEqual(socratic.band_for_level("G02"), 1)
        self.assertEqual(socratic.band_for_level("G05"), 2)
        self.assertEqual(socratic.band_for_level("G09"), 3)


class LiteratureStandardTests(TestCase):
    """The reusable framework ties any literature curriculum to Socratic + tools."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="lit", email="lit@e.com", password="pw")
        cls.family = Family.objects.create(name="Lit Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )

    def test_devices_scale_by_level(self):
        from tutor import literature

        self.assertLess(len(literature.devices_for("G03")), len(literature.devices_for("G07")))
        names_g3 = {d["name"] for d in literature.devices_for("G03")}
        self.assertIn("Onomatopoeia", names_g3)         # band-1 tool for a 3rd grader
        self.assertNotIn("Irony", names_g3)             # band-3 tool held back
        self.assertIn("Irony", {d["name"] for d in literature.devices_for("G07")})

    def test_command_scaffolds_and_applies(self):
        call_command(
            "seed_literature_standard", "--for-user", "lit", "--child-name", "Violet",
            "--name", "Blackbird Literature (Grade 3)", "--level", "G03", stdout=StringIO(),
        )
        curriculum = Curriculum.objects.get(name="Blackbird Literature (Grade 3)")
        self.assertEqual(curriculum.subject, "Literature")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        # exactly the two teacher-led standard sets, both discussion mode
        self.assertEqual(sets.count(), 2)
        self.assertTrue(all(s.mode == QuestionSet.MODE_DISCUSSION for s in sets))
        self.assertTrue(sets.filter(title__contains="Story-Grammar").exists())
        self.assertTrue(sets.filter(title__contains="Literary Toolbox").exists())
        # child is placed
        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.child, curriculum=curriculum).exists()
        )

    def test_apply_is_idempotent(self):
        from tutor import literature

        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Some Novel", subject="Literature",
            grade_level="G05", family=self.family,
        )
        literature.apply_literature_standard(curriculum, "G05")
        literature.apply_literature_standard(curriculum, "G05")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        self.assertEqual(sets.count(), 2)  # no duplication on re-run

    def test_reapply_at_new_level_does_not_duplicate_toolbox(self):
        from tutor import literature

        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Aging Reader", subject="Literature", family=self.family,
        )
        literature.apply_literature_standard(curriculum, "G05")   # band 2
        literature.apply_literature_standard(curriculum, "G07")   # band 3 — a grade bump
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=curriculum)
        toolboxes = sets.filter(title__startswith="Literary Toolbox")
        self.assertEqual(toolboxes.count(), 1)                    # exactly one, not two
        # and it now holds the higher-band tool set
        self.assertEqual(toolboxes.first().questions.count(), len(literature.devices_for("G07")))

    def test_scaffold_uses_childs_level_when_level_omitted(self):
        kaylin = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07", family=self.family,
        )
        call_command(
            "seed_literature_standard", "--for-user", "lit", "--child-name", "Kaylin",
            "--name", "Kaylin Lit", stdout=StringIO(),   # NO --level
        )
        from tutor import literature

        curriculum = Curriculum.objects.get(name="Kaylin Lit")
        self.assertEqual(curriculum.grade_level, "G07")           # inferred from Kaylin
        toolbox = QuestionSet.objects.get(
            lesson__chapter__curriculum=curriculum, title="Literary Toolbox",
        )
        self.assertEqual(toolbox.questions.count(), len(literature.devices_for("G07")))

    def test_toolbox_hidden_from_student_but_in_discussion_guide(self):
        from tutor import literature

        curriculum = Curriculum.objects.create(
            parent=self.parent, name="Novel 2", subject="Literature",
            grade_level="G03", family=self.family,
        )
        anchor = literature.ensure_anchor_lesson(curriculum)
        CurriculumPlacement.objects.create(child=self.child, curriculum=curriculum, current_lesson=anchor)
        literature.apply_literature_standard(curriculum, "G03")
        # not in the student's portal
        token = make_portal_token(self.child)
        home = self.client.get(reverse("portal:portal_home", kwargs={"token": token}))
        self.assertNotContains(home, "Literary Toolbox")
        # but present in the parent discussion guide
        self.client.login(username="lit", password="pw")
        guide = self.client.get(reverse("tutor:discussion_guide", kwargs={"curriculum_pk": curriculum.pk}))
        self.assertContains(guide, "Literary Toolbox")
        self.assertContains(guide, "Onomatopoeia")


class CharacterQuestionTests(TestCase):
    """A 'characters' question renders one labeled box per character."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ch", email="ch@e.com", password="pw")
        cls.family = Family.objects.create(name="Char Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="I Am David", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="Chapters 1–2")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="Journal")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Section 1 · Journal", family=cls.family,
            status=QuestionSet.APPROVED, intro="Note who each character is.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="character",
            response_type=Question.TYPE_CHARACTERS, passage="David · The Man · Johannes",
            prompt="CHARACTERS — note who each person is.",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_character_names_parses(self):
        self.assertEqual(self.q.character_names, ["David", "The Man", "Johannes"])

    def test_renders_a_box_per_character(self):
        resp = self.client.get(self._url("portal_questions", set_pk=self.qset.pk))
        self.assertEqual(resp.status_code, 200)
        for name in ("David", "The Man", "Johannes"):
            self.assertContains(resp, name)
        self.assertContains(resp, "character-widget")
        self.assertEqual(resp.content.decode().count("character-box"), 3)   # one box each
        self.assertContains(resp, "portal-characters")                      # widget JS loaded
        self.assertNotContains(resp, f'id="q{self.q.pk}"')                  # NOT one shared textarea

    def test_autosave_then_submit_stores_per_character_map(self):
        answer = '{"David": "A brave, careful boy.", "Johannes": "David\'s wise friend."}'
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.qset.pk),
            data=json.dumps({"answers": {str(self.q.pk): answer}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.client.post(self._url("portal_questions", set_pk=self.qset.pk), data={f"answer_{self.q.pk}": answer})
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertTrue(sheet.is_submitted)
        self.assertEqual(sheet.answers[str(self.q.pk)], answer)
        text = sheet.as_worklog_text()
        self.assertIn("David: A brave, careful boy.", text)
        self.assertIn("Johannes: David's wise friend.", text)

    def test_worklog_text_handles_blank_and_garbage(self):
        sheet = ResponseSheet.objects.create(question_set=self.qset, child=self.violet, answers={str(self.q.pk): ""})
        self.assertIn("(no answer)", sheet.as_worklog_text())
        sheet.answers = {str(self.q.pk): "not json"}
        self.assertIn("(no answer)", sheet.as_worklog_text())   # never crashes


class VocabWidgetTests(TestCase):
    """Workbook-style vocabulary: match-the-number + fill-in-the-blank."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="vw", email="vw@e.com", password="pw")
        cls.family = Family.objects.create(name="Vocab Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="Vocab Course", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="Acquire")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Vocabulary", family=cls.family,
            status=QuestionSet.APPROVED,
        )
        cls.match_q = Question.objects.create(
            question_set=cls.qset, order=1, category="vocabulary",
            response_type=Question.TYPE_MATCHING,
            prompt="Write in the number of the correct definition for each word.",
            passage=json.dumps({
                "words": ["gleam", "edible"],
                "definitions": [
                    {"n": 1, "text": "able to be eaten", "word": "edible"},
                    {"n": 2, "text": "to shine", "word": "gleam"},
                ],
            }),
        )
        cls.blank_q = Question.objects.create(
            question_set=cls.qset, order=2, category="vocabulary",
            response_type=Question.TYPE_FILL_BLANK,
            prompt="Fill in each blank with the best word.",
            passage=json.dumps({
                "words": ["gleam", "edible"],
                "sentences": [
                    {"text": "Polish it until you make it ______.", "word": "gleam"},
                    {"text": "Not everything ______ tastes good.", "word": "edible"},
                ],
            }),
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_renders_matching_and_fill_blank_widgets(self):
        html = self.client.get(self._url("portal_questions", set_pk=self.qset.pk)).content.decode()
        self.assertIn("vocab-matching", html)
        self.assertIn("vocab-fillblank", html)
        for token in ("gleam", "edible", "able to be eaten", "to shine"):
            self.assertIn(token, html)
        self.assertEqual(html.count('class="vocab-word"'), 2)   # a button per word
        self.assertEqual(html.count('class="vocab-def"'), 2)    # a button per definition
        self.assertIn("vocab-blank-select", html)
        self.assertIn("portal-vocab", html)          # widget JS loaded
        # No free-text box for either question — the widgets replace the textarea.
        self.assertNotIn(f'id="q{self.match_q.pk}"', html)
        self.assertNotIn(f'id="q{self.blank_q.pk}"', html)

    def test_autosave_and_submit_store_json_and_render_worklog(self):
        match_answer = json.dumps({"matches": {"gleam": 2, "edible": 1}, "tries": 1})
        blank_answer = json.dumps({"blanks": {"0": "gleam", "1": "edible"}, "tries": 0})
        resp = self.client.post(
            self._url("portal_autosave", set_pk=self.qset.pk),
            data=json.dumps({"answers": {
                str(self.match_q.pk): match_answer,
                str(self.blank_q.pk): blank_answer,
            }}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.client.post(self._url("portal_questions", set_pk=self.qset.pk), data={
            f"answer_{self.match_q.pk}": match_answer,
            f"answer_{self.blank_q.pk}": blank_answer,
        })
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertTrue(sheet.is_submitted)
        text = sheet.as_worklog_text()
        self.assertIn("gleam → 2 (to shine) ✓", text)
        self.assertIn("edible → 1 (able to be eaten) ✓", text)
        self.assertIn("(1 wrong try along the way)", text)
        self.assertIn("[gleam]", text)                # sentence rendered with the word
        self.assertIn("Polish it until you make it", text)

    def test_worklog_text_survives_blank_and_garbage(self):
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.violet,
            answers={str(self.match_q.pk): "", str(self.blank_q.pk): "not json"},
        )
        text = sheet.as_worklog_text()
        self.assertEqual(text.count("(no answer)"), 2)   # never crashes

    def test_vocab_data_survives_garbage_passage(self):
        self.match_q.passage = "{broken json"
        self.assertEqual(self.match_q.vocab_data, {})          # malformed JSON → {}
        # And the fill-blank helper pre-splits sentences at the blank.
        first = self.blank_q.fill_blank_sentences[0]
        self.assertEqual(first["word"], "gleam")
        self.assertEqual(first["before"], "Polish it until you make it ")
        self.assertEqual(first["after"], ".")


class ClozeWidgetTests(TestCase):
    """EIW-style fill-in-the-blanks: inline inputs at each blank (own words)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="cz", email="cz@e.com", password="pw")
        cls.family = Family.objects.create(name="Cloze Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="EIW Test", subject="Writing", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Fill in the blanks", family=cls.family,
            status=QuestionSet.APPROVED, intro="Add subjects where they are missing.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="grammar",
            response_type=Question.TYPE_CLOZE,
            passage="____________ liked to ride his bike. One day, ____________ met a girl.",
            prompt="",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def test_segments_and_blank_count(self):
        self.assertEqual(self.q.cloze_blank_count, 2)
        segs = self.q.cloze_segments
        self.assertEqual(segs[0]["blank"], 0)                     # starts with a blank
        self.assertIn("liked to ride his bike", segs[1]["text"])
        self.assertEqual(segs[2]["blank"], 1)

    def test_renders_inline_inputs_not_underscores(self):
        html = self.client.get(self._url("portal_questions", set_pk=self.qset.pk)).content.decode()
        self.assertIn("cloze-input", html)
        self.assertEqual(html.count('class="cloze-input"'), 2)   # one input per blank
        self.assertNotIn("____", html)                           # no underscore walls
        self.assertIn("liked to ride his bike", html)

    def test_submit_renders_words_into_worklog(self):
        answer = json.dumps({"blanks": {"0": "Marcus", "1": "he"}})
        self.client.post(self._url("portal_questions", set_pk=self.qset.pk),
                         data={f"answer_{self.q.pk}": answer})
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        text = sheet.as_worklog_text()
        self.assertIn("[Marcus] liked to ride his bike", text)
        self.assertIn("[he] met a girl", text)

    def test_blank_answer_and_garbage_degrade(self):
        sheet = ResponseSheet.objects.create(
            question_set=self.qset, child=self.violet, answers={str(self.q.pk): "junk"},
        )
        self.assertIn("(no answer)", sheet.as_worklog_text())

    def test_eiw_seed_converts_fill_blank_to_cloze(self):
        from io import StringIO
        from django.core.management import call_command
        call_command("seed_eiw_violet", "--for-user", "cz", stdout=StringIO())
        cloze = Question.objects.filter(response_type=Question.TYPE_CLOZE)
        self.assertGreater(cloze.count(), 10)                    # the workbook's blanks
        self.assertTrue(all("___" in c.passage for c in cloze.exclude(pk=self.q.pk)))


class FeedbackAgentTests(TestCase):
    """HH-97: submit → kid feedback page → parent 'feedback to review' card."""

    GRADE_RESULT = {
        "level": "proficient",
        "summary": "Solid comprehension against the rubric.",
        "criteria": [{"criterion": "Complete sentences", "met": True, "comment": "Yes"}],
        "encouragement": "Violet, your answer about Wolf's bravery was wonderful!",
        "kid_highlights": ["You used complete sentences.", "Next time, add one more detail."],
        "parent_pointers": ["Ask Violet to point to the part that shows bravery.",
                            "Reinforce with a re-read of that page together."],
    }

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="fb", email="fb@e.com", password="pw")
        cls.family = Family.objects.create(name="FB Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="FB Course", subject="Literature",
            grade_level="G03", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Comprehension", family=cls.family,
            status=QuestionSet.APPROVED, rubric="Answer in complete sentences.",
            answer_key="1. Wolf is brave.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="comprehension", prompt="Why is Wolf brave?",
        )
        cls.token = make_portal_token(cls.violet)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def _submit(self):
        return self.client.post(
            self._url("portal_questions", set_pk=self.qset.pk),
            data={f"answer_{self.q.pk}": "Wolf sings for help even though he is small."},
        )

    def test_submit_redirects_to_feedback_page(self):
        resp = self._submit()
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/feedback/", resp["Location"])
        page = self.client.get(resp["Location"])
        self.assertContains(page, "Turned in!")
        self.assertContains(page, "What's next?")

    def test_feedback_page_before_submit_redirects_back(self):
        resp = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn("/feedback/", resp["Location"])

    def test_generate_creates_one_draft_and_returns_kid_fields_only(self):
        from unittest.mock import patch
        from tutor.models import MasteryAssessment

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)) as mocked:
            r1 = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
            r2 = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        data = r1.json()
        self.assertTrue(data["ok"])
        self.assertIn("bravery", data["encouragement"])
        self.assertEqual(len(data["highlights"]), 2)
        self.assertNotIn("level", data)                       # the child never sees a level
        self.assertNotIn("proficient", str(data))
        self.assertTrue(r2.json()["ok"])                      # idempotent
        self.assertEqual(mocked.call_count, 1)                # graded exactly once
        a = MasteryAssessment.objects.get()
        self.assertEqual(a.status, MasteryAssessment.DRAFT)
        self.assertIsNone(a.graded_by)                        # agent-drafted
        self.assertTrue(a.is_auto)
        self.assertEqual(a.ai_level, "proficient")
        self.assertIn("Reference answers", a.rubric)          # answer key folded in
        self.assertEqual(a.ai_parent_pointers, self.GRADE_RESULT["parent_pointers"])  # stored for the parent
        self.assertNotIn("point to the part", str(data))      # parent pointers never leak to the child

    def test_unconfigured_and_error_fall_back_without_assessment(self):
        from unittest.mock import patch
        from tutor import ai
        from tutor.models import MasteryAssessment

        self._submit()
        r = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        self.assertFalse(r.json()["ok"])                      # no key configured in tests
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", side_effect=ai.GraderError("boom")):
            r = self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        self.assertFalse(r.json()["ok"])
        self.assertEqual(MasteryAssessment.objects.count(), 0)
        # and the page itself still celebrates
        page = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertContains(page, "Turned in!")
        self.assertContains(page, "look at it soon")

    def test_feedback_page_renders_existing_assessment_without_level(self):
        from unittest.mock import patch

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        page = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertContains(page, "A note about your work")
        self.assertContains(page, "bravery")
        self.assertContains(page, "complete sentences.")
        self.assertNotContains(page, "Proficient")            # no levels for the child
        self.assertNotContains(page, "proficient")

    def test_feedback_page_holds_until_ai_is_ready(self):
        # Track C: while grading is pending, show a "reading your work" hold state
        # and keep the feedback + "what's next" gated (hidden) until JS reveals them.
        from unittest.mock import patch

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True):
            page = self.client.get(self._url("portal_feedback", set_pk=self.qset.pk))
        self.assertContains(page, "reading your work")           # the hold state
        self.assertContains(page, 'id="portal-hold"')
        self.assertContains(page, 'id="portal-reveal" hidden')    # reveal gated until ready

    def test_sibling_token_cannot_reach_feedback(self):
        self._submit()
        sibling = make_portal_token(self.kaylin)
        for name in ("portal_feedback", "portal_feedback_generate"):
            url = reverse(f"portal:{name}", kwargs={"token": sibling, "set_pk": self.qset.pk})
            resp = self.client.post(url) if "generate" in name else self.client.get(url)
            self.assertEqual(resp.status_code, 404)

    def test_parent_hub_shows_feedback_to_review_until_finalized(self):
        from unittest.mock import patch
        from tutor.models import MasteryAssessment

        self._submit()
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        self.client.login(username="fb", password="pw")
        home = self.client.get(reverse("home"))
        self.assertContains(home, "Feedback to review")
        self.assertContains(home, "Violet")
        a = MasteryAssessment.objects.get()
        detail = self.client.get(reverse("tutor:assess_detail", kwargs={"pk": a.pk}))
        self.assertContains(detail, "What Violet was told at turn-in")
        self.assertContains(detail, "bravery")
        # finalize → the hub card clears
        self.client.post(reverse("tutor:assess_finalize", kwargs={"pk": a.pk}),
                         data={"final_level": "proficient"})
        home = self.client.get(reverse("home"))
        self.assertNotContains(home, "Feedback to review")


class WritingCoachTests(TestCase):
    """HH-98: draft feedback on rough drafts — formative, never a grade."""

    COACH_RESULT = {
        "praise": "Your first sentence really hooks the reader!",
        "suggestions": ["Add one detail about how Wolf feels.", "Read it out loud to catch the missing word."],
    }

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="wc", email="wc@e.com", password="pw")
        cls.family = Family.objects.create(name="WC Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="WC Course", subject="Literature",
            grade_level="G03", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Writing", family=cls.family,
            status=QuestionSet.APPROVED,
        )
        cls.draft_q = Question.objects.create(
            question_set=cls.qset, order=1, category="application",
            prompt="ROUGH DRAFT — Write a paragraph about Wolfgang Amadeus Mouse.",
        )
        cls.comp_q = Question.objects.create(
            question_set=cls.qset, order=2, category="comprehension",
            prompt="Why is Wolf brave?",
        )
        cls.token = make_portal_token(cls.violet)

    def _coach(self, qid, text, token=None):
        url = reverse("portal:portal_draft_feedback", kwargs={
            "token": token or self.token, "set_pk": self.qset.pk,
        })
        return self.client.post(url, data=json.dumps({"question": str(qid), "text": text}),
                                content_type="application/json")

    def test_supports_draft_coach_gating(self):
        self.assertTrue(self.draft_q.supports_draft_coach)     # ROUGH DRAFT marker
        self.assertFalse(self.comp_q.supports_draft_coach)     # comprehension: no coach
        eiw_q = Question.objects.create(
            question_set=self.qset, order=3, category="writing", prompt="Write a paragraph.",
        )
        self.assertTrue(eiw_q.supports_draft_coach)            # EIW writing category

    def test_coach_stores_feedback_and_draft(self):
        from unittest.mock import patch

        draft = "Wolf is a very small mouse but he has a very big dream about singing."
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.review_draft", return_value=dict(self.COACH_RESULT)) as mocked:
            resp = self._coach(self.draft_q.pk, draft)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertIn("hooks", data["praise"])
        self.assertEqual(len(data["suggestions"]), 2)
        self.assertEqual(mocked.call_count, 1)
        sheet = ResponseSheet.objects.get(question_set=self.qset, child=self.violet)
        self.assertEqual(sheet.answers[str(self.draft_q.pk)], draft)   # draft saved too
        self.assertIn(str(self.draft_q.pk), sheet.draft_feedback)
        # and it renders back on reload
        page = self.client.get(reverse("portal:portal_questions", kwargs={
            "token": self.token, "set_pk": self.qset.pk,
        }))
        self.assertContains(page, "Your writing coach says")
        self.assertContains(page, "hooks the reader")
        self.assertContains(page, "Get feedback on my draft")

    def test_coach_rejects_non_draft_question_and_short_text(self):
        from unittest.mock import patch

        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.review_draft", return_value=dict(self.COACH_RESULT)):
            self.assertEqual(self._coach(self.comp_q.pk, "x" * 50).status_code, 400)
            self.assertEqual(self._coach(self.draft_q.pk, "too short").json()["error"], "too_short")

    def test_coach_blocked_after_submit_and_for_siblings(self):
        from unittest.mock import patch

        kaylin = Student.objects.create(
            parent=self.parent, first_name="Kaylin", grade_level="G07", family=self.family,
        )
        with patch("tutor.ai.is_configured", return_value=True), \
             patch("tutor.ai.review_draft", return_value=dict(self.COACH_RESULT)), \
             patch("tutor.grading.start_background_grade"):  # submit now kicks a grade; don't hit the real one
            resp = self._coach(self.draft_q.pk, "x" * 40, token=make_portal_token(kaylin))
            self.assertEqual(resp.status_code, 404)            # not her course
            self.client.post(reverse("portal:portal_questions", kwargs={
                "token": self.token, "set_pk": self.qset.pk,
            }), data={f"answer_{self.draft_q.pk}": "final text here"})
            resp = self._coach(self.draft_q.pk, "x" * 40)
            self.assertEqual(resp.status_code, 409)            # already turned in

    def test_coach_unconfigured_degrades(self):
        resp = self._coach(self.draft_q.pk, "x" * 40)
        self.assertFalse(resp.json()["ok"])                    # no key in tests → soft fail
        self.assertFalse(ResponseSheet.objects.filter(draft_feedback__isnull=False,
                                                      question_set=self.qset).exclude(draft_feedback={}).exists())


class GradingHistoryTests(TestCase):
    """HH-98: the family's grading history — drafts first, then the record."""

    @classmethod
    def setUpTestData(cls):
        from tutor.models import MasteryAssessment

        cls.parent = User.objects.create_user(username="gh", email="gh@e.com", password="pw")
        cls.family = Family.objects.create(name="GH Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family,
        )
        e1 = WorkLogEntry.objects.create(parent=cls.parent, family=cls.family,
                                         child=cls.violet, subject="Literature")
        e2 = WorkLogEntry.objects.create(parent=cls.parent, family=cls.family,
                                         child=cls.kaylin, subject="Writing")
        cls.draft = MasteryAssessment.objects.create(
            work_entry=e1, rubric="r", answers="a", ai_level="proficient",
        )
        cls.final = MasteryAssessment.objects.create(
            work_entry=e2, rubric="r", answers="a", ai_level="mastered",
            final_level="mastered", status=MasteryAssessment.FINALIZED,
        )
        # another family's assessment must never appear
        other = User.objects.create_user(username="gh2", email="gh2@e.com", password="pw")
        fam2 = Family.objects.create(name="Other GH")
        FamilyMembership.objects.create(user=other, family=fam2, role="parent")
        kid2 = Student.objects.create(parent=other, first_name="Eve", grade_level="G01", family=fam2)
        e3 = WorkLogEntry.objects.create(parent=other, family=fam2, child=kid2, subject="SecretSubj")
        MasteryAssessment.objects.create(work_entry=e3, rubric="r", answers="a", ai_level="beginning")

    def test_history_lists_drafts_then_finalized_scoped_to_family(self):
        self.client.login(username="gh", password="pw")
        resp = self.client.get(reverse("tutor:assessment_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([a.pk for a in resp.context["drafts"]], [self.draft.pk])
        self.assertEqual([a.pk for a in resp.context["finalized"]], [self.final.pk])
        self.assertContains(resp, "Awaiting your review")
        self.assertContains(resp, "Agent draft")
        self.assertNotContains(resp, "SecretSubj")
        self.assertNotIn("Eve", [c.first_name for c in resp.context["children"]])

    def test_child_filter(self):
        self.client.login(username="gh", password="pw")
        resp = self.client.get(reverse("tutor:assessment_list"), {"child_id": self.kaylin.id})
        self.assertEqual(resp.context["drafts"], [])
        self.assertEqual([a.pk for a in resp.context["finalized"]], [self.final.pk])

    def test_requires_login(self):
        resp = self.client.get(reverse("tutor:assessment_list"))
        self.assertEqual(resp.status_code, 302)

    def test_progress_page_links_to_history(self):
        self.client.login(username="gh", password="pw")
        resp = self.client.get(reverse("dashboard:dashboard"))
        self.assertContains(resp, reverse("tutor:assessment_list"))   # the grading-history link


class OnlineCurriculumTests(TestCase):
    """A core subject done on an external site launches out of the portal."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="oc", email="oc@e.com", password="pw")
        cls.family = Family.objects.create(name="OC Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.online = Curriculum.objects.create(
            parent=cls.parent, name="Beast Academy", subject="Math", grade_level="G03",
            family=cls.family, is_online=True, website_url="https://beastacademy.com/",
        )
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.online)
        cls.token = make_portal_token(cls.violet)

    def test_is_external_needs_flag_and_url(self):
        self.assertTrue(self.online.is_external)
        self.online.website_url = ""
        self.assertFalse(self.online.is_external)     # flag alone isn't enough

    def test_home_card_launches_out(self):
        from portal.views import _subject_cards
        card = _subject_cards(self.violet)[0]
        self.assertTrue(card["is_external"])
        self.assertEqual(card["launch_url"], "https://beastacademy.com/")
        html = self.client.get(reverse("portal:portal_home", kwargs={"token": self.token})).content.decode()
        self.assertIn("Beast Academy", html)
        self.assertIn('href="https://beastacademy.com/"', html)
        self.assertIn('rel="noopener noreferrer"', html)
        self.assertIn("opens your lessons ↗", html)
        # NOT an in-app drill-in link for this subject
        self.assertNotIn(f"/subject/{self.online.pk}/", html)

    def test_drilldown_shows_launch_button(self):
        resp = self.client.get(reverse("portal:portal_subject", kwargs={
            "token": self.token, "curriculum_id": self.online.pk,
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Open Beast Academy ↗")
        self.assertContains(resp, "this subject online")

    def test_form_exposes_is_online(self):
        from curricula.forms import CurriculumForm
        self.assertIn("is_online", CurriculumForm().fields)


class PortalMarkdownRenderTests(TestCase):
    """Prompts/intros render Markdown (bold, lists) instead of showing raw **."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="mdp", email="mdp@e.com", password="pw")
        cls.family = Family.objects.create(name="MD Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="MD Course", subject="Literature", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Vocab", family=cls.family,
            status=QuestionSet.APPROVED, intro="Do **all** of these:",
        )
        Question.objects.create(question_set=cls.qset, order=1, category="vocabulary",
                                prompt="Define: **scamper**")
        cls.token = make_portal_token(cls.violet)

    def test_bold_prompt_renders_strong_not_asterisks(self):
        url = reverse("portal:portal_questions", kwargs={"token": self.token, "set_pk": self.qset.pk})
        html = self.client.get(url).content.decode()
        self.assertIn("<strong>scamper</strong>", html)   # bold, not raw
        self.assertNotIn("**scamper**", html)             # no literal asterisks
        self.assertIn("<strong>all</strong>", html)       # intro bold too


class AMouseCalledWolfSeedTests(TestCase):
    """Violet's Blackbird 'A Mouse Called Wolf' course (original, book-grounded)."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="mw", email="mw@e.com", password="pw")
        cls.family = Family.objects.create(name="MW Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        call_command("seed_a_mouse_called_wolf", "--for-user", "mw", stdout=StringIO())
        cls.curriculum = Curriculum.objects.get(name__contains="Mouse Called Wolf")

    def test_course_shape_and_teacher_answer_keys(self):
        self.assertEqual(self.curriculum.grade_level, "G03")
        sets = QuestionSet.objects.filter(lesson__chapter__curriculum=self.curriculum)
        # 6 sets/section x 4 sections + Glean + Story-Grammar + Toolbox = 27,
        # plus the hands-on Glean option = 28. The guide's own Glean set is
        # still one of them: the hands-on one was added ALONGSIDE the printed
        # five options, never in place of them.
        self.assertEqual(sets.count(), 28)
        self.assertEqual(sets.filter(title__contains="Glean").count(), 2)
        self.assertTrue(sets.filter(title__endswith="Glean: Final Project").exists())
        # every Comprehension set carries a teacher answer key (never shown to students)
        comp = sets.filter(title__contains="Comprehension")
        self.assertEqual(comp.count(), 4)
        self.assertTrue(all(c.answer_key.strip() for c in comp))
        self.assertTrue(comp.filter(answer_key__contains="teacher reference only").exists())

    def test_answer_key_resource_seeded_teacher_only(self):
        r = CurriculumResource.objects.get(
            curriculum=self.curriculum, resource_type=CurriculumResource.ANSWER_KEY,
        )
        self.assertTrue(r.teacher_only)             # never shown to the student
        self.assertIn("blackbirdandcompany.com", r.url)

    def test_journal_uses_per_character_boxes(self):
        journal = QuestionSet.objects.get(
            lesson__chapter__curriculum=self.curriculum, title="Section 1 · Journal",
        )
        q = journal.questions.get(order=1)
        self.assertEqual(q.response_type, Question.TYPE_CHARACTERS)
        # The guide's own character list for Section 1.
        self.assertIn("Wolfgang Amadeus Mouse", q.character_names)
        self.assertEqual(len(q.character_names), 2)

    def test_vocabulary_is_workbook_matching_plus_fill_blank(self):
        vocab = QuestionSet.objects.get(
            lesson__chapter__curriculum=self.curriculum, title="Section 1 · Vocabulary",
        )
        qs = list(vocab.questions.order_by("order"))
        self.assertEqual([q.response_type for q in qs],
                         [Question.TYPE_MATCHING, Question.TYPE_FILL_BLANK])
        matching = qs[0].vocab_data
        # The guide's real Section 1 words, with its fixed answer numbering.
        self.assertEqual(matching["words"],
                         ["ordinary", "venture", "gleam", "edible", "dwindle", "curiosity"])
        by_word = {d["word"]: d["n"] for d in matching["definitions"]}
        self.assertEqual(by_word["ordinary"], 3)
        self.assertEqual(by_word["curiosity"], 1)
        # Fill-blank: 6 sentences, one blank each, answers drawn from the same words.
        sentences = qs[1].vocab_data["sentences"]
        self.assertEqual(len(sentences), 6)
        self.assertTrue(all("______" in s["text"] for s in sentences))
        self.assertTrue(all(s["word"] in matching["words"] for s in sentences))
        # Teacher key on the set covers both halves.
        self.assertIn("Matching:", vocab.answer_key)
        self.assertIn("Fill in the blank:", vocab.answer_key)

    def test_section4_is_chapters_10_to_11(self):
        # The guide's Section 4 covers chapters 10–11 (the book has 11 chapters).
        from curricula.models import Chapter as Ch
        title = Ch.objects.get(curriculum=self.curriculum, number=4).title
        self.assertIn("10–11", title)

    def test_violet_placed_and_discussion_hidden_from_student(self):
        from portal.views import _visible_question_sets

        self.assertTrue(
            CurriculumPlacement.objects.filter(child=self.violet, curriculum=self.curriculum).exists()
        )
        titles = set(_visible_question_sets(self.violet).values_list("title", flat=True))
        self.assertIn("Section 1 · Comprehension", titles)     # student work is visible
        self.assertNotIn("Section 1 · Discussion", titles)     # teacher-led stays hidden
        self.assertNotIn("Section 1 · Socratic Seminar", titles)

    def test_idempotent(self):
        before = QuestionSet.objects.filter(lesson__chapter__curriculum=self.curriculum).count()
        call_command("seed_a_mouse_called_wolf", "--for-user", "mw", stdout=StringIO())
        after = QuestionSet.objects.filter(lesson__chapter__curriculum=self.curriculum).count()
        self.assertEqual(before, after)


class BackgroundGradingTests(TestCase):
    """HH: submit-time grading runs off the request path; the page polls for it."""

    GRADE_RESULT = {
        "level": "proficient",
        "summary": "Solid comprehension against the rubric.",
        "criteria": [{"criterion": "Complete sentences", "met": True, "comment": "Yes"}],
        "encouragement": "Rae, your answer about Wolf's bravery was wonderful!",
        "kid_highlights": ["You used complete sentences.", "Add one more detail next time."],
        "parent_pointers": ["Ask Rae to point to the part that shows bravery."],
    }

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="bg", email="bg@e.com", password="pw")
        cls.family = Family.objects.create(name="BG Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Rae", grade_level="G03", family=cls.family,
        )
        cls.cur = Curriculum.objects.create(
            parent=cls.parent, name="BG Course", subject="Literature",
            grade_level="G03", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.cur, number=1, title="One")
        cls.lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L1")
        CurriculumPlacement.objects.create(child=cls.child, curriculum=cls.cur, current_lesson=cls.lesson)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Comprehension", family=cls.family,
            status=QuestionSet.APPROVED, rubric="Answer in complete sentences.",
        )
        cls.q = Question.objects.create(
            question_set=cls.qset, order=1, category="comprehension", prompt="Why is Wolf brave?",
        )
        cls.token = make_portal_token(cls.child)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def _submit(self):
        return self.client.post(
            self._url("portal_questions", set_pk=self.qset.pk),
            data={f"answer_{self.q.pk}": "Wolf sings for help even though he is small."},
        )

    def test_status_reports_not_ready_then_ready(self):
        self._submit()
        body = self.client.get(self._url("portal_feedback_status", set_pk=self.qset.pk)).json()
        self.assertFalse(body["ready"])
        self.assertFalse(body["grading"])        # no key configured in tests → nothing to wait for
        # Grade it (inline via the synchronous fallback with a mocked grader).
        with mock.patch("tutor.ai.is_configured", return_value=True), \
             mock.patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self.client.post(self._url("portal_feedback_generate", set_pk=self.qset.pk))
        body = self.client.get(self._url("portal_feedback_status", set_pk=self.qset.pk)).json()
        self.assertTrue(body["ready"])
        self.assertIn("bravery", body["encouragement"])
        self.assertEqual(len(body["highlights"]), 2)
        self.assertNotIn("level", body)          # the child never sees a level

    @override_settings(GRADE_IN_BACKGROUND=False)
    def test_start_grades_and_is_idempotent(self):
        from tutor.models import MasteryAssessment

        self._submit()
        with mock.patch("tutor.ai.is_configured", return_value=True), \
             mock.patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)) as mocked:
            r1 = self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk))
            self.assertTrue(r1.json()["grading"])            # grade kicked off
            self.assertEqual(MasteryAssessment.objects.count(), 1)   # ran inline (background off)
            r2 = self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk))
            self.assertTrue(r2.json()["ready"])              # already graded → ready, no re-grade
        self.assertEqual(mocked.call_count, 1)               # graded exactly once

    def test_start_reports_grader_off_when_unconfigured(self):
        from tutor.models import MasteryAssessment

        self._submit()
        body = self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk)).json()
        self.assertFalse(body["grading"])                    # no key in tests
        self.assertEqual(MasteryAssessment.objects.count(), 0)

    @override_settings(GRADE_IN_BACKGROUND=False)
    def test_submit_grades_immediately_and_is_never_double_graded(self):
        # Grading now starts at submit (a head start, not dependent on the
        # feedback page's JS firing). The feedback page's start endpoint is
        # idempotent, so re-kicking never produces a second assessment.
        from tutor.models import MasteryAssessment

        with mock.patch("tutor.ai.is_configured", return_value=True), \
             mock.patch("tutor.ai.grade_work", return_value=dict(self.GRADE_RESULT)):
            self._submit()
            self.assertEqual(MasteryAssessment.objects.count(), 1)   # submit kicks the grade
            self.client.post(self._url("portal_feedback_start", set_pk=self.qset.pk))
            self.assertEqual(MasteryAssessment.objects.count(), 1)   # idempotent — not graded twice

    def test_status_scoped_to_own_token(self):
        self._submit()
        stranger = Student.objects.create(
            parent=self.parent, first_name="Nope", grade_level="G03", family=self.family,
        )
        url = reverse("portal:portal_feedback_status",
                      kwargs={"token": make_portal_token(stranger), "set_pk": self.qset.pk})
        # A different child's token can't even see this question set (not placed in it).
        self.assertEqual(self.client.get(url).status_code, 404)


class ParentGateTests(TestCase):
    """Portal → parent dashboard: a password-only re-auth that lands on the dashboard."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="pg", email="pg@e.com", password="s3cret", first_name="Dana",
        )
        cls.family = Family.objects.create(name="Gate Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Rae", grade_level="G03", family=cls.family,
        )
        cls.token = make_portal_token(cls.child)

    def setUp(self):
        cache.clear()  # the brute-force lockout counter lives in the process cache

    def _gate_url(self):
        return reverse("portal:portal_parent_gate", kwargs={"token": self.token})

    def test_gate_prompts_for_password_not_the_login_page(self):
        resp = self.client.get(self._gate_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Parent access")
        self.assertContains(resp, "Dana")            # greets the known parent from the token
        self.assertContains(resp, "password")

    def test_correct_password_signs_in_and_lands_on_dashboard(self):
        resp = self.client.post(self._gate_url(), data={"password": "s3cret"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("dashboard:dashboard"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.parent.pk)

    def test_wrong_password_shows_error_and_stays_signed_out(self):
        resp = self.client.post(self._gate_url(), data={"password": "wrong"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Please try again")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_live_session_skips_the_gate(self):
        self.client.login(username="pg", password="s3cret")
        resp = self.client.get(self._gate_url())
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("dashboard:dashboard"))

    def test_repeated_wrong_passwords_lock_out_brute_force(self):
        for _ in range(8):
            self.client.post(self._gate_url(), data={"password": "wrong"})
        # further attempts are refused — even the correct password, while locked.
        resp = self.client.post(self._gate_url(), data={"password": "wrong"})
        self.assertContains(resp, "Too many tries")
        resp = self.client.post(self._gate_url(), data={"password": "s3cret"})
        self.assertContains(resp, "Too many tries")
        self.assertNotIn("_auth_user_id", self.client.session)


class PortalOutlineAndDeactivateTests(TestCase):
    """HH-148 outline+manga nesting; HH-149 deactivate curriculum/placement."""

    @classmethod
    def setUpTestData(cls):
        from tutor.models import Material

        cls.parent = User.objects.create_user(username="hh148", email="h148@e.com", password="pw")
        cls.family = Family.objects.create(name="HH148 Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family,
        )
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G06", family=cls.family,
        )
        cls.math = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math",
            grade_level="G03", family=cls.family,
        )
        ch = Chapter.objects.create(curriculum=cls.math, number=2, title="Mental Math")
        cls.lesson = Lesson.objects.create(
            chapter=ch, order=8, number=8, title="Sum and Difference",
        )
        cls.manga = Material.objects.create(
            lesson=cls.lesson, title="Chi Sweet Home Math", skill_type="manga",
            status=Material.APPROVED, family=cls.family, child=cls.violet,
        )
        CurriculumPlacement.objects.create(
            child=cls.violet, curriculum=cls.math, current_lesson=cls.lesson,
        )
        cls.beast = Curriculum.objects.create(
            parent=cls.parent, name="Beast Academy", subject="Math", grade_level="G03",
            family=cls.family, is_online=True, website_url="https://beastacademy.com/",
        )
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.beast)
        CurriculumPlacement.objects.create(child=cls.kaylin, curriculum=cls.beast)
        cls.violet_token = make_portal_token(cls.violet)
        cls.kaylin_token = make_portal_token(cls.kaylin)

    def test_subject_nests_manga_under_lesson(self):
        resp = self.client.get(reverse("portal:portal_subject", kwargs={
            "token": self.violet_token, "curriculum_id": self.math.pk,
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Chapter 2")
        self.assertContains(resp, "Sum and Difference")
        self.assertContains(resp, "Chi Sweet Home Math")
        self.assertNotContains(resp, "🦸 Adventures")
        self.assertContains(resp, "portal-lesson-title")
        self.assertContains(resp, "portal-manga-row")

    def test_inactive_placement_hides_from_violet_portal_not_kaylin(self):
        placement = CurriculumPlacement.objects.get(child=self.violet, curriculum=self.beast)
        placement.is_active = False
        placement.save(update_fields=["is_active"])
        v_home = self.client.get(reverse("portal:portal_home", kwargs={"token": self.violet_token}))
        k_home = self.client.get(reverse("portal:portal_home", kwargs={"token": self.kaylin_token}))
        self.assertNotContains(v_home, "Beast Academy")
        self.assertContains(k_home, "Beast Academy")
        resp = self.client.get(reverse("portal:portal_subject", kwargs={
            "token": self.violet_token, "curriculum_id": self.beast.pk,
        }))
        self.assertEqual(resp.status_code, 404)

    def test_inactive_curriculum_hidden_from_list_unless_toggled(self):
        self.client.login(username="hh148", password="pw")
        self.beast.is_active = False
        self.beast.save(update_fields=["is_active"])
        hidden = self.client.get(reverse("curricula:curriculum_list"))
        names = [c.name for c in hidden.context["curricula"]]
        self.assertNotIn("Beast Academy", names)
        self.assertIn("Dimensions Math 3A", names)
        shown = self.client.get(reverse("curricula:curriculum_list") + "?show_deactivated=1")
        shown_names = [c.name for c in shown.context["curricula"]]
        self.assertIn("Beast Academy", shown_names)
        # Switched off but never archived, so it reads as waiting rather than finished.
        self.assertContains(shown, "Ready to start")
        self.assertNotContains(shown, "Archived")


class OnlineSubjectWithInAppLessonsTests(TestCase):
    """An online subject that ALSO has lessons here (HH-155).

    Kaylin's Saxon runs on DIVE — the video, the practice set and the progress
    tracking all live there — but the explainers live in this app. A card that
    jumps straight out to DIVE would leave them permanently unreachable, which is
    exactly what happened before this.
    """

    @classmethod
    def setUpTestData(cls):
        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
        from students.models import Student
        from tutor.models import Material
        cls.Material = Material
        cls.parent = User.objects.create_user("dv", "dv@e.com", "pw")
        cls.family = Family.objects.create(name="DIVE Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.kid = Student.objects.create(parent=cls.parent, first_name="Kaylin",
                                         grade_level="G07", family=cls.family)

        def course(name, **kw):
            cur = Curriculum.objects.create(
                parent=cls.parent, family=cls.family, name=name, subject="Math", **kw)
            ch = Chapter.objects.create(curriculum=cur, number=1, title="C")
            lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L")
            CurriculumPlacement.objects.create(
                child=cls.kid, curriculum=cur, current_lesson=lesson)
            return cur, lesson

        # Purely external — nothing of ours in it.
        cls.beast, _ = course("Beast Academy", is_online=True,
                              website_url="https://beastacademy.com/")
        # External, but we have a lesson for it.
        cls.saxon, saxon_lesson = course("Saxon Pre-Algebra (DIVE)", is_online=True,
                                         website_url="https://diveintomath.com/")
        Material.objects.create(
            lesson=saxon_lesson, title="Nonlinear functions",
            skill_type=Material.SKILL_LESSON, student_content="x",
            status=Material.APPROVED, child=cls.kid, family=cls.family)

    def _home(self):
        from portal.tokens import make_portal_token
        return self.client.get(f"/portal/{make_portal_token(self.kid)}/").content.decode()

    def _cards(self):
        from portal.views import _subject_cards
        return {c["curriculum"].name: c for c in _subject_cards(self.kid)}

    def test_a_purely_external_subject_still_launches_straight_out(self):
        self.assertTrue(self._cards()["Beast Academy"]["launches_out"])
        self.assertIn("https://beastacademy.com/", self._home())

    def test_an_external_subject_with_lessons_opens_the_subject_page_instead(self):
        card = self._cards()["Saxon Pre-Algebra (DIVE)"]
        self.assertFalse(card["launches_out"])
        self.assertTrue(card["curriculum"].is_external)   # still an online subject
        html = self._home()
        self.assertIn(f"/subject/{self.saxon.pk}/", html)

    def test_the_DIVE_button_is_still_on_the_subject_page(self):
        # Losing the launch-out would be worse than the bug it fixes: the video
        # and her progress tracking both live there.
        from portal.tokens import make_portal_token
        html = self.client.get(
            f"/portal/{make_portal_token(self.kid)}/subject/{self.saxon.pk}/"
        ).content.decode()
        self.assertIn("https://diveintomath.com/", html)
        self.assertIn("Nonlinear functions", html)

    def test_a_lesson_built_from_blocks_renders_for_the_child(self):
        from tutor.models import LessonBlock, Material
        from portal.tokens import make_portal_token
        m = Material.objects.get(title="Nonlinear functions")
        LessonBlock.objects.create(material=m, order=1, kind=LessonBlock.KIND_SAY,
                                   data={"text": "Say this out loud."})
        LessonBlock.objects.create(
            material=m, order=2, kind=LessonBlock.KIND_TOOL,
            data={"widget": "grid", "config": {"choices": ["x^2"]}})
        html = self.client.get(
            f"/portal/{make_portal_token(self.kid)}/materials/{m.pk}/"
        ).content.decode()
        self.assertIn("Say this out loud.", html)
        self.assertIn('data-tool="grid"', html)
        # The tool config crosses to JS through json_script, never an attribute.
        self.assertIn('type="application/json"', html)
        # And the plain-text fallback must NOT also render.
        self.assertNotIn("white-space: pre-wrap", html)


class MaterialWorkflowTests(TestCase):
    """The lesson's whole workflow lives on the material page (HH-166): manga math
    gets a kid 'I finished this ✓' that moves the chapter counter, and a mission's
    journal Start button renders INSIDE the mission page."""

    @classmethod
    def setUpTestData(cls):
        from curricula.models import LessonProgress  # noqa: F401  (used in tests)
        from tutor.models import Material

        cls.parent = User.objects.create_user(username="mw", email="mw@e.com", password="pw")
        cls.family = Family.objects.create(name="Workflow Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.token = make_portal_token(cls.violet)

        # Math-shaped: a chapter of two manga-only lessons (no question sets).
        cls.math = Curriculum.objects.create(
            parent=cls.parent, family=cls.family, name="Dimensions Math Test", subject="Math")
        ch = Chapter.objects.create(curriculum=cls.math, number=2, title="Addition")
        cls.math_l1 = Lesson.objects.create(chapter=ch, order=1, number=1, title="Sums")
        cls.math_l2 = Lesson.objects.create(chapter=ch, order=2, number=2, title="Differences")
        cls.manga1 = Material.objects.create(
            lesson=cls.math_l1, title="Chi adds it up", student_content="hi",
            family=cls.family, child=cls.violet, status=Material.APPROVED)
        cls.manga2 = Material.objects.create(
            lesson=cls.math_l2, title="Chi takes away", student_content="hi",
            family=cls.family, child=cls.violet, status=Material.APPROVED)
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.math)

        # Mission-shaped: one lesson carrying a material AND a journal set.
        cls.sci = Curriculum.objects.create(
            parent=cls.parent, family=cls.family, name="Science Test", subject="Science")
        sch = Chapter.objects.create(curriculum=cls.sci, number=1, title="Forces")
        cls.sci_l1 = Lesson.objects.create(chapter=sch, order=1, number=1, title="Push It")
        cls.mission = Material.objects.create(
            lesson=cls.sci_l1, title="Mission 1: Push It, Pull It", student_content="steps",
            family=cls.family, child=cls.violet, status=Material.APPROVED)
        cls.journal = QuestionSet.objects.create(
            lesson=cls.sci_l1, title="Mission 1 · Science Log", family=cls.family,
            child=cls.violet, status=QuestionSet.APPROVED)
        Question.objects.create(
            question_set=cls.journal, order=1, category="application", prompt="3 things")
        CurriculumPlacement.objects.create(child=cls.violet, curriculum=cls.sci)

    def _url(self, name, **kw):
        return reverse(f"portal:{name}", kwargs={"token": self.token, **kw})

    def _subject_html(self, curriculum):
        return self.client.get(
            self._url("portal_subject", curriculum_id=curriculum.pk)).content.decode()

    def test_chapter_counter_counts_marked_manga_lessons(self):
        from curricula.models import LessonProgress

        html = self._subject_html(self.math)
        self.assertIn("0/2", html)                            # nothing done yet
        LessonProgress.objects.create(
            child=self.violet, lesson=self.math_l1,
            status=LessonProgress.COMPLETED, marked_by=self.parent)
        html = self._subject_html(self.math)
        self.assertIn("1/2", html)                            # the mark now counts
        self.assertIn("Finished ✓", html)                     # and the row shows it

    def test_kid_can_mark_a_manga_lesson_done_idempotently(self):
        from curricula.models import LessonProgress

        page = self.client.get(self._url("portal_material", pk=self.manga1.pk))
        self.assertContains(page, "I finished this ✓")
        resp = self.client.post(self._url("portal_material_done", pk=self.manga1.pk))
        self.assertEqual(resp.status_code, 302)
        row = LessonProgress.objects.get(child=self.violet, lesson=self.math_l1)
        self.assertEqual(row.status, LessonProgress.COMPLETED)
        self.assertIsNone(row.marked_by)                      # kid-marked, not parent
        self.assertIn("Violet", row.note)
        # Second tap: still exactly one row, status untouched.
        self.client.post(self._url("portal_material_done", pk=self.manga1.pk))
        self.assertEqual(LessonProgress.objects.filter(
            child=self.violet, lesson=self.math_l1).count(), 1)
        # The page now shows the finished state, not the button.
        page = self.client.get(self._url("portal_material", pk=self.manga1.pk))
        self.assertNotContains(page, "I finished this ✓")
        self.assertContains(page, "Finished ✓")

    def test_mark_done_refused_when_the_lesson_has_a_journal(self):
        from curricula.models import LessonProgress

        page = self.client.get(self._url("portal_material", pk=self.mission.pk))
        self.assertNotContains(page, "I finished this ✓")     # journals are the turn-in
        self.client.post(self._url("portal_material_done", pk=self.mission.pk))
        self.assertFalse(LessonProgress.objects.filter(
            child=self.violet, lesson=self.sci_l1).exists())

    def test_journal_start_button_lives_inside_the_mission_page(self):
        page = self.client.get(self._url("portal_material", pk=self.mission.pk))
        self.assertContains(page, "Show what you know")
        self.assertContains(page, "Start · Mission 1 · Science Log")
        self.assertContains(page, self._url("portal_questions", set_pk=self.journal.pk))
        # Turn it in → the button flips to turned-in. Post against the REAL question
        # pk so the answer actually merges (a bogus key would still submit the sheet
        # and the flip would pass for the wrong reason).
        question = self.journal.questions.first()
        self.client.post(
            self._url("portal_questions", set_pk=self.journal.pk),
            {f"answer_{question.pk}": "I learned about pushes"})
        sheet = ResponseSheet.objects.get(question_set=self.journal, child=self.violet)
        self.assertTrue(sheet.is_submitted)
        self.assertEqual(sheet.answers[str(question.pk)], "I learned about pushes")
        page = self.client.get(self._url("portal_material", pk=self.mission.pk))
        self.assertContains(page, "turned in!")
        self.assertNotContains(page, "Start · Mission 1 · Science Log")

    def test_placement_floor_counts_toward_the_chapter_total(self):
        """The floor (everything before current_lesson) is what makes a chapter jump
        without any explicit mark — and it's how the parent's own checklist reads."""
        placement = CurriculumPlacement.objects.get(child=self.violet, curriculum=self.math)
        placement.current_lesson = self.math_l2
        placement.save()
        html = self._subject_html(self.math)
        self.assertIn("1/2", html)                            # L1 is below the floor
        self.assertIn("Finished ✓", html)

    def test_journal_page_links_back_to_the_mission_instructions(self):
        page = self.client.get(self._url("portal_questions", set_pk=self.journal.pk))
        self.assertContains(page, "Open the mission instructions")
        self.assertContains(page, self._url("portal_material", pk=self.mission.pk))

    def test_continue_button_skips_finished_manga(self):
        from curricula.models import LessonProgress

        html = self._subject_html(self.math)
        self.assertIn("Chi adds it up", html)
        LessonProgress.objects.create(
            child=self.violet, lesson=self.math_l1, status=LessonProgress.COMPLETED)
        resp = self.client.get(self._url("portal_subject", curriculum_id=self.math.pk))
        self.assertEqual(resp.context["next_material"].pk, self.manga2.pk)


class BookletViewerTests(TestCase):
    """The girls can open their own booklet beside their work.

    The whole design turns on one thing: these PDFs are TEACHER editions.
    Violet's Studies Weekly issue carries the marked answer key on pages 8-9
    and the teacher's lesson plans, answers printed inline, on 11-19. So she is
    never served the file — she is served a NEW pdf built from a whitelist. The
    answer key is not withheld by a permission check that could be got around;
    it is not in her file at all.
    """

    @classmethod
    def setUpTestData(cls):
        from core.models import Family, FamilyMembership
        from portal.tokens import make_portal_token

        cls.parent = User.objects.create_user(
            username="bk", email="bk@e.com", password="pw")
        cls.family = Family.objects.create(name="BK Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family,
                                        role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        cls.kaylin = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07",
            family=cls.family)
        cls.vtoken = make_portal_token(cls.violet)
        cls.ktoken = make_portal_token(cls.kaylin)

    # -- a source PDF we control, with a fake "answer key" page --------------

    def _source_pdf(self, pages=6):
        """Six pages. Page 3 is the answer key; 5 and 6 are her articles."""
        import io as _io

        try:
            import pymupdf as fitz
        except ImportError:                                   # pragma: no cover
            import fitz

        doc = fitz.open()
        for n in range(1, pages + 1):
            page = doc.new_page()
            if n == 3:
                page.insert_text((72, 100), "ANSWER KEY the answer is b")
            elif n >= 5:
                page.insert_text((72, 100), "Article page for the child %d" % n)
            else:
                page.insert_text((72, 100), "Teacher pacing notes page %d" % n)
        buf = _io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def _ingest(self, child, name, student_pages="5-6", curriculum=None):
        import os
        import tempfile

        from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson

        if curriculum is None:
            curriculum = Curriculum.objects.create(
                parent=self.parent, name=name, subject="Social Studies",
                grade_level=child.grade_level, family=self.family)
            chapter = Chapter.objects.create(curriculum=curriculum, number=1,
                                             title="Unit 1")
            lesson = Lesson.objects.create(chapter=chapter, number=1, order=1,
                                           title="Week 1")
            CurriculumPlacement.objects.create(
                child=child, curriculum=curriculum, current_lesson=lesson)

        fd, path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, "wb") as fh:
            fh.write(self._source_pdf())
        try:
            call_command("ingest_booklet", "--curriculum", str(curriculum.pk),
                         "--pdf", path, "--title", name + " (teacher edition)",
                         "--student-pages", student_pages,
                         "--student-label", "This week's issue",
                         stdout=StringIO())
        finally:
            os.unlink(path)
        from curricula.models import CurriculumDocument
        return CurriculumDocument.objects.get(curriculum=curriculum)

    def _fetch(self, token, doc):
        return self.client.get(reverse("portal:portal_booklet",
                                       kwargs={"token": token, "pk": doc.pk}))

    @staticmethod
    def _text_of(response):
        try:
            import pymupdf as fitz
        except ImportError:                                   # pragma: no cover
            import fitz

        data = b"".join(response.streaming_content)
        doc = fitz.open(stream=data, filetype="pdf")
        return doc.page_count, " ".join(doc[i].get_text()
                                        for i in range(doc.page_count))

    # -- the point of the whole thing ---------------------------------------

    def test_the_answer_key_is_not_in_the_file_she_is_served(self):
        doc = self._ingest(self.violet, "Violet Weekly")
        pages, text = self._text_of(self._fetch(self.vtoken, doc))

        self.assertEqual(pages, 2)
        self.assertIn("Article page for the child", text)
        self.assertNotIn("ANSWER KEY", text)
        self.assertNotIn("the answer is b", text)
        self.assertNotIn("Teacher pacing notes", text)

    def test_the_teacher_edition_itself_is_kept_and_kept_separate(self):
        """The parent still needs the whole thing — it just is not what any
        portal URL serves."""
        doc = self._ingest(self.violet, "Violet Weekly")
        self.assertTrue(doc.file)
        self.assertNotEqual(doc.file.name, doc.student_file.name)
        with doc.file.open("rb") as fh:
            try:
                import pymupdf as fitz
            except ImportError:                               # pragma: no cover
                import fitz
            full = fitz.open(stream=fh.read(), filetype="pdf")
        self.assertEqual(full.page_count, 6)
        self.assertIn("ANSWER KEY",
                      " ".join(full[i].get_text() for i in range(6)))

    def test_a_document_with_no_whitelist_is_offered_to_nobody(self):
        """Fail-closed. A document nobody has vetted must not become readable
        just because it exists."""
        doc = self._ingest(self.violet, "Violet Weekly")
        doc.student_pages = ""
        doc.save(update_fields=["student_pages"])
        self.assertFalse(doc.child_visible)
        self.assertEqual(self._fetch(self.vtoken, doc).status_code, 404)

        doc.student_pages = "5-6"
        doc.student_file = ""
        doc.save(update_fields=["student_pages", "student_file"])
        self.assertFalse(doc.child_visible)
        self.assertEqual(self._fetch(self.vtoken, doc).status_code, 404)

    def test_one_child_cannot_open_another_child_s_booklet(self):
        vdoc = self._ingest(self.violet, "Violet Weekly")
        kdoc = self._ingest(self.kaylin, "Kaylin Weekly")

        self.assertEqual(self._fetch(self.vtoken, vdoc).status_code, 200)
        self.assertEqual(self._fetch(self.ktoken, kdoc).status_code, 200)
        self.assertEqual(self._fetch(self.ktoken, vdoc).status_code, 404)
        self.assertEqual(self._fetch(self.vtoken, kdoc).status_code, 404)

    def test_a_shelved_curriculum_takes_its_booklet_with_it(self):
        """Access follows the ACTIVE placement, not a link she once had."""
        from curricula.models import CurriculumPlacement

        doc = self._ingest(self.violet, "Violet Weekly")
        self.assertEqual(self._fetch(self.vtoken, doc).status_code, 200)
        CurriculumPlacement.objects.filter(
            child=self.violet, curriculum=doc.curriculum).update(is_active=False)
        self.assertEqual(self._fetch(self.vtoken, doc).status_code, 404)

    def test_a_bad_token_gets_nothing(self):
        doc = self._ingest(self.violet, "Violet Weekly")
        self.assertEqual(
            self.client.get(reverse("portal:portal_booklet",
                                    kwargs={"token": "not-a-token",
                                            "pk": doc.pk})).status_code, 404)

    # -- how a browser is told to show it ------------------------------------

    def test_it_is_served_so_a_browser_will_show_it_in_the_page(self):
        """Three headers decide whether the panel works at all. The site sends
        X-Frame-Options: DENY by default, which blocks Django's own response
        from being framed by Django's own page — the panel just opens blank,
        with nothing in the console to say why."""
        doc = self._ingest(self.violet, "Violet Weekly")
        r = self._fetch(self.vtoken, doc)
        self.assertEqual(r["Content-Type"], "application/pdf")
        self.assertEqual(r["X-Frame-Options"], "SAMEORIGIN")
        self.assertIn("inline", r["Content-Disposition"])
        self.assertTrue(b"".join(r.streaming_content).startswith(b"%PDF-"))

    # -- the panel on her page ----------------------------------------------

    def test_the_panel_appears_beside_the_work_with_a_way_out(self):
        from tutor.models import QuestionSet

        doc = self._ingest(self.violet, "Violet Weekly")
        lesson = doc.curriculum.chapters.first().lessons.first()
        qset = QuestionSet.objects.create(
            lesson=lesson, title="Week 1 check", family=self.family,
            status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)

        html = self.client.get(reverse(
            "portal:portal_questions",
            kwargs={"token": self.vtoken, "set_pk": qset.pk})).content.decode()
        self.assertIn("booklet-frame", html)
        self.assertIn("This week&#x27;s issue", html)
        self.assertIn(reverse("portal:portal_booklet",
                              kwargs={"token": self.vtoken, "pk": doc.pk}), html)
        # Closed until she asks for it — an open PDF would push the questions
        # off a tablet screen. Asserted on the tag the template really renders:
        # matching a literal '<details class="booklet" open' could not appear
        # whatever the state, because the tag carries other attributes.
        panel = html.split("<details", 1)[1].split(">", 1)[0]
        self.assertIn('class="booklet"', panel)
        self.assertNotIn("open", panel)
        # And the way out is present for a browser with no PDF reader.
        self.assertIn("if the page below stays empty", html)

    def test_the_panel_is_on_the_reading_page_too(self):
        """Both halves of a lesson: she reads the material, then answers. The
        booklet has to be on whichever one she is looking at."""
        from tutor.models import Material

        doc = self._ingest(self.violet, "Violet Weekly")
        lesson = doc.curriculum.chapters.first().lessons.first()
        material = Material.objects.create(
            lesson=lesson, child=self.violet, family=self.family,
            title="The issue", student_content="", status=Material.APPROVED)

        html = self.client.get(reverse(
            "portal:portal_material",
            kwargs={"token": self.vtoken, "pk": material.pk})).content.decode()
        self.assertIn("booklet-frame", html)
        self.assertIn(reverse("portal:portal_booklet",
                              kwargs={"token": self.vtoken, "pk": doc.pk}), html)

    def test_a_shelved_curriculum_takes_its_booklet_with_it_too(self):
        """The placement can be active while the CURRICULUM has been retired.
        Both gates matter; only the placement one was covered."""
        doc = self._ingest(self.violet, "Violet Weekly")
        self.assertEqual(self._fetch(self.vtoken, doc).status_code, 200)
        doc.curriculum.is_active = False
        doc.curriculum.save(update_fields=["is_active"])
        self.assertEqual(self._fetch(self.vtoken, doc).status_code, 404)

    def test_a_row_whose_file_has_gone_is_a_missing_booklet_not_a_crash(self):
        """A cleared bucket or a half-finished ingest must not 500 the page she
        is trying to do her work on."""
        doc = self._ingest(self.violet, "Violet Weekly")
        doc.student_file.storage.delete(doc.student_file.name)
        self.assertEqual(self._fetch(self.vtoken, doc).status_code, 404)

    def test_re_extracting_an_uploaded_document_replaces_it_in_place(self):
        """How this is done on production: the parent uploads through their own
        form, and the extraction runs server-side against the row. Keyed on the
        row, so narrowing a range that turned out too wide REPLACES the booklet
        rather than leaving the wide one beside it."""
        from curricula.models import CurriculumDocument

        doc = self._ingest(self.violet, "Violet Weekly", student_pages="1-6")
        _, wide = self._text_of(self._fetch(self.vtoken, doc))
        self.assertIn("ANSWER KEY", wide)          # too wide, as uploaded

        call_command("ingest_booklet", "--doc", str(doc.pk),
                     "--student-pages", "5-6", stdout=StringIO())

        self.assertEqual(
            CurriculumDocument.objects.filter(curriculum=doc.curriculum).count(),
            1, "a correction must not leave the wide one beside it")
        pages, text = self._text_of(self._fetch(self.vtoken, doc))
        self.assertEqual(pages, 2)
        self.assertNotIn("ANSWER KEY", text)
        doc.refresh_from_db()
        self.assertEqual(doc.student_pages, "5-6")
        self.assertTrue(doc.file, "the teacher edition is still there for a parent")

    def test_extracting_from_a_document_with_no_file_is_refused(self):
        from django.core.management.base import CommandError

        from curricula.models import CurriculumDocument

        doc = self._ingest(self.violet, "Violet Weekly")
        doc.file = ""
        doc.save(update_fields=["file"])
        with self.assertRaises(CommandError) as caught:
            call_command("ingest_booklet", "--doc", str(doc.pk),
                         "--student-pages", "5-6", stdout=StringIO())
        self.assertIn("no file", str(caught.exception))

    def test_a_correction_filed_under_a_new_title_is_shouted_about(self):
        """update_or_create keys on (curriculum, title), so a correction typed
        with a different title ADDS a booklet instead of replacing one — and
        she is then offered both, including the wide one somebody had already
        noticed was wrong. It is the only realistic route back to the answer
        key, so the command has to say so."""
        first = self._ingest(self.violet, "Violet Weekly", student_pages="1-6")
        out = StringIO()
        from curricula.models import Curriculum
        import os
        import tempfile

        fd, path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, "wb") as fh:
            fh.write(self._source_pdf())
        try:
            call_command("ingest_booklet",
                         "--curriculum", str(first.curriculum.pk),
                         "--pdf", path, "--title", "Violet Weekly CORRECTED",
                         "--student-pages", "5-6", stdout=out)
        finally:
            os.unlink(path)
        message = out.getvalue()
        self.assertIn("WARNING", message)
        self.assertIn("already offers", message)
        self.assertIn("1-6", message, "it names the one still reachable")

    # -- the whitelist parser ------------------------------------------------

    def test_a_page_spec_that_cannot_be_read_is_refused_not_guessed(self):
        """A misread spec is the difference between four article pages and the
        answer key, so it must never fall back to a default."""
        from curricula.models import CurriculumDocument as D

        self.assertEqual(D.parse_pages("23-26"), [23, 24, 25, 26])
        self.assertEqual(D.parse_pages("5, 3, 5"), [5, 3])   # order kept, deduped
        self.assertEqual(D.parse_pages("1-2,9"), [1, 2, 9])
        for bad in ("", "   ", "abc", "3-", "-", "9-2", "0", "-4", "2-x", ","):
            with self.assertRaises(ValueError, msg=bad):
                D.parse_pages(bad)
        with self.assertRaises(ValueError):
            D.parse_pages("1-9", page_count=4)               # past the end

    def test_the_command_refuses_a_spec_past_the_end_of_the_file(self):
        from django.core.management.base import CommandError

        with self.assertRaises(CommandError) as caught:
            self._ingest(self.violet, "Violet Weekly", student_pages="5-99")
        self.assertIn("only 6", str(caught.exception))


class HundredDressesSeedTests(TestCase):
    """Violet's Blackbird guide for The Hundred Dresses.

    Transcribed from the family's purchased Level 3 guide. What these pin is the
    transcription: a vocabulary number that drifts, or a word missing from a
    bank, tells a nine-year-old her right answer is wrong.
    """

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(
            username="hd", email="hd@e.com", password="pw")
        cls.family = Family.objects.create(name="HD Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family,
                                        role="parent")
        cls.violet = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03",
            family=cls.family)
        call_command("seed_the_hundred_dresses", "--for-user", "hd",
                     stdout=StringIO())
        cls.curriculum = Curriculum.objects.get(
            name__contains="Hundred Dresses")

    def _set(self, title):
        return QuestionSet.objects.get(
            lesson__chapter__curriculum=self.curriculum, title=title)

    # -- the guide's own shape ----------------------------------------------

    def test_the_course_is_the_guide_s_five_week_shape(self):
        """Four reading sections plus a final project — Read, Journal, Acquire,
        Recollect, Explore."""
        guide_sections = self.curriculum.chapters.filter(number__lte=5)
        self.assertEqual(guide_sections.count(), 5)
        self.assertEqual(self.curriculum.grade_level, "G03")
        for n in range(1, 5):
            for part in ("Journal", "Vocabulary", "Comprehension", "Writing",
                         "Discussion"):
                self._set(f"Section {n} · {part}")     # raises if missing
        self._set("Section 5 · Glean: Final Project")

    def test_the_sections_are_named_the_way_the_guide_names_them(self):
        """This guide divides the book by where the story gets to, not by
        chapter number. Calling section 1 "Chapters Wanda—The Dresses Game"
        would be nonsense on her page."""
        titles = [c.title for c in
                  self.curriculum.chapters.filter(number__lte=5).order_by("number")]
        self.assertIn("Section 1: Wanda—The Dresses Game", titles)
        self.assertIn("Section 4: The Letter to Room 13", titles)
        for title in titles:
            self.assertNotIn("Chapters None", title)

    # -- the transcription ---------------------------------------------------

    def test_every_vocabulary_word_can_be_matched_and_used(self):
        """A word in the bank with no definition — or a definition whose word is
        not in the bank — is a question she cannot finish."""
        from tutor.hundred_dresses import SECTIONS

        for section in SECTIONS:
            words = set(section["matching"]["words"])
            defined = {word for _n, _text, word in section["matching"]["definitions"]}
            self.assertEqual(words, defined, f"section {section['number']}")

            numbers = sorted(n for n, _t, _w in section["matching"]["definitions"])
            self.assertEqual(numbers, [1, 2, 3, 4, 5, 6],
                             f"section {section['number']} numbering")

            used = [word for _text, word in section["fill_blank"]]
            self.assertEqual(sorted(used), sorted(words),
                             f"section {section['number']}: each word once")

    def test_every_blank_is_actually_blank(self):
        """A sentence that lost its ______ is one she cannot answer."""
        from tutor.hundred_dresses import SECTIONS

        for section in SECTIONS:
            for text, word in section["fill_blank"]:
                self.assertIn("______", text, f"{word}: no blank to fill")

    def test_the_matching_exercise_marks_itself(self):
        """Six words a week across four weeks is not something a parent should
        be checking by hand."""
        import json

        qset = self._set("Section 1 · Vocabulary")
        question = qset.questions.get(order=1)
        right = {d["word"]: d["n"] for d in question.vocab_data["definitions"]}

        sheet = ResponseSheet(question_set=qset)
        sheet.answers = {str(question.pk): json.dumps({"matches": right, "tries": 6})}
        shown = sheet.answer_display(question)
        self.assertIn("scuffling", shown)
        self.assertIn("a noisy shuffling of feet", shown)

    def test_the_comprehension_key_is_teacher_only_and_present(self):
        """Suggested answers, never shown to the child."""
        for n in range(1, 5):
            key = self._set(f"Section {n} · Comprehension").answer_key
            self.assertIn("teacher reference only", key)
            self.assertTrue(key.strip())
        resource = CurriculumResource.objects.get(
            curriculum=self.curriculum,
            resource_type=CurriculumResource.ANSWER_KEY)
        self.assertTrue(resource.teacher_only)
        self.assertIn("blackbirdandcompany.com", resource.url)

    def test_the_guide_s_printed_slips_are_kept_not_tidied(self):
        """Three of them. A child copying from a page that reads one way and a
        screen that reads another is a small avoidable confusion, and reviewers
        keep flagging these as mine."""
        from tutor.hundred_dresses import SECTIONS

        sentences = {text for s in SECTIONS for text, _w in s["fill_blank"]}
        self.assertTrue(any("in the Forrest" in t for t in sentences))
        self.assertTrue(any("when I'm talk to my tutor" in t for t in sentences))
        self.assertTrue(any(t.rstrip().endswith("toys?") for t in sentences))

    # -- what she opens ------------------------------------------------------

    def test_the_journal_gives_a_box_per_character_the_guide_names(self):
        """Section 3 journals three people, section 1 only two."""
        first = self._set("Section 1 · Journal").questions.get(order=1)
        third = self._set("Section 3 · Journal").questions.get(order=1)
        self.assertEqual(first.character_names, ["Peggy", "Wanda"])
        self.assertEqual(third.character_names,
                         ["Miss Mason", "Peggy", "Old Man Svenson"])

    def test_the_writing_prompt_is_the_guide_s_own(self):
        writing = self._set("Section 2 · Writing").questions.get(order=1)
        self.assertIn("teasing", writing.prompt)
        self.assertEqual(writing.response_type, Question.TYPE_PARAGRAPH)

    def test_the_discussion_sets_are_teacher_led_not_turned_in(self):
        """Discussion is spoken. Rendering it as work to submit would turn the
        best part of the week into a worksheet."""
        for n in range(1, 5):
            self.assertEqual(self._set(f"Section {n} · Discussion").mode,
                             QuestionSet.MODE_DISCUSSION)

    def test_the_glean_lists_all_six_of_the_guide_s_options(self):
        from tutor.hundred_dresses import GLEAN_OPTIONS

        intro = self._set("Section 5 · Glean: Final Project").intro
        self.assertEqual(len(GLEAN_OPTIONS), 6)
        for option in GLEAN_OPTIONS:
            self.assertIn(option[:40], intro)

    def test_the_glean_note_points_at_the_hands_on_option(self):
        """This guide's Glean is already hands-on, so it needs no no-writing
        alternative added beside it the way A Mouse Called Wolf did."""
        rubric = self._set("Section 5 · Glean: Final Project").rubric
        self.assertIn("already hands-on", rubric)
        self.assertIn("Option 3", rubric)

    def test_reseeding_changes_nothing(self):
        before = (QuestionSet.objects.count(), Question.objects.count())
        call_command("seed_the_hundred_dresses", "--for-user", "hd",
                     stdout=StringIO())
        self.assertEqual(
            (QuestionSet.objects.count(), Question.objects.count()), before)

    def test_a_missing_child_is_refused(self):
        from django.core.management.base import CommandError

        with self.assertRaises(CommandError):
            call_command("seed_the_hundred_dresses", "--for-user", "hd",
                         "--child-name", "Nobody", stdout=StringIO())


# ---- HH-199: photographed answers ------------------------------------------

import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class AnswerPhotoTests(TestCase):
    """HH-199: a step whose answer is a thing she MADE.

    Answers live in a JSONField, which can hold a drawing's strokes but not a
    file — so a project built around making needed its own substrate."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="ph", email="ph@e.com", password="pw")
        cls.family = Family.objects.create(name="PH Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)
        cls.sibling = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Blackbird", subject="Reading", family=cls.family)
        chapter = Chapter.objects.create(curriculum=cls.curriculum, number=1, title="C")
        cls.lesson = Lesson.objects.create(chapter=chapter, order=1, number=1, title="L")
        # A shared set (child=None) is only visible to a child PLACED in the
        # curriculum, and both girls read the same Blackbird guide.
        for kid in (cls.child, cls.sibling):
            CurriculumPlacement.objects.create(
                child=kid, curriculum=cls.curriculum, current_lesson=cls.lesson,
                is_active=True)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Glean", family=cls.family,
            status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)
        cls.photo_q = Question.objects.create(
            question_set=cls.qset, order=1, category="application",
            prompt="Build the bundle.", response_type=Question.TYPE_PHOTO)
        cls.text_q = Question.objects.create(
            question_set=cls.qset, order=2, category="writing",
            prompt="A sentence.", response_type=Question.TYPE_TEXT)

    def setUp(self):
        self.token = make_portal_token(self.child)

    @staticmethod
    def _jpg(name="made.jpg", size=32):
        return SimpleUploadedFile(name, b"\xff\xd8\xff" + b"x" * size,
                                  content_type="image/jpeg")

    def _url(self, q=None):
        return reverse("portal:portal_answer_photo", kwargs={
            "token": self.token, "set_pk": self.qset.pk,
            "question_pk": (q or self.photo_q).pk})

    def _rm_url(self, q=None):
        return reverse("portal:portal_answer_photo_remove", kwargs={
            "token": self.token, "set_pk": self.qset.pk,
            "question_pk": (q or self.photo_q).pk})

    def test_a_photo_is_filed_against_that_step(self):
        r = Client().post(self._url(), {"photo": self._jpg()})
        self.assertEqual(r.status_code, 302)
        photo = AnswerPhoto.objects.get()
        self.assertEqual(photo.question, self.photo_q)
        self.assertEqual(photo.sheet.child, self.child)
        self.assertTrue(photo.image.name.startswith("answer_photos/"))

    def test_more_than_one_photo_per_step(self):
        """The front and the back of a dust jacket are two photographs. One slot
        per step would flatten a made object into a single shot."""
        c = Client()
        c.post(self._url(), {"photo": self._jpg("front.jpg")})
        c.post(self._url(), {"photo": self._jpg("back.jpg")})
        self.assertEqual(AnswerPhoto.objects.count(), 2)

    def test_a_step_that_does_not_take_photos_refuses_one(self):
        r = Client().post(self._url(self.text_q), {"photo": self._jpg()})
        self.assertEqual(r.status_code, 404)
        self.assertFalse(AnswerPhoto.objects.exists())

    def test_a_pdf_is_refused(self):
        r = Client().post(self._url(), {
            "photo": SimpleUploadedFile("x.pdf", b"%PDF", content_type="application/pdf")})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(AnswerPhoto.objects.exists())

    def test_an_oversized_photo_is_refused(self):
        big = self._jpg("huge.jpg", size=AnswerPhoto.PHOTO_MAX_BYTES + 1)
        r = Client().post(self._url(), {"photo": big})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(AnswerPhoto.objects.exists())

    def test_there_is_a_ceiling_on_photos_per_step(self):
        c = Client()
        for i in range(AnswerPhoto.MAX_PER_QUESTION + 2):
            c.post(self._url(), {"photo": self._jpg("p%d.jpg" % i)})
        self.assertEqual(AnswerPhoto.objects.count(), AnswerPhoto.MAX_PER_QUESTION)

    def test_a_turned_in_sheet_takes_no_more_photos(self):
        c = Client()
        c.post(self._url(), {"photo": self._jpg()})
        sheet = ResponseSheet.objects.get()
        sheet.status = ResponseSheet.SUBMITTED
        sheet.save()
        c.post(self._url(), {"photo": self._jpg("late.jpg")})
        self.assertEqual(AnswerPhoto.objects.count(), 1)

    def test_remove_deletes_the_row_and_the_file(self):
        import os

        c = Client()
        c.post(self._url(), {"photo": self._jpg()})
        photo = AnswerPhoto.objects.get()
        path = photo.image.path
        self.assertTrue(os.path.exists(path))
        r = c.post(self._rm_url(), {"photo": photo.pk})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(AnswerPhoto.objects.filter(pk=photo.pk).exists())
        self.assertFalse(os.path.exists(path))

    def test_remove_refuses_a_siblings_photo_on_the_same_shared_question(self):
        """The question set is shared between the girls. A guessed id must not
        reach the other child's sheet."""
        Client().post(self._url(), {"photo": self._jpg()})
        hers = AnswerPhoto.objects.get()

        # Give the sibling a sheet of her own FIRST, so this exercises the real
        # scoping filter rather than the has-no-sheet short circuit.
        sib_token = make_portal_token(self.sibling)
        sib_add = reverse("portal:portal_answer_photo", kwargs={
            "token": sib_token, "set_pk": self.qset.pk, "question_pk": self.photo_q.pk})
        Client().post(sib_add, {"photo": self._jpg("sib.jpg")})
        self.assertEqual(AnswerPhoto.objects.count(), 2)

        sib_rm = reverse("portal:portal_answer_photo_remove", kwargs={
            "token": sib_token, "set_pk": self.qset.pk, "question_pk": self.photo_q.pk})
        r = Client().post(sib_rm, {"photo": hers.pk})
        self.assertEqual(r.status_code, 404)
        self.assertTrue(AnswerPhoto.objects.filter(pk=hers.pk).exists())

    def test_a_junk_photo_id_404s_rather_than_500s(self):
        Client().post(self._url(), {"photo": self._jpg()})
        self.assertEqual(
            Client().post(self._rm_url(), {"photo": "abc"}).status_code, 404)

    def test_a_photographed_step_counts_as_answered(self):
        """This number renders as 'N of M answered' directly above a Turn-it-in
        button she cannot undo, and photos live outside the answers JSON."""
        Client().post(self._url(), {"photo": self._jpg()})
        sheet = ResponseSheet.objects.get()
        self.assertEqual(sheet.answered_count, 1)

    def test_answered_count_does_not_double_count_a_photo_step(self):
        Client().post(self._url(), {"photo": self._jpg()})
        sheet = ResponseSheet.objects.get()
        sheet.answers = {str(self.photo_q.pk): "something"}
        sheet.save()
        self.assertEqual(sheet.answered_count, 1)

    def test_the_display_says_how_many_she_made(self):
        c = Client()
        sheet = ResponseSheet.objects.create(question_set=self.qset, child=self.child)
        self.assertIn("nothing photographed", sheet.answer_display(self.photo_q))
        c.post(self._url(), {"photo": self._jpg()})
        sheet.refresh_from_db()
        self.assertIn("1 photo", sheet.answer_display(self.photo_q))

    def test_heic_is_stored_but_never_rendered_as_an_image(self):
        """No browser draws HEIC. An <img> would be a broken icon in the middle
        of the printed charter report."""
        Client().post(self._url(), {
            "photo": SimpleUploadedFile("p.heic", b"ftypheic", content_type="image/heic")})
        photo = AnswerPhoto.objects.get()
        self.assertTrue(photo.image)
        self.assertFalse(photo.is_viewable)

    def test_the_portal_page_shows_her_photos_and_an_add_control(self):
        Client().post(self._url(), {"photo": self._jpg()})
        html = Client().get(reverse("portal:portal_questions", kwargs={
            "token": self.token, "set_pk": self.qset.pk})).content.decode()
        self.assertIn("photo-widget", html)
        self.assertIn('id="photo-add-%d"' % self.photo_q.pk, html)   # the out-of-form form
        self.assertIn('form="photo-add-%d"' % self.photo_q.pk, html)  # the control reaching it
        self.assertIn("answer_photos/", html)                         # the photo itself

    def test_the_upload_form_is_not_nested_inside_the_answers_form(self):
        """Nested forms are illegal and the browser drops the inner one, so the
        upload would silently post the answers form instead."""
        html = Client().get(reverse("portal:portal_questions", kwargs={
            "token": self.token, "set_pk": self.qset.pk})).content.decode()
        widget = html.split('class="photo-widget"')[1].split("</div>")[0]
        self.assertNotIn("<form", widget)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DrawOrPhotographTests(TestCase):
    """A drawing step can opt into paper: draw it on the tablet, OR draw it on
    real paper and photograph it. A comic page is very often better on paper,
    and every hands-on project's intro already promised she could photograph
    each piece — the drawing steps just could not accept one."""

    @classmethod
    def setUpTestData(cls):
        cls.parent = User.objects.create_user(username="dp", email="dp@e.com", password="pw")
        cls.family = Family.objects.create(name="DP Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Blackbird", subject="Reading", family=cls.family)
        chapter = Chapter.objects.create(curriculum=cls.curriculum, number=1, title="C")
        cls.lesson = Lesson.objects.create(chapter=chapter, order=1, number=1, title="L")
        CurriculumPlacement.objects.create(
            child=cls.child, curriculum=cls.curriculum,
            current_lesson=cls.lesson, is_active=True)
        cls.qset = QuestionSet.objects.create(
            lesson=cls.lesson, title="Glean", family=cls.family,
            status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)
        cls.comic = Question.objects.create(
            question_set=cls.qset, order=1, category="application",
            prompt="One chapter, six panels.",
            response_type=Question.TYPE_DRAWING,
            passage=json.dumps({"height": 620, "allow_photo": True}))
        cls.screen_only = Question.objects.create(
            question_set=cls.qset, order=2, category="application",
            prompt="Draw it here.",
            response_type=Question.TYPE_DRAWING,
            passage=json.dumps({"height": 400}))

    def setUp(self):
        self.token = make_portal_token(self.child)

    @staticmethod
    def _jpg(name="comic.jpg"):
        return SimpleUploadedFile(name, b"\xff\xd8\xff" + b"x" * 32,
                                  content_type="image/jpeg")

    def _url(self, q):
        return reverse("portal:portal_answer_photo", kwargs={
            "token": self.token, "set_pk": self.qset.pk, "question_pk": q.pk})

    def test_a_drawing_step_that_opted_in_accepts_a_photo(self):
        r = Client().post(self._url(self.comic), {"photo": self._jpg()})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(AnswerPhoto.objects.get().question, self.comic)

    def test_a_drawing_step_that_did_not_opt_in_still_refuses_one(self):
        """Only steps that say so take paper. Otherwise every drawing question
        in the app silently grows an upload box."""
        r = Client().post(self._url(self.screen_only), {"photo": self._jpg()})
        self.assertEqual(r.status_code, 404)
        self.assertFalse(AnswerPhoto.objects.exists())

    def test_accepts_photo_is_the_flag_not_the_response_type(self):
        self.assertTrue(self.comic.accepts_photo)
        self.assertFalse(self.screen_only.accepts_photo)
        self.assertTrue(self.comic.is_drawing)      # still a drawing step

    def test_the_page_offers_the_canvas_AND_the_camera_on_that_step(self):
        html = Client().get(reverse("portal:portal_questions", kwargs={
            "token": self.token, "set_pk": self.qset.pk})).content.decode()
        self.assertIn("drawing-widget", html)                       # the canvas
        self.assertIn('id="photo-add-%d"' % self.comic.pk, html)    # and the camera
        self.assertIn("Done it on paper?", html)
        # ...but not on the step that never opted in.
        self.assertNotIn('id="photo-add-%d"' % self.screen_only.pk, html)

    def test_a_photo_answers_the_step_even_with_an_empty_canvas(self):
        """She drew it on paper, so the canvas is blank. The count above the
        Turn-it-in button has to know that step is done."""
        Client().post(self._url(self.comic), {"photo": self._jpg()})
        sheet = ResponseSheet.objects.get()
        self.assertEqual(sheet.answered_count, 1)

    def test_the_parent_sees_the_photographed_comic_in_the_review(self):
        from tutor.views import _assessed_work
        from worklog.models import WorkLogEntry
        from tutor.models import MasteryAssessment

        Client().post(self._url(self.comic), {"photo": self._jpg()})
        sheet = ResponseSheet.objects.get()
        entry = WorkLogEntry.objects.create(
            child=self.child, family=self.family, parent=self.parent,
            date=date(2026, 8, 26), subject="Reading", description="Glean")
        sheet.work_entry = entry
        sheet.save()
        assessment = MasteryAssessment.objects.create(
            work_entry=entry, rubric="r", answers="a")
        rows = _assessed_work(assessment)["rows"]
        comic_row = [r for r in rows if r["question"].pk == self.comic.pk][0]
        self.assertTrue(comic_row["photos"])
        self.assertTrue(comic_row["answered"])


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PortalLessonWorkTests(TestCase):
    """HH-200: she photographs her maths from the lesson itself.

    A manga maths lesson has no turn-in work on screen, so the portal could say
    "I finished this" and had nowhere for the page she actually worked. The
    upload existed but only on the parent's lesson checklist — not where anybody
    is standing when they finish a lesson.
    """

    @classmethod
    def setUpTestData(cls):
        from curricula.models import LessonWork  # noqa: F401
        from tutor.models import Material

        cls.parent = User.objects.create_user(username="pw2", email="pw2@e.com", password="pw")
        cls.family = Family.objects.create(name="PW Fam")
        FamilyMembership.objects.create(user=cls.parent, family=cls.family, role="parent")
        cls.child = Student.objects.create(
            parent=cls.parent, first_name="Violet", grade_level="G03", family=cls.family)
        cls.sibling = Student.objects.create(
            parent=cls.parent, first_name="Kaylin", grade_level="G07", family=cls.family)
        cls.curriculum = Curriculum.objects.create(
            parent=cls.parent, name="Dimensions Math 3A", subject="Math", family=cls.family)
        chapter = Chapter.objects.create(curriculum=cls.curriculum, number=1, title="C")
        cls.lesson = Lesson.objects.create(chapter=chapter, order=1, number=1, title="L")
        for kid in (cls.child, cls.sibling):
            CurriculumPlacement.objects.create(
                child=kid, curriculum=cls.curriculum,
                current_lesson=cls.lesson, is_active=True)
        cls.material = Material.objects.create(
            lesson=cls.lesson, title="Chapter 1 manga",
            student_content="Read the manga, then do the page.",
            family=cls.family, status=Material.APPROVED)

    def setUp(self):
        self.token = make_portal_token(self.child)

    @staticmethod
    def _jpg(name="page.jpg", size=32):
        return SimpleUploadedFile(name, b"\xff\xd8\xff" + b"x" * size,
                                  content_type="image/jpeg")

    def _url(self):
        return reverse("portal:portal_material_work",
                       kwargs={"token": self.token, "pk": self.material.pk})

    def _rm_url(self, token=None):
        return reverse("portal:portal_material_work_remove",
                       kwargs={"token": token or self.token, "pk": self.material.pk})

    def test_she_can_photograph_her_work_from_the_lesson(self):
        from curricula.models import LessonWork

        r = Client().post(self._url(), {"work": self._jpg()})
        self.assertEqual(r.status_code, 302)
        work = LessonWork.objects.get()
        self.assertEqual(work.lesson, self.lesson)
        self.assertEqual(work.child, self.child)
        self.assertEqual(work.family, self.family)
        self.assertIsNone(work.uploaded_by)     # token-authed; no user behind it

    def test_it_lands_where_the_parents_checklist_looks(self):
        """One home, two doors. If these wrote to different places, a parent
        would tick a lesson while looking at an empty page."""
        from curricula.models import LessonWork

        Client().post(self._url(), {"work": self._jpg()})
        c = Client()
        c.login(username="pw2", password="pw")
        html = c.get(reverse("students:lesson_work", kwargs={
            "pk": self.child.pk, "curriculum_id": self.curriculum.pk,
            "lesson_id": self.lesson.pk})).content.decode()
        self.assertIn(LessonWork.objects.get().filename, html)

    def test_the_lesson_page_offers_the_camera_when_there_is_nothing_to_fill_in(self):
        html = Client().get(reverse("portal:portal_material", kwargs={
            "token": self.token, "pk": self.material.pk})).content.decode()
        self.assertIn("Add my work", html)
        self.assertIn("Your work for this lesson", html)

    def test_a_lesson_with_turn_in_work_does_not_offer_it(self):
        """Where there IS something to fill in, the answers are the work and a
        second upload box is just clutter."""
        qs = QuestionSet.objects.create(
            lesson=self.lesson, title="Journal", family=self.family,
            status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)
        Question.objects.create(question_set=qs, order=1, category="writing",
                                prompt="Write.", response_type=Question.TYPE_TEXT)
        html = Client().get(reverse("portal:portal_material", kwargs={
            "token": self.token, "pk": self.material.pk})).content.decode()
        self.assertNotIn("Add my work", html)

    def test_her_photos_show_and_the_siblings_do_not(self):
        sib_token = make_portal_token(self.sibling)
        sib_url = reverse("portal:portal_material_work",
                          kwargs={"token": sib_token, "pk": self.material.pk})
        Client().post(self._url(), {"work": self._jpg("violet.jpg")})
        Client().post(sib_url, {"work": self._jpg("kaylin.jpg")})
        html = Client().get(reverse("portal:portal_material", kwargs={
            "token": self.token, "pk": self.material.pk})).content.decode()
        self.assertIn("violet", html)
        self.assertNotIn("kaylin", html)

    def test_remove_refuses_a_siblings_photo_on_the_same_lesson(self):
        from curricula.models import LessonWork

        Client().post(self._url(), {"work": self._jpg("violet.jpg")})
        hers = LessonWork.objects.get()
        sib_token = make_portal_token(self.sibling)
        r = Client().post(self._rm_url(sib_token), {"work": hers.pk})
        self.assertEqual(r.status_code, 404)
        self.assertTrue(LessonWork.objects.filter(pk=hers.pk).exists())

    def test_remove_deletes_the_row_and_the_file(self):
        import os

        from curricula.models import LessonWork

        Client().post(self._url(), {"work": self._jpg()})
        work = LessonWork.objects.get()
        path = work.file.path
        Client().post(self._rm_url(), {"work": work.pk})
        self.assertFalse(LessonWork.objects.filter(pk=work.pk).exists())
        self.assertFalse(os.path.exists(path))

    def test_an_executable_is_refused(self):
        from curricula.models import LessonWork

        r = Client().post(self._url(), {
            "work": SimpleUploadedFile("x.exe", b"MZ",
                                       content_type="application/octet-stream")})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(LessonWork.objects.exists())

    def test_there_is_a_ceiling_on_photos_per_lesson(self):
        from curricula.models import LessonWork

        c = Client()
        for i in range(LessonWork.MAX_PER_LESSON + 2):
            c.post(self._url(), {"work": self._jpg("p%d.jpg" % i)})
        self.assertEqual(LessonWork.objects.count(), LessonWork.MAX_PER_LESSON)

    def test_a_junk_row_id_404s_rather_than_500s(self):
        Client().post(self._url(), {"work": self._jpg()})
        self.assertEqual(Client().post(self._rm_url(), {"work": "abc"}).status_code, 404)

    def test_a_material_she_cannot_see_is_refused(self):
        from tutor.models import Material

        other_fam = Family.objects.create(name="Other")
        other_user = User.objects.create_user(username="pw3", email="pw3@e.com", password="pw")
        other_curr = Curriculum.objects.create(
            parent=other_user, name="Someone else", subject="Math", family=other_fam)
        ch = Chapter.objects.create(curriculum=other_curr, number=1, title="C")
        other_lesson = Lesson.objects.create(chapter=ch, order=1, number=1, title="L")
        foreign = Material.objects.create(
            lesson=other_lesson, title="Not hers", student_content="…",
            family=other_fam, status=Material.APPROVED)
        url = reverse("portal:portal_material_work",
                      kwargs={"token": self.token, "pk": foreign.pk})
        self.assertEqual(Client().post(url, {"work": self._jpg()}).status_code, 404)
