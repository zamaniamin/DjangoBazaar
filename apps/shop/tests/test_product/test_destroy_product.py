from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class DestroyProductTest(ProductBaseTestCase):
    @classmethod
    def setUp(cls):
        cls.active_product = ProductFactory.create_product()

    def test_delete_by_admin(self):
        """Test deleting a product by an admin (expects HTTP 204 No Content)."""

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.delete(
            reverse("product-detail", kwargs={"pk": self.active_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_by_user(self):
        """Test deleting a product by a user (expects HTTP 403 Forbidden)."""

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.delete(
            reverse("product-detail", kwargs={"pk": self.active_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_guest(self):
        """Test deleting a product by a guest (expects HTTP 401 Unauthorized)."""

        self.client.credentials()
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.active_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# TODO test destroy a product deletes all related information too
