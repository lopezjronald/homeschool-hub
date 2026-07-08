from django.contrib import admin

from .models import (
    Chapter,
    Curriculum,
    CurriculumDocument,
    CurriculumPlacement,
    Lesson,
)


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "grade_level", "parent", "created_at")
    list_filter = ("subject", "grade_level")
    search_fields = ("name", "subject", "parent__username", "parent__email")
    raw_id_fields = ("parent",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("order", "number", "title", "lesson_type")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("curriculum", "number", "title")
    list_filter = ("curriculum",)
    ordering = ("curriculum", "number")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("chapter", "order", "number", "title", "lesson_type")
    list_filter = ("lesson_type", "chapter__curriculum")
    search_fields = ("title", "objectives")


@admin.register(CurriculumDocument)
class CurriculumDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "curriculum", "doc_type", "uploaded_by", "created_at")
    list_filter = ("doc_type",)
    raw_id_fields = ("curriculum", "uploaded_by")


@admin.register(CurriculumPlacement)
class CurriculumPlacementAdmin(admin.ModelAdmin):
    list_display = ("child", "curriculum", "current_lesson", "updated_at")
    raw_id_fields = ("child", "curriculum", "current_lesson")
