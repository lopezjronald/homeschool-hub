from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["title", "child", "curriculum", "due_date", "status", "parent"]
    list_filter = ["status", "due_date"]
    search_fields = ["title", "description"]
    raw_id_fields = ["parent", "child", "curriculum"]
