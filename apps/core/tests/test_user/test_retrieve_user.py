from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin, APIAssertMixin


class RetrieveUserTest(APIGetTestCaseMixin, APIAssertMixin):
    def api_path(self) -> str:
        return reverse("user-detail", kwargs={"pk": self.regular_user.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), 7)
        self.assertIsInstance(self.response_body["id"], int)
        self.assertIsInstance(self.response_body["email"], str)
        self.assertIsInstance(self.response_body["first_name"], str)
        self.assertIsInstance(self.response_body["last_name"], str)
        self.assertIsInstance(self.response_body["is_active"], bool)
        self.assertDatetimeFormat(self.response_body["date_joined"])
        self.assertTrue(
            self.response_body["last_login"] is None
            or self.assertDatetimeFormat(self.response_body["last_login"])
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user(status.HTTP_403_FORBIDDEN)

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user(status.HTTP_401_UNAUTHORIZED)

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)
