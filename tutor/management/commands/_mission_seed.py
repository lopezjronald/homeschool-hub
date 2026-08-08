"""Shared machinery for the self-directed "mission" courses (Social Studies, Science).

A mission course = a blueprint (Units → Missions) + one APPROVED Material per
mission built from LessonBlock rows (``upsert_mission``). Each mission also gets a
student **journal** QuestionSet (``add_journal``): the child logs their reflection
(and any short auto-check quiz), turns it in — which fires warm AI encouragement +
a DRAFT mastery assessment — and the parent reviews and stamps it. The journal is
what lands in the charter record. Callers: seed_sci_violet, seed_sci_kaylin,
seed_ss_violet, seed_ss_kaylin.
"""
import json
import re
from pathlib import Path

from django.core.management.base import CommandError
from django.utils import timezone

from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint
from students.models import Student
from tutor.models import LessonBlock, Material, Question, QuestionSet, ResponseSheet

from ._saxon_seed import validate_blocks


# Per-mission auto-check quizzes (verified content, keyed course -> "number" ->
# [items]). Authored + adversarially checked once, then baked to JSON so the seed
# stays deterministic and offline. Missing file = journals seed without a quiz.
_QUIZ_DATA_PATH = Path(__file__).with_name("_mission_quizzes.json")
try:
    _MISSION_QUIZZES = json.loads(_QUIZ_DATA_PATH.read_text(encoding="utf-8"))
except (OSError, ValueError):
    _MISSION_QUIZZES = {}


def mission_quiz(course_key, number):
    """The verified auto-check quiz items for one mission (``[]`` if none)."""
    return _MISSION_QUIZZES.get(course_key, {}).get(str(number), [])


# Reflection logs aren't tests — the AI grader should celebrate honest, complete
# work and suggest a level from effort, not correctness. Auto-check quiz answers
# self-correct in the portal, so the child has already seen right/wrong.
JOURNAL_RUBRIC_DEFAULT = (
    "## Teacher notes — Mission journal (assess effort, not perfection)\n"
    "This is a reflection log, not an exam. Be warm and specific — name something the "
    "child actually wrote.\n"
    "- Reward complete answers in the child's own words; a full log is Proficient or "
    "Mastered.\n"
    "- Any quiz questions are self-checking (the child already saw right/wrong) — don't "
    "re-grade them harshly.\n"
    "- Suggest Developing when an answer is thin, Beginning only if it's mostly blank.\n\n"
    "Assess mastery, not perfection — Beginning · Developing · Proficient · Mastered."
)


def resolve_child(name):
    child = Student.objects.filter(first_name__iexact=name).order_by("pk").first()
    if child is None:
        raise CommandError(f"No student named {name!r} found.")
    return child


def setup_course(child, blueprint):
    """Ensure the Curriculum exists, apply the blueprint (Units → Missions), and
    place the child on it. Idempotent. Returns the Curriculum."""
    curriculum, _ = Curriculum.objects.get_or_create(
        parent=child.parent,
        name=blueprint["name"],
        defaults={
            "family": child.family,
            "subject": blueprint["subject"],
            "grade_level": blueprint["grade_level"],
        },
    )
    apply_blueprint(curriculum, blueprint)
    CurriculumPlacement.objects.get_or_create(
        child=child, curriculum=curriculum, defaults={"is_active": True})
    return curriculum


def upsert_mission(curriculum, child, number, *, title, intro, parent_content, blocks):
    """Upsert one APPROVED Material (validated LessonBlocks) for the mission lesson
    identified by its global ``number``. Idempotent — rewrites blocks in order and
    trims any that a shortened mission dropped."""
    validate_blocks(blocks)
    lesson = Lesson.objects.filter(
        chapter__curriculum=curriculum, number=number).first()
    if lesson is None:
        raise CommandError(f"Mission {number} lesson not found — blueprint not applied?")
    material, created = Material.objects.get_or_create(
        lesson=lesson, skill_type=Material.SKILL_LESSON,
        defaults={
            "title": title, "student_intro": intro, "student_content": intro,
            "parent_content": parent_content, "child": child,
            "family": curriculum.family,
            "status": Material.APPROVED, "approved_at": timezone.now(),
        },
    )
    if not created:
        material.title = title
        material.parent_content = parent_content
        material.child = material.child or child
        if material.status != Material.APPROVED:
            material.status = Material.APPROVED
            material.approved_at = timezone.now()
        material.save()
    for order, (kind, data) in enumerate(blocks, start=1):
        LessonBlock.objects.update_or_create(
            material=material, order=order, defaults={"kind": kind, "data": data})
    LessonBlock.objects.filter(material=material, order__gt=len(blocks)).delete()
    return material


def _matching_passage(pairs):
    """A ``matching`` vocab passage: words in one column, definitions shown in a
    stable, non-aligned order (so it isn't a trivial 1:1) with the correct word
    tagged on each. Self-checks in the portal via ``data-word``."""
    words = [p["term"] for p in pairs]
    ordered = sorted(pairs, key=lambda p: p["definition"].lower())
    definitions = [
        {"n": i, "text": p["definition"], "word": p["term"]}
        for i, p in enumerate(ordered, start=1)
    ]
    return json.dumps({"words": words, "definitions": definitions}, ensure_ascii=False)


def _fill_blank_passage(words, sentences):
    """A ``fill_blank`` vocab passage. The widget splits the blank on exactly six
    underscores, so normalize any run of underscores to that (and guarantee one)."""
    norm = []
    for s in sentences:
        text = re.sub(r"_{2,}", "______", s["text"])
        if "______" not in text:
            text = text.rstrip(". ") + " ______."
        norm.append({"text": text, "word": s["word"]})
    return json.dumps({"words": words, "sentences": norm}, ensure_ascii=False)


def _quiz_questions(quiz):
    """Convert verified quiz items into add_journal question tuples (auto-check)."""
    out = []
    for item in quiz or []:
        kind, prompt = item.get("type"), item.get("prompt", "")
        if kind == "matching" and item.get("pairs"):
            out.append((
                "vocabulary", prompt,
                "Tap a word, then tap the meaning that matches it. Green means got it!",
                {"response_type": Question.TYPE_MATCHING,
                 "passage": _matching_passage(item["pairs"])},
            ))
        elif kind == "fill_blank" and item.get("sentences"):
            out.append((
                "vocabulary", prompt,
                "Pick the best word for each blank — each word is used once.",
                {"response_type": Question.TYPE_FILL_BLANK,
                 "passage": _fill_blank_passage(item.get("words", []), item["sentences"])},
            ))
    return out


def add_journal(curriculum, child, number, *, title, intro, questions, quiz=None,
                reading="", rubric="", answer_key=""):
    """Attach the mission's student journal (a MODE_STUDENT QuestionSet) to its lesson.

    ``questions`` is a list of ``(category, prompt, hint)`` reflection prompts (add a
    4th dict for a non-text type). ``quiz`` is the mission's verified quiz items
    (see ``mission_quiz``); they render after the reflection as auto-check
    matching/fill-blank questions. Turning the journal in resolves the mission, fires
    AI encouragement, and creates a DRAFT assessment the parent stamps. Idempotent —
    rewrites questions in order and trims stale ones, but never one a child already
    answered (that would orphan their saved response).
    """
    lesson = Lesson.objects.filter(
        chapter__curriculum=curriculum, number=number).first()
    if lesson is None:
        raise CommandError(f"Mission {number} lesson not found — blueprint not applied?")
    qset, _ = QuestionSet.objects.update_or_create(
        lesson=lesson, title=title,
        defaults={
            "family": curriculum.family, "child": child,
            "mode": QuestionSet.MODE_STUDENT,
            "intro": intro, "reading": reading,
            "rubric": rubric or JOURNAL_RUBRIC_DEFAULT,
            "answer_key": answer_key,
            "status": QuestionSet.APPROVED,
        },
    )
    all_questions = list(questions) + _quiz_questions(quiz)
    for order, item in enumerate(all_questions, start=1):
        category, prompt, hint = item[0], item[1], item[2]
        extra = item[3] if len(item) > 3 else {}
        Question.objects.update_or_create(
            question_set=qset, order=order,
            defaults={
                "category": category, "prompt": prompt, "hint": hint,
                "response_type": extra.get("response_type", Question.TYPE_TEXT),
                "passage": extra.get("passage", ""),
            },
        )
    stale = qset.questions.filter(order__gt=len(all_questions))
    answered = set()
    for sheet in ResponseSheet.objects.filter(question_set=qset):
        answered |= {
            int(k) for k, v in (sheet.answers or {}).items()
            if str(v).strip() and str(k).isdigit()
        }
    stale.exclude(pk__in=answered).delete()
    return qset
