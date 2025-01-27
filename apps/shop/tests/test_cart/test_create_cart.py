import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import APITestCaseMixin


class CreateCartTestMixin(APITestCaseMixin):
    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_cart_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.post(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cart_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cart_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --------------------------
    # --- Test Create a Cart ---
    # --------------------------

    def test_create_cart(self):
        # request
        response = self.client.post(
            reverse("cart-list"), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        self.assertEqual(len(expected["items"]), 0)
        self.assertEqual(expected["total_price"], 0)
