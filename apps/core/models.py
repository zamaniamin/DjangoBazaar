from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.managers.user_manager import UserManager


class User(AbstractUser):
    """
    Note: Users cant change their username.
    """

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=False, null=False)
    USERNAME_FIELD = 'email'

    # fix error [users.User: (auth.E002)], so you should remove 'email' from the 'REQUIRED_FIELDS', like this.
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)


class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    new_email = models.EmailField(max_length=255)
