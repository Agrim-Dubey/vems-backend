from django.db import models

from accounts.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=150)

    last_name = models.CharField(max_length=150)

    student_number = models.CharField(max_length=50, unique=True)

    photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True
    )

    is_profile_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

