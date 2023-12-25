from django.conf import settings
from pyotp import TOTP


class TokenService:
    """
    Manage "jwt-token" or "otp-token" that used for authentication.
    """

    @classmethod
    def create_otp_token(cls):
        totp = TOTP(settings.OTP_SECRET_KEY, interval=int(settings.OTP_EXPIRE_SECONDS))
        return totp.now()
