from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Customize the Django admin display for our user model."""

    list_display = ("username", "email", "is_active", "is_staff")
