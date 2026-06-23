import logging

from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer
from ocr.services import process_document
from core.schemas import MessageSerializer

logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Documents"],
        summary="Upload a document",
        description=(
            "Upload RC, DL, or COLLEGE_ID document. OCR is triggered automatically on upload. "
            "`ocr_status` will be `COMPLETED` or `FAILED` in the response."
        ),
        request={"multipart/form-data": UserDocumentSerializer},
        responses={
            200: OpenApiResponse(response=UserDocumentSerializer, description="Document uploaded and OCR processed"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
    )
    def post(self, request):

        serializer = UserDocumentSerializer(
            data=request.data
        )

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

        return Response(UserDocumentSerializer(document).data)

    @extend_schema(
        tags=["Documents"],
        summary="List documents",
        description="Returns all documents uploaded by the authenticated user.",
        responses={
            200: OpenApiResponse(response=UserDocumentSerializer(many=True), description="List of documents"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
    )
    def get(self, request):

        documents = UserDocument.objects.filter(
            user=request.user
        )

        serializer = UserDocumentSerializer(
            documents,
            many=True
        )

        return Response(serializer.data)
