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

    @classmethod
    def create_otp_token(cls):
        totp = TOTP(settings.OTP_SECRET_KEY, interval=int(settings.OTP_EXPIRE_SECONDS))
        return totp.now()

    @classmethod
    def validate_otp_token(cls, token: str):
        totp = TOTP(settings.OTP_SECRET_KEY, interval=int(settings.OTP_EXPIRE_SECONDS))
        return totp.verify(token)

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
