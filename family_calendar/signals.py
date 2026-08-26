"""Keeping Google in step with the app (HH-168).

Connected from apps.py ready(), matching how worklog wires its lingua adapter.

The rule these receivers exist to honour: a parent saving a dentist appointment
must never see an error from Google, and must never wait on it. The push happens
off the request thread, and everything it might have done wrong is recorded on
the link row for `sync_google_calendar` to retry.
"""

import logging
import threading

from django.conf import settings
from django.db import connection, transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import CalendarEvent, GoogleCalendarLink

logger = logging.getLogger(__name__)


def _run_off_thread(fn):
    """Run fn in a daemon thread, closing its DB connection afterwards.

    A thread gets its own connection and Django will not clean it up, so a
    push per save would leak one connection per save until Postgres refused.

    Not a durable queue: a dyno restart mid-push loses the attempt. That is what
    the reconcile command is for, and it is the right trade for an app with no
    worker dyno — the alternative is making the parent wait on Google.
    """
    def run():
        try:
            fn()
        except Exception:                      # noqa: BLE001 - never surface here
            logger.exception("calendar sync thread failed")
        finally:
            connection.close()

    threading.Thread(target=run, daemon=True).start()


def _dispatch(fn):
    if getattr(settings, "GOOGLE_CALENDAR_SYNC_ASYNC", True):
        _run_off_thread(fn)
    else:
        fn()                                   # tests, and management commands


@receiver(post_save, sender=CalendarEvent, dispatch_uid="gcal_push_event")
def push_on_save(sender, instance, **kwargs):
    from . import google_api, sync

    if not google_api.is_configured():
        return
    pk = instance.pk

    def work():
        event = (CalendarEvent.objects.filter(pk=pk)
                 .select_related("child").first())
        if event is not None:
            sync.push_event(event)

    # on_commit, not immediately: the thread reads the row back through its own
    # connection and would find nothing (or the pre-save values) if it started
    # before this transaction committed.
    transaction.on_commit(lambda: _dispatch(work))


@receiver(pre_delete, sender=CalendarEvent, dispatch_uid="gcal_remove_event")
def remove_on_delete(sender, instance, **kwargs):
    """PRE_delete, not post_delete.

    Django's collector deletes the related rows BEFORE sending post_delete for
    the parent, so by then GoogleCalendarLink.objects.filter(event=...) is empty
    and there is nothing left to say which Google events to remove — they would
    sit on both calendars forever. Registering on_commit from here is still
    correct: a rolled-back delete never commits, so nothing is sent.
    """
    from . import google_api, sync

    if not google_api.is_configured():
        return
    links = list(GoogleCalendarLink.objects.filter(event=instance))
    if not links:
        return
    for link in links:
        link.pk = None                         # detached: do not try to re-delete

    def work():
        sync.remove_event(links=links)

    transaction.on_commit(lambda: _dispatch(work))
