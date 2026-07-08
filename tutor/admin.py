from django.contrib import admin

from .models import Material, MasteryAssessment


@admin.register(MasteryAssessment)
class MasteryAssessmentAdmin(admin.ModelAdmin):
    list_display = ("work_entry", "ai_level", "final_level", "status", "graded_by", "created_at")
    list_filter = ("status", "ai_level", "final_level")
    raw_id_fields = ("work_entry", "lesson", "graded_by")
    readonly_fields = ("created_at", "finalized_at")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "skill_type", "lesson", "child", "status", "created_at")
    list_filter = ("skill_type", "status")
    search_fields = ("title", "student_content", "parent_content")
    raw_id_fields = ("lesson", "child", "family", "created_by")
