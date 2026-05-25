from django.db import models

from accounts.models import User


class UserProfile(models.Model):

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(max_length=255)

    student_id = models.CharField(max_length=50)

    phone_number = models.CharField(max_length=15)

    department = models.CharField(max_length=100)

    year = models.IntegerField()

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices
    )

    hostel_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    is_profile_completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

