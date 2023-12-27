from faker import Faker

from apps.core.managers.user_manager import UserManager
from apps.core.models import User


class FakeUser:
    """
    Populates the database with fake accounts.
    """

    fake = Faker()
    password = 'Demo_1234'

    @classmethod
    def random_email(cls):
        return cls.fake.email()

    @classmethod
    def create_inactive_user(cls):
        """
        Register a new user and get the OTP code.
        """

        # --- register a user ---
        register_payload = {
            'email': cls.random_email(),
            'password': cls.password
        }
        return UserManager.create_inactive_user(**register_payload)

    @classmethod
    def create_active_user(cls):
        """
        Registered a new user and verified their OTP code.
        """
        user = User.objects.create_user(email=cls.random_email(), password=cls.password)
        return user

    # @classmethod
    # def populate_members(cls):
    #     """
    #     Create an admin and a user.
    #     """
    #
    #     # --- admin ---
    #     user, access_token = FakeAccount.verified_registration()
    #     user_data = {
    #         'email': 'superuser@example.com',
    #         'first_name': cls.fake.first_name(),
    #         'last_name': cls.fake.last_name(),
    #         'is_superuser': True,
    #         'role': 'admin'
    #     }
    #
    #     UserService.update_user(user.id, **user_data)
    #
    #     # --- user ---
    #     user, access_token = FakeAccount.verified_registration()
    #     user_data = {
    #         'email': 'member@example.com',
    #         'first_name': cls.fake.first_name(),
    #         'last_name': cls.fake.last_name()
    #     }
    #
    #     UserService.update_user(user.id, **user_data)

    # @classmethod
    # def populate_superuser(cls):
    #     """
    #     Create an admin and generate an access token too.
    #     """
    #
    #     user, access_token = FakeAccount.verified_registration()
    #     user = UserService.update_user(user.id)
    #     UserService.set_role(user.id, 'superuser')
    #
    #     return user, access_token

    # @classmethod
    # def populate_user(cls):
    #     """
    #     Create a new user and generate an access token too.
    #     """
    #
    #     user, access_token = FakeAccount.verified_registration()
    #     user_data = {
    #         'first_name': cls.fake.first_name(),
    #         'last_name': cls.fake.last_name()
    #     }
    #
    #     user = UserService.update_user(user.id, **user_data)
    #     return user, access_token
