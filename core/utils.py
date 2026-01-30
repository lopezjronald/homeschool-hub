from django.utils import timezone

from core.models import Family


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
