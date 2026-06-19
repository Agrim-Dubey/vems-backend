from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from registrations.models import VehicleRegistration
from registrations.services import validate_registration
from registrations.serializers import VehicleRegistrationSerializer

from vehicles.models import Vehicle


class RegistrationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        vehicle_id = request.data.get("vehicle")

        vehicle = Vehicle.objects.filter(
            id=vehicle_id,
            user=request.user
        ).first()

        if not vehicle:
            return Response(
                {"message": "Vehicle not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        is_valid, message = validate_registration(request.user)

        if not is_valid:
            return Response(
                {"message": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration = VehicleRegistration.objects.create(
            user=request.user,
            vehicle=vehicle
        )

        return Response(
            VehicleRegistrationSerializer(registration).data,
            status=status.HTTP_201_CREATED
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