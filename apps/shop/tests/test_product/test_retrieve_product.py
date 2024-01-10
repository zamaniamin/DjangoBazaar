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

    def test_retrieve_product_with_options(self):
        """
        Test retrieve a product with options:
        - with price and stock.
        - with options
        - with variants.
        - no media.
        """

        # --- request ---
        response = self.client.get(f"{self.product_path}{self.variable_product.id}/")

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(
            expected["product_name"], self.variable_product_payload["product_name"]
        )
        self.assertEqual(
            expected["description"], self.variable_product_payload["description"]
        )
        self.assertEqual(expected["status"], self.variable_product_payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedOptions(
            expected["options"], self.variable_product_payload["options"]
        )

        # --- expected product variants ---
        self.assertTrue(len(expected["variants"]) == 8)
        self.assertExpectedVariants(
            expected["variants"],
            self.variable_product_payload["price"],
            self.variable_product_payload["stock"],
        )

    def test_404(self):
        """
        Test retrieve a product if it doesn't exist.
        """
        response = self.client.get(f"{self.product_path}{999999999}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.get(f"{self.product_path}{self.simple_product.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_product_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.get(self.product_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")
        response = self.client.get(f"{self.product_path}{self.simple_product.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_product_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")
        response = self.client.get(self.product_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_by_guest(self):
        self.client.credentials()
        response = self.client.get(f"{self.product_path}{self.simple_product.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_product_by_guest(self):
        self.client.credentials()
        response = self.client.get(self.product_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# TODO test_with_media
# TODO test_with_options_media


