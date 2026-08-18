"""Seed Kaylin's Intro to Composition: The Essay, Volume 2 (idempotent).

Ten weeks, five descriptive essays — an orange, a person, an object, a
photograph, a room — two weeks each. The publisher levels Volume 2 at Grades
6-8, so this is Kaylin's.

ONE LESSON PER WEEK, not per essay. The book numbers both ("WEEK 3 ... LESSON
2"), and either could be the unit here, but her progress advances a lesson at a
time and she works a week at a time; making the essay the lesson would leave her
sitting on the same tile for a fortnight. The titles carry both numbers so the
paper guide and the screen agree.

THE TWO WEEKS ARE DIFFERENT SHAPES, which is the whole reason this seed is not
a copy of the other Blackbird ones:

  odd week   the guide's own pages — a dictionary look-up, an observation
             exercise, then the thesis statement, the hook and a body-paragraph
             warm-up. Short typed answers, plus the book's "Now ask yourself:"
             questions as a quick self-check.
  even week  one paragraph question whose rough-draft sections ARE the guide's
             five-paragraph blueprint, then the thirty-box blueprint checklist,
             then the twelve-component self-evaluation. The writing coach sits
             inside the paragraph widget, which is where the guide puts
             "conference, then revise".

    python manage.py seed_essay_kaylin --for-user ronald
    python manage.py seed_essay_kaylin --for-user ronald --dry-run
"""

import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Chapter, Curriculum, CurriculumPlacement, Lesson
from students.models import Student
from tutor import essay
from tutor.essay_lessons import LESSONS
from tutor.models import Question, QuestionSet, ResponseSheet

CHAPTER_TITLE = "The Descriptive Essay"

# The guide's checkbox list, flattened. The paragraph heading rides along on
# each item ("P1 · Introduction — Hook") because the widget renders a flat list
# and, without it, "Opener" and "Clincher" appear three times each with nothing
# to tell them apart.
def blueprint_checklist():
    """Thirty rows, every one of them distinct.

    Each body paragraph prints "Sensory detail" three times — on paper they are
    told apart by sitting on the same rule as the factual detail they expand,
    and flattened into a list they become three identical checkboxes she cannot
    tell apart. The blueprint's own gloss says which is which ("expands on
    factual detail #2"), so the pairing is put back into the label.
    """
    items = []
    for para in essay.BLUEPRINT:
        head = para["name"].replace("BODY - ", "Body, ").title()
        seen = {}
        for label, gloss in para["lines"]:
            seen[label] = seen.get(label, 0) + 1
            shown = label
            if [x for x, _ in para["lines"]].count(label) > 1:
                shown = "%s (expands #%d)" % (label, seen[label])
            items.append("%s · %s — %s" % (para["tag"], head, shown))
    return items


SELF_EVAL_COMPONENTS = [
    "Follows Essay Format",
    "Clearly Communicates My Big Idea",
    "Hook Grabs Reader's Attention",
    "Thesis Statement & Three Sub-Topics",
    "Body Paragraph Openers",
    "Details Support My Thesis",
    "Good Transitions",
    "Compelling Twist",
    "Overall Readability",
    "Interesting Vocabulary",
    "Good Mechanics",
    "Vocal Creativity",
]

SELF_EVAL_SCALE = ["Excellent", "Satisfactory", "Needs to Improve"]
CHECKLIST_SCALE = ["In my draft", "Not yet"]

# Fallbacks for the steps the guide prints without an instruction of their own.
STEP_HINTS = {
    "observation": "Look, listen, touch — write what is actually there, not "
                   "what you expect to be there.",
    "idea_development": "This is pre-writing. Rough notes are fine; you are "
                        "collecting material, not writing the essay yet.",
    "reference": "Look it up properly, then put the meaning in your own words.",
    "other": "Take your time with this one — it feeds the essay you write next "
             "week.",
}


def _rubric(lesson):
    """What the grader is told, in the guide's own terms.

    The fifty-point form is the book's, and every line on it names something the
    blueprint taught, so it can be handed over as-is rather than paraphrased
    into something vaguer.
    """
    form = []
    for name, total, items in essay.TEACHER_FORM:
        form.append("**%s (%d points)**" % (name, total))
        form.append("  " + " · ".join("%s (%d)" % (label, pts)
                                      for label, pts in items))
    bands = "\n".join(
        "- **%s** — %s" % (name, "; ".join(criteria))
        for name, criteria in essay.EVALUATION_RUBRIC)
    return """## The Essay, Volume 2 — Lesson {n}: {title}

She is writing a DESCRIPTIVE essay: five paragraphs, thirty sentences, built on
the guide's blueprint — introduction (hook, context, thesis statement), three
body paragraphs (opener, three factual/sensory pairs, clincher), conclusion
(weave, echo, twist).

### The guide's grading form — {total} points

{form}

### The guide's bands

{bands}

Grade the FINAL DRAFT. The rough-draft sections are planning and are not marked.
Where she has self-evaluated, that is her own judgement of her own work — read
it for honesty and self-awareness, and never mark her down for naming a weakness
she can see. Noticing what to strengthen is the skill this week is teaching.

Grade-7 mastery: Beginning → Developing → Proficient → Mastered.
""".format(n=lesson["number"], title=lesson["title"], total=essay.TOTAL_POINTS,
           form="\n".join(form), bands=bands)


ODD_INTRO = """**{banner}**

This week is the guide's pre-writing: look closely, then build the parts of the
essay one at a time — your three sub-topics and thesis statement, a hook, and a
body paragraph warmed up. Next week you draft the whole thing.
"""

EVEN_INTRO = """**Lesson {n}: {title} — the draft.**

Work in the order the guide sets out:

1. Write the five paragraphs of your **rough draft** in the boxes, following the
   blueprint. Skip nothing — thirty sentences.
2. Ask your **writing coach** for feedback, and read it aloud to someone.
3. Run the **blueprint checklist** and the **self-evaluation** below.
4. Only then write your **final draft**, putting the changes in.

The guide asks for the final draft typed, double-spaced, with 1-inch margins,
and printed for your binder — type it here first.
"""


class Command(BaseCommand):
    help = "Seed The Essay, Volume 2 (10 weeks, 5 descriptive essays)."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True)
        parser.add_argument("--child-name", default="Kaylin")
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['for_user']}' does not exist.")

        child = Student.objects.filter(
            parent=user, first_name__iexact=options["child_name"]).first()
        if child is None:
            raise CommandError(f"No child named '{options['child_name']}'.")

        family = get_active_family(user)

        if options["dry_run"]:
            # Before any writes: a dry run that seeds is not a dry run.
            for L in LESSONS:
                odd, even = L["weeks"]
                self.stdout.write(
                    "  Lesson %d %-20s week %2d: %2d questions   week %2d: draft "
                    "+ %d checks + %d ratings"
                    % (L["number"], L["title"], odd, self._odd_count(L), even,
                       len(blueprint_checklist()), len(SELF_EVAL_COMPONENTS)))
            self.stdout.write(self.style.WARNING(
                "Dry run — nothing written. Would seed %d weeks across %d essays."
                % (2 * len(LESSONS), len(LESSONS))))
            return

        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=essay.CURRICULUM_NAME,
            defaults={"subject": "Language Arts", "grade_level": "G07",
                      "family": family},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using'} curriculum #{curriculum.pk}")

        chapter, _ = Chapter.objects.get_or_create(
            curriculum=curriculum, number=1,
            defaults={"title": CHAPTER_TITLE},
        )

        sets = questions = 0
        for L in LESSONS:
            for week in L["weeks"]:
                lesson = self._lesson(chapter, L, week)
                qset = self._set(lesson, family, L, week)
                questions += (self._fill_odd(qset, L) if week % 2
                              else self._fill_even(qset, L))
                sets += 1
                self.stdout.write("  Week %2d · Lesson %d: %s%s"
                                  % (week, L["number"], L["title"],
                                     "" if week % 2 else " (draft)"))

        first = Lesson.objects.filter(chapter=chapter).order_by("order").first()
        _, made = CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first},
        )
        self.stdout.write(self.style.SUCCESS(
            "Seeded %d weeks, %d questions across %d essays. %s %s."
            % (sets, questions, len(LESSONS), child.first_name,
               "placed at week 1" if made else "kept at existing progress")))

    # -- shape -------------------------------------------------------------

    @staticmethod
    def _odd_count(L):
        n = len(L["vocabulary"])
        for step in L["steps"]:
            n += len(step["prompts"])
            if step.get("checks"):
                n += 1
        return n

    @staticmethod
    def set_title(L, week):
        return ("Week %d · Lesson %d: %s%s"
                % (week, L["number"], L["title"], "" if week % 2 else " — the draft"))

    def _lesson(self, chapter, L, week):
        lesson, _ = Lesson.objects.update_or_create(
            chapter=chapter, order=week,
            defaults={
                "number": week,
                "title": self.set_title(L, week),
                "objectives": (
                    "Look closely, then build the parts: three sub-topics, a "
                    "thesis statement, a hook, a body paragraph."
                    if week % 2 else
                    "Draft the five-paragraph essay from the blueprint, check it "
                    "against the blueprint and the self-evaluation, then write "
                    "the final draft."
                ),
            },
        )
        return lesson

    def _set(self, lesson, family, L, week):
        intro = (ODD_INTRO.format(banner=L["banner"]) if week % 2
                 else EVEN_INTRO.format(n=L["number"], title=L["title"]))
        # The printed-quirk notes are NOT copied in here. They are rendered from
        # tutor.essay_lessons by the week's header, week-scoped, so correcting
        # one needs no re-seed — and putting them in both places printed every
        # warning on the page twice.
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson, title=self.set_title(L, week),
            defaults={
                "family": family,
                "intro": intro,
                "rubric": _rubric(L),
                "status": QuestionSet.APPROVED,
                "reading": "",
                "mode": QuestionSet.MODE_STUDENT,
            },
        )
        return qset

    # -- questions ---------------------------------------------------------

    def _fill_odd(self, qset, L):
        order = 0
        for word in L["vocabulary"]:
            order += 1
            self._q(qset, order, category="vocabulary",
                    prompt="Use a dictionary to define: **%s**" % word,
                    hint="Write the definition in your own words once you have "
                         "read the dictionary's.")
        for step in L["steps"]:
            head = step["heading"]
            for i, p in enumerate(step["prompts"]):
                order += 1
                prompt = p["text"]
                if head and i == 0:
                    prompt = "%s\n\n%s" % (head, prompt)
                # Every question carries a nudge. Most steps print their own
                # instruction; the ones that do not still need something, or
                # she gets a bare question with no idea what it is for.
                self._q(qset, order, category="writing", prompt=prompt,
                        hint=step.get("instruction") or STEP_HINTS.get(
                            step["kind"], STEP_HINTS["other"]))
            if step.get("checks"):
                order += 1
                # The book prints "Now ask yourself:" under each step, so a
                # page with two of them showed her the same question twice with
                # different contents. Name which step is being checked.
                lead = step.get("check_lead") or "Now ask yourself:"
                if head:
                    lead = "%s — %s" % (head.replace("»", "").strip(),
                                        lead[0].lower() + lead[1:])
                self._q(
                    qset, order, category="writing",
                    response_type=Question.TYPE_SELF_EVAL,
                    prompt=lead,
                    hint="The guide's own check. Be honest — a 'Not yet' here "
                         "is what tells you what to fix.",
                    passage=json.dumps({"items": step["checks"],
                                        "scale": ["Yes", "Not yet"],
                                        "notes": False}),
                )
        self._prune(qset, order)
        return order

    def _fill_even(self, qset, L):
        order = 1
        self._q(
            qset, order, category="writing",
            response_type=Question.TYPE_PARAGRAPH,
            prompt="Write **%s** — your descriptive essay." % L["title"].lower(),
            hint="Five paragraphs, thirty sentences, straight off the blueprint. "
                 "Get your ideas down first; you will fix them afterwards.",
            # A box per paragraph, sized to the paragraph: the three body
            # paragraphs are eight sentences each and the opener and close are
            # three, so a uniform box would either cramp the body or leave her
            # staring at eight empty rows for a three-sentence conclusion.
            passage=json.dumps({
                "sections": essay.PARAGRAPH_SECTIONS,
                "section_rows": [p["sentences"] for p in essay.BLUEPRINT],
            }),
        )
        order += 1
        self._q(
            qset, order, category="editing",
            response_type=Question.TYPE_SELF_EVAL,
            prompt="Checking the Blueprint — is every sentence there?",
            hint="Read your rough draft through and tick off each sentence you "
                 "actually wrote. Whatever is left unticked is what to add.",
            passage=json.dumps({"items": blueprint_checklist(),
                                "scale": CHECKLIST_SCALE, "notes": False}),
        )
        order += 1
        self._q(
            qset, order, category="editing",
            response_type=Question.TYPE_SELF_EVAL,
            prompt="Student Self-Evaluation — read your essay aloud a second "
                   "time, then judge each part.",
            hint="Rate each one and say how you would make it stronger. This is "
                 "yours, not a test — naming a weakness is the point.",
            passage=json.dumps({"items": SELF_EVAL_COMPONENTS,
                                "scale": SELF_EVAL_SCALE}),
        )
        self._prune(qset, order)
        return order

    @staticmethod
    def _q(qset, order, *, category, prompt, hint,
           response_type=Question.TYPE_TEXT, passage=""):
        Question.objects.update_or_create(
            question_set=qset, order=order,
            defaults={
                "category": category,
                "response_type": response_type,
                "prompt": prompt,
                "hint": hint,
                "passage": passage,
            },
        )

    @staticmethod
    def _prune(qset, keep_through):
        """Drop questions past the end that nobody has answered."""
        stale = qset.questions.filter(order__gt=keep_through)
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and k.isdigit()}
        stale.exclude(pk__in=answered).delete()
