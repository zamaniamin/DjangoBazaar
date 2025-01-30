import json
from abc import ABC, abstractmethod
from datetime import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory
from apps.core.services.time_service import DateTime
from apps.core.services.token_service import TokenService


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
        cls.response_body = None

    def setUp(self):
        self.authorization_as_admin_user()

    @abstractmethod
    def api_path(self) -> str:
        raise NotImplementedError("Please implement`api_path()` in your test class!")

    def send_request(self, payload: dict = None, path: str = None, **kwargs):
        """Send a POST request to the server and return response."""
        return self.client.post(
            path=path if path else self.api_path(),
            data=json.dumps(payload if payload else {}),
            content_type="application/json",
            **kwargs,
        )

    def send_multipart_request(self, payload: dict = None, path: str = None, **kwargs):
        """Send a POST request to the server and return response."""
        return self.client.post(
            path=path if path else self.api_path(),
            data=payload if payload else {},
            format="multipart",
            **kwargs,
        )

    @abstractmethod
    def validate_response_body(self, response, payload):
        """Expected response body."""
        self.response_body = response.json()
        self.expected_status_code(response)

    def expected_status_code(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def check_access_permission_by_regular_user(
        self, status_code: int = status.HTTP_403_FORBIDDEN
    ):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response

    def check_access_permission_by_anonymous_user(
        self, status_code: int = status.HTTP_401_UNAUTHORIZED
    ):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response


class APIGetTestCaseMixin(ABC, _APITestCaseAuthorizationMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.response_body = None

    def setUp(self):
        self.authorization_as_admin_user()

    @abstractmethod
    def api_path(self) -> str:
        pass
        raise NotImplementedError("Please implement`api_path()` in your test class!")

    def send_request(self, path: str = None):
        """Send a GET request to the server and return response."""
        return self.client.get(path=path if path else self.api_path())

    @abstractmethod
    def validate_response_body(self, response, payload: dict = None):
        """Expected response body."""
        self.response_body = response.json()
        self.assertHTTPStatusCode(response)

    # TODO check all test status with this method
    def assertHTTPStatusCode(self, response, status_code: int = status.HTTP_200_OK):
        self.assertEqual(response.status_code, status_code)

    def check_access_permission_by_regular_user(
        self, status_code: int = status.HTTP_200_OK
    ):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response

    def check_access_permission_by_anonymous_user(
        self, status_code: int = status.HTTP_200_OK
    ):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response


class APIUpdateTestCaseMixin(ABC, _APITestCaseAuthorizationMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.response_body = None

    def setUp(self):
        self.authorization_as_admin_user()

    @abstractmethod
    def api_path(self) -> str:
        raise NotImplementedError("Please implement`api_path()` in your test class!")

    def send_request(self, payload: dict = None, path: str = None, **kwargs):
        """Send a PUT request to the server and return response."""
        return self.client.put(
            path=path if path else self.api_path(),
            data=json.dumps(payload if payload else {}),
            content_type="application/json",
            **kwargs,
        )

    @abstractmethod
    def validate_response_body(self, response, payload):
        """Expected response body."""
        self.response_body = response.json()
        self.expected_status_code(response)

    def expected_status_code(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def check_access_permission_by_regular_user(
        self, status_code: int = status.HTTP_403_FORBIDDEN
    ):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response

    def check_access_permission_by_anonymous_user(
        self, status_code: int = status.HTTP_401_UNAUTHORIZED
    ):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response


class APIDeleteTestCaseMixin(ABC, _APITestCaseAuthorizationMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.response_body = None

    def setUp(self):
        self.authorization_as_admin_user()

    @abstractmethod
    def api_path(self) -> str:
        raise NotImplementedError("Please implement`api_path()` in your test class!")

    def send_request(self, path: str = None, **kwargs):
        """Send a DELETE request to the server and return response."""
        return self.client.delete(path=path if path else self.api_path())

    def expected_status_code(self, response):
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def check_access_permission_by_regular_user(
        self, status_code: int = status.HTTP_403_FORBIDDEN
    ):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response

    def check_access_permission_by_anonymous_user(
        self, status_code: int = status.HTTP_401_UNAUTHORIZED
    ):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertEqual(response.status_code, status_code)
        return response
