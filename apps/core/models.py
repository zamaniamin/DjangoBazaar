from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.managers.user_manager import UserManager


class User(AbstractUser):
    """
    Represents a user in the system.

    Note: Users can't change their username.

    Attributes:
        email (str): The email address of the user (required, max length 255, unique).
        username (str): The username of the user (required, max length 255).
        USERNAME_FIELD (str): The field used for authentication (set to 'email').
        REQUIRED_FIELDS (list): Additional fields required for creating a user (set to an empty list).

    """

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=False, null=False)
    USERNAME_FIELD = "email"

    # fix error [users.User: (auth.E002)], so you should remove 'email' from the 'REQUIRED_FIELDS', like this.
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        """
        Save method to set the username to the email before saving the user.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        self.username = self.email
        super().save(*args, **kwargs)


class UserVerification(models.Model):
    """
    Represents a user verification model.

    Attributes:
        user (User): The user associated with the verification.
        new_email (str): The new email address for verification (max length 255).

    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    new_email = models.EmailField(max_length=255)
