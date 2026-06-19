from django.utils import timezone
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsAdminUser

from registrations.models import VehicleRegistration
from registrations.serializers import VehicleRegistrationSerializer

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer

from vehicles.serializers import VehicleSerializer


class DashboardStatsView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        return Response({
            "pending": VehicleRegistration.objects.filter(status="PENDING").count(),
            "approved": VehicleRegistration.objects.filter(status="APPROVED").count(),
            "rejected": VehicleRegistration.objects.filter(status="REJECTED").count(),
        })


class AllRegistrationsView(APIView):
    """List all registrations, optionally filtered by status."""

    permission_classes = [IsAdminUser]

    def get(self, request):

        status_filter = request.GET.get("status")

        registrations = VehicleRegistration.objects.select_related(
            "user", "vehicle"
        ).order_by("-submitted_at")

        if status_filter:
            registrations = registrations.filter(status=status_filter.upper())

        data = []
        for reg in registrations:
            data.append({
                "id": reg.id,
                "status": reg.status,
                "submitted_at": reg.submitted_at,
                "reviewed_at": reg.reviewed_at,
                "rejection_reason": reg.rejection_reason,
                "user": {
                    "id": reg.user.id,
                    "email": reg.user.email,
                },
                "vehicle": VehicleSerializer(reg.vehicle).data,
            })

        return Response(data)


class RegistrationDetailView(APIView):
    """Full detail for one registration: user, vehicle, documents + OCR data."""

    permission_classes = [IsAdminUser]

    def get(self, request, registration_id):

        registration = VehicleRegistration.objects.select_related(
            "user", "vehicle"
        ).filter(id=registration_id).first()

        if not registration:
            return Response(
                {"message": "Registration not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        documents = UserDocument.objects.filter(user=registration.user)

        return Response({
            "id": registration.id,
            "status": registration.status,
            "submitted_at": registration.submitted_at,
            "reviewed_at": registration.reviewed_at,
            "rejection_reason": registration.rejection_reason,
            "user": {
                "id": registration.user.id,
                "email": registration.user.email,
            },
            "vehicle": VehicleSerializer(registration.vehicle).data,
            "documents": UserDocumentSerializer(documents, many=True).data,
        })


class ApproveRegistrationView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):

        registration = VehicleRegistration.objects.filter(
            id=registration_id
        ).first()

        if not registration:
            return Response(
                {"message": "Registration not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        registration.status = "APPROVED"
        registration.reviewed_at = timezone.now()
        registration.save()

        send_mail(
            subject="VEMS — Vehicle Registration Approved",
            message=(
                f"Dear {registration.vehicle.owner_name},\n\n"
                f"Your vehicle registration has been approved.\n\n"
                f"Vehicle Number: {registration.vehicle.vehicle_number}\n"
                f"Vehicle: {registration.vehicle.vehicle_model} ({registration.vehicle.vehicle_color})\n\n"
                f"You can now bring your vehicle to the campus.\n\n"
                f"— AKGEC Vehicle Entry Management System"
            ),
            from_email=None,
            recipient_list=[registration.user.email],
            fail_silently=True,
        )

        return Response({"message": "Registration approved"})


class RejectRegistrationView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):

        reason = request.data.get("reason")

        registration = VehicleRegistration.objects.filter(
            id=registration_id
        ).first()

        if not registration:
            return Response(
                {"message": "Registration not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        registration.status = "REJECTED"
        registration.rejection_reason = reason
        registration.reviewed_at = timezone.now()
        registration.save()

        send_mail(
            subject="VEMS — Vehicle Registration Rejected",
            message=(
                f"Dear {registration.vehicle.owner_name},\n\n"
                f"Your vehicle registration has been rejected.\n\n"
                f"Vehicle Number: {registration.vehicle.vehicle_number}\n"
                f"Reason: {reason or 'No reason provided'}\n\n"
                f"Please re-submit with the correct documents or contact the admin for assistance.\n\n"
                f"— AKGEC Vehicle Entry Management System"
            ),
            from_email=None,
            recipient_list=[registration.user.email],
            fail_silently=True,
        )

        return Response({"message": "Registration rejected"})
