from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

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
        summary="Verify vehicle",
        description=(
            "**Public endpoint — no authentication required.**\n\n"
            "Used by security guards to verify a vehicle at the gate. "
            "Looks up a vehicle by registration number and returns its verification status.\n\n"
            "- Returns `verified: true` only if the vehicle has an **APPROVED** registration\n"
            "- Vehicle number is **case-insensitive** (`up03mf4477` = `UP03MF4477`)"
        ),
        parameters=[
            OpenApiParameter(
                name="vehicle_number",
                description="Vehicle registration number. Example: UP03MF4477",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            )
        ],
        responses={
            200: OpenApiResponse(response=SearchResultSerializer, description="Result — check `verified` field"),
            400: OpenApiResponse(response=MessageSerializer, description="vehicle_number param missing"),
        },
        auth=[],
        examples=[
            OpenApiExample(
                "Verified vehicle",
                value={
                    "verified": True,
                    "owner_name": "Agrim Dubey",
                    "vehicle_number": "UP03MF4477",
                    "vehicle_type": "CAR",
                    "vehicle_model": "Honda City",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Not found / not approved",
                value={"verified": False},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Missing param",
                value={"verified": False, "message": "vehicle_number param required"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
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
            return Response({"verified": False})

        registration = VehicleRegistration.objects.filter(
            vehicle=vehicle,
            status="APPROVED"
        ).first()

        if not registration:
            return Response({"verified": False})

        return Response({
            "verified": True,
            "owner_name": vehicle.owner_name,
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_type": vehicle.vehicle_type,
            "vehicle_model": vehicle.vehicle_model
        })
