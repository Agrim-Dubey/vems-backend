from rest_framework import serializers

from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = UserProfile

        fields = "__all__"

        read_only_fields = [
            "user",
            "is_profile_completed"
        ]