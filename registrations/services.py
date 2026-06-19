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


def _latest_doc(user, doc_type):
    return UserDocument.objects.filter(
        user=user,
        document_type=doc_type
    ).order_by("-uploaded_at").first()


def cross_validate_documents(user, vehicle):
    """
    Runs consistency checks across the three uploaded documents.
    Returns a list of warning strings (empty = all checks passed).
    Flags issues rather than blocking — admin makes the final call.
    """
    warnings = []

    rc = _latest_doc(user, "RC")
    college_id = _latest_doc(user, "COLLEGE_ID")

    # Check 1: vehicle number on RC matches the registered vehicle number
    if rc:
        rc_vehicle_number = rc.extracted_data.get("vehicle_number")
        if rc_vehicle_number:
            normalised_rc = rc_vehicle_number.replace(" ", "").upper()
            normalised_reg = vehicle.vehicle_number.replace(" ", "").upper()
            if normalised_rc != normalised_reg:
                warnings.append(
                    f"Vehicle number on RC ({rc_vehicle_number}) does not match "
                    f"registered vehicle number ({vehicle.vehicle_number})"
                )
        else:
            warnings.append("Could not extract vehicle number from RC — verify manually")

    # Check 2: owner name from vehicle registration appears in RC raw text
    if rc and rc.extracted_data.get("raw_text"):
        raw_text_lower = rc.extracted_data["raw_text"].lower()
        name_parts = [p for p in vehicle.owner_name.lower().split() if len(p) > 2]
        if name_parts and not any(part in raw_text_lower for part in name_parts):
            warnings.append(
                f"Owner name '{vehicle.owner_name}' not found in RC document — verify manually"
            )

    # Check 3: student number on College ID matches profile
    profile = getattr(user, "profile", None)
    if college_id and profile:
        extracted_student_id = college_id.extracted_data.get("student_id")
        if extracted_student_id:
            if extracted_student_id != profile.student_number:
                warnings.append(
                    f"Student ID on College ID ({extracted_student_id}) does not match "
                    f"profile student number ({profile.student_number})"
                )
        else:
            warnings.append("Could not extract student ID from College ID — verify manually")

    return warnings
