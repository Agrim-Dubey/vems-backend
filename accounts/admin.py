from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["email", "username", "role", "is_verified", "is_staff"]
    list_filter = ["role", "is_verified"]
    search_fields = ["email", "username"]
    ordering = ["email"]

    fieldsets = UserAdmin.fieldsets + (
        ("VEMS", {"fields": ("role", "is_verified")}),
    )


