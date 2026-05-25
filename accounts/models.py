from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "User"
        STAFF = "STAFF", "Staff"
        ADMIN = "ADMIN", "Admin"


    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    email = models.EmailField(unique=True)

    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class EmailOTP(models.Model):

    email = models.EmailField(unique=True)

    otp = models.CharField(max_length=6)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
