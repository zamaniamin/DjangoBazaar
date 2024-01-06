from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives

from apps.core.services.token_service import TokenService


class EmailService:
    @classmethod
    def __send_email(cls, subject, body, to_address):
        """
        Sends an email with the provided subject, body, and recipient address.

        Args:
            subject (str): The subject of the email.
            body (str): The body content of the email.
            to_address (str): The recipient's email address.

        Raises:
            Exception: If there is an error during the email sending process.

        """
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[to_address],
            )
            email.send(fail_silently=False)

        except Exception as e:
            # Handle any exceptions that occur during sending
            raise Exception(f"Failed to send email: {str(e)}")

    @classmethod
    def send_activation_email(cls, to_address):
        """
        Sends a verification email for the registration process.

        Args:
            to_address (str): The recipient's email address.

        """
        otp = TokenService.create_otp_token(to_address)
        subject = "Email Verification"
        body = (
            f'Thank you for registering with "{Site.objects.get_current().name}"!\n\n'
            f"To complete your registration, please enter the following code: {otp}\n\n"
            f"If you didn't register, please ignore this email."
        )

        cls.__send_email(subject, body, to_address)

    @classmethod
    def send_change_email(cls, to_address):
        """
        Sends a verification email to the new-email for the change process.

        Args:
            to_address (str): The recipient's email address.

        """
        otp = TokenService.create_otp_token(to_address)
        subject = "Email Change Verification"
        body = (
            f'We received a request to change the email associated with your "{Site.objects.get_current().name}" account. \n'
            f"To confirm this change, please enter the following code: {otp}\n\n"
            f"If you didn't request this, please contact our support team."
        )

        cls.__send_email(subject, body, to_address)

    @classmethod
    def send_reset_password_email(cls, to_address):
        """
        Sends a verification email for the password reset process.

        Args:
            to_address (str): The recipient's email address.

        """
        otp = TokenService.create_otp_token(to_address)
        subject = "Password Reset Verification"
        body = (
            f'We received a request to reset your "{Site.objects.get_current().name}" password.\n\n'
            f"Please enter the following code to reset your password: {otp}\n\n"
            f"If you didn't register, please ignore this email."
        )

        cls.__send_email(subject, body, to_address)
