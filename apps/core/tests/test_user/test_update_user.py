from django.urls import reverse

from apps.core.tests.mixin import APIUpdateTestCaseMixin, APIAssertMixin


class UpdateUserTest(APIUpdateTestCaseMixin, APIAssertMixin):
    def api_path(self) -> str:
        return reverse("user-detail", kwargs={"pk": self.regular_user.id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response), 7)
        self.assertIsInstance(self.response["id"], int)
        self.assertEqual(self.response["email"], payload["email"])
        self.assertEqual(self.response["first_name"], payload["first_name"])
        self.assertEqual(self.response["last_name"], payload["last_name"])
        self.assertEqual(self.response["is_active"], payload["is_active"])
        self.assertDatetimeFormat(self.response["date_joined"])
        self.assertTrue(
            self.response["last_login"] is None
            or self.assertDatetimeFormat(self.response["last_login"])
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_update_user(self):
        payload = {
            "email": self.regular_user.email,
            "first_name": "F name",
            "last_name": "L name",
            "is_active": True,
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)
