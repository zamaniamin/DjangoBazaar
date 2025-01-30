from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin


class RetrieveProfileTest(APIGetTestCaseMixin):
    def api_path(self) -> str:
        return reverse("user-me")

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(self.response_body.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "is_staff",
                "date_joined",
                "last_login",
            },
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user(status.HTTP_401_UNAUTHORIZED)

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)
