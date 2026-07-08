from django.contrib import admin

from .models import MasteryAssessment


@admin.register(MasteryAssessment)
class MasteryAssessmentAdmin(admin.ModelAdmin):
    list_display = ("work_entry", "ai_level", "final_level", "status", "graded_by", "created_at")
    list_filter = ("status", "ai_level", "final_level")
    raw_id_fields = ("work_entry", "lesson", "graded_by")
    readonly_fields = ("created_at", "finalized_at")
