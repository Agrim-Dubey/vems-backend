from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from vehicles.models import Vehicle

from registrations.models import VehicleRegistration


class PublicVehicleSearchView(APIView):

    authentication_classes = []

    permission_classes = []

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