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


def get_inbox_buckets(request, family):
    """The parent action inbox: everything needing the signed-in editor.

    Four buckets, all derived from live state (nothing stored) and scoped to the
    selected family: finalize proficiency, work still to grade, draft materials to
    approve, and activity check-ins due. Read-only reviewers get an empty inbox.
    Returns ``{"buckets": [...], "total": int, "new": int}`` where each bucket is
    ``{"key","title","icon","kind","items":[...]}``. "link" items are dicts
    ``{label, sub, url, cta, created_at, is_new}``; "activity" items are
    ``ExternalActivity`` objects (the template renders log/snooze/mute).
    """
    from accounts.models import UserProfile
    from activities.models import ExternalActivity
    from curricula.models import Curriculum
    from core.permissions import scoped_queryset, user_can_edit
    from students.models import Student
    from tutor.models import MasteryAssessment, Material
    from worklog.models import WorkLogEntry

    user = request.user
    if not user_can_edit(user):
        return {"buckets": [], "total": 0, "new": 0}

    seen = UserProfile.get_for(user).inbox_seen_at

    def is_new(dt):
        # Null seen (never opened) reads as "nothing new" — a calm first visit.
        return bool(seen and dt and dt > seen)

    children = scoped_queryset(Student.objects.all(), user, family)
    curricula = scoped_queryset(Curriculum.objects.all(), user, family)

    # 1) Finalize proficiency — every DRAFT assessment for the family's children
    #    (note: unlike the hub card, we do NOT filter graded_by, so parent-started
    #    drafts also surface).
    drafts = (
        MasteryAssessment.objects
        .filter(status=MasteryAssessment.DRAFT, work_entry__child__in=children)
        .select_related("work_entry", "work_entry__child")
        .order_by("-created_at")
    )
    finalize = [{
        "label": f"{a.work_entry.child.first_name} · {a.work_entry.subject}",
        "sub": (a.ai_encouragement or a.ai_summary or "")[:100],
        "url": reverse("tutor:assess_detail", args=[a.pk]),
        "cta": "Review & finalize",
        "created_at": a.created_at,
        "is_new": is_new(a.created_at),
    } for a in drafts]

    # 2) Work to grade — a submitted sheet exists but no assessment yet.
    ungraded_entries = (
        scoped_queryset(WorkLogEntry.objects.all(), user, family)
        .filter(response_sheets__isnull=False, assessments__isnull=True)
        .select_related("child")
        .distinct()
        .order_by("-date", "-created_at")
    )
    ungraded = [{
        "label": f"{e.child.first_name} · {e.subject}",
        "sub": (e.description or "")[:100],
        "url": reverse("tutor:assess_create", args=[e.pk]),
        "cta": "Grade it",
        "created_at": e.created_at,
        "is_new": is_new(e.created_at),
    } for e in ungraded_entries]

    # 3) Draft materials — awaiting approval before the child can see them.
    draft_materials = (
        Material.objects
        .filter(status=Material.DRAFT, lesson__chapter__curriculum__in=curricula)
        .select_related("lesson", "lesson__chapter", "lesson__chapter__curriculum")
        .order_by("-created_at")
    )
    materials = [{
        "label": m.title,
        "sub": m.lesson.chapter.curriculum.name if m.lesson_id else "",
        "url": reverse("tutor:material_detail", args=[m.pk]),
        "cta": "Review & approve",
        "created_at": m.created_at,
        "is_new": is_new(m.created_at),
    } for m in draft_materials]

    # 4) Activity check-ins due — the recurring nudge (Python is_due, like the hub).
    due_activities = [
        a for a in scoped_queryset(ExternalActivity.objects.all(), user, family) if a.is_due
    ]

    buckets = []
    if finalize:
        buckets.append({"key": "finalize", "title": "Finalize proficiency",
                        "icon": "bi-patch-check", "kind": "link", "items": finalize})
    if ungraded:
        buckets.append({"key": "ungraded", "title": "Work to grade",
                        "icon": "bi-pencil-square", "kind": "link", "items": ungraded})
    if materials:
        buckets.append({"key": "materials", "title": "Materials to approve",
                        "icon": "bi-file-earmark-check", "kind": "link", "items": materials})
    if due_activities:
        buckets.append({"key": "activities", "title": "Activity check-ins",
                        "icon": "bi-calendar-check", "kind": "activity", "items": due_activities})

    total = len(finalize) + len(ungraded) + len(materials) + len(due_activities)
    new = sum(1 for x in (finalize + ungraded + materials) if x["is_new"])
    return {"buckets": buckets, "total": total, "new": new}


def inbox_count(request, family):
    """Cheap nav-badge number — three COUNT queries (proficiency + ungraded +
    materials). Excludes activity check-ins (``is_due`` is Python-only). Zero for
    read-only reviewers. Kept lean because it runs on every authenticated page.
    """
    from curricula.models import Curriculum
    from core.permissions import scoped_queryset, user_can_edit
    from students.models import Student
    from tutor.models import MasteryAssessment, Material
    from worklog.models import WorkLogEntry

    user = request.user
    if not user_can_edit(user):
        return 0

    children = scoped_queryset(Student.objects.all(), user, family)
    curricula = scoped_queryset(Curriculum.objects.all(), user, family)
    return (
        MasteryAssessment.objects.filter(
            status=MasteryAssessment.DRAFT, work_entry__child__in=children,
        ).count()
        + scoped_queryset(WorkLogEntry.objects.all(), user, family)
        .filter(response_sheets__isnull=False, assessments__isnull=True)
        .distinct().count()
        + Material.objects.filter(
            status=Material.DRAFT, lesson__chapter__curriculum__in=curricula,
        ).count()
    )
