from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer

from ocr.services import process_document
from core.schemas import MessageSerializer


class ProcessOCRView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["OCR"],
        summary="Trigger OCR on a document",
        description=(
            "Manually re-run OCR on a document you already uploaded. "
            "Useful if the first attempt failed. "
            "Returns the updated document with `extracted_data` and updated `ocr_status`."
        ),
        responses={
            200: OpenApiResponse(response=UserDocumentSerializer, description="OCR processed successfully"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            404: OpenApiResponse(response=MessageSerializer, description="Document not found"),
            500: OpenApiResponse(response=MessageSerializer, description="OCR processing failed — re-upload a clearer image"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value={
                    "id": 1,
                    "document_type": "RC",
                    "ocr_status": "COMPLETED",
                    "extracted_data": {
                        "vehicle_number": "UP03MF4477",
                        "dl_number": None,
                        "student_id": None,
                        "raw_text": "UP03MF4477 HONDA CITY ..."
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "OCR failed",
                value={"message": "OCR processing failed — please re-upload a clearer image"},
                response_only=True,
                status_codes=["500"],
            ),
        ],
    )
    def post(self, request, document_id):

        document = UserDocument.objects.filter(
            id=document_id,
            user=request.user
        ).first()

        if not document:
            return Response(
                {"message": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        document.ocr_status = "PROCESSING"
        document.save(update_fields=["ocr_status"])

        try:
            extracted_data = process_document(document)
            document.extracted_data = extracted_data
            document.ocr_status = "COMPLETED"
            document.save(update_fields=["extracted_data", "ocr_status"])
            return Response(UserDocumentSerializer(document).data)

        except Exception:
            document.ocr_status = "FAILED"
            document.save(update_fields=["ocr_status"])
            return Response(
                {"message": "OCR processing failed — please re-upload a clearer image"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
