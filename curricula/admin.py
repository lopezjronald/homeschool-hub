from django.contrib import admin

from .models import Curriculum


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "grade_level", "parent", "created_at")
    list_filter = ("subject", "grade_level")
    search_fields = ("name", "subject", "parent__username", "parent__email")
    raw_id_fields = ("parent",)
