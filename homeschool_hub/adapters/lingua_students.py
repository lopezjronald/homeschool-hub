"""Host-side Student→Learner resolution (D-04).

The ONLY place the host maps a child onto a lingua Learner. The portal and the parent
Spanish pages both import from here, so band inference and lazy provisioning have one
definition. lingua itself still imports no host model (D-03/D-04).
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
