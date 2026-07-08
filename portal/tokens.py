"""Signed portal tokens — tokenless student access, one child per link.

Mirrors the assignments magic-link pattern (django.core.signing). A parent
generates the link from the child's profile and puts it on the kid's device;
the token only unlocks that child's own portal. Long-lived by design (it's a
bookmark for a kid), but revocable by rotating SECRET_KEY if ever needed.
"""

from django.core import signing

from students.models import Student

SALT = "student-portal"
MAX_AGE = 180 * 24 * 60 * 60  # 6 months — long enough to bookmark, short enough to age out


def make_portal_token(student):
    """Return a signed token that unlocks this student's portal.

    The token carries the child's rotatable ``portal_key``; rotating that key
    (e.g. via ``portal_link --rotate``) instantly invalidates any link that
    leaked, without a global SECRET_KEY change.
    """
    return signing.dumps({"student_id": student.pk, "k": student.portal_key}, salt=SALT)


def student_from_token(token, max_age=MAX_AGE):
    """Resolve a portal token to a Student, or None if invalid/expired/revoked."""
    try:
        data = signing.loads(token, salt=SALT, max_age=max_age)
        student = Student.objects.select_related("family", "parent").get(pk=data["student_id"])
    except (signing.BadSignature, signing.SignatureExpired, KeyError, TypeError, Student.DoesNotExist):
        return None
    if data.get("k") != student.portal_key:
        return None  # link was revoked (key rotated)
    return student
