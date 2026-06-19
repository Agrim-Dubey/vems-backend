from django.contrib import admin

from vehicles.models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["vehicle_number", "owner_name", "vehicle_type", "vehicle_model", "vehicle_color", "user"]
    search_fields = ["vehicle_number", "owner_name", "user__email"]
    list_filter = ["vehicle_type", "is_active"]
