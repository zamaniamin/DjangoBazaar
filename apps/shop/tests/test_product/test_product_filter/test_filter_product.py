from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class FilterProductTest(ProductBaseTestCase):
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

    def test_filter_active_product(self):
        response = self.client.get(
            path=reverse(viewname="product-list"), data={"status": "active"}
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(expected["count"], 3)
        self.assertEqual(len(expected["results"]), 3)

    def test_pagination_is_ten(self):
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)  # ?

    def test_invalid_page_number(self):
        response = self.client.get(reverse("product-list") + "?page=999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_integer_page_number(self):
        response = self.client.get(reverse("product-list") + "?page=abc")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# TODO scenario 1 : test pagination
# TODO scenario 2 : test in each pagination should load 10 products (DefaultPagination.page_size)
