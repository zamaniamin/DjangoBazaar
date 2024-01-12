from datetime import datetime

from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.time_service import DateTime
from apps.core.services.token_service import TokenService


class BaseCoreTestCase(APITestCase):
    regular_user = None
    admin = None

    @classmethod
    def setUpTestData(cls):
        # super().setUpTestData()

        # --- create users ---
        cls.admin = FakeUser.populate_admin()
        cls.admin_access_token = TokenService.jwt_get_access_token(cls.admin)

        cls.regular_user = FakeUser.populate_user()
        cls.user_access_token = TokenService.jwt_get_access_token(cls.regular_user)

    @staticmethod
    def assertDatetimeFormat(date: str | datetime):
        if isinstance(date, datetime):
            date = DateTime.string(date)

        formatted_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        assert date == formatted_date
