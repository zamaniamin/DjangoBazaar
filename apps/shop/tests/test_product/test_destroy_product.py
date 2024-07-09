from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class DestroyProductTest(ProductBaseTestCase):
    @classmethod
    def setUp(cls):
        cls.active_product = ProductFactory.create_product()

    def test_delete_product_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.delete(
            reverse(
                "product-detail", kwargs={"pk": self.active_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_product_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            reverse(
                "product-detail", kwargs={"pk": self.active_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            reverse(
                "product-detail", kwargs={"pk": self.active_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# TODO test destroy a product deletes all related information too
