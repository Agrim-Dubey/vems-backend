from django.urls import path

from vehicles.views import VehicleView

urlpatterns = [
    path("", VehicleView.as_view()),
]