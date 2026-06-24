import logging

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer
from ocr.services import process_document
from core.schemas import MessageSerializer
from core.throttles import UploadRateThrottle

logger = logging.getLogger(__name__)

_DOCUMENT_EXAMPLE = {
    "id": 1,
    "user": 1,
    "document_type": "RC",
    "file": "https://vems.akgec.ac.in/media/documents/rc_upload.jpg",
    "ocr_status": "COMPLETED",
    "verification_status": "PENDING",
    "extracted_data": {
        "vehicle_number": "UP03MF4477",
        "dl_number": None,
        "student_id": None,
        "raw_text": "UP03MF4477 ..."
    },
    "uploaded_at": "2026-06-23T10:00:00Z",
}


class DocumentUploadView(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [UploadRateThrottle]

    @extend_schema(
        tags=["Documents"],
        summary="Upload a document",
        description=(
            "Upload one of: **RC** (Registration Certificate), **DL** (Driving Licence), or **COLLEGE_ID**.\n\n"
            "OCR is triggered automatically — the response will include `extracted_data` with detected "
            "`vehicle_number`, `dl_number`, or `student_id` depending on document type.\n\n"
            "Send as `multipart/form-data`. Accepted file types: JPG, PNG, PDF."
        ),
        request={"multipart/form-data": UserDocumentSerializer},
        responses={
            200: OpenApiResponse(response=UserDocumentSerializer, description="Document uploaded and OCR processed"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
        examples=[
            OpenApiExample(
                "RC response (OCR completed)",
                value=_DOCUMENT_EXAMPLE,
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "OCR failed",
                value={**_DOCUMENT_EXAMPLE, "ocr_status": "FAILED", "extracted_data": {}},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request):

        serializer = UserDocumentSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        document = serializer.save(user=request.user)

        document.ocr_status = "PROCESSING"
        document.save(update_fields=["ocr_status"])

        try:
            extracted_data = process_document(document)
            document.extracted_data = extracted_data
            document.ocr_status = "COMPLETED"
        except Exception as e:
            logger.exception("OCR failed for document %s: %s", document.id, e)
            document.ocr_status = "FAILED"

        document.save(update_fields=["extracted_data", "ocr_status"])

        return Response(UserDocumentSerializer(document, context={"request": request}).data)

    @extend_schema(
        tags=["Documents"],
        summary="List my documents",
        description="Returns all documents uploaded by the authenticated user.",
        responses={
            200: OpenApiResponse(response=UserDocumentSerializer(many=True), description="List of documents"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value=[_DOCUMENT_EXAMPLE],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):

        documents = UserDocument.objects.filter(user=request.user)

        serializer = UserDocumentSerializer(documents, many=True)

        return Response(serializer.data)
