from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Human-readable result or error description")


class TokenResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    access_token = serializers.CharField(help_text="Short-lived JWT — use in Authorization: Bearer header")
    refresh_token = serializers.CharField(help_text="Long-lived token — use to get a new access_token")


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(help_text="Refresh token obtained from /api/auth/login/")


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["USER", "STAFF"], help_text="USER = student, STAFF = security guard. ADMIN is blocked from this endpoint.")


class SearchResultSerializer(serializers.Serializer):
    verified = serializers.BooleanField(help_text="True if vehicle has an APPROVED registration")
    owner_name = serializers.CharField(required=False)
    vehicle_number = serializers.CharField(required=False)
    vehicle_type = serializers.ChoiceField(choices=["CAR", "BIKE", "SCOOTY"], required=False)
    vehicle_model = serializers.CharField(required=False)


class DashboardStatsSerializer(serializers.Serializer):
    pending = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()


class RegistrationUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()


class AdminRegistrationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=["PENDING", "APPROVED", "REJECTED"])
    submitted_at = serializers.DateTimeField()
    reviewed_at = serializers.DateTimeField(allow_null=True)
    rejection_reason = serializers.CharField(allow_null=True)
    cross_validation_warnings = serializers.ListField(child=serializers.CharField())
    user = RegistrationUserSerializer()


class RejectRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(help_text="Reason shown to the student in the rejection email")


class RegistrationSubmitSerializer(serializers.Serializer):
    vehicle = serializers.IntegerField(help_text="ID of the vehicle to register. Get vehicle IDs from GET /api/vehicles/")
