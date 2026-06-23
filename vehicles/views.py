from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from core.schemas import MessageSerializer

_VEHICLE_EXAMPLE = {
    "id": 1,
    "vehicle_number": "UP03MF4477",
    "vehicle_type": "CAR",
    "vehicle_model": "Honda City",
    "vehicle_color": "White",
    "rc_number": "RC123456789",
    "owner_name": "Agrim Dubey",
    "is_active": True,
    "user": 1,
    "created_at": "2026-06-23T10:00:00Z",
}


class VehicleView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Vehicles"],
        summary="Add a vehicle",
        description="Register a new vehicle under the authenticated user's account.",
        request=VehicleSerializer,
        responses={
            200: OpenApiResponse(response=VehicleSerializer, description="Vehicle created"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "vehicle_number": "UP03MF4477",
                    "vehicle_type": "CAR",
                    "vehicle_model": "Honda City",
                    "vehicle_color": "White",
                    "rc_number": "RC123456789",
                    "owner_name": "Agrim Dubey",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Success",
                value=_VEHICLE_EXAMPLE,
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request):

        serializer = VehicleSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return Response(serializer.data)

    @extend_schema(
        tags=["Vehicles"],
        summary="List my vehicles",
        description="Returns all vehicles belonging to the authenticated user that have a registration submitted.",
        responses={
            200: OpenApiResponse(response=VehicleSerializer(many=True), description="List of vehicles"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value=[_VEHICLE_EXAMPLE],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):

        vehicles = Vehicle.objects.filter(
            user=request.user,
            registrations__isnull=False
        ).distinct()

        serializer = VehicleSerializer(vehicles, many=True)

        return Response(serializer.data)
