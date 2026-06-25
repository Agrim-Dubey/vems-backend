from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from django.core.mail import send_mail

from registrations.models import VehicleRegistration
from documents.models import UserDocument


@admin.register(VehicleRegistration)
class VehicleRegistrationAdmin(admin.ModelAdmin):

    list_display = [
        "id", "student_email", "vehicle_number_display",
        "vehicle_type_display", "status", "has_warnings",
        "submitted_at", "reviewed_at",
    ]
    list_filter = ["status"]
    search_fields = ["user__email", "vehicle__vehicle_number"]
    ordering = ["-submitted_at"]
    actions = ["approve_registrations"]

    readonly_fields = [
        "submitted_at", "reviewed_at", "cross_validation_warnings",
        "student_details", "vehicle_details", "documents_review",
    ]

    fieldsets = (
        ("Decision", {
            "fields": ("status", "rejection_reason", "submitted_at", "reviewed_at"),
        }),
        ("Cross-Validation Warnings", {
            "fields": ("cross_validation_warnings",),
            "classes": ("collapse",),
        }),
        ("Student", {
            "fields": ("student_details",),
        }),
        ("Vehicle", {
            "fields": ("vehicle_details",),
        }),
        ("Documents", {
            "fields": ("documents_review",),
        }),
    )

    # --- List view columns ---

    def student_email(self, obj):
        return obj.user.email
    student_email.short_description = "Student"
    student_email.admin_order_field = "user__email"

    def vehicle_number_display(self, obj):
        return obj.vehicle.vehicle_number
    vehicle_number_display.short_description = "Vehicle No."
    vehicle_number_display.admin_order_field = "vehicle__vehicle_number"

    def vehicle_type_display(self, obj):
        return obj.vehicle.vehicle_type
    vehicle_type_display.short_description = "Type"

    def has_warnings(self, obj):
        return bool(obj.cross_validation_warnings)
    has_warnings.boolean = True
    has_warnings.short_description = "Warnings"

    # --- Detail view readonly panels ---

    def student_details(self, obj):
        try:
            p = obj.user.profile
            name = f"{p.first_name} {p.last_name}".strip() or "—"
            student_number = p.student_number or "—"
            photo_html = (
                format_html('<br><img src="{}" style="max-height:80px;margin-top:6px;border-radius:4px">', p.photo.url)
                if p.photo else ""
            )
        except Exception:
            name = "—"
            student_number = "—"
            photo_html = mark_safe("")

        return mark_safe(format_html(
            "<b>Email:</b> {email}<br>"
            "<b>Name:</b> {name}<br>"
            "<b>Student No:</b> {sn}"
            "{photo}",
            email=obj.user.email,
            name=name,
            sn=student_number,
            photo=photo_html,
        ))
    student_details.short_description = "Student"

    def vehicle_details(self, obj):
        v = obj.vehicle
        return format_html(
            "<b>Number:</b> {number}<br>"
            "<b>Owner:</b> {owner}<br>"
            "<b>Type:</b> {vtype}<br>"
            "<b>Model:</b> {model}<br>"
            "<b>Color:</b> {color}<br>"
            "<b>RC No:</b> {rc}",
            number=v.vehicle_number,
            owner=v.owner_name,
            vtype=v.vehicle_type,
            model=v.vehicle_model,
            color=v.vehicle_color,
            rc=v.rc_number,
        )
    vehicle_details.short_description = "Vehicle"

    def documents_review(self, obj):
        docs = UserDocument.objects.filter(user=obj.user).order_by("document_type")
        if not docs.exists():
            return "No documents uploaded."

        rows = []
        for doc in docs:
            file_html = (
                format_html('<a href="{}" target="_blank" style="color:#4a9eda">View ↗</a>', doc.file.url)
                if doc.file else mark_safe("—")
            )
            ocr_data = doc.extracted_data or {}
            extracted_parts = [
                f"{k.replace('_', ' ').title()}: {v}"
                for k, v in ocr_data.items()
                if k != "raw_text" and v
            ]
            extracted = " | ".join(extracted_parts) or "—"

            status_color = {
                "VERIFIED": "#2ecc71",
                "REJECTED": "#e74c3c",
                "PENDING": "#f39c12",
            }.get(doc.verification_status, "#f39c12")

            rows.append(format_html(
                '<tr style="border-bottom:1px solid #444">'
                '<td style="padding:8px;font-weight:bold">{doc_type}</td>'
                '<td style="padding:8px">{file}</td>'
                '<td style="padding:8px">{ocr}</td>'
                '<td style="padding:8px"><span style="color:{color};font-weight:bold">{vstatus}</span></td>'
                '<td style="padding:8px;font-size:11px;color:#aaa">{extracted}</td>'
                '</tr>',
                doc_type=doc.document_type,
                file=file_html,
                ocr=doc.ocr_status,
                color=status_color,
                vstatus=doc.verification_status,
                extracted=extracted,
            ))

        header = mark_safe(
            '<table style="width:100%;border-collapse:collapse;margin-top:8px">'
            '<thead><tr style="background:#2c2c2c">'
            '<th style="padding:8px;text-align:left;color:#fff">Type</th>'
            '<th style="padding:8px;text-align:left;color:#fff">File</th>'
            '<th style="padding:8px;text-align:left;color:#fff">OCR</th>'
            '<th style="padding:8px;text-align:left;color:#fff">Verification</th>'
            '<th style="padding:8px;text-align:left;color:#fff">Extracted Data</th>'
            '</tr></thead><tbody>'
        )
        footer = mark_safe('</tbody></table>')
        return header + mark_safe(''.join(str(r) for r in rows)) + footer
    documents_review.short_description = "Documents"

    # --- Save hook: auto-verify docs + email on approval ---

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data:
            obj.reviewed_at = timezone.now()
            if obj.status == VehicleRegistration.Status.APPROVED:
                UserDocument.objects.filter(user=obj.user).update(
                    verification_status=UserDocument.VerificationStatus.VERIFIED
                )
                _send_approval_email(obj)
        super().save_model(request, obj, form, change)

    # --- Bulk approve action ---

    @admin.action(description="Approve selected registrations")
    def approve_registrations(self, request, queryset):
        approved = 0
        for reg in queryset.filter(status=VehicleRegistration.Status.PENDING):
            reg.status = VehicleRegistration.Status.APPROVED
            reg.reviewed_at = timezone.now()
            reg.save()
            UserDocument.objects.filter(user=reg.user).update(
                verification_status=UserDocument.VerificationStatus.VERIFIED
            )
            _send_approval_email(reg)
            approved += 1
        self.message_user(request, f"{approved} registration(s) approved and documents marked as verified.")


def _send_approval_email(reg):
    send_mail(
        subject="VEMS — Vehicle Registration Approved",
        message=(
            f"Dear {reg.vehicle.owner_name},\n\n"
            f"Your vehicle registration has been approved.\n\n"
            f"Vehicle Number: {reg.vehicle.vehicle_number}\n"
            f"Vehicle: {reg.vehicle.vehicle_model} ({reg.vehicle.vehicle_color})\n\n"
            f"You can now bring your vehicle to the campus.\n\n"
            f"— AKGEC Vehicle Entry Management System"
        ),
        from_email=None,
        recipient_list=[reg.user.email],
        fail_silently=True,
    )
