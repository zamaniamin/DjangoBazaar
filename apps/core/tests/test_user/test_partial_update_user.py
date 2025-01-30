import json

from django.urls import reverse

from apps.core.tests.mixin import APIUpdateTestCaseMixin, APIAssertMixin


class UpdateUserTest(APIUpdateTestCaseMixin, APIAssertMixin):
    def api_path(self) -> str:
        return reverse("user-detail", kwargs={"pk": self.regular_user.id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response), 7)
        self.assertEqual(self.response["id"], self.regular_user.id)
        self.assertEqual(self.response["email"], self.regular_user.email)
        self.assertEqual(self.response["first_name"], payload["first_name"])
        self.assertEqual(self.response["last_name"], self.regular_user.last_name)
        self.assertEqual(self.response["is_active"], self.regular_user.is_active)
        self.assertDatetimeFormat(self.response["date_joined"])
        self.assertTrue(
            self.response["last_login"] is None
            or self.assertDatetimeFormat(self.response["last_login"])
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_partial_update(self):
        payload = {"first_name": "test F name"}
        response = self.client.patch(
            self.api_path(),
            json.dumps(payload),
            content_type="application/json",
        )
