import base64
import hashlib

from django.conf import settings
from pyotp import TOTP
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.core.models import User


class TokenService:
    """
    Manage "jwt-token" or "otp-token" that used for authentication.
    """

    # -----------
    # --- OTP ---
    # -----------

    # TODO write test for check the otp generate for each user is not the same

    @classmethod
    def create_otp_token(cls, user_email: str):
        totp = TOTP(cls.__generate_secret_key(user_email), interval=int(settings.OTP_EXPIRE_SECONDS))
        return totp.now()

    @staticmethod
    def __generate_secret_key(user_email: str):
        """
        Generate a secret key based on the user's email.
        """

        # Combine user email with additional information (if needed) and encode
        combined_data = f"{user_email}+{settings.OTP_SECRET_KEY}".encode('utf-8')
        hashed_data = hashlib.sha256(combined_data).digest()

        # Use base64 encoding and then convert to base32
        return base64.b32encode(hashed_data).decode('utf-8')

    @classmethod
    def otp_verification(cls, user_email: str, otp: str):
        totp = TOTP(cls.__generate_secret_key(user_email), interval=int(settings.OTP_EXPIRE_SECONDS))
        return totp.verify(otp)

    # -----------
    # --- JWT ---
    # -----------

    @staticmethod
    def jwt__get_access_token(user: User):
        return str(AccessToken.for_user(user))

    @staticmethod
    def jwt__get_refresh_token(user: User):
        return str(RefreshToken.for_user(user))

    @staticmethod
    def jwt__get_tokens(user: User):
        return str(RefreshToken.for_user(user)), str(AccessToken.for_user(user))
