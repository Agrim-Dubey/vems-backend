from django.urls import path

from registrations.views import RegistrationView

urlpatterns = [
    path("", RegistrationView.as_view()),
]