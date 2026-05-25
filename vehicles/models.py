from django.db import models

from accounts.models import User


class Vehicle(models.Model):

    class VehicleType(models.TextChoices):
        CAR = "CAR", "Car"
        BIKE = "BIKE", "Bike"
        SCOOTY = "SCOOTY", "Scooty"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )

    owner_name = models.CharField(
        max_length=255
    )

    vehicle_number = models.CharField(
        max_length=50,
        unique=True
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices
    )

    vehicle_model = models.CharField(
        max_length=255
    )

    vehicle_color = models.CharField(
        max_length=100
    )

    rc_number = models.CharField(
        max_length=100
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )