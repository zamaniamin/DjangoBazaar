from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class CreateAttributeTest(APIPostTestCaseMixin):
    def api_path(self) -> str:
        return reverse("attribute-list")

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response), 4)
        self.assertEqual(self.response["attribute_name"], payload["attribute_name"])

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_create(self):
        payload = {
            "attribute_name": "test attribute",
        }
        response = self.send_request(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.validate_response_body(response, payload)

    def test_create_if_already_exist(self):
        AttributeFactory.create_attribute()
        payload = {
            "attribute_name": AttributeFactory.attribute_name,
        }
        response = self.send_request(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_if_name_is_empty(self):
        payload = {"attribute_name": ""}
        response = self.send_request(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
