from django.apps import AppConfig


class WorklogConfig(AppConfig):
    name = 'worklog'

    def ready(self):
        # The Spanish module mirrors finished books into this log, so deleting the
        # work-log entry has to clear the mirror. That host<->lingua glue lives in the
        # adapters package (lingua D-04); importing it connects its post_delete
        # receiver. Extracting lingua drops the package, hence the guard.
        try:
            from homeschool_hub.adapters import lingua_worklog  # noqa: F401
        except ImportError:
            pass
