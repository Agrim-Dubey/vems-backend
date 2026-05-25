from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from accounts.utils import (
    generate_otp,
    generate_access_token,
    generate_refresh_token
)
from django.contrib.auth.hashers import make_password
from .serializers import SetPasswordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import User, EmailOTP
from accounts.serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    LoginSerializer
)

from accounts.utils import generate_otp


class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        otp = generate_otp()

        EmailOTP.objects.update_or_create(
            email=email,
            defaults={
                "otp": otp,
                "is_verified": False
            }
        )

        send_mail(
            "VEMS OTP Verification",
            f"Your OTP is {otp}",
            None,
            [email]
        )

        return Response({
            "message": "OTP sent successfully"
        })


class VerifyOTPView(APIView):

    def post(self, request):

        serializer = VerifyOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        otp = serializer.validated_data["otp"]

        otp_obj = EmailOTP.objects.filter(
            email=email,
            otp=otp
        ).first()

        if not otp_obj:
            return Response(
                {
                    "message": "Invalid OTP"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_verified = True

        otp_obj.save()

        return Response({
            "message": "OTP verified successfully"
        })

class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        password = serializer.validated_data["password"]

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if not user:
            return Response(
                {
                    "message": "Invalid credentials"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        access_token = generate_access_token(user)

        refresh_token = generate_refresh_token(user)

        return Response({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "id": request.user.id,
            "email": request.user.email
        })
    
class SetPasswordView(APIView):

    def post(self, request):

        serializer = SetPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        password = serializer.validated_data["password"]

        otp_obj = EmailOTP.objects.filter(
            email=email,
            is_verified=True
        ).first()

        if not otp_obj:
            return Response(
                {
                    "message": "OTP verification required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            username=email.split("@")[0],
            email=email,
            password=make_password(password),
            is_verified=True
        )

        return Response({
            "message": "Account created successfully"
        })