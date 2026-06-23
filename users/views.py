from django.db import IntegrityError

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import UserProfile
from users.serializers import UserProfileSerializer
from core.schemas import MessageSerializer

_PROFILE_EXAMPLE = {
    "id": 1,
    "first_name": "Agrim",
    "last_name": "Dubey",
    "student_number": "24154080",
    "photo": "https://vems.akgec.ac.in/media/profile_photos/photo.jpg",
}

_PROFILE_REQUEST_EXAMPLE = {
    "first_name": "Agrim",
    "last_name": "Dubey",
    "student_number": "24154080",
}


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Profile"],
        summary="Get my profile",
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile data"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            404: OpenApiResponse(response=MessageSerializer, description="Profile not found"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value=_PROFILE_EXAMPLE,
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):

        profile = UserProfile.objects.filter(user=request.user).first()

        if not profile:
            return Response(
                {"message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(UserProfileSerializer(profile, context={"request": request}).data)

    @extend_schema(
        tags=["Profile"],
        summary="Create or update profile",
        description="Creates a new profile or fully replaces an existing one. Send as `multipart/form-data` if uploading a photo, otherwise `application/json`.",
        request={"multipart/form-data": UserProfileSerializer, "application/json": UserProfileSerializer},
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile saved"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error or duplicate student number"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
        examples=[
            OpenApiExample(
                "Request",
                value=_PROFILE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Success",
                value=_PROFILE_EXAMPLE,
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Duplicate student number",
                value={"message": "A profile with this student number already exists."},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):

        profile = UserProfile.objects.filter(user=request.user).first()

        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=bool(profile),
        )

        serializer.is_valid(raise_exception=True)

        try:
            serializer.save(user=request.user, is_profile_completed=True)
        except IntegrityError:
            return Response(
                {"student_number": ["A profile with this student number already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(UserProfileSerializer(serializer.instance, context={"request": request}).data)

    @extend_schema(
        tags=["Profile"],
        summary="Partially update profile",
        description="Update one or more fields on an existing profile.",
        request={"multipart/form-data": UserProfileSerializer, "application/json": UserProfileSerializer},
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile updated"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            404: OpenApiResponse(response=MessageSerializer, description="Profile not found"),
        },
        examples=[
            OpenApiExample(
                "Partial update",
                value={"first_name": "Vishwajeet"},
                request_only=True,
            ),
        ],
    )
    def patch(self, request):

        profile = UserProfile.objects.filter(user=request.user).first()

        if not profile:
            return Response(
                {"message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except IntegrityError:
            return Response(
                {"message": "A profile with this student number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(UserProfileSerializer(serializer.instance, context={"request": request}).data)
