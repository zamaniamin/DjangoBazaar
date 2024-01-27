import base64
import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model
from pyotp import TOTP
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


class TokenService:
    """Manage OTP and JWT tokens for authentication."""

    # -----------
    # --- OTP ---
    # -----------

    # TODO write test for check the otp generate for each user is not the same

    @classmethod
    def create_otp_token(cls, user_email: str) -> str:
        """Create a one-time password (OTP) token for the given user's email."""

        totp = TOTP(
            cls.__generate_secret_key(user_email),
            interval=int(settings.OTP_EXPIRE_SECONDS),
        )
        return totp.now()

    @staticmethod
    def __generate_secret_key(user_email: str) -> str:
        """Generate a secret key based on the user's email."""

        combined_data = f"{user_email}+{settings.OTP_SECRET_KEY}".encode("utf-8")
        hashed_data = hashlib.sha256(combined_data).digest()
        return base64.b32encode(hashed_data).decode("utf-8")

    @classmethod
    def otp_verification(cls, user_email: str, otp: str) -> bool:
        """Verify an OTP against the generated secret key for the given user's email."""

        totp = TOTP(
            cls.__generate_secret_key(user_email),
            interval=int(settings.OTP_EXPIRE_SECONDS),
        )
        return totp.verify(otp)

    # -----------
    # --- JWT ---
    # -----------

    @staticmethod
    def jwt_get_access_token(user: User) -> str:
        """Get the access token for the given user."""

        return str(AccessToken.for_user(user))

    @staticmethod
    def jwt_get_refresh_token(user: User) -> str:
        """Get the refresh token for the given user."""

        return str(RefreshToken.for_user(user))

    @staticmethod
    def jwt_get_tokens(user: User) -> tuple:
        """Get both the refresh token and access token for the given user."""

        return str(RefreshToken.for_user(user)), str(AccessToken.for_user(user))
