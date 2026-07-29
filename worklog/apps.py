from django.apps import AppConfig


class WorklogConfig(AppConfig):
    name = 'worklog'

    def ready(self):
        # The Spanish module mirrors finished books into this log, so deleting the
        # work-log entry has to clear the mirror. That host<->lingua glue lives in the
        # adapters package (lingua D-04); importing it connects its post_delete
        # receiver. Extracting lingua drops the package, hence the guard.
        # Catch only "the package isn't there". A bare `except ImportError` would also
        # swallow a typo or a renamed model INSIDE the adapter, silently disconnecting
        # the receiver — and the symptom would be a book that stays ticked after its
        # work-log entry is deleted, with nothing logged anywhere.
        try:
            from homeschool_hub.adapters import lingua_worklog  # noqa: F401
        except ModuleNotFoundError as exc:
            if exc.name != "homeschool_hub.adapters.lingua_worklog":
                raise
