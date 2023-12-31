from faker import Faker

from apps.core.models import User


class FakeUser:
    """
    Populates the database with fake users.
    """

    fake = Faker()

    # --- demo users ---
    superuser_email = 'super@test.test'
    admin_email = 'admin@test.test'
    user1_email = 'user1@test.test'
    user2_email = 'user2@test.test'
    user3_email = 'user3@test.test'
    password = 'user1234'

    @classmethod
    def random_email(cls):
        return cls.fake.email()

    @classmethod
    def populate_demo_users(cls):
        cls.populate_superuser()
        cls.populate_admin()
        cls.populate_user(cls.user1_email)
        cls.populate_user(cls.user2_email)
        cls.populate_inactive_user(cls.user3_email)

    @classmethod
    def populate_superuser(cls):
        """
        Create a new superuser.
        """

        user = User.objects.create_user(email=cls.superuser_email, password=cls.password, is_superuser=True,
                                        is_staff=True)
        return user

    @classmethod
    def populate_admin(cls):
        """
        Creat a new admin.
        """

        user = User.objects.create_user(email=cls.admin_email, password=cls.password, is_staff=True)
        return user

    @classmethod
    def populate_user(cls, email=None):
        """
        Create a new user.
        """
        if not email:
            email = cls.random_email()

        user = User.objects.create_user(email=email, password=cls.password)
        return user

    @classmethod
    def populate_inactive_user(cls, email=None):
        """
        Create a new inactive user.
        """

        if not email:
            email = cls.random_email()

        user = User.objects.create_user(email=email, password=cls.password, is_active=False)
        return user
