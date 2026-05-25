import random
import jwt
import datetime
import os




def generate_otp():
    return str(random.randint(100000, 999999))

def generate_access_token(user):

    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        "iat": datetime.datetime.utcnow(),
        "type": "access"
    }

    return jwt.encode(
        payload,
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )


def generate_refresh_token(user):

    payload = {
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "iat": datetime.datetime.utcnow(),
        "type": "refresh"
    }

    return jwt.encode(
        payload,
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )