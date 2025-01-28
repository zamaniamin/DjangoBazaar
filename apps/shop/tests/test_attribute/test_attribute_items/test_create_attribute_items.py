from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class CreateAttributeItemsTestMixin(APIPostTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()
        cls.payload = {"item_name": AttributeFactory.attribute_item_name}

    def api_path(self) -> str:
        return reverse(
            "attribute-items-list", kwargs={"attribute_pk": self.attribute.id}
        )

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertIsInstance(self.response["id"], int)
        self.assertIsInstance(self.response["item_name"], str)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_create(self):
        response = self.send_request(self.payload)
        self.validate_response_body(response, self.payload)

    def test_create_one_item_if_already_exist(self):
        # create an attribute item
        AttributeFactory.add_one_attribute_item(self.attribute.id)
        response = self.send_request(self.payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_one_item_if_item_name_is_empty(self):
        payload = {"item_name": ""}
        response = self.send_request(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_one_item_if_attribute_not_exist(self):
        response = self.send_request(
            self.payload, reverse("attribute-items-list", kwargs={"attribute_pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
