from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class UpdateOptionItemTest(APIUpdateTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.item = OptionFactory.add_one_option_item(cls.option.id)

    def api_path(self) -> str:
        return reverse(
            "options:item",
            kwargs={"option_id": self.option.id, "pk": self.item.id},
        )

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "item_name",
            },
        )
        self.assertEqual(self.response_body["item_name"], payload.get("item_name"))

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_update(self):
        payload = {"item_name": "red 2"}
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_update_invalid_item_pk(self):
        response = self.send_request(
            path=reverse(
                "options:item",
                kwargs={"option_id": self.option.id, "pk": 999},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_update_with_invalid_option_id(self):
        response = self.send_request(
            path=reverse(
                "options:item",
                kwargs={"option_id": 99999, "pk": self.item.id},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
