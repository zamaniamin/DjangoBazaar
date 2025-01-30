from django.urls import reverse

from apps.core.tests.mixin import APIUpdateTestCaseMixin


class PartialUpdateProfileTest(APIUpdateTestCaseMixin):
    def api_path(self) -> str:
        return reverse("user-me")

    def validate_response_body(self, response, payload):
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
        self.authorization_as_regular_user()
        payload = {"first_name": "member f name"}
        response = self.send_patch_request(payload)
        self.validate_response_body(response, payload)

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_partial_update(self):
        payload = {
            "first_name": "admin f name",
            "last_name": "admin l name",
        }
        response = self.send_patch_request(payload)
        self.validate_response_body(response, payload)
