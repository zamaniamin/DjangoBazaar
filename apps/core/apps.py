from django.apps import AppConfig
from django.db.models.signals import post_save

from config import settings


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        from apps.core.signals import send_activation_email

        post_save.connect(send_activation_email, sender=settings.AUTH_USER_MODEL)
