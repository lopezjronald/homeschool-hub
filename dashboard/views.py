from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from assignments.models import Assignment
from curricula.models import Curriculum
from students.models import Student


@login_required
def dashboard_view(request):
    today = date.today()

    # Base queryset: only this parent's assignments
    qs = Assignment.objects.filter(parent=request.user).select_related(
        "child", "curriculum"
    )

    # --- Read filter params ---------------------------------------------------
    child_id = request.GET.get("child_id", "")
    curriculum_id = request.GET.get("curriculum_id", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    has_filters = any([child_id, curriculum_id, start_date, end_date])
    date_filter_active = bool(start_date or end_date)

    # --- Apply filters --------------------------------------------------------
    if child_id:
        qs = qs.filter(child_id=child_id, child__parent=request.user)

    if curriculum_id:
        qs = qs.filter(
            curriculum_id=curriculum_id, curriculum__parent=request.user
        )

    if date_filter_active:
        # Exclude assignments with null due_date when date filtering
        qs = qs.filter(due_date__isnull=False)
        if start_date:
            qs = qs.filter(due_date__gte=start_date)
        if end_date:
            qs = qs.filter(due_date__lte=end_date)

    # --- Aggregate summary metrics --------------------------------------------
    summary = qs.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="complete")),
        overdue=Count(
            "id", filter=Q(due_date__lt=today) & ~Q(status="complete")
        ),
    )
    summary["not_completed"] = summary["total"] - summary["completed"]

    # Progress percentage (avoid division by zero)
    if summary["total"] > 0:
        summary["progress_pct"] = round(
            summary["completed"] / summary["total"] * 100
        )
    else:
        summary["progress_pct"] = 0

    # --- Breakdown by child ---------------------------------------------------
    by_child = (
        qs.values("child__id", "child__first_name", "child__last_name")
        .annotate(
            total=Count("id"),
            completed=Count("id", filter=Q(status="complete")),
            overdue=Count(
                "id", filter=Q(due_date__lt=today) & ~Q(status="complete")
            ),
        )
        .order_by("child__first_name")
    )

    # --- Breakdown by curriculum ----------------------------------------------
    by_curriculum = (
        qs.values("curriculum__id", "curriculum__name")
        .annotate(
            total=Count("id"),
            completed=Count("id", filter=Q(status="complete")),
            overdue=Count(
                "id", filter=Q(due_date__lt=today) & ~Q(status="complete")
            ),
        )
        .order_by("curriculum__name")
    )

    # --- Assignment list for drill-down ---------------------------------------
    assignments = qs.order_by("due_date", "title")

    # --- Filter dropdown options (scoped to this user) ------------------------
    children = Student.objects.filter(parent=request.user).order_by(
        "first_name"
    )
    curricula = Curriculum.objects.filter(parent=request.user).order_by("name")

    context = {
        "summary": summary,
        "by_child": by_child,
        "by_curriculum": by_curriculum,
        "assignments": assignments,
        "children": children,
        "curricula": curricula,
        "today": today,
        # Current filter values (for form state)
        "selected_child": child_id,
        "selected_curriculum": curriculum_id,
        "start_date": start_date,
        "end_date": end_date,
        "has_filters": has_filters,
    }
    return render(request, "dashboard/dashboard.html", context)
