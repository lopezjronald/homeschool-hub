"""The student portal — a kid's own view of just their work.

Every view resolves a signed token to ONE student and scopes every queryset to
that student. No login, no navigation into the parent app, nothing that isn't
theirs. Parents generate the link from the child's profile page.
"""

import json
from collections import defaultdict
from itertools import groupby

from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from activities.models import ExternalActivity
from curricula.models import Curriculum, CurriculumPlacement
from curricula.subjects import emoji_for, is_spelling
from tutor import ai, grading
from tutor.models import Material, QuestionSet, ResponseSheet
from worklog.models import WorkLogEntry

from .tokens import student_from_token


def _resolve_student(token):
    student = student_from_token(token)
    if student is None:
        raise Http404
    return student


def _placed_curriculum_ids(student):
    return list(student.placements.values_list("curriculum_id", flat=True))


def _visible_materials(student):
    """Approved materials for this child (theirs, or unpinned ones in their curricula)."""
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        Material.objects.filter(status=Material.APPROVED)
        .filter(
            Q(child=student)
            | Q(child__isnull=True, lesson__chapter__curriculum_id__in=curriculum_ids)
        )
        .select_related("lesson", "lesson__chapter")
        .order_by("lesson__chapter__number", "lesson__order")
    )


def _visible_question_sets(student):
    """Approved STUDENT-form question sets this child may open.

    Teacher-led discussion sets are intentionally excluded — those are for the
    parent to lead orally, not for the child to fill out.
    """
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        QuestionSet.objects.filter(status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)
        .filter(
            Q(child=student)
            | Q(child__isnull=True, lesson__chapter__curriculum_id__in=curriculum_ids)
        )
        .select_related("lesson", "lesson__chapter", "lesson__chapter__curriculum")
    )


def _annotated_question_sets(student):
    """Ordered list of visible sets with this child's response attached."""
    sets = list(
        _visible_question_sets(student).order_by(
            "lesson__chapter__curriculum__name", "lesson__chapter__number", "lesson__order", "id",
        )
    )
    responses = {
        r.question_set_id: r
        for r in ResponseSheet.objects.filter(child=student, question_set__in=sets)
    }
    for qs in sets:
        qs.my_response = responses.get(qs.pk)
    return sets


def _visible_activities(student):
    """Active external activities for this child (theirs + whole-family)."""
    qs = ExternalActivity.objects.filter(is_active=True)
    if student.family_id:
        return qs.filter(Q(student=student) | Q(student__isnull=True, family=student.family))
    # Null-family child: scope whole-family activities to the owner so a null
    # family filter can't match every other user's null-family activities.
    return qs.filter(
        Q(student=student)
        | Q(student__isnull=True, family__isnull=True, parent=student.parent)
    )


def _set_is_done(qs):
    """True if this child has already turned in the set."""
    return bool(getattr(qs, "my_response", None) and qs.my_response.is_submitted)


def _subject_cards(student):
    """One card per subject the child is in: progress + the single next thing.

    Unions the child's curriculum placements with any curriculum that owns work
    they can see (question sets or materials), so nothing is hidden — but each
    subject collapses to one calm card, never a wall of rows. This is the
    "what's next, tap-a-subject" surface (autonomy to choose, one clear step).
    """
    annotated = _annotated_question_sets(student)
    materials = list(_visible_materials(student))

    sets_by_curr = defaultdict(list)
    for qs in annotated:
        sets_by_curr[qs.lesson.chapter.curriculum_id].append(qs)
    materials_by_curr = defaultdict(list)
    for m in materials:
        materials_by_curr[m.lesson.chapter.curriculum_id].append(m)

    placements = {
        p.curriculum_id: p
        for p in CurriculumPlacement.objects.filter(child=student).select_related(
            "curriculum", "current_lesson", "current_lesson__chapter",
        )
    }

    # Placements first (stable order), then any other curriculum owning work.
    curr_ids = list(placements)
    for cid in list(sets_by_curr) + list(materials_by_curr):
        if cid not in curr_ids:
            curr_ids.append(cid)

    curricula = {p.curriculum_id: p.curriculum for p in placements.values()}
    missing = [cid for cid in curr_ids if cid not in curricula]
    if missing:
        for c in Curriculum.objects.filter(id__in=missing):
            curricula[c.id] = c

    cards = []
    for cid in curr_ids:
        curriculum = curricula.get(cid)
        if curriculum is None:
            continue
        placement = placements.get(cid)
        curr_sets = sets_by_curr.get(cid, [])
        sets_total = len(curr_sets)
        sets_done = sum(1 for qs in curr_sets if _set_is_done(qs))
        cards.append({
            "curriculum": curriculum,
            "emoji": emoji_for(curriculum.subject),
            "placement": placement,
            "progress": placement.progress() if placement else None,
            "current_lesson": placement.current_lesson if placement else None,
            "next_set": next((qs for qs in curr_sets if not _set_is_done(qs)), None),
            "sets_done": sets_done,
            "sets_total": sets_total,
            "sets_pct": round(sets_done / sets_total * 100) if sets_total else 0,
            "materials_count": len(materials_by_curr.get(cid, [])),
            # Online subjects (Beast Academy, DIVE…) launch out to the website.
            "is_external": curriculum.is_external,
            "launch_url": curriculum.website_url if curriculum.is_external else "",
        })

    cards.sort(key=lambda c: (c["curriculum"].subject or "", c["curriculum"].name))
    return cards


def portal_home(request, token):
    """The kid's 'Today' surface: one calm card per subject, one next step each."""
    student = _resolve_student(token)
    return render(request, "portal/portal_home.html", {
        "student": student,
        "token": token,
        "subjects": _subject_cards(student),
        "activities": _visible_activities(student),
    })


def portal_subject(request, token, curriculum_id):
    """Drill into one subject: chapters, the current one open, finished folded."""
    student = _resolve_student(token)

    sets = [
        qs for qs in _annotated_question_sets(student)
        if qs.lesson.chapter.curriculum_id == curriculum_id
    ]
    materials = [
        m for m in _visible_materials(student)
        if m.lesson.chapter.curriculum_id == curriculum_id
    ]
    placement = (
        CurriculumPlacement.objects
        .filter(child=student, curriculum_id=curriculum_id)
        .select_related("curriculum", "current_lesson", "current_lesson__chapter")
        .first()
    )
    # Authorize: the child must be placed in this subject or own work in it.
    if placement is None and not sets and not materials:
        raise Http404
    curriculum = placement.curriculum if placement else get_object_or_404(Curriculum, pk=curriculum_id)

    next_set = next((qs for qs in sets if not _set_is_done(qs)), None)
    if next_set is not None:
        current_chapter = next_set.lesson.chapter.number
    elif placement and placement.current_lesson:
        current_chapter = placement.current_lesson.chapter.number
    else:
        current_chapter = None

    # Sets arrive ordered curriculum→chapter→lesson, so group by chapter number.
    chapters = []
    for (number, title), group in groupby(
        sets, key=lambda s: (s.lesson.chapter.number, s.lesson.chapter.title),
    ):
        items = list(group)
        chapters.append({
            "number": number,
            "title": title,
            "sets": items,
            "done": sum(1 for qs in items if _set_is_done(qs)),
            "total": len(items),
            "is_current": number == current_chapter,
        })
    # If nothing is flagged current (e.g. all finished), open the first chapter.
    if chapters and not any(ch["is_current"] for ch in chapters):
        chapters[0]["is_current"] = True

    return render(request, "portal/portal_subject.html", {
        "student": student,
        "token": token,
        "curriculum": curriculum,
        "emoji": emoji_for(curriculum.subject),
        "placement": placement,
        "progress": placement.progress() if placement else None,
        "current_lesson": placement.current_lesson if placement else None,
        "next_set": next_set,
        "chapters": chapters,
        "materials": materials,
    })


def portal_material(request, token, pk):
    """Kid view of an approved material — student layers only, never the teaching guide."""
    student = _resolve_student(token)
    material = get_object_or_404(_visible_materials(student), pk=pk)
    return render(request, "portal/portal_material.html", {
        "student": student,
        "token": token,
        "material": material,
    })


# Brute-force guard for the parent gate. Per-worker with the default LocMemCache,
# so the real ceiling is a small multiple of this — still enough to stop an
# online guessing attack from a child's device.
_GATE_MAX_ATTEMPTS = 8
_GATE_LOCKOUT_SECONDS = 15 * 60


def portal_parent_gate(request, token):
    """Cross back from a child's portal to the parent dashboard.

    The portal is the child's surface — token-authed, no login — so the child
    also holds this link. We already know *which* parent owns the child from the
    token, so returning to the parent side asks only for that parent's password
    (a re-auth, not a fresh sign-in) and then drops them straight on the
    dashboard, instead of bouncing to the public landing / full login page. A
    parent who still has a live session skips the prompt entirely.
    """
    student = _resolve_student(token)
    parent = student.parent
    if parent is None:  # no owner to re-auth against; fall back to normal sign-in
        return redirect("accounts:login")

    # Live parent session → straight through, no password needed.
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    # The child's link is a bookmark on a kid's device, so throttle password
    # attempts against this (already-identified) parent to blunt brute-forcing.
    fail_key = f"parentgate:fail:{parent.pk}"

    error = ""
    if request.method == "POST":
        if cache.get(fail_key, 0) >= _GATE_MAX_ATTEMPTS:
            error = "Too many tries. Please wait a few minutes, then try again."
        else:
            password = request.POST.get("password", "")
            # Authenticate the token's parent specifically — a wrong password (or a
            # different user's password) can't open this dashboard.
            user = authenticate(request, username=parent.get_username(), password=password)
            if user is not None:
                cache.delete(fail_key)
                login(request, user)
                return redirect("dashboard:dashboard")
            cache.set(fail_key, cache.get(fail_key, 0) + 1, _GATE_LOCKOUT_SECONDS)
            error = "That password doesn't match. Please try again."

    return render(request, "portal/parent_gate.html", {
        "student": student,
        "token": token,
        "parent": parent,
        "error": error,
    })


def _sheet_for(student, question_set):
    sheet, _ = ResponseSheet.objects.get_or_create(question_set=question_set, child=student)
    return sheet


def portal_questions(request, token, set_pk):
    """The response form: no autocorrect, autosaves as the child types."""
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)

    if request.method == "POST":
        _submit_sheet(student, question_set, request.POST)
        return redirect("portal:portal_feedback", token=token, set_pk=set_pk)

    sheet = _sheet_for(student, question_set)
    questions = list(question_set.questions.all())
    for q in questions:
        q.my_answer = sheet.answer_for(q)
        q.my_coach = (sheet.draft_feedback or {}).get(str(q.pk))

    # Spell-check + synonym help everywhere EXCEPT spelling curricula, where the
    # child is supposed to spell the words unaided.
    spelling = is_spelling(question_set.lesson.chapter.curriculum.subject)

    return render(request, "portal/portal_questions.html", {
        "student": student,
        "token": token,
        "question_set": question_set,
        "questions": questions,
        "sheet": sheet,
        "spellcheck_on": not spelling,
        "wordhelp_on": not spelling,
    })


def _submit_sheet(student, question_set, post_data):
    """Atomically turn in a sheet: exactly one DRAFT→SUBMITTED transition.

    Locks the sheet row so a double-click or two-tab race can't create two
    WorkLogEntries; a request that loses the race sees SUBMITTED and no-ops.
    """
    with transaction.atomic():
        sheet, _ = ResponseSheet.objects.select_for_update().get_or_create(
            question_set=question_set, child=student,
        )
        if sheet.is_submitted:
            return sheet  # someone already turned it in

        _merge_answers(sheet, post_data)
        sheet.status = ResponseSheet.SUBMITTED
        sheet.submitted_at = timezone.now()
        curriculum = question_set.lesson.chapter.curriculum
        sheet.work_entry = WorkLogEntry.objects.create(
            parent=student.parent,
            family=student.family,
            child=student,
            curriculum=curriculum,
            subject=curriculum.subject or "Literature",
            description=(
                f"{question_set.title} — submitted from {student.first_name}'s portal.\n\n"
                + sheet.as_worklog_text()
            ),
            date=timezone.localdate(),
        )
        sheet.save()
        return sheet


def _merge_answers(sheet, data):
    """Merge posted answer_<id> fields into the sheet's answers JSON."""
    answers = dict(sheet.answers or {})
    question_ids = set(
        str(pk) for pk in sheet.question_set.questions.values_list("pk", flat=True)
    )
    for key, value in data.items():
        if key.startswith("answer_"):
            qid = key.removeprefix("answer_")
            if qid in question_ids:
                answers[qid] = value
    sheet.answers = answers


def portal_feedback(request, token, set_pk):
    """The 'you turned it in!' page — celebration plus the agent's quick feedback.

    If a draft assessment already exists, its child-facing pieces render at
    once; otherwise the page shows a friendly reading state and JS asks
    ``portal_feedback_generate`` to produce one. The child never sees a level.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return redirect("portal:portal_questions", token=token, set_pk=set_pk)

    from tutor.models import MasteryAssessment

    assessment = MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).first()
    from tutor import ai

    return render(request, "portal/portal_feedback.html", {
        "student": student,
        "token": token,
        "question_set": question_set,
        "sheet": sheet,
        "assessment": assessment,
        "can_generate": assessment is None and ai.is_configured(),
    })


@csrf_exempt
@require_POST
def portal_feedback_generate(request, token, set_pk):
    """Generate (idempotently) the agent's feedback for a submitted sheet.

    CSRF-exempt for the same reason as autosave: portal auth is the signed
    token in the URL, not an ambient cookie. Returns only child-facing fields.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return JsonResponse({"ok": False}, status=409)

    from tutor import ai, grading

    try:
        assessment, _created = grading.auto_grade_sheet(sheet)
    except ai.GraderError:
        return JsonResponse({"ok": False})  # kid page falls back to plain celebration
    if assessment is None:
        return JsonResponse({"ok": False})
    return JsonResponse({
        "ok": True,
        "encouragement": assessment.ai_encouragement,
        "highlights": assessment.ai_kid_highlights or [],
    })


@csrf_exempt
@require_POST
def portal_feedback_start(request, token, set_pk):
    """Kick off (idempotently) the background grade for a submitted sheet.

    Returns immediately — grading runs off the request path (no 30s wall) and the
    page then polls ``portal_feedback_status``. Safe to call repeatedly: if the
    assessment already exists we report it ready and skip re-grading; if the
    grader isn't configured we say so, so the page can stop waiting.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return JsonResponse({"ok": False}, status=409)

    from tutor.models import MasteryAssessment

    if MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).exists():
        return JsonResponse({"ok": True, "ready": True})
    if not ai.is_configured():
        return JsonResponse({"ok": True, "ready": False, "grading": False})

    grading.start_background_grade(sheet.pk)
    return JsonResponse({"ok": True, "ready": False, "grading": True})


def portal_feedback_status(request, token, set_pk):
    """Poll for the agent's feedback. Returns the child-facing pieces once ready.

    ``ready`` flips true as soon as the background grade has saved the draft
    assessment. ``grading`` tells the page whether a grade is still expected (the
    grader is configured) so it knows to keep waiting vs. fall back gracefully.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return JsonResponse({"ready": False}, status=409)

    from tutor.models import MasteryAssessment

    assessment = MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).first()
    if assessment is None:
        return JsonResponse({"ready": False, "grading": ai.is_configured()})
    return JsonResponse({
        "ready": True,
        "encouragement": assessment.ai_encouragement,
        "highlights": assessment.ai_kid_highlights or [],
    })


@csrf_exempt
@require_POST
def portal_draft_feedback(request, token, set_pk):
    """Writing-coach feedback on a ROUGH draft (before the final draft).

    Token-authed like autosave. Saves the draft text first (so nothing is
    lost), asks the coach for praise + suggestions, stores them on the sheet
    (visible again on reload), and returns the kid-facing pieces. Never grades.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"ok": False}, status=400)
    qid = str(payload.get("question", ""))
    draft = payload.get("text", "")
    if not isinstance(draft, str) or len(draft.strip()) < 20:
        return JsonResponse({"ok": False, "error": "too_short"})

    question = question_set.questions.filter(pk=qid).first() if qid.isdigit() else None
    if question is None or not question.supports_draft_coach:
        return JsonResponse({"ok": False}, status=400)

    sheet = _sheet_for(student, question_set)
    if sheet.is_submitted:
        return JsonResponse({"ok": False}, status=409)

    from tutor import ai

    curriculum = question_set.lesson.chapter.curriculum
    grade = (curriculum.get_grade_level_display() if curriculum.grade_level
             else student.get_grade_level_display())
    try:
        result = ai.review_draft(
            draft=draft,
            assignment=question.prompt or question_set.intro,
            grade_level=grade,
            subject=curriculum.subject or "Writing",
        )
    except (ai.GraderNotConfigured, ai.GraderError):
        return JsonResponse({"ok": False})

    with transaction.atomic():
        locked, _ = ResponseSheet.objects.select_for_update().get_or_create(
            question_set=question_set, child=student,
        )
        if locked.is_submitted:
            return JsonResponse({"ok": False}, status=409)
        answers = dict(locked.answers or {})
        answers[qid] = draft                     # keep the draft she asked about
        feedback = dict(locked.draft_feedback or {})
        feedback[qid] = {
            "praise": result["praise"],
            "suggestions": result["suggestions"],
            "at": timezone.localtime(timezone.now()).strftime("%b %d, %I:%M %p"),
        }
        locked.answers = answers
        locked.draft_feedback = feedback
        locked.save(update_fields=["answers", "draft_feedback", "updated_at"])

    return JsonResponse({"ok": True, "praise": result["praise"],
                         "suggestions": result["suggestions"]})


@csrf_exempt
@require_POST
def portal_autosave(request, token, set_pk):
    """Autosave endpoint — merges the draft answers, returns a saved timestamp.

    CSRF-exempt by design: portal auth is the unguessable signed token in the
    URL (not an ambient cookie), so cross-site forgery has nothing to ride on,
    and exemption lets ``navigator.sendBeacon`` deliver the last-chance save.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
    posted = payload.get("answers") if isinstance(payload, dict) else None
    if not isinstance(posted, dict):
        return JsonResponse({"ok": False, "error": "bad payload"}, status=400)

    question_ids = set(str(pk) for pk in question_set.questions.values_list("pk", flat=True))
    with transaction.atomic():
        sheet, _ = ResponseSheet.objects.select_for_update().get_or_create(
            question_set=question_set, child=student,
        )
        if sheet.is_submitted:
            return JsonResponse({"ok": False, "error": "already submitted"}, status=409)
        answers = dict(sheet.answers or {})
        for qid, text in posted.items():
            if str(qid) in question_ids and isinstance(text, str):
                answers[str(qid)] = text
        sheet.answers = answers
        sheet.save(update_fields=["answers", "updated_at"])

    return JsonResponse({
        "ok": True,
        "saved_at": timezone.localtime(sheet.updated_at).strftime("%I:%M %p").lstrip("0"),
        "answered": sheet.answered_count,
    })


@csrf_exempt
@require_POST
def portal_word_help(request, token, set_pk):
    """Suggest better/similar words for a word the child selected while writing.

    Token-authed like autosave. Disabled on spelling curricula. Returns only a
    small list of clean words; degrades to an empty list on any lookup failure.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    if is_spelling(question_set.lesson.chapter.curriculum.subject):
        return JsonResponse({"ok": False, "words": []})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "words": []}, status=400)
    word = str(payload.get("word", "")).strip()[:40] if isinstance(payload, dict) else ""

    from . import thesaurus

    words = thesaurus.synonyms(word, grade_level=student.get_grade_level_display())
    return JsonResponse({"ok": bool(words), "word": word, "words": words})


@csrf_exempt
@require_POST
def portal_spellcheck(request, token, set_pk):
    """Find misspelled words in the child's writing so the page can draw its own
    red squiggle + one-tap fixes. Token-authed; disabled on spelling curricula.
    Returns [{"wrong", "fixes":[...]}]; empty on any failure.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    if is_spelling(question_set.lesson.chapter.curriculum.subject):
        return JsonResponse({"ok": False, "misspelled": []})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "misspelled": []}, status=400)
    text = str(payload.get("text", ""))[:4000] if isinstance(payload, dict) else ""

    from tutor import ai

    misspelled = ai.check_spelling(text, grade_level=student.get_grade_level_display())
    return JsonResponse({"ok": True, "misspelled": misspelled})
