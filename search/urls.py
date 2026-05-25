from django.urls import path

from search.views import PublicVehicleSearchView

urlpatterns = [
    path(
        "vehicle/",
        PublicVehicleSearchView.as_view()
    ),
]