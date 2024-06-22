from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class SearchProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create product
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFactory.create_product(get_payload=True)
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = ProductFactory.create_product(is_variable=True, get_payload=True)

        # products with different status
        cls.active_product = ProductFactory.create_product()
        cls.archived_product = ProductFactory.create_product(
            status=Product.STATUS_ARCHIVED
        )
        cls.draft_product = ProductFactory.create_product(status=Product.STATUS_DRAFT)

    def test_search_active_product(self):
        response = self.client.get(
            path=reverse(viewname="product-list"), data={"status": "active"}
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(expected["count"], 3)
        self.assertEqual(len(expected["results"]), 3)

        # name = "product test"
        # description = "lorem epsom"

# TODO scenario 1 : test search base on just "product name"
# TODO scenario 2 : test search base on "product name" and "product description"
# TODO scenario 3 : test search base on "category name"
# TODO scenario 4 : test search base on "category name" and ignore "category description"
# TODO scenario 5 : test search base on "product name" and "product description" and "category name"
# TODO scenario 6 : test search base on "product name" and "product description" and "category name" and ignore "category description"

# TODO scenario  : test pagination
# TODO scenario  : test in each pagination should load 10 products (DefaultPagination.page_size)
