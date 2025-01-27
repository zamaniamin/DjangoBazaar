from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class RetrieveVariableProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create variable product
        cls.variable_product_payload, cls.variable_product = (
            ProductFactory.create_product(get_payload=True, is_variable=True)
        )

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def validate_response(self, response, payload):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = response.json()
        self.validate_product_general_data(expected)
        self.validate_product_options(expected["options"])
        self.validate_product_variants(expected["variants"])

    def validate_product_general_data(self, expected):
        self.assertEqual(len(expected), 13)
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], self.variable_product_payload["name"])

        # TODO add slug
        self.assertEqual(
            expected["description"], self.variable_product_payload["description"]
        )
        self.assertEqual(expected["status"], self.variable_product_payload["status"])

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(expected)

        self.assertEqual(
            set(expected["price"].keys()),
            {"min_price", "max_price"},
        )

        self.assertIsInstance(expected["total_stock"], int)
        # TODO add min price
        # TODO add max price
        # TODO add total stock

    def validate_product_options(self, options):
        # expected product options
        self.assertEqual(len(options), 3)

    def validate_product_variants(self, variants):
        # expected product variants
        self.assertEqual(len(variants), 8)
        self.assertExpectedVariants(
            variants,
            expected_price=self.variable_product_payload["price"],
            expected_stock=self.variable_product_payload["stock"],
        )

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------
    # TODO add access permission tests

    def test_retrieve(self):
        # request
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.variable_product.id})
        )
        self.validate_response(response, self.variable_product_payload)

    # todo test_retrieve_with_min_price
    # todo test_retrieve_with_max_price
    # todo test_retrieve_with_total_stock
