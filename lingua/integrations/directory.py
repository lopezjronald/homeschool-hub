"""UserDirectory — the SINGLE point in lingua that reads a host model.

D-04: all host *identity* coupling is concentrated here. A learner is carried
through lingua as a plain ``host_student_id`` (D-03); these functions are the
only place that resolves it against the host's ``students.Student``. To extract
lingua as a standalone product, this one file is what you reimplement.
"""
from students.models import Student  # the ONE permitted host import in lingua


def learner_exists(host_student_id):
    """True if the host still has a Student with this pk (used to validate a
    host_student_id at the service boundary and to prune orphans — LGA-20)."""
    return Student.objects.filter(pk=host_student_id).exists()


def get_learner_display(host_student_id):
    """Display info for a learner, or None if the host Student is gone.

    Returns ``{"name": str, "grade_level": str}``. ``grade_level`` is the host's
    LEVEL code (e.g. "G03") — the child's school Level, distinct from a lingua
    content level.
    """
    row = (
        Student.objects
        .filter(pk=host_student_id)
        .values("first_name", "last_name", "grade_level")
        .first()
    )
    if row is None:
        return None
    name = f"{row['first_name']} {row['last_name'] or ''}".strip()
    return {"name": name, "grade_level": row["grade_level"]}


def list_for_family(host_family_id):
    """host_student_id list for a host family (drives family-scoped views)."""
    return list(
        Student.objects.filter(family_id=host_family_id).values_list("pk", flat=True)
    )


def family_children(host_family_id):
    """Every child in a host family, as plain dicts (no host model escapes this file).

    Includes children who have never opened Español — a Learner row is only created
    the first time something is logged, and the parent must still be able to log that
    first book for them. Ordered by name for a stable picker.
    """
    if not host_family_id:
        return []
    rows = (
        Student.objects
        .filter(family_id=host_family_id)
        .order_by("first_name", "last_name")
        .values("pk", "first_name", "last_name", "grade_level", "date_of_birth")
    )
    return [dict(r) for r in rows]


def child_in_family(host_student_id, host_family_id):
    """One child resolved INSIDE the family, or None.

    The posted child id is never trusted: scoping the lookup here is what stops a
    parent from filing work against another family's child.
    """
    if not host_student_id or not host_family_id:
        return None
    row = (
        Student.objects
        .filter(pk=host_student_id, family_id=host_family_id)
        .values("pk", "first_name", "last_name", "grade_level", "date_of_birth")
        .first()
    )
    return dict(row) if row else None


def find_student_id(first_name):
    """host_student_id for a child matched by first name, or None.

    Authoring-time convenience for seed commands that target one named child, so
    they don't have to reach for a host model themselves (D-04). Returns None when
    the name matches nothing OR more than one child: this app is multi-family, and
    silently picking one of two same-named children would scope private material —
    a tutor's homework, say — to somebody else's kid.
    """
    name = (first_name or "").strip()
    if not name:
        return None
    ids = list(
        Student.objects
        .filter(first_name__iexact=name)
        .values_list("pk", flat=True)[:2]
    )
    return ids[0] if len(ids) == 1 else None


def existing_student_ids(host_student_ids):
    """The subset of the given ids that still exist as host Students (one query).
    Used by lingua_prune_orphans to find orphaned learners efficiently."""
    return set(
        Student.objects
        .filter(pk__in=list(host_student_ids))
        .values_list("pk", flat=True)
    )
