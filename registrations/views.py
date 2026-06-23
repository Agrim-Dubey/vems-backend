from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.openapi import OpenApiTypes

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from registrations.models import VehicleRegistration
from registrations.services import validate_registration, cross_validate_documents
from registrations.serializers import VehicleRegistrationSerializer

from vehicles.models import Vehicle
from core.schemas import MessageSerializer


class RegistrationView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Registrations"],
        summary="Submit vehicle registration",
        description=(
            "Submit a vehicle for registration. Requires:\n"
            "- Vehicle must belong to the user\n"
            "- All three documents (RC, DL, COLLEGE_ID) must have `ocr_status = COMPLETED`\n"
            "- No existing registration for this vehicle\n\n"
            "Registration is created with `status = PENDING`. Admin reviews and approves/rejects."
        ),
        request={"application/json": {"type": "object", "properties": {"vehicle": {"type": "integer", "description": "Vehicle ID"}}, "required": ["vehicle"]}},
        responses={
            201: OpenApiResponse(response=VehicleRegistrationSerializer, description="Registration submitted"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation failed or already submitted"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            404: OpenApiResponse(response=MessageSerializer, description="Vehicle not found"),
        },
    )
    def post(self, request):

        vehicle_id = request.data.get("vehicle")

        if not vehicle_id:
            return Response(
                {"vehicle": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle = Vehicle.objects.filter(
            id=vehicle_id,
            user=request.user
        ).first()

        if not vehicle:
            return Response(
                {"message": "Vehicle not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if VehicleRegistration.objects.filter(user=request.user, vehicle=vehicle).exists():
            return Response(
                {"message": "Registration already submitted for this vehicle"},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_valid, message = validate_registration(request.user)

        if not is_valid:
            return Response(
                {"message": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        warnings = cross_validate_documents(request.user, vehicle)

        registration = VehicleRegistration.objects.create(
            user=request.user,
            vehicle=vehicle,
            cross_validation_warnings=warnings
        )

        return Response(
            VehicleRegistrationSerializer(registration).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=["Registrations"],
        summary="List my registrations",
        description="Returns all vehicle registrations submitted by the authenticated user.",
        responses={
            200: OpenApiResponse(response=VehicleRegistrationSerializer(many=True), description="List of registrations"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
    )
    def get(self, request):

        registrations = VehicleRegistration.objects.filter(
            user=request.user
        )

        serializer = VehicleRegistrationSerializer(
            registrations,
            many=True
        )

        return Response(serializer.data)
