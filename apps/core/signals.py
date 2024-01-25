from apps.core.services.email.email_service import EmailService


def send_activation_email(sender, instance, created, **kwargs):
    if created:
        EmailService.send_activation_email(instance.email)
