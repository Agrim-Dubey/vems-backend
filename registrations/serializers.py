from rest_framework import serializers

from registrations.models import VehicleRegistration


class VehicleRegistrationSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = VehicleRegistration

        fields = "__all__"

        read_only_fields = [
            "user",
            "status",
            "reviewed_at",
            "submitted_at"
        ]