from faker import Faker

from apps.core.models import User


class FakeUser:
    """
    Utility class for populating the database with fake users.

    Attributes:
        fake (Faker): An instance of the Faker library for generating fake data.
        superuser_email (str): Email for the superuser.
        admin_email (str): Email for the admin user.
        user1_email (str): Email for the first user.
        user2_email (str): Email for the second user.
        user3_email (str): Email for the third user.
        password (str): Default password for the demo users.

    Methods:
        random_email(): Generate a random fake email address.
        populate_demo_users(): Populate the database with demo users.

    """
    fake = Faker()

    # Demo users
    superuser_email = 'super@test.test'
    admin_email = 'admin@test.test'
    user1_email = 'user1@test.test'
    user2_email = 'user2@test.test'
    user3_email = 'user3@test.test'
    password = 'user1234'

    @classmethod
    def random_email(cls):
        """
        Generate a random fake email address.

        Returns:
            str: A random fake email address.

        """
        return cls.fake.email()

    @classmethod
    def populate_demo_users(cls):
        """
        Populate the database with demo users.

        """
        cls.populate_superuser()
        cls.populate_admin()
        cls.populate_user(cls.user1_email)
        cls.populate_user(cls.user2_email)
        cls.populate_inactive_user(cls.user3_email)

    @classmethod
    def populate_superuser(cls):
        """
        Create a new superuser.

        Returns:
            User: The newly created superuser.

        """
        user = User.objects.create_user(email=cls.superuser_email, password=cls.password, is_superuser=True,
                                        is_staff=True)
        return user

    @classmethod
    def populate_admin(cls):
        """
        Create a new admin.

        Returns:
            User: The newly created admin.

        """
        user = User.objects.create_user(email=cls.admin_email, password=cls.password, is_staff=True)
        return user

    @classmethod
    def populate_user(cls, email=None):
        """
        Create a new user.

        Args:
            email (str, optional): The email address for the new user. If not provided, a random email is generated.

        Returns:
            User: The newly created user.

        """
        if not email:
            email = cls.random_email()

        user = User.objects.create_user(email=email, password=cls.password)
        return user

    @classmethod
    def populate_inactive_user(cls, email=None):
        """
        Create a new inactive user.

        Args:
            email (str, optional): The email address for the new user. If not provided, a random email is generated.

        Returns:
            User: The newly created inactive user.

        """
        if not email:
            email = cls.random_email()

        user = User.objects.create_user(email=email, password=cls.password, is_active=False)
        return user
