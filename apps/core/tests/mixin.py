import io
import json
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime

from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory
from apps.core.services.time_service import DateTime
from apps.core.services.token_service import TokenService
from config import settings


class _APITestCaseMixin_(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Runs once per test class.

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

    def assertImageSrcPattern(self, src):
        # Define the regex pattern for the src
        pattern = r"^http://.*media.*$"

        # Assert that the src matches the pattern
        self.assertTrue(
            re.match(pattern, src), f"src '{src}' does not match the expected pattern"
        )

    def assertImageFileDirectory(self, src):
        """Assert that the image file exists in the correct directory based on the src URL."""

        # Extract the relative file path from the src
        match = re.search(r"testserver/(.*)", src)
        self.assertIsNotNone(match, "The src does not contain a valid path.")

        # Build the full path based on the extracted path and the base directory
        relative_path = match.group(1)
        full_file_path = os.path.join(settings.BASE_DIR, relative_path)

        # Assert that the file exists at the generated full path
        self.assertTrue(
            os.path.exists(full_file_path), f"File does not exist: {full_file_path}"
        )

    @staticmethod
    def generate_single_photo_file():
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file

    @staticmethod
    def generate_list_photo_files() -> list:
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

    def post_multipart(self, url, data: dict = None, **kwargs):
        if data is None:
            data = {}
        return self.client.post(url, data, format="multipart", **kwargs)


class _APITestCaseAuthorizationMixin(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Runs once per test class.

        # create users
        cls.admin = UserFactory.create(is_staff=True)
        cls.admin_access_token = TokenService.jwt_get_access_token(cls.admin)

        cls.regular_user = UserFactory.create()
        cls.regular_user_access_token = TokenService.jwt_get_access_token(
            cls.regular_user
        )

    def authorization_as_admin_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

    def authorization_as_regular_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"JWT {self.regular_user_access_token}"
        )

    def authorization_as_anonymous_user(self):
        self.client.credentials()


class APIAssertMixin(APITestCase):
    @staticmethod
    def assertDatetimeFormat(date: str | datetime):
        if isinstance(date, datetime):
            date = DateTime.string(date)

        formatted_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        assert date == formatted_date


class APIPostTestCaseMixin(ABC, _APITestCaseAuthorizationMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.response = None

    def setUp(self):
        self.authorization_as_admin_user()

    @abstractmethod
    def api_path(self) -> str:
        raise NotImplementedError("Please implement`api_path()` in your test class!")

    def send_request(self, payload: dict = None, **kwargs):
        """Send a POST request to the server and return response."""
        return self.client.post(
            path=self.api_path(),
            data=json.dumps(payload if payload else {}),
            content_type="application/json",
            **kwargs,
        )

    @abstractmethod
    def validate_response_body(self, response, payload):
        """Expected response body."""
        self.response = response.json()
        self._expected_status_code(response)

    def _expected_status_code(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_access_permission_by_regular_user(self):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_permission_by_anonymous_user(self):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIUpdateTestCaseMixin(ABC, _APITestCaseAuthorizationMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.response = None

    def setUp(self):
        self.authorization_as_admin_user()

    @abstractmethod
    def api_path(self) -> str:
        raise NotImplementedError("Please implement`api_path()` in your test class!")

    def send_request(self, path: str = None, payload: dict = None, **kwargs):
        """Send a POST request to the server and return response."""
        return self.client.put(
            path=path if path else self.api_path(),
            data=json.dumps(payload if payload else {}),
            content_type="application/json",
            **kwargs,
        )

    @abstractmethod
    def validate_response_body(self, response, payload):
        """Expected response body."""
        self.response = response.json()
        self._expected_status_code(response)

    def _expected_status_code(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_access_permission_by_regular_user(self):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_permission_by_anonymous_user(self):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
