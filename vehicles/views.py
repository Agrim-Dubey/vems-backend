from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer


class VehicleView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = VehicleSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return Response(serializer.data)

    def get(self, request):

        vehicles = Vehicle.objects.filter(
            user=request.user
        )

        serializer = VehicleSerializer(
            vehicles,
            many=True
        )

        return Response(serializer.data)