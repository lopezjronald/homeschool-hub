"""Host-side Student→Learner resolution (D-04).

Where the host maps a *host model* onto a lingua Learner: the kid portal hands its
Student straight here. The parent Spanish pages never hold a Student — they read plain
dicts from ``lingua.integrations.directory`` and call ``services.learner_for_child`` —
so both paths land on the same provisioning and the same band rule
(``services.band_for_dob``), which is the one definition. lingua itself imports no host
model (D-03/D-04).
"""
from lingua import services as lingua_services
from students.models import Student


def infer_band(student):
    """Pick a Lingua track band from the child's age. The rule itself is lingua's
    (services.band_for_dob) — this only pulls the field off the host model, so the
    two entry points can't drift apart."""
    return lingua_services.band_for_dob(getattr(student, "date_of_birth", None))


def learner_for(student):
    """The lingua Learner for this student, provisioned on first use (idempotent)."""
    return lingua_services.get_or_create_learner(student.pk, infer_band(student))


def children_of(family):
    """EVERY child in the family — including ones who have never opened Español.

    The parent book-logging UI must list all of them; a child only gets a Learner row
    the first time something is actually logged for them.
    """
    if family is None:
        return []
    return list(Student.objects.filter(family=family).order_by("first_name", "last_name"))
