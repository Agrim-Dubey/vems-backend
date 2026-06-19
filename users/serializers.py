from rest_framework import serializers

from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ["id", "first_name", "last_name", "student_number", "photo"]
        read_only_fields = ["id"]
