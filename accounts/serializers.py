import re

from rest_framework import serializers

from accounts.models import User

class RegisterSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):

        pattern = r'^[a-zA-Z0-9._%+-]+@akgec\.ac\.in$'

        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid college email")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")

        return value
class SetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(min_length=8)

    confirm_password = serializers.CharField()

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": ["Passwords do not match"]
            })

        return attrs

class VerifyOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()

    otp = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email")
        return value


class ResetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": ["Passwords do not match"]
            })
        return attrs