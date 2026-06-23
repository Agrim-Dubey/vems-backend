from django.db import IntegrityError

from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import UserProfile
from users.serializers import UserProfileSerializer
from core.schemas import MessageSerializer


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Profile"],
        summary="Get profile",
        description="Returns the authenticated user's profile.",
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile data"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            404: OpenApiResponse(response=MessageSerializer, description="Profile not found"),
        },
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
        description="Creates a new profile or fully updates an existing one.",
        request=UserProfileSerializer,
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile saved"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error or duplicate student number"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
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
        description="Updates specific fields on an existing profile.",
        request=UserProfileSerializer,
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Profile updated"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error or duplicate student number"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            404: OpenApiResponse(response=MessageSerializer, description="Profile not found"),
        },
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
