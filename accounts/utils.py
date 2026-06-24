import secrets
import jwt
import os
from datetime import datetime, timedelta, timezone


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


def generate_access_token(user):

    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": now + timedelta(minutes=15),
        "iat": now,
        "type": "access"
    }

    return jwt.encode(
        payload,
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )


def generate_refresh_token(user):

    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user.id,
        "exp": now + timedelta(days=7),
        "iat": now,
        "type": "refresh"
    }

    return jwt.encode(
        payload,
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )