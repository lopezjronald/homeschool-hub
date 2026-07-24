import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.permissions import viewable_queryset, editable_queryset, scoped_queryset, user_can_edit
from core.utils import get_active_family, get_selected_family

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
    can_edit = user_can_edit(request.user)
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
            student.family = get_active_family(request.user)
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
    can_edit = user_can_edit(request.user)

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

    return render(request, "students/student_detail.html", {
        "student": student,
        "can_edit": can_edit,
        "curricula": curricula,
        "portal_url": portal_url,
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
        "can_edit": user_can_edit(request.user),
    })


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
