from django.utils import timezone

from core.models import Family, FamilyMembership


def get_active_family(user):
    """Return the user's primary family (first parent-role membership by id).

    Returns None if the user has no family membership with role='parent'.
    """
    membership = (
        user.family_memberships
        .filter(role="parent")
        .select_related("family")
        .order_by("id")
        .first()
    )
    if membership is not None:
        return membership.family
    return None


def get_user_families(user):
    """Return queryset of families the user belongs to, ordered by id."""
    family_ids = FamilyMembership.objects.filter(
        user=user,
    ).values_list("family_id", flat=True)
    return Family.objects.filter(pk__in=family_ids).order_by("id")


def get_selected_family(request):
    """Return the currently selected family for the request user.

    Resolution order:
    1. GET param ``family_id`` (validated + stored to session)
    2. Session ``selected_family_id``
    3. First parent-role family (by id)
    4. First any-role family (by id)
    5. None (legacy user with no memberships)

    Result is cached on ``request._selected_family``.
    """
    if hasattr(request, "_selected_family"):
        return request._selected_family

    user = request.user
    if not user.is_authenticated:
        request._selected_family = None
        return None

    from core.permissions import can_view_family

    # 1. GET param
    family_id_str = request.GET.get("family_id")
    if family_id_str:
        try:
            family = Family.objects.get(pk=int(family_id_str))
            if can_view_family(user, family):
                request.session["selected_family_id"] = family.id
                request._selected_family = family
                return family
        except (Family.DoesNotExist, ValueError, TypeError):
            pass

    # 2. Session
    session_id = request.session.get("selected_family_id")
    if session_id is not None:
        try:
            family = Family.objects.get(pk=session_id)
            if can_view_family(user, family):
                request._selected_family = family
                return family
        except Family.DoesNotExist:
            pass
        # Stale session value — clear it
        del request.session["selected_family_id"]

    # 3. First parent-role family
    membership = (
        FamilyMembership.objects
        .filter(user=user, role="parent")
        .select_related("family")
        .order_by("id")
        .first()
    )
    if membership:
        request.session["selected_family_id"] = membership.family.id
        request._selected_family = membership.family
        return membership.family

    # 4. First any-role family
    membership = (
        FamilyMembership.objects
        .filter(user=user)
        .select_related("family")
        .order_by("id")
        .first()
    )
    if membership:
        request.session["selected_family_id"] = membership.family.id
        request._selected_family = membership.family
        return membership.family

    # 5. Legacy user
    request._selected_family = None
    return None


def _family_name_for_user(user):
    """Derive a human-readable family name from a user record."""
    if user.last_name:
        return f"{user.last_name} Family"
    if user.email:
        return f"{user.email} Family"
    return f"Family for {user.pk}"


def backfill_families(apps, schema_editor):
    """Create Family + Membership per parent user and set family FK on owned rows.

    Idempotent: skips users who already have a parent-role membership and
    skips resource rows where family is already set.
    """
    User = apps.get_model("accounts", "CustomUser")
    FamilyModel = apps.get_model("core", "Family")
    FamilyMembership = apps.get_model("core", "FamilyMembership")
    Student = apps.get_model("students", "Student")
    Curriculum = apps.get_model("curricula", "Curriculum")
    Assignment = apps.get_model("assignments", "Assignment")

    # Collect distinct user ids who own at least one resource
    parent_ids = set()
    parent_ids.update(Student.objects.values_list("parent_id", flat=True).distinct())
    parent_ids.update(Curriculum.objects.values_list("parent_id", flat=True).distinct())
    parent_ids.update(Assignment.objects.values_list("parent_id", flat=True).distinct())

    now = timezone.now()

    for user in User.objects.filter(pk__in=parent_ids).iterator():
        # Find or create a family for this user
        membership = (
            FamilyMembership.objects
            .filter(user=user, role="parent")
            .select_related("family")
            .order_by("id")
            .first()
        )

        if membership is not None:
            family = membership.family
        else:
            family = FamilyModel.objects.create(
                name=_family_name_for_user(user),
                created_at=now,
                updated_at=now,
            )
            FamilyMembership.objects.create(
                user=user,
                family=family,
                role="parent",
                created_at=now,
            )

        # Backfill only rows where family IS NULL
        Student.objects.filter(parent=user, family__isnull=True).update(family=family)
        Curriculum.objects.filter(parent=user, family__isnull=True).update(family=family)
        Assignment.objects.filter(parent=user, family__isnull=True).update(family=family)
