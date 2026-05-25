from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer


class DocumentUploadView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = UserDocumentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return Response(serializer.data)

    def get(self, request):

        documents = UserDocument.objects.filter(
            user=request.user
        )

        serializer = UserDocumentSerializer(
            documents,
            many=True
        )

        return Response(serializer.data)