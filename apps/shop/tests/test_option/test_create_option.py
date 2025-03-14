from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin, APIAssertMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class CreateOptionTest(APIPostTestCaseMixin, APIAssertMixin):
    def api_path(self) -> str:
        return reverse("options:option-list")

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), 4)
        self.assertEqual(
            set(self.response_body.keys()),
            {
                "id",
                "option_name",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(self.response_body["option_name"], payload["option_name"])
        self.assertDatetimeFormat(self.response_body["created_at"])
        self.assertDatetimeFormat(self.response_body["updated_at"])

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_create(self):
        payload = {
            "option_name": "test option",
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_create_if_already_exist(self):
        OptionFactory.create_option()
        payload = {
            "option_name": OptionFactory.option_name_color,
        }
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_if_option_name_is_empty(self):
        payload = {"option_name": ""}
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)
