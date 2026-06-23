from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from core.schemas import MessageSerializer


class VehicleView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Vehicles"],
        summary="Add vehicle",
        description="Register a new vehicle under the authenticated user.",
        request=VehicleSerializer,
        responses={
            200: OpenApiResponse(response=VehicleSerializer, description="Vehicle created"),
            400: OpenApiResponse(response=MessageSerializer, description="Validation error"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
    )
    def post(self, request):

        serializer = VehicleSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return Response(serializer.data)

    @extend_schema(
        tags=["Vehicles"],
        summary="List vehicles",
        description="Returns vehicles belonging to the authenticated user that have a registration.",
        responses={
            200: OpenApiResponse(response=VehicleSerializer(many=True), description="List of vehicles"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
        },
    )
    def get(self, request):

        vehicles = Vehicle.objects.filter(
            user=request.user,
            registrations__isnull=False
        ).distinct()

        serializer = VehicleSerializer(
            vehicles,
            many=True
        )

        return Response(serializer.data)
