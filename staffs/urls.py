from django.urls import path

from staffs.views import (
    DashboardStatsView,
    AllRegistrationsView,
    RegistrationDetailView,
    ApproveRegistrationView,
    RejectRegistrationView,
)

urlpatterns = [
    path("dashboard/stats/", DashboardStatsView.as_view()),
    path("registrations/", AllRegistrationsView.as_view()),
    path("registrations/<int:registration_id>/", RegistrationDetailView.as_view()),
    path("registrations/<int:registration_id>/approve/", ApproveRegistrationView.as_view()),
    path("registrations/<int:registration_id>/reject/", RejectRegistrationView.as_view()),
]
