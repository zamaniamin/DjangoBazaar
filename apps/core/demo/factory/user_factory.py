import factory
from factory.django import DjangoModelFactory

from apps.core.demo.factory.core_factory_settings import REGULAR_USERS_COUNT
from config import settings


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "user1234")

    @classmethod
    def populate_demo_users(cls):
        cls.create(email="super@test.test", is_superuser=True, is_staff=True)
        cls.create(email="admin@test.test", is_staff=True)
        cls.create(email="user1@test.test")
        cls.create(email="user2@test.test")
        cls.create(email="user3@test.test", is_active=False)

        print(f"Adding {REGULAR_USERS_COUNT} users ... ", end="")
        for regular in range(REGULAR_USERS_COUNT - 3):
            cls.create()
        print("DONE")

    @classmethod
    def random_email(cls):
        return cls.build().email

    @classmethod
    def demo_password(cls):
        return "user1234"
