from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import UserProfile
from users.serializers import UserProfileSerializer


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        profile = UserProfile.objects.filter(user=request.user).first()

        if not profile:
            return Response(
                {"message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(UserProfileSerializer(profile).data)

    def post(self, request):

        profile = UserProfile.objects.filter(user=request.user).first()

        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=bool(profile),
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user, is_profile_completed=True)

        return Response(serializer.data)
