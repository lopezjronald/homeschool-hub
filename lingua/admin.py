from django.contrib import admin

from .models import (
    AiUsage, ComprehensionCheck, KnownWord, Learner, LearnerProfile, ListeningResource,
    ListeningSession, MilestoneAward, PhonicsRule, ReadingSession, ReviewItem, Story,
    StoryAudio, Theme,
)


class LearnerProfileInline(admin.StackedInline):
    model = LearnerProfile
    extra = 0


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    # host_student_id is a plain int (no FK), so show it directly; the resolved
    # name would come from the UserDirectory adapter (LGA-17), added later.
    list_display = ("host_student_id", "language", "variant", "created_at")
    search_fields = ("host_student_id",)
    inlines = [LearnerProfileInline]


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "age_band", "active")
    list_filter = ("age_band", "active")


@admin.register(PhonicsRule)
class PhonicsRuleAdmin(admin.ModelAdmin):
    list_display = ("pattern", "title", "order", "active")
    list_filter = ("active",)


@admin.register(AiUsage)
class AiUsageAdmin(admin.ModelAdmin):
    """Read-only ledger — it's the cost governor, so no editing/adding/deleting from
    admin (deleting a row would silently reset the month's ceiling)."""

    list_display = ("period", "input_tokens", "output_tokens", "calls", "updated_at")
    readonly_fields = ("period", "input_tokens", "output_tokens", "calls",
                       "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "suggested_level", "status", "source", "theme", "created_at")
    list_filter = ("status", "level", "source", "language")
    search_fields = ("title",)


@admin.register(StoryAudio)
class StoryAudioAdmin(admin.ModelAdmin):
    list_display = ("story", "voice", "engine", "provider", "duration_ms", "is_current", "updated_at")
    list_filter = ("provider", "voice", "engine")
    search_fields = ("story__title", "content_hash")
    readonly_fields = ("content_hash", "audio_key", "created_at", "updated_at")

    @admin.display(boolean=True, description="Current")
    def is_current(self, obj):
        return obj.is_current


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ("learner", "story", "words", "seconds", "created_at")
    list_filter = ("created_at",)


@admin.register(ReviewItem)
class ReviewItemAdmin(admin.ModelAdmin):
    list_display = ("learner", "target_kind", "target_ref", "scheduler", "due", "paused_until")
    list_filter = ("scheduler", "target_kind")
    search_fields = ("target_ref",)


@admin.register(ListeningResource)
class ListeningResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "provider", "age_band", "level", "visual_support", "order", "active")
    list_filter = ("age_band", "active", "visual_support")
    search_fields = ("title", "provider")


@admin.register(ListeningSession)
class ListeningSessionAdmin(admin.ModelAdmin):
    list_display = ("learner", "resource", "minutes", "created_at")
    list_filter = ("created_at",)


@admin.register(KnownWord)
class KnownWordAdmin(admin.ModelAdmin):
    list_display = ("learner", "word", "created_at")
    search_fields = ("word",)


@admin.register(MilestoneAward)
class MilestoneAwardAdmin(admin.ModelAdmin):
    list_display = ("learner", "kind", "threshold", "created_at")
    list_filter = ("kind",)


@admin.register(ComprehensionCheck)
class ComprehensionCheckAdmin(admin.ModelAdmin):
    list_display = ("learner", "story", "kind", "result", "reviewed_by", "created_at")
    list_filter = ("kind", "result")
