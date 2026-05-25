from django.urls import path

from staffs.views import (
    DashboardStatsView,
    PendingRegistrationsView,
    ApproveRegistrationView,
    RejectRegistrationView
)

urlpatterns = [

    path(
        "dashboard/stats/",
        DashboardStatsView.as_view()
    ),

    path(
        "registrations/pending/",
        PendingRegistrationsView.as_view()
    ),

    path(
        "registrations/<int:registration_id>/approve/",
        ApproveRegistrationView.as_view()
    ),

    path(
        "registrations/<int:registration_id>/reject/",
        RejectRegistrationView.as_view()
    ),
]