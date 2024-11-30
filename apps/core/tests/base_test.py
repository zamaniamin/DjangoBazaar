import io
import json
from datetime import datetime

from PIL import Image
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory
from apps.core.services.time_service import DateTime
from apps.core.services.token_service import TokenService


class CoreBaseTestCase(APITestCase):
    regular_user = None
    admin = None

    @classmethod
    def setUpTestData(cls):
        # create users
        cls.admin = UserFactory.create(is_staff=True)
        cls.admin_access_token = TokenService.jwt_get_access_token(cls.admin)

        cls.regular_user = UserFactory.create()
        cls.regular_user_access_token = TokenService.jwt_get_access_token(
            cls.regular_user
        )

    def set_admin_user_authorization(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

    def set_regular_user_authorization(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"JWT {self.regular_user_access_token}"
        )

    def set_anonymous_user_authorization(self):
        self.client.credentials()

    @staticmethod
    def assertDatetimeFormat(date: str | datetime):
        if isinstance(date, datetime):
            date = DateTime.string(date)

        formatted_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        assert date == formatted_date

    @staticmethod
    def generate_single_photo_file():
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file

    @staticmethod
    def generate_list_photo_files():
        files = []

        for i in range(1, 5):
            file = io.BytesIO()
            image = Image.new("RGBA", size=(100, 100), color=(155 * i, 0, 0))
            image.save(file, "png")
            file.name = f"test_{i}.png"
            file.seek(0)
            files.append(file)

        return files

    def post_json(self, url, data: dict = None, **kwargs):
        if data is None:
            data = {}
        return self.client.post(
            url, data=json.dumps(data), content_type="application/json", **kwargs
        )

    def put_json(self, url, data: dict = None, **kwargs):
        if data is None:
            data = {}
        return self.client.put(
            url, data=json.dumps(data), content_type="application/json", **kwargs
        )
