from django.apps import AppConfig


class FamilyCalendarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "family_calendar"
    verbose_name = "Family calendar"

    def ready(self):
        # Importing connects the post_save/post_delete receivers that keep the
        # Google copies in step (HH-168). Same wiring worklog uses for its
        # lingua adapter. Import last so a failure here cannot stop the app.
        from . import signals  # noqa: F401
