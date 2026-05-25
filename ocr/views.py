from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from documents.models import UserDocument

from ocr.services import process_document


class ProcessOCRView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):

        document = UserDocument.objects.filter(
            id=document_id,
            user=request.user
        ).first()

        if not document:
            return Response({
                "message": "Document not found"
            })

        document.ocr_status = "PROCESSING"

        document.save()

        try:

            extracted_data = process_document(
                document
            )

            document.extracted_data = extracted_data

            document.ocr_status = "COMPLETED"

            document.save()

            return Response(extracted_data)

        except Exception as e:

            document.ocr_status = "FAILED"

            document.save()

            return Response({
                "message": str(e)
            })