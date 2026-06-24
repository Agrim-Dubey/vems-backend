from rest_framework import serializers

from documents.models import UserDocument

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf", ".docx"}


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

    def validate_file(self, file):
        if file.size > MAX_FILE_SIZE_BYTES:
            raise serializers.ValidationError(
                f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB."
            )

        content_type = getattr(file, "content_type", "")
        if content_type not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(
                "Invalid file type. Allowed: JPG, PNG, WEBP, PDF, DOCX."
            )

        import os
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Invalid file extension. Allowed: .jpg, .jpeg, .png, .webp, .pdf, .docx."
            )

        return file