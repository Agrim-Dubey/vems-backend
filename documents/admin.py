from django.contrib import admin

from documents.models import UserDocument


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ["user", "document_type", "ocr_status", "verification_status", "uploaded_at"]
    search_fields = ["user__email"]
    list_filter = ["document_type", "ocr_status", "verification_status"]
    readonly_fields = ["extracted_data", "ocr_status"]
