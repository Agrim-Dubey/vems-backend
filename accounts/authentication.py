import jwt
import os

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise AuthenticationFailed("Invalid authorization header format")

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                os.getenv("SECRET_KEY"),
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.DecodeError:
            raise AuthenticationFailed("Invalid token")

        user = User.objects.filter(id=payload["user_id"]).first()

        if not user:
            raise AuthenticationFailed("User not found")

        return (user, token)