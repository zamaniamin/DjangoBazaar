import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase


class CreateCartBaseTest(CoreBaseTestCase):
    def test_create_cart(self):
        response = self.client.post(
            reverse("cart-list"), {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        self.assertEqual(len(expected["items"]), 0)
        self.assertEqual(expected["total_price"], 0)

# TODO test remove cart
# TODO test cart total price
# TODO test access permissions
# TODO add cart to faker
# print(response.data)
