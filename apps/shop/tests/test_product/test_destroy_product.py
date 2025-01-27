from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class DestroyProductTest(ProductBaseTestCase):
    @classmethod
    def setUp(cls):
        cls.product = ProductFactory.create_product()

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def send_request(self):
        """Send a DELETE request to the server and return response."""
        return self.client.delete(
            reverse("product-detail", kwargs={"pk": self.product.id})
        )

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_delete_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.send_request()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.send_request()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------
    # --- Test Delete Product ---
    # ---------------------------

    def test_delete(self):
        self.set_admin_user_authorization()
        response = self.send_request()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# TODO test destroy a product deletes all related information too
