from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin, APIAssertMixin


class ListUserTest(APIGetTestCaseMixin, APIAssertMixin):
    def api_path(self) -> str:
        return reverse("user-list")

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), 2)
        for user in self.response_body:
            self.assertEqual(len(user), 7)
            self.assertIsInstance(user["id"], int)
            self.assertIsInstance(user["email"], str)
            self.assertIsInstance(user["first_name"], str)
            self.assertIsInstance(user["last_name"], str)
            self.assertIsInstance(user["is_active"], bool)
            self.assertDatetimeFormat(user["date_joined"])
            self.assertTrue(
                user["last_login"] is None
                or self.assertDatetimeFormat(user["last_login"])
            )

    def test_access_permission_by_regular_user(self):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.expected_status_code(response, status.HTTP_403_FORBIDDEN)

    def test_access_permission_by_anonymous_user(self):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.expected_status_code(response, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        response = self.send_request()
        self.validate_response_body(response)
