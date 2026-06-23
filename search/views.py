from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from vehicles.models import Vehicle

from registrations.models import VehicleRegistration
from core.schemas import SearchResultSerializer, MessageSerializer


class PublicVehicleSearchView(APIView):

    authentication_classes = []

    permission_classes = []

    @extend_schema(
        tags=["Search"],
        summary="Search vehicle by number",
        description=(
            "Public endpoint — no authentication required.\n\n"
            "Looks up a vehicle by number and returns verification status. "
            "Only returns data for APPROVED registrations. "
            "Vehicle number is case-insensitive."
        ),
        parameters=[
            OpenApiParameter(
                name="vehicle_number",
                description="Vehicle registration number (e.g. UP03MF4477). Case-insensitive.",
                required=True,
                type=str,
            )
        ],
        responses={
            200: OpenApiResponse(response=SearchResultSerializer, description="Vehicle found or not found"),
            400: OpenApiResponse(response=MessageSerializer, description="vehicle_number param missing"),
        },
        auth=[],
    )
    def get(self, request):

        vehicle_number = request.GET.get("vehicle_number")

        if not vehicle_number:
            return Response(
                {"verified": False, "message": "vehicle_number param required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle = Vehicle.objects.filter(
            vehicle_number=vehicle_number.upper()
        ).first()

        if not vehicle:
            return Response({
                "verified": False
            })

        registration = VehicleRegistration.objects.filter(
            vehicle=vehicle,
            status="APPROVED"
        ).first()

        if not registration:
            return Response({
                "verified": False
            })

        return Response({
            "verified": True,
            "owner_name": vehicle.owner_name,
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_type": vehicle.vehicle_type,
            "vehicle_model": vehicle.vehicle_model
        })
