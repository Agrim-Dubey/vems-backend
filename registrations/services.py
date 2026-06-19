from documents.models import UserDocument

from vehicles.models import Vehicle


REQUIRED_DOCUMENTS = ["RC", "DL", "COLLEGE_ID"]


def validate_registration(user):

    if not Vehicle.objects.filter(user=user).exists():
        return False, "No vehicle registered"

    for doc_type in REQUIRED_DOCUMENTS:
        latest = UserDocument.objects.filter(
            user=user,
            document_type=doc_type
        ).order_by("-uploaded_at").first()

        if not latest:
            return False, f"{doc_type} document missing"

        if latest.ocr_status != "COMPLETED":
            return False, f"{doc_type} OCR not completed — please re-upload a clearer image"

    return True, "Validation successful"