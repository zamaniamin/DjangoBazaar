# from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives


class EmailService:
    current_site: Site = Site.objects.get_current()

    @classmethod
    def send_activation_email(cls, to_address):
        """
        Sends a verification email for the registration process.
        """
        try:

            # Create an email message with both plain text and HTML content
            email = EmailMultiAlternatives(
                subject="Email Verification",
                body=f"Thank you for registering with \"{cls.current_site.name}\"!\n\n" \
                     f"To complete your registration, please enter the following code: {123}\n\n" \
                     f"If you didn't register, please ignore this email.",
                from_email=settings.EMAIL_HOST_USER,
                to=[to_address]
            )

            # Send the email
            email.send(fail_silently=False)

        except Exception as e:

            # Handle any exceptions that occur during sending
            raise Exception(f'Failed to send email: {str(e)}')
