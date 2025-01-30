from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class CreateOptionItemsTest(APIPostTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.payload = {"item_name": OptionFactory.item_name}

    def api_path(self) -> str:
        return reverse("option-items-list", kwargs={"option_pk": self.option.id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(self.response["item_name"], payload.get("item_name"))

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_create(self):
        response = self.send_request(self.payload)
        self.validate_response_body(response, self.payload)

    def test_create_if_already_exist(self):
        OptionFactory.add_one_option_item(self.option.id)
        response = self.send_request(self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_if_item_name_is_empty(self):
        payload = {"item_name": ""}
        response = self.send_request(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_if_option_not_exist(self):
        response = self.send_request(
            self.payload, reverse("option-items-list", kwargs={"option_pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
