from rest_framework import serializers

from documents.models import UserDocument


class UserDocumentSerializer(serializers.ModelSerializer):

    class Meta:

        model = UserDocument

        fields = "__all__"

        read_only_fields = [
            "user",
            "ocr_status",
            "verification_status",
            "extracted_data"
        ]