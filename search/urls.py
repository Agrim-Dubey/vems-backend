from django.urls import path

from search.views import PublicVehicleSearchView, StaffVehicleSearchView

urlpatterns = [
    path("vehicle/", PublicVehicleSearchView.as_view()),
    path("vehicle/staff/", StaffVehicleSearchView.as_view()),
]