from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives

from apps.core.services.token_service import TokenService


class EmailService:

    @classmethod
    def send_activation_email(cls, to_address):
        """
        Sends a verification email for the registration process.
        """
        try:
            # note: dont use `Site.objects.get_current()` during the class initialization process.
            otp = TokenService.create_otp_token()
            email = EmailMultiAlternatives(
                subject="Email Verification",
                body=f"Thank you for registering with \"{Site.objects.get_current().name}\"!\n\n" \
                     f"To complete your registration, please enter the following code: {otp}\n\n" \
                     f"If you didn't register, please ignore this email.",
                from_email=settings.EMAIL_HOST_USER,
                to=[to_address]
            )

            # Send the email
            email.send(fail_silently=False)

        except Exception as e:

            # Handle any exceptions that occur during sending
            raise Exception(f'Failed to send email: {str(e)}')

    @classmethod
    def send_change_email(cls, to_address):
        """
        Sends a verification email to the new-email for change process.
        """
        try:
            otp = TokenService.create_otp_token()
            email = EmailMultiAlternatives(
                subject="Email Change Verification",
                body=f"We received a request to change the email associated with your \"{Site.objects.get_current().name}\" account. \n" \
                     f"To confirm this change, please enter the following code:: {otp}\n\n" \
                     f"If you didn't request this, please contact our support team.",
                from_email=settings.EMAIL_HOST_USER,
                to=[to_address]
            )

            # Send the email
            email.send(fail_silently=False)

        except Exception as e:

            # Handle any exceptions that occur during sending
            raise Exception(f'Failed to send email: {str(e)}')
