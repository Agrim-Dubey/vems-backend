from documents.models import UserDocument

from vehicles.models import Vehicle


REQUIRED_DOCUMENTS = ["RC", "DL", "COLLEGE_ID"]


def validate_registration(user):

    documents = UserDocument.objects.filter(user=user)

    uploaded_types = list(
        documents.values_list("document_type", flat=True)
    )

    for doc_type in REQUIRED_DOCUMENTS:
        if doc_type not in uploaded_types:
            return False, f"{doc_type} document missing"

    failed_or_pending = documents.exclude(ocr_status="COMPLETED")
    if failed_or_pending.exists():
        return False, "One or more documents have not completed OCR processing"

    if not Vehicle.objects.filter(user=user).exists():
        return False, "No vehicle registered"

    return True, "Validation successful"