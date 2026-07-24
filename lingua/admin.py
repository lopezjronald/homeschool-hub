from django.contrib import admin

from .models import Learner, LearnerProfile, Story, Theme


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


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "suggested_level", "status", "source", "theme", "created_at")
    list_filter = ("status", "level", "source", "language")
    search_fields = ("title",)
