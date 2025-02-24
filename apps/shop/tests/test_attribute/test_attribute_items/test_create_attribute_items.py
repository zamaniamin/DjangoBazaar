from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class CreateAttributeItemTest(APIPostTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_with_items(item_count=1)
        item = cls.attribute.items.first()
        cls.payload = {"item_name": item.item_name}

    def api_path(self) -> str:
        return reverse("attributes:items", kwargs={"attribute_id": self.attribute.id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertIsInstance(self.response_body["id"], int)
        self.assertIsInstance(self.response_body["item_name"], str)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_create(self):
        payload = {"item_name": "999"}
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_create_if_already_exist(self):
        # AttributeFactory.add_one_attribute_item(self.attribute.id)
        response = self.send_request(self.payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_if_name_is_empty(self):
        payload = {"item_name": ""}
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_if_attribute_not_exist(self):
        response = self.send_request(
            self.payload, reverse("attributes:items", kwargs={"attribute_id": 999})
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
