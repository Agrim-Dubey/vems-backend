from django.contrib import admin

from registrations.models import VehicleRegistration


@admin.register(VehicleRegistration)
class VehicleRegistrationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "vehicle", "status", "submitted_at", "reviewed_at"]
    search_fields = ["user__email", "vehicle__vehicle_number"]
    list_filter = ["status"]
    readonly_fields = ["submitted_at", "reviewed_at"]
