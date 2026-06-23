import jwt
import os
import datetime

from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from accounts.utils import (
    generate_otp,
    generate_access_token,
    generate_refresh_token
)
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


class RegisterView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        otp = generate_otp()

        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email, otp=otp, is_verified=False)

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

    authentication_classes = []
    permission_classes = []

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
                {"message": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        expiry = otp_obj.created_at + datetime.timedelta(minutes=10)
        if timezone.now() > expiry:
            otp_obj.delete()
            return Response(
                {"message": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_verified = True
        otp_obj.save()

        return Response({"message": "OTP verified successfully"})

class LoginView(APIView):

    authentication_classes = []
    permission_classes = []

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

        if request.user.role == "ADMIN":
            return Response(
                {"message": "Access denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({
            "id": request.user.id,
            "email": request.user.email,
            "role": request.user.role
        })
    
class SetPasswordView(APIView):

    authentication_classes = []
    permission_classes = []

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
                {"message": "OTP verification required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "Account already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        User.objects.create(
            username=email.split("@")[0],
            email=email,
            password=make_password(password),
            is_verified=True
        )

        otp_obj.delete()

        return Response({"message": "Account created successfully"})


class RefreshTokenView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"message": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = jwt.decode(
                refresh_token,
                os.getenv("SECRET_KEY"),
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"message": "Refresh token expired"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.DecodeError:
            return Response(
                {"message": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if payload.get("type") != "refresh":
            return Response(
                {"message": "Invalid token type"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = User.objects.filter(id=payload["user_id"]).first()

        if not user:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = generate_access_token(user)

        return Response({"access_token": access_token})