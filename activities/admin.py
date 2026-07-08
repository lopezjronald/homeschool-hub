from django.contrib import admin

from .models import ExternalActivity


@admin.register(ExternalActivity)
class ExternalActivityAdmin(admin.ModelAdmin):
    list_display = ("display_label", "student", "family", "cadence", "is_active", "is_muted")
    list_filter = ("cadence", "is_active", "is_muted", "provider")
    search_fields = ("title", "provider", "url")
