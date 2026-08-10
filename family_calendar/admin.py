from django.contrib import admin

from .models import CalendarEvent


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "child", "date", "start_time",
                    "repeats_weekly", "family", "parent")
    list_filter = ("event_type", "repeats_weekly", "family")
    search_fields = ("title", "location", "notes")
    date_hierarchy = "date"
