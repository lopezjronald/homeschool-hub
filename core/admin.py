from django.contrib import admin

from .models import Family, FamilyMembership, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "org_type", "requires_teacher_oversight"]
    list_filter = ["org_type", "requires_teacher_oversight"]


class FamilyMembershipInline(admin.TabularInline):
    model = FamilyMembership
    extra = 1


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ["name", "organization"]
    list_filter = ["organization"]
    inlines = [FamilyMembershipInline]


@admin.register(FamilyMembership)
class FamilyMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "family", "role"]
    list_filter = ["role"]
