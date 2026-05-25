from django.db import models

from accounts.models import User


class UserDocument(models.Model):

    class DocumentType(models.TextChoices):
        RC = "RC", "RC"
        DL = "DL", "DL"
        COLLEGE_ID = "COLLEGE_ID", "COLLEGE_ID"

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"
    
    class OCRStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
    ocr_status = models.CharField(
    max_length=20,
    choices=OCRStatus.choices,
    default=OCRStatus.PENDING
)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices
    )

    file = models.FileField(
        upload_to="documents/"
    )

    extracted_data = models.JSONField(
        default=dict,
        blank=True
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )