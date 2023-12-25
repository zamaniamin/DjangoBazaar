from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.

        We're subclassing the built-in `BaseUserManager` class and overriding its `create_superuser` method.
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
        Creates and saves a SuperUser with the given email and password.

        We're subclassing the built-in `BaseUserManager` class and overriding its `create_user` method.
        """

        if not email:
            raise ValueError('Email field must be set')

        # `normalize_email` ensure that the email address is correctly formatted and valid before saved to the database
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    @classmethod
    def create_inactive_user(cls, **user_data):
        """
        Creates and saves an inactive user.
        """

        new_user = get_user_model().objects.create(**user_data)
        new_user.set_password(user_data['password'])
        new_user.is_active = False
        new_user.save()
        return new_user
