from faker import Faker

from apps.core.models import User


class FakeUser:
    """
    Populates the database with fake users.
    """

    fake = Faker()
    password = 'Demo_1234'

    @classmethod
    def random_email(cls):
        return cls.fake.email()

    @classmethod
    def populate_superuser(cls):
        """
        Create a new superuser.
        """

        user = User.objects.create_user(email=cls.random_email(), password=cls.password, is_superuser=True,
                                        is_staff=True)
        return user

    @classmethod
    def populate_admin(cls):
        """
        Creat a new admin.
        """

        user = User.objects.create_user(email=cls.random_email(), password=cls.password, is_staff=True)
        return user

    @classmethod
    def populate_user(cls):
        """
        Create a new user.
        """

        user = User.objects.create_user(email=cls.random_email(), password=cls.password)
        return user

    @classmethod
    def populate_inactive_user(cls):
        """
        Create a new inactive user.
        """

        user = User.objects.create_user(email=cls.random_email(), password=cls.password, is_active=False)
        return user
