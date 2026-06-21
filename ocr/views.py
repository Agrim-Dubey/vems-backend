from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer

from ocr.services import process_document


class ProcessOCRView(APIView):

    permission_classes = [IsAuthenticated]

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