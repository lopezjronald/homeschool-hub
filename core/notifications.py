"""Outbound email notifications for events that need a parent's attention.

Mirrors the send pattern in ``accounts/services.py`` (render_to_string + send_mail).
The submission notifier is called from the grading path when a child's work
produces a draft assessment, so it may run in a background thread with no
request — links are built from ``settings.SITE_BASE_URL`` (relative if unset).
The email backend gates delivery (console in dev, SMTP when EMAIL_HOST is set).
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

logger = logging.getLogger(__name__)


def _recipient_emails(assessment):
    """Opted-in editor-parent emails to notify for this assessment's child.

    Family editors (parent/guardian/admin) for the work's family, or the child's
    own parent when the work has no family (legacy null-family rows). Only users
    with ``notify_on_submission`` set and a real email address are included.
    """
    from accounts.models import UserProfile
    from core.models import FamilyMembership
    from core.permissions import EDIT_ROLES

    entry = assessment.work_entry
    student = entry.child

    if entry.family_id:
        users = [
            m.user
            for m in FamilyMembership.objects
            .filter(family_id=entry.family_id, role__in=EDIT_ROLES)
            .select_related("user")
        ]
    elif student and student.parent_id:
        users = [student.parent]
    else:
        users = []

    emails, seen = [], set()
    for u in users:
        if not u or not u.email or u.pk in seen:
            continue
        seen.add(u.pk)
        if UserProfile.get_for(u).notify_on_submission:
            emails.append(u.email)
    return emails


def notify_parents_of_submission(assessment):
    """Email the family's editors that a child's work is ready to finalize.

    Best-effort and fail-soft: a mail hiccup must never affect grading. Returns
    the number of recipients emailed (0 if none / on error).
    """
    try:
        entry = assessment.work_entry
        student = entry.child
        emails = _recipient_emails(assessment)
        if not emails:
            return 0

        path = reverse("tutor:assess_detail", args=[assessment.pk])
        base = (getattr(settings, "SITE_BASE_URL", "") or "").rstrip("/")
        review_url = f"{base}{path}" if base else path

        ctx = {
            "student": student,
            "subject_name": entry.subject,
            "assessment": assessment,
            "review_url": review_url,
        }
        subject = render_to_string("tutor/emails/submission_subject.txt", ctx).strip()
        body = render_to_string("tutor/emails/submission_notify.txt", ctx)
        send_mail(subject, body, getattr(settings, "DEFAULT_FROM_EMAIL", None), emails)
        return len(emails)
    except Exception:  # noqa: BLE001 — a notification must never break grading
        logger.exception(
            "submission notification failed for assessment %s",
            getattr(assessment, "pk", "?"),
        )
        return 0
