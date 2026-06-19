from django.contrib import admin

from users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "student_number", "is_profile_completed"]
    search_fields = ["user__email", "student_number", "first_name", "last_name"]
    list_filter = ["is_profile_completed"]
