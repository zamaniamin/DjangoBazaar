from django.urls import reverse
from rest_framework import status

from apps.shop.faker.product_faker import ProductFaker
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class FilterProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # --- create product ---
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFaker.populate_active_simple_product(get_payload=True)
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = ProductFaker.populate_unique_variable_product(get_payload=True)

        # --- products with different status ---
        cls.active_product = ProductFaker.populate_active_simple_product()
        cls.archived_product = ProductFaker.populate_archived_simple_product()
        cls.draft_product = ProductFaker.populate_draft_simple_product()

    def test_filter_active_product(self):
        response = self.client.get(reverse("product-list"), data={"status": "active"})

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(expected["count"], 3)
        self.assertEqual(len(expected["results"]), 3)


# TODO create a list of products and use them in test scenarios
# TODO test base on user role
# TODO test pagination
# TODO test in each pagination should load 10 products (DefaultPagination.page_size)
