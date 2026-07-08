from django.contrib import admin

from .models import WorkLogEntry


@admin.register(WorkLogEntry)
class WorkLogEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "child", "subject", "family", "created_by")
    list_filter = ("date", "family", "subject")
    search_fields = ("subject", "description", "child__first_name", "child__last_name")
    date_hierarchy = "date"
    autocomplete_fields = ()
    raw_id_fields = ("parent", "child", "curriculum", "assignment", "created_by")
