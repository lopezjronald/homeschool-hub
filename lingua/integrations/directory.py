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
