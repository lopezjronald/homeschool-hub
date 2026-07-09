"""Hub services — new-parent onboarding / setup progress.

The setup checklist is the app's front door for a brand-new parent. It drives
toward *activation*: the first finalized mastery review, which is the moment the
whole loop has run once AND the first durable line on the charter report exists.
Everything here is read-only and cheap (a handful of ``.exists()`` probes).
"""

from django.urls import reverse


def get_setup_progress(request, family):
    """Return the setup-checklist state for the signed-in parent hub.

    Four milestones, in order: add a child → set up a subject → hand over the
    kid portal → confirm mastery. Returns a dict::

        {"steps": [...], "done_count", "total", "percent", "complete"}

    Read-only reviewers (no edit rights anywhere) get ``complete=True`` with no
    steps, so the card never shows for them.
    """
    from core.permissions import scoped_queryset, user_can_edit
    from curricula.models import Curriculum, CurriculumPlacement
    from students.models import Student
    from tutor.models import MasteryAssessment
    from worklog.models import WorkLogEntry

    user = request.user
    if not user_can_edit(user):
        return {"steps": [], "done_count": 0, "total": 0, "percent": 100, "complete": True}

    students = scoped_queryset(Student.objects.all(), user, family)
    student_ids = list(students.values_list("id", flat=True))

    has_child = bool(student_ids)
    has_subject = bool(
        scoped_queryset(Curriculum.objects.all(), user, family).exists()
        or (student_ids and CurriculumPlacement.objects.filter(child_id__in=student_ids).exists())
    )
    has_work = bool(
        student_ids and WorkLogEntry.objects.filter(child_id__in=student_ids).exists()
    )
    has_mastery = bool(
        student_ids
        and MasteryAssessment.objects.filter(
            work_entry__child_id__in=student_ids,
            status=MasteryAssessment.FINALIZED,
        ).exists()
    )

    steps = [
        {
            "key": "child",
            "label": "Add your first child",
            "why": "Set each child's Level — every subject then runs at its own grade.",
            "done": has_child,
            "url": reverse("students:student_list" if has_child else "students:student_create"),
            "cta": "Add a child",
        },
        {
            "key": "subject",
            "label": "Set up a subject",
            "why": "Use a built-in course or add your own — tick “done on an external website” for online subjects.",
            "done": has_subject,
            "url": reverse("curricula:curriculum_list" if has_subject else "curricula:curriculum_create"),
            "cta": "Add a subject",
        },
        {
            "key": "portal",
            "label": "Open the kid portal — hand over the device",
            "why": "On a child's page tap “Open portal” (or bookmark the link on their tablet). They see only their own work.",
            "done": has_work,
            "url": reverse("students:student_list"),
            "cta": "Open a child's portal",
        },
        {
            "key": "mastery",
            "label": "Review feedback & confirm mastery",
            "why": "When your child turns in work, confirm the level — that's what builds the record your charter can trust.",
            "done": has_mastery,
            "url": reverse("dashboard:dashboard"),
            "cta": "See progress",
        },
    ]

    done_count = sum(1 for s in steps if s["done"])
    total = len(steps)

    # Mark the first not-yet-done step so the card can foreground one action.
    next_marked = False
    for s in steps:
        s["is_next"] = False
        if not s["done"] and not next_marked:
            s["is_next"] = True
            next_marked = True

    return {
        "steps": steps,
        "done_count": done_count,
        "total": total,
        "percent": int(round(done_count / total * 100)) if total else 100,
        "complete": done_count == total,
    }
