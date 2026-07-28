"""Host adapter: mirrors a finished Spanish book into the host's Work Log (LGA-76).

Like lingua_ai.py / lingua_image.py, this is the ONLY place lingua's book log touches
the host (D-04). A book the child finishes becomes a real WorkLogEntry, so it shows up
in the Work Log AND in the charter report with no report-side changes. To extract
lingua, reimplement just this file and point LINGUA["WORKLOG_SINK"] at it.
"""
from django.utils import timezone

from lingua.ports import WorkLogSink
from students.models import Student
from worklog.models import WorkLogEntry

SUBJECT = "Spanish reading"


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
