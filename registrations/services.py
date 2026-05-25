from documents.models import UserDocument

from vehicles.models import Vehicle


REQUIRED_DOCUMENTS = [
    "RC",
    "DL",
    "COLLEGE_ID"
]


def validate_registration(user):

    profile = getattr(user, "profile", None)

    if not profile:
        return False, "Profile incomplete"

    documents = UserDocument.objects.filter(
        user=user
    )

    uploaded_types = list(
        documents.values_list(
            "document_type",
            flat=True
        )
    )

    for doc_type in REQUIRED_DOCUMENTS:

        if doc_type not in uploaded_types:
            return False, f"{doc_type} missing"

    pending_ocr = documents.exclude(
        ocr_status="COMPLETED"
    )

    if pending_ocr.exists():
        return False, "OCR processing pending"

    vehicle = Vehicle.objects.filter(
        user=user
    ).first()

    if not vehicle:
        return False, "Vehicle not found"

    return True, "Validation successful"