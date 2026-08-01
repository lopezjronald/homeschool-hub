from django.contrib import admin

from .models import AiSpend, Material, MasteryAssessment


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


@admin.register(AiSpend)
class AiSpendAdmin(admin.ModelAdmin):
    """Read-only view of the tutor AI spend ledger (HH-145).

    Editable rows would be a foot-gun: the ceiling reads micro_usd, so a typo here
    either stops all AI work or removes the stop entirely. To spend more this
    month, raise TUTOR_MONTHLY_COST_CEILING_USD.
    """

    list_display = ("period", "dollars", "calls", "input_tokens", "output_tokens", "updated_at")
    readonly_fields = ("period", "micro_usd", "calls", "input_tokens", "output_tokens",
                       "created_at", "updated_at")

    @admin.display(description="Estimated spend", ordering="micro_usd")
    def dollars(self, obj):
        return f"${obj.micro_usd / 1_000_000:.2f}"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
