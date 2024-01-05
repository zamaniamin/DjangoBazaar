from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.

        Args:
            email (str): Email address for the superuser.
            password (str): Password for the superuser.
            **extra_fields: Additional fields for the superuser.

        Returns:
            User: The created superuser instance.

        Raises:
            ValueError: If is_staff or is_superuser attributes are not set correctly.

        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have `is_staff=True`')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have `is_superuser=True`')

        return self.create_user(email, password, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a user with the given email and password.

        Args:
            email (str): Email address for the user.
            password (str): Password for the user.
            **extra_fields: Additional fields for the user.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If the email field is not set.

        """

        if not email:
            raise ValueError('Email field must be set')

        # `normalize_email` ensure that the email address is correctly formatted and valid before saved to the database
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
