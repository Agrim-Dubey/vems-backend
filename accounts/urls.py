from django.urls import path

from accounts.views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    MeView,
    SetPasswordView,
    RefreshTokenView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("set-password/", SetPasswordView.as_view()),
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshTokenView.as_view()),
    path("me/", MeView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("forgot-password/reset/", ResetPasswordView.as_view()),
]