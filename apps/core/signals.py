from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.services.email.email_service import EmailService


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        EmailService.send_activation_email(instance.email)
