from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class FilterProductTest(ProductAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create product
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFactory.customize(get_payload=True)
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = ProductFactory.customize(is_variable=True, get_payload=True)

        # products with different status
        cls.active_product = ProductFactory.customize()
        cls.archived_product = ProductFactory.customize(status=Product.STATUS_ARCHIVED)
        cls.draft_product = ProductFactory.customize(status=Product.STATUS_DRAFT)

    def test_filter_active_product(self):
        response = self.client.get(reverse("product-list"), {"status": "active"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(expected["count"], 3)
        self.assertEqual(len(expected["results"]), 3)


# TODO create a list of products and use them in test scenarios
# TODO test base on user role
# TODO test pagination
# TODO test in each pagination should load 10 products (DefaultPagination.page_size)
