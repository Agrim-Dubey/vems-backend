from django.urls import path

from documents.views import DocumentUploadView

urlpatterns = [
    path("upload/", DocumentUploadView.as_view()),
]