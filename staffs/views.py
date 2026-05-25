from django.utils import timezone
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response

from core.permissions import IsStaffUser

from registrations.models import VehicleRegistration

from registrations.serializers import (
    VehicleRegistrationSerializer
)


class DashboardStatsView(APIView):

    permission_classes = [IsStaffUser]

    def get(self, request):

        pending = VehicleRegistration.objects.filter(
            status="PENDING"
        ).count()

        approved = VehicleRegistration.objects.filter(
            status="APPROVED"
        ).count()

        rejected = VehicleRegistration.objects.filter(
            status="REJECTED"
        ).count()

        return Response({
            "pending": pending,
            "approved": approved,
            "rejected": rejected
        })


class PendingRegistrationsView(APIView):

    permission_classes = [IsStaffUser]

    def get(self, request):

        registrations = VehicleRegistration.objects.filter(
            status="PENDING"
        )

        serializer = VehicleRegistrationSerializer(
            registrations,
            many=True
        )

        return Response(serializer.data)


class ApproveRegistrationView(APIView):

    permission_classes = [IsStaffUser]

    def post(self, request, registration_id):

        registration = VehicleRegistration.objects.filter(
            id=registration_id
        ).first()

        if not registration:
            return Response({
                "message": "Registration not found"
            })

        registration.status = "APPROVED"

        registration.reviewed_at = timezone.now()

        registration.save()

        return Response({
            "message": "Registration approved"
        })


class RejectRegistrationView(APIView):

    permission_classes = [IsStaffUser]

    def post(self, request, registration_id):

        reason = request.data.get(
            "reason"
        )

        registration = VehicleRegistration.objects.filter(
            id=registration_id
        ).first()

        if not registration:
            return Response({
                "message": "Registration not found"
            })

        registration.status = "REJECTED"

        registration.rejection_reason = reason

        registration.reviewed_at = timezone.now()

        registration.save()

        return Response({
            "message": "Registration rejected"
        })