from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "grade_level", "parent", "created_at")
    list_filter = ("grade_level",)
    search_fields = ("first_name", "last_name", "parent__username", "parent__email")
    raw_id_fields = ("parent",)
