import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, ProtectedError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.permissions import (
    viewable_queryset, editable_queryset, scoped_queryset, user_can_edit,
    can_edit_family_or_global,
)
from core.utils import get_active_family, get_selected_family, resolve_family_for_write

from portal.tokens import make_portal_token

from .models import Student
from .forms import StudentForm

# Host is the composition root that wires the extractable lingua module (D-04):
# no FK links Student -> lingua (D-03), so deletion must purge lingua explicitly.
from lingua import services as lingua_services

logger = logging.getLogger(__name__)


@login_required
def student_list(request):
    """Display list of children the user can view (via family membership)."""
    family = get_selected_family(request)
    students = scoped_queryset(Student.objects.all(), request.user, family)
    # Gate edit controls on THIS family — an editor in another family who is only a
    # viewer of the selected family must not see edit/portal controls here.
    can_edit = can_edit_family_or_global(request.user, family)
    return render(request, "students/student_list.html", {
        "students": students,
        "can_edit": can_edit,
    })


@login_required
@require_POST
def enter_portal(request, pk):
    """Hand the device to a child: drop into their portal and sign the parent out.

    POST-only (it's a state change). Signing the parent out is deliberate — it
    means the child can't wander back into the parent app, and returning
    requires re-entering the login credentials, exactly as intended.
    """
    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)
    url = reverse("portal:portal_home", kwargs={"token": make_portal_token(student)})
    logout(request)
    return redirect(url)


@login_required
def student_create(request):
    """Create a new child profile (editors only)."""
    if not user_can_edit(request.user):
        from django.http import Http404
        raise Http404

    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.parent = request.user
            student.family = resolve_family_for_write(request)
            student.save()
            messages.success(request, f"{student.first_name} has been added.")
            return redirect("students:student_list")
    else:
        form = StudentForm()

    return render(request, "students/student_form.html", {"form": form, "action": "Add"})


@login_required
def student_detail(request, pk):
    """View a child's profile plus the curricula they're currently doing."""
    student = get_object_or_404(viewable_queryset(Student.objects.all(), request.user), pk=pk)
    # Gate on the CHILD's family: a view-only member of that family must not get the
    # edit controls or the login-free portal bearer URL (built below when can_edit).
    can_edit = can_edit_family_or_global(request.user, student.family)

    placements = (
        student.placements
        .select_related("curriculum", "current_lesson", "current_lesson__chapter")
        .order_by("curriculum__subject", "curriculum__name")
    )
    from tutor.models import QuestionSet

    discussion_curriculum_ids = set(
        QuestionSet.objects.filter(
            lesson__chapter__curriculum__in=[p.curriculum_id for p in placements],
            mode=QuestionSet.MODE_DISCUSSION,
        ).values_list("lesson__chapter__curriculum_id", flat=True)
    )
    curricula = [
        {
            "curriculum": placement.curriculum,
            "current_lesson": placement.current_lesson,
            "next_lesson": placement.next_lesson(),
            "progress": placement.progress(),
            "has_discussion": placement.curriculum_id in discussion_curriculum_ids,
        }
        for placement in placements
    ]

    portal_url = None
    if can_edit:
        from django.urls import reverse

        from portal.tokens import make_portal_token

        portal_url = request.build_absolute_uri(
            reverse("portal:portal_home", kwargs={"token": make_portal_token(student)})
        )

    # Spelling is a separate programme; show its card only when a parent has
    # actually placed her in it. Guarded so this page never breaks over a
    # sibling app.
    spelling_placement = spelling_week = None
    try:
        from spelling.models import SpellingPlacement, SpellingWeek

        spelling_placement = SpellingPlacement.objects.filter(child=student).first()
        if spelling_placement:
            spelling_week = SpellingWeek.objects.filter(
                number=spelling_placement.current_week).first()
    except Exception:
        spelling_placement = spelling_week = None

    return render(request, "students/student_detail.html", {
        "student": student,
        "can_edit": can_edit,
        "curricula": curricula,
        "portal_url": portal_url,
        "spelling_placement": spelling_placement,
        "spelling_week": spelling_week,
    })


@login_required
def student_work(request, pk, curriculum_id):
    """Parent read-only browser: a child's question sets in one curriculum,
    grouped by chapter, each showing whether it's turned in, in progress, or
    not started."""
    from itertools import groupby

    from curricula.models import Curriculum
    from tutor.models import QuestionSet, ResponseSheet

    student = get_object_or_404(viewable_queryset(Student.objects.all(), request.user), pk=pk)
    curriculum = get_object_or_404(
        viewable_queryset(Curriculum.objects.all(), request.user), pk=curriculum_id,
    )

    sets = list(
        QuestionSet.objects.filter(
            lesson__chapter__curriculum=curriculum,
            mode=QuestionSet.MODE_STUDENT,
            status=QuestionSet.APPROVED,
        )
        # Honor the per-child pin, exactly as the child's own portal does, so
        # this list matches what the child actually has (no phantom siblings' sets).
        .filter(Q(child=student) | Q(child__isnull=True))
        .select_related("lesson", "lesson__chapter")
        .order_by("lesson__chapter__number", "lesson__order", "id")
    )
    sheets = {
        s.question_set_id: s
        for s in ResponseSheet.objects.filter(question_set__in=sets, child=student)
    }
    for qs in sets:
        qs.my_sheet = sheets.get(qs.pk)

    chapters = [
        {"heading": f"Chapter {number} · {items[0].lesson.chapter.title}", "sets": items}
        for (number, _t), group in groupby(
            sets, key=lambda s: (s.lesson.chapter.number, s.lesson.chapter.title),
        )
        for items in [list(group)]
    ]
    done = sum(1 for qs in sets if qs.my_sheet and qs.my_sheet.is_submitted)

    return render(request, "students/student_work.html", {
        "student": student,
        "curriculum": curriculum,
        "chapters": chapters,
        "done": done,
        "total": len(sets),
    })


@login_required
def student_work_set(request, pk, set_pk):
    """Parent read-only view of one question set with the child's answers."""
    from curricula.models import Curriculum
    from tutor.models import MasteryAssessment, QuestionSet, ResponseSheet

    student = get_object_or_404(viewable_queryset(Student.objects.all(), request.user), pk=pk)
    viewable_curricula = viewable_queryset(Curriculum.objects.all(), request.user)
    question_set = get_object_or_404(
        QuestionSet.objects.filter(
            lesson__chapter__curriculum__in=viewable_curricula,
        )
        # Same per-child pin scoping as the portal: a set pinned to a sibling
        # isn't this child's work.
        .filter(Q(child=student) | Q(child__isnull=True))
        .select_related("lesson", "lesson__chapter", "lesson__chapter__curriculum"),
        pk=set_pk,
    )
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()

    rows = []
    for q in question_set.questions.all():
        display = sheet.answer_display(q) if sheet else ""
        rows.append({
            "question": q,
            "answer": display,
            # Derive from the rendered display so an empty structured answer
            # (e.g. only-wrong matching attempts → "(no answer)") reads as unanswered.
            "answered": display not in ("", "(no answer)"),
            "replay": sheet.answer_replay(q) if sheet else None,
            "coach": (sheet.draft_feedback or {}).get(str(q.pk)) if sheet else None,
        })

    assessment = None
    if sheet and sheet.work_entry_id:
        assessment = MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).first()

    return render(request, "students/student_work_set.html", {
        "student": student,
        "question_set": question_set,
        "curriculum": question_set.lesson.chapter.curriculum,
        "sheet": sheet,
        "rows": rows,
        "assessment": assessment,
        "can_edit": can_edit_family_or_global(request.user, student.family),
    })


@login_required
@require_POST
def student_work_set_approve(request, pk, set_pk):
    """Mark a section done from the paper copy — the parent's half of the rule.

    Completion needs BOTH a file and this click. The upload alone leaves the
    section waiting; this alone is refused, because a section marked done with
    nothing attached is exactly the hole the work log exists to close.

    The parent may also attach the file here — Joyce scans the paper herself
    rather than handing the tablet to a child who has already finished.

    On approval the sheet becomes SUBMITTED and gets a WorkLogEntry, the same
    as an on-screen turn-in, so progress, the reports and the grade record all
    treat it as the finished section it is. The file stays owned by the sheet.
    """
    import os

    from django.utils import timezone

    from tutor.models import QuestionSet, ResponseSheet
    from worklog.models import WorkLogEntry

    from curricula.models import Curriculum

    student = get_object_or_404(
        editable_queryset(Student.objects.all(), request.user), pk=pk)
    if not can_edit_family_or_global(request.user, student.family):
        raise Http404
    # Scope the SET too, exactly as the read view above does. Scoping only the
    # child leaves the set id a free parameter: posting another family's set_pk
    # created a sheet against their set and a work-log row carrying their
    # section title, curriculum and subject — readable back on /worklog/. The
    # per-child pin matters for the same reason it does on the read side: a set
    # pinned to a sibling is not this child's work.
    viewable_curricula = viewable_queryset(Curriculum.objects.all(), request.user)
    question_set = get_object_or_404(
        QuestionSet.objects.filter(
            lesson__chapter__curriculum__in=viewable_curricula,
        ).filter(Q(child=student) | Q(child__isnull=True)),
        pk=set_pk,
    )
    back = redirect("students:student_work_set", pk=pk, set_pk=set_pk)

    upload = request.FILES.get("project")
    with transaction.atomic():
        sheet, _ = ResponseSheet.objects.select_for_update().get_or_create(
            question_set=question_set, child=student,
        )
        if upload is not None:
            ext = os.path.splitext(upload.name)[1].lower()
            if ext not in ResponseSheet.PROJECT_EXTENSIONS:
                messages.error(request, "Use a photo, a PDF or a Word document.")
                return back
            if upload.size > ResponseSheet.PROJECT_MAX_BYTES:
                messages.error(request, "That file is over the %d MB limit."
                               % (ResponseSheet.PROJECT_MAX_BYTES // (1024 * 1024)))
                return back
            sheet.attachment = upload
            sheet.attachment_uploaded_at = timezone.now()
            sheet.completion_mode = ResponseSheet.ON_PAPER
            sheet.save(update_fields=["attachment", "attachment_uploaded_at",
                                      "completion_mode"])

        if sheet.is_submitted:
            messages.info(request, "That section was already complete.")
            return back
        if not sheet.has_project_file:
            messages.error(
                request,
                "Attach the paper copy first — a section can't be marked "
                "complete with nothing to show for it.")
            return back

        curriculum = question_set.lesson.chapter.curriculum
        sheet.work_entry = WorkLogEntry.objects.create(
            parent=student.parent,
            family=student.family,
            child=student,
            curriculum=curriculum,
            subject=curriculum.subject or "Literature",
            description="%s — completed on paper; %s attached."
                        % (question_set.title, sheet.project_filename),
            date=timezone.localdate(),
        )
        sheet.status = ResponseSheet.SUBMITTED
        sheet.submitted_at = timezone.now()
        sheet.completion_mode = ResponseSheet.ON_PAPER
        sheet.approved_at = timezone.now()
        sheet.approved_by = request.user
        sheet.save()

    messages.success(request, "Marked complete — %s is on the record."
                     % sheet.project_filename)
    return back


@login_required
def student_update(request, pk):
    """Edit an existing child profile (editors only)."""
    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"{student.first_name}'s profile has been updated.")
            return redirect("students:student_list")
    else:
        form = StudentForm(instance=student)

    return render(
        request, "students/student_form.html", {"form": form, "student": student, "action": "Edit"}
    )


@login_required
def student_delete(request, pk):
    """Delete a child profile with confirmation (editors only)."""
    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)

    if request.method == "POST":
        name = student.first_name
        try:
            student.delete()
        except ProtectedError as err:
            # Several host models PROTECT a child's records (worklog entries,
            # assignments). Name what's actually blocking so the parent isn't
            # sent chasing the wrong records. (Was an unguarded 500.)
            kinds = sorted({
                str(obj._meta.verbose_name_plural).lower()
                for obj in err.protected_objects
            })
            what = ", ".join(kinds) if kinds else "related records"
            messages.error(
                request,
                f"{name}'s profile can't be deleted yet because it still has "
                f"{what}. Remove those first, then try again.",
            )
            return redirect("students:student_list")
        # Student is gone; purge the lingua rows it can't cascade to (D-03).
        # Best-effort: a purge failure must NOT 500 an already-committed delete —
        # lingua_prune_orphans is the scheduled backstop that reconciles.
        try:
            lingua_services.delete_learner_for_student(pk)
        except Exception:  # noqa: BLE001 — backstop command cleans up orphans
            logger.exception("lingua purge failed for deleted student %s", pk)
        messages.success(request, f"{name}'s profile has been deleted.")
        return redirect("students:student_list")

    return render(request, "students/student_confirm_delete.html", {"student": student})


def _child_curriculum(request, student, curriculum_id):
    """Resolve a curriculum for a WRITE against ``student`` (HH-141).

    Beyond the normal viewable scope, require that the curriculum belongs to the
    child's own family (or is family-less content the requester owns). Without this a
    parent of two families could bind their child to the other family's curriculum."""
    from django.db.models import Q as _Q
    from curricula.models import Curriculum as _Curriculum
    qs = viewable_queryset(_Curriculum.objects.all(), request.user).filter(
        _Q(family=student.family) | _Q(family__isnull=True))
    return get_object_or_404(qs, pk=curriculum_id)


@login_required
def student_lessons(request, pk, curriculum_id):
    """Per-child lesson checklist for one curriculum (HH-141): each lesson's status
    (not started / in progress / completed / skipped) with mark controls, so a parent
    can mark lessons done, skip practice lessons based on performance, and see exactly
    where the child is. Read view; the mark buttons POST to lesson_mark."""
    from itertools import groupby

    from django.db.models import Count

    from curricula.models import (
        Curriculum, CurriculumPlacement, Lesson, LessonProgress, LessonWork)
    from tutor.models import QuestionSet, ResponseSheet

    student = get_object_or_404(viewable_queryset(Student.objects.all(), request.user), pk=pk)
    curriculum = get_object_or_404(
        viewable_queryset(Curriculum.objects.all(), request.user), pk=curriculum_id)
    can_edit = can_edit_family_or_global(request.user, student.family)

    lessons = list(
        Lesson.objects.filter(chapter__curriculum=curriculum)
        .exclude(lesson_type=Lesson.TYPE_OPENER)
        .select_related("chapter").order_by("chapter__number", "order")
    )
    marks = {lp.lesson_id: lp.status for lp in
             LessonProgress.objects.filter(child=student, lesson__in=lessons)}
    submitted = set(
        ResponseSheet.objects.filter(
            child=student, status=ResponseSheet.SUBMITTED,
            question_set__mode=QuestionSet.MODE_STUDENT, question_set__lesson__in=lessons,
        ).values_list("question_set__lesson_id", flat=True)
    )
    # One grouped count for the whole page — a per-row .count() would be one
    # query per lesson, and Saxon runs to 120 of them.
    work_counts = dict(
        LessonWork.objects.filter(child=student, lesson__in=lessons)
        .values_list("lesson_id").annotate(n=Count("id")).values_list("lesson_id", "n")
    )
    placement = CurriculumPlacement.objects.filter(child=student, curriculum=curriculum).first()
    # Resolve ONCE and hand the result to both derived readings below — the checklist,
    # the "Now" pointer and the progress bar all need it, and each recomputing it meant
    # the same three queries three times per page load.
    resolution = placement.resolved_lesson_ids() if placement else ([], set())
    _, resolved = resolution
    actionable = placement.current_actionable_lesson(resolution) if placement else None
    current_id = actionable.id if actionable else None
    # Lessons BELOW the parent's placement pointer already count as done (the floor),
    # so they must render TICKED — otherwise the bar says "16 done" while every box
    # sits empty, which reads as broken.
    for lesson in lessons:
        lesson.mark_status = (
            marks.get(lesson.id)
            or ("submitted" if lesson.id in submitted else "")
            or ("completed" if lesson.id in resolved else "not_started")
        )
        lesson.is_current = lesson.id == current_id
        lesson.is_practice = lesson.lesson_type == Lesson.TYPE_PRACTICE
        lesson.work_count = work_counts.get(lesson.id, 0)

    chapters = [
        {"heading": f"Chapter {num} · {items[0].chapter.title}", "lessons": items}
        for (num, _t), group in groupby(lessons, key=lambda x: (x.chapter.number, x.chapter.title))
        for items in [list(group)]
    ]
    # "Now" is DERIVED live (first unresolved lesson, skips passed over) — the stored
    # placement pointer is the parent's placement and is never auto-rewritten.
    prog = placement.progress(resolution) if placement else {
        "done": 0, "total": len(lessons), "pct": 0, "skipped": 0}
    return render(request, "students/student_lessons.html", {
        "student": student, "curriculum": curriculum, "chapters": chapters,
        "can_edit": can_edit, "progress": prog,
        "current_lesson": actionable,
        "finished": bool(placement and actionable is None and lessons),
    })


def _lesson_for_child(request, pk, curriculum_id, lesson_id, *, editable):
    """Resolve (student, curriculum, lesson) for a per-lesson work upload (HH-167).

    The lesson is looked up THROUGH the resolved curriculum, so a lesson id from
    another family's course 404s instead of quietly attaching a child's work to
    a course she is not enrolled in.
    """
    from curricula.models import Lesson

    base = editable_queryset if editable else viewable_queryset
    student = get_object_or_404(base(Student.objects.all(), request.user), pk=pk)
    # The curriculum is pinned to the CHILD's family on read as well as on write.
    # Resolving GET with a plain viewable_queryset leaked nothing, but it rendered a
    # dead end: someone who parents family A and teaches family B got family B's
    # lesson title shown as child A's page, with an upload form whose POST then 404s.
    curriculum = _child_curriculum(request, student, curriculum_id)
    lesson = get_object_or_404(
        Lesson.objects.filter(chapter__curriculum=curriculum).select_related("chapter"),
        pk=lesson_id)
    return student, curriculum, lesson


@login_required
def lesson_work(request, pk, curriculum_id, lesson_id):
    """Show and add the finished work for ONE lesson (HH-167).

    Maths is done on paper. Saxon and Dimensions carry no question sets, so
    before this there was nowhere to file a chapter test except a work-log entry
    keyed on a DATE — the wrong index when a reviewer asks to see Lesson 71.

    GET renders the file list; POST adds one. Deliberately its own page rather
    than a control on the checklist: that page is one big checkbox form, and a
    file input cannot be nested inside it.
    """
    import os

    from curricula.models import LessonWork

    editable = request.method == "POST"
    student, curriculum, lesson = _lesson_for_child(
        request, pk, curriculum_id, lesson_id, editable=editable)
    can_edit = can_edit_family_or_global(request.user, student.family)
    back = redirect("students:lesson_work", pk=pk, curriculum_id=curriculum_id,
                    lesson_id=lesson_id)

    if request.method == "POST":
        upload = request.FILES.get("file")
        if upload is None:
            messages.error(request, "Choose a file first.")
            return back
        ext = os.path.splitext(upload.name)[1].lower()
        if ext not in LessonWork.WORK_EXTENSIONS:
            messages.error(
                request,
                "That file type isn't one we can take. Use a photo (JPG, PNG, "
                "HEIC), a PDF, or a Word document.")
            return back
        if upload.size > LessonWork.WORK_MAX_BYTES:
            messages.error(
                request,
                "That file is too big (%.0f MB). The limit is %d MB."
                % (upload.size / 1024 / 1024,
                   LessonWork.WORK_MAX_BYTES // (1024 * 1024)))
            return back
        LessonWork.objects.create(
            lesson=lesson, child=student, family=student.family, file=upload,
            caption=(request.POST.get("caption", "") or "").strip()[:200],
            uploaded_by=request.user, source=LessonWork.BY_PARENT,
        )
        messages.success(request, "Saved to %s." % lesson.code)
        return back

    uploads = list(
        LessonWork.objects.filter(lesson=lesson, child=student)
        .select_related("uploaded_by")
    )
    return render(request, "students/lesson_work.html", {
        "student": student, "curriculum": curriculum, "lesson": lesson,
        "uploads": uploads, "can_edit": can_edit,
        "max_mb": LessonWork.WORK_MAX_BYTES // (1024 * 1024),
        "accept": ",".join(LessonWork.WORK_EXTENSIONS),
    })


@login_required
@require_POST
def lesson_work_delete(request, pk, curriculum_id, lesson_id):
    """Remove one uploaded file (HH-167) — a blurred photo, or the wrong lesson.

    Scoped through the same resolver as the upload, and the row itself is
    re-filtered on child AND lesson so an id belonging to a sibling's copy of
    the same lesson cannot be deleted by guessing.
    """
    from curricula.models import LessonWork

    student, _curriculum, lesson = _lesson_for_child(
        request, pk, curriculum_id, lesson_id, editable=True)
    work_pk = (request.POST.get("work") or "").strip()
    if not (work_pk.isdigit() and work_pk.isascii()):
        raise Http404  # a non-numeric pk must 404, not 500
    work = get_object_or_404(
        LessonWork.objects.filter(lesson=lesson, child=student), pk=work_pk)
    name = work.filename
    work.file.delete(save=False)
    work.delete()
    messages.success(request, "Removed %s." % name)
    return redirect("students:lesson_work", pk=pk, curriculum_id=curriculum_id,
                    lesson_id=lesson_id)


@login_required
@require_POST
def lesson_mark(request, pk, curriculum_id):
    """Mark one lesson completed/skipped, or reset it (HH-141). Family-scoped write
    (editable_queryset 404s a view-only role). Keeps the placement pointer canonical."""
    from curricula.models import Curriculum, CurriculumPlacement, Lesson, LessonProgress

    action = request.POST.get("action")
    if action not in ("reset", LessonProgress.COMPLETED, LessonProgress.SKIPPED):
        raise Http404  # unknown action: change nothing
    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)
    curriculum = _child_curriculum(request, student, curriculum_id)
    lesson_pk = (request.POST.get("lesson") or "").strip()
    if not (lesson_pk.isdigit() and lesson_pk.isascii()):
        raise Http404  # a non-numeric pk must 404, not 500
    lesson = get_object_or_404(
        Lesson.objects.filter(chapter__curriculum=curriculum), pk=lesson_pk)
    if action == "reset":
        LessonProgress.objects.filter(child=student, lesson=lesson).delete()
    else:
        LessonProgress.objects.update_or_create(
            child=student, lesson=lesson,
            defaults={"status": action, "marked_by": request.user,
                      "note": (request.POST.get("note", "") or "")[:300]})
    # Ensure a placement exists so progress has something to hang off, but NEVER
    # rewrite its current_lesson: that pointer is the PARENT's placement, and
    # everything before it counts as done (the floor). Auto-advancing it made "Undo" a
    # permanent no-op (the floor re-resolved the un-done lesson), silently rewrote an
    # opener placement, and nulled the pointer on the last lesson. "Where the child is
    # now" is derived live by CurriculumPlacement.current_actionable_lesson().
    CurriculumPlacement.objects.get_or_create(child=student, curriculum=curriculum)
    return redirect("students:student_lessons", pk=pk, curriculum_id=curriculum_id)


@login_required
@require_POST
def lessons_skip_practice(request, pk, curriculum_id):
    """Skip all remaining (unresolved) PRACTICE lessons in one click (HH-141)."""
    from curricula.models import Curriculum, CurriculumPlacement, Lesson, LessonProgress

    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)
    curriculum = _child_curriculum(request, student, curriculum_id)
    placement, _ = CurriculumPlacement.objects.get_or_create(child=student, curriculum=curriculum)
    ids, resolved = placement.resolved_lesson_ids()
    practice = (Lesson.objects.filter(chapter__curriculum=curriculum,
                                      lesson_type=Lesson.TYPE_PRACTICE, id__in=ids)
                .exclude(id__in=resolved))
    n = 0
    for lesson in practice:
        LessonProgress.objects.update_or_create(
            child=student, lesson=lesson,
            defaults={"status": LessonProgress.SKIPPED, "marked_by": request.user})
        n += 1
    messages.success(request, f"Skipped {n} remaining practice lesson{'' if n == 1 else 's'}.")
    return redirect("students:student_lessons", pk=pk, curriculum_id=curriculum_id)


@login_required
@require_POST
def lessons_save(request, pk, curriculum_id):
    """Save the whole lesson checklist in one submit (HH-142).

    The parent's mental model is a checklist: tick the lessons the child finished.
    So the page is ONE form of checkboxes and this view reconciles the full state —
    ``done`` holds the lesson ids that are now ticked, ``skip`` the ones marked
    skipped. Anything previously marked but absent from both is cleared, which makes
    un-ticking work exactly the way un-ticking should. Works with no JavaScript.
    """
    from curricula.models import CurriculumPlacement, Lesson, LessonProgress

    student = get_object_or_404(editable_queryset(Student.objects.all(), request.user), pk=pk)
    curriculum = _child_curriculum(request, student, curriculum_id)

    valid = set(
        Lesson.objects.filter(chapter__curriculum=curriculum)
        .exclude(lesson_type=Lesson.TYPE_OPENER).values_list("id", flat=True)
    )

    def _ids(field):
        out = set()
        for raw in request.POST.getlist(field):
            raw = (raw or "").strip()
            if raw.isdigit() and raw.isascii() and int(raw) in valid:
                out.add(int(raw))
        return out

    done = _ids("done")
    skipped = _ids("skip") - done            # ticking "done" wins over a stale skip
    keep = done | skipped

    # Clear marks the parent un-ticked, then upsert the current state.
    LessonProgress.objects.filter(child=student, lesson_id__in=valid - keep).delete()
    for lesson_id in keep:
        LessonProgress.objects.update_or_create(
            child=student, lesson_id=lesson_id,
            defaults={"status": (LessonProgress.COMPLETED if lesson_id in done
                                 else LessonProgress.SKIPPED),
                      "marked_by": request.user},
        )
    CurriculumPlacement.objects.get_or_create(child=student, curriculum=curriculum)
    messages.success(
        request,
        f"Saved — {len(done)} lesson{'' if len(done) == 1 else 's'} done"
        + (f", {len(skipped)} skipped." if skipped else "."),
    )
    return redirect("students:student_lessons", pk=pk, curriculum_id=curriculum_id)
