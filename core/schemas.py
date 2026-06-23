from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class AccessTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["USER", "STAFF", "ADMIN"])


class SearchResultSerializer(serializers.Serializer):
    verified = serializers.BooleanField()
    owner_name = serializers.CharField(required=False)
    vehicle_number = serializers.CharField(required=False)
    vehicle_type = serializers.CharField(required=False)
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
    reason = serializers.CharField()
