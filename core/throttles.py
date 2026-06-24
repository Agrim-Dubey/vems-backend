from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class OTPRateThrottle(AnonRateThrottle):
    """5 OTP requests per hour per IP — prevents email spam."""
    scope = "otp"


class LoginRateThrottle(AnonRateThrottle):
    """20 login attempts per hour per IP — brute force protection."""
    scope = "login"


class UploadRateThrottle(UserRateThrottle):
    """30 document uploads per hour per user — OCR is expensive."""
    scope = "upload"


class PublicSearchRateThrottle(AnonRateThrottle):
    """60 searches per minute per IP — guards scan frequently."""
    scope = "search"


class StaffSearchRateThrottle(UserRateThrottle):
    """120 searches per minute per staff user."""
    scope = "search"
