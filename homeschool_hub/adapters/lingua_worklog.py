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

SUBJECT = settings.LINGUA.get("WORKLOG_SUBJECT", "Spanish reading")


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
            subject=SUBJECT,
            description=desc,
        )
        return entry.pk

    def remove(self, host_record_id):
        if host_record_id:
            WorkLogEntry.objects.filter(pk=host_record_id, subject=SUBJECT).delete()


@receiver(post_delete, sender=WorkLogEntry, dispatch_uid="lingua_forget_mirror")
def _forget_mirrored_book(sender, instance, **kwargs):
    """Deleting the work-log entry also un-reads the book (HH-143).

    The Work Log is now where the parent manages reading entries, so a delete there
    has to clear the lingua-side BookLogEntry — otherwise the library keeps the book
    ticked and points at a row that no longer exists. Connected from
    ``worklog.apps.WorklogConfig.ready``; only fires for our own subject."""
    if instance.subject != SUBJECT:
        return
    from lingua import services
    services.forget_mirror(instance.pk)
