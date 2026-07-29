"""Host adapter: mirrors a finished Spanish book into the host's Work Log (LGA-76).

Like lingua_ai.py / lingua_image.py, this is the ONLY place lingua's book log touches
the host (D-04). A book the child finishes becomes a real WorkLogEntry, so it shows up
in the Work Log AND in the charter report with no report-side changes. To extract
lingua, reimplement just this file and point LINGUA["WORKLOG_SINK"] at it.
"""
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

from lingua.ports import WorkLogSink
from students.models import Student
from worklog.models import WorkLogEntry

def subject():
    """The work-log subject mirrored books are filed under. Read per-call, not frozen
    at import: a module-level constant can't be reached by override_settings, so the
    setting would be untestable and a deployment-time change would need a restart."""
    return getattr(settings, "LINGUA", {}).get("WORKLOG_SUBJECT", "Spanish reading")


class HostWorkLogSink(WorkLogSink):
    def record_book(self, *, host_student_id, title, author="", read_on=None, note=""):
        student = (
            Student.objects.select_related("family", "parent")
            .filter(pk=host_student_id).first()
        )
        # A WorkLogEntry requires both a child and an owning parent user; without them
        # there's nothing to file, so skip silently (the book log itself still stands).
        if student is None or student.parent_id is None:
            return None
        desc = f"Leyó «{title}»"
        if author:
            desc += f" — {author}"
        if note:
            desc += f". {note}"
        entry = WorkLogEntry.objects.create(
            parent=student.parent,
            family=student.family,
            child=student,
            date=read_on or timezone.localdate(),
            subject=subject(),
            description=desc,
        )
        return entry.pk

    def remove(self, host_record_id):
        # Match on the pk ALONE: it came from our own record_book, so no other row can
        # have it. Matching on the subject too would strand the entry the moment the
        # parent renamed it (the subject is a free-text field they can edit) — and the
        # host_worklog_id that was the only handle on it is about to be deleted.
        if host_record_id:
            WorkLogEntry.objects.filter(pk=host_record_id).delete()


@receiver(post_delete, sender=WorkLogEntry, dispatch_uid="lingua_forget_mirror")
def _forget_mirrored_book(sender, instance, **kwargs):
    """Deleting the work-log entry also un-reads the book (HH-143).

    The Work Log is now where the parent manages reading entries, so a delete there
    has to clear the lingua-side BookLogEntry — otherwise the library keeps the book
    ticked and points at a row that no longer exists. Connected from
    ``worklog.apps.WorklogConfig.ready``.

    Deliberately does NOT pre-filter on the subject. `forget_mirror` already keys on
    host_worklog_id == this pk, which only a mirrored entry can match, so the guard
    would save one query at the cost of missing every entry the parent renamed."""
    from lingua import services
    services.forget_mirror(instance.pk)
