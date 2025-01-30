import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin


class CreateCartTest(APIPostTestCaseMixin):
    def api_path(self) -> str:
        return reverse("cart-list")

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response), 3)
        self.assertIsInstance(uuid.UUID(self.response["id"]), uuid.UUID)
        self.assertIsInstance(self.response["items"], list)
        self.assertEqual(len(self.response["items"]), 0)
        self.assertEqual(self.response["total_price"], 0)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user(status.HTTP_201_CREATED)

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user(status.HTTP_201_CREATED)

    def test_create_cart(self):
        response = self.send_request()
        self.validate_response_body(response, {})
