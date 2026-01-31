"""Centralized family-membership permission helpers.

Vocabulary:
- *viewable*: user has ANY membership (parent / teacher / admin) in the family.
- *editable*: user has a parent OR admin membership in the family.

Legacy fallback: records where ``family IS NULL`` are only accessible to the
user referenced by the record's ``parent`` FK.
"""

from django.db.models import Q

from core.models import FamilyMembership

EDIT_ROLES = ("parent", "admin")
VIEW_ROLES = ("parent", "teacher", "admin")


def viewable_family_ids(user):
    """Return a flat queryset of Family IDs the user can view."""
    return (
        FamilyMembership.objects
        .filter(user=user, role__in=VIEW_ROLES)
        .values_list("family_id", flat=True)
    )


def editable_family_ids(user):
    """Return a flat queryset of Family IDs the user can edit."""
    return (
        FamilyMembership.objects
        .filter(user=user, role__in=EDIT_ROLES)
        .values_list("family_id", flat=True)
    )


def can_view_family(user, family):
    """Return True if user has any membership role in the given family."""
    if family is None:
        return False
    return FamilyMembership.objects.filter(
        user=user, family=family, role__in=VIEW_ROLES,
    ).exists()


def can_edit_family(user, family):
    """Return True if user has parent/admin role in the given family."""
    if family is None:
        return False
    return FamilyMembership.objects.filter(
        user=user, family=family, role__in=EDIT_ROLES,
    ).exists()


def viewable_queryset(qs, user, family_field="family", parent_field="parent"):
    """Filter a queryset to records the user may *view*.

    Includes:
    - records where family is in the user's viewable families
    - records where family IS NULL and parent == user (legacy fallback)
    """
    family_lookup = f"{family_field}__in"
    null_lookup = f"{family_field}__isnull"
    return qs.filter(
        Q(**{family_lookup: viewable_family_ids(user)})
        | Q(**{null_lookup: True, parent_field: user})
    )


def editable_queryset(qs, user, family_field="family", parent_field="parent"):
    """Filter a queryset to records the user may *edit* (create/update/delete).

    Includes:
    - records where family is in the user's editable families
    - records where family IS NULL and parent == user (legacy fallback)
    """
    family_lookup = f"{family_field}__in"
    null_lookup = f"{family_field}__isnull"
    return qs.filter(
        Q(**{family_lookup: editable_family_ids(user)})
        | Q(**{null_lookup: True, parent_field: user})
    )


def scoped_queryset(qs, user, family, family_field="family", parent_field="parent"):
    """Filter a queryset to records in the selected *family* only.

    - If *family* is None (legacy user with no memberships), returns only
      records where family IS NULL and parent == user.
    - Parents/admins also see their legacy null-family records alongside
      the selected family's records.
    - Teachers see only the selected family's records.
    """
    if family is None:
        null_lookup = f"{family_field}__isnull"
        return qs.filter(**{null_lookup: True, parent_field: user})

    family_filter = Q(**{family_field: family})

    if user_can_edit(user):
        null_lookup = f"{family_field}__isnull"
        return qs.filter(
            family_filter | Q(**{null_lookup: True, parent_field: user})
        )
    return qs.filter(family_filter)


def user_can_edit(user):
    """Return True if the user has edit rights in at least one family.

    Legacy fallback: if the user has NO family memberships at all,
    they are treated as a standalone parent and can edit.
    """
    memberships = FamilyMembership.objects.filter(user=user)
    if not memberships.exists():
        return True  # Legacy user with no memberships
    return memberships.filter(role__in=EDIT_ROLES).exists()
