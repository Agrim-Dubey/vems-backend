from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer
from ocr.services import process_document


class DocumentUploadView(APIView):

    permission_classes = [IsAuthenticated]

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
        except Exception:
            document.ocr_status = "FAILED"

        document.save(update_fields=["extracted_data", "ocr_status"])

        return Response(UserDocumentSerializer(document).data)

    def get(self, request):

        documents = UserDocument.objects.filter(
            user=request.user
        )

        serializer = UserDocumentSerializer(
            documents,
            many=True
        )

        return Response(serializer.data)