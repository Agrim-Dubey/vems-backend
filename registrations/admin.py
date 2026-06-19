from django.contrib import admin

from registrations.models import VehicleRegistration


@admin.register(VehicleRegistration)
class VehicleRegistrationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "vehicle", "status", "has_warnings", "submitted_at", "reviewed_at"]
    search_fields = ["user__email", "vehicle__vehicle_number"]
    list_filter = ["status"]
    readonly_fields = ["submitted_at", "reviewed_at", "cross_validation_warnings"]

    def has_warnings(self, obj):
        return bool(obj.cross_validation_warnings)
    has_warnings.boolean = True
    has_warnings.short_description = "Warnings"
