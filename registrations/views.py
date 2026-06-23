from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from registrations.models import VehicleRegistration
from registrations.services import validate_registration, cross_validate_documents
from registrations.serializers import VehicleRegistrationSerializer

from vehicles.models import Vehicle
from core.schemas import MessageSerializer, RegistrationSubmitSerializer

_REG_EXAMPLE = {
    "id": 1,
    "user": 1,
    "vehicle": 1,
    "status": "PENDING",
    "rejection_reason": None,
    "cross_validation_warnings": [],
    "submitted_at": "2026-06-23T10:30:00Z",
    "reviewed_at": None,
}


class RegistrationView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Registrations"],
        summary="Submit vehicle registration",
        description=(
            "Submit a vehicle for admin review. Prerequisites:\n"
            "1. Vehicle must belong to the authenticated user — create one via `POST /api/vehicles/`\n"
            "2. All three documents **RC**, **DL**, and **COLLEGE_ID** must be uploaded with `ocr_status = COMPLETED`\n"
            "3. No existing registration for this vehicle\n\n"
            "Submission is always created with `status = PENDING`. Admin approves or rejects from the dashboard."
        ),
        request=RegistrationSubmitSerializer,
        responses={
            201: OpenApiResponse(response=VehicleRegistrationSerializer, description="Registration submitted"),
            400: OpenApiResponse(response=MessageSerializer, description="Missing vehicle, docs not ready, or already submitted"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            404: OpenApiResponse(response=MessageSerializer, description="Vehicle not found"),
        },
        examples=[
            OpenApiExample(
                "Request",
                value={"vehicle": 1},
                request_only=True,
            ),
            OpenApiExample(
                "Success",
                value=_REG_EXAMPLE,
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "With cross-validation warnings",
                value={**_REG_EXAMPLE, "cross_validation_warnings": ["Vehicle number on RC does not match registered number"]},
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Docs not ready",
                value={"message": "All documents must be uploaded and OCR completed before submitting registration"},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Already submitted",
                value={"message": "Registration already submitted for this vehicle"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
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
        examples=[
            OpenApiExample(
                "Success",
                value=[_REG_EXAMPLE],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):

        registrations = VehicleRegistration.objects.filter(user=request.user)

        serializer = VehicleRegistrationSerializer(registrations, many=True)

        return Response(serializer.data)
