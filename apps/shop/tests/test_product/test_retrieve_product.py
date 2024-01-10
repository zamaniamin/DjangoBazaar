from rest_framework import status

from apps.shop.faker.product_faker import FakeProduct
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class RetrieveProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data that will be shared across all test methods in this class.
        """

        super().setUpTestData()

        # --- create product ---
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = FakeProduct.populate_product()
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = FakeProduct.populate_product_with_options()

    def test_retrieve_product(self):
        """
        Test retrieve a product:
        - with product fields.
        - with one variant.
        - no options.
        - no media.
        """

        # --- request ---
        response = self.client.get(f"{self.product_path}{self.simple_product.id}/")

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(
            expected["product_name"], self.simple_product_payload["product_name"]
        )
        self.assertEqual(
            expected["description"], self.simple_product_payload["description"]
        )
        self.assertEqual(expected["status"], self.simple_product_payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertIsNone(expected["options"])

        # --- expected product variants ---
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(
            expected["variants"],
            expected_price=self.simple_product_payload["price"],
            expected_stock=self.simple_product_payload["stock"],
        )
