from django.urls import path

from ocr.views import ProcessOCRView

urlpatterns = [
    path(
        "process/<int:document_id>/",
        ProcessOCRView.as_view()
    ),
]