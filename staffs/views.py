from django.utils import timezone
from django.core.mail import send_mail

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsAdminUser
from core.schemas import (
    MessageSerializer,
    DashboardStatsSerializer,
    AdminRegistrationSerializer,
    RejectRequestSerializer,
)

from registrations.models import VehicleRegistration
from registrations.serializers import VehicleRegistrationSerializer

from documents.models import UserDocument
from documents.serializers import UserDocumentSerializer

from vehicles.serializers import VehicleSerializer

_VEHICLE_EXAMPLE = {
    "id": 1,
    "vehicle_number": "UP03MF4477",
    "vehicle_type": "CAR",
    "vehicle_model": "Honda City",
    "vehicle_color": "White",
    "rc_number": "RC123456789",
    "owner_name": "Agrim Dubey",
}

_REG_LIST_EXAMPLE = {
    "id": 1,
    "status": "PENDING",
    "submitted_at": "2026-06-23T10:30:00Z",
    "reviewed_at": None,
    "rejection_reason": None,
    "cross_validation_warnings": [],
    "user": {"id": 1, "email": "student24154001@akgec.ac.in"},
    "vehicle": _VEHICLE_EXAMPLE,
}


class DashboardStatsView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Dashboard stats",
        description="Returns count of PENDING, APPROVED, and REJECTED registrations.",
        responses={
            200: OpenApiResponse(response=DashboardStatsSerializer, description="Registration counts"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            403: OpenApiResponse(response=MessageSerializer, description="Not an admin"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value={"pending": 12, "approved": 45, "rejected": 3},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):

        return Response({
            "pending": VehicleRegistration.objects.filter(status="PENDING").count(),
            "approved": VehicleRegistration.objects.filter(status="APPROVED").count(),
            "rejected": VehicleRegistration.objects.filter(status="REJECTED").count(),
        })


class AllRegistrationsView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="List all registrations",
        description="Returns all registrations ordered by submission date. Filter by status using `?status=PENDING|APPROVED|REJECTED`.",
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter by status",
                required=False,
                type=str,
                enum=["PENDING", "APPROVED", "REJECTED"],
                location=OpenApiParameter.QUERY,
            )
        ],
        responses={
            200: OpenApiResponse(response=AdminRegistrationSerializer(many=True), description="List of registrations"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            403: OpenApiResponse(response=MessageSerializer, description="Not an admin"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value=[_REG_LIST_EXAMPLE],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
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
                "cross_validation_warnings": reg.cross_validation_warnings,
                "user": {
                    "id": reg.user.id,
                    "email": reg.user.email,
                },
                "vehicle": VehicleSerializer(reg.vehicle).data,
            })

        return Response(data)


class RegistrationDetailView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Registration detail",
        description="Full detail for one registration — includes user info, vehicle data, and all uploaded documents with extracted OCR data.",
        responses={
            200: OpenApiResponse(description="Registration with documents"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            403: OpenApiResponse(response=MessageSerializer, description="Not an admin"),
            404: OpenApiResponse(response=MessageSerializer, description="Registration not found"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value={
                    **_REG_LIST_EXAMPLE,
                    "documents": [
                        {
                            "id": 1,
                            "document_type": "RC",
                            "ocr_status": "COMPLETED",
                            "verification_status": "PENDING",
                            "extracted_data": {
                                "vehicle_number": "UP03MF4477",
                                "dl_number": None,
                                "student_id": None,
                                "raw_text": "...",
                            },
                            "uploaded_at": "2026-06-23T10:00:00Z",
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
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
            "cross_validation_warnings": registration.cross_validation_warnings,
            "user": {
                "id": registration.user.id,
                "email": registration.user.email,
            },
            "vehicle": VehicleSerializer(registration.vehicle).data,
            "documents": UserDocumentSerializer(documents, many=True).data,
        })


class ApproveRegistrationView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Approve registration",
        description="Approve a vehicle registration. Sends an approval email to the student automatically.",
        responses={
            200: OpenApiResponse(response=MessageSerializer, description="Registration approved"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            403: OpenApiResponse(response=MessageSerializer, description="Not an admin"),
            404: OpenApiResponse(response=MessageSerializer, description="Registration not found"),
        },
        examples=[
            OpenApiExample(
                "Success",
                value={"message": "Registration approved"},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
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

    @extend_schema(
        tags=["Admin"],
        summary="Reject registration",
        description="Reject a vehicle registration with a reason. Sends a rejection email to the student.",
        request=RejectRequestSerializer,
        responses={
            200: OpenApiResponse(response=MessageSerializer, description="Registration rejected"),
            400: OpenApiResponse(response=MessageSerializer, description="reason is required"),
            401: OpenApiResponse(response=MessageSerializer, description="Unauthenticated"),
            403: OpenApiResponse(response=MessageSerializer, description="Not an admin"),
            404: OpenApiResponse(response=MessageSerializer, description="Registration not found"),
        },
        examples=[
            OpenApiExample(
                "Request",
                value={"reason": "RC document is blurry and unreadable. Please re-upload a clearer scan."},
                request_only=True,
            ),
            OpenApiExample(
                "Success",
                value={"message": "Registration rejected"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Missing reason",
                value={"message": "This field is required."},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request, registration_id):

        reason = request.data.get("reason")

        if not reason or not reason.strip():
            return Response(
                {"reason": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )

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
