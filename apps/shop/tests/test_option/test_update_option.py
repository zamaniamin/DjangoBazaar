from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class UpdateOptionTest(APIUpdateTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()

    def api_path(self) -> str:
        return reverse(
            "option-detail",
            kwargs={"pk": self.option.id},
        )

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "option_name",
                "updated_at",
                "created_at",
            },
        )
        self.assertEqual(self.response["option_name"], payload.get("option_name"))

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_update(self):
        payload = {"option_name": "color2"}
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_update_404(self):
        response = self.send_request(
            path=reverse(
                "option-detail",
                kwargs={"pk": 999},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
